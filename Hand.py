import logging

import DerivedStats
from Exceptions import FpdbParseError

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("hand")

class Hand(object):
    def __init__(self, game_type, hand_text):
        self.game_type = game_type
        self.hand_text = hand_text
        self.id = 0
        self.table_name = ""
        self.hand_no = 0
        self.game_type_id = 0
        self.start_time = ""
        self.players_ids = None
        self.hero = ""
        self.button_pos = 0

        # tourney stuff
        self.tour_no = 0
        self.tourney_id = 0
        self.tourney_type_id = 0
        self.buy_in = 0
        self.buy_in_currency = None
        self.fee = 0
        self.speed = "Regular"
        self.is_private = False
        self.is_sng = False
        self.is_ko = False
        self.ko_bounty = 0

        self.seating = []
        self.players = []
        # Cache used for check_player_exists.
        self.player_exists_cache = set()

        # Collections indexed by street names
        self.bets = {}
        self.last_bet = {}
        self.streets = {}
        self.actions = {}  # [['mct','bets','$10'],['mika','folds'],['carlg','raises','$20']]
        self.board = {}  # dict from street names to community cards
        self.hole_cards = {}

        for street in self.action_streets:
            self.streets[street] = ""  # portions of the hand_text, filled by mark_streets()
            self.actions[street] = []

        for street in self.action_streets:
            self.bets[street] = {}
            self.last_bet[street] = 0
            self.board[street] = []

        # Collections indexed by player names
        self.stacks = {}
        self.won_bounty = {}
        self.end_bounty = {}

        self.hand = {}
        self.hand_players = {}
        self.hand_actions = {}

    def add_hole_cards(self, player, cards=[]):
        # Assigns observed hole_cards to a player.
        # cards   list of card bigrams e.g. ['2h','Jc']
        # player  (string) name of player
        log.debug(f"Hand.add_hole_cards cards: {cards}, player: {player}")

        self.check_player_exists(player, "add_hole_cards")

        self.hole_cards[player] = cards

    def prep_insert(self, db):
        # Players, GameTypes, TourneyTypes are all shared functions that are needed for additional tables
        # These functions are intended for prep insert eventually

        self.players_ids = db.get_players_ids([p[1] for p in self.players], self.hero)
        self.game_type_id = db.get_game_type_id(self.game_type)
        self.tourney_type_id = db.get_tourney_type_id(self)
        self.tourney_id = db.get_tourney_id_from_hand(self)

    def assemble_hand(self, file_id):
        stats = DerivedStats.stats_initializer()

        for player in self.players:
            self.hand_players[player[1]] = stats.copy()

        self.hand["tableName"] = self.table_name
        self.hand["handNo"] = self.hand_no
        self.hand["tourneyId"] = self.tourney_id
        self.hand["gameTypeId"] = self.game_type_id
        self.hand["fileId"] = file_id
        self.hand["startTime"] = self.start_time
        self.hand["seats"] = len(self.players_ids)
        self.hand["heroSeat"] = 0

        for player in self.players:
            if self.hero == player[1]:
                self.hand["heroSeat"] = player[0]
                break

        board_cards = []

        for street in self.community_streets:
            board_cards += self.board[street]

        for i, card in enumerate(board_cards):
            self.hand[f"boardCard{i + 1}"] = card

        if len(board_cards) < 5:
            for i in range(len(board_cards), 5):
                self.hand[f"boardCard{i + 1}"] = None

        DerivedStats.vpip(self)  # Gives playersVPI (num of players vpip)

        self.set_positions()

    def assemble_hand_players(self):
        # street0VPI/vpip already called in Hand

        for player in self.players:
            player_name = player[1]
            player_stats = self.hand_players.get(player_name)
            player_stats["startStack"] = int(player[2])

            if player[4] is not None:
                player_stats["startBounty"] = float(player[4])
                player_stats["endBounty"] = float(player[4])

                if player_name in self.end_bounty:
                    player_stats["endBounty"] = self.end_bounty.get(player_name)

            player_stats["seatNo"] = player[0]

        for i in enumerate(self.action_streets[1:]):
            DerivedStats.aggr(self, i[0])

            if i[0] > 0:
                DerivedStats.folds(self, i[0])

        DerivedStats.calc_cbets(self)

        for player in self.players:
            player_name = player[1]

            if player_name in list(self.hole_cards.keys()):
                player_stats = self.hand_players.get(player_name)
                player_stats["card1"] = self.hole_cards[player_name][0]
                player_stats["card2"] = self.hole_cards[player_name][1]

        DerivedStats.calc_check_raise(self)
        DerivedStats.calc_tfbets(self)
        DerivedStats.calc_steals(self)

    def assemble_hand_actions(self):
        k = 0

        for street in self.action_streets:
            for action in self.actions[street]:
                self.hand_actions[k] = {}
                self.hand_actions[k]["player"] = action[0]
                self.hand_actions[k]["street"] = street
                self.hand_actions[k]["action"] = action[1]

                if len(action) > 2:
                    self.hand_actions[k]["amount"] = action[2]
                else:
                    self.hand_actions[k]["amount"] = 0

                if len(action) > 3:
                    self.hand_actions[k]["allIn"] = action[-1]
                else:
                    self.hand_actions[k]["allIn"] = False

                k += 1

    def set_positions(self):
        # Sets the position for each player in HandPlayers starting from D = 0 counter clockwise
        # then sets SB to S and BB to B

        button_index = [i for i, x in enumerate(self.players) if x[0] == self.button_pos][0]

        self.hand_players[self.players[button_index][1]]["position"] = 0

        reverse_index = button_index - 1
        position = 1

        while self.players[reverse_index][0] != self.button_pos:
            self.hand_players[self.players[reverse_index][1]]["position"] = position
            reverse_index -= 1
            position += 1

        bb = [x[0] for x in self.actions[self.action_streets[1]] if x[1] == "big blind"]
        sb = [x[0] for x in self.actions[self.action_streets[1]] if x[1] == "small blind"]

        if bb:
            self.hand_players[bb[0]]["position"] = "B"

        if sb:
            self.hand_players[sb[0]]["position"] = "S"

    def add_player(self, seat, name, chips, position=None, bounty=None):
        # Adds a player to the hand, and initialises data structures indexed by player.
        # seat     (int)    indicating the seat
        # name     (string) player name
        # chips    (string) the chips the player has at the start of the hand (can be None)
        # position (string) indicating the position of the player (S,B, 0-7) (optional, not needed on Hand import from Handhistory).
        # If a player has None chips he won't be added.

        log.debug(f"add_player: {seat} {name} ({chips})")

        if chips is not None:
            self.players.append([seat, name, chips, position, bounty])
            self.stacks[name] = int(chips)

            for street in self.action_streets:
                self.bets[street][name] = []

    def add_streets(self, match):
        # go through m and initialise actions to empty list for each street.
        if match:
            self.streets.update(match.groupdict())

            log.debug(f"add_streets:\n{str(self.streets)}")
        else:
            tmp = self.hand_text[0:100]
            raise FpdbParseError(f"Streets didn't match - Hand '{self.hand_no}'. First 100 characters: {tmp}")

    def check_player_exists(self, player, source=None):
        # Fast path, because this function is called ALL THE TIME.
        if player in self.player_exists_cache:
            return

        if player not in (p[1] for p in self.players):
            if source is not None:
                log.error(f"Hand.{source}: '{self.hand_no}' unknown player: '{player}'")
            raise FpdbParseError
        else:
            self.player_exists_cache.add(player)

    def set_community_cards(self, street, cards):
        log.debug(f"set_community_cards {street} {cards}")
        self.board[street] = cards

    def add_ante(self, player, amount):
        log.debug(f"add_ante: {player} antes {amount}")

        if self.game_type["ante"] != amount:
            self.game_type["ante"] = amount

        self.check_player_exists(player, "add_ante")

        street = "ANTES"
        amount = int(amount)
        self.stacks[player] -= amount

        act = (player, "ante", amount, self.stacks[player] == 0)
        self.actions[street].append(act)
        self.bets[street][player].append(amount)

    def add_blind(self, player, blind_type, amount):
        # if player is None, it's a missing small blind.
        # The situation we need to cover are:
        # Player in small blind posts
        #   - this is a bet of 1 sb, as yet uncalled.
        # Player in the big blind posts
        #   - this is a call of 1 sb and a raise to 1 bb

        log.debug(f"add_blind: {player} posts {blind_type}, {amount}")

        self.check_player_exists(player, "add_blind")

        street = "PREFLOP"
        amount = int(amount)
        self.stacks[player] -= amount

        act = (player, blind_type, amount, self.stacks[player] == 0)
        self.actions[street].append(act)
        self.bets[street][player].append(amount)

        if amount > self.last_bet.get(street):
            self.last_bet[street] = amount

    def add_call(self, street, player, amount):
        log.debug(f"add_call: {street} {player} calls {amount}")

        self.check_player_exists(player, "add_call")

        amount = int(amount)
        self.stacks[player] -= amount

        act = (player, "calls", amount, self.stacks[player] == 0)
        self.actions[street].append(act)
        self.bets[street][player].append(amount)

        if amount > self.last_bet.get(street):
            self.last_bet[street] = amount

    def add_raise_to(self, street, player, amount, amount_to):
        log.debug(f"add_raise_to: {street} {player} raises {amount} to {amount_to}")

        self.check_player_exists(player, "add_raise_to")

        amount = int(amount)
        amount_to = int(amount_to)

        bets = sum(self.bets[street][player])
        called = amount_to - amount - bets
        raised = called + amount

        self.stacks[player] -= raised

        act = (player, "raises", amount, amount_to, called, self.stacks[player] == 0)
        self.actions[street].append(act)
        self.bets[street][player].append(raised)
        self.last_bet[street] = amount_to

    def add_bet(self, street, player, amount):
        log.debug(f"add_bet: {street} {player} bets {amount}")

        self.check_player_exists(player, "add_bet")

        amount = int(amount)
        self.stacks[player] -= amount

        act = (player, "bets", amount, self.stacks[player] == 0)
        self.actions[street].append(act)
        self.bets[street][player].append(amount)
        self.last_bet[street] = amount

    def add_fold(self, street, player):
        log.debug(f"add_fold: {street} {player} folds")

        self.check_player_exists(player, "add_fold")

        self.actions[street].append((player, "folds"))

    def add_check(self, street, player):
        log.debug(f"add_check: {street} {player} checks")

        self.check_player_exists(player, "add_check")

        self.actions[street].append((player, "checks"))

    def add_uncalled(self, street, player, amount):
        log.debug(f"add_uncalled: {street} {player} uncalled {amount}")

        self.check_player_exists(player, "add_uncalled")

        amount = int(amount)
        self.stacks[player] += amount

class HoldemHand(Hand):
    def __init__(self, hhc, game_type, hand_text):
        self.hole_streets = ["PREFLOP"]
        self.community_streets = ["FLOP", "TURN", "RIVER"]
        self.action_streets = ["ANTES", "PREFLOP", "FLOP", "TURN", "RIVER"]
        
        super().__init__(game_type, hand_text)

        # Populate a HoldemHand
        # Generally, we call 'read' methods here, which get the info according to the particular filter (hhc)
        # which then invokes a 'add_XXX' callback
        hhc.read_hand_info(self)
        hhc.read_button(self)
        hhc.read_player_stacks(self)
        hhc.read_antes(self)
        hhc.read_blinds(self)
        hhc.mark_streets(self)
        hhc.read_hole_cards(self)

        for street in self.community_streets:
            if self.streets[street]:
                hhc.read_community_cards(self, street)

        for street in self.action_streets:
            if self.streets[street]:
                hhc.read_action(self, street)

        hhc.read_bounty(self)
        hhc.read_shown_cards(self)

def stats_initializer():
    init = {}

    # Init vars that may not be used, but still need to be inserted.
    init["startBounty"] = None
    init["endBounty"] = None
    init["position"] = None
    init["seatNo"] = None
    init["card1"] = None
    init["card2"] = None
    init["winnings"] = 0
    init["totalProfit"] = 0
    init["startingHand"] = None
    init["street0VPIChance"] = True
    init["street0VPI"] = False
    init["street0AggrChance"] = True
    init["street0Aggr"] = False
    init["street0TBChance"] = False
    init["street0TBDone"] = False
    init["street0FBChance"] = False
    init["street0FBDone"] = False
    init["street0FoldTo3BChance"] = False
    init["street0FoldTo3BDone"] = False
    init["street0FoldTo4BChance"] = False
    init["street0FoldTo4BDone"] = False
    init["raiseToStealChance"] = False
    init["raiseToStealDone"] = False
    init["stealChance"] = False
    init["stealDone"] = False
    init["foldBBToStealChance"] = False
    init["foldedBBToSteal"] = False
    init["foldSBToStealChance"] = False
    init["foldedSBToSteal"] = False

    for i in range(1, 4):
        init[f"otherRaisedStreet{i}"] = False
        init[f"foldToOtherRaisedStreet{i}"] = False
        init[f"street{i}CBChance"] = False
        init[f"street{i}CBDone"] = False
        init[f"foldToStreet{i}CBChance"] = False
        init[f"foldToStreet{i}CBDone"] = False
        init[f"street{i}CheckRaiseChance"] = False
        init[f"street{i}CheckRaiseDone"] = False

    return init

def vpip(hand):
    vpipers = set()
    bb = [x[0] for x in hand.actions[hand.action_streets[1]] if x[1] == "big blind"]

    for action in hand.actions[hand.action_streets[1]]:
        if action[1] in ("calls", "raises"):
            vpipers.add(action[0])

    for player in hand.players:
        if player[1] in vpipers:
            hand.hand_players[player[1]]["street0VPI"] = True

    if len(vpipers) == 0 and bb:
        hand.hand_players[bb[0]]["street0VPIChance"] = False
        hand.hand_players[bb[0]]["street0AggrChance"] = False

def calc_steals(hand):
    # Fills fold(BB|SB)ToSteal(Chance)
    # Steal attempt - open raise on positions 1 0 S - i.e. CO, D, SB
    # Fold to steal - folding blind after steal attemp wo any other callers or raisers

    steal_attempt = False
    steal_positions = (1, 0, "S")

    for action in hand.actions[hand.action_streets[1]]:
        player_name, act = action[0], action[1]
        player_stats = hand.hand_players.get(player_name)
        position = player_stats["position"]

        if steal_attempt:
            if position == "B":
                player_stats["foldBBToStealChance"] = True
                player_stats["raiseToStealChance"] = True
                player_stats["foldedBBToSteal"] = act == "folds"
                player_stats["raiseToStealDone"] = act == "raises"
                break
            elif position == "S":
                player_stats["foldSBToStealChance"] = True
                player_stats["raiseToStealChance"] = True
                player_stats["foldedSBToSteal"] = act == "folds"
                player_stats["raiseToStealDone"] = act == "raises"

                if act == "calls":
                    break

        if position not in steal_positions and act in ("calls", "raises"):
            break

        if position in steal_positions and not steal_attempt and act not in ("small blind", "big blind"):
            player_stats["stealChance"] = True

            if act == "calls":
                break
            elif act == "raises":
                steal_attempt = True
                player_stats["stealDone"] = True

def calc_tfbets(hand):
    # Fills street0(T|F)B(Chance|Done)
    # bet_level after 3-bet is equal to 3

    bet_level, raise_chance, action_cnt, first_agressor = 1, True, {}, None

    p_in = set([x[0] for x in hand.actions[hand.action_streets[1]]])

    for p in p_in:
        action_cnt[p] = 0

    for action in hand.actions[hand.action_streets[1]]:
        player_name, act, aggr, all_in = action[0], action[1], action[1] == "raises", False
        player_stats = hand.hand_players.get(player_name)
        action_cnt[player_name] += 1

        if len(action) > 3:
            all_in = action[-1]

        if len(p_in) == 1 and action_cnt[player_name] == 1:
            raise_chance = False
            player_stats["street0AggrChance"] = raise_chance

        if act == "folds" or all_in:
            p_in.discard(player_name)

        if bet_level == 1:
            if aggr:
                bet_level += 1
        elif bet_level == 2:
            player_stats["street0TBChance"] = True

            if aggr:
                player_stats["street0TBDone"] = True
                bet_level += 1
        elif bet_level == 3:
            player_stats["street0FBChance"] = True
            player_stats["street0FoldTo3BChance"] = True

            if aggr:
                player_stats["street0FBDone"] = True
                bet_level += 1
            elif act == "folds":
                player_stats["street0FoldTo3BDone"] = True
        elif bet_level == 4:
            player_stats["street0FoldTo4BChance"] = True

            if act == "folds":
                player_stats["street0FoldTo4BDone"] = True

def calc_cbets(hand):
    # Fill streetXCBChance, streetXCBDone, foldToStreetXCBDone, foldToStreetXCBChance 
    # Continuation Bet chance, action:
    # Had the last bet (initiative) on previous street, got called, close street action
    # Then no bets before the player with initiatives first action on current street
    # ie. if player on street-1 had initiative and no donkbets occurred

    for i, street in enumerate(hand.action_streets[2:]):
        name = last_aggressor(hand.actions, hand.action_streets[i + 1])  # previous street

        if name:
            chance = no_bets_before(hand.actions, hand.action_streets[i + 2], name)  # this street

            if chance:
                player_stats = hand.hand_players.get(name)
                player_stats[f"street{i + 1}CBChance"] = True
                player_stats[f"street{i + 1}CBDone"] = bet_street(hand.actions, hand.action_streets[i + 2], name)

                if player_stats[f"street{i + 1}CBDone"]:
                    for player, folds in list(fold_to_aggressor(hand.actions, street, name).items()):
                        hand.hand_players[player][f"foldToStreet{i + 1}CBChance"] = True
                        hand.hand_players[player][f"foldToStreet{i + 1}CBDone"] = folds

def calc_check_raise(hand):
    # Fill streetXCheckRaiseChance, streetXCheckRaiseDone
    # streetXCheckRaiseChance = got bet after check
    # streetXCheckRaiseDone = checked. got bet. raise

    for i, street in enumerate(hand.action_streets[2:]):
        actions = hand.actions[street]
        checkers = set()
        acted = set()
        initial_better = None

        for action in actions:
            player_name, act = action[0], action[1]

            if act == "bets" and initial_better is None:
                initial_better = player_name
            elif act == "checks" and initial_better is None:
                checkers.add(player_name)
            elif initial_better is not None and player_name in checkers and player_name not in acted:
                player_stats = hand.hand_players.get(player_name)
                player_stats[f"street{i + 1}CheckRaiseChance"] = True
                player_stats[f"street{i + 1}CheckRaiseDone"] = act == "raises"
                acted.add(player_name)

def aggr(hand, i):
    aggrers = set()
    others = set()
    first_aggr_made = False

    for action in hand.actions[hand.action_streets[i + 1]]:
        if first_aggr_made:
            others.add(action[0])

        if action[1] in ("bets", "raises"):
            aggrers.add(action[0])
            first_aggr_made = True

    if i == 0:
        for player in hand.players:
            if player[1] in aggrers:
                hand.hand_players[player[1]]["street0Aggr"] = True
    else:
        if len(aggrers) > 0:
            for player_name in others:
                hand.hand_players[player_name][f"otherRaisedStreet{i}"] = True

def folds(hand, i):
    for action in hand.actions[hand.action_streets[i + 1]]:
        if action[1] == "folds":
            player_stats = hand.hand_players.get(action[0])

            if player_stats[f"otherRaisedStreet{i}"]:
                player_stats[f"foldToOtherRaisedStreet{i}"] = True

def fold_to_aggressor(actions, street, aggressor):
    # Returns player names that folded to aggressor.
    # None if there were no bets or raises on that street

    i, players = 0, {}

    for action in actions[street]:
        if i > 1:
            break

        if action[0] != aggressor:
            players[action[0]] = action[1] == "folds"

            if action[1] == "raises":
                break
        else:
            i += 1

    return players

def last_aggressor(actions, street):
    # Returns player name that placed the last bet or raise for that street.
    # None if there were no bets or raises on that street

    player = None

    for action in actions[street]:
        if action[1] in ("bets", "raises"):
            player = action[0]

    return player

def no_bets_before(actions, street, player):
    # Returns true if there were no bets before the specified players turn, false otherwise

    for action in actions[street]:
        # Must test for player first in case UTG
        if action[0] == player:
            return True

        if action[1] in ("bets", "raises"):
            return False

    return False

def bet_street(actions, street, player):
    # Returns true if player bets the street as his first action

    for action in actions[street]:
        if action[0] == player:
            return action[1] == "bets"

    return False

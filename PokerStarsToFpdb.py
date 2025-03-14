import codecs
from decimal import Decimal
import logging
import re

from Exceptions import FpdbParseError
import Hand
import PokerStarsStructures

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("parser")

SUBSTITUTIONS = {
    "LEGAL_ISO": "EUR",  # legal ISO currency codes
    "LS": "\u20ac",  # legal currency symbols
    "PLYR": r"(?P<PNAME>.+?)"
}
LIMITS = {"No Limit": "nl"}
GAMES = {"Hold'em": "hold"}
RE_SPLIT_HANDS = re.compile("(?:\s?\n){2,}")
RE_GAME_INFO = re.compile(
    r"""
        PokerStars\s(?:Game|Hand)\s\#(?P<HID>\d+):\s
        (?:Tournament\s\#(?P<TOURNO>\d+),\s
        (?P<BUYIN>(?P<BIAMT>(?P<BILS>%(LS)s)[.\d]+)\+?(?P<FEE>[%(LS)s.\d]+)?\+?(?P<BOUNTY>[%(LS)s.\d]+)?\s(?P<BICURRENCY>%(LEGAL_ISO)s)))?
        \s(?P<GAME>Hold'em)\s(?P<LIMIT>No\sLimit)\s
        (?:-\sLevel\s[IVXLC]+\s)?
        \((?:%(LS)s)?(?P<SB>[.\d]+)\/(?:%(LS)s)?(?P<BB>[.\d]+)(?:\s)?(?P<CASHCURRENCY>%(LEGAL_ISO)s)?\)
        (?:\s(?P<ADM>\[(?:ADM|AAMS)\sID:\s[A-Z\d]+\]))?
        \s-\s(?P<DATETIME>.*$)
    """
    % SUBSTITUTIONS,
    re.MULTILINE | re.VERBOSE
)
RE_DATE_TIME = re.compile(r"(?P<Y>\d{4})\/(?P<M>\d{2})\/(?P<D>\d{2})[\- ]+(?P<H>\d{1,2}):(?P<MIN>\d{2}):(?P<S>\d{2})")
RE_HAND_INFO = re.compile(r"Table\s\'(?P<TABLE>.+?)\'\s((?P<MAX>\d+)-max)")
RE_BUTTON = re.compile(r"Seat #(?P<BUTTON>\d+) is the button")
RE_PLAYER_INFO = re.compile(r"Seat\s(?P<SEAT>\d+):\s%(PLYR)s\s\((?:%(LS)s)?(?P<CASH>[.\d]+)\sin\schips(?:,\s%(LS)s(?P<BOUNTY>[.\d]+)\sbounty)?\)(?P<SITOUT>\sis\ssitting\sout)?" % SUBSTITUTIONS)
RE_ANTES = re.compile(r"%(PLYR)s:\sposts\sthe\sante\s(?P<ANTE>\d+)" % SUBSTITUTIONS)
RE_POST_SB = re.compile(r"%(PLYR)s:\sposts\ssmall\sblind\s(?:%(LS)s)?(?P<SB>[.\d]+)" % SUBSTITUTIONS)
RE_POST_BB = re.compile(r"%(PLYR)s:\sposts\sbig\sblind\s(?:%(LS)s)?(?P<BB>[.\d]+)" % SUBSTITUTIONS)
RE_HERO_CARDS = re.compile(r"Dealt\sto\s%(PLYR)s\s(\[(?P<CARDS>.+?)\])" % SUBSTITUTIONS)
RE_BOARD = re.compile(r"\[(?P<CARDS>.+)\]")
RE_ACTION = re.compile(r"%(PLYR)s:(?P<ATYPE>\sbets|\schecks|\sraises|\scalls|\sfolds)(?:\s(?:%(LS)s)?(?P<BET>[.\d]+))?(?:\sto\s(?:%(LS)s)?(?P<BETTO>[.\d]+))?\s*(?:and\sis\sall.in)?" % SUBSTITUTIONS)
RE_UNCALLED = re.compile(r"Uncalled\sbet\s\((?:%(LS)s)?(?P<BET>[.\d]+)\)\sreturned\sto\s%(PLYR)s$" % SUBSTITUTIONS, re.MULTILINE)
RE_COLLECTED = re.compile(r"%(PLYR)s\scollected\s(?:%(LS)s)?(?P<POT>[.\d]+)\sfrom\s(?:side|main)?(?:\s)?pot$" % SUBSTITUTIONS, re.MULTILINE)
# Kaor89 wins €0.45 for eliminating campisi1995 and their own bounty increases by €0.45 to €1.35
# Berry67 wins €0.23 for splitting the elimination of Iroshi1 and their own bounty increases by €0.22 to €1.12
RE_BOUNTY = re.compile(r"%(PLYR)s\swins\s%(LS)s(?P<BOUNTY>[.\d]+)\sfor\s(splitting\sthe\selimination\sof|eliminating)\s.+?\sand\stheir\sown\sbounty\sincreases\sby\s%(LS)s[.\d]+\sto\s%(LS)s(?P<ENDBOUNTY>[.\d]+)" % SUBSTITUTIONS)
RE_SHOWN_CARDS = re.compile(r"Seat\s\d+:\s%(PLYR)s\s((\(button\)|\(small\sblind\)|\(big\sblind\)|\(button\)\s\(small\sblind\))\s)?(showed|mucked)\s\[(?P<CARDS>.*)\]" % SUBSTITUTIONS)

class PokerStars(object):
    def __init__(self, file, index, auto_pop):
        self.file = file
        self.index = index
        self.auto_pop = auto_pop
        self.processed_hands = []
        self.num_hands = 0
        self.num_errors = 0

        self.start()

    def start(self):
        # Process a hand at a time from the input specified by file
        hands_list = self.get_hands_list()

        log.info(f"Parsing {len(hands_list)} hands")

        for hand_text in hands_list:
            try:
                self.processed_hands.append(self.process_hand(hand_text))
            except FpdbParseError:
                self.num_errors += 1
                log.error(f"FpdbParseError for file '{self.file}'")

        self.num_hands = len(hands_list)

        log.info(f"Read {self.num_hands} hands ({self.num_errors} failed)")

    def get_hands_list(self):
        # Return a list of hand_texts in the file at self.file
        self.read_file()

        if self.obs is None or self.obs == "":
            log.info(f"Read no hands from file: '{self.file}'")
            return []

        hand_list = re.split(RE_SPLIT_HANDS, self.obs)

        return hand_list

    def process_hand(self, hand_text):
        game_type = self.determine_game_type(hand_text)
        game_details = None

        if game_type is None:
            log.error("Unsupported game type: unmatched")
            raise FpdbParseError

        game_details = [game_type["base"], game_type["limitType"]]

        if game_details in self.read_supported_games():
            return Hand.HoldemHand(self, game_type, hand_text)

        log.error(f"Unsupported game type: {game_type}")
        raise FpdbParseError

    def read_file(self):
        try:
            with codecs.open(self.file, "r", "utf-8") as file_reader:
                whole_file = file_reader.read().replace("\r\n", "\n").replace("\xa0", " ")
                file_reader.close()

            self.obs = whole_file[self.index :].rstrip()
            self.index = len(whole_file)
        except Exception as e:
            log.error(f"Failed to read file {self.file}: {e}")

    def read_supported_games(self):
        return [["hold", "nl"]]

    def determine_game_type(self, hand_text):
        info = {}

        try:
            m = RE_GAME_INFO.search(hand_text)

            if not m:
                log.error(f"PokerStarsToFpdb.determine_game_type: '{self.file}'")
                raise FpdbParseError

            mg = m.groupdict()

            info["limitType"] = LIMITS[mg["LIMIT"]]
            info["base"] = GAMES[mg["GAME"]]

            if mg["CASHCURRENCY"] is not None:
                info["type"] = "cash"
                info["currency"] = mg["CASHCURRENCY"]
            else:
                info["type"] = "tour"
                info["currency"] = "CHIP"

            info["sb"] = mg["SB"]
            info["bb"] = mg["BB"]
            info["ante"] = "0"

            return info
        except Exception as e:
            log.error(f"PokerStarsToFpdb.determine_game_type: '{e}'")
            raise FpdbParseError

    def read_hand_info(self, hand):
        info = {}

        try:
            m = RE_GAME_INFO.search(hand.hand_text)
            m2 = RE_HAND_INFO.search(hand.hand_text)

            if m is None or m2 is None:
                log.error(f"PokerStarsToFpdb.read_hand_info: '{self.file}'")
                raise FpdbParseError

            info.update(m.groupdict())
            info.update(m2.groupdict())

            hand.hand_no = int(info["HID"])

            if info["TOURNO"] is not None:
                hand.tour_no = int(info["TOURNO"])
                hand.buy_in_currency = info["BICURRENCY"]
                ls = info["BILS"]
                info["BIAMT"] = info["BIAMT"].strip(ls)

                if info["BOUNTY"] is not None:
                    # There is a bounty, Which means we need to switch BOUNTY and FEE values
                    tmp = info["BOUNTY"]
                    info["BOUNTY"] = info["FEE"]
                    info["FEE"] = tmp
                    info["BOUNTY"] = info["BOUNTY"].strip(ls)  # Strip here where it isn't 'None'
                    hand.ko_bounty = Decimal(info["BOUNTY"])
                    hand.is_ko = True

                info["FEE"] = info["FEE"].strip(ls)
                hand.buy_in = Decimal(info["BIAMT"]) + hand.ko_bounty
                hand.fee = Decimal(info["FEE"])

            if info["ADM"] is not None:
                hand.is_private = False
            else:
                hand.is_private = True
                hand.speed = "Turbo"

            m3 = RE_DATE_TIME.finditer(info["DATETIME"])
            a = next(m3)
            hand.start_time = f"{a.group('Y')}/{a.group('M')}/{a.group('D')} {a.group('H'):0>2}:{a.group('MIN')}:{a.group('S')}"

            if info["TOURNO"] is not None:
                table_split = re.split(" ", info["TABLE"])
                hand.table_name = f"Tournament {hand.tour_no} Table {table_split[1]}"
            else:
                hand.table_name = info["TABLE"]

            hand.game_type["maxSeats"] = int(info["MAX"])

            speed = PokerStarsStructures.SNG_STRUCTURES.get((hand.buy_in, hand.fee, hand.game_type["maxSeats"]))

            if speed is not None:
                hand.speed = speed
                hand.is_sng = True
        except Exception as e:
            log.error(f"PokerStarsToFpdb.read_hand_info: '{e}'")
            raise FpdbParseError

    def read_button(self, hand):
        m = RE_BUTTON.search(hand.hand_text)
        hand.button_pos = int(m.group("BUTTON"))

    def read_player_stacks(self, hand):
        for m in RE_PLAYER_INFO.finditer(hand.hand_text):
            if hand.game_type["type"] == "tour" or m.group("SITOUT") is None:
                hand.add_player(
                    int(m.group("SEAT")),
                    m.group("PNAME"),
                    m.group("CASH"),
                    None,
                    m.group("BOUNTY")
                )

    def mark_streets(self, hand):
        # PREFLOP = ** Dealing down cards **
        m = re.search(
            r"\*\*\* HOLE CARDS \*\*\*(?P<PREFLOP>.+(?=\*\*\* FLOP \*\*\*)|.+)"
            r"(\*\*\* FLOP \*\*\*(?P<FLOP> (\[\S\S\] )?\[(\S\S ?)?\S\S \S\S\].+(?=\*\*\* TURN \*\*\*)|.+))?"
            r"(\*\*\* TURN \*\*\* \[\S\S \S\S \S\S\] (?P<TURN>\[\S\S\].+(?=\*\*\* RIVER \*\*\*)|.+))?"
            r"(\*\*\* RIVER \*\*\* \[\S\S \S\S \S\S\]? \[?\S\S\] (?P<RIVER>\[\S\S\].+))?",
            hand.hand_text,
            re.DOTALL
        )

        hand.add_streets(m)

    def read_community_cards(self, hand, street):
        m = RE_BOARD.search(hand.streets[street])
        hand.set_community_cards(street, m.group("CARDS").split(" "))

    def read_antes(self, hand):
        for m in RE_ANTES.finditer(hand.hand_text):
            hand.add_ante(m.group("PNAME"), m.group("ANTE"))

    def read_blinds(self, hand):
        m = RE_POST_SB.search(hand.hand_text)
        m2 = RE_POST_BB.finditer(hand.hand_text)

        if m:
            hand.add_blind(m.group("PNAME"), "small blind", m.group("SB"))

        for bb in m2:
            hand.add_blind(bb.group("PNAME"), "big blind", bb.group("BB"))

    def read_hole_cards(self, hand):
        street = "PREFLOP"
        m = RE_HERO_CARDS.search(hand.streets[street])
        hand.hero = m.group("PNAME")
        cards = m.group("CARDS").split(" ")
        hand.add_hole_cards(hand.hero, cards)

    def read_action(self, hand, street):
        if not hand.streets[street]:
            return

        m = RE_ACTION.finditer(hand.streets[street])

        for action in m:
            if action.group("ATYPE") == " folds":
                hand.add_fold(street, action.group("PNAME"))
            elif action.group("ATYPE") == " checks":
                hand.add_check(street, action.group("PNAME"))
            elif action.group("ATYPE") == " calls":
                hand.add_call(street, action.group("PNAME"), action.group("BET"))
            elif action.group("ATYPE") == " raises":
                hand.add_raise_to(street, action.group("PNAME"), action.group("BET"), action.group("BETTO"))
            elif action.group("ATYPE") == " bets":
                hand.add_bet(street, action.group("PNAME"), action.group("BET"))
            else:
                raise FpdbParseError(f"Unimplemented read_action: '{action.group('PNAME')}' '{action.group('ATYPE')}'")

        m = RE_UNCALLED.search(hand.streets[street])

        if m:
            hand.add_uncalled(street, m.group("PNAME"), m.group("BET"))

        m = RE_COLLECTED.finditer(hand.streets[street])

        for action in m:
            hand.add_collected(street, action.group("PNAME"), action.group("POT"))

    def read_bounty(self, hand):
        for m in RE_BOUNTY.finditer(hand.hand_text):
            if m.group("PNAME") not in hand.won_bounty:
                hand.won_bounty[m.group("PNAME")] = 0

            hand.won_bounty[m.group("PNAME")] += Decimal(m.group("BOUNTY"))
            hand.end_bounty[m.group("PNAME")] = Decimal(m.group("ENDBOUNTY"))

    def read_shown_cards(self, hand):
        for m in RE_SHOWN_CARDS.finditer(hand.hand_text):
            cards = m.group("CARDS").split(" ")

            hand.add_hole_cards(m.group("PNAME"), cards)

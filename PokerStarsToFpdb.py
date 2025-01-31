import logging
import re

from Exceptions import FpdbParseError
from HandHistoryConverter import HandHistoryConverter
import PokerStarsStructures

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("parser")

class PokerStars(HandHistoryConverter):
    # Class Variables
    substitutions = {
        "LEGAL_ISO": "EUR",  # legal ISO currency codes
        "LS": "\u20ac",  # legal currency symbols
        "PLYR": r"(?P<PNAME>.+?)"
    }
    limits = {"No Limit": "nl"}
    games = {"Hold'em": "hold"}

    # Static regexes
    re_SplitHands = re.compile("(?:\s?\n){2,}")
    re_GameInfo = re.compile(
        r"""
          (PokerStars|POKERSTARS)\sHand\s\#(?P<HID>\d+):\s(Tournament|TOURNAMENT)\s\#(?P<TOURNO>\d+),\s
          (?P<BUYIN>(?P<BIAMT>(?P<BILS>%(LS)s)[.\d]+)\+?(?P<FEE>[%(LS)s.\d]+)?\+?(?P<BOUNTY>[%(LS)s.\d]+)?\s(?P<BICURRENCY>%(LEGAL_ISO)s))\s
          (?P<GAME>Hold'em|HOLD'EM)\s(?P<LIMIT>No\sLimit|NO\sLIMIT)\s
          -\s(Level|LEVEL)\s([IVXLC]+)\s\((?P<SB>\d+)/(?P<BB>\d+)\)
          (\s(?P<ADM>\[(ADM|AAMS)\sID:\s[A-Z\d]+\]))?
          \s-\s(?P<DATETIME>.*$)
        """
        % substitutions,
        re.MULTILINE | re.VERBOSE
    )
    re_DateTime = re.compile(r"(?P<Y>\d{4})\/(?P<M>\d{2})\/(?P<D>\d{2})[\- ]+(?P<H>\d{1,2}):(?P<MIN>\d{2}):(?P<S>\d{2})")
    re_HandInfo = re.compile(r"Table\s\'(?P<TABLE>.+?)\'\s((?P<MAX>\d+)-[Mm]ax)")
    re_Button = re.compile(r"Seat #(?P<BUTTON>\d+) is the button")
    re_PlayerInfo = re.compile(r"Seat\s(?P<SEAT>\d+):\s%(PLYR)s\s\((?P<CASH>\d+)\sin\schips(,\s%(LS)s(?P<BOUNTY>[.\d]+)\sbounty)?\)" % substitutions)
    re_Antes = re.compile(r"%(PLYR)s:\sposts\sthe\sante\s(?P<ANTE>\d+)" % substitutions)
    re_PostSB = re.compile(r"%(PLYR)s:\sposts\ssmall\sblind\s(?P<SB>\d+)" % substitutions)
    re_PostBB = re.compile(r"%(PLYR)s:\sposts\sbig\sblind\s(?P<BB>\d+)" % substitutions)
    re_HeroCards = re.compile(r"Dealt\sto\s%(PLYR)s\s(\[(?P<CARDS>.+?)\])" % substitutions)
    re_Board = re.compile(r"\[(?P<CARDS>.+)\]")
    re_Action = re.compile(r"%(PLYR)s:(?P<ATYPE>\sbets|\schecks|\sraises|\scalls|\sfolds)(\s(?P<BET>\d+))?(\sto\s(?P<BETTO>\d+))?\s*(and\sis\sall.in)?" % substitutions)
    re_Uncalled = re.compile(r"Uncalled\sbet\s\((?P<BET>\d+)\)\sreturned\sto\s%(PLYR)s$" % substitutions, re.MULTILINE)
    # Kaor89 wins €0.45 for eliminating campisi1995 and their own bounty increases by €0.45 to €1.35
    # Berry67 wins €0.23 for splitting the elimination of Iroshi1 and their own bounty increases by €0.22 to €1.12
    re_Bounty = re.compile(r"%(PLYR)s\swins\s%(LS)s(?P<BOUNTY>[.\d]+)\sfor\s(splitting\sthe\selimination\sof|eliminating)\s.+?\sand\stheir\sown\sbounty\sincreases\sby\s%(LS)s[.\d]+\sto\s%(LS)s(?P<ENDBOUNTY>[.\d]+)" % substitutions)
    re_ShownCards = re.compile(r"Seat\s\d+:\s%(PLYR)s\s((\(button\)|\(small\sblind\)|\(big\sblind\)|\(button\)\s\(small\sblind\))\s)?(showed|mucked)\s\[(?P<CARDS>.*)\]" % substitutions)

    def read_supported_games(self):
        return [["hold", "nl"]]

    def determine_game_type(self, hand_text):
        info = {}

        try:
            m = self.re_GameInfo.search(hand_text)

            if not m:
                log.error(f"PokerStarsToFpdb.determine_game_type: '{self.file}'")
                raise FpdbParseError

            mg = m.groupdict()

            info["limitType"] = self.limits[mg["LIMIT"]]
            info["base"] = self.games[mg["GAME"]]
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
            m = self.re_GameInfo.search(hand.hand_text)
            m2 = self.re_HandInfo.search(hand.hand_text)

            if m is None or m2 is None:
                log.error(f"PokerStarsToFpdb.read_hand_info: '{self.file}'")
                raise FpdbParseError

            info.update(m.groupdict())
            info.update(m2.groupdict())

            hand.hand_no = int(info["HID"])
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
                hand.ko_bounty = float(info["BOUNTY"])
                hand.is_ko = True
            else:
                hand.is_ko = False

            info["FEE"] = info["FEE"].strip(ls)
            hand.buy_in = float(info["BIAMT"]) + hand.ko_bounty
            hand.fee = float(info["FEE"])

            if info["ADM"] is not None:
                hand.is_private = False
            else:
                hand.is_private = True
                hand.speed = "Turbo"

            m3 = self.re_DateTime.finditer(info["DATETIME"])
            a = next(m3)
            hand.start_time = f"{a.group('Y')}/{a.group('M')}/{a.group('D')} {a.group('H')}:{a.group('MIN')}:{a.group('S')}"

            table_split = re.split(" ", info["TABLE"])
            hand.table_name = f"Tournament {hand.tour_no} Table {table_split[1]}"
            hand.game_type["maxSeats"] = int(info["MAX"])

            speed = PokerStarsStructures.SNG_STRUCTURES.get((hand.buy_in, hand.fee, hand.game_type["maxSeats"]))

            if speed is not None:
                hand.speed = speed
                hand.is_sng = True
        except Exception as e:
            log.error(f"PokerStarsToFpdb.determine_game_type: '{e}'")
            raise FpdbParseError

    def read_button(self, hand):
        m = self.re_Button.search(hand.hand_text)
        hand.button_pos = int(m.group("BUTTON"))

    def read_player_stacks(self, hand):
        for m in self.re_PlayerInfo.finditer(hand.hand_text):
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
        m = self.re_Board.search(hand.streets[street])
        hand.set_community_cards(street, m.group("CARDS").split(" "))

    def read_antes(self, hand):
        for m in self.re_Antes.finditer(hand.hand_text):
            hand.add_ante(m.group("PNAME"), m.group("ANTE"))

    def read_blinds(self, hand):
        m = self.re_PostSB.search(hand.hand_text)
        m2 = self.re_PostBB.search(hand.hand_text)

        if m:
            hand.add_blind(m.group("PNAME"), "small blind", m.group("SB"))

        if m2:
            hand.add_blind(m2.group("PNAME"), "big blind", m2.group("BB"))

    def read_hole_cards(self, hand):
        street = "PREFLOP"
        m = self.re_HeroCards.search(hand.streets[street])
        hand.hero = m.group("PNAME")
        cards = m.group("CARDS").split(" ")
        hand.add_hole_cards(hand.hero, cards)

    def read_action(self, hand, street):
        if not hand.streets[street]:
            return

        m = self.re_Action.finditer(hand.streets[street])

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

        m = self.re_Uncalled.search(hand.streets[street])

        if m:
            hand.add_uncalled(street, m.group("PNAME"), m.group("BET"))

    def read_bounty(self, hand):
        for m in self.re_Bounty.finditer(hand.hand_text):
            if m.group("PNAME") not in hand.won_bounty:
                hand.won_bounty[m.group("PNAME")] = 0

            hand.won_bounty[m.group("PNAME")] += float(m.group("BOUNTY"))
            hand.end_bounty[m.group("PNAME")] = float(m.group("ENDBOUNTY"))

    def read_shown_cards(self, hand):
        for m in self.re_ShownCards.finditer(hand.hand_text):
            cards = m.group("CARDS").split(" ")

            hand.add_hole_cards(m.group("PNAME"), cards)

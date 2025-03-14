import codecs
from decimal import Decimal
import logging
import re

from Exceptions import FpdbParseError

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("parser")

SUBSTITUTIONS = {
    "LEGAL_ISO": "EUR",  # legal ISO currency codes
    "LS": "\u20ac",  # legal currency symbols
    "PLYR": r"(?P<PNAME>.+?)"
}
RE_TOURNEY_INFO = re.compile(
    r"""
        PokerStars\sTournament\s\#(?P<TOURNO>\d+),\sNo\sLimit\sHold'em\s
        Buy-In:\s%(LS)s[.\d]+\/%(LS)s?[.\d]+\s%(LEGAL_ISO)s\s
        (?P<ENTRIES>\d+)\splayers\s
        Total\sPrize\sPool:\s%(LS)s(?P<PRIZEPOOL>[.\d]+)\s%(LEGAL_ISO)s\s+
        Tournament\sstarted\s(?P<DATETIME>.*$)
    """
    % SUBSTITUTIONS,
    re.MULTILINE | re.VERBOSE
)
RE_DATE_TIME = re.compile(r"(?P<Y>\d{4})\/(?P<M>\d{2})\/(?P<D>\d{2})[\- ]+(?P<H>\d{1,2}):(?P<MIN>\d{2}):(?P<S>\d{2})")
RE_PLAYER = re.compile(r"(?P<RANK>\d+):\s%(PLYR)s(\s\[\d+\])?\s\(.+,\s((?P<LS>%(LS)s)(?P<WINNINGS>[.\d]+))?" % SUBSTITUTIONS)

class PokerStarsSummary(object):
    def __init__(self, file, hero_name):
        self.file = file
        self.hero_name = hero_name
        self.file_text = None
        self.tour_no = None
        self.entries = None
        self.prize_pool = None
        self.start_time = None
        self.rank = 0
        self.winnings = 0

        self.start()

    def start(self):
        self.read_file()
        self.read_tourney_info()

    def read_file(self):
        try:
            with codecs.open(self.file, "r", "utf-8") as file_reader:
                whole_file = file_reader.read().replace("\r\n", "\n").replace("\xa0", " ")
                file_reader.close()

            self.file_text = whole_file.rstrip()
        except Exception as e:
            log.error(f"Failed to read file {self.file}: {e}")
            raise FpdbParseError

    def read_tourney_info(self):
        info = {}

        try:
            m = RE_TOURNEY_INFO.search(self.file_text)

            if m is None:
                log.error(f"PokerStarsSummary.read_tourney_info: '{self.file}'")
                raise FpdbParseError

            info.update(m.groupdict())

            self.tour_no = int(info["TOURNO"])
            self.entries = int(info["ENTRIES"])
            self.prize_pool = Decimal(info["PRIZEPOOL"])

            m2 = RE_DATE_TIME.finditer(info["DATETIME"])
            a = next(m2)
            self.start_time = f"{a.group('Y')}/{a.group('M')}/{a.group('D')} {a.group('H'):0>2}:{a.group('MIN')}:{a.group('S')}"

            m3 = RE_PLAYER.finditer(self.file_text)

            for player in m3:
                mg = player.groupdict()

                name = mg["PNAME"]

                if self.hero_name == name:
                    self.rank = int(mg["RANK"])

                    if mg["WINNINGS"] is not None:
                        ls = mg["LS"]
                        self.winnings = Decimal(mg["WINNINGS"].strip(ls))

                    break
        except Exception as e:
            log.error(f"PokerStarsSummary.read_tourney_info: '{e}'")
            raise FpdbParseError

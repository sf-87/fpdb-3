from abc import ABC, abstractmethod
import codecs
import logging
import re

from Exceptions import FpdbParseError
import Hand

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("handHistoryConverter")

class HandHistoryConverter(ABC):
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

        hand_list = re.split(self.re_SplitHands, self.obs)

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

    # These functions are parse actions that may be overridden by the inheriting class

    @abstractmethod
    def read_supported_games(self):
        pass

    @abstractmethod
    def determine_game_type(self, hand_text):
        pass

    @abstractmethod
    def read_hand_info(self, hand):
        pass

    @abstractmethod
    def read_player_stacks(self, hand):
        pass

    @abstractmethod
    def mark_streets(self, hand):
        pass

    @abstractmethod
    def read_blinds(self, hand):
        pass

    @abstractmethod
    def read_antes(self, hand):
        pass

    @abstractmethod
    def read_button(self, hand):
        pass

    @abstractmethod
    def read_hole_cards(self, hand):
        pass

    @abstractmethod
    def read_action(self, hand, street):
        pass

    @abstractmethod
    def read_shown_cards(self, hand):
        pass

    @abstractmethod
    def read_bounty(self, hand):
        pass

    def read_file(self):
        try:
            with codecs.open(self.file, "r", "utf-8") as file_reader:
                whole_file = file_reader.read().replace("\r\n", "\n").replace("\xa0", " ")
                file_reader.close()

            self.obs = whole_file[self.index :].rstrip()
            self.index = len(whole_file)
        except Exception as e:
            log.error(f"Failed to read file {self.file}: {e}")

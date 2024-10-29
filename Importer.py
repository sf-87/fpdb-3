from datetime import datetime
import logging
import os
from time import time
import zmq

from Exceptions import FpdbParseError
import PokerStarsSummary
import PokerStarsToFpdb

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("importer")

class ZMQSender:
    def __init__(self, port="5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.socket.bind(f"tcp://127.0.0.1:{port}")
        log.info(f"ZMQ sender initialized on port {port}")

    def send_hand_id(self, hand_id):
        try:
            self.socket.send_string(str(hand_id))
            log.debug(f"Sent hand ID {hand_id} via ZMQ")
        except zmq.ZMQError as e:
            log.error(f"Failed to send hand ID {hand_id}: {e}")

    def close(self):
        self.socket.close()
        self.context.term()
        log.info("ZMQ sender closed")

class FPDBFile(object):
    def __init__(self, path, ftype):
        self.path = path
        self.ftype = ftype  # Valid: hh, summary
        self.id = 0

    def set_id(self, db):
        file = os.path.basename(self.path)

        self.id = db.get_file_id(file)

        if self.id == 0:
            self.id = db.insert_file([file, datetime.now(), 0, 0, 0, 0, False])
            db.commit()

class Importer(object):
    def __init__(self, db, parent=None):
        self.db = db
        self.parent = parent
        self.zmq_sender = None
        self.dir_list = []
        self.file_list = {}
        self.updated_size = {}
        self.updated_time = {}
        self.pos_in_file = {}  # dict to remember how far we have read in the file

    # Set functions
    def clear_file_list(self):
        self.file_list = {}
        self.updated_size = {}
        self.pos_in_file = {}

    def log_import(self, stored, duplicates, errors, id):
        hands = stored + duplicates + errors
        self.db.update_file([datetime.now(), hands, stored, duplicates, errors, True, id])
        self.db.commit()

    # Add an individual file to file_list
    def add_import_file(self, file, file_name):
        if self.file_list.get(file) is not None:
            return False

        if file_name.startswith("HH"):
            file_type = "hh"
        elif file_name.startswith("TS"):
            file_type = "summary"
        else:
            log.error(f"Importer.add_import_file: Failed for: '{file}'")
            return False

        fpdb_file = FPDBFile(file, file_type)
        fpdb_file.set_id(self.db)

        self.file_list[file] = fpdb_file

        return True

    # Called from GuiBulkImport to add a directory.
    def add_bulk_import_dir(self, path):
        # Add files for bulk import
        for subdir in os.walk(path):
            for file in subdir[2]:
                self.add_import_file(os.path.join(subdir[0], file), file)

    # Called from GuiAutoImport to add a directory.
    def add_auto_import_dir(self, path):
        if os.path.isdir(path):
            self.dir_list.append(path)
        else:
            log.warning(f"Attempted to add non-directory '{str(path)}' as an import directory")

    def check_for_files(self):
        for path in self.dir_list:
            for subdir in os.walk(path):
                for file in subdir[2]:
                    file_name = os.path.join(subdir[0], file)

                    if (time() - os.stat(file_name).st_mtime) <= 300:
                        self.add_import_file(file_name, file)

    def run_import(self):
        # Run full import on self.file_list. This is called from GuiBulkImport.py
        log.info(f"Started at {datetime.now()} -- {len(self.file_list)} files to import.")

        return self.import_files()

    def import_files(self):
        # Read filenames in self.file_list and pass to despatcher.
        tot_stored = 0
        tot_duplicates = 0
        tot_errors = 0

        # prepare progress popup window
        progress_dialog = ImportProgressDialog(len(self.file_list), self.parent)
        progress_dialog.resize(500, 200)
        progress_dialog.show()

        for path, f in list(self.file_list.items()):
            progress_dialog.progress_update(os.path.basename(path))

            if f.ftype == "hh":
                stored, duplicates, errors = self.import_hh_file(f)
            elif f.ftype == "summary":
                stored, duplicates, errors = self.import_summary_file(f, self.db.hero_name)

            tot_stored += stored
            tot_duplicates += duplicates
            tot_errors += errors

            self.log_import(stored, duplicates, errors, f.id)

        progress_dialog.accept()
        del progress_dialog

        return tot_stored, tot_duplicates, tot_errors

    # Run import on updated files, then store latest update time. Called from GuiAutoImport.py
    def run_updated(self):
        # Check for new files in monitored directories
        self.check_for_files()

        for path, f in list(self.file_list.items()):
            if os.path.exists(path):
                stat_info = os.stat(path)

                if path in self.updated_size:  # we should be able to assume that if we're in size, we're in time as well
                    if stat_info.st_size > self.updated_size[path] or stat_info.st_mtime > self.updated_time[path]:
                        if f.ftype == "hh":
                            stored, duplicates, errors = self.import_hh_file(f)
                        elif f.ftype == "summary":
                            stored, duplicates, errors = self.import_summary_file(f, self.db.hero_name)

                        self.log_import(stored, duplicates, errors, f.id)

                        try:
                            # Note: This assumes that whatever calls us has an "add_text" func
                            self.parent.add_text(f"{os.path.basename(path)} {stored} stored, {duplicates} duplicates, {errors} errors")
                        except KeyError:  # TODO: Again, what error happens here? fix when we find out ..
                            pass

                        self.updated_size[path] = stat_info.st_size
                        self.updated_time[path] = time()
                else:
                    if (time() - stat_info.st_mtime) < 60:
                        self.updated_size[path] = 0
                        self.updated_time[path] = 0
                    else:
                        self.updated_size[path] = stat_info.st_size
                        self.updated_time[path] = time()

    def import_hh_file(self, f):
        stored, duplicates, errors = 0, 0, 0

        log.info(f"Converting {f.path}")

        if f.path in self.pos_in_file:
            index = self.pos_in_file[f.path]
        else:
            self.pos_in_file[f.path], index = 0, 0

        hhc = PokerStarsToFpdb.PokerStars(f.path, index, self.parent.__module__ == "GuiAutoImport")

        self.pos_in_file[f.path] = hhc.index

        # Tally the results
        errors = hhc.num_errors
        stored = hhc.num_hands - errors

        if stored > 0:
            if self.parent:
                self.progress_notify()

            hand_list = hhc.processed_hands
            to_hud = []

            ####Lock Placeholder####
            for hand in hand_list:
                hand.prep_insert(self.db)

            self.db.commit()
            ####Lock Placeholder####

            for hand in hand_list:
                hand.assemble_hand(f.id)
                hand.assemble_hand_players()
                hand.assemble_hand_actions()

            ####Lock Placeholder####
            for hand in hand_list:
                try:
                    if self.db.is_hand_duplicate(hand.hand_no):
                        duplicates += 1
                    else:
                        hand.id = self.db.insert_hand(list(hand.hand.values()))
                        self.db.store_hand_players(hand.id, hand.players_ids, hand.hand_players)
                        self.db.store_hand_actions(hand.id, hand.players_ids, hand.hand_actions)
                        self.db.store_hud_cache(hand.game_type_id, hand.players_ids, hand.hand_players)

                        if hand.hero in hand.won_bounty:
                            self.db.update_tourney_bounties([hand.won_bounty[hand.hero], hand.tourney_id])

                        to_hud.append(hand.id)
                except Exception as e:
                    log.error(f"Importer.import_hh_file: '{f.path}' Fatal error: '{e}'")

            self.db.commit()
            ####Lock Placeholder####

            # Pipe the hand.id out to the HUD
            if self.parent.__module__ == "GuiAutoImport":
                if self.zmq_sender is None:
                    self.zmq_sender = ZMQSender()

                for hand_id in to_hud:
                    try:
                        log.debug(f"Sending hand ID {hand_id} to HUD via socket")

                        self.zmq_sender.send_hand_id(hand_id)
                    except IOError as e:
                        log.error(f"Failed to send hand ID to HUD via socket: {e}")

        stored -= duplicates

        return stored, duplicates, errors

    def import_summary_file(self, f, hero_name):
        stored, duplicates, errors = 0, 0, 0

        log.info(f"Converting {f.path}")

        try:
            tsc = PokerStarsSummary.PokerStarsSummary(f.path, hero_name)
            tourney_id = self.db.get_tourney_id(tsc.tour_no)

            if tourney_id == 0:
                log.error(f"Tourney {tsc.tour_no} does not exists")
                raise FpdbParseError

            stored = 1
        except FpdbParseError:
            log.error(f"Summary import parse error in file: {f.path}")
            errors = 1

        if stored > 0:
            if self.parent:
                self.progress_notify()

            data = [tsc.entries, tsc.prize_pool, tsc.start_time, tsc.rank, tsc.winnings, tourney_id]

            self.db.update_tourney(data)
            self.db.commit()

        return stored, duplicates, errors

    def progress_notify(self):
        QCoreApplication.processEvents()

    def __del__(self):
        if hasattr(self, "zmq_sender"):
            self.zmq_sender.close()

class ImportProgressDialog(QDialog):
    # Popup window to show progress
    # Init method sets up total number of expected iterations
    # If no parent is passed to init, command line
    # mode assumed, and does not create a progress bar
    def __init__(self, total, parent):
        if parent is None:
            return
        super().__init__(parent)
        self.fraction = 0
        self.total = total
        self.p_bar = QProgressBar()
        self.p_text = QLabel()

        self.setWindowTitle("Importing")
        self.p_bar.setRange(0, total)
        self.p_text.setWordWrap(True)

        box = QVBoxLayout()
        box.addWidget(self.p_bar)
        box.addWidget(self.p_text)

        self.setLayout(box)

    def progress_update(self, file):
        self.fraction += 1

        # update total if fraction exceeds expected total number of iterations
        if self.fraction > self.total:
            self.total = self.fraction
            self.p_bar.setRange(0, self.total)

        self.p_bar.setValue(self.fraction)

        now = datetime.now().strftime("%H:%M:%S")
        self.p_text.setText(f"{now} - Importing {file}\n")

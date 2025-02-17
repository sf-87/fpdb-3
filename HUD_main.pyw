import Configuration

Configuration.set_log_file("HUD-log.txt")

from cachetools import TTLCache
import codecs
import contextlib
import copy
import logging
import os
from qt_material import apply_stylesheet
import sys
import time
import zmq

import Database
import Hud
import TableWindow

from PyQt5.QtCore import pyqtSignal, QCoreApplication, QObject, Qt, QThread, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

log = logging.getLogger("hud")

class ZMQWorker(QThread):
    def __init__(self, zmq_receiver):
        super().__init__()
        self.zmq_receiver = zmq_receiver
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                self.zmq_receiver.process_message()
            except Exception as e:
                log.error(f"Error in ZMQWorker: {e}")

            time.sleep(0.01)  # Short delay to avoid excessive CPU usage

    def stop(self):
        self.is_running = False
        self.wait()

class ZMQReceiver(QObject):
    message_received = pyqtSignal(str)

    def __init__(self, interval, port="5555", parent=None):
        super().__init__(parent)
        self.interval = interval
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect(f"tcp://127.0.0.1:{port}")
        self.poller = zmq.Poller()

        log.info(f"ZMQ receiver connected on port {port}")

        # Heartbeat configuration
        self.poller.register(self.socket, zmq.POLLIN)

    def process_message(self):
        try:
            socks = dict(self.poller.poll(self.interval * 1000))

            if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                hand_id = self.socket.recv_string(zmq.NOBLOCK)
                log.debug(f"Received hand ID: {hand_id}")
                self.message_received.emit(hand_id)
            else:
                # Heartbeat
                log.debug("Heartbeat: No message received")
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass  # No message available
            else:
                log.error(f"ZMQ error: {e}")

    def close(self):
        self.socket.close()
        self.context.term()
        log.info("ZMQ receiver closed")

class HUD_main(QObject):
    # A main() object to own both the socket thread and the gui.
    def __init__(self):
        super().__init__()
        self.config = Configuration.Config()
        self.db = Database.Database(self.config)
        self.interval = self.config.imp.interval
        self.hud_params = self.config.hud_ui
        self.cache = None
        self.zmq_receiver = None
        self.zmq_worker = None
        self.main_window = None
        self.hud_dict = {}

        file = os.path.join(Configuration.LOG_PATH, "HUD-errors.txt")
        log.info(f"Note: error output is being diverted to {file}. Any major error will be reported there _only_.")
        sys.stderr = codecs.open(file, "w", "utf-8")

        log.info("HUD_main starting")

        try:
            # Cache initialization
            self.cache = TTLCache(maxsize=1000, ttl=300)  # Cache of 1000 elements with a TTL of 5 minutes
            # Initialization ZMQ with QThread
            self.zmq_receiver = ZMQReceiver(self.interval, parent=self)
            self.zmq_receiver.message_received.connect(self.handle_message)
            self.zmq_worker = ZMQWorker(self.zmq_receiver)
            self.zmq_worker.start()

            # Main window
            self.init_main_window()

            log.debug("Main window initialized and shown.")
        except Exception as e:
            log.error(f"Error during HUD_main initialization: {e}")
            raise

    def init_main_window(self):
        self.main_window = QWidget(None, Qt.Dialog | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.main_window.destroyed.connect(self.destroy)
        self.main_window.closeEvent = self.close_event_handler

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(2, 0, 2, 0)
        self.layout.addWidget(QLabel("Closing this window will exit from the HUD."))

        self.main_window.setWindowTitle("HUD Main Window")
        icon = os.path.join(Configuration.GRAPHICS_PATH, "tribal.jpg")

        if os.path.exists(icon):
            self.main_window.setWindowIcon(QIcon(icon))

        # Timer for periodically checking tables
        check_tables_timer = QTimer(self)
        check_tables_timer.timeout.connect(self.check_tables)
        check_tables_timer.start(1000)

        self.main_window.setLayout(self.layout)
        self.main_window.show()

    def close_event_handler(self, event):
        self.zmq_worker.stop()
        self.zmq_receiver.close()
        self.destroy()
        event.accept()

    def handle_message(self, hand_id):
        # This method will be called in the main thread
        self.read(hand_id)

    def destroy(self):
        log.info("Quitting normally")
        QCoreApplication.quit()

    def check_tables(self):
        for hud in list(self.hud_dict.values()):
            if not hud.table.check_table():
                self.kill_hud(hud.table_name)

    def table_is_stale(self, hud):
        log.debug("Moved to a new table, killing current HUD")
        self.kill_hud(hud.table_name)

    def kill_hud(self, table_name):
        try:
            if table_name in self.hud_dict:
                self.layout.removeWidget(self.hud_dict[table_name].table_hud_label)
                self.hud_dict[table_name].table_hud_label.setParent(None)
                self.hud_dict[table_name].kill()
                del self.hud_dict[table_name]

            self.main_window.resize(1, 1)
        except Exception:
            log.exception(f"Error killing HUD for table: {table_name}.")

    def create_hud(self, hand_id, table, table_name, max_seats, stat_dict):
        log.debug(f"Creating HUD for table {table_name} and hand {hand_id}")

        try:
            self.hud_dict[table_name] = Hud.Hud(self, table, table_name, max_seats, self.config, stat_dict, copy.deepcopy(self.hud_params))

            table.hud = self.hud_dict[table_name]

            new_label = QLabel(f"{table_name}")
            self.layout.addWidget(new_label)

            self.hud_dict[table_name].table_hud_label = new_label
            self.hud_dict[table_name].aux_window.create()
            log.debug(f"HUD for table {table_name} created successfully.")
        except Exception:
            log.exception(f"Error creating HUD for hand {hand_id}.")

    def update_hud(self, hand_id, table_name):
        log.debug(f"Updating HUD for table {table_name} and hand {hand_id}")

        try:
            self.hud_dict[table_name].aux_window.update_gui()
        except Exception:
            log.exception(f"Error updating HUD for hand {hand_id}.")

    def read(self, hand_id):
        log.debug(f"Processing new hand id: {hand_id}")

        if hand_id != "":
            log.debug("HUD_main.read: Hand processing starting.")

            if hand_id in self.cache:
                log.debug(f"Using cached data for hand {hand_id}")

                table_info = self.cache[hand_id]
            else:
                log.debug(f"Data not found in cache for hand_id: {hand_id}")

                try:
                    table_info = self.db.get_table_info(hand_id)

                    self.cache[hand_id] = table_info
                except Exception as e:
                    log.error(f"Database error while processing hand {hand_id}: {e}")
                    return

        tourney_no, table_name, max_seats, num_seats = table_info

        # Managing table changes for tournaments
        if table_name in self.hud_dict:
            if self.hud_dict[table_name].table.has_table_title_changed():
                log.debug("Table has been renamed")
                self.table_is_stale(self.hud_dict[table_name])
                return
        else:
            for k in list(self.hud_dict.keys()):
                log.debug("Check if the tournament number is in the hud_dict under a different table")

                if k.startswith(f"Tournament {tourney_no}"):
                    self.table_is_stale(self.hud_dict[k])
                    continue

        # Detection of max_seats changes
        if table_name in self.hud_dict:
            with contextlib.suppress(Exception):
                new_max = self.hud_dict[table_name].new_max_seats

                if new_max is not None and self.hud_dict[table_name].max_seats != new_max:
                    log.debug("Going to kill_hud due to max seats change")
                    self.kill_hud(table_name)

                    while table_name in self.hud_dict:
                        time.sleep(0.5)

                    max_seats = new_max

                self.hud_dict[table_name].new_max_seats = None

        # Updating or creating the HUD
        if table_name in self.hud_dict:
            log.debug(f"Update HUD for hand {hand_id}")
            stat_dict = self.db.get_stats_from_hand(hand_id, self.hud_dict[table_name].hud_params, num_seats)
            log.debug(f"Got stats for hand {hand_id}")

            self.hud_dict[table_name].stat_dict = stat_dict

            log.debug(f"Updating HUD for table {table_name} and hand {hand_id}")
            self.update_hud(hand_id, table_name)
            log.debug(f"HUD updated for table {table_name} and hand {hand_id}")
        else:
            log.debug(f"Create new HUD for hand {hand_id}")
            stat_dict = self.db.get_stats_from_hand(hand_id, self.hud_params, num_seats)
            log.debug(f"Got stats for hand {hand_id}")

            table_window = TableWindow.TableWindow(table_name, max_seats, tourney_no)

            if table_window.number is None:
                log.error(f"HUD create: table name {table_name} not found, skipping.")
                return
            else:
                self.create_hud(hand_id, table_window, table_name, max_seats, stat_dict)

if __name__ == "__main__":
    app = QApplication([])
    apply_stylesheet(app, theme="dark_purple.xml")
    hm = HUD_main()
    app.exec_()

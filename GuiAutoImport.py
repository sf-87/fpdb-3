import logging
import subprocess
import traceback

import Configuration
import Importer

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QTextEdit, QVBoxLayout, QWidget

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("importer")

class GuiAutoImport(QWidget):
    def __init__(self, global_lock, db, config, parent):
        super().__init__(parent)
        self.global_lock = global_lock
        self.db = db
        self.interval = config.imp.interval
        self.import_dirs = [config.site.hh_path, config.site.ts_path]
        self.importer = Importer.Importer(db, self)
        self.import_timer = None
        self.pipe_to_hud = None
        self.do_auto_import = False
        self.start_button = QCheckBox("Start Auto Import")
        self.text_view = QTextEdit()

        self.start_button.stateChanged.connect(self.start_clicked)
        self.text_view.setReadOnly(True)

        import_box = QVBoxLayout()
        browse_box = QHBoxLayout()
        browse_box.addWidget(self.start_button)
        import_box.addLayout(browse_box)
        import_box.addWidget(self.text_view)

        self.setLayout(import_box)

        self.add_text("Auto Import Ready.")

    def add_text(self, text):
        self.text_view.moveCursor(QTextCursor.End)
        self.text_view.insertPlainText(f"{text}\n")

    def do_import(self):
        # Callback for timer to do an import iteration.

        if self.do_auto_import:
            self.importer.run_updated()

    def start_clicked(self):
        # Runs when user clicks start on auto import tab

        if self.start_button.isChecked():
            # - Ideally we want to release the lock if the auto-import is killed by some
            # kind of exception - is this possible?
            if self.global_lock.acquire("GuiAutoImport"):
                self.add_text("Global lock taken. Auto Import Started.")
                self.do_auto_import = True

                if self.pipe_to_hud is None:
                    try:
                        if Configuration.INSTALL_METHOD == "exe":
                            command = "HUD_main.exe"
                        #else:
                        #    command = f"python \"{Configuration.FPDB_ROOT_PATH}\HUD_main.pyw\""

                        if Configuration.INSTALL_METHOD == "exe":
                            self.pipe_to_hud = subprocess.Popen(
                                command,
                                bufsize=0,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True
                            )
                        #else:
                        #    self.pipe_to_hud = subprocess.Popen(command, bufsize=0, stdin=subprocess.PIPE, universal_newlines=True)
                    except Exception:
                        self.add_text(f"*** GuiAutoImport Error opening pipe: {traceback.format_exc()}")
                    else:
                        for path in self.import_dirs:
                            self.importer.add_auto_import_dir(path)
                            self.add_text(f"* Add import directory {path}")

                        self.do_import()

                        self.import_timer = QTimer()
                        self.import_timer.timeout.connect(self.do_import)
                        self.import_timer.start(self.interval * 1000)
            else:
                self.add_text("Auto import aborted - global lock not available")
        else:  # toggled off
            self.do_auto_import = False
            self.import_timer = None

            self.global_lock.release()

            self.add_text("Stopping Auto Import. Global lock released.")

            if self.pipe_to_hud and self.pipe_to_hud.poll() is not None:
                self.add_text("Stop Auto Import: HUD already terminated.")
            else:
                if self.pipe_to_hud:
                    self.pipe_to_hud.terminate()

                self.pipe_to_hud = None

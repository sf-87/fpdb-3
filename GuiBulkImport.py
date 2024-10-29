import logging

import Importer

from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("importer")

class GuiBulkImport(QWidget):
    def __init__(self, global_lock, db, config, parent):
        super().__init__(parent)
        self.global_lock = global_lock
        self.db = db
        self.importer = Importer.Importer(db, self)
        self.import_dir = QLineEdit(config.site.hh_path)

        import_box = QVBoxLayout()
        browse_box = QHBoxLayout()
        browse_box.addWidget(self.import_dir)
        choose_button = QPushButton("Browse...")
        choose_button.clicked.connect(self.browse_clicked)
        browse_box.addWidget(choose_button)
        import_box.addLayout(browse_box)
        load_button = QPushButton(("Bulk Import"))
        load_button.clicked.connect(self.load_clicked)
        import_box.addWidget(load_button)

        self.setLayout(import_box)

    def load_clicked(self):
        stored, duplicates, errors = 0, 0, 0

        if self.global_lock.acquire("GuiBulkImport"):
            # get the dir to import from the chooser
            selected = self.import_dir.text()

            self.importer.add_bulk_import_dir(selected)

            stored, duplicates, errors = self.importer.run_import()

            log.info(f"Bulk import done: Stored: {stored}, Duplicates: {duplicates}, Errors: {errors}")

            self.importer.clear_file_list()

            self.global_lock.release()
        else:
            log.error("Bulk import aborted - global lock not available")

    def browse_clicked(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Please choose the path that you want to Import", self.import_dir.text())

        if new_dir:
            self.import_dir.setText(new_dir)

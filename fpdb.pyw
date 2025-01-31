import Configuration

Configuration.set_log_file("fpdb-log.txt")

import codecs
import logging
import os
import sys

import Database
from Exceptions import FpdbError
import GuiAutoImport
import GuiBulkImport
import GuiTourneyGraphViewer
import GuiTourneyPlayerStats
import interlocks

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QMessageBox, QTabWidget, QVBoxLayout, QWidget

log = logging.getLogger("fpdb")

class fpdb(QMainWindow):
    def __init__(self):
        super().__init__()
        self.global_lock = interlocks.InterProcessLockWin32(name="fpdb_global_lock")
        self.config = None
        self.db = None
        self.threads = []
        self.pages = []
        self.nb_tab_names = []
        self.nb = QTabWidget()

        self.setWindowTitle("Free Poker DB 3")
        icon = os.path.join(Configuration.GRAPHICS_PATH, "tribal.jpg")

        if os.path.exists(icon):
            self.setWindowIcon(QIcon(icon))

        self.move(0, 0)
        sg = QApplication.primaryScreen().availableGeometry()
        self.resize(sg.width(), sg.height())

        # Create central widget and layout
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        # Add menu bar to layout
        menu_bar = self.menuBar()
        central_layout.setMenuBar(menu_bar)

        self.nb.setTabsClosable(True)
        self.nb.tabCloseRequested.connect(self.close_tab)
        central_layout.addWidget(self.nb)
        self.setCentralWidget(central_widget)

        self.create_menu_bar()
        self.load_profile()
        
        self.showMaximized()

        file = os.path.join(Configuration.LOG_PATH, "fpdb-errors.txt")
        log.info(f"Note: error output is being diverted to {file}. Any major error will be reported there _only_.")
        sys.stderr = codecs.open(file, "w", "utf-8")

    def add_and_display_tab(self, new_page, new_tab_name):
        # adds a tab, namely creates the button and displays it and appends all the relevant arrays
        for i, name in enumerate(self.nb_tab_names):
            if new_tab_name == name:
                self.display_tab(i)
                return  # if tab already exists, just go to it

        used_before = False

        for i, name in enumerate(self.nb_tab_names):
            if name == new_tab_name:
                used_before = True
                page = self.pages[i]
                break

        if not used_before:
            page = new_page
            self.pages.append(new_page)
            self.nb_tab_names.append(new_tab_name)

        index = self.nb.addTab(page, new_tab_name)
        self.nb.setCurrentIndex(index)

    def display_tab(self, tab_no):
        # displays the indicated tab
        if tab_no < 0 or tab_no >= self.nb.count():
            raise FpdbError(f"invalid tab_no {tab_no}")
        else:
            self.nb.setCurrentIndex(tab_no)

    def dia_database_stats(self):
        QMessageBox(QMessageBox.Information, "Database Statistics", f"Number of Hands: {self.db.get_hand_count()}\nNumber of Tourneys: {self.db.get_tourney_count()}\nNumber of TourneyTypes: {self.db.get_tourney_type_count()}").exec_()

    def dia_recreate_tables(self):
        # Dialogue that asks user to confirm that he wants to delete and recreate the tables
        if self.global_lock.acquire("dia_recreate_tables"):
            response = QMessageBox(
                QMessageBox.Warning,
                "Recreate Tables",
                "Please confirm that you want to recreate the tables. The database will be deleted and you will have to re-import your histories.",
                QMessageBox.Yes | QMessageBox.No,
                self
            ).exec_()

            if response == QMessageBox.Yes:
                self.db.recreate_tables()

                QMessageBox(QMessageBox.Information, "Recreate Tables", "Tables recreated").exec_()
            else:
                log.info("User cancelled recreating tables")

            self.global_lock.release()
        else:
            QMessageBox(QMessageBox.Warning, "WARNING", "Cannot open Database Maintenance window because other windows have been opened. Re-start fpdb to use this option.").exec_()

    def create_menu_bar(self):
        mb = self.menuBar()
        import_menu = mb.addMenu("Import")
        hud_menu = mb.addMenu("HUD")
        tournament_menu = mb.addMenu("Tournament")
        maintenance_menu = mb.addMenu("Maintenance")

        # Create actions
        def make_action(name, callback):
            action = QAction(name, self)
            action.triggered.connect(callback)
            return action

        import_menu.addAction(make_action("Bulk Import", self.tab_bulk_import))
        hud_menu.addAction(make_action("HUD and Auto Import", self.tab_auto_import))
        tournament_menu.addAction(make_action("Tourney Graphs", self.tab_tourney_graph_viewer))
        tournament_menu.addAction(make_action("Tourney Stats", self.tab_tourney_player_stats))
        maintenance_menu.addAction(make_action("Statistics", self.dia_database_stats))
        maintenance_menu.addAction(make_action("Recreate Tables", self.dia_recreate_tables))

    def load_profile(self):
        # Loads profile from the provided path name.
        # Set:
        #    - self.config
        #    - self.db

        self.config = Configuration.Config()

        if self.config.file_error:
            QMessageBox(QMessageBox.Warning, "CONFIG FILE ERROR", "There is an error in your config file").exec_()
            sys.exit()

        self.db = Database.Database(self.config)

        if self.db is not None and self.db.is_connected:
            self.statusBar().showMessage(f"Status: Connected to database named {self.db.database}")

    def tab_auto_import(self):
        # opens the auto import tab
        new_import_thread = GuiAutoImport.GuiAutoImport(self.global_lock, self.db, self.config, self)
        self.threads.append(new_import_thread)
        self.add_and_display_tab(new_import_thread, "HUD")

    def tab_bulk_import(self):
        # opens the bulk importing tab
        new_import_thread = GuiBulkImport.GuiBulkImport(self.global_lock, self.db, self.config, self)
        self.threads.append(new_import_thread)
        self.add_and_display_tab(new_import_thread, "Bulk Import")

    def tab_tourney_player_stats(self):
        # opens a player stats tab
        new_ps_thread = GuiTourneyPlayerStats.GuiTourneyPlayerStats(self.db, self)
        self.threads.append(new_ps_thread)
        self.add_and_display_tab(new_ps_thread, "Tourney Stats")

    def tab_tourney_graph_viewer(self):
        # opens a graph viewer tab
        new_gv_thread = GuiTourneyGraphViewer.GuiTourneyGraphViewer(self.db, self)
        self.threads.append(new_gv_thread)
        self.add_and_display_tab(new_gv_thread, "Tourney Graphs")

    def close_tab(self, index):
        item = self.nb.widget(index)
        self.nb.removeTab(index)
        self.nb_tab_names.pop(index)

        try:
            self.threads.remove(item)
        except ValueError:
            pass

        item.deleteLater()

    def closeEvent(self, *args, **kwargs):
        if self.db is not None and self.db.is_connected:
            self.db.disconnect()

if __name__ == "__main__":
    from qt_material import apply_stylesheet
    app = QApplication([])
    apply_stylesheet(app, theme="dark_purple.xml")
    me = fpdb()
    app.exec_()

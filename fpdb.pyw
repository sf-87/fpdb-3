#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2008-2013 Steffen Schaumburg
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# In the "official" distribution you can find the license in agpl-3.0.txt.


import os
import sys
import queue

import codecs
import Options

cl_options = '.'.join(sys.argv[1:])
(options, argv) = Options.fpdb_options()
from L10n import set_locale_translation
import logging

from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtWidgets import QAction, QApplication, QLabel, QMainWindow, QMessageBox, QTabWidget, QVBoxLayout, QWidget

import interlocks
from Exceptions import FpdbError

import GuiLogView
import GuiBulkImport

import GuiTourneyPlayerStats
import GuiAutoImport
import GuiTourneyGraphViewer

import SQL
import Database
import Configuration

Configuration.set_logfile("fpdb-log.txt")

log = logging.getLogger("fpdb")

class fpdb(QMainWindow):
    def add_and_display_tab(self, new_page, new_tab_name):
        """adds a tab, namely creates the button and displays it and appends all the relevant arrays"""
        for name in self.nb_tab_names:  # todo: check this is valid
            if name == new_tab_name:
                self.display_tab(new_tab_name)
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

    def display_tab(self, new_tab_name):
        """displays the indicated tab"""
        tab_no = -1
        for i, name in enumerate(self.nb_tab_names):
            if new_tab_name == name:
                tab_no = i
                break

        if tab_no < 0 or tab_no >= self.nb.count():
            raise FpdbError(f"invalid tab_no {str(tab_no)}")
        else:
            self.nb.setCurrentIndex(tab_no)

    def dia_database_stats(self, widget, data=None):
        self.warning_box(
            string=f"Number of Hands: {self.db.getHandCount()}\nNumber of Tourneys: {self.db.getTourneyCount()}\nNumber of TourneyTypes: {self.db.getTourneyTypeCount()}",
            diatitle="Database Statistics"
        )

    def dia_recreate_tables(self, widget, data=None):
        """Dialogue that asks user to confirm that he wants to delete and recreate the tables"""
        if self.obtain_global_lock("fpdb.dia_recreate_tables"):  # returns true if successful
            dia_confirm = QMessageBox(
                QMessageBox.Warning,
                "Wipe DB",
                "Confirm deleting and recreating tables",
                QMessageBox.Yes | QMessageBox.No,
                self
            )
            diastring = (
                f"Please confirm that you want to (re-)create the tables. If there already are tables in"
                f" the database {self.db.database} on {self.db.host}"
                f" they will be deleted and you will have to re-import your histories.\nThis may take a while."
            )

            dia_confirm.setInformativeText(diastring)  # todo: make above string with bold for db, host and deleted
            response = dia_confirm.exec_()

            if response == QMessageBox.Yes:
                self.db.recreate_tables()
                # find any guibulkimport/guiautoimport windows and clear cache:
                for t in self.threads:
                    if isinstance(t, GuiBulkImport.GuiBulkImport) or isinstance(t, GuiAutoImport.GuiAutoImport):
                        t.importer.database.resetCache()
                self.release_global_lock()
            else:
                self.release_global_lock()
                log.info("User cancelled recreating tables")
        else:
            self.warning_box(
                "Cannot open Database Maintenance window because other"
                " windows have been opened. Re-start fpdb to use this option."
            )

    def dia_logs(self, widget, data=None):
        """opens the log viewer window"""
        # remove members from self.threads if close messages received
        self.process_close_messages()

        viewer = None
        for i, t in enumerate(self.threads):
            if str(t.__class__) == "GuiLogView.GuiLogView":
                viewer = t
                break

        if viewer is None:
            # print "creating new log viewer"
            new_thread = GuiLogView.GuiLogView(self.config, self.window, self.closeq)
            self.threads.append(new_thread)
        else:
            # print "showing existing log viewer"
            viewer.get_dialog().present()

        # if lock_set:
        #    self.release_global_lock()

    def process_close_messages(self):
        # check for close messages
        try:
            while True:
                name = self.closeq.get(False)
                for i, t in enumerate(self.threads):
                    if str(t.__class__) == str(name):
                        # thread has ended so remove from list:
                        del self.threads[i]
                        break
        except queue.Empty:
            # no close messages on queue, do nothing
            pass

    def createMenuBar(self):
        mb = self.menuBar()
        importMenu = mb.addMenu('Import')
        hudMenu = mb.addMenu('HUD')
        tournamentMenu = mb.addMenu('Tournament')
        maintenanceMenu = mb.addMenu('Maintenance')
        helpMenu = mb.addMenu('Help')

        # Create actions
        def makeAction(name, callback, shortcut=None, tip=None):
            action = QAction(name, self)
            if shortcut:
                action.setShortcut(shortcut)
            if tip:
                action.setToolTip(tip)
            action.triggered.connect(callback)
            return action

        importMenu.addAction(makeAction('Bulk Import', self.tab_bulk_import, 'Ctrl+B'))
        hudMenu.addAction(makeAction('HUD and Auto Import', self.tab_auto_import, 'Ctrl+A'))
        tournamentMenu.addAction(makeAction('Tourney Graphs', self.tabTourneyGraphViewer))
        tournamentMenu.addAction(makeAction('Tourney Stats', self.tab_tourney_player_stats, 'Ctrl+T'))
        maintenanceMenu.addAction(makeAction('Statistics', self.dia_database_stats, 'View Database Statistics'))
        maintenanceMenu.addAction(makeAction('Create or Recreate Tables', self.dia_recreate_tables))
        helpMenu.addAction(makeAction('Log Messages', self.dia_logs, 'Log and Debug Messages'))


    def load_profile(self, create_db=False):
        """Loads profile from the provided path name.
        Set:
           - self.settings
           - self.config
           - self.db
        """
        self.config = Configuration.Config(file=options.config, dbname=options.dbname)
        if self.config.file_error:
            self.warning_box(
                f"There is an error in your config file" f" {self.config.file}:\n{str(self.config.file_error)}",
                diatitle="CONFIG FILE ERROR",
            )
            sys.exit()

        log.info(f"Logfile is {os.path.join(self.config.dir_log, self.config.log_file)}")

        self.settings = {}
        self.settings["global_lock"] = self.lock
        self.settings["os"] = "windows"

        self.settings.update({"cl_options": cl_options})
        self.settings.update(self.config.get_db_parameters())
        self.settings.update(self.config.get_import_parameters())
        self.settings.update(self.config.get_default_paths())

        if self.db is not None and self.db.is_connected():
            self.db.disconnect()

        self.sql = SQL.Sql(db_server=self.settings["db-server"])
        err_msg = None
        self.db = Database.Database(self.config, sql=self.sql)
        log.info(f"Connected to SQLite: {self.db.db_path}")
        if err_msg is not None:
            self.db = None
            self.warning_box(err_msg)
        if self.db is not None and not self.db.is_connected():
            self.db = None

        if self.db is not None and self.db.wrongDbVersion:
            diaDbVersionWarning = QMessageBox(
                QMessageBox.Warning,
                "Strong Warning - Invalid database version",
                "An invalid DB version or missing tables have been detected.",
                QMessageBox.Ok,
                self
            )
            diaDbVersionWarning.setInformativeText(
                "This error is not necessarily fatal but it is strongly"
                " recommended that you recreate the tables by using the Database menu."
                "Not doing this will likely lead to misbehaviour including fpdb crashes, corrupt data etc."
            )

            diaDbVersionWarning.exec_()
        if self.db is not None and self.db.is_connected():
            self.statusBar().showMessage(f"Status: Connected to database named {self.db.database} on host {self.db.host}")

            # rollback to make sure any locks are cleared:
            self.db.rollback()

        # If the db-version is out of date, don't validate the config
        # otherwise the end user gets bombarded with false messages
        # about every site not existing
        if hasattr(self.db, "wrongDbVersion"):
            if not self.db.wrongDbVersion:
                self.validate_config()

    def obtain_global_lock(self, source):
        ret = self.lock.acquire(source=source)  # will return false if lock is already held
        if ret:
            log.info(f"Global lock taken by {source}")
            self.lockTakenBy = source
        else:
            log.info(f"Failed to get global lock, it is currently held by {source}")
        return ret
        # need to release it later:
        # self.lock.release()

    def release_global_lock(self):
        self.lock.release()
        self.lockTakenBy = None
        log.info("Global lock released.")

    def tab_auto_import(self, widget, data=None):
        """opens the auto import tab"""
        new_aimp_thread = GuiAutoImport.GuiAutoImport(self.settings, self.config, self.sql, self)
        self.threads.append(new_aimp_thread)
        self.add_and_display_tab(new_aimp_thread, "HUD")
        if options.autoimport:
            new_aimp_thread.startClicked(new_aimp_thread.startButton, "autostart")
            options.autoimport = False

    def tab_bulk_import(self, widget, data=None):
        """opens a tab for bulk importing"""
        new_import_thread = GuiBulkImport.GuiBulkImport(self.settings, self.config, self.sql, self)
        self.threads.append(new_import_thread)
        self.add_and_display_tab(new_import_thread, "Bulk Import")

    def tab_tourney_player_stats(self, widget, data=None):
        new_ps_thread = GuiTourneyPlayerStats.GuiTourneyPlayerStats(self.config, self.db, self.sql, self)
        self.threads.append(new_ps_thread)
        self.add_and_display_tab(new_ps_thread, "Tourney Stats")

    def tab_main_help(self, widget, data=None):
        """Displays a tab with the main fpdb help screen"""
        mh_tab = QLabel(
            (
                """
                        Welcome to Fpdb!

                        This program is currently in an alpha-state, so our database format is still sometimes changed.
                        You should therefore always keep your hand history files so that you can re-import
                        after an update, if necessary.

                        all configuration now happens in HUD_config.xml.

                        This program is free/libre open source software licensed partially under the AGPL3,
                        and partially under GPL2 or later.
                        The Windows installer package includes code licensed under the MIT license.
                        You can find the full license texts in agpl-3.0.txt, gpl-2.0.txt, gpl-3.0.txt
                        and mit.txt in the fpdb installation directory."""
            )
        )
        self.add_and_display_tab(mh_tab, "Help")

    def get_theme_colors(self):
        """
        Returns a dictionary containing the theme colors used in the application.

        The dictionary contains the following keys:
        - "background": the name of the color used for the background.
        - "foreground": the name of the color used for the foreground.
        - "grid": the name of the color used for the grid.
        - "line_showdown": the name of the color used for the showdown line.
        - "line_nonshowdown": the name of the color used for the non-showdown line.
        - "line_ev": the name of the color used for the event line.
        - "line_hands": the name of the color used for the hands line.

        Returns:
            dict: A dictionary containing the theme colors.
        """
        return {
            "background": self.palette().color(QPalette.Window).name(),
            "foreground": self.palette().color(QPalette.WindowText).name(),
            "grid": "#444444",  # to customize
            "line_up": "g",
            "line_down": "r",
            "line_showdown": "b",
            "line_nonshowdown": "m",
            "line_ev": "orange",
            "line_hands": "c"
        }

    def tabTourneyGraphViewer(self, widget, data=None):
        """opens a graph viewer tab"""
        colors = self.get_theme_colors()
        new_gv_thread = GuiTourneyGraphViewer.GuiTourneyGraphViewer(self.sql, self.config, self, colors=colors)
        self.threads.append(new_gv_thread)
        self.add_and_display_tab(new_gv_thread, "Tourney Graphs")

    def validate_config(self):
        # check if sites in config file are in DB
        for site in self.config.supported_sites:  # get site names from config file
            try:
                self.config.get_site_id(site)  # and check against list from db
            except KeyError:
                log.warning(f"site {site} missing from db")
                dia = QMessageBox()
                dia.setIcon(QMessageBox.Warning)
                dia.setText("Unknown Site")
                dia.setStandardButtons(QMessageBox.Ok)
                dia.exec_()
                diastring = f"Warning: Unable to find site '{site}'"
                dia.format_secondary_text(diastring)
                dia.run()
                dia.destroy()

    def warning_box(self, string, diatitle="FPDB WARNING"):
        return QMessageBox(QMessageBox.Warning, diatitle, string).exec_()

    def close_tab(self, index):
        item = self.nb.widget(index)
        self.nb.removeTab(index)
        self.nb_tab_names.pop(index)

        try:
            self.threads.remove(item)
        except ValueError:
            pass

        item.deleteLater()

    def __init__(self):
        super().__init__()
        cards = os.path.join(Configuration.GRAPHICS_PATH, "tribal.jpg")
        if os.path.exists(cards):
            self.setWindowIcon(QIcon(cards))
        set_locale_translation()
        self.lock = interlocks.InterProcessLock(name="fpdb_global_lock")
        self.db = None
        self.status_bar = None
        self.threads = []
        self.closeq = queue.Queue(20)
        self.move(0, 0)
        self.setWindowTitle("Free Poker DB 3")
        sg = QApplication.primaryScreen().availableGeometry()
        self.resize(sg.width(), sg.height())

        # Create central widget and layout
        self.central_widget = QWidget(self)
        self.central_layout = QVBoxLayout(self.central_widget)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setSpacing(0)

        # Add menu bar to layout
        self.menu_bar = self.menuBar()
        self.central_layout.setMenuBar(self.menu_bar)

        self.nb = QTabWidget()
        self.nb.setTabsClosable(True)
        self.nb.tabCloseRequested.connect(self.close_tab)
        self.central_layout.addWidget(self.nb)
        self.setCentralWidget(self.central_widget)

        self.createMenuBar()

        self.pages = []
        self.nb_tab_names = []

        self.tab_main_help(None, None)

        self.showMaximized()

        self.load_profile(create_db=True)

        fileName = os.path.join(self.config.dir_log, "fpdb-errors.txt")
        log.info(f"Note: error output is being diverted to {self.config.dir_log}. Any major error will be reported there _only_.")
        errorFile = codecs.open(fileName, "w", "utf-8")
        sys.stderr = errorFile

        sys.stderr.write("fpdb starting ...")

if __name__ == "__main__":
    from qt_material import apply_stylesheet
    app = QApplication([])
    apply_stylesheet(app, theme="dark_purple.xml")
    me = fpdb()
    app.exec_()

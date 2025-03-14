from functools import partial

from PyQt5.QtCore import QDate, QDateTime
from PyQt5.QtWidgets import QCalendarWidget, QCheckBox, QDateEdit, QDialog, QGridLayout, QGroupBox, QLabel, QPushButton, QVBoxLayout, QWidget

START_DATE = QDate(2000, 1, 1)
END_DATE = QDate(2100, 1, 1)

class Filters(QWidget):
    def __init__(self, db, display={}):
        super().__init__(None)
        self.db = db
        self.sql = db.sql
        self.display = display
        self.start_date = QDateEdit(START_DATE)
        self.end_date = QDateEdit(END_DATE)
        self.tourney_buy_ins = {}
        self.stakes = {}

        self.setLayout(QVBoxLayout())
        self.setStyleSheet("QPushButton {padding-left:5;padding-right:5;padding-top:2;padding-bottom:2;}")
        self.make_filter()

    def make_filter(self):
        if self.display.get("TourneyBuyIn", False):
            self.layout().addWidget(self.create_tourney_buy_in_frame())

        if self.display.get("Stakes", False):
            self.layout().addWidget(self.create_stakes_frame())

        if self.display.get("Dates", False):
            self.layout().addWidget(self.create_date_frame())

        if self.display.get("Button", False):
            self.layout().addWidget(self.create_button())

    def create_tourney_buy_in_frame(self):
        tourney_buy_in_frame = QGroupBox("Buy-In:")
        self.fill_tourney_buy_in_frame(tourney_buy_in_frame)
        return tourney_buy_in_frame

    def create_date_frame(self):
        date_frame = QGroupBox("Date:")
        self.fill_date_frame(date_frame)
        return date_frame

    def create_button(self):
        button_frame = QWidget()
        button_layout = QVBoxLayout(button_frame)
        self.button = QPushButton("Unnamed")
        button_layout.addWidget(self.button)
        return button_frame

    def get_tourney_buy_ins(self):
        return [g for g in self.tourney_buy_ins if self.tourney_buy_ins[g].isChecked()]

    def get_stakes(self):
        return [g for g in self.stakes if self.stakes[g].isChecked()]

    def get_dates(self):
        offset = self.db.day_start * 3600
        t1 = self.start_date.date()
        t2 = self.end_date.date()
        adj_t1 = QDateTime(t1).addSecs(offset)
        adj_t2 = QDateTime(t2).addSecs(offset + 24 * 3600 - 1)
        return adj_t1.toString("yyyy/MM/dd HH:mm:ss"), adj_t2.toString("yyyy/MM/dd HH:mm:ss")

    def register_button_name(self, title):
        self.button.setText(title)

    def register_button_callback(self, callback):
        self.button.clicked.connect(callback)
        self.button.setEnabled(True)

    def fill_tourney_buy_in_frame(self, frame):
        vbox = QVBoxLayout()
        frame.setLayout(vbox)

        result = self.db.get_buy_ins()

        if len(result) >= 1:
            for buy_in, fee in result:
                display_text = f"{buy_in:.2f} + {fee:.2f}"
                value = f"{buy_in},{fee}"

                self.tourney_buy_ins[value] = QCheckBox(display_text)
                self.tourney_buy_ins[value].setChecked(True)
                vbox.addWidget(self.tourney_buy_ins[value])

    def fill_date_frame(self, frame):
        table = QGridLayout()
        frame.setLayout(table)

        lbl_start = QLabel(("From:"))
        btn_start = QPushButton("Cal")
        btn_start.clicked.connect(partial(self.calendar_dialog, self.start_date))
        clr_start = QPushButton("Reset")
        clr_start.clicked.connect(self.clear_start_date)

        lbl_end = QLabel(("To:"))
        btn_end = QPushButton("Cal")
        btn_end.clicked.connect(partial(self.calendar_dialog, self.end_date))
        clr_end = QPushButton("Reset")
        clr_end.clicked.connect(self.clear_end_date)

        table.addWidget(lbl_start, 0, 0)
        table.addWidget(btn_start, 0, 1)
        table.addWidget(self.start_date, 0, 2)
        table.addWidget(clr_start, 0, 3)

        table.addWidget(lbl_end, 1, 0)
        table.addWidget(btn_end, 1, 1)
        table.addWidget(self.end_date, 1, 2)
        table.addWidget(clr_end, 1, 3)

        table.setColumnStretch(0, 1)

    def calendar_dialog(self, date_edit):
        d = QDialog()
        d.setWindowTitle("Pick a date")

        vb = QVBoxLayout()
        d.setLayout(vb)
        cal = QCalendarWidget()
        vb.addWidget(cal)

        btn = QPushButton("Done")
        btn.clicked.connect(partial(self.get_date, d, cal, date_edit))
        vb.addWidget(btn)
        d.exec_()

    def clear_start_date(self):
        self.start_date.setDate(START_DATE)

    def clear_end_date(self):
        self.end_date.setDate(END_DATE)

    def get_date(self, dlg, calendar, date_edit):
        new_date = calendar.selectedDate()
        date_edit.setDate(new_date)

        if date_edit == self.start_date:
            end = self.end_date.date()

            if new_date > end:
                self.end_date.setDate(new_date)
        else:
            start = self.start_date.date()

            if new_date < start:
                self.start_date.setDate(new_date)

        dlg.accept()

    def create_stakes_frame(self):
        stakes_frame = QGroupBox("Stakes:")
        self.fill_stakes_frame(stakes_frame)
        return stakes_frame

    def fill_stakes_frame(self, frame):
        vbox = QVBoxLayout()
        frame.setLayout(vbox)

        result = self.db.get_stakes()

        if len(result) >= 1:
            for sb, bb in result:
                display_text = f"{sb:.2f}/{bb:.2f}"
                value = f"{sb},{bb}"

                self.stakes[value] = QCheckBox(display_text)
                self.stakes[value].setChecked(True)
                vbox.addWidget(self.stakes[value])

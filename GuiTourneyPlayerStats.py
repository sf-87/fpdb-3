import Filters

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QFrame, QScrollArea, QSplitter, QTableView, QVBoxLayout

class GuiTourneyPlayerStats(QSplitter):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.columns = [
            "Buy-In", "Fee", "Seats", "SnG", "KO", "Speed", "#", "ITM", "1st", "2nd",
            "3rd", "4th", "5th", "6th", "?", "Spent", "Won", "Net", "ROI", "\u20ac/Tour"
        ]
        self.filters = Filters.Filters(db, { "Dates": True, "Button": True })
        self.filters.register_button_name("Refresh Stats")
        self.filters.register_button_callback(self.generate_stats)
        self.view = QTableView()

        scroll = QScrollArea()
        scroll.setWidget(self.filters)
        stats_frame = QFrame()
        stats_box = QVBoxLayout()
        stats_frame.setLayout(stats_box)
        stats_splitter = QSplitter(Qt.Vertical)
        stats_splitter.addWidget(self.view)
        stats_box.addWidget(stats_splitter)

        self.addWidget(scroll)
        self.addWidget(stats_frame)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)

    def generate_stats(self):
        start_date, end_date = self.filters.get_dates()
        result = self.db.get_tourney_player_detailed_stats(start_date, end_date)

        model = QStandardItemModel(0, len(self.columns))
        model.setHorizontalHeaderLabels(self.columns)

        self.view.setModel(model)
        self.view.verticalHeader().hide()

        # Fullfill
        for row_data in result:
            tree_row = []

            for i in range(0, len(row_data)):
                item = QStandardItem(row_data[i])
                item.setEditable(False)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tree_row.append(item)

            model.appendRow(tree_row)

        self.view.resizeColumnsToContents()

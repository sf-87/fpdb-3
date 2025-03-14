from decimal import Decimal

import Filters

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QFrame, QLabel, QScrollArea, QSplitter, QTableView, QVBoxLayout, QWidget

RANKS = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10, "9": 9, "8": 8, "7": 7, "6": 6, "5": 5, "4": 4, "3": 3, "2": 2}

class GuiCashPlayerStats(QSplitter):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.columns = ["Stakes", "#", "VPIP", "PFR", "PF3Bet", "PF4Bet", "Steal", "BBStol", "SBStol", "RTS", "Net"]
        self.hands_columns = ["Hand", "#", "VPIP", "PFR", "PF3Bet", "PF4Bet", "Steal", "BBStol", "SBStol", "RTS", "Net"]
        self.filters = Filters.Filters(db, { "Stakes": True, "Dates": True, "Button": True })
        self.filters.register_button_name("Refresh Stats")
        self.filters.register_button_callback(self.generate_stats)
        self.view = QTableView()
        self.hands_view = QTableView()
        self.stats_splitter = QSplitter(Qt.Vertical)

        scroll = QScrollArea()
        scroll.setWidget(self.filters)
        stats_frame = QFrame()
        stats_box = QVBoxLayout()
        stats_frame.setLayout(stats_box)
        self.stats_splitter.addWidget(self.view)
        hands_widget = QWidget()
        hands_box = QVBoxLayout()
        hands_box.setContentsMargins(0, 0, 0, 0)
        hands_widget.setLayout(hands_box)
        self.stats_splitter.addWidget(hands_widget)
        label = QLabel("Hand Breakdown for all levels listed above")
        label.setAlignment(Qt.AlignHCenter)
        hands_box.addWidget(label)
        hands_box.addWidget(self.hands_view)
        stats_box.addWidget(self.stats_splitter)

        self.addWidget(scroll)
        self.addWidget(stats_frame)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)

    def generate_stats(self):
        start_date, end_date = self.filters.get_dates()
        stakes = ' OR '.join(tuple(f"(gt.smallBlind = {Decimal(stakes.split(',')[0])} AND gt.BigBlind = {Decimal(stakes.split(',')[1])})" for stakes in self.filters.get_stakes()))
        result = self.db.get_cash_player_detailed_stats(start_date, end_date, stakes)
        hands_result = self.db.get_cash_hands_player_detailed_stats(start_date, end_date, stakes)

        model = QStandardItemModel(0, len(self.columns))
        model.setHorizontalHeaderLabels(self.columns)
        hands_model = QStandardItemModel(0, len(self.hands_columns))
        hands_model.setHorizontalHeaderLabels(self.hands_columns)
        hands_model.setSortRole(Qt.UserRole)

        self.view.setModel(model)
        self.view.verticalHeader().hide()
        self.hands_view.setModel(hands_model)
        self.hands_view.verticalHeader().hide()

        # Fullfill
        for row_data in result:
            tree_row = []

            for i in range(0, len(row_data)):
                item = QStandardItem(row_data[i])
                item.setEditable(False)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tree_row.append(item)

            model.appendRow(tree_row)

        for row_data in hands_result:
            tree_row = []

            for i in range(0, len(row_data)):
                item = QStandardItem(row_data[i])
                item.setData(float(row_data[i]) if i > 0 and row_data[i] is not None else 1000 * RANKS[row_data[i][0]] + 10 * RANKS[row_data[i][1]] + (1 if len(row_data[i]) == 3 and row_data[i][2] == "s" else 0) if i == 0 else -1, Qt.UserRole)
                item.setEditable(False)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                tree_row.append(item)

            hands_model.appendRow(tree_row)

        self.view.resizeColumnsToContents()
        self.hands_view.resizeColumnsToContents()
        self.hands_view.setSortingEnabled(True)

        top_height = self.view.rowHeight(0) * model.rowCount() + self.view.horizontalHeader().height() + 2
        self.stats_splitter.setSizes([top_height, self.stats_splitter.height() - top_height])
        self.stats_splitter.setStretchFactor(0, 0)
        self.stats_splitter.setStretchFactor(1, 1)

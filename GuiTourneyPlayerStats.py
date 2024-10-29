import Filters

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QFrame, QScrollArea, QSplitter, QTableView, QVBoxLayout

colalias, colheading, colformat = 0, 1, 2

class GuiTourneyPlayerStats(QSplitter):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.columns = [
            ["siteName", "Site", "%s"],
            ["category", "Cat.", "%s"],
            ["limitType", "Limit", "%s"],
            ["currency", "Curr.", "%s"],
            ["buyIn", "Buy-In", "%3.2f"],
            ["fee", "Fee", "%3.2f"],
            ["maxSeats", "Seats", "%s"],
            ["knockout", "KO", "%s"],
            ["reEntry", "ReEntry", "%s"],
            ["playerName", "Name", "%s"],
            ["tourneyCount", "#", "%1.0f"],
            ["itm", "ITM%", "%3.2f"],
            ["_1st", "1st", "%1.0f"],
            ["_2nd", "2nd", "%1.0f"],
            ["_3rd", "3rd", "%1.0f"],
            ["unknownRank", "Rank?", "%1.0f"],
            ["spent", "Spent", "%3.2f"],
            ["won", "Won", "%3.2f"],
            ["net", "Net", "%3.2f"],
            ["roi", "ROI%", "%3.2f"],
            ["profitPerTourney", "\u20ac/Tour", "%3.2f"],
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
        list_cols = []

        start_date, end_date = self.filters.get_dates()
        col_names, result = self.db.get_tourney_player_detailed_stats(start_date, end_date)

        model = QStandardItemModel(0, len(self.columns))

        self.view.setModel(model)
        self.view.verticalHeader().hide()

        # Create Header
        for column in self.columns:
            list_cols.append(column[colheading])

        model.setHorizontalHeaderLabels(list_cols)

        # Fullfill
        for row_data in result:
            tree_row = []

            for column in self.columns:
                if column[colalias] in col_names:
                    value = row_data[col_names.index(column[colalias])]
                else:
                    value = None

                if column[colalias] in ["knockout", "reEntry"]:
                    value = "Yes" if row_data[col_names.index(column[colalias])] == 1 else "No"

                item = QStandardItem("")

                if value is not None and value != -999:
                    item = QStandardItem(column[colformat] % value)

                item.setEditable(False)
                item.setTextAlignment(Qt.AlignRight)
                tree_row.append(item)

            model.appendRow(tree_row)

        self.view.resizeColumnsToContents()

from decimal import Decimal
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from mplfinance.original_flavor import candlestick_ochl
from numpy import append, cumsum, diff, nonzero

import Filters

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QFrame, QLabel, QScrollArea, QSplitter, QTableView, QVBoxLayout

matplotlib.use("qt5agg")

class GuiCashSessionViewer(QSplitter):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.columns = ["Session", "Hands", "Start", "End", "Open", "Close", "Low", "High", "Range", "Profit"]
        self.colors = {'background': '#31363b', 'foreground': '#ffffff', 'grid': '#444444', "line_up": "g", "line_down": "r"}
        self.fig = None
        self.canvas = None
        self.view = None
        self.filters = Filters.Filters(self.db, { "Stakes": True, "Dates": True, "Button": True })
        self.filters.register_button_name("Refresh")
        self.filters.register_button_callback(self.generate_graph)
        self.graph_box = QVBoxLayout()
        self.stats_box = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidget(self.filters)
        graph_frame = QFrame()
        graph_frame.setLayout(self.graph_box)
        graph_frame.setStyleSheet(f'background-color: {self.colors["background"]}')
        stats_frame = QFrame()
        stats_frame.setLayout(self.stats_box)
        label = QLabel("Session Breakdown")
        label.setAlignment(Qt.AlignHCenter)
        self.stats_box.addWidget(label)
        self.stats_splitter = QSplitter(Qt.Vertical)
        self.stats_splitter.addWidget(graph_frame)
        self.stats_splitter.addWidget(stats_frame)

        self.addWidget(scroll)
        self.addWidget(self.stats_splitter)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)

    def clear_graph_data(self):
        try:
            if self.canvas:
                self.graph_box.removeWidget(self.canvas)

            if self.view:
                self.stats_box.removeWidget(self.view)
                self.view.setParent(None)
        except (AttributeError, RuntimeError):
            pass

        if self.fig is not None:
            self.fig.clear()

        self.fig = Figure(figsize=(5.0, 4.0), dpi=100)
        self.fig.patch.set_facecolor(self.colors["background"])

        if self.canvas is not None:
            self.canvas.destroy()

        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)

        self.view = QTableView()

    def generate_graph(self):
        self.clear_graph_data()

        ax = self.fig.add_subplot(111)
        ax.set_xlabel("Sessions", color=self.colors["foreground"])
        ax.set_facecolor(self.colors["background"])
        ax.tick_params(axis="x", colors=self.colors["foreground"])
        ax.tick_params(axis="y", colors=self.colors["foreground"])
        ax.spines["left"].set_color(self.colors["foreground"])
        ax.spines["right"].set_color(self.colors["foreground"])
        ax.spines["top"].set_color(self.colors["foreground"])
        ax.spines["bottom"].set_color(self.colors["foreground"])
        ax.set_ylabel("\u20ac", color=self.colors["foreground"])
        ax.grid(color=self.colors["grid"], linestyle=":", linewidth=0.2)

        result, quotes = self.get_data()

        if len(quotes) == 1:
            ax.set_title("No Data for Player Found", color=self.colors["foreground"])
        else:
            ax.set_title("Session Results", color=self.colors["foreground"])
            candlestick_ochl(ax, quotes, width=0.50, colordown=self.colors["line_down"], colorup=self.colors["line_up"], alpha=1.00)
        
        self.graph_box.addWidget(self.canvas)
        self.canvas.draw()

        model = QStandardItemModel(0, len(self.columns))
        model.setHorizontalHeaderLabels(self.columns)

        self.view.setModel(model)
        self.view.verticalHeader().hide()
        self.stats_box.addWidget(self.view)

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

    def get_data(self):
        start_date, end_date = self.filters.get_dates()
        stakes = ' OR '.join(tuple(f"(gt.smallBlind = {Decimal(stakes.split(',')[0])} AND gt.BigBlind = {Decimal(stakes.split(',')[1])})" for stakes in self.filters.get_stakes()))
        hands = self.db.get_cash_player_sessions_stats(start_date, end_date, stakes)

        if not hands:
            return [], [[0, 0, 0, 0, 0]]

        hands.insert(0, (hands[0][0], hands[0][1], 0))

        dates = [x[0] for x in hands]
        times = [int(x[1]) for x in hands]
        profits = [Decimal(x[2]) for x in hands]

        threshold = 1800  # Min # of secs between consecutive hands before being considered a new session
        diffs = append(diff(times), threshold + 1)
        index = nonzero(diffs > threshold)
        first_idx = 1
        result = []
        quotes = [[0, 0, 0, 0, 0]]
        cum_sum = cumsum(profits)
        session_id = 1
        total_hands = 0
        global_open = None
        global_lower = 0
        global_higher = 0

        for i in range(len(index[0])):
            last_idx = index[0][i]
            session_hands = last_idx - first_idx + 1

            if session_hands > 0:
                start_time = dates[first_idx]
                end_time = dates[last_idx]
                won = sum(profits[first_idx:last_idx + 1])
                higher = max(cum_sum[first_idx:last_idx + 1])
                lower = min(cum_sum[first_idx:last_idx + 1])
                open = sum(profits[:first_idx])
                close = sum(profits[:last_idx + 1])
                total_hands += session_hands

                if global_lower > lower:
                    global_lower = lower

                if global_higher < higher:
                    global_higher = higher

                if global_open is None:
                    global_open = open
                    global_start_time = start_time

                result.append(
                    [
                        f"{session_id}",
                        f"{session_hands}",
                        start_time,
                        end_time,
                        f"{open:.2f}",
                        f"{close:.2f}",
                        f"{lower:.2f}",
                        f"{higher:.2f}",
                        f"{higher - lower:.2f}",
                        f"{won:.2f}"
                    ]
                )
                quotes.append([session_id, open, close, higher, lower])
                first_idx = last_idx + 1
                session_id = session_id + 1

        global_close = close
        global_end_time = end_time
        result.append([""] * 10)
        result.append(
            [
                "All",
                f"{total_hands}",
                global_start_time,
                global_end_time,
                f"{global_open:.2f}",
                f"{global_close:.2f}",
                f"{global_lower:.2f}",
                f"{global_higher:.2f}",
                f"{global_higher - global_lower:.2f}",
                f"{global_close - global_open:.2f}"
            ]
        )

        return result, quotes

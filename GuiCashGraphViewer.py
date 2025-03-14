from decimal import Decimal
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from numpy import cumsum

import Filters

from PyQt5.QtWidgets import QFrame, QScrollArea, QSplitter, QVBoxLayout

matplotlib.use("qt5agg")

class GuiCashGraphViewer(QSplitter):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.colors = {'background': '#31363b', 'foreground': '#ffffff', 'grid': '#444444'}
        self.fig = None
        self.canvas = None
        self.filters = Filters.Filters(self.db, { "Stakes": True, "Dates": True, "Button": True })
        self.filters.register_button_name("Refresh Graph")
        self.filters.register_button_callback(self.generate_graph)
        self.graph_box = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidget(self.filters)
        graph_frame = QFrame()
        graph_frame.setLayout(self.graph_box)
        graph_frame.setStyleSheet(f'background-color: {self.colors["background"]}')

        self.addWidget(scroll)
        self.addWidget(graph_frame)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)

    def clear_graph_data(self):
        try:
            if self.canvas:
                self.graph_box.removeWidget(self.canvas)
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

    def generate_graph(self):
        self.clear_graph_data()

        ax = self.fig.add_subplot(111)
        ax.set_xlabel("Hands", color=self.colors["foreground"])
        ax.set_facecolor(self.colors["background"])
        ax.tick_params(axis="x", colors=self.colors["foreground"])
        ax.tick_params(axis="y", colors=self.colors["foreground"])
        ax.spines["left"].set_color(self.colors["foreground"])
        ax.spines["right"].set_color(self.colors["foreground"])
        ax.spines["top"].set_color(self.colors["foreground"])
        ax.spines["bottom"].set_color(self.colors["foreground"])
        ax.set_ylabel("\u20ac", color=self.colors["foreground"])
        ax.grid(color=self.colors["grid"], linestyle=":", linewidth=0.2)

        green = self.get_data()

        if len(green) == 1:
            ax.set_title("No Data for Player Found", color=self.colors["foreground"])
        else:
            ax.set_title("Cash Results", color=self.colors["foreground"])
            ax.plot(green, color="green", label=f"Hands: {len(green) - 1}\nProfit: \u20ac{green[-1]:.2f}")
            ax.legend(
                loc="upper left",
                fancybox=True,
                shadow=True,
                prop=FontProperties(size="smaller"),
                facecolor=self.colors["background"],
                labelcolor=self.colors["foreground"]
            )

        self.graph_box.addWidget(self.canvas)
        self.canvas.draw()

    def get_data(self):
        start_date, end_date = self.filters.get_dates()
        stakes = ' OR '.join(tuple(f"(gt.smallBlind = {Decimal(stakes.split(',')[0])} AND gt.BigBlind = {Decimal(stakes.split(',')[1])})" for stakes in self.filters.get_stakes()))
        winnings = self.db.get_cash_player_graph_stats(start_date, end_date, stakes)
        green = [Decimal(x[0]) for x in winnings]
        green.insert(0, Decimal(0))
        greenline = cumsum(green)

        return greenline

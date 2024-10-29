import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from numpy import cumsum

import Filters

from PyQt5.QtWidgets import QFrame, QScrollArea, QSplitter, QVBoxLayout

matplotlib.use("qt5agg")

class GuiTourneyGraphViewer(QSplitter):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.colors = {'background': '#31363b', 'foreground': '#ffffff', 'grid': '#444444'}
        self.fig = None
        self.canvas = None
        self.filters = Filters.Filters(self.db, { "TourneyBuyIn": True, "Dates": True, "Button": True })
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
        ax.set_xlabel("Tournaments", color=self.colors["foreground"])
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
            ax.set_title("Tournament Results", color=self.colors["foreground"])
            ax.plot(green, color="green", label=f"Tournaments: {len(green) - 1}\nProfit: \u20ac{green[-1]:.2f}")
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
        tourney_buy_ins = ' OR '.join(tuple(f"(tt.buyIn = {float(buy_in.split(',')[0])} AND tt.fee = {float(buy_in.split(',')[1])})" for buy_in in self.filters.get_tourney_buy_ins()))
        winnings = self.db.get_tourney_player_graph_stats(start_date, end_date, tourney_buy_ins)
        green = [float(x[0]) for x in winnings]
        green.insert(0, float(0))
        greenline = cumsum(green)

        return greenline

import contextlib
from functools import partial
import logging

import Stats

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("hud")

class SimpleHud(object):
    def __init__(self, hud, config):
        self.hud = hud
        self.config = config
        self.rows = self.hud.stat_set_parameters.rows
        self.cols = self.hud.stat_set_parameters.cols
        self.x_shift = self.hud.hud_params.hud_menu_x_shift
        self.y_shift = self.hud.hud_params.hud_menu_y_shift
        self.fg_color = self.hud.stat_set_parameters.fg_color
        self.bg_color = self.hud.stat_set_parameters.bg_color
        self.opacity = self.hud.stat_set_parameters.opacity
        self.font = QFont(self.hud.stat_set_parameters.font_family, self.hud.stat_set_parameters.font_size)
        self.style_sheet = f"QLabel{{font-family: {self.hud.stat_set_parameters.font_family};font-size: {self.hud.stat_set_parameters.font_size}pt;"
        self.table_menu = SimpleTableMenuLabel(self)
        self.positions = {}  # dict of window positions. normalised for favourite seat and offset
        self.displayed = False  # the seat windows are displayed
        self.stats = [[None] * self.cols for _ in range(self.rows)]

        for stat in self.hud.stat_set_parameters.stats:
            self.stats[self.hud.stat_set_parameters.stats[stat].row_col[0]][self.hud.stat_set_parameters.stats[stat].row_col[1]] = (
                self.hud.stat_set_parameters.stats[stat].stat_name
            )

    def move_windows(self):
        for i in list(range(1, self.hud.max_seats + 1)):
            self.m_windows[i].move(self.positions[i][0], self.positions[i][1])

    def save_layout(self):
        # Save new layout back to the aux element in the config file.
        new_locs = {self.adj[int(i)]: ((pos[0]), (pos[1])) for i, pos in list(self.positions.items())}
        self.config.save_layout_set(self.hud.max_seats, new_locs, self.hud.table.q_window.width(), self.hud.table.q_window.height())

    def create(self):
        self.adj = self.adj_seats()
        self.m_windows = {}  # windows to put the card/hud items in

        for i in list(range(1, self.hud.max_seats + 1)):
            x, y = self.hud.layout.location[self.adj[i]]
            self.m_windows[i] = SimpleStatWindow(self, i)
            self.positions[i] = self.create_scale_position(x, y)
            self.hud.layout.location[self.adj[i]] = self.positions[i]

            # Main action below - fill the created window with content
            self.m_windows[i].create_contents()

            self.m_windows[i].create()  # ensure there is a native window handle for topify
            self.hud.table.topify(self.m_windows[i])
            self.m_windows[i].show()

        self.table_menu.create()  # ensure there is a native window handle for topify
        self.hud.table.topify(self.table_menu)
        self.table_menu.show()

        self.hud.layout.height = self.hud.table.q_window.height()
        self.hud.layout.width = self.hud.table.q_window.width()

        self.update_gui()

    def create_scale_position(self, x, y):
        # For a given x/y, scale according to current height/width vs. reference height/width
        # This method is needed for create (because the table may not be the same size as the layout in config)
        # Any subsequent resizing of this table will be handled through hud_main
        x_scale = 1.0 * self.hud.table.q_window.width() / self.hud.layout.width
        y_scale = 1.0 * self.hud.table.q_window.height() / self.hud.layout.height
        return int(x * x_scale), int(y * y_scale)

    def update_gui(self):
        for i in list(self.m_windows.keys()):
            self.m_windows[i].update_contents(i)

            if self.hud.layout.height != self.hud.table.q_window.height() or self.hud.layout.width != self.hud.table.q_window.width():
                for i in list(range(1, self.hud.max_seats + 1)):
                    self.positions[i] = self.create_scale_position(self.hud.layout.location[self.adj[i]][0], self.hud.layout.location[self.adj[i]][1])
                    self.hud.layout.location[self.adj[i]] = self.positions[i]

                self.hud.layout.height = self.hud.table.q_window.height()
                self.hud.layout.width = self.hud.table.q_window.width()

        self.move_windows()

    def destroy(self):
        # Destroy all of the seat windows
        with contextlib.suppress(AttributeError):
            for i in list(self.m_windows.keys()):
                self.m_windows[i].destroy()
                del self.m_windows[i]

            self.table_menu.destroy()
            del self.table_menu

    def hide(self):
        # Hide the seat windows
        for w in list(self.m_windows.values()):
            if w is not None:
                w.hide()

        self.displayed = False

    def configure_event_cb(self, widget, i):
        # This method updates the current location for each statblock.
        # This method is needed to record moves for an individual block.
        if i:
            self.positions[i] = (widget.pos().x(), widget.pos().y())  # write this back to our map
            self.hud.layout.location[self.adj[i]] = self.positions[i]  # update the hud-level dict, so other aux can be told

    def adj_seats(self):
        # Determine how to adjust seating arrangements
        adj = list(range(self.hud.max_seats + 1))  # default seat adjustments = no adjustment
        # Find the hero's actual seat
        actual_seat = None

        for key in self.hud.stat_dict:
            if self.hud.stat_dict[key]["screen_name"] == self.config.site.screen_name:
                for i in range(1, self.hud.max_seats + 1):
                    if self.hud.stat_dict[key]["seat"] == i:
                        actual_seat = i
                        break

        for i in range(self.hud.max_seats):
            j = actual_seat + i

            if j > self.hud.max_seats:
                j = j - self.hud.max_seats

            adj[j] = self.hud.fav_seat[self.hud.max_seats] + i

            if adj[j] > self.hud.max_seats:
                adj[j] = adj[j] - self.hud.max_seats

        return adj

    def get_id_from_seat(self, seat):
        # Determine player id from seat number, given stat_dict
        return next((id for id, dict in list(self.hud.stat_dict.items()) if seat == dict["seat"]), None)

class SimpleStatWindow(QWidget):
    # Simple window class for stat windows
    def __init__(self, aw, seat):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowDoesNotAcceptFocus)
        self.aw = aw
        self.seat = seat
        self.last_pos = None

        self.resize(10, 10)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.button_press_left(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.button_release_left()

    def mouseMoveEvent(self, event):
        if self.last_pos is not None:
            self.move(self.pos() + event.globalPos() - self.last_pos)
            self.last_pos = event.globalPos()

    def button_press_left(self, event):
        self.last_pos = event.globalPos()

    def button_release_left(self):
        self.last_pos = None
        self.aw.configure_event_cb(self, self.seat)

    def create_contents(self):
        self.stat_box = [[None] * self.aw.cols for _ in range(self.aw.rows)]

        grid = QGridLayout()
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(1)
        grid.setContentsMargins(2, 2, 2, 2)

        for r in range(self.aw.rows):
            for c in range(self.aw.cols):
                self.stat_box[r][c] = SimpleStat(
                    self.aw.style_sheet,
                    self.aw.font,
                    self.aw.hud.stat_set_parameters.stats[(r, c)]
                )
                grid.addWidget(self.stat_box[r][c].label, r, c)

        self.setLayout(grid)
        self.setStyleSheet(f"QWidget{{background:{self.aw.bg_color}; color:{self.aw.fg_color};}}")

    def update_contents(self, i):
        player_id = self.aw.get_id_from_seat(i)

        if player_id is None:
            # No player dealt in this seat for this hand, hide the display
            self.hide()
            return

        for r in range(self.aw.rows):
            for c in range(self.aw.cols):
                self.stat_box[r][c].update(player_id, self.aw.hud.stat_dict)

        # Player dealt-in, force display of stat block
        self.setWindowOpacity(float(self.aw.opacity))
        # Show item, just in case it was hidden by the user
        self.show()

class SimpleStat(object):
    # A simple class for displaying a single stat
    def __init__(self, style_sheet, font, stat):
        self.style_sheet = style_sheet
        self.stat_name = stat.stat_name
        self.label = QLabel("xxx")  # xxx is used as initial value because longer labels don't shrink
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)

        try:
            self.stat_lo_color = stat.stat_lo_color
            self.stat_lo_val = float(stat.stat_lo_val)
        except Exception:
            self.stat_lo_color = ""
            self.stat_lo_val = 0

        try:
            self.stat_hi_color = stat.stat_hi_color
            self.stat_hi_val = float(stat.stat_hi_val)
        except Exception:
            self.stat_hi_color = ""
            self.stat_hi_val = 0

    def update(self, player_id, stat_dict):
        stat = Stats.do_stat(stat_dict, player_id, self.stat_name)
        fg = None

        if not stat:  # stat did not create, so exit now
            return False

        if self.stat_lo_val != 0 and self.stat_hi_val != 0:
            try:
                if stat[0] != "NA":
                    value = float(stat[0])

                    if value < self.stat_lo_val:
                        fg = self.stat_lo_color
                    elif value > self.stat_hi_val:
                        fg = self.stat_hi_color
            except Exception as e:
                print(f"Error in color selection: {e}")

        self.set_color(fg)
        self.label.setText(stat[0])

        tip = f"{stat_dict[player_id]['screen_name']}\n{stat[3]}\n{stat[1]} {stat[2]}"
        self.label.setToolTip(tip)

    def set_color(self, fg=None):
        ss = self.style_sheet

        if fg:
            ss += f"color: {fg};"

        self.label.setStyleSheet(ss + "}")

class SimpleTableMenuLabel(QWidget):
    def __init__(self, aw):
        super().__init__(None, Qt.Tool | Qt.FramelessWindowHint)
        self.hud = aw.hud
        self.x_shift = aw.x_shift
        self.y_shift = aw.y_shift
        self.menu_label = aw.hud.hud_params.label
        self.menu_is_popped = False

        lab = QLabel(self.menu_label)
        lab.setStyleSheet(f"background: {aw.bg_color}; color: {aw.fg_color};")

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(lab)

        self.move(self.x_shift, self.y_shift)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.button_press_right()

    def button_press_right(self):
        # Handle button clicks in the FPDB main menu event box
        if not self.menu_is_popped:
            self.menu_is_popped = True
            menu = SimpleTableMenu(self)
            menu.create()  # ensure there is a native window handle for topify
            self.hud.table.topify(menu)
            menu.show()

class SimpleTableMenu(QWidget):
    def __init__(self, table_menu_label):
        super().__init__(None, Qt.Window | Qt.FramelessWindowHint)
        self.table_menu_label = table_menu_label
        self.setWindowTitle(table_menu_label.menu_label)
        self.move(table_menu_label.x_shift, table_menu_label.y_shift)

        grid = QGridLayout()
        vbox = QVBoxLayout()

        vbox.addWidget(self.build_button("Restart This HUD", "kill"))
        vbox.addWidget(self.build_button("Save HUD Layout", "save"))
        vbox.addWidget(self.build_button("Close", "close"))

        grid.addLayout(vbox, 0, 0)
        
        self.setLayout(grid)

    def callback(self, data):
        self.table_menu_label.menu_is_popped = False

        if data == "kill":
            self.table_menu_label.hud.parent.kill_hud(self.table_menu_label.hud.table_name)
        elif data == "save":
            self.table_menu_label.hud.save_layout()

        self.destroy()

    def build_button(self, name, data):
        button = QPushButton(name)
        button.clicked.connect(partial(self.callback, data))
        return button

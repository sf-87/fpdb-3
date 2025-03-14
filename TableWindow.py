import ctypes
from ctypes import wintypes
import logging
import re

from PyQt5.QtGui import QWindow

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("hud")

# Windows functions via ctypes
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindow = ctypes.windll.user32.IsWindow

# Class for temporarily storing securities
class WindowInfoTemp:
    def __init__(self):
        self.titles = {}

# Function for listing windows and retrieving titles
def win_enum_handler(hwnd, lParam):
    window_info = ctypes.cast(lParam, ctypes.py_object).value
    length = GetWindowTextLength(hwnd)

    if length > 0:
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)

        if "Tournament" in buff.value or "Hold'em" in buff.value:
            window_info.titles[hwnd] = buff.value

    return True

class TableWindow(object):
    def __init__(self, table_name, max_seats, tourney_no):
        self.table_name = table_name
        self.max_seats = max_seats
        self.table_no = re.split(" ", table_name)[3] if tourney_no is not None else None
        self.re_table_no = f"{tourney_no}\sTable\s(\d+)"
        self.hud = None  # fill in later
        self.q_window = None
        self.number = None

        self.find_table_parameters()

        if self.number is None:
            return None

        self.q_window = QWindow.fromWinId(self.number)

    def get_table_no(self):
        window_title = self.get_window_title()

        if window_title is None:
            return 0

        mo = re.search(self.re_table_no, window_title)

        if mo is not None:
            return mo.group(1)

        return 0

    def check_table(self):
        return IsWindow(self.number)

    def has_table_title_changed(self):
        result = self.get_table_no()

        if result != 0 and result != self.table_no:
            self.table_no = result
            return True

        return False

    def find_table_parameters(self):
        # Find a poker client window with the given table name
        window_info = WindowInfoTemp()

        try:
            log.debug("Before EnumWindows")
            EnumWindows(EnumWindowsProc(win_enum_handler), ctypes.py_object(window_info))
            log.debug(f"After EnumWindows found {len(window_info.titles)} windows")
        except Exception as e:
            log.error(f"Error during EnumWindows: {e}")

        for hwnd in window_info.titles:
            log.debug(f"hwnd {hwnd}")

            try:
                title = window_info.titles[hwnd]

                if re.search(self.table_name, title):
                    self.number = hwnd
                    self.title = title
                    log.debug(f"Found table in hwnd {self.number} title {self.title}")
                    break
            except Exception as e:
                log.error(f"Unexpected error for hwnd {hwnd}: {e}")

        if self.number is None:
            log.error(f"Window {self.table_name} not found.")

    def get_window_title(self):
        length = GetWindowTextLength(self.number)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(self.number, buff, length + 1)

        return buff.value

    def topify(self, widget):
        # Set the table's window as parent
        window_handle = widget.windowHandle()
        window_handle.setParent(self.q_window)

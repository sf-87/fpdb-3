import ctypes
from ctypes import wintypes
import logging
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWindow

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("hud")

# Definition of Windows API constants
SM_CXSIZEFRAME = 32
SM_CYCAPTION = 4

# Windows functions via ctypes
EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
GetWindowRect = ctypes.windll.user32.GetWindowRect
GetSystemMetrics = ctypes.windll.user32.GetSystemMetrics
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

        if "Tournament" in buff.value:
            window_info.titles[hwnd] = buff.value

    return True

class TableWindow(object):
    def __init__(self, table_name, max_seats, tourney_no):
        self.table_name = table_name
        self.max_seats = max_seats
        self.table_no = re.split(" ", table_name)[3]
        self.re_table_no = f"{tourney_no}\sTable\s(\d+)"
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        self.hud = None  # fill in later
        self.gdk_handle = None
        self.number = None

        self.find_table_parameters()

        if self.number is None:
            return None

        geo = self.get_geometry()

        if geo is None:
            return None

        self.width = geo["width"]
        self.height = geo["height"]
        self.x = geo["x"]
        self.y = geo["y"]

    def get_table_no(self):
        window_title = self.get_window_title()

        if window_title is None:
            return 0

        mo = re.search(self.re_table_no, window_title)

        if mo is not None:
            return mo.group(1)

        return 0

    ####################################################################
    #    check_table() is meant to be called by the hud periodically to
    #    determine if the client has been moved or resized. check_table()
    #    also checks and signals if the client has been closed.
    def check_table(self):
        return self.check_size() or self.check_loc()

    ####################################################################
    #    "check" methods. They use the corresponding get method, update the
    #    table object and return the name of the signal to be emitted or
    #    False if unchanged. These do not signal for destroyed
    #    clients to prevent a race condition.

    #    These might be called by a Window.timeout, so they must not
    #    return False, or the timeout will be cancelled.
    def check_size(self):
        new_geo = self.get_geometry()

        if new_geo is None:  # window destroyed
            return "client_destroyed"

        if self.width != new_geo["width"] or self.height != new_geo["height"]:  # window resized
            self.width = new_geo["width"]
            self.height = new_geo["height"]
            return "client_resized"

        return False  # no change

    def check_loc(self):
        new_geo = self.get_geometry()

        if new_geo is None:  # window destroyed
            return "client_destroyed"

        if self.x != new_geo["x"] or self.y != new_geo["y"]:  # window moved
            self.x = new_geo["x"]
            self.y = new_geo["y"]
            return "client_moved"

        return False  # no change

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

    def get_geometry(self):
        # Get the window geometry
        try:
            rect = ctypes.wintypes.RECT()

            if IsWindow(self.number):
                result = GetWindowRect(self.number, ctypes.byref(rect))

                if result != 0:
                    x, y = rect.left, rect.top
                    width = rect.right - rect.left
                    height = rect.bottom - rect.top
                    b_width = GetSystemMetrics(SM_CXSIZEFRAME)
                    tb_height = GetSystemMetrics(SM_CYCAPTION)

                    return {
                        "x": x + b_width,
                        "y": y + tb_height + b_width,
                        "height": height - 2 * b_width - tb_height,
                        "width": width - 2 * b_width
                    }
                else:
                    log.error(f"Failed to retrieve GetWindowRect for hwnd: {self.number}")
                    return None
            else:
                log.error(f"The window {self.number} is not valid.")
                return None
        except Exception as e:
            log.error(f"Error retrieving geometry: {e}")
            return None

    def get_window_title(self):
        length = GetWindowTextLength(self.number)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(self.number, buff, length + 1)

        return buff.value

    def topify(self, window):
        # Make the specified Qt window 'always on top' under Windows
        if self.gdk_handle is None:
            self.gdk_handle = QWindow.fromWinId(self.number)

        q_window = window.windowHandle()
        q_window.setTransientParent(self.gdk_handle)
        #q_window.setFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowDoesNotAcceptFocus | Qt.WindowStaysOnTopHint)

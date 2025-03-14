import codecs
import logging, logging.config
import os
import shutil
import sys
import traceback
import xml.dom.minidom

# Setup constants
# code is centralised here to ensure uniform handling of path names
# especially important when user directory includes non-ascii chars
#
# INSTALL_METHOD ("source" or "exe")
# FPDB_ROOT_PATH (path to the root fpdb installation dir root
# APPDATA_PATH (root path for appdata eg /~ or appdata)
# CONFIG_PATH (path to the directory holding config, logs, sqlite db)
# LOG_PATH (path to the directory holding logs)
# DB_PATH (path to the directory holding sqlite db)
# GRAPHICS_PATH (path to graphics assets (normally .gfx)

if hasattr(sys, "frozen"):
    INSTALL_METHOD = "exe"
else:
    INSTALL_METHOD = "source"

if INSTALL_METHOD == "exe":
    FPDB_ROOT_PATH = os.path.dirname(sys.executable)
    GRAPHICS_PATH = os.path.join(FPDB_ROOT_PATH, "_internal")
else:
    FPDB_ROOT_PATH = os.getcwd()
    GRAPHICS_PATH = FPDB_ROOT_PATH

APPDATA_PATH = os.getenv("APPDATA")
CONFIG_PATH = os.path.join(APPDATA_PATH, "fpdb")
LOG_PATH = os.path.join(CONFIG_PATH, "log")
DB_PATH = os.path.join(CONFIG_PATH, "database")

log = None

def set_log_file(file_name):
    check_dir(CONFIG_PATH)
    check_dir(LOG_PATH)
    check_dir(DB_PATH)

    conf_file = os.path.join(CONFIG_PATH, "logging.conf").replace("\\", "/")
    log_file = os.path.join(LOG_PATH, file_name).replace("\\", "/")

    try:
        print(f"Using logging configfile: {conf_file}")
        logging.config.fileConfig(conf_file, {"logFile": log_file})
    except Exception as e:
        sys.stderr.write(f"Could not setup log file {file_name}: {e}")

def check_dir(path):
    # Check if a dir exists, creates if not.
    if not os.path.exists(path):
        os.makedirs(path)

class Layout(object):
    def __init__(self, node):
        self.max = int(node.getAttribute("max"))
        self.width = int(node.getAttribute("width"))
        self.height = int(node.getAttribute("height"))
        self.location = [None for x in range(self.max + 1)]  # fill array with max seats+1 empty entries

        for location_node in node.getElementsByTagName("location"):
            hud_seat = int(location_node.getAttribute("seat"))
            self.location[hud_seat] = (
                int(location_node.getAttribute("x")),
                int(location_node.getAttribute("y"))
            )

class Site(object):
    def __init__(self, node):
        self.site_name = node.getAttribute("site_name")
        self.screen_name = node.getAttribute("screen_name")
        self.hh_path = node.getAttribute("hh_path")
        self.ts_path = node.getAttribute("ts_path")
        self.fav_seat = {}

        for fav_node in node.getElementsByTagName("fav"):
            max = int(fav_node.getAttribute("max"))
            fav = int(fav_node.getAttribute("fav_seat"))
            self.fav_seat[max] = fav

class Stat(object):
    def __init__(self, node):
        row_col = node.getAttribute("row_col")  # human string "(r,c)" values >0)
        self.row_col = tuple(int(s) - 1 for s in row_col[1:-1].split(","))  # tuple (r-1,c-1)
        self.stat_name = node.getAttribute("stat_name")
        self.stat_hi_color = node.getAttribute("stat_hi_color")
        self.stat_hi_val = node.getAttribute("stat_hi_val")
        self.stat_lo_color = node.getAttribute("stat_lo_color")
        self.stat_lo_val = node.getAttribute("stat_lo_val")

class StatSet(object):
    def __init__(self, node):
        self.rows = int(node.getAttribute("rows"))
        self.cols = int(node.getAttribute("cols"))
        self.bg_color = node.getAttribute("bg_color")
        self.fg_color = node.getAttribute("fg_color")
        self.font_family = node.getAttribute("font_family")
        self.font_size = int(node.getAttribute("font_size"))
        self.opacity = float(node.getAttribute("opacity"))
        self.stats = {}

        for stat_node in node.getElementsByTagName("stat"):
            stat = Stat(stat_node)
            self.stats[stat.row_col] = stat

class Import(object):
    def __init__(self, node):
        self.interval = int(node.getAttribute("interval"))
        self.session_timeout = int(node.getAttribute("session_timeout"))

class HudUI(object):
    def __init__(self, node):
        self.tour_agg_bb_mult = float(node.getAttribute("tour_aggregation_level_multiplier"))
        self.tour_seats_style = node.getAttribute("tour_seats_style")
        self.cash_agg_bb_mult = float(node.getAttribute("cash_aggregation_level_multiplier"))
        self.cash_seats_style = node.getAttribute("cash_seats_style")
        self.label = node.getAttribute("label")
        self.hud_menu_x_shift = int(node.getAttribute("hud_menu_x_shift"))
        self.hud_menu_y_shift = int(node.getAttribute("hud_menu_y_shift"))

class General(object):
    def __init__(self, node):
        self.day_start = int(node.getAttribute("day_start"))

class Config(object):
    def __init__(self):
        self.database = "fpdb.db3"
        self.db_path = os.path.join(DB_PATH, self.database)
        self.file_error = False
        self.general = None
        self.imp = None
        self.hud_ui = None
        self.site = None
        self.stat_set = None
        self.layouts = {}
        self.doc = None  # Root of XML tree
        self.file = os.path.join(CONFIG_PATH, "HUD_config.xml")

        log = logging.getLogger("config")

        log.info(f"Reading configuration file {self.file}")

        try:
            self.doc = xml.dom.minidom.parse(self.file)
        except (OSError, IOError, xml.parsers.expat.ExpatError) as e:
            log.error(f"Error while processing XML: {traceback.format_exc()} Exception: {e}")
            self.file_error = True
            return None

        for gen_node in self.doc.getElementsByTagName("general"):
            self.general = General(gen_node)

        for imp_node in self.doc.getElementsByTagName("import"):
            self.imp = Import(imp_node)

        for hui_node in self.doc.getElementsByTagName("hud_ui"):
            self.hud_ui = HudUI(hui_node)

        for site_node in self.doc.getElementsByTagName("site"):
            self.site = Site(site_node)

        for layout_node in self.doc.getElementsByTagName("layout"):
            layout = Layout(layout_node)
            self.layouts[layout.max] = layout

        for ss_node in self.doc.getElementsByTagName("stat_set"):
            self.stat_set = StatSet(ss_node)

    def get_layout_node(self, max):
        for layout_node in self.doc.getElementsByTagName("layout"):
            if layout_node.getAttribute("max") == str(max):
                return layout_node

    def get_location_node(self, layout_node, seat):
        for location_node in layout_node.getElementsByTagName("location"):
            if location_node.getAttribute("seat") == str(seat):
                return location_node

    def save(self):
        try:
            shutil.move(self.file, f"{self.file}.backup")
        except OSError as e:
            log.error(f"Failed to move file {self.file} to backup. Exception: {e}")

        with codecs.open(self.file, "w", "utf-8") as file_writer:
            file_writer.write(self.doc.toxml())
            file_writer.close()

    def save_layout_set(self, max, locations, width, height):
        layout_node = self.get_layout_node(max)
        layout_node.setAttribute("width", str(width))
        layout_node.setAttribute("height", str(height))

        for i in list(locations.keys()):
            location_node = self.get_location_node(layout_node, i)
            location_node.setAttribute("x", str(locations[i][0]))
            location_node.setAttribute("y", str(locations[i][1]))
            # Refresh the live instance of the layout set with the new locations.
            # This is needed because any future windows created after a save layout MUST pickup the new layout
            self.layouts[max].location[i] = (locations[i][0], locations[i][1])

        self.layouts[max].height = height
        self.layouts[max].width = width

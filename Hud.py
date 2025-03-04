import copy
import logging

import Aux_Hud

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("hud")

class Hud(object):
    def __init__(self, parent, table, table_name, max_seats, config, stat_dict, hud_params):
        self.parent = parent
        self.table = table
        self.table_name = table_name
        self.max_seats = max_seats
        self.config = config
        self.stat_dict = stat_dict
        self.hud_params = hud_params
        self.fav_seat = config.site.fav_seat
        self.stat_set_parameters = config.stat_set
        self.table_hud_label = None
        self.new_max_seats = None

        if self.max_seats not in config.layouts:
            log.error(f"No layout found for {self.max_seats}-max games.")
            return

        # deepcopy required here, because self.layout is used
        # to propagate block moves from hud
        # (needed because there is only 1 layout for all aux)
        #
        # If we didn't deepcopy, self.layout would be shared
        # amongst all open huds - this is fine until one of the
        # huds does a resize, and then we have a total mess to
        # understand how a single block move on a resized screen
        # should be propagated to other tables of different sizes
        self.layout = copy.deepcopy(config.layouts[self.max_seats])
        self.aux_window = Aux_Hud.SimpleHud(self, config)

    def kill(self):
        self.aux_window.destroy()
        self.aux_window = None

    def save_layout(self):
        # Save its layout back to the config object
        self.aux_window.save_layout()
        # Write the layouts back to the HUD_config
        self.config.save()

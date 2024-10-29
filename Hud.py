import copy
import logging

import Aux_Hud

# logging has been set up in fpdb.py or HUD_main.py, use their settings:
log = logging.getLogger("hud")

class Hud(object):
    def __init__(self, table, table_name, max_seats, config, stat_dict, hud_params):
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
        # to propagate block moves from hud to mucked display
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

    def resize_windows(self):
        # Resize self.layout object; this will then be picked-up
        # by all attached aux's when called by hud_main.idle_update

        x_scale = 1.0 * self.table.width / self.layout.width
        y_scale = 1.0 * self.table.height / self.layout.height

        for i in list(range(1, self.max_seats + 1)):
            if self.layout.location[i]:
                self.layout.location[i] = (
                    (int(self.layout.location[i][0] * x_scale)),
                    (int(self.layout.location[i][1] * y_scale)),
                )

        self.layout.width = self.table.width
        self.layout.height = self.table.height

    def save_layout(self):
        # Save its layout back to the config object
        self.aux_window.save_layout()
        # Write the layouts back to the HUD_config
        self.config.save()

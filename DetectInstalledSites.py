#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011 Gimick bbtgaf@googlemail.com
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# In the "official" distribution you can find the license in agpl-3.0.txt.

"""
Attempt to detect which poker sites are installed by the user, their
 heroname and the path to the HH files.

This is intended for new fpdb users to get them up and running quickly.

We assume that the majority of these users will install the poker client
into default locations so we will only check those places.

We just look for a hero HH folder, and don't really care if the
  application is installed

Situations not handled are:
    Multiple screennames using the computer
    TODO Unexpected dirs in HH dir (e.g. "archive" may become a heroname!)
    Non-standard installation locations
    TODO Mac installations

Typical Usage:
    See TestDetectInstalledSites.py

Todo:
    replace hardcoded site list with something more subtle

"""

import os
import sys

import Configuration

LOCAL_APPDATA = os.getenv('APPDATA')

class DetectInstalledSites(object):
    def __init__(self, sitename="All"):
        self.Config = Configuration.Config()
        #
        # objects returned
        #
        self.sitestatusdict = {}
        self.sitename = sitename
        self.heroname = ""
        self.hhpath = ""
        self.tspath = ""
        self.detected = ""
        #
        # since each site has to be hand-coded in this module, there
        # is little advantage in querying the sites table at the moment.
        # plus we can run from the command line as no dependencies
        #
        self.supportedSites = [ "PokerStars"]

        self.supportedPlatforms = ["Win7"]

        if sitename == "All":
            for siteiter in self.supportedSites:
                self.sitestatusdict[siteiter] = self.detect(siteiter)
        else:
            self.sitestatusdict[sitename] = self.detect(sitename)
            self.heroname = self.sitestatusdict[sitename]["heroname"]
            self.hhpath = self.sitestatusdict[sitename]["hhpath"]
            self.tspath = self.sitestatusdict[sitename]["tspath"]
            self.detected = self.sitestatusdict[sitename]["detected"]

        return

    def detect(self, siteToDetect):
        self.hhpathfound = ""
        self.tspathfound = ""
        self.herofound = ""

        if siteToDetect == "PokerStars":
            self.detectPokerStars()

        if self.hhpathfound and self.herofound:
            encoding = sys.getfilesystemencoding()
            if type(self.hhpathfound) is not str:
                self.hhpathfound = str(self.hhpathfound, encoding)
            if type(self.tspathfound) is not str:
                self.tspathfound = str(self.tspathfound, encoding)
            if type(self.herofound) is not str:
                self.herofound = str(self.herofound, encoding)
            return {
                "detected": True,
                "hhpath": self.hhpathfound,
                "heroname": self.herofound,
                "tspath": self.tspathfound,
            }
        else:
            return {"detected": False, "hhpath": "", "heroname": "", "tspath": ""}

    def detectPokerStars(self):

        hhp = os.path.expanduser(os.path.join(LOCAL_APPDATA, "PokerStars", "HandHistory"))
        tsp = os.path.expanduser(os.path.join(LOCAL_APPDATA, "PokerStars", "TournSummary"))

        if os.path.exists(hhp):
            self.hhpathfound = hhp
            if os.path.exists(tsp):
                self.tspathfound = tsp
        else:
            return

        try:
            self.herofound = os.listdir(self.hhpathfound)[0]
            self.hhpathfound = os.path.join(self.hhpathfound, self.herofound)
            if self.tspathfound:
                self.tspathfound = os.path.join(self.tspathfound, self.herofound)
        except:
            pass

        return
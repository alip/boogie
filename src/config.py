#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=4 ts=4 sts=4 et tw=80 :
#
# Copyright (c) 2008 Ali Polatel <alip@exherbo.org>
#
# This file is part of Boogie mpd client. Boogie is free software; you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License version 2, as published by the Free Software Foundation.
#
# Boogie is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA

"""Boogie configuration"""

import os
import ConfigParser

# borrowed from mercurial.util
# differences from SafeConfigParser:
# - case-sensitive keys
# - allows values that are not strings (this means that you may not
#   be able to save the configuration to a file)
class configParser(ConfigParser.SafeConfigParser):
    def optionxform(self, optionstr):
        return optionstr

    def set(self, section, option, value):
        return ConfigParser.ConfigParser.set(self, section, option, value)

    def _interpolate(self, section, option, rawval, vars):
        if not isinstance(rawval, str):
            return rawval
        return ConfigParser.SafeConfigParser._interpolate(self, section,
                                                          option, rawval, vars)

if "BOOGIE_CONFIG_DIR" in os.environ:
    config_dir = os.environ["BOOGIE_CONFIG_DIR"]
else:
    config_dir = os.path.expanduser("~/.boogie")

if not os.path.exists(config_dir):
    os.makedirs(config_dir)

config_data = configParser()
config_data.read(os.path.join(config_dir, "config"))

if "BOOGIE_TEMPLATE_DIR" in os.environ:
    template_dir = os.environ["BOOGIE_TEMPLATE_DIR"]
elif config_data.has_option("template", "directory"):
    template_dir = os.path.expanduser(config_data.get("template", "directory"))
else:
    template_dir = os.path.join(config_dir, "templates")

if not os.path.exists(template_dir):
    os.makedirs(template_dir)

if "BOOGIE_CONSOLE_DIR" in os.environ:
    console_dir = os.environ["BOOGIE_CONSOLE_DIR"]
elif config_data.has_option("console", "directory"):
    console_dir = os.path.expanduser(config_data.get("console", "directory"))
else:
    console_dir = os.path.join(config_dir, "console")

if not os.path.exists(console_dir):
    os.makedirs(console_dir)


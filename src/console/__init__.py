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

"""Interactive mpd console based on IPython."""

import os
import shutil

import boogie
from boogie.config import config_data, console_dir
from boogie.colour import bold, red
from boogie.i18n import _

from IPython import Release
from IPython.Shell import IPShellEmbed

def prop(func):
    return property(**func())

class config(object):
    """Object to allow configuration in console."""
    def __init__(self):
        """Initialize defaults."""
        if config_data.has_option("console", "ping"):
            self.__ping = config_data.getboolean("console", "ping")
        else:
            self.__ping = True

        if config_data.has_option("console", "ping_interval"):
            self.__ping_interval = config_data.getint("console", "ping_interval")
        else:
            self.__ping_interval = 50

        if config_data.has_option("console", "return"):
            self.__ret = config_data.getboolean("console", "return")
        else:
            self.__ret = False

    @prop
    def ping():
        doc = "If True boogie periodically ping the mpd server."
        def fget(self):
            return self.__ping
        def fset(self, value):
            self.__ping = bool(value)
        return locals()

    @prop
    def ping_interval():
        doc = "Ping interval in seconds."
        def fget(self):
            return self.__ping_interval
        def fset(self, value):
            self.__ping_interval = float(value)
        def fdel(self):
            print((self.__delmsg))
        return locals()

    @prop
    def ret():
        doc = "If True magic functions will return data structures returned by server."
        def fget(self):
            return self.__ret
        def fset(self, value):
            self.__ret = bool(value)
        def fdel(self):
            print((self.__delmsg))
        return locals()

def mpdshell(conn):
    cwd = os.getcwd()

    # Change dir so we can load the mpd profile and copy files
    profiledir = os.path.join(boogie.__path__[0], "console")
    os.chdir(profiledir)

    if not os.path.exists(os.path.join(console_dir, "ipythonrc")):
        shutil.copy("ipythonrc", os.path.join(console_dir, "ipythonrc"))
    if not os.path.exists(os.path.join(console_dir, "ipy_user_conf.py")):
        shutil.copy("ipy_user_conf.py", os.path.join(console_dir,
            "ipy_user_conf.py"))

    args = "-profile mpd -ipythondir %s" % console_dir
    args = args.split()
    banner = _("mpd console") + ", boogie %s ipy %s" % (
            boogie.__version__, Release.version)
    exit_msg = _("leaving mpd console")

    namespace = { "_config_data": config_data, "_mpc":conn, "config":config() }
    ipshell = IPShellEmbed(args, banner=banner,
            exit_msg=_("leaving mpd console"), user_ns=namespace)
    os.chdir(cwd)
    ipshell()


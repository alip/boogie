#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=4 ts=4 sts=4 et tw=80 :
#
# Copyright (c) 2008 Ali Polatel <polatel@itu.edu.tr>
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

"""IPython command line completion for mpd console."""

import os

from IPython import ipapi
ip = ipapi.get()

def lsinfo(pathname):
    dname = os.path.dirname(pathname)
    if not dname:
        ip.ex("_ret = _mpc.mpc.lsinfo()")
    else:
        ip.ex("""
try:
    _ret = _mpc.mpc.lsinfo("%s")
except:
    _ret = []""" % dname)

    return ip.user_ns["_ret"]

def music_dir_completer(self, event):
    """Complete music directories."""
    if "_connected" not in ip.user_ns or not ip.user_ns["_connected"]:
        # Not connected
        return []

    flist = lsinfo(event.symbol)
    mylist = []
    for entry in flist:
        if "directory" in entry:
            mylist.append(entry["directory"] + os.path.sep)

    return mylist

def music_all_completer(self, event):
    """Complete music files and directories."""
    if "_connected" not in ip.user_ns or not ip.user_ns["_connected"]:
        # Not connected
        return []

    dirlist = lsinfo(event.symbol)
    mylist = []
    for entry in dirlist:
        if "directory" in entry:
            mylist.append(entry["directory"] + os.path.sep)
        elif "file" in entry:
            mylist.append(entry["file"])

    return mylist


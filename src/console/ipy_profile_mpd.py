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

"""Mpd profile for IPython"""

import os
import sys
import re

import boogie
from boogie.colour import bold, red, green
from boogie.config import config_data
from boogie.i18n import _
from boogie.mpdclient import mpd_command_dict

from IPython import ipapi, Release
ip = ipapi.get()

o = ip.options
o.automagic = 1
o.prompts_pad_left = 1
o.prompt_in1 = "mpd> "
o.prompt_in2 = "...  "
o.prompt_out = "out> "
o.nosep = 1

def exc_handler(cls, etype, value, tb):
    """Exception handler for mpd console."""
    print bold(red(_("error:"))) + " " +\
            bold(green(etype.__name__ + ":")) + " " + bold(str(value))
ip.set_custom_exc((Exception,), exc_handler)

def expose_magic(fn):
    global ip
    ip.expose_magic(fn.__name__, fn)

def make_mpd_magic(command_name):
    """Turn an mpd function into a magic function."""
    def magic_func(self, args=''):
        args = args.split()
        if (mpd_command_dict[command_name][0] is not None and
                len(args) not in mpd_command_dict[command_name][0]):
            raise TypeError, _("%s takes one of %r arguments (%d given)") % (
                    command_name, mpd_command_dict[command_name][0], len(args))

        # Convert them to correct type
        typ = mpd_command_dict[command_name][1]
        if typ is not None:
            index = 0
            while index < len(args):
                try:
                    args[index] = typ[index](args[index])
                except ValueError:
                    raise ValueError, _("%r is not %s") % (args[index], typ)
                index += 1

        if args:
            self.api.ex("_ret = getattr(_mpc, '%s')(*%r)" % (command_name, args))
        else:
            self.api.ex("_ret = getattr(_mpc, '%s')()" % command_name)

        if getattr(self.api.user_ns["config"], "ret"):
            return self.api.user_ns["_ret"]
    magic_func.__doc__ = mpd_command_dict[command_name][6]
    ip.expose_magic(command_name, magic_func)

    # Create aliases if there are any
    if config_data.has_section("alias"):
        for alias, command in config_data.items("alias"):
            if command_name == command:
                ip.expose_magic(alias, magic_func)

@expose_magic
def connect(self, args=''):
    """Connect to mpd server.
    usage: %connect [<string host>] [<int port>]"""
    if not args:
        host = port = None
    else:
        split_args = args.split()
        if len(split) != 2:
            raise TypeError, _("%s takes %d or %d arguments (%d given)" %\
                ("connect()", 0, 2, len(split_args)))
        else:
            host = split[0]
            port = int(split[1])

    self.api.ex("""
import time as _time
import thread as _thread
_disconnecting = False

_ret = _mpc.connect(%s, %s)
_connected = True
def _pinger():
    while not _disconnecting:
        if config.ping:
            _mpc.mpc.ping()
        _time.sleep(config.ping_interval)
_thread.start_new_thread(_pinger, ())""" % (host, port))
    return self.api.user_ns["_ret"]

@expose_magic
def disconnect(self, args=''):
    """Disconnect from mpd server."""
    if args:
        raise TypeError, _("%s takes exactly %d arguments (%d given)") %\
            ("disconnect()", 0, len(args.split()))

    self.api.ex("""
_disconnecting = True
_ret = _mpc.disconnect()
_connected = False""")
    if getattr(self.api.user_ns["config"], "ret"):
        return self.api.user_ns["_ret"]

# Create other commands
for command in mpd_command_dict:
    make_mpd_magic(command)


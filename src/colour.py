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

"""Colour support for boogie."""

import os
import re

bold      = lambda s : "\033[1m"  + s + "\033[0m"
underline = lambda s : "\033[4m"  + s + "\033[0m"
blink     = lambda s : "\033[5m"  + s + "\033[0m"
invert    = lambda s : "\033[7m"  + s + "\033[0m"
hide      = lambda s : "\033[8m"  + s + "\033[0m"
if "BOOGIE_NO_COLOUR" in os.environ or "BOOGIE_NO_COLOR" in os.environ:
    black = red = green = yellow = blue = magenta = cyan = white = lambda s: s
else:
    black     = lambda s : "\033[30m" + s + "\033[0m"
    red       = lambda s : "\033[31m" + s + "\033[0m"
    green     = lambda s : "\033[32m" + s + "\033[0m"
    yellow    = lambda s : "\033[33m" + s + "\033[0m"
    blue      = lambda s : "\033[34m" + s + "\033[0m"
    magenta   = lambda s : "\033[35m" + s + "\033[0m"
    cyan      = lambda s : "\033[36m" + s + "\033[0m"
    white     = lambda s : "\033[37m" + s + "\033[0m"

def colourify(string, colourfunc, **kwargs):
    """Colourify a keyworded string like:
    "Moving song with id %(id)s in playlist %(pl)s to position %(pos)s."
    where kwargs has the form:
    { "id" = "coloured_string",
      "pl" = "coloured_string",
      "pos"= "coloured_string",
    }
    colourfunc is used to colourify the other parts of the string."""

    # Form a regex string like "%\((id|pl|pos)\)s"
    regex = "%\(("
    keys = kwargs.keys()
    for key in keys:
        regex += key
        if keys.index(key) + 1 != len(keys):
            regex += "|"
    regex += ")\)s"

    splitted_string = re.split(regex, string)
    coloured_string = ""

    for element in splitted_string:
        if element in keys:
            coloured_string += kwargs[element]
        else:
            coloured_string += colourfunc(element)

    return coloured_string


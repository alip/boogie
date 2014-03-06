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

"""Common utilities for boogie."""

import os
import copy
import re

from boogie.i18n import _

SECSPERMIN = 60
SECSPERHOUR = 3600
SECSPERDAY = 86400

class TimeSpecError(Exception):
    pass

def asHuman(seconds, highest=3):
    """Convert seconds to human readable form.
    highest determines the highest time unit to return
    1 : minutes
    2 : hours
    3 : days
    """
    seconds = int(seconds)

    if highest > 3 or highest < 1:
        raise TypeError("highest must be a number between 1 and 3")

    if highest == 3:
        days = seconds / SECSPERDAY
        seconds %= SECSPERDAY
    if highest >= 2:
        hours = seconds / SECSPERHOUR
        seconds %= SECSPERHOUR
    if highest >= 1:
        minutes = seconds / SECSPERMIN
        seconds %= SECSPERMIN
    else:
        raise TypeError("highest must be a number between 1 and 3")

    if highest == 1:
        return "%02d:%02d" % (minutes, seconds)
    elif highest == 2:
        return "%d:%02d:%02d" % (hours, minutes, seconds)
    elif highest == 3:
        return str(days) + " " + _("days") + ", " + "%d:%02d:%02d" % (hours,
                                                            minutes, seconds)

def fillSpace(*args):
    """Given a list of strings,
    make all same length by placing spaces at the end.
    """

    args = list(args)
    unsorted_args = copy.copy(args)

    args.sort(key=len, reverse=True)
    length = len(args[0])

    for arg in args[1:]:
        filled_arg = arg + " " * (length - len(arg))
        unsorted_args[unsorted_args.index(arg)] = filled_arg

    return unsorted_args

def parseTimeSpec(timespec, elapsedtime, totaltime):
    """Parse a timespec in format [+-][HH:MM:SS]|<0-100>%
    Returns seconds which can be passed to seek() and seekid().
    Raises TimeSpecError if the format isn't valid."""

    # Check if it's a relative seek
    relative = 0
    if timespec.startswith("+"):   relative = 1
    elif timespec.startswith("-"): relative = -1

    # Check if seeking by percent
    if timespec.endswith("%"):
        perc = float(timespec[:-1])
        if (not relative and (perc < 0 or perc > 100)) or (relative and perc > 100):
            raise TimeSpecError(_("'%s' is not a number between 0 and 100")
                                % timespec[-1] )

        seekchange = perc * totaltime / 100 + 0.5

    else: # Seeking by absolute time
        if ":" in timespec:
            timespec_split = timespec.split(":")
            if len(timespec_split) == 3:
                hours, minutes, seconds = timespec_split

                # Hours exist, check if minutes is more than two digits
                if len(minutes) > 2:
                    raise TimeSpecError(_("'%s' is not two digits")
                                        % minutes)
                hours = int(hours)

            elif len(timespec_split) == 2:
                hours = 0
                minutes, seconds = timespec_split

                # Minutes exist, check if seconds is more than two digits
                if len(seconds) > 2:
                    raise TimeSpecError(_("'%s' is not two digits")
                                        % seconds)

                minutes = int(minutes)
                seconds = int(seconds)

            elif len(timespec_split) == 1:
                hours = minutes = 0
                seconds = timespec_split

            else:
                raise TimeSpecError(_("More than two colons in timespec"))

            # Make sure they're not above 60 if higher unit exists.
            if minutes != 0 and seconds > 60:
                raise TimeSpecError(_("%d is greater than 60") % seconds)
            elif hours != 0 and minutes > 60:
                raise TimeSpecError(_("%d is greater than 60") % minutes)

            totalseconds = ( hours * 3600 ) + ( minutes * 60 ) + seconds

        else: # Absolute seek in seconds
            totalseconds = float(timespec)

            if not relative and totalseconds < 0:
                raise TimeSpecError(_("'%s' is not a positive number")
                                    % timespec)

        seekchange = totalseconds

    if relative == 1:
        seekto = elapsedtime + seekchange
    elif relative == -1:
        seekto = elapsedtime + seekchange
    else:
        seekto = seekchange

    if seekto > totaltime:
        raise TimeSpecError(_("Seek amount would seek past the end of the song"))

    return int(seekto)

def parseTimeStatus(timespec):
    """Parse timespec in format elapsed:total and return seconds."""
    elapsed, total = timespec.split(":")

    return int(elapsed), int(total)


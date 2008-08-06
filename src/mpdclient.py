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

"""Handles MPD interaction."""

import os
import sys

import mpd

from boogie.config import config_data
from boogie.templates import printByName, printError
from boogie.util import parseTimeSpec, parseTimeStatus
from boogie.i18n import _

BOOLEAN_TRUE  = ("1", "on", "true", "yes")
BOOLEAN_FALSE = ("0", "off", "false", "no")

# MPD commands, format is:
# command_name :
#       ((number of args), type conversion, group, since, usage, explanation)
mpd_command_dict = {
        # Admin Commands
        "disableoutput":((1,), (lambda a: int(a)-1,) ,"admin", _("Admin Commands"),
            "0", _("<output #>"), _("Turn an output off")),
        "enableoutput":((1,), (lambda a: int(a)-1,), "admin", _("Admin Commands"), "0",
            _("<output #>"), _("Turn an output on")),
        "kill":((0,), None, "admin", _("Admin Commands"), "0", "",
            "Stop MPD from running, in a safe way"),
        "update":(None, None, "admin", _("Admin Commands"), "0", _("[<path>]"),
            _("Scan path for updates, path defaults to music_directory")),
        # Informational commands
        "status":((0,), None, "read", _("Informational Commands"), "0", "",
            _("Report the current status of mpd")),
        "stats":((0,), None, "read", _("Informational Commands"), "0", "",
            _("Display statistics")),
        "outputs":((0,), None, "read",  _("Informational Commands"), "0", "",
            _("Show information about all outputs")),
        "commands":((0,), None, "read", _("Informational Commands"), "0", "",
            _("Show which commands you have has access to")),
        "notcommands":((0,), None, "read", _("Informational Commands"), "0", "",
            _("Show which commands you don't have has access to")),
        "tagtypes":((0,), None, "read", _("Informational Commands"), "0", "",
            _("Get a list of available song metadata")),
        "urlhandlers":((0,), None, "read", _("Informational Commands"), "0", "",
            _("Get a list of available URL handlers")),
        # Database commands
        "find":((2,), None, "read", _("Database Commands"), "0", _("<type> <query>"),
            _("Find songs with a case sensitive, exact match to <query>")),
        "list":((1,3), None, "read", _("Database Commands"), "0",
            _("<type> [<type> <query>]"), _("Show all tags of <type>")),
        "listall":((0,1), None, "read", _("Database Commands"), "0", _("[<path>]"),
            _("Lists all directories and filenames in <path> recursively")),
        "listallinfo":((0,1), None, "read", _("Database Commands"), "0",
            _("[<path>]"),
            _("Lists all information about songs in <path> recursively")),
        "lsinfo":((0,1), None, "read", _("Database Commands"), "0",
            _("[<directory>]"),
            _("List contents of <directory>")),
        "lsplaylists":((0,1), None, "read", _("Database Commands"), "0",
            _("[<prefix>]"), _("List playlists")),
        "search":((2,), None, "read", _("Database Commands"), "0", _("<type> <query>"),
            _("Finds songs with a case insensitive match to <query>")),
        "count":((2,), None, "read", _("Database Commands"), "0", _("<type> <query>"),
            _("Retrieve the number of songs and their total playtime matching <query>")),
        # Playlist commands
        "add":(None, None, "add", _("Playlist Commands"), "0", _("<file>"),
            _("Add a song to the current playlist")),
        "addid":((1,2), (str, int), "add", _("Playlist Commands"), "0",
            _("<file> [<position>]"),
            _("Add a song to the current playlist at position <position>")),
        "clear":((0,), None, "control", _("Playlist Commands"), "0", "",
            _("Clear the current playlist")),
        "crop":((0,), None, "control", _("Playlist Commands"), "0", "",
            _("Remove all but the currently playing song")),
        "currentsong":((0,), None, "read", _("Playlist Commands"), "0", "",
            _("Display the metadata of the current song")),
        "delete":((1,), None, "control", _("Playlist Commands"),
            "0", _("<position>"), _("Delete a song from playlist")),
        "deleteid":((1,), (int,), "control", _("Playlist Commands"), "0",
            _("<songid #>"),
            _("Delete a song from playlist specifying its id")),
        "load":((1,), None, "add", _("Playlist Commands"), "0", _("<file>"),
            _("Load <file> as a playlist")),
        "rename":((2,), None, "control", _("Playlist Commands"), "0",
            _("<from> <to>"), _("Rename a playlist")),
        "move":((2,), (lambda a: int(a)-1, lambda a: int(a)-1), "control",
                _("Playlist Commands"), "0", _("<from> <to>"),
                _("Move song in playlist")),
        "moveid":((2,), (int, lambda a: int(a)-1), "control",
            _("Playlist Commands"), "0", _("<songid #> <to>"), _("Move song in playlist")),
        "playlist":((0,1), (lambda a: int(a)-1,), "control", _("Playlist Commands"), "0",
            _("[<position>]"), _("Display metadata for song in playlist")),
        "playlistid":((0,1), (int,), "read", _("Playlist Commands"), "0",
            _("[<songid #>]"), _("Display meteadata for song in playlist")),
        "plchanges":((1,), (int,), "read", _("Playlist Commands"), "0",
            _("<playlist_version>"),
            _("Displays changed songs currently in the playlist since <playlist_version>")),
        "plchangesposid":((1,), (int,), "read", _("Playlist Commands"), "0",
            _("<playlist_version>"),
            _("Displays changed songs currently in the playlist since <playlist_version>")),
        "rm":((1,), None, "control", _("Playlist Commands"), "0", _("<file>"),
            _("Remove playlist")),
        "save":((1,), None, "control", _("Playlist Commands"), "0", _("<file>"),
            _("Save a playlist as <file>")),
        "shuffle":((0,), None, "control", _("Playlist Commands"), "0", "",
            _("Shuffle the current playlist")),
        "swap":((2,), (lambda a: int(a)-1, lambda a: int(a)-1), "control",
            _("Playlist Commands"), "0", _("<position> <position>"),
            _("Swap positions of two songs in the playlist")),
        "swapid":((2,), (int, lambda a: int(a)-1), "control",
            _("Playlist Commands"), "0", _("<songid #> <songid #>"),
            _("Swap positions of two songs in the playlist")),
        "listplaylist":((1,), None, "read", _("Playlist Commands"), "0.13.0",
            _("<file>"), _("List files in playlist")),
        "listplaylistinfo":((1,), None, "read", _("Playlist Commands"), "0.12.0",
            _("<file>"), _("List songs in playlist")),
        "playlistadd":((2,), None, "control", _("Playlist Commands"), "0.13.0",
            _("<file> <song path>"), _("Add song to playlist")),
        "playlistclear":((1,), None, "control", _("Playlist Commands"), "0.13.0",
            _("<file>"), _("Clear playlist")),
        "playlistdelete":((2,), (str, int), "control", _("Playlist Commands"), "0.13.0",
            _("<file> <songid #>"), _("Delete song from playlist")),
        "playlistmove":((3,), (str, int, int), "control", _("Playlist Commands"), "0.13.0",
            _("<file> <songid #> <position>"),
            _("Move song to a position in playlist")),
        "playlistfind":((2,), None, "read", _("Playlist Commands"), "0.13.0",
            _("<type> <query>"),
            _("Search for songs in the current playlist with strict matching")),
        "playlistsearch":((2,), None, "read", _("Playlist Commands"), "0.13.0",
            _("<type> <query>"),
            _("Search case-insensitively with partial matches for songs in the current playlist")),
        # Playback commands
        "crossfade":((0,1), (int,), "control", _("Playback Commands"), "0",
            _("[<seconds>]"), _("Set and display crossfade settings")),
        "next":((0,), None, "control", _("Playback Commands"), "0", "",
            _("Play the next song in the current playlist")),
        "pause":((0,), None, "control", _("Playback Commands"), "0", "",
            _("Pauses the currently playing song")),
        "play":((0,1), (lambda a: int(a)-1,), "control", _("Playback Commands"), "0",
            _("[<position>]"),
            _("Start playing at <position> (default: 1)")),
        "playid":((0,1), (int,), "control", _("Playback Commands"), "0",
            _("[<songid #>]"),
            _("Start playing <songid #> (default: 1)")),
        "previous":((0,), None, "control", _("Playback Commands"), "0", "",
            _("Play the previous song in the current playlist")),
        "random":((0,1), None, "control", _("Playback Commands"), "0", "<on|off>",
            _("Toggle random mode, or specify state")),
        "repeat":((0,1), None, "control", _("Playback Commands"), "0", "<on|off>",
            _("Toggle repeat mode, or specify state")),
        "seek":((1,2), (str, lambda a: int(a)-1), "control", _("Playlist Commands"), "0",
            _("[+-][HH:MM:SS]|<0-100>% [<song #>]"),
            _("Seeks to the specified position in <song #>")),
        "seekid":((1,2), (str, int), "control", _("Playlist Commands"), "0",
            _("[+-][HH:MM:SS]|<0-100>% [<songid #>]"),
            _("Seeks to the specified position in <songid #>")),
        "stop":((0,), None, "control", _("Playlist Commands"), "0", "",
            _("Stop the currently playing playlists")),
        "toggle":((0,), None, "control", _("Playback Commands"), "0", "",
            _("Toggles Play/Pause, plays if stopped")),
        "volume":((0,1), None, "control", _("Playlist Commands"), "0",
            _("[+-]<num>"),
            _("Sets volume to <num> or adjusts by [+-]<num>")),
        # Misc
        "version":((0,), None, "", _("Miscellaneous Commands"), "0", "",
            _("Display version of MPD"))
}

class SmartMPDClient(mpd.MPDClient, object):
    """MPDClient extended to handle authentication."""

    @property
    def __super(self):
        return super(SmartMPDClient, self)

    def __init__(self):
        self.__super.__init__()
        self.mpd_notcommands = []

    def connect(self, host, port):
        self.__super.connect(host, port)
        # Get notcommands here to save bandwidth.
        self.mpd_notcommands = self.__super.__getattr__("notcommands")()

    def authenticate(self, funcname):
        """authenticate with the server if not allowed to execute funcname."""
        if funcname in self.mpd_notcommands:
            authfunc = self.__super.__getattr__("password")
            if config_data.has_option("mpd", "password"):
                authfunc(config_data.get("mpd", "password"))
            else:
                import getpass
                printByName("askpass", command=funcname)
                authfunc(getpass.getpass(_("Password: ")))
            self.mpd_notcommands = self.__super.__getattr__("notcommands")()

    def __getattr__(self, attr):
        if attr == "notcommands":
            return lambda *args: self.mpd_notcommands
        else:
            return self.__super.__getattr__(attr)

class Mpc(object):
    """Main class used by the command line client."""

    def __init__(self, conn=None, output=None, after_status=None):
        """Initialize class.
        conn is an mpd.MPDClient() instance, if None a new one will be created.
        if output is False, no output is printed (used by mpd console)
        if after_status is True, commands like clear, next, previous will call
        status() after execution to print status."""
        if conn:
            self.mpc = conn
        else:
            self.mpc = SmartMPDClient()

        if after_status is not None:
            self.after_status = after_status
        elif config_data.has_option("ui", "after_status"):
            self.after_status = config_data.getboolean("ui", "after_status")
        else:
            self.after_status = True

        if output is not None:
            self.output = output
        elif config_data.has_option("console", "output"):
            self.output = config_data.getboolean("console", "output")
        else:
            self.output = True

        # Commands with common argument & return values
        self._common_commands = {
                "commands" : "commands",
                "notcommands" : "notcommands",
                "outputs" : "outputs",
                "stats" : "stats",
                "tagtypes" : "tagtypes",
                "urlhandlers" : "urlhandlers",
                "list" : "results",
                "listall" : "results",
                "listallinfo" : "results",
                "listplaylist" : "results",
                "listplaylistinfo" : "results",
                "lsinfo" : "results",
                "currentsong" : "song",
                "plchangesposid" : "results",
                }
        # Commands that return none
        # Template is rendered before real function is called.
        self._none_commands = ["deleteid", "kill", "load", "rename", "move",
                "moveid", "rm", "save", "swap", "swapid", "playlistadd",
                "playlistclear", "playlistdelete", "playlistmove",]
        # Search commands
        self._search_commands = ["count", "find", "search", "playlistfind",
                "playlistsearch",]
        # Commands that print status after execution.
        self._status_commands = ["clear", "shuffle", "next", "previous",
                "stop",]
        # Commands that don't pass any arguments to the mpd function if their
        # argument is None and print status after execution.
        self._status_none_commands = {
                "play"  : "pos",
                "playid": "songid",
                }

    def __getattr__(self, attr):
        if attr in self._common_commands:
            def func(*args):
                self.mpc.authenticate(attr)
                if args:
                    ret = getattr(self.mpc, attr)(*args)
                else:
                    ret = getattr(self.mpc, attr)()
                kwargs = { self._common_commands[attr] : ret }
                if self.output:
                    printByName(attr, **kwargs)
                return ret
            return func
        elif attr in self._none_commands:
            def func(*args):
                if self.output:
                    printByName(attr, args=args)
                self.mpc.authenticate(attr)
                return getattr(self.mpc, attr)(*args)
            return func
        elif attr in self._search_commands:
            def func(qtype, query):
                self.mpc.authenticate(attr)
                ret = getattr(self.mpc, attr)(qtype, query)
                if self.output:
                    printByName(attr, qtype=qtype, query=query, results=ret)
                return ret
            return func
        elif attr in self._status_commands:
            def func(*args):
                if args:
                    if self.output:
                        printByName(attr, args=args)
                    self.mpc.authenticate(attr)
                    ret = getattr(self.mpc, attr)(*args)
                else:
                    if self.output:
                        printByName(attr)
                    self.mpc.authenticate(attr)
                    ret = getattr(self.mpc, attr)()

                if self.after_status:
                    self.status(after_command=True)

                return ret
            return func
        elif attr in self._status_none_commands:
            def func(arg=None):
                kwargs = { self._status_none_commands[attr] : arg }
                if self.output:
                    printByName(attr, **kwargs)
                self.mpc.authenticate(attr)
                if arg is None:
                    ret = getattr(self.mpc, attr)()
                else:
                    ret = getattr(self.mpc, attr)(arg)

                if self.after_status:
                    self.status(after_command=True)
                return ret
            return func
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                (self.__class__.__name__, attr))

    def connect(self, host=None, port=None):
        if host is not None:
            mpd_host = host
        elif "MPD_HOST" in os.environ:
            mpd_host = os.environ["MPD_HOST"]
        elif config_data.has_option("mpd", "host"):
            mpd_host = config_data.get("mpd", "host")
        else:
            mpd_host = "localhost"

        if port is not None:
            mpd_port = port
        elif "MPD_PORT" in os.environ:
            mpd_port = int(os.environ["MPD_PORT"])
        elif config_data.has_option("mpd", "port"):
            mpd_port = config_data.getint("mpd", "port")
        else:
            mpd_port = 6600

        self.mpc.connect(mpd_host, mpd_port)

    def disconnect(self):
        self.mpc.disconnect()

    # Commands that need special handling.
    def disableoutput(self, outputid):
        if self.output:
            printByName("disableoutput", outputid=outputid)
        self.mpc.authenticate("disableoutput")
        ret = self.mpc.disableoutput(outputid)

        if self.after_status:
            self.mpc.authenticate("outputs")
            self.outputs()
        return ret

    def enableoutput(self, outputid):
        if self.output:
            printByName("enableoutput", outputid=outputid)
        self.mpc.authenticate("enableoutput")
        ret = self.mpc.enableoutput(outputid)

        if self.after_status:
            self.outputs()
        return ret

    def update(self, *paths):
        self.mpc.authenticate("update")
        if not paths:
            ret = self.mpc.update()
        else:
            self.mpc.command_list_ok_begin()
            for path in paths:
                self.mpc.update(path)
            # When calling multiple update() commands only
            # one job id is returned.
            ret = self.mpc.command_list_end()[-1]

        if self.output:
            printByName("update", paths=list(paths), job=ret)
        return ret

    def playlistid(self, songid=None):
        self.mpc.authenticate("playlistid")
        if songid is None:
            ret = self.mpc.playlistid()
        else:
            ret = self.mpc.playlistid(songid)

        if self.output:
            currentsong = self.mpc.currentsong()
            printByName("playlistid", currentsong=currentsong, results=ret)

        return ret

    def playlist(self, song=None):
        self.mpc.authenticate("playlistinfo")
        if song is None:
            ret = self.mpc.playlistinfo()
        else:
            ret = self.mpc.playlistinfo(song)

        if self.output:
            currentsong = self.mpc.currentsong()
            printByName("playlist", currentsong=currentsong, results=ret)

        return ret

    def plchanges(self, version):
        self.mpc.authenticate("plchanges")
        ret = self.mpc.plchanges(version)

        if self.output:
            currentsong = self.mpc.currentsong()
            printByName("plchanges", currentsong=currentsong, results=ret)

        return ret

    def lsplaylists(self, prefix=None):
        self.mpc.authenticate("lsinfo")
        ret = self.mpc.lsinfo()
        playlists = []
        for value in ret:
            if "playlist" in value:
                if prefix is None or value["playlist"].startswith(prefix):
                    playlists.append(value)

        if self.output:
            printByName("lsplaylists", results=playlists)

        return playlists

    def status(self, after_command=False):
        self.mpc.authenticate("status")
        ret = self.mpc.status()

        if "songid" in ret:
            # We have a song playing/paused/stopped
            # Get information about it.
            song = self.mpc.playlistid(ret["songid"])
            if song:
                song = song[0]
            else:
                song = dict()
        else:
            song = dict()

        if self.output:
            printByName("status", status=ret, song=song)
        return ret

    def add(self, *paths):
        if not paths:
            paths = list(paths)
            # Read from standard input
            for line in sys.stdin.readlines():
                if line.endswith("\n"):
                    line = line[:-1]
                paths.append(line)

        if self.output:
            printByName("add", paths=paths)

        self.mpc.authenticate("add")
        self.mpc.command_list_ok_begin()
        for path in paths:
            self.mpc.add(path)
        return self.mpc.command_list_end()

    def addid(self, path, position=None):
        if self.output:
            printByName("addid_before", args=(path, position))

        self.mpc.authenticate("addid")
        if position is None:
            ret = self.mpc.addid(path)
        else:
            ret = self.mpc.addid(path, position)

        if self.output:
            printByName("addid_after", playlistid=ret)
        return ret

    def crop(self):
        self.mpc.authenticate("currentsong")
        self.mpc.command_list_ok_begin()
        self.mpc.currentsong()
        self.mpc.playlistinfo()
        currentsong, songlist = self.mpc.command_list_end()

        if self.output:
            printByName("crop", currentsong=currentsong)

        self.mpc.authenticate("deleteid")
        self.mpc.command_list_ok_begin()
        for song in songlist:
            if currentsong and currentsong["id"] == song["id"]:
                continue
            self.mpc.deleteid(song["id"])
        return self.mpc.command_list_end()

    def crossfade(self, seconds=None):
        if seconds is None:
            self.mpc.authenticate("status")
            current_fade = self.mpc.status()["xfade"]
            if self.output:
                printByName("crossfade", seconds=None, current=current_fade)
        else:
            if self.output:
                printByName("crossfade", seconds=seconds, current=None)
            self.mpc.authenticate("crossfade")
            ret = self.mpc.crossfade(seconds)

            if self.after_status:
                self.status()
            return ret

    def delete(self, position):
        """Delete song specified at position,
        Position can be a range like num-num
        If position is 0, remove the current playing song."""
        if "-" in position:
            split_position = position.split("-")
            if len(split_position) != 2:
                printError("delete_parse", position=position)
                return None
            elif not split_position[0]:
                # Negative number?
                try:
                    end = -1 * int(split_position[1])
                except ValueError:
                    printError("delete_parse", position=position)
                else:
                    printError("delete_negative", position=[end,])
                return None
            else:
                begin, end = split_position

            try:
                begin = int(begin) - 1
                end = int(end) - 1
            except ValueError:
                printError("delete_parse", position=position)
                return None

            if begin < 0 or end < 0:
                printError("delete_negative", position=[begin+1, end+1])
                return None

            if begin > end:
                begin, end = end, begin
            elif begin == end:
                end+=1

            printByName("delete", position=range(begin+1, end+1))

            self.mpc.authenticate("delete")
            self.mpc.command_list_ok_begin()
            diff = 0
            for pos in range(begin, end):
                self.mpc.delete(pos - diff)
                diff += 1
            return self.mpc.command_list_end()

        if position == "0":
            # Remove current song
            self.mpc.authenticate("currentsong")
            pos = int(self.mpc.currentsong()["pos"])
        else:
            try:
                pos = int(position) - 1
            except ValueError:
                printError("delete_parse", position=position)
                return None

        printByName("delete", position=[pos+1,])

        self.mpc.authenticate("delete")
        return self.mpc.delete(pos)

    def pause(self):
        if self.output:
            printByName("pause")

        self.mpc.authenticate("pause")
        ret = self.mpc.pause(1)

        if self.after_status:
            self.status(after_command=True)

        return ret

    def random(self, state=None):
        if state is None:
            # Toggle random mode
            self.mpc.authenticate("status")
            current_state = self.mpc.status()["random"]
            if current_state == "0":
                new_state = 1
            elif current_state == "1":
                new_state = 0
        elif state in BOOLEAN_TRUE:
            new_state = 0
        elif state in BOOLEAN_FALSE:
            new_state = 1
        else:
            printError("not_boolean", state=state,
                    boolean_true=BOOLEAN_TRUE, boolean_false=BOOLEAN_FALSE)
            return None

        if self.output:
            printByName("random", state=new_state)
        self.mpc.authenticate("random")
        ret = self.mpc.random(new_state)

        if self.after_status:
            self.status()
        return ret

    def repeat(self, state=None):
        if state is None:
            # Toggle random mode
            self.mpc.authenticate("status")
            current_state = self.mpc.status()["repeat"]
            if current_state == "0":
                new_state = 1
            elif current_state == "1":
                new_state = 0
        elif state in BOOLEAN_TRUE:
            new_state = 0
        elif state in BOOLEAN_FALSE:
            new_state = 1
        else:
            printError("not_boolean", state=state,
                    boolean_true=BOOLEAN_TRUE, boolean_false=BOOLEAN_FALSE)
            return None

        if self.output:
            printByName("repeat", state=new_state)
        self.mpc.authenticate("repeat")
        ret = self.mpc.repeat(new_state)

        if self.after_status:
            self.status()
        return ret

    def toggle(self):
        self.mpc.authenticate("status")
        state = self.mpc.status()["state"]

        printByName("toggle", state=state)
        if state == "play":
            self.mpc.authenticate("pause")
            ret = self.mpc.pause(1)
        elif state == "pause":
            self.mpc.authenticate("pause")
            ret = self.mpc.pause(0)
        else:
            self.mpc.authenticate("play")
            ret = self.mpc.play()

        if self.after_status:
            self.status(after_command=True)

        return ret

    def seek(self, timespec, position=None):
        self.mpc.authenticate("status")
        status = self.mpc.status()

        if position is None:
            # Default is current song
            position = int(status["song"])
            elapsedtime, totaltime = parseTimeStatus(status["time"])
        else:
            stats = self.mpc.playlistinfo(position)
            # Check if the position refers to the current song.
            if status["songid"] == stats[0]["id"]:
                elapsedtime, totaltime = parseTimeStatus(status["time"])
            else:
                elapsedtime = 0
                totaltime = int(stats[0]["time"])

        seekto = parseTimeSpec(timespec, elapsedtime, totaltime)

        if self.output:
            printByName("seek", position=position, seekto=seekto)
        self.mpc.authenticate("seek")
        ret = self.mpc.seek(position, seekto)
        if self.after_status:
            self.status(after_command=True)

        return ret

    def seekid(self, timespec, songid=None):
        self.mpc.authenticate("status")
        status = self.mpc.status()

        if songid is None:
            # Default is current song
            songid = int(status["songid"])
            elapsedtime, totaltime = parseTimeStatus(status["time"])
        else:
            # Check if the position refers to the current song.
            if songid == int(status["songid"]):
                elapsedtime, totaltime = parseTimeStatus(status["time"])
            else:
                stats = self.mpc.playlistid(songid)
                elapsedtime = 0
                totaltime = int(stats[0]["time"])

        seekto = parseTimeSpec(timespec, elapsedtime, totaltime)

        if self.output: printByName("seekid", songid=songid, seekto=seekto)
        self.mpc.authenticate("seekid")
        ret = self.mpc.seekid(songid, seekto)
        if self.after_status:
            self.status(after_command=True)

        return ret

    def setvol(self, volumespec):
        relative = 0
        if volumespec.startswith("+"): relative = 1
        elif volumespec.startswith("-"): relative = -1

        if relative:
            self.mpc.authenticate("status")
            status = self.mpc.status()

            volumechange = int(volumespec[1:])
            volume = int(status["volume"])
        else:
            volume = int(volumespec)
            if self.output:
                printByName("setvol", volume=volume)
            self.mpc.authenticate("setvol")
            ret = self.mpc.setvol(volume)

            if self.after_status:
                self.status(after_command=True)
            return ret

        if relative == 1:
            newvolume = volume + volumechange
        elif relative == -1:
            newvolume = volume - volumechange

        if self.output:
            printByName("setvol", volume=newvolume)
        self.mpc.authenticate("setvol")
        ret = self.mpc.setvol(newvolume)

        if self.after_status:
            self.status(after_command=True)
        return ret

    def volume(self, volumespec=None):
        if volumespec is None:
            self.mpc.authenticate("status")
            status = self.mpc.status()
            volume = status["volume"]
            if self.output:
                printByName("volume", volume=volume)
        else:
            self.setvol(volumespec)

    def version(self):
        if self.output:
            printByName("version", version=self.mpc.mpd_version)
        return self.mpc.mpd_version


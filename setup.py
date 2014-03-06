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

"""boogie setup
"""

from distutils.core import setup
import src as boogie

setup(name = boogie.__name__,
        version = boogie.__version__,
        license = boogie.__license__,
        description = "boogie mpd client",
        author = "Ali Polatel",
        author_email = "alip@exherbo.org",
        packages = ["boogie", "boogie.console", "boogie.templates"],
        scripts = [ "src/bin/boogie", ],
        package_dir = { "boogie" : "src" },
        package_data = { "boogie" : ["templates/*.txt",],
            "boogie.console" : ["ipythonrc",]},
        classifiers = [ "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Programming Language :: Python",
            "Topic :: Multimedia :: Sound/Audio",
            ],
        keywords = ["mpd", "mpc", "music console",],
        # python-mpd doesn't fit the name convention of distutils?!!
        # requires = ["ipython", "mako", "python-mpd" ],
        requires = ["ipython", "mako"],
    )


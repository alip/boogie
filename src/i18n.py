#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set sw=4 ts=4 sts=4 et tw=80 :
#
# Copyright (c) 2008 Ali Polatel <polatel@itu.edu.tr>
# depends on mercurial.i18n which is:
# Copyright (c) 2005, 2006 Matt Mackall <mpm@selenic.com>
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

"""Internationalization support for boogie"""

import gettext
t = gettext.translation("boogie", fallback=1)
gettext = t.gettext
_ = gettext


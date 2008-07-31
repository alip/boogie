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

import os
import sys

from mako.template import Template
from mako.lookup import TemplateLookup

from boogie.config import config_data, template_dir
from boogie.i18n import _

template_dirs = [template_dir]

cache_dir = os.path.join(template_dir, "cache")
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

template_dirs.append(__path__[0])

# Encoding
if config_data.has_option("template", "input_encoding"):
    input_encoding = config_data.get_option("template", "input encoding")
    input_encoding = input_encoding.lower()
else:
    input_encoding = "utf-8"

if config_data.has_option("template", "output_encoding"):
    output_encoding = config_data.get_option("template", "output_encoding")
    output_encoding = output_encoding.lower()
else:
    output_encoding = "utf-8"

if input_encoding == "utf-8":
    default_filters = ["decode.utf8"]
else:
    default_filters = ["unicode"]

if config_data.has_option("template", "encoding_errors"):
    encoding_errors = config_data.get_option("template", "encoding_errors")
else:
    encoding_errors = "replace"

template_lookup = TemplateLookup(directories=template_dirs,
        module_directory=cache_dir, default_filters=default_filters,
        input_encoding=input_encoding,
        output_encoding=output_encoding,
        encoding_errors=encoding_errors)

def renderByName(templatename, suffix=".txt", **kwargs):
    """Render a template using its name.
    If templatename doesn't add with suffix, add it.
    """
    if not templatename.endswith(suffix):
        templatename += suffix

    template = template_lookup.get_template(templatename)
    return template.render(_=_, **kwargs)

def printByName(templatename, **kwargs):
    """Render a template using its name and print."""
    sys.stdout.write(renderByName(templatename, **kwargs))

def printError(templatename, **kwargs):
    """Render a template usıng ıts name and prınt to stderr."""
    sys.stderr.write(renderByName(templatename, **kwargs))


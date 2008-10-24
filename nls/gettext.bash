#!/bin/bash
# vim: set sw=4 et sts=4 tw=80 :
# Copyright 2008 Ali Polatel <polatel@itu.edu.tr>
# Distributed under the terms of the GNU General Public License v2

# Generate boogie.pot file

gettext="$(type -P pygettext)"
if [[ -z "$gettext" ]]; then
    echo "pygettext not found in PATH" 1>&2
    exit 1
fi

if [[ ! -d ./src ]]; then
    echo "this script should be called from the parent project directory" 1>&2
    exit 1
fi

"${gettext}" -d boogie -p nls $(find src -name '*.py' -o -wholename '*templates/*.txt')


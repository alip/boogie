#!/bin/bash
# vim: set sw=4 et sts=4 tw=80 :
# Copyright 2008 Ali Polatel <alip@exherbo.org>
# Distributed under the terms of the GNU General Public License v2

MANPAGE_XSL="/etc/asciidoc/docbook-xsl/manpage.xsl"

asciidoc=$(type -P asciidoc 2>/dev/null)
if [[ -z "$asciidoc" ]]; then
    echo "asciidoc not in PATH" >&2
    exit 1
fi

xsltproc=$(type -P xsltproc 2>/dev/null)
if [[ -z "$xsltproc" ]]; then
    echo "xsltproc not in PATH" >&2
    exit 1
fi

if [[ ! -f "$MANPAGE_XSL" ]]; then
    echo "$MANPAGE_XSL doesn't exist" >&2
    exit 1
fi

$asciidoc -d manpage -b docbook boogie.1.txt
$xsltproc --nonet "$MANPAGE_XSL" boogie.1.xml
rm -f boogie.1.xml


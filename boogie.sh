#!/bin/sh

export PYTHONPATH="/home/alip/.local/lib/python3.3/site-packages:$PYTHONPATH"
export PATH="/home/alip/.local/bin:$PATH"
exec boogie "$@"

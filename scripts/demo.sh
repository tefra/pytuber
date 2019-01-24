#!/usr/bin/env bash

# DEMO_PROMPT="$ " ./demo.sh -w 1
. demo-magic.sh

clear

terminalizer record demo

p "# Hi, welcome to pytuber demo!"
p "# I already run pytuber setup for youtube and lastfm"
pe "pytuber --help"
pe "pytuber list"
pe "pytuber fetch youtube --all"
pe "pytuber list"
p "# We imported the playlist from youtube but still need to sync with last.fm"
pe "pytuber fetch lastfm --tracks"
pe "pytuber show 0d385e0"
pe "pytuber add lastfm user-playlist"
pe "pytuber fetch lastfm --tracks"
pe "pytuber fetch youtube --tracks"
pe "pytuber push youtube --all"
pe "pytuber fetch lastfm --tags"

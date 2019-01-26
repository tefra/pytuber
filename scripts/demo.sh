#!/usr/bin/env bash

# terminalizer record demo -c config.yml

. demo-magic.sh
echo -e "\e[35m# Hi, welcome to pytuber demo!"
pe "pytuber --help"
sleep 2
pe "clear"
pe "pytuber list"
pe "pytuber fetch youtube --playlists"
pe "pytuber list"
pe "pytuber show 0d385e0"
pe "clear"
pe "pytuber add lastfm country-playlist --country jp --limit 10 --title \"Japan Top10\""
pe "pytuber list"
pe "pytuber fetch youtube --tracks"
pe "pytuber push youtube --all"
echo -e "\e[35m# See help for more, bye bye :)"
sleep 2

# terminalizer render -o demo.gif demo

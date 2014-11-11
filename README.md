castaway
========

CastAway is a Google Chromecast framework with REST API written in python (and remuxing using ffmpeg)

USAGE

Add tracks to playlist

    find /Users/erik/Desktop -d 1 -name "*.mp4" -exec curl -X POST -d {} http://127.0.0.1:8000/playlist/add \;

# Command line Interface


    curl http://127.0.0.1:8000/streaminfo

    curl http://127.0.0.1:8000/playlist

    curl http://127.0.0.1:8000/{next,resume,pause,skip-to/#}

    curl http://127.0.0.1:8000/set/{volume/0.0-1.0,repeat/[01],mute/[01]}
  
# Getting started

  put ffmpeg in the same folder as castaway.py

    python castaway.py

    open -a 'Google Chrome' http://192.168.1.72:8000/ # must your computers IP, not 127.0.0.1

    find /Users/erik/Desktop -d 1 -name "*.mp4" -exec curl -X POST -d {} http://127.0.0.1:8000/playlist/add \;

    curl http://127.0.0.1:8000/{next,resume,pause,skip-to/#}

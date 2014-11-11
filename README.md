castaway
========

CastAway is a Google Chromecast framework with REST API written in python (and remuxing using ffmpeg)

### Install

castaway.py requires ffmpeg (http://ffmpeg.org/) in the $PATH or in same directory (in order to remux files to mkv, and convert the sound to aac), the flags to ffmpeg are not in away way optimized for you, but they worked for me.

### How to stream your first file

1. Start the castaway server
```
python castaway.py
```
2. Go to your LAN IP (eg. http://192.168.1.71:8000), 127.0.0.1 will NOT work.
```
    open -a 'Google Chrome' http://192.168.1.72:8000/
```
3. Add files to stream using castfile.sh
```
    sh castfile.sh Desktop/Video.mkv
```

### Command Line Interface

There are some commands, and possible more in the API but here are some...

    curl http://127.0.0.1:8000/streaminfo

    curl http://127.0.0.1:8000/playlist

    curl http://127.0.0.1:8000/{next,resume,pause,skip-to/#}

    curl http://127.0.0.1:8000/set/{volume/0.0-1.0,repeat/[01],mute/[01]}
  
    curl http://127.0.0.1:8000/{next,resume,pause,skip-to/#}

castaway
========

CastAway is a Google Chromecast framework with REST API written in python (and remuxing using ffmpeg)

### Install

castaway.py requires ffmpeg (http://ffmpeg.org/) in the $PATH or in same directory (in order to remux files to mkv, and convert the sound to aac), the flags to ffmpeg are not in away way optimized for you, but they worked for me.

### How to stream your first file

Start the castaway server.
```
python castaway.py
```
Go to your LAN IP (eg. http://192.168.1.71:8000/backend), 127.0.0.1 will NOT work. As of now, it should turn "limegreen" when ready :)
```
open -a 'Google Chrome' http://192.168.1.71:8000/backend
```
Add files to stream using castfile.sh to cast them directly.
```
sh castfile.sh Desktop/Video.mkv
```
Mobile "APP" is available at http://192.168.1.71:8000/

### REST API

It's fully controlled using REST, however, the code is the documentation.
```
curl -X POST -d "/Users/erik/Videos/video.mvk" http://127.0.0.1:8000/playlist
find ~/Desktop -d 1 -name "*.mp4" -exec curl -X POST -d {} http://127.0.0.1:8000/playlist \;
```

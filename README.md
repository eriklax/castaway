CastAway is a Google Chromecast streaming server (with a responsive playlist interface) with REST API written in Python (and remuxing using ffmpeg)

Requirements
------------
* Google Chrome
* Python 2.7 or later
* ffmpeg (http://ffmpeg.org/)

Installation
------------
castaway.py requires `ffmpeg` (http://ffmpeg.org/) in the `$PATH` or `$PWD` (in same directory) in order to remux files to mkv, and convert the sound to aac), the flags to `ffmpeg` are not in away way optimized for you, but they worked for me.

Install shell extensions in Mac OSX
-----------------------------------
In `Automator` create a new `Service`

1. Service receives selected `files ore folders` in `Finder`
2. Add a new `Run Shell Script` action, us Shell `/usr/bin/python`, Pass input `as arguments`.
3. Paste the content of `castfile.py` (not castaway.py)

In `Finder`s context menu a new service is now available, select a file and CastAway!

Running
-------

1. Run CastAway
   
   `python castaway.py`

2. Add files to playlist using REST by POST'ing them to /playlist
   
   `find ~/Movies -name "*.mp4" -exec curl -X POST -d {} http://127.0.0.1:8000/playlist \;`
   or run `sh castfile.sh ~/Movies/Video.mkv` to play a single file (step 2 and 3)

3. Make it begin playing on connect
   
   `curl http://127.0.0.1:8000/next`

4. Open Google Chrome and open http://127.0.0.1:8000/backend, enable casting (page should turn green) and minimize window
   
   `open -a 'Google Chrome' http://127.0.0.1:8000/backend`

5. Open http://127.0.0.1:8000/ (or LAN-IP) to control the playback using any browser/device
   
   `open -a 'Google Chrome' http://127.0.0.1:8000/`

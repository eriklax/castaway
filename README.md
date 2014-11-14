CastAway is a Google Chromecast streaming server (with a responsive playlist interface) with REST API written in Python (and remuxing using ffmpeg).

Requirements
------------
* Google Chrome with Chromecast extention
* Python 2.7 or later
* ffmpeg (http://ffmpeg.org/)

Installation
------------
castaway.py requires `ffmpeg` (http://ffmpeg.org/) in the `$PATH` or `$PWD` (in the same directory) in order to remux files to mkv, and convert the sound to aac), the flags to `ffmpeg` are not in away way optimized for you, but they worked for me.

Bonus: Install shell extension in OSX
-----------------------------------
In `Automator` create a new `Service`.

1. Service receives selected `files or folders` in `Finder`.
2. Add a new `Run Shell Script` action, us Shell `/usr/bin/python`, Pass input `as arguments`.
3. Paste the content below, but correct the path for your `castfile.py`.

```
#!/usr/bin/env python

execfile("/Users/erik/castaway/castfile.py")
```

In `Finder`s context menu a new service is now available, select a file or folder and CastAway!

Running
-------

1. Run the CastAway server.
   
   `python castaway.py`

2. Open Google Chrome and browse to http://127.0.0.1:8000/backend, enable casting (page should turn green, reload in wrost case) and minimize window.
   
   `open -a 'Google Chrome' http://127.0.0.1:8000/backend`

3. Run `python castfile.py /path/to/file/or/folder` to begin queuing files (or use shell extension mentioned above).

4. Open http://127.0.0.1:8000/ (or LAN-IP) to control the playback using any browser/device.
   
   `open -a 'Google Chrome' http://127.0.0.1:8000/`

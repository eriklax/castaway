#!/usr/bin/env python

import SimpleHTTPServer, SocketServer, socket
import urllib, subprocess, json, sys
import playlist

ffmpegBinary = False
castVolume = 1
castMute = False
castActionQueue = []

castingUUID = None
playList = playlist.Playlist()

class ChromeCast(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
		restURI = [x for x in self.path.split('/') if x]

		if restURI == ['playlist']:
			if self.client_address[0] != '127.0.0.1':
				self.send_response(403)
				self.end_headers()
				self.wfile.write('use 127.0.0.1 when adding files')
				return

			global playlist
			track = self.rfile.read(int(self.headers.getheader('content-length')))
			item = playList.insert(track)
			self.wfile.write(json.dumps({'uuid': item.uuid}))
			return

		if restURI[0:1] == ['streamuuid'] and len(restURI) == 2:
			global castingUUID
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			castingUUID = restURI[1]
			self.wfile.write(json.dumps({'uuid': castingUUID}))
			return
		return

    def do_GET(self):
		global castVolume, castMute
		global ffmpegBinary
		global castingUUID, playList
		restURI = [x for x in self.path.split('/') if x]

		# serve html pages
		if restURI == []:
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			self.copyfile(urllib.urlopen('mobile.html'), self.wfile)
			return

		if restURI == ['backend']:
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.end_headers()
			self.copyfile(urllib.urlopen('backend.html'), self.wfile)
			return

		# retrive playlist
		if restURI == ['playlist']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			l = dict()
			l['tracks'] = [{'name': p.name, 'uuid': p.uuid} for p in playList.items]
			l['repeat'] = playList.repeat
			l['shuffle'] = playList.shuffle
			self.wfile.write(json.dumps(l))
			return

		# skip-to a uuid
		if restURI[0:1] == ['skip-to'] and len(restURI) == 2:
			uuid = restURI[1]
			self.wfile.write(json.dumps({'uuid': uuid}))
			castActionQueue.append(json.dumps({'playback': 'load', 'uuid': uuid}))
			return

		# next respects repeat
		if restURI[0:1] == ['next']:
			try:
				uuid = playList.nexttrack(restURI[1] if len(restURI) > 1 else castingUUID).uuid
				self.send_response(200)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				self.wfile.write(json.dumps({'uuid': uuid}))
				castActionQueue.append(json.dumps({'playback': 'load', 'uuid': uuid}))
			except IndexError:
				self.send_response(404)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				self.wfile.write(json.dumps({'error': 'empty playlist'}))
			return

		# repeat current uuid on /next
		if restURI[0:2] == ['set', 'repeat']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			playList.repeat = restURI[2] == '1'
			self.wfile.write(json.dumps({'repeat': playList.repeat}))
			castActionQueue.append(json.dumps({'repeat': playList.repeat}))
			return

		# shuffle on /next
		if restURI[0:2] == ['set', 'shuffle']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			playList.shuffle = restURI[2] == '1'
			self.wfile.write(json.dumps({'shuffle': playList.shuffle}))
			castActionQueue.append(json.dumps({'shuffle': playList.shuffle}))
			return

		# volume control
		if restURI[0:2] == ['set', 'volume']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			castVolume = float(restURI[2])
			self.wfile.write(json.dumps({'volume': castVolume}))
			castActionQueue.append(json.dumps({'volume': castVolume}))
			return

		if restURI[0:2] == ['set', 'mute']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			castMute = restURI[2] == '1'
			self.wfile.write(json.dumps({'mute': castMute}))
			castActionQueue.append(json.dumps({'mute': castMute}))
			return

		# playback control
		if restURI == ['pause'] or restURI == ['resume']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps({'playback': restURI[0]}))
			castActionQueue.append(json.dumps({'playback': restURI[0]}))
			return

		# get current casting UUID
		if restURI == ['streamuuid']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps({'uuid': castingUUID}))
			return

		# get stream info like duration
		if restURI[0:1] == ['streaminfo'] and len(restURI) == 2:
			track = playList.gettrack(restURI[1])
			if not track:
				self.send_response(404)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				self.wfile.write(json.dumps({'error': 'uuid not in playlist'}))
				return

			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()

			ffmpeg = [
						ffmpegBinary,
						'-i', track.path
					]

			# more stream info
			p = subprocess.Popen(ffmpeg, shell=False, stdin=None, stderr=subprocess.PIPE, bufsize=0)
			l = [s for s in p.communicate()[1].split('\n') if 'Duration' in s]
			if len(l):
				l = [[x.strip().lower() for x in s.strip().split(':', 1)] for s in l[0].split(',')]
			l = dict(l)
			l['duration'] = sum([a * b for a, b in zip([3600, 60, 1], map(int, l['duration'].split('.')[0].split(':')))])
			l['name'] = track.name
			l['path'] = track.path
			l['uuid'] = track.uuid
			self.wfile.write(json.dumps(l))
			return

		# stream a uuid
		if restURI[0:1] == ['stream'] and len(restURI) == 2:
			track = playList.gettrack(restURI[1])
			if not track:
				self.send_response(404)
				self.send_header('Content-Type', 'application/json')
				self.end_headers()
				self.wfile.write(json.dumps({'error': 'uuid not in playlist'}))
				return

			self.send_response(200)
			self.send_header('Content-Type', 'video/x-matroska')
			self.end_headers()

			# add support for subtitles...
			ffmpeg = [
						ffmpegBinary,
						'-y',
						'-i', track.path,
						'-vcodec', 'copy',
						'-acodec', 'aac',
						'-strict', '-2',
						'-movflags', 'faststart',
						'-f', 'matroska',
						'-'
					]
			
			null = open('/dev/null', 'w')
			p = subprocess.Popen(ffmpeg, shell=False, stdin=None, stderr=null, stdout=subprocess.PIPE, bufsize=0)
			byte = p.stdout.read(1024 * 1024)
			while byte:
					try:
						self.wfile.write(byte)
						self.wfile.flush()
					except:
						return	
					byte = p.stdout.read(1024 * 1024)
			return

		# pop action from queue
		if restURI == ['streamqueue']:
			if len(castActionQueue) == 0:
				self.wfile.write(json.dumps({}))
			else:
				self.wfile.write(castActionQueue.pop(0))
			return
		return

class FastrebindServer(SocketServer.ThreadingTCPServer):
    def server_bind(self):
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(self.server_address)

p = subprocess.Popen(['which', 'ffmpeg', './ffmpeg'], stdout=subprocess.PIPE)
ffmpegBinary = p.communicate()[0].split('\n')[0]
if not ffmpegBinary:
	print 'missing ffmpeg, go get it! https://www.ffmpeg.org/download.html'
	sys.exit(1)

try:
	httpd = FastrebindServer(('0.0.0.0', 8000), ChromeCast)
	print 'Ready to CastAway!'
	httpd.serve_forever()
except KeyboardInterrupt:
	httpd.socket.close()

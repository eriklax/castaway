#!/usr/bin/env python

import SimpleHTTPServer, SocketServer, socket
import urllib, subprocess, json, os, sys

ffmpegBinary = False
castVolume = 1
castMute = False
castRepeat = False
castActionQueue = []

playListId = 0
playList = []

class ChromeCast(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
		if self.client_address[0] != '127.0.0.1':
			self.send_response(403)
			self.end_headers()
			self.wfile.write('use 127.0.0.1 when adding files')
			return

		global playList
		restURI = [x for x in self.path.split('/') if x]

		content = self.rfile.read(int(self.headers.getheader('content-length')))
		if restURI == ['playlist', 'add']:
			playList.append(content);
			self.wfile.write(json.dumps({'id': len(playList) - 1}))
			return

		return

    def do_GET(self):
		global castRepeat, castVolume, castMute
		global ffmpegBinary, playListId, playList
		restURI = [x for x in self.path.split('/') if x]

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

		if restURI == ['playlist']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps([os.path.basename(p) for p in playList]))
			return

		if restURI[0:2] == ['set', 'volume']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			castVolume = float(restURI[2])
			self.wfile.write(json.dumps({'status': 'ok'}))
			castActionQueue.append(json.dumps({'volume' : castVolume}))
			return

		if restURI[0:2] == ['set', 'mute']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			castMute = restURI[2] == '1'
			self.wfile.write(json.dumps({'status': 'ok'}))
			castActionQueue.append(json.dumps({'mute' : castMute}))
			return

		if restURI[0:2] == ['set', 'repeat']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			castRepeat = restURI[2] == '1'
			self.wfile.write(json.dumps({'status': 'ok'}))
			castActionQueue.append(json.dumps({'repeat' : castRepeat}))
			return

		if restURI == ['pause'] or restURI == ['resume'] or restURI == ['load']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			self.wfile.write(json.dumps({'status': 'ok'}))
			castActionQueue.append(json.dumps({'playback' : restURI[0]}))
			return

		# set track id
		if restURI[0:1] == ['skip-to']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			playListId = int(restURI[1:2][0])
			self.wfile.write(json.dumps({'status': 'ok'}))
			castActionQueue.append(json.dumps({'playback' : 'load'}))
			return

		# next respects repeat
		if restURI == ['next']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			if castRepeat == False:
				playListId = playListId + 1
			self.wfile.write(json.dumps({'status': 'ok'}))
			castActionQueue.append(json.dumps({'playback' : 'load'}))
			return

		# skip regardless of repeat
		if restURI == ['skip']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
			playListId = playListId + 1
			self.wfile.write(json.dumps({'status': 'ok'}))
			castActionQueue.append(json.dumps({'playback' : 'load'}))
			return

		if restURI == ['streaminfo']:
			self.send_response(200)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()

			if len(playList) == 0:
				self.wfile.write(json.dumps({}));
				return

			ffmpeg = [
						ffmpegBinary,
						'-i', playList[playListId % len(playList)]
					]

			# more stream info
			p = subprocess.Popen(ffmpeg, shell=False, stdin=None, stderr=subprocess.PIPE, bufsize=0)
			l = [s for s in p.communicate()[1].split('\n') if 'Duration' in s]
			if len(l):
				l = [[x.strip().lower() for x in s.strip().split(':', 1)] for s in l[0].split(',')]
			l = dict(l)
			l['duration'] = sum([a * b for a, b in zip([3600, 60, 1], map(int, l['duration'].split('.')[0].split(':')))])
			l['name'] = os.path.basename(playList[playListId % len(playList)])
			l['id'] = playListId % len(playList)
			self.wfile.write(json.dumps(l))
			return

		if restURI == ['stream']:
			if len(playList) == 0:
				self.send_response(404)
				self.end_headers()
				return

			self.send_response(200)
			self.send_header('Content-Type', 'video/x-matroska')
			self.end_headers()

			# add support for subtitles...
			ffmpeg = [
						ffmpegBinary,
						'-y',
						'-i', playList[playListId % len(playList)],
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
		if restURI == ['queue']:
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

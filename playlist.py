import os, uuid, random

class Item:
	uuid = None
	path = None
	name = None
	duration = None
	def __init__(self, path):
		self.uuid = str(uuid.uuid1())	
		self.path = path
		self.name = os.path.basename(path)

class Playlist:
	items = []
	shuffle = False
	repeat = False
	repeatall = False

	def insert(self, track):
		item = Item(track)
		self.items.append(item)	
		return item
	
	def gettrack(self, uuid):
		for item in self.items:
			if item.uuid == uuid:
				return item
		return None
	
	def nexttrack(self, uuid):
		if self.shuffle and not self.repeat:
			return random.choice(self.items)

		next = False
		for item in self.items:
			if not uuid or next:
				return item
			if item.uuid == uuid:
				if self.repeat:
					return item
				next = True
		if next and not self.repeatall:
			return None
		return self.items[0]

import thing
import settings

class Room:
	hasWalls = True
	contains = []
	
	north = False
	northeast = False
	east = False
	southeast = False
	south = False
	southwest = False
	west = False
	northwest = False
	
	def __init__(self, name, desc):
		self.name = name
		self.desc = desc
		self.contains = []
		
	def addThing(self, thing):
		self.contains.append(thing)
		
	def removeThing(self, thing):
		self.contains.remove(thing)
	
	def describe(self):
		game = __import__(settings.main_file)
		
		self.fulldesc = self.desc
		for thing in self.contains:
			self.fulldesc = self.fulldesc + " " + thing.desc
			# give player "knowledge" of a thing upon having it described
			if thing not in game.me.knows_about:
				game.me.knows_about.append(thing)
		print("") # line break before title
		print('\033[1m' + self.name + '\033[0m')
		print(self.fulldesc)
		print("")
	

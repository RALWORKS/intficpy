import thing

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
		self.fulldesc = self.desc
		for thing in self.contains:
			self.fulldesc = self.fulldesc + " " + thing.desc
		print("") # line break before title
		print('\033[1m' + self.name + '\033[0m')
		print(self.fulldesc)
		print("")
	

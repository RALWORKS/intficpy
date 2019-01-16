from . import thing

class Room:
	hasWalls = True
	contains = []
	sub_contains = []
	
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
		thing.location = self
		
	def removeThing(self, thing):
		self.contains.remove(thing)
		thing.location = False
	
	def describe(self, me, app):
		self.fulldesc = self.desc
		for thing in self.contains:
			self.fulldesc = self.fulldesc + " " + thing.desc
			# give player "knowledge" of a thing upon having it described
			if thing not in me.knows_about:
				me.knows_about.append(thing)
		#app.printToGUI("") # line break before title
		app.printToGUI(self.name, True)
		app.printToGUI(self.fulldesc)
	

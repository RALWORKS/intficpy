from . import thing
from . import verb
from . import room
##############################################################
# ROOM.PY - travel functions for IntFicPy
# Defines travel functions and the direction vocab dictionary
##############################################################

class TravelConnector:
	"""Base class for travel connectors
	Links two rooms together"""
	def __init__(self, room1, direction1, room2, direction2):
		self.pointA = room1
		self.pointB = room2
		r = [room1, room2]
		d = [direction1, direction2]
		interactables = []
		self.entranceA = thing.Thing("doorway")
		self.entranceB = thing.Thing("doorway")
		self.entranceA.invItem = False
		self.entranceB.invItem = False
		self.entranceA.connection = self
		self.entranceB.connection = self
		self.entranceA.direction = direction1
		self.entranceB.direction = direction2
		interactables.append(self.entranceA)
		interactables.append(self.entranceB)
		for x in range(0, 2):
			r[x].addThing(interactables[x])
			if d[x]=="n":
				r[x].north = self
				interactables[x].setAdjectives(["north"])
				interactables[x].describeThing("There is a doorway to the north. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the north doorway. ")
			elif d[x]=="s":
				r[x].south = self
				interactables[x].setAdjectives(["south"])
				interactables[x].describeThing("There is a doorway to the south. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the south doorway. ")
			elif d[x]=="e":
				r[x].east = self
				interactables[x].setAdjectives(["east"])
				interactables[x].describeThing("There is a doorway to the east. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the east doorway. ")
			elif d[x]=="w":
				r[x].west = self
				interactables[x].setAdjectives(["west"])
				interactables[x].describeThing("There is a doorway to the west. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the west door. ")
			elif d[x]=="ne":
				r[x].northeast = self
				interactables[x].setAdjectives(["northeast"])
				interactables[x].describeThing("There is a doorway to the northeast. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the northeast doorway. ")
			elif d[x]=="nw":
				r[x].northwest = self
				interactables[x].setAdjectives(["northwest"])
				interactables[x].describeThing("There is a doorway to the northwest. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the northwest doorway. ")
			elif d[x]=="se":
				r[x].southeast = self
				interactables[x].setAdjectives(["southeast"])
				interactables[x].describeThing("There is a doorway to the southeast. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the southeast doorway. ")
			elif d[x]=="sw":
				r[x].southwest = self
				interactables[x].setAdjectives(["southwest"])
				interactables[x].describeThing("There is a doorway to the southwest. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the southwest doorway. ")
			elif d[x]=="u":
				r[x].up = self
				interactables[x].setAdjectives(["up", "upward"])
				interactables[x].addSynonym("staircase")
				interactables[x].name = "staircase"
				interactables[x].removeSynonym("doorway")
				interactables[x].describeThing("There is a staircase leading up. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the staircase. ")
			elif d[x]=="d":
				r[x].down = self
				interactables[x].setAdjectives(["down", "downward"])
				interactables[x].addSynonym("staircase")
				interactables[x].name = "staircase"
				interactables[x].removeSynonym("doorway")
				interactables[x].describeThing("There is a staircase leading down. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the staircase. ")
			else:
				print("error: invalid direction input for TravelConnector: " + d[x])
	
	def travel(self, me, app):
		outer_loc = me.getOutermostLocation()
		if outer_loc == self.pointA:
			preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
			me.location = self.pointB
			me.location.addThing(me)
			app.printToGUI("You go through the doorway. ")
			me.location.describe(me, app)
		elif outer_loc == self.pointB:
			preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
			me.location = self.pointA
			me.location.addThing(me)
			app.printToGUI("You go through the doorway. ")
			me.location.describe(me, app)
		else:
			app.printToGUI("You cannot go that way. ")

class DoorConnector(TravelConnector):
	"""Base class for travel connectors
	Links two rooms together"""
	def __init__(self, room1, direction1, room2, direction2):
		self.pointA = room1
		self.pointB = room2
		r = [room1, room2]
		d = [direction1, direction2]
		interactables = []
		self.entranceA = thing.Door("door")
		self.entranceB = thing.Door("door")
		self.entranceA.twin = self.entranceB
		self.entranceB.twin = self.entranceA
		self.entranceA.connection = self
		self.entranceB.connection = self
		self.entranceA.direction = direction1
		self.entranceB.direction = direction2
		interactables.append(self.entranceA)
		interactables.append(self.entranceB)
		for x in range(0, 2):
			r[x].addThing(interactables[x])
			if d[x]=="n":
				r[x].north = self
				interactables[x].setAdjectives(["north"])
				interactables[x].describeThing("There is a door to the north. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the north door. ")
			elif d[x]=="s":
				r[x].south = self
				interactables[x].setAdjectives(["south"])
				interactables[x].describeThing("There is a door to the south. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the south door. ")
			elif d[x]=="e":
				r[x].east = self
				interactables[x].setAdjectives(["east"])
				interactables[x].describeThing("There is a door to the east. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the east door. ")
			elif d[x]=="w":
				r[x].west = self
				interactables[x].setAdjectives(["west"])
				interactables[x].describeThing("There is a door to the west. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the west door.  ")
			elif d[x]=="ne":
				r[x].northeast = self
				interactables[x].setAdjectives(["northeast"])
				interactables[x].describeThing("You notice nothing remarkable about the northeast door. ")
			elif d[x]=="nw":
				r[x].northwest = self
				interactables[x].setAdjectives(["northwest"])
				interactables[x].describeThing("There is a door to the northwest. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the northwest door. ")
			elif d[x]=="se":
				r[x].southeast = self
				interactables[x].setAdjectives(["southeast"])
				interactables[x].describeThing("There is a door to the southeast. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the southeast door. ")
			elif d[x]=="sw":
				r[x].southwest = self
				interactables[x].setAdjectives(["southwest"])
				interactables[x].describeThing("There is a door to the southwest. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the southwest door. ")
			else:
				print("error: invalid direction input for DoorConnector: " + d[x])
	
	def travel(self, me, app):
		from . import verb
		outer_loc = me.getOutermostLocation()
		preRemovePlayer(me, app)
		if outer_loc == self.pointA:
			if not self.entranceA.open:
				opened = verb.openVerb.verbFunc(me, app, self.entranceA)
				if not opened:
					return False
			#preRemovePlayer(me, app)
			if me.location:
				me.location.removeThing(me)
			me.location = self.pointB
			me.location.addThing(me)
			app.printToGUI("You go through " + self.entranceA.getArticle(True) + self.entranceA.verbose_name + ". ")
			me.location.describe(me, app)
		elif outer_loc == self.pointB:
			if not self.entranceB.open:
				opened = verb.openVerb.verbFunc(me, app, self.entranceB)
				if not opened:
					return False
			#preRemovePlayer(me, app)
			if me.location:
				me.location.removeThing(me)
			me.location = self.pointA
			me.location.addThing(me)
			app.printToGUI("You go through " + self.entranceB.getArticle(True) + self.entranceB.verbose_name + ". ")
			me.location.describe(me, app)
		else:
			app.printToGUI("You cannot go that way. ")

class LadderConnector(TravelConnector):
	"""Class for ladder travel connectors (up/down)
	Links two rooms together"""
	def __init__(self, room1, room2):
		self.pointA = room1
		self.pointB = room2
		r = [room1, room2]
		d = ["u", "d"]
		interactables = []
		self.entranceA = thing.AbstractClimbable("ladder")
		self.entranceB = thing.AbstractClimbable("ladder")
		self.entranceA.connection = self
		self.entranceB.connection = self
		self.entranceA.direction = "u"
		self.entranceB.direction = "d"
		interactables.append(self.entranceA)
		interactables.append(self.entranceB)
		for x in range(0, 2):
			r[x].addThing(interactables[x])
			if d[x]=="u":
				r[x].up = self
				interactables[x].setAdjectives(["up", "upward"])
				interactables[x].describeThing("There is a ladder leading up. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the ladder. ")
			elif d[x]=="d":
				r[x].down = self
				interactables[x].setAdjectives(["down", "downward"])
				interactables[x].describeThing("There is a ladder leading down. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the ladder. ")
			else:
				print("error: invalid direction input for LadderConnector: " + d[x])
	
	def travel(self, me, app):
		outer_loc = me.getOutermostLocation()
		if outer_loc == self.pointA:
			preRemovePlayer(me, app)
			if me.location:
				me.location.removeThing(me)
			me.location = self.pointB
			me.location.addThing(me)
			app.printToGUI("You climb the ladder. ")
			me.location.describe(me, app)
		elif outer_loc == self.pointB:
			preRemovePlayer(me, app)
			if me.location:
				me.location.removeThing(me)
			me.location = self.pointA
			me.location.addThing(me)
			app.printToGUI("You climb the ladder. ")
			me.location.describe(me, app)
		else:
			app.printToGUI("You cannot go that way. ")

class StaircaseConnector(TravelConnector):
	"""Class for staircase travel connectors (up/down)
	Links two rooms together"""
	def __init__(self, room1, room2):
		self.pointA = room1
		self.pointB = room2
		r = [room1, room2]
		d = ["u", "d"]
		interactables = []
		self.entranceA = thing.AbstractClimbable("staircase")
		self.entranceB = thing.AbstractClimbable("staircase")
		self.entranceA.addSynonym("stairway")
		self.entranceB.addSynonym("stairway")
		self.entranceA.addSynonym("stairs")
		self.entranceB.addSynonym("stairs")
		self.entranceA.addSynonym("stair")
		self.entranceB.addSynonym("stair")
		self.entranceA.connection = self
		self.entranceB.connection = self
		self.entranceA.direction = "u"
		self.entranceB.direction = "d"
		interactables.append(self.entranceA)
		interactables.append(self.entranceB)
		for x in range(0, 2):
			r[x].addThing(interactables[x])
			if d[x]=="u":
				r[x].up = self
				interactables[x].setAdjectives(["up", "upward"])
				interactables[x].describeThing("There is a staircase leading up. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the staircase ")
			elif d[x]=="d":
				r[x].down = self
				interactables[x].setAdjectives(["down", "downward"])
				interactables[x].describeThing("There is a staircase leading down. ")
				interactables[x].xdescribeThing("You notice nothing remarkable about the staircase. ")
			else:
				print("error: invalid direction input for StaircaseConnector: " + d[x])
	
	def travel(self, me, app):
		outer_loc = me.getOutermostLocation()
		if outer_loc == self.pointA:
			preRemovePlayer(me, app)
			if me.location:
				me.location.removeThing(me)
			me.location = self.pointB
			me.location.addThing(me)
			app.printToGUI("You climb the staircase. ")
			me.location.describe(me, app)
		elif outer_loc == self.pointB:
			preRemovePlayer(me, app)
			if me.location:
				me.location.removeThing(me)
			me.location = self.pointA
			me.location.addThing(me)
			app.printToGUI("You climb the staircase. ")
			me.location.describe(me, app)
		else:
			app.printToGUI("You cannot go that way. ")

# travel functions, called by getDirection in parser.py
def preRemovePlayer(me, app):
	"""Remove the Player from the current room
	Called by travel functions
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	x = me.location
	if isinstance(x, thing.Thing):
		x.removeThing(me)
		x.containsListUpdate()
		if isinstance(x, thing.Surface):
			app.printToGUI("You get off of " + x.getArticle(True) + x.verbose_name + ".")
		else:
			app.printToGUI("You get out of " + x.getArticle(True) + x.verbose_name + ".")
		x = x.location
		while not isinstance(x, room.Room):
			x.sub_contains[me.ix].remove(me)
			if x.sub_contains[me.ix]==[]:
				del x.sub_contains[me.ix]
			x = x.location
		
def travelN(me, app):
	"""Travel north
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.north:
		app.printToGUI("You cannot go north from here.")
	elif isinstance(loc.north, TravelConnector):
		loc.north.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.north
		me.location.addThing(me)
		app.printToGUI("You go north.")
		me.location.describe(me, app)

def travelNE(me, app):
	"""Travel northeast
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.northeast:
		app.printToGUI("You cannot go northeast from here.")
	elif isinstance(loc.northeast, TravelConnector):
		loc.northeast.travel(me, app)
	else:		
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.northeast
		me.location.addThing(me)
		app.printToGUI("You go northeast.")
		me.location.describe(me, app)

def travelE(me, app):
	"""Travel east
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.east:
		app.printToGUI("You cannot go east from here.")
	elif isinstance(loc.east, TravelConnector):
		loc.east.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.east
		me.location.addThing(me)
		app.printToGUI("You go east.")
		me.location.describe(me, app)

def travelSE(me, app):
	"""Travel southeast
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.southeast:
		app.printToGUI("You cannot go southeast from here.")
	elif isinstance(loc.southeast, TravelConnector):
		loc.southeast.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.southeast
		me.location.addThing(me)
		app.printToGUI("You go southeast.")
		me.location.describe(me, app)

def travelS(me, app):
	"""Travel south
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.south:
		app.printToGUI("You cannot go south from here.")
	elif isinstance(loc.south, TravelConnector):
		loc.south.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.south
		me.location.addThing(me)
		app.printToGUI("You go south.")
		me.location.describe(me, app)

def travelSW(me, app):
	"""Travel southwest
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.southwest:
		app.printToGUI("You cannot go southwest from here.")
	elif isinstance(loc.southwest, TravelConnector):
		loc.southwest.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.southwest
		me.location.addThing(me)
		app.printToGUI("You go southwest.")
		me.location.describe(me, app)

def travelW(me, app):
	"""Travel west
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.west:
		app.printToGUI("You cannot go west from here.")
	elif isinstance(loc.west, TravelConnector):
		loc.west.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.west
		me.location.addThing(me)
		app.printToGUI("You go west.")
		me.location.describe(me, app)

# travel northwest
def travelNW(me, app):
	"""Travel northwest
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.northwest:
		app.printToGUI("You cannot go northwest from here.")
	elif isinstance(loc.northwest, TravelConnector):
		loc.northwest.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.northwest
		me.location.addThing(me)
		app.printToGUI("You go northwest.")
		me.location.describe(me, app)

# travel up
def travelU(me, app):
	"""Travel upward
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.up:
		app.printToGUI("You cannot go up from here.")
	elif isinstance(loc.up, TravelConnector):
		loc.up.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.up
		me.location.addThing(me)
		app.printToGUI("You go up.")
		me.location.describe(me, app)

# travel down
def travelD(me, app):
	"""Travel downward
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.down:
		app.printToGUI("You cannot go down from here.")
	elif isinstance(loc.down, TravelConnector):
		loc.down.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.down
		me.location.addThing(me)
		app.printToGUI("You go down.")
		me.location.describe(me, app)

# go out
# synonym "exit" implemented as a verb
def travelOut(me, app):
	"""Travel out
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.exit:
		app.printToGUI("There is no obvious exit. ")
	elif isinstance(loc.exit, TravelConnector):
		loc.exit.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.exit
		me.location.addThing(me)
		app.printToGUI("You exit. ")
		me.location.describe(me, app)

# go in
# synonym "enter" implemented as a verb
def travelIn(me, app):
	"""Travel through entance
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.entrance:
		app.printToGUI("There is no obvious enrance. ")
	elif isinstance(loc.entrance, TravelConnector):
		loc.entrance.travel(me, app)
	else:
		preRemovePlayer(me, app)
		if me.location:
			me.location.removeThing(me)
		me.location = loc.entrance
		me.location.addThing(me)
		app.printToGUI("You enter. ")
		me.location.describe(me, app)

# maps user input to travel functions
directionDict = {"n": travelN, "north": travelN, "ne": travelNE, "northeast": travelNE, "e": travelE, "east": travelE, "se": travelSE, "southeast": travelSE, "s": travelS, "south": travelS, "sw": travelSW, "southwest": travelSW, "w": travelW, "west": travelW, "nw": travelNW, "northwest": travelNW, "up": travelU, "u": travelU, "down": travelD, "d": travelD, "in": travelIn, "out": travelOut}

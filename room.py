from . import thing
from . import serializer

##############################################################
# ROOM.PY - verbs for IntFicPy 
# Defines the Room class
##############################################################
# TODO: implement walls as interactable objects (north, south, east and west) and outdoor rooms (no walls)


# a dictionary of the indeces of all Room objects, mapped to their object
# populated at runtime
rooms = {}
# index is an integer appended to the string "room"- increases by 1 for each Room defined
# index of a room will always be the same provided the game file is written according to the rules
room_ix = 0

class Room:
	"""Room is the overarching class for all locations in an IntFicPy game """
	def __init__(self, name, desc):
		"""Initially set basic properties for the Room instance """
		# indexing for save
		global room_ix
		self.ix = "room" + str(room_ix)
		room_ix = room_ix + 1
		rooms[self.ix] = self
		# travel connections can be set to other Rooms after initialization
		self.north = None
		self.northeast = None
		self.east = None
		self.southeast = None
		self.south = None
		self.southwest = None
		self.west = None
		self.northwest = None
		# room properties
		self.name = name
		self.desc = desc
		self.hasWalls = True
		self.contains = []
		self.sub_contains = []
	
	def addThing(self, thing):
		"""Places a Thing in a Room
		Should generally be used by game creators instead of using room.contains.append() directly """
		self.contains.append(thing)
		thing.location = self
	
	def removeThing(self, thing):
		"""Removes a Thing from a Room
		Should generally be used by game creators instead of using room.contains.remove() directly """
		if thing in self.sub_contains:
			self.sub_contains.remove(thing)
		else:
			self.contains.remove(thing)
			thing.location = False
	
	def describe(self, me, app):
		"""Prints the Room title and description and lists items in the Room """
		self.fulldesc = self.desc
		for thing in self.contains:
			self.fulldesc = self.fulldesc + " " + thing.desc
			# give player "knowledge" of a thing upon having it described
			if thing not in me.knows_about:
				me.knows_about.append(thing)
		app.printToGUI(self.name, True)
		app.printToGUI(self.fulldesc)
	

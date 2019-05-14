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
		self.contains = {}
		self.sub_contains = {}
	
	def addThing(self, item):
		"""Places a Thing in a Room
		Should generally be used by game creators instead of using room.contains.append() directly """
		#self.contains.append(thing)
		if item.ix in self.contains:
			self.contains[item.ix].append(item)
		else:
			self.contains[item.ix] = [item]
		item.location = self
	
	def removeThing(self, item):
		"""Removes a Thing from a Room
		Should generally be used by game creators instead of using room.contains.remove() directly """
		if item.ix in self.sub_contains:
			self.sub_contains[item.ix].remove(item)
			if self.sub_contains[item.ix] == []:
				del self.sub_contains[item.ix]
		else:
			self.contains[item.ix].remove(item)
			if self.contains[item.ix] == []:
				del self.contains[item.ix]
			item.location = False
	
	def describe(self, me, app):
		"""Prints the Room title and description and lists items in the Room """
		self.fulldesc = self.desc
		for key, things in self.contains.items():
			if len(things) > 1:
				self.fulldesc = self.fulldesc + " There are " + str(len(things)) + " " + things[0].getPlural() + " here. "
			else:	
				self.fulldesc = self.fulldesc + " " + things[0].desc
			# give player "knowledge" of a thing upon having it described
			if key not in me.knows_about:
				me.knows_about.append(key)
		app.printToGUI(self.name, True)
		app.printToGUI(self.fulldesc)
	

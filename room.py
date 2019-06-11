from . import thing

##############################################################
# ROOM.PY - verbs for IntFicPy 
# Defines the Room class
##############################################################


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
		self.location = False
		# travel connections can be set to other Rooms after initialization
		self.north = None
		self.northeast = None
		self.east = None
		self.southeast = None
		self.south = None
		self.southwest = None
		self.west = None
		self.northwest = None
		self.up = False
		self.down = False
		self.entrance = False
		self.exit = False
		# room properties
		self.name = name
		self.desc = desc
		self.fulldesc = ""
		self.hasWalls = False
		self.contains = {}
		self.sub_contains = {}
		self.walls = []
		
		self.floor = thing.Thing("floor")
		self.floor.addSynonym("ground")
		self.floor.invItem = False
		self.floor.describeThing("")
		self.floor.xdescribeThing("You notice nothing remarkable about the floor.")
		self.addThing(self.floor)
		
		self.north_wall = thing.Thing("wall")
		self.north_wall.addSynonym("walls")
		self.north_wall.setAdjectives(["north"])
		self.north_wall.invItem = False
		self.north_wall.describeThing("")
		self.north_wall.xdescribeThing("You notice nothing remarkable about the north wall.")
		self.addThing(self.north_wall)
		self.walls.append(self.north_wall)
		
		self.south_wall = thing.Thing("wall")
		self.south_wall.addSynonym("walls")
		self.south_wall.setAdjectives(["south"])
		self.south_wall.invItem = False
		self.south_wall.describeThing("")
		self.south_wall.xdescribeThing("You notice nothing remarkable about the south wall.")
		self.addThing(self.south_wall)
		self.walls.append(self.south_wall)
		
		self.east_wall = thing.Thing("wall")
		self.east_wall.addSynonym("walls")
		self.east_wall.setAdjectives(["east"])
		self.east_wall.invItem = False
		self.east_wall.describeThing("")
		self.east_wall.xdescribeThing("You notice nothing remarkable about the east wall.")
		self.addThing(self.east_wall)
		self.walls.append(self.east_wall)
		
		self.west_wall = thing.Thing("wall")
		self.west_wall.addSynonym("walls")
		self.west_wall.setAdjectives(["west"])
		self.west_wall.invItem = False
		self.west_wall.describeThing("")
		self.west_wall.xdescribeThing("You notice nothing remarkable about the west wall.")
		self.addThing(self.west_wall)
		self.walls.append(self.west_wall)
	
	def addThing(self, item):
		"""Places a Thing in a Room
		Should generally be used by game creators instead of using room.contains.append() directly """
		from . import actor
		if isinstance(item, thing.Container):
			if item.lock_obj:
				if item.lock_obj.ix in self.contains:
					if not item.lock_obj in self.contains[lock_obj.ix]:
						self.addThing(item.lock_obj)
				else:
					self.addThing(item.lock_obj)
		if item.is_composite:
			for item2 in item.children:
				if item2.ix in self.contains:
					if not item2 in self.contains[item2.ix]:
						self.addThing(item2)
				else:
					self.addThing(item2)
		item.location = self
		# nested items
		if not isinstance(item, actor.Actor):
			nested = getNested(item)
			for t in nested:
				if t.ix in self.sub_contains:
					self.sub_contains[t.ix].append(t)
				else:
					self.sub_contains[t.ix] = [t]
		# top level item
		if item.ix in self.contains:
			self.contains[item.ix].append(item)
		else:
			self.contains[item.ix] = [item]
	
	def removeThing(self, item):
		"""Removes a Thing from a Room
		Should generally be used by game creators instead of using room.contains.remove() directly """
		if isinstance(item, thing.Container):
			if item.lock_obj:
				if item.lock_obj.ix in self.contains:
					if item.lock_obj in self.contains[item.lock_obj.ix]:
						self.removeThing(item.lock_obj)
				if item.lock_obj.ix in self.sub_contains:
					if item.lock_obj in self.sub_contains[item.lock_obj.ix]:
						self.removeThing(item.lock_obj)
		if item.is_composite:
			for item2 in item.children:
				if item2.ix in self.contains:
					if item2 in self.contains[item2.ix]:
						self.removeThing(item2)
				if item2.ix in self.sub_contains:
					if item2 in self.sub_contains[item2.ix]:
						self.removeThing(item2)
		rval = False
		# nested items
		nested = getNested(item)
		for t in nested:
			if t.ix in self.sub_contains:
				if t in self.sub_contains[t.ix]:
					self.sub_contains[t.ix].remove(t)
					if self.sub_contains[t.ix]==[]:
						del self.sub_contains[t.ix]
		# top level item
		if item.ix in self.contains:
			if item in self.contains[item.ix]:
				self.contains[item.ix].remove(item)
				if self.contains[item.ix]==[]:
					del self.contains[item.ix]
				rval = True
		if item.ix in self.sub_contains:
			if item in self.sub_contains[item.ix]:
				self.sub_contains[item.ix].remove(item)
				if self.sub_contains[item.ix]==[]:
					del self.sub_contains[item.ix]
				rval = True
		item.location = False
		return rval
	
	def getLocContents(self, me):
		if len(me.location.contains.items()) > 1:
			onlist = "Also " + me.location.contains_preposition + " " + me.location.getArticle(True) + me.location.verbose_name + " is "
			# iterate through contents, appending the verbose_name of each to onlist
			list_version = list(me.location.contains.keys())
			list_version.remove(me.ix)
			for key in list_version:
				if len(me.location.contains[key]) > 1:
					onlist = onlist + str(len(things)) + " " + me.location.contains[key][0].verbose_name
				else:
					onlist = onlist + me.location.contains[key][0].getArticle() + me.location.contains[key][0].verbose_name
				if key is list_version[-1]:
					onlist = onlist + "."
				elif key is list_version[-2]:
					onlist = onlist + " and "
				else:
					onlist = onlist + ", "
			self.fulldesc = self.fulldesc + onlist
	
	def describe(self, me, app):
		"""Prints the Room title and description and lists items in the Room """
		self.fulldesc = self.desc
		desc_loc = False
		child_items = []
		for key, things in self.contains.items():
			for item in things:
				if item==me.location:
					desc_loc = key
				elif item.parent_obj:
					child_items.append(item.ix)
			if desc_loc != key and key not in child_items and len(things) > 1:
				self.fulldesc = self.fulldesc + " There are " + str(len(things)) + " " + things[0].getPlural() + " here. "
			elif desc_loc != key and key not in child_items and len(things) > 0:	
				self.fulldesc = self.fulldesc + " " + things[0].desc
			# give player "knowledge" of a thing upon having it described
			if key not in me.knows_about:
				me.knows_about.append(key)
		if desc_loc:
			self.fulldesc = self.fulldesc + "<br>"
			if len(self.contains[desc_loc]) > 2:
				self.fulldesc = self.fulldesc + ("You are " + me.position + " " + me.location.contains_preposition + " " + me.location.getArticle() + me.location.verbose_name + ". ")
				self.getLocContents(me)
				self.fulldesc = self.fulldesc + ("There are " + str(len(self.contains[desc_loc]) - 1) + " more " + self.contains[desc_loc][0].getPlural + " nearby. ")
			elif len(self.contains[desc_loc]) > 1:
				self.fulldesc = self.fulldesc + ("You are " + me.position + " " + me.location.contains_preposition + " " + me.location.getArticle() + me.location.verbose_name + ". ")
				self.getLocContents(me)
				self.fulldesc = self.fulldesc + ("There is another " + self.contains[desc_loc][0].verbose_name + " nearby. ")
			else:
				self.fulldesc = self.fulldesc + ("You are " + me.position + " " + me.location.contains_preposition + " " + me.location.getArticle() + me.location.verbose_name + ". ")	
				self.getLocContents(me)
		app.printToGUI("<b>" + self.name + "</b>")
		app.printToGUI(self.fulldesc)

class OutdoorRoom(Room):
	"""Room is the class for outdoor locations in an IntFicPy game
	OutdoorRooms have no walls, and the floor is called ground"""
	def __init__(self, name, desc):
		"""Initially set basic properties for the OutdoorRoom instance """
		# indexing for save
		global room_ix
		self.ix = "room" + str(room_ix)
		room_ix = room_ix + 1
		rooms[self.ix] = self
		self.location = False
		# travel connections can be set to other Rooms after initialization
		self.north = None
		self.northeast = None
		self.east = None
		self.southeast = None
		self.south = None
		self.southwest = None
		self.west = None
		self.northwest = None
		self.up = False
		self.down = False
		self.entrance = False
		self.exit = False
		# room properties
		self.name = name
		self.desc = desc
		self.fulldesc = desc
		self.hasWalls = False
		self.contains = {}
		self.sub_contains = {}
		self.walls = []
		
		self.floor = thing.Thing("ground")
		self.floor.invItem = False
		self.floor.describeThing("")
		self.floor.xdescribeThing("You notice nothing remarkable about the ground.")
		self.addThing(self.floor)

def getNested(target):
	"""Use a depth first search to find all nested Things in Containers and Surfaces
	Takes argument target, pointing to a Thing
	Returns a list of Things
	Used by multiple verbs """
	# list to populate with found Things
	nested = []
	# iterate through top level contents
	for key, items in target.contains.items():
		for item in items:
			lvl = 0
			push = False
			# a dictionary of levels used to keep track of what has not yet been searched
			lvl_dict = {}
			lvl_dict[0] = []
			# get a list of things in the top level
			for key, things in item.contains.items():
				for thing in things:
					lvl_dict[0].append(thing)
			# a list of the parent items of each level
			# last item is current parent
			lvl_parent = [item]
			if item not in nested:
				nested.append(item)
			# when the bottom level is empty, the search is complete
			while lvl_dict[0] != []:
				# a list of searched items to remove from the level
				remove_scanned = []
				# pop to lower level if empty
				if lvl_dict[lvl]==[]:
					lvl_dict[lvl-1].remove(lvl_parent[-1])
					lvl_parent = lvl_parent[:-1]
					lvl = lvl - 1
				# scan items on current level
				for y in lvl_dict[lvl]:
					if not y in nested:
						nested.append(y)
					# if y contains items, push into y.contains 
					if y.contains != {}:
						lvl = lvl + 1
						lvl_dict[lvl] = []
						for things, key in item.contains.items():
							for thing in things:
								lvl_dict[lvl].append(thing)
						lvl_parent.append(y)
						push = True
						#break
					else:
						remove_scanned.append(y)
				# remove scanned items from lvl_dict
				for r in remove_scanned:
					# NOTE: this will break for duplicate objects with contents
					if push:
						lvl_dict[lvl-1].remove(r)
					else:
						lvl_dict[lvl].remove(r)
				
				# reset push marker
				push = False
	return nested

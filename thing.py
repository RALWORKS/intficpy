from . import vocab
import copy

##############################################################
# THING.PY - the Thing class for IntFicPy 
# Defines the Thing class,  its subclasses Surface, Container, and Clothing, and the thing dictionary
##############################################################

# a dictionary of the indeces of all Thing objects, including subclass instances, mapped to their object
# populated at runtime
things = {}
# index is an integer appended to the string "thing"- increases by 1 for each Thing defined
# index of a Thing will always be the same provided the game file is written according to the rules
thing_ix = 0

class Thing:
	"""Thing is the overarching class for all items that exist in the game """
	def __init__(self, name):
		"""Sets essential properties for the Thing instance """
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
		self.distinct = True
		# False except when Thing is the face of a TravelConnector
		self.connection = False
		self.direction = False
		# thing properties
		self.far_away = False
		self.is_composite = False
		self.parent_obj = False
		self.size = 50
		self.contains_preposition = False
		self.contains_preposition_inverse = False
		self.canSit = False
		self.canStand = False
		self.canLie = False
		self.isPlural = False
		self.special_plural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = True
		self.adjectives = []
		self.cannotTakeMsg = "You cannot take that."
		self.contains = {}
		self.sub_contains = {}
		self.wearable = False
		self.location = False
		self.name = name
		self.synonyms = []
		# verbose name will be updated when adjectives are added
		self.verbose_name = name
		# Thing instances that are not Actors cannot be spoken to
		self.give = False
		# the default description to print from the room
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
		# the default description for the examine command
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]
	
	def makeKnown(self, me):
		if not self.ix in me.knows_about:
			me.knows_about.append(self.ix)
	
	def addSynonym(self, word):
		"""Adds a synonym (noun) that can be used to refer to a Thing
		Takes argument word, a string, which should be a single noun """
		self.synonyms.append(word)
		if word in vocab.nounDict:
			if self not in vocab.nounDict[word]:
				vocab.nounDict[word].append(self)
		else:
			vocab.nounDict[word] = [self]
			
	def removeSynonym(self, word):
		"""Adds a synonym (noun) that can be used to refer to a Thing
		Takes argument word, a string, which should be a single noun """
		if word in self.synonyms:
			self.synonyms.remove(word)
		if word in vocab.nounDict:
			if self in vocab.nounDict[word]:
				vocab.nounDict[word].remove(self)
			if vocab.nounDict[word] == []:
				del vocab.nounDict[word]
	
	def setAdjectives(self, adj_list, update_desc=True):
		"""Sets adjectives for a Thing
		Takes arguments adj_list, a list of one word strings (adjectives), and update_desc, a Boolean defaulting to True
		Game creators should set update_desc to False if using a custom desc or xdesc for a Thing """
		self.adjectives = adj_list
		self.verbose_name = " ".join(adj_list) + " " + self.name
		if update_desc:
			self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
			self.desc = self.base_desc

	def getArticle(self, definite=False):
		"""Gets the correct article for a Thing
		Takes argument definite (defaults to False), which specifies whether the article is definite
		Returns a string """
		if not self.hasArticle:
			return ""
		elif definite or self.isDefinite:
			return "the "
		else:
			if self.verbose_name[0] in ["a", "e", "i", "o", "u"]:
				return "an "
			else:
				return "a "
	
	def getPlural(self):
		if self.special_plural:
			return self.special_plural
		elif self.verbose_name[-1]=="s" or self.verbose_name[-1]=="x" or self.verbose_name[-1]=="z" or self.verbose_name[-2:]=="sh" or self.verbose_name[-2:]=="ch":
			return self.verbose_name + "es"
		else:
			return self.verbose_name + "s"
	
	def makeUnique(self):
		"""Make a Thing unique (use definite article)
		Creators should use a Thing's makeUnique method rather than setting its definite property directly """
		self.isDefinite = True
		self.base_desc = self.getArticle().capitalize() + self.verbose_name + " is here."
		self.desc = self.base_desc

	def copyThing(self):
		"""Copy a Thing, keeping the index of the original. Safe to use for dynamic item duplication. """
		out = copy.copy(self)
		vocab.nounDict[out.name].append(out)
		out.setAdjectives(out.adjectives)
		for synonym in out.synonyms:
			vocab.nounDict[synonym].append(out)
		out.desc = self.desc
		out.xdesc = self.xdesc
		out.distinct = False
		return out
	
	def copyThingUniqueIx(self):
		"""Copy a Thing, creating a new index. NOT safe to use for dynamic item duplication. """
		out = copy.copy(self)
		global thing_ix
		out.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[out.ix] = out
		vocab.nounDict[out.name].append(out)
		out.setAdjectives(out.adjectives)
		for synonym in out.synonyms:
			vocab.nounDict[synonym].append(out)
		out.desc = self.desc
		out.xdesc = self.xdesc
		out.distinct = False
		return out
	
	def describeThing(self, description):
		self.base_desc = description
		self.desc = description
		if self.is_composite:
			if self.children_desc:
				self.desc = self.desc + self.children_desc
			else:
				for item in self.children:
					self.desc = self.desc + item.desc
		
	def xdescribeThing(self, description):
		self.base_xdesc = description
		self.xdesc = description
		if self.is_composite:
			if self.children_desc:
				self.xdesc = self.xdesc + self.children_desc
			else:
				for item in self.children:
					self.xdesc = self.xdesc + item.desc
		
	def addComposite(self, item):
		self.is_composite = True
		try:
			defined = self.child_Things
		except:
			self.children_desc = False
			self.child_Things = []
			self.child_Surfaces = []
			self.child_Containers = []
			self.child_UnderSpaces = []
			self.children = []
		item.parent_obj = self
		self.children.append(item)
		if isinstance(item, Surface):
			self.child_Surfaces.append(item)
		elif isinstance(item, Container):
			self.child_Containers.append(item)
		elif isinstance(item, UnderSpace):
			self.child_UnderSpaces.append(item)
		elif isinstance(item, Thing):
			self.child_Containers.append(item)
		self.location.addThing(item)
		item.setAdjectives(item.adjectives + self.adjectives + [self.name])
		#self.children_desc = ""
		#item.describeThing("")
		item.xdescribeThing("You notice nothing remarkable about " + item.getArticle(True) + item.verbose_name + ". ")
		item.invItem = False
		if isinstance(self, Container):
			self.updateDesc()
			self.containsListUpdate()
		if isinstance(self, Surface):
			self.containsListUpdate()
	
	def describeChildren(self, description):
		self.children_desc = description
		self.desc = self.desc + self.children_desc
		self.xdesc = self.xdesc + self.children_desc
		if isinstance(self, Container):
			self.updateDesc()
			self.containsListUpdate()
		if isinstance(self, Surface):
			self.containsListUpdate()

class Surface(Thing):
	"""Class for Things that can have other Things placed on them """
	def __init__(self, name, me):
		"""Sets the essential properties for a new Surface object """
		self.distinct = True
		self.me = me
		self.contains_preposition = "on"
		self.contains_preposition_inverse = "off"
		self.isPlural = False
		self.hasArticle = True
		self.isDefinite = False
		self.canSit = False
		self.canStand = False
		self.canLie = False
		# the items on the Surface
		self.contains = {}
		# items contained by items on the Surface
		# accessible by default, but not shown in outermost description
		self.sub_contains = {}
		self.far_away = False
		self.adjectives = []
		self.is_composite = False
		self.parent_obj = False
		self.size = 50
		self.name = name
		# verbose_name will be updated by Thing method setAdjectives 
		self.verbose_name = name
		self.give = False
		# default description printed by room
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
		# description of items on the Surface
		# will be appended to descriptions
		self.contains_desc = ""
		# Surfaces are not contains items by default, but can be safely made so
		self.invItem = False
		self.cannotTakeMsg = "You cannot take that."
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]
		# indexing and adding to dictionary for save/load
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self

	def containsListUpdate(self):
		"""Update description of contents
		Called when a Thing is added or removed """
		from .actor import Player
		onlist = " On the " + self.name + " is "
		# iterate through contents, appending the verbose_name of each to onlist
		list_version = list(self.contains.keys())
		player_here = False
		for key in list_version:
			for item in self.contains[key]:
				if isinstance(item, Player):
					list_version.remove(key)
					player_here = True
				elif item.parent_obj:
					list_version.remove(key)
		for key in list_version:
			if len(self.contains[key]) > 1:
				onlist = onlist + str(len(things)) + " " + self.contains[key][0].verbose_name
			else:
				onlist = onlist + self.contains[key][0].getArticle() + self.contains[key][0].verbose_name
			if key is list_version[-1]:
				onlist = onlist + "."
			elif key is list_version[-2]:
				onlist = onlist + " and "
			else:
				onlist = onlist + ", "
			if key not in self.me.knows_about:
				self.me.knows_about.append(key)
		# if contains is empty, there should be no onlist
		# TODO: consider rewriting this logic to avoid contructing an empty onlist, then deleting it
		if len(list_version)==0:
			onlist = ""
		if player_here:
			if onlist != "":
				onlist = onlist + "<br>"
			onlist = onlist + "You are on " + self.getArticle(True) + self.verbose_name + "."
		# append onlist to description
		if self.is_composite:
			if self.children_desc:
				self.desc = self.base_desc + self.children_desc
				self.xdesc = self.base_xdesc + self.children_desc
			else:
				self.xdesc = self.base_xdesc
				self.desc = self.base_desc
				for item in self.children:
					self.xdesc = self.xdesc + item.desc
					self.desc = self.desc + item.desc
			self.desc = self.desc + onlist
			self.xdesc = self.xdesc + onlist
		else:
			self.desc = self.base_desc + onlist
			self.xdesc = self.base_xdesc + onlist
		self.contains_desc = onlist
	
	def addOn(self, item):
		"""Add a Thing to a Surface
		Takes argument item, pointing to a Thing"""
		from . import actor
		if isinstance(item, Container):
			if item.lock_obj and (item.lock_obj.ix in self.contains or item.lock_obj.ix in self.sub_contains):
				if not (item.lock_obj in self.contains[item.lock_obj.ix] or item.lock_obj in self.sub_contains[item.lock_obj.ix]):
					self.addOn(item.lock_obj)
			elif item.lock_obj:
				self.addOn(item.lock_obj)
		if item.is_composite:
			for item2 in item.children:
				if item2.ix in self.contains:
					if not item2 in self.contains[item2.ix]:
						self.addOn(item2)
				else:
					self.addOn(item2)
		item.location = self
		# nested items
		nested = getNested(item)
		next_loc = self.location
		while next_loc:
			if not isinstance(item, actor.Actor):
				for t in nested:
					if t.ix in next_loc.sub_contains:
						if not t in next_loc.sub_contains[t.ix]:
							next_loc.sub_contains[t.ix].append(t)
					else:
						next_loc.sub_contains[t.ix] = [t]
			if item.ix in next_loc.sub_contains:
				if not item in next_loc.sub_contains[item.ix]:
					next_loc.sub_contains[item.ix].append(item)
			else:
				next_loc.sub_contains[item.ix] = [item]
			next_loc = next_loc.location
		for t in nested:
			if not isinstance(item, actor.Actor):
				if t.ix in self.sub_contains:
					self.sub_contains[t.ix].append(t)
				else:
					self.sub_contains[t.ix] = [t]
		# top level item
		if item.ix in self.contains:
			self.contains[item.ix].append(item)
		else:
			self.contains[item.ix] = [item]
		if item.ix in self.location.sub_contains:
			self.location.sub_contains[item.ix].append(item)
		else:
			self.location.sub_contains[item.ix] = [item]
		self.containsListUpdate()

	def removeThing(self, item):
		"""Remove a Thing from a Surface """
		if isinstance(item, Container):
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
		nested = getNested(item)
		for t in nested:
			if t.ix in self.sub_contains:
				if t in self.sub_contains[t.ix]:
					self.sub_contains[t.ix].remove(t)
					if self.sub_contains[t.ix]==[]:
						del self.sub_contains[t.ix]
		next_loc = self.location
		while next_loc:
			if item.ix in next_loc.sub_contains:
				if item in next_loc.sub_contains[item.ix]:
					next_loc.sub_contains[item.ix].remove(item)
					if next_loc.sub_contains[item.ix] == {}:
						del next_loc.sub_contains[item.ix]
			for t in nested:
				if t.ix in next_loc.sub_contains:
					if t in next_loc.sub_contains[t.ix]:
						next_loc.sub_contains[t.ix].remove(t)
						if next_loc.sub_contains[t.ix]==[]:
							del next_loc.sub_contains[t.ix]
			next_loc = next_loc.location
		rval = False
		if item.ix in self.contains:
			if item in self.contains[item.ix]:
				self.contains[item.ix].remove(item)
				if self.contains[item.ix]==[]:
					del self.contains[item.ix]
				rval = True
				item.location = False
				self.containsListUpdate()
		if item.ix in self.sub_contains:
			if item in self.sub_contains[item.ix]:
				self.sub_contains[item.ix].remove(item)
				if self.sub_contains[item.ix]==[]:
					del self.sub_contains[item.ix]
				rval = True
				item.location = False
				self.containsListUpdate()
		return rval
			

	def describeThing(self, description):
		self.base_desc = description
		if self.is_composite:
			if self.children_desc:
				self.desc = self.base_desc + self.children_desc
			else:
				self.desc = self.base_desc
				for item in self.children:
					self.desc = self.desc + item.desc
		self.containsListUpdate()
	
	def xdescribeThing(self, description):
		self.base_xdesc = description
		if self.is_composite:
			if self.children_desc:
				self.xdesc = self.xdesc + self.children_desc
			else:
				self.xdesc = self.base_xdesc
				for item in self.children:
					self.desc = self.xdesc + item.desc
		self.containsListUpdate()
	
# NOTE: Container duplicates a lot of code from Surface. Consider a parent class for Things with a contains property
class Container(Thing):
	"""Things that can contain other Things """
	def __init__(self, name, me):
		"""Set basic properties for the Container instance
		Takes argument name, a single noun (string)"""
		self.distinct = True
		self.me = me
		self.size = 50
		self.contains_preposition = "in"
		self.contains_preposition_inverse = "out"
		self.far_away = False
		self.has_lid = False
		self.lock_obj = False
		self.lock_desc = ""
		self.state_desc = ""
		self.is_composite = False
		self.parent_obj = False
		self.canSit = False
		self.canStand = False
		self.canLie = False
		self.isPlural = False
		self.special_plural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = True
		self.cannotTakeMsg = "You cannot take that."
		self.contains = {}
		self.sub_contains = {}
		self.name = name
		self.verbose_name = name
		self.adjectives = []
		self.give = False
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
		# description of contents
		self.contains_desc = ""
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]
		# index and add to dictionary for save/load
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
	
	def containsListUpdate(self):
		"""Update description for addition/removal of items from the Container instance """
		from .actor import Player
		desc = self.base_desc
		xdesc = self.base_xdesc
		if self.has_lid:
			desc = desc + self.state_desc
			xdesc = xdesc + self.state_desc
			if not self.is_open:
				self.desc = desc
				self.xdesc = xdesc + self.lock_desc
				self.contains_desc = "You cannot see inside " + self.getArticle(True) + self.verbose_name + " as it is closed."
				return False
		inlist = " In the " + self.name + " is "
		# iterate through contents, appending the verbose_name of each to onlist
		list_version = list(self.contains.keys())
		player_here = False
		for key in list_version:
			for item in self.contains[key]:
				if isinstance(item, Player):
					list_version.remove(key)
					player_here = True
				elif item.parent_obj:
					list_version.remove(key)
		for key in list_version:
			if len(self.contains[key]) > 1:
				inlist = inlist + str(len(things)) + " " + self.contains[key][0].verbose_name
			else:
				inlist = inlist + self.contains[key][0].getArticle() + self.contains[key][0].verbose_name
			if key is list_version[-1]:
				inlist = inlist + "."
			elif key is list_version[-2]:
				inlist = inlist + " and "
			else:
				inlist = inlist + ", "
			if key not in self.me.knows_about:
				self.me.knows_about.append(key)
		# remove the empty inlist in the case of no contents
		# TODO: consider rewriting this logic to avoid contructing an empty inlist, then deleting it
		if len(list_version)==0:
			inlist = ""
		if player_here:
			if inlist != "":
				inlist = inlist + "<br>"
			inlist = inlist + "You are in " + self.getArticle(True) + self.verbose_name + "."
		# update descriptions
		if self.is_composite:
			if self.children_desc:
				self.desc = self.base_desc + self.children_desc
				self.xdesc = self.base_xdesc + self.children_desc
			else:
				self.xdesc = self.base_xdesc
				self.desc = self.base_desc
				for item in self.children:
					self.xdesc = self.xdesc + item.desc
					self.desc = self.desc + item.desc
			self.desc = self.desc + inlist
			self.xdesc = self.xdesc + inlist
		else:
			self.desc = desc + inlist
			self.xdesc = xdesc + self.lock_desc + inlist
		self.contains_desc = inlist
		return True
	
	def addIn(self, item):
		"""Add an item to contents, update descriptions
		Takes argument item, pointing to a Thing """
		from . import actor
		item.location = self
		if isinstance(item, Container):
			if item.lock_obj and (item.lock_obj.ix in self.contains or item.lock_obj.ix in self.sub_contains):
				if not (item.lock_obj in self.contains[item.lock_obj.ix] or item.lock_obj in self.sub_contains[item.lock_obj.ix]):
					self.addIn(item.lock_obj)
			elif item.lock_obj:
				self.addIn(item.lock_obj)
		if item.is_composite:
			for item2 in item.children:
				if item2.ix in self.contains:
					if not item2 in self.contains[item2.ix]:
						self.addIn(item2)
				else:
					self.addIn(item2)
		# nested items
		nested = getNested(item)
		next_loc = self.location
		while next_loc:
			if not isinstance(item, actor.Actor):
				for t in nested:
					if t.ix in next_loc.sub_contains:
						if not t in next_loc.sub_contains[t.ix]:
							next_loc.sub_contains[t.ix].append(t)
					else:
						next_loc.sub_contains[t.ix] = [t]
			if item.ix in next_loc.sub_contains:
				if not item in next_loc.sub_contains[item.ix]:
					next_loc.sub_contains[item.ix].append(item)
			else:
				next_loc.sub_contains[item.ix] = [item]
			next_loc = next_loc.location
		if not isinstance(item, actor.Actor):
			for t in nested:
				if t.ix in self.sub_contains:
					self.sub_contains[t.ix].append(t)
				else:
					self.sub_contains[t.ix] = [t]
		if item.ix in self.contains:
			self.contains[item.ix].append(item)
		else:
			self.contains[item.ix] = [item]
		if self.has_lid:
			if not self.is_open:
				self.hideContents()
		self.containsListUpdate()
	
	def revealContents(self):
		list_version = list(self.contains.keys())
		for key in list_version:
			for item in self.contains[key]:
				nested = getNested(item)
				next_loc = self.location
				while next_loc:
					for x in nested:
						if x.ix in next_loc.sub_contains:
							next_loc.sub_contains[x.ix].append(x)
						else:
							next_loc.sub_contains[x.ix] = [x]
					if item.ix in next_loc.sub_contains:
						next_loc.sub_contains[item.ix].append(item)
					else:
						next_loc.sub_contains[item.ix] = [item]
					next_loc = next_loc.location
					
	def hideContents(self):
		list_version = list(self.contains.keys())
		for key in list_version:
			for item in self.contains[key]:
				nested = getNested(item)
				next_loc = self.location
				while next_loc:
					for x in nested:
						if x.ix in next_loc.sub_contains:
							next_loc.sub_contains[x.ix].remove(x)
							if next_loc.sub_contains[x.ix] == []:
								del next_loc.sub_contains[x.ix]
					if item.ix in next_loc.sub_contains:
						next_loc.sub_contains[item.ix].remove(item)
						if next_loc.sub_contains[item.ix] == []:
							del next_loc.sub_contains[item.ix]
					next_loc = next_loc.location
	
	def removeThing(self, item):
		"""Remove an item from contents, update decription """
		if isinstance(item, Container):
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
		nested = getNested(item)
		for t in nested:
			if t.ix in self.sub_contains:
				if t in self.sub_contains[t.ix]:
					self.sub_contains[t.ix].remove(t)
					if self.sub_contains[t.ix]==[]:
						del self.sub_contains[t.ix]
		next_loc = self.location
		while next_loc:
			if item.ix in next_loc.sub_contains:
				if item in next_loc.sub_contains[item.ix]:
					next_loc.sub_contains[item.ix].remove(item)
					if next_loc.sub_contains[item.ix] == {}:
						del next_loc.sub_contains[item.ix]
			for t in nested:
				if t.ix in next_loc.sub_contains:
					if t in next_loc.sub_contains[t.ix]:
						next_loc.sub_contains[t.ix].remove(t)
						if next_loc.sub_contains[t.ix]==[]:
							del next_loc.sub_contains[t.ix]
			next_loc = next_loc.location
		rval = False
		if item.ix in self.contains:
			if item in self.contains[item.ix]:
				self.contains[item.ix].remove(item)
				if self.contains[item.ix]==[]:
					del self.contains[item.ix]
				rval = True
				item.location = False
				self.containsListUpdate()
		if item.ix in self.sub_contains:
			if item in self.sub_contains[item.ix]:
				self.sub_contains[item.ix].remove(item)
				if self.sub_contains[item.ix]==[]:
					del self.sub_contains[item.ix]
				rval = True
				item.location = False
				self.containsListUpdate()
		return rval
	
	def setLock(self, lock_obj):
		if isinstance(lock_obj, Lock) and self.has_lid:
			if not lock_obj.parent_obj:
				self.lock_obj = lock_obj
				lock_obj.parent_obj = self
				self.location.addThing(lock_obj)
				lock_obj.setAdjectives(lock_obj.adjectives + self.adjectives + [self.name])
				if lock_obj.is_locked:
					self.lock_desc = " It is locked. "
				else:
					self.lock_desc = " It is unlocked. "
				lock_obj.describeThing("")
				lock_obj.xdescribeThing("You notice nothing remarkable about " + lock_obj.getArticle(True) + lock_obj.verbose_name + ". ")
				self.updateDesc()
			else:
				print("Cannot set lock_obj for " + self.verbose_name + ": lock_obj.parent already set ")
		else:
			print("Cannot set lock_obj for " + self.verbose_name + ": not a Lock ")
			
	def describeThing(self, description):
		self.base_desc = description
		self.desc = self.base_desc + self.state_desc
		if self.is_composite:
			if self.children_desc:
				self.desc = self.desc + self.children_desc
			else:
				for item in self.children:
					self.desc = self.desc + item.desc
		self.containsListUpdate()
	
	def xdescribeThing(self, description):
		self.base_xdesc = description
		self.xdesc = self.base_xdesc + self.state_desc + self.lock_desc
		if self.is_composite:
			if self.children_desc:
				self.xdesc = self.xdesc + self.children_desc
			else:
				for item in self.children:
					self.xdesc = self.xdesc + item.desc
		self.containsListUpdate()
	
	def updateDesc(self):
		self.containsListUpdate()
	
	def giveLid(self):
		self.has_lid = True
		self.is_open = False
		self.state_desc = " It is currently closed. "
		self.containsListUpdate()
	
	def makeOpen(self):
		self.is_open = True
		self.state_desc = " It is currently open. "
		self.containsListUpdate()
		self.revealContents()
		if self.parent_obj:
			self.parent_obj.describeThing(self.parent_obj.base_desc)
			self.parent_obj.xdescribeThing(self.parent_obj.base_xdesc)
			
	def makeClosed(self):
		self.is_open = False
		self.state_desc = " It is currently closed. "
		self.containsListUpdate()
		self.hideContents()
		if self.parent_obj:
			self.parent_obj.describeThing(self.parent_obj.base_desc)
			self.parent_obj.xdescribeThing(self.parent_obj.base_xdesc)
		
# NOTE: May not be necessary as a distinct class. Consider just using the wearable property.
class Clothing(Thing):
	"""Class for Things that can be worn """
	# all clothing is wearable
	wearable = True
	# uses __init__ from Thing

class AbstractClimbable(Thing):
	"""Represents one end of a staircase or ladder.
	Creators should generally use a LadderConnector or StaircaseConnector (travel.py) rather than directly creating AbstractClimbable instances. """
	def __init__(self, name):
		"""Sets essential properties for the AbstractClimbable instance """
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
		self.distinct = True
		# connector properties
		self.twin = False
		self.connection = False
		self.direction = False
		# thing properties
		self.far_away = False
		self.is_composite = False
		self.parent_obj = False
		self.size = 50
		self.contains_preposition = False
		self.contains_preposition_inverse = False
		self.canSit = False
		self.canStand = False
		self.canLie = False
		self.isPlural = False
		self.special_plural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = False
		self.adjectives = []
		self.cannotTakeMsg = "You cannot take that."
		self.contains = {}
		self.sub_contains = {}
		self.wearable = False
		self.location = False
		self.name = name
		self.synonyms = []
		# verbose name will be updated when adjectives are added
		self.verbose_name = name
		# the default description to print from the room
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
		# the default description for the examine command
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]

class Door(Thing):
	"""Represents one side of a door. Always define with a twin, and set a direction. Can be open or closed.
	Creators should generally use DoorConnectors (travel.py) rather than defining Doors  directly. """
	def __init__(self, name):
		"""Sets essential properties for the Door instance """
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
		self.distinct = True
		# door properties
		self.direction = False
		self.twin = False
		self.is_open = False
		self.lock_obj = False
		self.state_desc = "It is currently closed. "
		self.lock_desc = ""
		self.connection = False
		# thing properties
		self.far_away = False
		self.is_composite = False
		self.parent_obj = False
		self.size = 50
		self.contains_preposition = False
		self.contains_preposition_inverse = False
		self.canSit = False
		self.canStand = False
		self.canLie = False
		self.isPlural = False
		self.special_plural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = False
		self.adjectives = []
		self.cannotTakeMsg = "You cannot take that."
		self.contains = {}
		self.sub_contains = {}
		self.wearable = False
		self.location = False
		self.name = name
		self.synonyms = []
		# verbose name will be updated when adjectives are added
		self.verbose_name = name
		# the default description to print from the room
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc + self.state_desc
		self.xdesc = self.base_xdesc + self.state_desc
		# the default description for the examine command
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]
	
	def makeOpen(self):
		self.is_open = True
		self.state_desc = "It is currently open. "
		self.desc = self.base_desc + self.state_desc
		self.xdesc = self.base_xdesc + self.state_desc
		if self.twin:
			if not self.twin.is_open:
				self.twin.makeOpen()
		if self.parent_obj:
			self.parent_obj.describeThing(self.parent_obj.base_desc)
			self.parent_obj.xdescribeThing(self.parent_obj.base_xdesc)
	
	def makeClosed(self):
		self.is_open = False
		self.state_desc = "It is currently closed. "
		self.desc = self.base_desc + self.state_desc
		self.xdesc = self.base_xdesc + self.state_desc
		if self.twin:
			if self.twin.is_open:
				self.twin.makeClosed()
		if self.parent_obj:
			self.parent_obj.describeThing(self.parent_obj.base_desc)
			self.parent_obj.xdescribeThing(self.parent_obj.base_xdesc)
	
	def describeThing(self, description):
		self.base_desc = description
		self.desc = description + self.state_desc
		if self.is_composite:
			if self.children_desc:
				self.desc = self.desc + self.children_desc
			else:
				for item in self.children:
					self.desc = self.desc + item.desc
		
	def xdescribeThing(self, description):
		self.base_xdesc = description
		self.xdesc = description + self.state_desc + self.lock_desc
		if self.is_composite:
			if self.children_desc:
				self.xdesc = self.xdesc + self.children_desc
			else:
				for item in self.children:
					self.xdesc = self.xdesc + item.desc
		
	def updateDesc(self):
		self.xdesc = self.base_xdesc + self.state_desc + self.lock_desc
		self.desc = self.base_desc + self.state_desc
		if self.is_composite:
			if self.children_desc:
				self.desc = self.desc + self.children_desc
				self.xdesc = self.xdesc + self.children_desc
			else:
				for item in self.children:
					self.desc = self.desc + item.desc
					self.xdesc = self.xdesc + item.desc

class Key(Thing):
	"""Class for keys """
	def __init__(self, name="key"):
		"""Sets essential properties for the Thing instance """
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
		self.distinct = True
		# key properties
		self.lock = False
		# False except when Thing is the face of a TravelConnector
		self.connection = False
		self.direction = False
		# thing properties
		self.far_away = False
		self.is_composite = False
		self.parent_obj = False
		self.size = 10
		self.contains_preposition = False
		self.contains_preposition_inverse = False
		self.canSit = False
		self.canStand = False
		self.canLie = False
		self.isPlural = False
		self.special_plural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = True
		self.adjectives = []
		self.cannotTakeMsg = "You cannot take that."
		self.contains = {}
		self.sub_contains = {}
		self.wearable = False
		self.location = False
		self.name = name
		self.synonyms = []
		# verbose name will be updated when adjectives are added
		self.verbose_name = name
		# Thing instances that are not Actors cannot be spoken to
		self.give = False
		# the default description to print from the room
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
		# the default description for the examine command
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]

class Lock(Thing):
	"""Lock is the class for lock items in the game  """
	def __init__(self, is_locked, key_obj, name="lock"):
		"""Sets essential properties for the Lock instance """
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
		self.distinct = True
		# lock
		self.is_locked = is_locked
		self.key_obj = key_obj
		self.is_composite = False
		self.parent_obj = False
		self.twin = False
		if self.is_locked:
			self.state_desc = " It is currently locked. "
		else:
			self.state_desc = "It is currently unlocked. "
		# False except when Thing is the face of a TravelConnector
		self.connection = False
		self.direction = False
		# thing properties
		self.far_away = False
		self.size = 20
		self.contains_preposition = False
		self.contains_preposition_inverse = False
		self.canSit = False
		self.canStand = False
		self.canLie = False
		self.isPlural = False
		self.special_plural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = False
		self.adjectives = []
		self.cannotTakeMsg = "You cannot take that."
		self.contains = {}
		self.sub_contains = {}
		self.wearable = False
		self.location = False
		self.name = name
		self.synonyms = []
		# verbose name will be updated when adjectives are added
		self.verbose_name = name
		# Thing instances that are not Actors cannot be spoken to
		self.give = False
		# the default description to print from the room
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc + self.state_desc
		# the default description for the examine command
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]

	def makeUnlocked(self):
		self.is_locked = False
		self.state_desc = "It is currently unlocked. "
		self.xdesc = self.base_xdesc + self.state_desc
		if self.parent_obj:
			self.parent_obj.lock_desc = " It is unlocked. "
			self.parent_obj.updateDesc()
		if self.twin:
			if self.twin.is_locked:
				self.twin.makeUnlocked()
	
	def makeLocked(self):
		self.is_locked = True
		self.state_desc = "It is currently locked. "
		self.xdesc = self.base_xdesc + self.state_desc
		if self.parent_obj:
			self.parent_obj.lock_desc = " It is locked. "
			self.parent_obj.updateDesc()
		if self.twin:
			if not self.twin.is_locked:
				self.twin.makeLocked()
				
	def describeThing(self, description):
		self.base_desc = description
		self.desc = self.base_desc
		if self.is_composite:
			if self.children_desc:
				self.desc = self.desc + self.children_desc
			else:
				for item in children:
					self.desc = self.desc + item.desc
	
	def xdescribeThing(self, description):
		self.base_xdesc = description
		self.xdesc = self.base_xdesc + self.state_desc
		if self.is_composite:
			if self.children_desc:
				self.xdesc = self.xdesc + self.children_desc
			else:
				for item in children:
					self.xdesc = self.xdesc + item.desc
	
class Abstract(Thing):
	"""Class for abstract game items with no location, such as ideas"""
	def __init__(self, name):
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
		self.distinct = True
		# properties
		self.far_away = False
		self.is_composite = False
		self.parent_obj = False
		self.isPlural = False
		self.special_plural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = False
		self.adjectives = []
		self.cannotTakeMsg = "You cannot take that."
		self.contains = {}
		self.wearable = False
		self.location = False
		self.name = name
		self.synonyms = []
		# verbose name will be updated when adjectives are added
		self.verbose_name = name
		self.give = False
		# no physical form or location, so no desc/xdesc
		#self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
		#self.base_xdesc = self.base_desc
		#self.desc = self.base_desc
		#self.xdesc = self.base_xdesc
		# the default description for the examine command
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]
	
	def makeKnown(self, me):
		if not self.ix in me.knows_about:
			me.knows_about.append(self.ix)

class UnderSpace(Thing):
	"""Things that can have other Things underneath """
	def __init__(self, name, me):
		"""Set basic properties for the UnderSpace instance
		Takes argument name, a single noun (string)"""
		self.distinct = True
		self.me = me
		self.far_away = False
		self.revealed = False
		self.size = 50
		self.contains_preposition = "under"
		self.contains_preposition_inverse = "out"
		self.is_composite = False
		self.parent_obj = False
		self.canSit = False
		self.canStand = False
		self.canLie = False
		self.isPlural = False
		self.special_plural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = True
		self.cannotTakeMsg = "You cannot take that."
		self.contains = {}
		self.sub_contains = {}
		self.name = name
		self.verbose_name = name
		self.adjectives = []
		self.give = False
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
		# description of contents
		self.contains_desc = ""
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]
		# index and add to dictionary for save/load
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
	
	def containsListUpdate(self):
		"""Update description for addition/removal of items from the Container instance """
		from .actor import Player
		desc = self.base_desc
		xdesc = self.base_xdesc
		if not self.revealed:
			return False
		inlist = " " + self.contains_preposition.capitalize() + " " + self.getArticle(True) + self.verbose_name + " is "
		# iterate through contents, appending the verbose_name of each to onlist
		list_version = list(self.contains.keys())
		player_here = False
		for key in list_version:
			for item in self.contains[key]:
				if key in list_version:
					if isinstance(item, Player):
						list_version.remove(key)
						player_here = True
					elif item.parent_obj:
						list_version.remove(key)
		for key in list_version:
			if len(self.contains[key]) > 1:
				inlist = inlist + str(len(things)) + " " + self.contains[key][0].verbose_name
			else:
				inlist = inlist + self.contains[key][0].getArticle() + self.contains[key][0].verbose_name
			if key is list_version[-1]:
				inlist = inlist + "."
			elif key is list_version[-2]:
				inlist = inlist + " and "
			else:
				inlist = inlist + ", "
			if key not in self.me.knows_about:
				self.me.knows_about.append(key)
		# remove the empty inlist in the case of no contents
		# TODO: consider rewriting this logic to avoid contructing an empty inlist, then deleting it
		if len(list_version)==0:
			inlist = ""
		if player_here:
			if inlist != "":
				inlist = inlist + "<br>"
			inlist = inlist + "You are in " + self.getArticle(True) + self.verbose_name + "."
		# update descriptions
		if self.is_composite:
			if self.children_desc:
				self.desc = self.desc + self.children_desc
				self.xdesc = self.xdesc + self.children_desc
			else:
				for item in children:
					self.desc = self.desc + item.desc
					self.xdesc = self.xdesc + item.desc
			self.desc = self.desc + inlist
			self.xdesc = self.xdesc + inlist
		else:
			self.desc = desc + inlist
			self.xdesc = xdesc + inlist
		self.contains_desc = inlist
		return True
	
	def revealUnder(self):
		from . import actor
		self.revealed = True
		self.containsListUpdate()
		next_loc = self.location
		for key in self.contains:
			for item in self.contains[key]:
				nested = getNested(item)
				while next_loc:
					if not isinstance(item, actor.Actor):
						for t in nested:
							if t.ix in next_loc.sub_contains:
								if not t in next_loc.sub_contains[t.ix]:
									next_loc.sub_contains[t.ix].append(t)
							else:
								next_loc.sub_contains[t.ix] = [t]
					if item.ix in next_loc.sub_contains:
						if not item in next_loc.sub_contains[item.ix]:
							next_loc.sub_contains[item.ix].append(item)
					else:
						next_loc.sub_contains[item.ix] = [item]
					next_loc = next_loc.location
	
	def moveContentsOut(self):
		contents = copy.copy(self.contains)
		out = ""
		list_version = list(contents.keys())
		counter = 0
		for key in contents:
			if len(contents[key])==1:
				out = out + contents[key][0].getArticle() + contents[key][0].verbose_name
			else:
				n_things = str(len(contents[key]))
				out = out + n_things + contents[key][0].verbose_name
				counter = counter + 1
			if len(list_version) > 1:
				if key == list_version[-2]:
					out = out + ", and "
				elif key != list_version[-1]:
					out = out + ", "
			elif key != list_version[-1]:
				out = out + ", "
			for item in contents[key]:
				self.removeThing(item)
				self.location.addThing(item)
			counter = counter + 1
		if counter > 1:
			return [out, True]
		else:
			return [out, False]

	def addUnder(self, item, revealed=False):
		"""Add an item to contents, update descriptions
		Takes argument item, pointing to a Thing """
		from . import actor
		item.location = self
		if isinstance(item, Container):
			if item.lock_obj and (item.lock_obj.ix in self.contains or item.lock_obj.ix in self.sub_contains):
				if not (item.lock_obj in self.contains[item.lock_obj.ix] or item.lock_obj in self.sub_contains[item.lock_obj.ix]):
					self.addIn(item.lock_obj)
			elif item.lock_obj:
				self.addIn(item.lock_obj)
		if item.is_composite:
			for item2 in item.children:
				if item2.ix in self.contains:
					if not item2 in self.contains[item2.ix]:
						self.addIn(item2)
				else:
					self.addIn(item2)
		# nested items
		nested = getNested(item)
		next_loc = self.location
		if revealed:
			while next_loc:
				if not isinstance(item, actor.Actor):
					for t in nested:
						if t.ix in next_loc.sub_contains:
							if not t in next_loc.sub_contains[t.ix]:
								next_loc.sub_contains[t.ix].append(t)
						else:
							next_loc.sub_contains[t.ix] = [t]
				if item.ix in next_loc.sub_contains:
					if not item in next_loc.sub_contains[item.ix]:
						next_loc.sub_contains[item.ix].append(item)
				else:
					next_loc.sub_contains[item.ix] = [item]
				next_loc = next_loc.location
		if not isinstance(item, actor.Actor):
			for t in nested:
				if t.ix in self.sub_contains:
					if not t in self.sub_contains[t.ix]:
						self.sub_contains[t.ix].append(t)
				else:
					self.sub_contains[t.ix] = [t]
		if item.ix in self.contains:
			self.contains[item.ix].append(item)
		else:
			self.contains[item.ix] = [item]
		self.revealed = revealed
		self.containsListUpdate()
	
	def removeThing(self, item):
		"""Remove an item from contents, update decription """
		if isinstance(item, Container):
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
		nested = getNested(item)
		for t in nested:
			if t.ix in self.sub_contains:
				if t in self.sub_contains[t.ix]:
					self.sub_contains[t.ix].remove(t)
					if self.sub_contains[t.ix]==[]:
						del self.sub_contains[t.ix]
		next_loc = self.location
		while next_loc:
			if item.ix in next_loc.sub_contains:
				if item in next_loc.sub_contains[item.ix]:
					next_loc.sub_contains[item.ix].remove(item)
					if next_loc.sub_contains[item.ix] == {}:
						del next_loc.sub_contains[item.ix]
			for t in nested:
				if t.ix in next_loc.sub_contains:
					if t in next_loc.sub_contains[t.ix]:
						next_loc.sub_contains[t.ix].remove(t)
						if next_loc.sub_contains[t.ix]==[]:
							del next_loc.sub_contains[t.ix]
			next_loc = next_loc.location
		rval = False
		if item.ix in self.contains:
			if item in self.contains[item.ix]:
				self.contains[item.ix].remove(item)
				if self.contains[item.ix]==[]:
					del self.contains[item.ix]
				rval = True
				item.location = False
				self.containsListUpdate()
		if item.ix in self.sub_contains:
			if item in self.sub_contains[item.ix]:
				self.sub_contains[item.ix].remove(item)
				if self.sub_contains[item.ix]==[]:
					del self.sub_contains[item.ix]
				rval = True
				item.location = False
				self.containsListUpdate()
		return rval
			
	def describeThing(self, description):
		self.base_desc = description
		self.desc = self.base_desc + self.state_desc
		if self.is_composite:
			if self.children_desc:
				self.desc = self.desc + self.children_desc
			else:
				for item in self.children:
					self.desc = self.desc + item.desc
		self.containsListUpdate()
	
	def xdescribeThing(self, description):
		self.base_xdesc = description
		self.xdesc = self.base_xdesc
		if self.is_composite:
			if self.children_desc:
				self.xdesc = self.xdesc + self.children_desc
			else:
				for item in self.children:
					self.xdesc = self.xdesc + item.desc
		self.containsListUpdate()
	
	def updateDesc(self):
		self.containsListUpdate()
			
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

# hacky solution for reflexive pronouns (himself/herself/itself)
reflexive = Abstract("itself")
reflexive.addSynonym("himself")
reflexive.addSynonym("herself")
reflexive.addSynonym("themself")
reflexive.addSynonym("themselves")

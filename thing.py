from . import vocab
import copy

##############################################################
# THING.PY - the Thing class for IntFicPy 
# Defines the Thing class,  its subclasses Surface, Container, and Clothing, and the thing dictionary
##############################################################
# TODO: create a describe method in Thing/Container/Surface to eliminate the need for creators to modify both desc/xdesc AND base_desc/base_xdesc in for Surfaces and Containers

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
		# thing properties
		self.size = 50
		self.contains_preposition = False
		self.contains_preposition_inverse = False
		self.canSit = False
		self.canStand = False
		self.canLie = False
		self.isPlural = False
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
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
		# the default description for the examine command
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]
	
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
		self.synonyms.remove(word)
		if word in vocab.nounDict:
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
			self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
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
		if self.verbose_name[-1]=="s" or self.verbose_name[-1]=="x" or self.verbose_name[-1]=="z" or self.verbose_name[-2:]=="sh" or self.verbose_name[-2:]=="ch":
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
		out = copy.copy(self)
		vocab.nounDict[out.name].append(out)
		out.setAdjectives(out.adjectives)
		for synonym in out.synonyms:
			vocab.nounDict[synonym].append(out)
		return out
	
	def describeThing(self, description):
		self.base_desc = description

class Surface(Thing):
	"""Class for Things that can have other Things placed on them """
	def __init__(self, name):
		"""Sets the essential properties for a new Surface object """
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
		self.size = 50
		self.name = name
		# verbose_name will be updated by Thing method setAdjectives 
		self.verbose_name = name
		self.give = False
		# default description printed by room
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.base_xdesc = self.base_desc
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
		# description of items on the Surface
		# will be appended to descriptions
		self.contains_desc = ""
		# Surfaces are not contains items by default, but can be safely made so
		self.invItem = False
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
					break
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
		# if contains is empty, there should be no onlist
		# TODO: consider rewriting this logic to avoid contructing an empty onlist, then deleting it
		if len(list_version)==0:
			onlist = ""
		if player_here:
			if inlist != "":
				onlist = onlist + "<br>"
			onlist = onlist + "You are on " + self.getArticle(True) + self.verbose_name + "."
		# append onlist to description
		self.desc = self.base_desc + onlist
		self.xdesc = self.base_xdesc + onlist
		self.contains_desc = onlist
	
	def addOn(self, item):
		"""Add a Thing to a Surface
		Takes argument item, pointing to a Thing"""
		item.location = self
		# nested items
		nested = getNested(item)
		for t in nested:
			if t.ix in self.sub_contains:
				self.sub_contains[t.ix].append(t)
			else:
				self.sub_contains[t.ix] = [t]
			if item.ix in self.location.sub_contains:
				self.location.sub_contains[t.ix].append(t)
			else:
				self.location.sub_contains[t.ix] = [t]
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
		if item.ix in self.contains:
			if item in self.contains[item.ix]:
				self.contains[item.ix].remove(item)
				self.location.sub_contains[item.ix].remove(item)
				if self.contains[item.ix] == []:
					del self.contains[item.ix]
				if self.location.sub_contains[item.ix] == []:
					del self.location.sub_contains[item.ix]
			item.location = False
			self.containsListUpdate()

	def describeThing(self, description):
		self.base_desc = description
		self.containsListUpdate()
	
	def xdescribeThing(self, description):
		self.base_xdesc = description
		self.containsListUpdate()
	
# NOTE: Container duplicates a lot of code from Surface. Consider a parent class for Things with a contains property
class Container(Thing):
	"""Things that can contain other Things """
	def __init__(self, name):
		"""Set basic properties for the Container instance
		Takes argument name, a single noun (string)"""
		self.size = 50
		self.contains_preposition = "in"
		self.contains_preposition_inverse = "out"
		self.canSit = False
		self.canStand = False
		self.canLie = False
		self.isPlural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = True
		self.contains = {}
		self.sub_contains = {}
		self.name = name
		self.verbose_name = name
		self.give = False
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
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
		inlist = " In the " + self.name + " is "
		# iterate through contents, appending the verbose_name of each to onlist
		list_version = list(self.contains.keys())
		player_here = False
		for key in list_version:
			for item in self.contains[key]:
				if isinstance(item, Player):
					list_version.remove(key)
					player_here = True
					break
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
		# remove the empty inlist in the case of no contents
		# TODO: consider rewriting this logic to avoid contructing an empty inlist, then deleting it
		if len(list_version)==0:
			inlist = ""
		if player_here:
			if inlist != "":
				inlist = inlist + "<br>"
			inlist = inlist + "You are in " + self.getArticle(True) + self.verbose_name + "."
		# update descriptions
		self.desc = self.base_desc + inlist
		self.xdesc = self.base_xdesc + inlist
		self.contains_desc = inlist
	
	def addIn(self, item):
		"""Add an item to contents, update descriptions
		Takes argument item, pointing to a Thing """
		item.location = self
		# nested items
		nested = getNested(item)
		for t in nested:
			if t.ix in self.sub_contains:
				self.sub_contains[t.ix].append(t)
			else:
				self.sub_contains[t.ix] = [t]
			if item.ix in self.location.sub_contains:
				self.location.sub_contains[t.ix].append(t)
			else:
				self.location.sub_contains[t.ix] = [t]
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
		"""Remove an item from contents, update decription """
		if item.ix in self.contains:
			if item in self.contains[item.ix]:
				self.contains[item.ix].remove(item)
				self.location.sub_contains[item.ix].remove(item)
				if self.contains[item.ix] == []:
					del self.contains[item.ix]
				if self.location.sub_contains[item.ix] == []:
					del self.location.sub_contains[item.ix]
				item.location = False
			self.containsListUpdate()
			
	def describeThing(self, description):
		self.base_desc = description
		self.containsListUpdate()
	
	def xdescribeThing(self, description):
		self.base_xdesc = description
		self.containsListUpdate()

# NOTE: May not be necessary as a distinct class. Consider just using the wearable property.
class Clothing(Thing):
	"""Class for Things that can be worn """
	# all clothing is wearable
	wearable = True
	# uses __init__ from Thing
	
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

class Abstract:
	"""Class for abstract game items with no location, such as ideas"""
	def __init__(self, name):
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
		# properties
		self.isPlural = False
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
		#self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
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

from . import vocab

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

# Thing is the overarching class for all items that exist in the game
class Thing:
	# sets essential properties for the Thing instance
	def __init__(self, name):
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
		# thing properties
		self.isPlural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = True
		self.adjectives = []
		self.cannotTakeMsg = "You cannot take that."
		self.contains = []
		self.wearable = False
		self.location = False
		self.name = name
		# verbose name will be updated when adjectives are added
		self.verbose_name = name
		# Thing instances that are not Actors cannot be spoken to
		self.ask = False
		self.tell = False
		# the default description to print from the room
		self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
		# the default description for the examine command
		self.xdesc = self.desc
		# add name to list of nouns
		if name in vocab.nounDict:
			vocab.nounDict[name].append(self)
		else:
			vocab.nounDict[name] = [self]
	
	# adds a synonym (noun) that can be used to refer to a Thing
	# takes argument word, a string, which should be a single noun
	def addSynonym(self, word):
		if word in vocab.nounDict:
			vocab.nounDict[word].append(self)
		else:
			vocab.nounDict[word] = [self]
	
	# sets adjectives for a Thing
	# takes arguments adj_list, a list of one word strings (adjectives), and update_desc, a Boolean defaulting to True
	# game creators should set update_desc to False if using a custom desc or xdesc for a Thing
	def setAdjectives(self, adj_list, update_desc=True):
		self.adjectives = adj_list
		self.verbose_name = " ".join(adj_list) + " " + self.name
		if update_desc:
			self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
			self.xdesc = self.desc
	
	# gets the correct article for a Thing
	# takes argument definite (defaults to False), which specifies whether the article is definite		
	def getArticle(self, definite=False):
		if not self.hasArticle:
			return ""
		elif definite or self.isDefinite:
			return "the "
		else:
			if self.verbose_name[0] in ["a", "e", "i", "o", "u"]:
				return "an "
			else:
				return "a "
	
	# make a Thing unique (use definite article)
	# creators should use a Thing's makeUnique method rather than setting its definite property directly
	def makeUnique(self):
		self.isDefinite = True
		self.desc = self.getArticle().capitalize() + self.verbose_name + " is here."


# class for Things that can have other things placed on them
class Surface(Thing):
	# sets the essential properties for a new Surface object
	def __init__(self, name):
		self.isPlural = False
		self.hasArticle = True
		self.isDefinite = False
		# the items on the Surface
		self.contains = []
		# items contained by items on the Surface
		# accessible by default, but not shown in outermost description
		self.sub_contains = []
		self.name = name
		# verbose_name will be updated by Thing method setAdjectives 
		self.verbose_name = name
		# cannot talk to a Surface
		self.ask = False
		self.tell = False
		# default description printed by room
		self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
		# default examine description
		self.xdesc = self.desc
		# description of items on the Surface
		# will be appended to descriptions
		self.contains_desc = ""
		# desc and xdesc without contains_desc
		# used in constructing descriptions
		# creators wanting custom descriptions for Surfaces should modify these
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.base_xdesc = self.base_desc
		# Surfaces are not inventory items by default, but can be safely made so
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
	
	# update description of contents
	# called when a Thing is added or removed
	def containsListUpdate(self):
		onlist = " On the " + self.name + " is "
		# iterate through contents, appending the verbose_name of each to onlist
		for thing in self.contains:
			onlist = onlist + thing.getArticle() + thing.verbose_name
			if thing is self.contains[-1]:
				onlist = onlist + "."
			elif thing is self.contains[-2]:
				onlist = onlist + " and "
			else:
				onlist = onlist + ", "
		# if contains is empty, there should be no onlist
		# TODO: consider rewriting this logic to avoid contructing an empty onlist, then deleting it
		if len(self.contains)==0:
			onlist = ""
		# append onlist to description
		self.desc = self.base_desc + onlist
		self.xdesc = self.base_xdesc + onlist
		self.contains_desc = onlist
	
	# add a Thing to a Surface
	# takes argument item, pointing to a Thing
	def addOn(self, item):
		item.location = self
		self.location.sub_contains.append(item)
		self.contains.append(item)
		self.containsListUpdate()

	# removes a Thing from a Surface
	def removeThing(self, item):
		if item in self.contains:
			self.contains.remove(item)
			self.location.sub_contains.remove(item)
			item.location = False
			self.containsListUpdate()

# class for Things that can contain other Things
class Container(Thing):
	# set basic properties for the Container instance
	# takes argument name, a single noun (string)
	def __init__(self, name):
		self.isPlural = False
		self.hasArticle = True
		self.isDefinite = False
		self.invItem = True
		self.contains = []
		self.sub_contains = []
		self.name = name
		self.verbose_name = name
		# you cannot talk to a Container
		self.ask = False
		self.tell = False
		self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.xdesc = self.desc
		# description of contents
		self.contains_desc = ""
		# descriptions without contains_desc
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.base_xdesc = self.base_desc
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
	
	# update description for addition/removal of items from the Container instance
	def containsListUpdate(self):
		inlist = " In the " + self.name + " is "
		# iterate through contents and append each verbose_name to description
		for thing in self.contains:
			inlist = inlist + thing.getArticle() + thing.verbose_name
			if thing is self.contains[-1]:
				inlist = inlist + "."
			elif thing is self.contains[-2]:
				inlist = inlist + " and "
			else:
				inlist = inlist + ", "
		# remove the empty inlist in the case of no contents
		# TODO: consider rewriting this logic to avoid contructing an empty inlist, then deleting it
		if len(self.contains)==0:
			inlist = ""
		# update descriptions
		self.desc = self.base_desc + inlist
		self.xdesc = self.base_xdesc + inlist
		self.contains_desc = inlist
	
	# adds an item to contents, updates descriptions
	# takes argument item, pointing to a Thing
	def addIn(self, item):
		item.location = self
		self.location.sub_contains.append(item)
		self.contains.append(item)
		self.containsListUpdate()

	# removes an item from contents, updates decription
	def removeThing(self, item):
		if item in self.contains:
			self.contains.remove(item)
			if not self.location==False:
				self.location.sub_contains.remove(item)
			item.location = False
			self.containsListUpdate()

# class for Things that can be worn
class Clothing(Thing):
	# all clothing is wearable
	wearable = True
	# uses __init__ from Thing

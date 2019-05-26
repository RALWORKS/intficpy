from .thing import Thing
from . import vocab

##############################################################
# ACTOR.PY - the Actor class for IntFicPy 
# Contains the Actor class, the Topic class the actors dictionary
##############################################################

# TODO: save ask_topics and tell_topics
# TODO: accomodate spaces in the proper_name argument of makeProper
# TODO: implement give/show topics

# a dictionary of the indeces of all Actor objects, mapped to their object
# populated at runtime
actors = {}
# index is an integer appended to the string "actor"- increases by 1 for each Actor defined
# index of an actor will always be the same provided the game file is written according to the rules
actor_ix = 0


class Actor(Thing):
	"""Actor class, used for characters in the creator's game """
	
	def __init__(self, name):
		"""Intitializes the Actor instance and sets essential properties """
		self.invItem = False # cannot be added to the contains
		self.parent_obj = False
		self.size = 50
		self.synonyms = []
		self.isPlural = False
		self.hasArticle = True
		self.isDefinite = False
		self.position = "standing"
		self.contains = {}
		self.sub_contains = {}
		self.name = name
		self.is_composite = False
		# verbose_name is modified when adjectives are applied using the setAdjectives method of the Thing class
		self.verbose_name = name
		# the default description of the Actor in a room
		self.base_desc = self.getArticle().capitalize() + name + " is here. "
		if self.position != "standing":
			self.desc = self.base_desc + " " +  self.getArticle().capitalize() + self.name + " is " + self.position + " down."
		else:
			self.desc = self.base_desc
		self.base_xdesc = self.base_desc
		if self.position != "standing":
			self.xdesc = self.base_xdesc + " " + self.getArticle().capitalize() + self.name + " is " + self.position + " down."
		else:
			self.desc = self.base_desc
		self.cannotTakeMsg = "You cannot take a person."
		# add name to the noun lookup dictionary
		if name not in vocab.nounDict:
			vocab.nounDict[name] = [self]
		elif self not in vocab.nounDict[name]:
			vocab.nounDict[name].append(self)
		# topics for conversation
		self.ask_topics = {}
		self.tell_topics = {}
		self.give_topics = {}
		self.show_topics = {}
		# prints when player's question/statement does not match a topis
		self.default_topic = "No response."
		# specifies the article to use in output
		self.hasArticle = True
		self.isDefinite = False
		# indexing for save
		global actor_ix
		self.ix = "actor" + str(actor_ix)
		actor_ix = actor_ix + 1
		actors[self.ix] = self
	
	def makeProper(self, proper_name):
		"""Makes the name of an Actor into proper name
		Takes a string argument proper_name
		Called by the game creator """
	# NOTE: currently enters vocab words incorrectly if proper_name contains multiple words
		self.name = proper_name
		self.desc = proper_name + " is here."
		self.hasArticle = False
		# convert to lowercase for addition to nounDict
		proper_name = proper_name.lower()
		# add name to nounDict
		if proper_name not in vocab.nounDict:
			vocab.nounDict[proper_name] = [self]
		elif self not in vocab.nounDict[proper_name]:
			vocab.nounDict[proper_name].append(self)
	
	def describeThing(self, description):
		self.base_desc = description
		self.desc = self.base_desc + " " +  self.getArticle().capitalize() + self.name + " is " + self.position + " down."
	
	def xdescribeThing(self, description):
		self.base_xdesc = description
		self.xdesc = self.base_xdesc + " " +  self.getArticle().capitalize() + self.name + " is " + self.position + " down."
	
	def addThing(self, item):
		"""Add an item to contents, update descriptions
		Takes argument item, pointing to a Thing """
		from . import thing
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
	
	def makeStanding(self):
		self.position = "standing"
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
	
	def makeSitting(self):
		self.position = "sitting"
		self.desc = self.base_desc + " " +  self.getArticle().capitalize() + self.name + " is sitting down."
		self.xdesc = self.base_xdesc + " " +  self.getArticle().capitalize() + self.name + " is sitting down."
	
	def makeLying(self):
		self.position = "lying"
		self.desc = self.base_desc + " " +  self.getArticle().capitalize() + self.name + " is lying down."
		self.xdesc = self.base_xdesc + " " +  self.getArticle().capitalize() + self.name + " is lying down."

	def removeThing(self, item):
		"""Remove an item from contents, update decription """
		from . import thing
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
		# nested items
		nested = getNested(item)
		for t in nested:
			if t.ix in self.sub_contains:
				if t in self.sub_contains[t.ix]:
					self.sub_contains[t.ix].remove(t)
					if self.sub_contains[t.ix]==[]:
						del self.sub_contains[t.ix]
		# top level item
		rval = False
		if item.ix in self.contains:
			if item in self.contains[item.ix]:
				self.contains[item.ix].remove(item)
				if self.contains[item.ix]==[]:
					del self.contains[item.ix]
				rval = True
				item.location = False
		if item.ix in self.sub_contains:
			if item in self.sub_contains[item.ix]:
				self.sub_contains[item.ix].remove(item)
				if self.sub_contains[item.ix]==[]:
					del self.sub_contains[item.ix]
				rval = True
				item.location = False
		return rval
	
	def addTopic(self, ask_tell_give_show, topic, thing):
		"""Adds a conversation topic to the Actor
		Takes argument ask_tell, a string """
		if "ask" in ask_tell_give_show or ask_tell_give_show=="all":
			self.ask_topics[thing] = topic
		if "tell" in ask_tell_give_show or ask_tell_give_show=="all":
			self.tell_topics[thing] = topic
		if "give" in ask_tell_give_show or ask_tell_give_show=="all":
			self.give_topics[thing] = topic
		if "show" in ask_tell_give_show or ask_tell_give_show=="all":
			self.show_topics[thing] = topic
	
	def defaultTopic(self, app):
		"""The default function for an Actor's default topic
		Should be overwritten by the game creator for an instance to create special responses
		Takes argument app, pointing to the PyQt5 GUI"""
		app.printToGUI(self.default_topic)
	
	def getOutermostLocation(self):
		"""Gets the Actor's current room 
		Takes argument app, pointing to the PyQt5 GUI"""
		from .room import Room 
		x = self.location
		while not isinstance(x, Room):
			x = x.location
		return x

class Player(Actor):
	"""Class for Player objects """
	def __init__(self, name):
		"""Set basic properties for the Player instance
		Takes argument loc, a Room"""
		#self.location = loc
		self.name = name
		self.verbose_name = name
		self.is_composite = False
		self.invItem = False
		self.cannotTakeMsg = "You cannot take yourself."
		self.parent_obj = False
		self.size = 50
		self.synonyms = []
		self.position = "standing"
		self.contains = {}
		self.sub_contains = {}
		self.wearing = {}
		self.inv_max = 100
		self.desc = ""
		self.base_desc = ""
		self.xdesc="You notice nothing remarkable about yourself. "
		self.base_xdesc = "You notice nothing remarkable about yourself. "
		self.ask_topics = {}
		self.tell_topics = {}
		self.give_topics = {}
		self.show_topics = {}
		self.default_topic = "No one responds. This should come as a relief."
		self.knows_about = []
		self.isPlural = False
		self.hasArticle = True
		self.isDefinite = False
		global actor_ix
		self.ix = "actor" + str(actor_ix)
		actor_ix = actor_ix + 1
		actors[self.ix] = self
		#self.gameOpening = False
		
	def setPlayer(self):
		self.addSynonym("me")
		self.addSynonym("myself")
		
	def makeStanding(self):
		self.position = "standing"
		self.desc = self.base_desc
		self.xdesc = self.base_xdesc
	
	def makeSitting(self):
		self.position = "sitting"
		if isinstance(self.location, Thing):
			self.desc = self.base_desc + " You are sitting on " + self.location.getArticle() + self.location.verbose_name + "."
			self.xdesc = self.base_xdesc + " You are sitting on " + self.location.getArticle() + self.location.verbose_name + "."
		else:
			self.desc = self.base_desc + " You are sitting down."
			self.xdesc = self.base_xdesc + " You are sitting down."
	
	def makeLying(self):
		self.position = "lying"
		if isinstance(self.location, Thing):
			self.desc = self.base_desc + " You are lying " + self.location.contains_preposition + " " + self.location.getArticle() + self.location.verbose_name + "."
			self.xdesc = self.base_xdesc + " You are lying " + self.location.contains_preposition + " " + self.location.getArticle() + self.location.verbose_name + "."
		else:
			self.desc = self.base_desc + " You are lying down."
			self.xdesc = self.base_xdesc + " You are lying down."

class Topic:
	"""class for conversation topics"""
	text = ""
	
	def __init__(self, topic_text):
		self.text = topic_text
	
	def func(self, app):
		app.printToGUI(self.text)

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


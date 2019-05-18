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
		self.invItem = False # cannot be added to the inventory
		self.size = 50
		self.synonyms = []
		self.isPlural = False
		self.hasArticle = True
		self.isDefinite = False
		self.position = "standing"
		self.contains = {}
		self.sub_contains = {}
		self.name = name
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
		#self.containsListUpdate()
	
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
		if item.ix in self.contains:
			if item in self.contains[item.ix]:
				self.contains[item.ix].remove(item)
				self.location.sub_contains[item.ix].remove(item)
				if self.contains[item.ix] == []:
					del self.contains[item.ix]
				if self.location.sub_contains[item.ix] == []:
					del self.location.sub_contains[item.ix]
				item.location = False
			#self.containsListUpdate()
	
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


class Player(Actor):
	"""Class for Player objects """
	def __init__(self, name):
		"""Set basic properties for the Player instance
		Takes argument loc, a Room"""
		#self.location = loc
		self.name = name
		self.verbose_name = name
		self.invItem = False
		self.cannotTakeMsg = "You cannot take yourself."
		self.size = 50
		self.synonyms = []
		self.position = "standing"
		self.inventory = {}
		self.sub_inventory = {}
		self.wearing = {}
		self.inv_max = 100
		self.desc = ""
		self.xdesc="You notice nothing remarkable about yourself. "
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

class Topic:
	"""class for conversation topics"""
	text = ""
	
	def __init__(self, topic_text):
		self.text = topic_text
	
	def func(self, app):
		app.printToGUI(self.text)
		

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
	invItem = False # cannot be added to the inventory
	
	def __init__(self, name):
		"""Intitializes the Actor instance and sets essential properties """
		self.size = 50
		self.synonyms = []
		self.isPlural = False
		self.hasArticle = True
		self.isDefinite = False
		self.contains = {}
		self.sub_contains = {}
		self.name = name
		# verbose_name is modified when adjectives are applied using the setAdjectives method of the Thing class
		self.verbose_name = name
		# the default description of the Actor in a room
		self.desc = self.getArticle().capitalize() + name + " is here."
		self.cannotTakeMsg = "You cannot take a person."
		# add name to the noun lookup dictionary
		if name not in vocab.nounDict:
			vocab.nounDict[name] = [self]
		elif self not in vocab.nounDict[name]:
			vocab.nounDict[name].append(self)
		# topics for conversation
		self.ask_topics = {}
		self.tell_topics = {}
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
		self.desc = description
	
	def xdescribeThing(self, description):
		self.xdesc = description
	
	def addTopic(self, ask_tell, topic, thing):
		"""Adds a conversation topic to the Actor
		Takes argument ask_tell, a string """
		correct = False
		if ask_tell == "ask" or ask_tell == "both":
			self.ask_topics[thing] = topic
			correct = True
		if ask_tell == "tell" or ask_tell == "both":
			self.tell_topics[thing] = topic
			correct = True
		if not correct:
			print("Incorrect argument ask_tell: " + ask_tell)
	
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
		self.size = 50
		self.synonyms = []
		self.inventory = {}
		self.sub_inventory = {}
		self.wearing = {}
		self.inv_max = 100
		self.desc = ""
		self.xdesc="You notice nothing remarkable about yourself. "
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
		

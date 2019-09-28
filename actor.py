from .thing import Thing
from . import vocab

##############################################################
# ACTOR.PY - the Actor class for IntFicPy 
# Contains the Actor class, the Topic class the actors dictionary
##############################################################

# a dictionary of the indeces of all Actor objects, mapped to their object
# populated at runtime
actors = {}
# index is an integer appended to the string "actor"- increases by 1 for each Actor defined
# index of an actor will always be the same provided the game file is written according to the rules
actor_ix = 0

topics = {}
topic_ix = 0

class Actor(Thing):
	"""Actor class, used for characters in the creator's game """
	def __init__(self, name):
		"""Intitializes the Actor instance and sets essential properties """
		self.ignore_if_ambiguous = False
		self.cannot_interact_msg = None
		self.invItem = False # cannot be added to the contains
		self.connection = None # this should almost always be None, but setting it probably won't break anything 
		self.contains_preposition = None
		self.parent_obj = False
		self.size = 50
		self.far_away = False
		self.adjectives = []
		self.synonyms = []
		self.special_plural = False
		self.isPlural = False
		self.location = None
		self.hasArticle = True
		self.isDefinite = False
		self.position = "standing"
		self.contains = {}
		self.sub_contains = {}
		self.name = name
		self.is_composite = False
		self.commodity = False
		self.can_lead = False
		# verbose_name is modified when adjectives are applied using the setAdjectives method of the Thing class
		self.verbose_name = name
		# the default description of the Actor in a room
		self.base_desc = self.getArticle().capitalize() + name + " is here. "
		if self.position != "standing":
			self.desc = self.base_desc + " " +  (self.getArticle(True) + self.name).capitalize() + " is " + self.position + " down."
		else:
			self.desc = self.base_desc
		self.base_xdesc = self.base_desc
		if self.position != "standing":
			self.xdesc = self.base_xdesc + " " + (self.getArticle(True) + self.name).capitalize()  + " is " + self.position + " down."
		else:
			self.desc = self.base_desc
		self.cannotTakeMsg = "You cannot take a person."
		# add name to the noun lookup dictionary
		if name not in vocab.nounDict:
			vocab.nounDict[name] = [self]
		elif self not in vocab.nounDict[name]:
			vocab.nounDict[name].append(self)
		# topics for conversation
		self.for_sale = {}
		self.will_buy = {}
		self.ask_topics = {}
		self.tell_topics = {}
		self.give_topics = {}
		self.show_topics = {}
		self.special_topics = {}
		self.special_topics_alternate_keys = {}
		self.sticky_topic = None
		self.hi_topic = None
		self.return_hi_topic = None
		self.said_hi = False
		self.hermit_topic = None
		self.manual_suggest = False
		# prints when player's question/statement does not match a topic
		self.default_topic = "No response."
		# specifies the article to use in output
		self.hasArticle = True
		self.isDefinite = False
		# indexing for save
		global actor_ix
		self.ix = "actor" + str(actor_ix)
		actor_ix = actor_ix + 1
		actors[self.ix] = self
		self.known_ix = self.ix
	
	def makeProper(self, proper_name):
		"""Makes the name of an Actor into proper name
		Takes a string argument proper_name
		Called by the game creator """
	# NOTE: currently enters vocab words incorrectly if proper_name contains multiple words
		from.parser import cleanInput, tokenize, removeArticles
		token_name = proper_name
		token_name = cleanInput(token_name, False)
		token_name = tokenize(token_name)
		token_name = removeArticles(token_name)
		self.name = token_name[-1]
		self.setAdjectives(self.adjectives + token_name)
		for tok in token_name:
			self.addSynonym(tok)
		self.verbose_name = proper_name
		#self.desc = proper_name + " is here."
		self.hasArticle = False
	
	def describeThing(self, description):
		self.base_desc = description
		self.desc = self.base_desc
		if self.position != "standing":
			self.desc = self.base_desc + " " + (self.getArticle(True) + self.name).capitalize()  + " is " + self.position + " down."
	
	def xdescribeThing(self, description):
		self.base_xdesc = description
		self.xdesc = self.base_xdesc
		if self.position != "standing":
			self.xdesc = self.base_xdesc + " " + (self.getArticle(True) + self.name).capitalize()  + " is " + self.position + " down."
	
	def addThing(self, item):
		"""Add an item to contents, update descriptions
		Takes argument item, pointing to a Thing """
		from . import thing
		if isinstance(item, thing.Container):
			if item.lock_obj:
				if item.lock_obj.ix in self.contains:
					if not item.lock_obj in self.contains[item.lock_obj.ix]:
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
	
	def setHiTopics(self, hi_topic, return_hi_topic):
		self.said_hi = False
		if hi_topic:
			hi_topic.owner = self
		if return_hi_topic:
			return_hi_topic.owner = self
		self.hi_topic = hi_topic
		self.return_hi_topic = return_hi_topic
		
	def setHermitTopic(self, hermit_topic):
		self.hermit_topic = hermit_topic
		if hermit_topic:
			hermit_topic.owner = self
	
	def removeHermitTopic(self):
		self.hermit_topic = None
	
	def addTopic(self, ask_tell_give_show, topic, thing):
		"""Adds a conversation topic to the Actor
		Takes argument ask_tell, a string """
		topic.owner = self
		if "ask" in ask_tell_give_show or ask_tell_give_show=="all":
			self.ask_topics[thing.ix] = topic
		if "tell" in ask_tell_give_show or ask_tell_give_show=="all":
			self.tell_topics[thing.ix] = topic
		if "give" in ask_tell_give_show or ask_tell_give_show=="all":
			self.give_topics[thing.ix] = topic
		if "show" in ask_tell_give_show or ask_tell_give_show=="all":
			self.show_topics[thing.ix] = topic
	
	def addSpecialTopic(self, topic):
		topic.owner = self
		self.special_topics[topic.suggestion] = topic
		for x in topic.alternate_phrasings:
			self.special_topics_alternate_keys[x] = topic
	
	def removeSpecialTopic(self, topic):
		if topic.suggestion in self.special_topics:
			del self.special_topics[topic.suggestion]
		for x in topic.alternate_phrasings:
			if x in self.special_topics_alternate_keys:
				del self.special_topics_alternate_keys[x]
	
	def removeAllSpecialTopics(self):
		topics = []
		for suggestion in self.special_topics:
			topics.append(self.special_topics[suggestion])
		for topic in topics:
			self.removeSpecialTopic(topic)
	
	def removeAllTopics(self):
		self.ask_topics = {}
		self.tell_topics = {}
		self.give_topics = {}
		self.show_topics = {}
	
	def printSuggestions(self, app):
		from .parser import lastTurn
		if self.special_topics != {}:
			lastTurn.convNode = True
			for suggestion in self.special_topics:
				app.printToGUI("(You could " + suggestion + ")")
				lastTurn.specialTopics[suggestion] = self.special_topics[suggestion]
			for phrasing in self.special_topics_alternate_keys:
				lastTurn.specialTopics[phrasing] = self.special_topics_alternate_keys[phrasing]
	
	def defaultTopic(self, app):
		"""The default function for an Actor's default topic
		Should be overwritten by the game creator for an instance to create special responses
		Takes argument app, pointing to the PyQt5 GUI"""
		app.printToGUI(self.default_topic)
		self.printSuggestions(app)
	
	def addSelling(self, item, currency, price, stock):
		"""item is the Thing for sale (by the unit), currency is the Thing to offer in exchange 
		(use currency.copyThing() for duplicates), price is the number of the currency Things required,
		and stock is the number of a given Thing the Actor has to sell (set to True for infinite) """
		if item.ix not in self.for_sale:
			self.for_sale[item.ix] = SaleItem(item, currency, price, stock)
	
	def addWillBuy(self, item, currency, price, max_wanted):
		"""item is the Thing the Actor wishes to purchase (by the unit), currency is the Thing the Actor will offer in exchange 
		(use currency.copyThing() for duplicates), price is the number of the currency Things the Actor will give,
		and max_wanted is the number of a given Thing the Actor is willing to buy (set to True for infinite) """
		if item.ix not in self.will_buy:
			self.will_buy[item.ix] = SaleItem(item, currency, price, max_wanted)
	
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
		self.cannot_interact_msg = None
		self.ignore_if_ambiguous = False
		self.connection = None # this should almost always be None, but setting it probably won't break anything 
		self.contains_preposition = None
		self.name = name
		self.verbose_name = "yourself"
		self.is_composite = False
		self.invItem = False
		self.far_away = False
		self.cannotTakeMsg = "You cannot take yourself."
		self.parent_obj = False
		self.special_plural = False
		self.size = 50
		self.adjectives = []
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
		self.sticky_topic = None
		self.hi_topic = None
		self.return_hi_topic = None
		self.said_hi = False
		self.hermit_topic = None
		self.manual_suggest = False
		self.for_sale = {}
		self.will_buy = {}
		self.ask_topics = {}
		self.tell_topics = {}
		self.give_topics = {}
		self.show_topics = {}
		self.special_topics = {}
		self.special_topics_alternate_keys = {}
		self.default_topic = "No one responds. This should come as a relief."
		self.isPlural = False
		self.hasArticle = False
		self.isDefinite = False
		self.commodity = False
		self.can_lead = False
		global actor_ix
		self.ix = "actor" + str(actor_ix)
		actor_ix = actor_ix + 1
		actors[self.ix] = self
		self.known_ix = self.ix
		self.knows_about = [self.ix]
		
	def setPlayer(self):
		self.addSynonym("me")
		self.addSynonym("myself")
		self.addSynonym("yourself")
		self.addSynonym("you")
		
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
	def __init__(self, topic_text):
		self.text = topic_text
		global topic_ix
		self.ix = "topic" + str(topic_ix)
		topic_ix = topic_ix + 1
		topics[self.ix] = self
		self.owner = None
	
	def func(self, app, suggest=True):
		app.printToGUI(self.text)
		if self.owner and suggest:
			if not self.owner.manual_suggest:
				self.owner.printSuggestions(app)

class SpecialTopic:
	"""class for conversation topics"""
	def __init__(self, suggestion, topic_text):
		self.text = topic_text
		self.suggestion = suggestion
		self.alternate_phrasings = []
		global topic_ix
		self.ix = "topic" + str(topic_ix)
		topic_ix = topic_ix + 1
		topics[self.ix] = self
		self.owner = None
	
	def func(self, app, suggest=True):
		app.printToGUI(self.text)
		if suggest and self.owner:
			if not self.owner.manual_suggest:
				self.owner.printSuggestions(app)
	
	def addAlternatePhrasing(self, phrasing):
		self.alternate_phrasings.append(phrasing)

class SaleItem:
	def __init__(self, item, currency, price, number):
		self.ix = item.ix
		self.thing = item
		self.currency = currency
		self.price = price
		self.number = number
		self.wants = number
		self.out_stock_msg = "That item is out of stock. "
		self.wants_no_more_msg = None
		self.purchase_msg = "You purchase " + item.lowNameArticle(False) + ". "
		self.sell_msg = "You sell " + item.lowNameArticle(True) + ". "
		global topic_ix
		self.ix = "topic" + str(topic_ix)
		topic_ix = topic_ix + 1
		topics[self.ix] = self
	
	def buyUnit(self, me, app):
		for i in range(0, self.price):
			if self.currency.ix in me.contains:
				me.removeThing(me.contains[self.currency.ix][0])
			elif self.currency.ix in me.sub_contains:
				me.removeThing(me.sub_contains[self.currency.ix][0])
		if self.price > 1:
			app.printToGUI("(Lost: " + str(self.price) + " " + self.currency.getPlural() + ")")
		else:
			app.printToGUI("(Lost: " + str(self.price) + " " + self.currency.verbose_name + ")")
		if self.number is True:
			obj = self.thing.copyThing()
		elif self.number > 1:
			obj = self.thing.copyThing()
		else:
			obj = self.thing
			if obj.location:
				obj.location.removeThing(obj)
		me.addThing(obj)
		if not self.number is True:
			self.number = self.number -1
		app.printToGUI("(Received: " + obj.verbose_name + ") ")
	
	def afterBuy(self, me, app):
		pass
	def beforeBuy(self, me, app):
		pass
	def soldOut(self, me, app):
		pass
		
	def sellUnit(self, me, app):
		me.removeThing(self.thing)
		app.printToGUI("(Lost: " + self.thing.verbose_name + ")")
		for i in range(0, self.price):
			me.addThing(self.currency)
		if not self.number is True:
			self.number = self.number -1
		if self.price > 1:
			app.printToGUI("(Received: " + str(self.price) + " " + self.currency.getPlural() + ") ")
		else:
			app.printToGUI("(Received: " + str(self.price) + " " + self.currency.verbose_name + ") ")

	def afterSell(self, me, app):
		pass
	def beforeSell(self, me, app):
		pass
	def boughtAll(self, me, app):
		pass


def getNested(target):
	"""Find revealed nested Things
	Takes argument target, pointing to a Thing
	Returns a list of Things
	Used by multiple verbs """
	from .thing import Container
	# list to populate with found Things
	nested = []
	# iterate through top level contents
	if isinstance(target, Container):
		if target.has_lid:
			if target.is_open==False:
				return []
	for key in target.contains:
		for item in target.contains[key]:
			nested.append(item)
	for key in target.sub_contains:
		for item in target.sub_contains[key]:
			nested.append(item)
	return nested

from .thing import Thing
from . import vocab
#from string import lower, capitalize

actors = {}
actor_ix = 0

class Actor(Thing):
	invItem = False
	isProperName = False
	ask_topics = {}
	tell_topics = {}
	default_topic = "No response."
	hasArticle = True
	isDefinite = False

	def __init__(self, name):
		self.name = name
		self.verbose_name = name
		self.desc = self.getArticle().capitalize() + name + " is here."
		self.cannotTakeMsg = "You cannot take a person."
		if name not in vocab.nounDict:
			vocab.nounDict[name] = [self]
		elif self not in vocab.nounDict[name]:
			vocab.nounDict[name].append(self)
		
		self.ask_topics = {}
		self.tell_topics = {}
		self.default_topic = "No response."
		
		# indexing for save
		global actor_ix
		self.ix = "actor" + str(actor_ix)
		actor_ix = actor_ix + 1
		actors[self.ix] = self

	def makeProper(self, name):
		self.name = name
		self.desc = name + " is here."
		self.hasArticle = False
		
		name = name.lower()
		
		if name not in vocab.nounDict:
			vocab.nounDict[name] = [self]
		elif self not in vocab.nounDict[name]:
			vocab.nounDict[name].append(self)
	
	def addTopic(self, ask_tell, topic, thing):
		if ask_tell == "a" or ask_tell == "b":
			self.ask_topics[thing] = topic
		if ask_tell == "t" or ask_tell == "b":
			self.tell_topics[thing] = topic
		else:
		 self.default_topic = topic
	
	def defaultTopic(self, app):
		app.printToGUI(self.default_topic)
	
class Topic:
	text = ""
	
	def __init__(self, t):
		self.text = t
	
	def func(self, app):
		app.printToGUI(self.text)
		

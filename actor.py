import settings
from thing import Thing
import vocab
from string import lower

class Actor(Thing):
	invItem = False
	isProperName = False
	ask_topics = {}
	tell_topics = {}
	default_topic = "No response."

	def __init__(self, name):
		self.name = name
		self.verbose_name = name
		self.desc = name + " is here."
		if name not in vocab.nounDict:
			vocab.nounDict[name] = [self]
		elif self not in vocab.nounDict[name]:
			vocab.nounDict[name].append(self)
		
		self.ask_topics = {}
		self.tell_topics = {}
		self.default_topic = "No response."

	def makeProper(self, name):
		self.name = name
		self.desc = name + " is here."
		prepsition = ""
		
		name = lower(name)
		
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
	
	def defaultTopic(self):
		print(self.default_topic)
	
class Topic:
	text = ""
	
	def __init__(self, t):
		self.text = t
	
	def func(self):
		print(self.text)
		

from . import vocab
#from string import capitalize

class Thing:
	def __init__(self, n):
		self.location = False
		self.name = n
		self.verbose_name = n
		self.ask = False
		self.tell = False
		self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.xdesc = self.desc
		# add name to list of nouns
		if n in vocab.nounDict:
			vocab.nounDict[n].append(self)
		else:
			vocab.nounDict[n] = [self]
	isPlural = False
	hasArticle = True
	isDefinite = False
	invItem = True
	adjectives = []
	cannotTakeMsg = "You cannot take that."
	containsOn = []
	containsIn = []
	wearable = False
	
	def addSynonym(self, word):
		if word in vocab.nounDict:
			vocab.nounDict[word].append(self)
		else:
			vocab.nounDict[word] = [self]
			
	def setAdjectives(self, adj_list, update_desc=True):
		self.adjectives = adj_list
		self.verbose_name = " ".join(adj_list) + " " + self.name
		if update_desc:
			self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
			
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
	
	def makeUnique(self):
		self.isDefinite = True
		self.desc = self.getArticle().capitalize() + self.verbose_name + " is here."

class Surface(Thing):
	invItem = False
	containsOn = []
	
	def __init__(self, n):
		self.name = n
		self.verbose_name = n
		self.ask = False
		self.tell = False
		self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.xdesc = self.desc
		# add name to list of nouns
		if n in vocab.nounDict:
			vocab.nounDict[n].append(self)
		else:
			vocab.nounDict[n] = [self]
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.base_xdesc = self.base_desc
	
	def onListUpdate(self):
		onlist = " On the " + self.name + " is "
		for thing in self.containsOn:
			onlist = onlist + thing.getArticle() + thing.verbose_name
			if thing is self.containsOn[-1]:
				onlist = onlist + "."
			elif thing is self.containsOn[-2]:
				onlist = onlist + " and "
			else:
				onlist = onlist + ", "
		if len(self.containsOn)==0:
			onlist = ""
		self.desc = self.base_desc + onlist
		self.xdesc = self.base_xdesc + onlist

	def addOn(self, item):
		item.location = self
		self.location.sub_contains.append(item)
		self.containsOn.append(item)
		self.onListUpdate()

	def removeThing(self, thing):
		if thing in self.containsOn:
			self.containsOn.remove(thing)
		else:
			self.containsIn.remove(thing)
		self.location.sub_contains.remove(thing)
		thing.location = False
		self.onListUpdate()
		
class Container(Thing):
	invItem = True
	containsIn = []
	
	def __init__(self, n):
		self.name = n
		self.verbose_name = n
		self.ask = False
		self.tell = False
		self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.xdesc = self.desc
		# add name to list of nouns
		if n in vocab.nounDict:
			vocab.nounDict[n].append(self)
		else:
			vocab.nounDict[n] = [self]
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.base_xdesc = self.base_desc
	
	def inListUpdate(self):
		inlist = " In the " + self.name + " is "
		for thing in self.containsIn:
			inlist = inlist + thing.getArticle() + thing.verbose_name
			if thing is self.containsIn[-1]:
				inlist = inlist + "."
			elif thing is self.containsIn[-2]:
				inlist = inlist + " and "
			else:
				inlist = inlist + ", "
		if len(self.containsIn)==0:
			inlist = ""
		self.desc = self.base_desc + inlist
		self.xdesc = self.base_xdesc + inlist
		self.containsDesc = inlist

	def addIn(self, item):
		item.location = self
		self.location.sub_contains.append(item)
		self.containsIn.append(item)
		self.inListUpdate()

	def removeThing(self, thing):
		if thing in self.containsOn:
			self.containsOn.remove(thing)
		else:
			self.containsIn.remove(thing)
		if not self.location==False:
			self.location.sub_contains.remove(thing)
		thing.location = False
		self.inListUpdate()

class Clothing(Thing):
	wearable = True

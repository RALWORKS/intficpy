from . import vocab
#from string import capitalize
things = {}
thing_ix = 0
class Thing:
	def __init__(self, n):
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
		
		# thing properties
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
	contains = []
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
	
	def __init__(self, n):
		self.contains = []
		self.sub_contains = []
		self.name = n
		self.verbose_name = n
		self.ask = False
		self.tell = False
		self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.xdesc = self.desc
		self.containsDesc = ""
		# add name to list of nouns
		if n in vocab.nounDict:
			vocab.nounDict[n].append(self)
		else:
			vocab.nounDict[n] = [self]
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.base_xdesc = self.base_desc
		
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
	
	def containsListUpdate(self):
		onlist = " On the " + self.name + " is "
		for thing in self.contains:
			onlist = onlist + thing.getArticle() + thing.verbose_name
			if thing is self.contains[-1]:
				onlist = onlist + "."
			elif thing is self.contains[-2]:
				onlist = onlist + " and "
			else:
				onlist = onlist + ", "
		if len(self.contains)==0:
			onlist = ""
		self.desc = self.base_desc + onlist
		self.xdesc = self.base_xdesc + onlist
		self.containsDesc = onlist

	def addOn(self, item):
		item.location = self
		self.location.sub_contains.append(item)
		self.contains.append(item)
		self.containsListUpdate()

	def removeThing(self, thing):
		if thing in self.contains:
			self.contains.remove(thing)
		else:
			self.contains.remove(thing)
		self.location.sub_contains.remove(thing)
		thing.location = False
		self.containsListUpdate()
		
class Container(Thing):
	invItem = True
	
	def __init__(self, n):
		self.contains = []
		self.sub_contains = []
		self.name = n
		self.verbose_name = n
		self.ask = False
		self.tell = False
		self.desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.xdesc = self.desc
		self.containsDesc = ""
		# add name to list of nouns
		if n in vocab.nounDict:
			vocab.nounDict[n].append(self)
		else:
			vocab.nounDict[n] = [self]
		self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here."
		self.base_xdesc = self.base_desc
		
		# indexing for save
		global thing_ix
		self.ix = "thing" + str(thing_ix)
		thing_ix = thing_ix + 1
		things[self.ix] = self
	
	def containsListUpdate(self):
		inlist = " In the " + self.name + " is "
		for thing in self.contains:
			inlist = inlist + thing.getArticle() + thing.verbose_name
			if thing is self.contains[-1]:
				inlist = inlist + "."
			elif thing is self.contains[-2]:
				inlist = inlist + " and "
			else:
				inlist = inlist + ", "
		if len(self.contains)==0:
			inlist = ""
		self.desc = self.base_desc + inlist
		self.xdesc = self.base_xdesc + inlist
		self.containsDesc = inlist

	def addIn(self, item):
		item.location = self
		self.location.sub_contains.append(item)
		self.contains.append(item)
		self.containsListUpdate()

	def removeThing(self, thing):
		if thing in self.contains:
			self.contains.remove(thing)
		else:
			self.contains.remove(thing)
		if not self.location==False:
			self.location.sub_contains.remove(thing)
		thing.location = False
		self.containsListUpdate()

class Clothing(Thing):
	wearable = True

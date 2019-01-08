import vocab
from string import capitalize

class Thing:
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
	isPlural = False
	hasArticle = True
	isDefinite = False
	invItem = True
	adjectives = []
	cannotTakeMsg = "You cannot take that."
	
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
		self.desc = capitalize(self.getArticle()) + self.verbose_name + " is here."


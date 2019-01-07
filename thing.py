import vocab

class Thing:
	def __init__(self, n):
		self.name = n
		self.verbose_name = n
		self.ask = False
		self.tell = False
		
		if self.verbose_name[0] in ["a", "e", "i", "o", "u"]:
			self.desc = "There is an " + self.verbose_name + " here."
		else:
			self.desc = "There is a " + self.verbose_name + " here."
		self.xdesc = self.desc
		# add name to list of nouns
		if n in vocab.nounDict:
			vocab.nounDict[n].append(self)
		else:
			vocab.nounDict[n] = [self]
	isPlural = False
	preposition = "a"
	invItem = True
	adjectives = []
	
	def addSynonym(self, word):
		if word in vocab.nounDict:
			vocab.nounDict[word].append(self)
		else:
			vocab.nounDict[word] = [self]
			
	def setAdjectives(self, adj_list, update_desc=True):
		self.adjectives = adj_list
		self.verbose_name = " ".join(adj_list) + " " + self.name
		if update_desc:
			if self.verbose_name[0] in ["a", "e", "i", "o", "u"]:
				self.desc = "There is an " + self.verbose_name + " here."
			else:
				self.desc = "There is a " + self.verbose_name + " here."
			self.xdesc = self.desc

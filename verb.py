import vocab
import settings
import actor
game = __import__(settings.main_file)

# Class for IntFicPy verbs
class Verb:
	word = ""
	hasDobj = False
	hasIobj = False
	impDobj = False
	impIobj = False
	preposition = False
	syntax = []
	dscope = "room" # "knows", "room" or "inv"
	iscope = "room"
	
	def __init__(self, word):
		if word in vocab.verbDict:
			vocab.verbDict[word].append(self)
		else:
			vocab.verbDict[word] = [self]
		self.word = word
		self.dscope = "room"
		
	def addSynonym(self, word):
		if word in vocab.verbDict:
			vocab.verbDict[word].append(self)
		else:
			vocab.verbDict[word] = [self]
	
	def verbFunc(self, dobj):
		print("You " + self.word + "the " + dobj.verbose_name + ".")
		
	def getImpDobj(self):
		print("Error: no implicit direct object defined")

	def getImpIobj(self):
		print("Error: no implicit indirect object defined")


# Below are IntFicPy's built in verbs
###########################################################################

# GET/TAKE
getVerb = Verb("get")
getVerb.addSynonym("take")
getVerb.syntax = [["get", "<dobj>"], ["take", "<dobj>"]]
getVerb.hasDobj = True

def getVerbFunc(dobj):
	print("You take the " + dobj.verbose_name + ".")
	game.me.location.removeThing(dobj)
	game.me.inventory.append(dobj)

getVerb.verbFunc = getVerbFunc

# DROP
dropVerb = Verb("drop")
dropVerb.syntax = [["drop", "<dobj>"]]
dropVerb.hasDobj = True
dropVerb.dscope = "inv"

def dropVerbFunc(dobj):
	print("You drop the " + dobj.verbose_name + ".")
	game.me.location.addThing(dobj)
	game.me.inventory.remove(dobj)

dropVerb.verbFunc = dropVerbFunc

# VIEW INVENTORY
invVerb = Verb("inventory")
invVerb.addSynonym("i")
invVerb.syntax = [["inventory"], ["i"]]
invVerb.hasDobj = False

def invVerbFunc():
	if len(game.me.inventory)==0:
		print("You don't have anything with you.")
	else:
		invdesc = "You have "
		for thing in game.me.inventory:
			if thing.verbose_name[0] in ["a", "e", "i", "o", "u"]:
				invdesc = invdesc + "an " + thing.verbose_name
			else:
				invdesc = invdesc + "a " + thing.verbose_name
			if thing is game.me.inventory[-1]:
				invdesc = invdesc + "."
			elif thing is game.me.inventory[-2]:
				invdesc = invdesc + " and "
			else:
				invdesc = invdesc + ", "
		print(invdesc)
invVerb.verbFunc = invVerbFunc


# LOOK (general)
lookVerb = Verb("look")
lookVerb.addSynonym("l")
lookVerb.syntax = [["look"], ["l"]]
lookVerb.hasDobj = False

def lookVerbFunc():
	game.me.location.describe()

lookVerb.verbFunc = lookVerbFunc

# EXAMINE (specific)
examineVerb = Verb("examine")
examineVerb.addSynonym("x")
examineVerb.syntax = [["examine", "<dobj>"], ["x", "<dobj>"]]
examineVerb.hasDobj = True

def examineVerbFunc(dobj):
	print (dobj.xdesc)

examineVerb.verbFunc = examineVerbFunc

# ASK (Actor)
askVerb = Verb("ask")
askVerb.syntax = [["ask", "<dobj>", "about", "<iobj>"]]
askVerb.hasDobj = True
askVerb.hasIobj = True
askVerb.iscope = "knows"
askVerb.impDobj = True

def getImpAsk():
	people = []
	for p in game.me.location.contains:
		if isinstance(p, actor.Actor):
			people.append(p)
	if len(people)==0:
		print("There's no one here to ask.")
	elif len(people)==1:
		return people[0]
	else:
		print("Please specify a person to ask.")

askVerb.getImpDobj = getImpAsk

def askVerbFunc(dobj, iobj):
	if isinstance(dobj, actor.Actor):
		if iobj in dobj.ask_topics:
			dobj.ask_topics[iobj].func()
		else:
			dobj.defaultTopic()
	else:
		print "You cannot talk to that."

askVerb.verbFunc = askVerbFunc

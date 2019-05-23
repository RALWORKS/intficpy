from . import vocab
from . import actor
from . import thing
from . import room

##############################################################
# VERB.PY - verbs for IntFicPy 
# Defines the Verb class,  and the default verbs
##############################################################

class Verb:
	"""Verb objects represent actions the player can take """
	def __init__(self, word):
		"""Set default properties for the Verb instance
		Takes argument word, a one word verb (string)
		The creator can build constructions like "take off" by specifying prepositions and syntax """
		if word in vocab.verbDict:
			vocab.verbDict[word].append(self)
		else:
			vocab.verbDict[word] = [self]
		self.word = word
		self.dscope = "room"
		word = ""
		self.hasDobj = False
		self.hasIobj = False
		self.impDobj = False
		self.impIobj = False
		self.preposition = False
		self.syntax = []
		# range for direct and indierct objects
		self.dscope = "room" # "knows", "near", "room" or "inv"
		self.iscope = "room"

	def addSynonym(self, word):
		"""Add a synonym verb
			Takes argument word, a single verb (string)
			The creator can build constructions like "take off" by specifying prepositions and syntax """
		if word in vocab.verbDict:
			vocab.verbDict[word].append(self)
		else:
			vocab.verbDict[word] = [self]
	
	def verbFunc(self, me, app):
		"""The default verb function
		Takes arguments me, pointing to the player, app, pointing to the GUI app, and dobj, the direct object
		Should generally be overwritten by the game creator
		Optionally add arguments dobj and iobj, and set hasDobj and hasIobj appropriately """
		app.printToGUI("You " + self.word + ".")
	
	def getImpDobj(self, me, app):
		"""Get the implicit direct object
		The creator should overwrite this if planning to use implicit objects
		View the ask verb for an example """
		app.printToGUI("Error: no implicit direct object defined")

	def getImpIobj(self, me, app):
		""""Get the implicit indirect object
		The creator should overwrite this if planning to use implicit objects """
		app.printToGUI("Error: no implicit indirect object defined")

def getNested(target):
	"""Use a depth first search to find all nested Things in Containers and Surfaces
	Takes argument target, pointing to a Thing
	Returns a list of Things
	Used by multiple verbs """
	# list to populate with found Things
	nested = []
	# iterate through top level contents
	for key, items in target.contains.items():
		for item in items:
			lvl = 0
			push = False
			# a dictionary of levels used to keep track of what has not yet been searched
			lvl_dict = {}
			lvl_dict[0] = []
			# get a list of things in the top level
			for key, things in item.contains.items():
				for thing in things:
					lvl_dict[0].append(thing)
			# a list of the parent items of each level
			# last item is current parent
			lvl_parent = [item]
			if item not in nested:
				nested.append(item)
			# when the bottom level is empty, the search is complete
			while lvl_dict[0] != []:
				# a list of searched items to remove from the level
				remove_scanned = []
				# pop to lower level if empty
				if lvl_dict[lvl]==[]:
					lvl_dict[lvl-1].remove(lvl_parent[-1])
					lvl_parent = lvl_parent[:-1]
					lvl = lvl - 1
				# scan items on current level
				for y in lvl_dict[lvl]:
					if not y in nested:
						# if y contains items, push into y.contains 
						if y.contains != {}:
							lvl = lvl + 1
							lvl_dict[lvl] = []
							for things, key in item.contains.items():
								for thing in things:
									lvl_dict[lvl].append(thing)
							lvl_parent.append(y)
							push = True
							#break
						else:
							remove_scanned.append(y)
				# remove scanned items from lvl_dict
				for r in remove_scanned:
					# NOTE: this will break for duplicate objects with contents
					if push:
						lvl_dict[lvl-1].remove(r)
					else:
						lvl_dict[lvl].remove(r)
				
				# reset push marker
				push = False
	return nested
	

# Below are IntFicPy's built in verbs
###########################################################################

# GET/TAKE
# transitive verb, no indirect object
getVerb = Verb("get")
getVerb.addSynonym("take")
getVerb.addSynonym("pick")
getVerb.syntax = [["get", "<dobj>"], ["take", "<dobj>"], ["pick", "up", "<dobj>"], ["pick", "<dobj>", "up"]]
getVerb.preposition = ["up"]
getVerb.hasDobj = True

def getVerbFunc(me, app, dobj):
	"""Take a Thing from the room
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	# first check if dobj can be taken
	if me.ix in dobj.contains or me.ix in dobj.sub_contains:
		while me.ix in dobj.sub_contains:
			if isinstance(me.location, thing.Container):
				climbOutOfVerb.verbFunc(me, app, dobj)
			elif isinstance(me.location, thing.Surface):
				climbDownFromVerb.verbFunc(me, app, dobj)
			else:
				app.printToGUI("Could not move player out of " + dobj.verbose_name)
				return False
		if me.ix in dobj.contains:
			if isinstance(dobj, thing.Container):
				climbOutOfVerb.verbFunc(me, app, dobj)
			elif isinstance(dobj, thing.Surface):
				climbDownFromVerb.verbFunc(me, app, dobj)
			else:
				app.printToGUI("Could not move player out of " + dobj.verbose_name)
				return False
			
	if dobj.invItem:
		# print the action message
		app.printToGUI("You take " + dobj.getArticle(True) + dobj.verbose_name + ".")
		# get any nested objects
		nested = getNested(dobj)
		for t in nested:
			#dobj.location.sub_contains.remove(t)
			dobj.location.sub_contains[t.ix].remove(t)
			if dobj.location.sub_contains[t.ix] == []:
				del dobj.location.sub_contains[t.ix]
			#me.sub_contains.append(t)
			if t.ix in me.contains:
				me.sub_contains[t.ix].append(t)
			else:
				me.sub_contains[t.ix] = [t]
		# if the location of dobj is a Thing, remove it from the Thing
		if isinstance(dobj.location, thing.Thing) and not isinstance(dobj.location, actor.Actor):
			old_loc = dobj.location
			dobj.location.removeThing(dobj)
			old_loc.containsListUpdate()
		# else assume location is a Room
		else:
			dobj.location.removeThing(dobj)
		dobj.location = me
		#me.contains.append(dobj)
		if dobj.ix in me.contains:
			me.contains[dobj.ix].append(dobj)
		else:
			me.contains[dobj.ix] = [dobj]
	else:
		# if the dobj can't be taken, print the message
		app.printToGUI(dobj.cannotTakeMsg)

# replace the default verb function
getVerb.verbFunc = getVerbFunc

# DROP
# transitive verb, no indirect object
dropVerb = Verb("drop")
dropVerb.addSynonym("put")
dropVerb.syntax = [["drop", "<dobj>"], ["put", "down", "<dobj>"], ["put", "<dobj>", "down"]]
dropVerb.hasDobj = True
dropVerb.dscope = "inv"
dropVerb.preposition = ["down"]

def dropVerbFunc(me, app, dobj):
	"""Drop a Thing from the contains
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	# print the action message
	app.printToGUI("You drop " + dobj.getArticle(True) + dobj.verbose_name + ".")
	# if dobj is in sub_contains, remove it
	if dobj.ix in me.sub_contains:
		#me.sub_contains.remove(dobj)
		me.sub_contains[dobj.ix].remove(dobj)
		if me.sub_contains[dobj.ix] == []:
			del me.sub_contains[dobj.ix]
	# get nested Things
	nested = getNested(dobj)
	for thing in nested:
		#me.sub_contains.remove(thing)
		me.sub_contains[thing.ix].remove(thing)
		if me.sub_contains[thing.ix] == []:
			del me.sub_contains[thing.ix]
		#me.location.sub_contains.append(thing)
		if thing.ix in me.location.sub_contains:
			me.location.sub_contains[thing.ix].append(thing)
		else:
			me.location.sub_contains[thing.ix] = [thing]
	# add the Thing to the player location
	me.location.addThing(dobj)
	#me.contains.remove(dobj)
	if dobj.ix in me.contains:
		if dobj in me.contains[dobj.ix]:
			me.contains[dobj.ix].remove(dobj)
			if me.contains[dobj.ix] == []:
				del me.contains[dobj.ix]
		else:
			me.sub_contains[dobj.ix].remove(dobj)
			if me.sub_contains[dobj.ix] == []:
				del me.sub_contains[dobj.ix]
	# set the Thing's location property
	dobj.location = me.location

# replace the default verbFunc method
dropVerb.verbFunc = dropVerbFunc

# PUT/SET ON
# transitive verb with indirect object
setOnVerb = Verb("set")
setOnVerb.addSynonym("put")
setOnVerb.syntax = [["put", "<dobj>", "on", "<iobj>"], ["set", "<dobj>", "on", "<iobj>"]]
setOnVerb.hasDobj = True
setOnVerb.dscope = "inv"
setOnVerb.hasIobj = True
setOnVerb.iscope = "room"
setOnVerb.preposition = ["on"]

def setOnVerbFunc(me, app, dobj, iobj):
	"""Put a Thing on a Surface
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	outer_loc = me.getOutermostLocation()
	if iobj==outer_loc.floor:
		app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " on the ground.")
		me.contains[dobj.ix].remove(dobj)
		if me.contains[dobj.ix] == []:
			del me.contains[dobj.ix]
		# remove all nested objects for dobj from contains
		nested = getNested(dobj)
		for t in nested:
			#me.sub_contains.remove(t)
			del me.sub_contains[t.ix][0]
			if me.sub_contains[t.ix] == []:
				del me.sub_contains[t.ix]
			#iobj.sub_contains.append(t)
			if t.ix in outer_loc.sub_contains:
				outer_loc.sub_contains[t.ix].append(t)
			else:
				outer_loc.sub_contains[t.ix] = [t]
		outer_loc.addThing(dobj)
		return True
	if isinstance(iobj, thing.Surface):
		app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " on " + iobj.getArticle(True) + iobj.verbose_name + ".")
		me.contains[dobj.ix].remove(dobj)
		if me.contains[dobj.ix] == []:
			del me.contains[dobj.ix]
		# remove all nested objects for dobj from contains
		nested = getNested(dobj)
		for t in nested:
			#me.sub_contains.remove(t)
			del me.sub_contains[t.ix][0]
			if me.sub_contains[t.ix] == []:
				del me.sub_contains[t.ix]
			#iobj.sub_contains.append(t)
			if t.ix in iobj.sub_contains:
				iobj.sub_contains[t.ix].append(t)
			else:
				iobj.sub_contains[t.ix] = [t]
		iobj.addOn(dobj)
	# if iobj is not a Surface
	else:
		app.printToGUI("There is no surface to set it on.")

# replace the default verbFunc method
setOnVerb.verbFunc = setOnVerbFunc

# PUT/SET IN
# transitive verb with indirect object
setInVerb = Verb("set")
setInVerb.addSynonym("put")
setInVerb.syntax = [["put", "<dobj>", "in", "<iobj>"], ["set", "<dobj>", "in", "<iobj>"]]
setInVerb.hasDobj = True
setInVerb.dscope = "inv"
setInVerb.hasIobj = True
setInVerb.iscope = "room"
setInVerb.preposition = ["in"]

def setInVerbFunc(me, app, dobj, iobj):
	"""Put a Thing in a Container
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if isinstance(iobj, thing.Container) and iobj.size >= dobj.size:
		app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " in " + iobj.getArticle(True) + iobj.verbose_name + ".")
		#me.contains.remove(dobj)
		me.contains[dobj.ix].remove(dobj)
		if me.contains[dobj.ix] == []:
			del me.contains[dobj.ix]
		# remove all nested objects for dobj from contains
		nested = getNested(dobj)
		for t in nested:
			#me.sub_contains.remove(t)
			del me.sub_contains[t.ix][0]
			if me.sub_contains[t.ix] == []:
				del me.sub_contains[t.ix]
			#iobj.sub_contains.append(t)
			if t.ix in iobj.sub_contains:
				iobj.sub_contains[t.ix].append(t)
			else:
				iobj.sub_contains[t.ix] = [t]
		iobj.addIn(dobj)
		return True
	elif isinstance(iobj, thing.Container):
		app.printToGUI("The " + dobj.verbose_name + " is too big to fit inside the " + iobj.verbose_name + ".")
		return False
	else:
		app.printToGUI("There is no way to put it inside the " + iobj.verbose_name + ".")
		return False

# replace the default verbFunc method
setInVerb.verbFunc = setInVerbFunc

# VIEW contains
# intransitive verb
invVerb = Verb("contains")
invVerb.addSynonym("i")
invVerb.syntax = [["contains"], ["i"]]
invVerb.hasDobj = False

def invVerbFunc(me, app):
	"""View the player's contains
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# describe contains
	if len(me.contains)==0:
		app.printToGUI("You don't have anything with you.")
	else:
		# the string to print listing the contains
		invdesc = "You have "
		list_version = list(me.contains.keys())
		for key in list_version:
			if len(me.contains[key]) > 1:
				# fix for containers?
				invdesc = invdesc + str(len(me.contains[key])) + " " + me.contains[key][0].getPlural()
			else:
				invdesc = invdesc + me.contains[key][0].getArticle() + me.contains[key][0].verbose_name
			# if the Thing contains Things, list them
			if me.contains[key][0].contains != {}:
				# remove capitalization and terminating period from contains_desc
				c = me.contains[key][0].contains_desc.lower()
				c =c[1:-1]
				invdesc = invdesc + " (" + c + ")"
			# add appropriate punctuation and "and"
			if key is list_version[-1]:
				invdesc = invdesc + "."
			else:
				invdesc = invdesc + ", "
			if len(list_version) > 1:
				if key is list_version[-2]:
					invdesc = invdesc + " and "
		app.printToGUI(invdesc)
	# describe clothing
	if me.wearing != {}:
		# the string to print listing clothing
		weardesc = "You are wearing "
		list_version = list(me.wearing.keys())
		for key in list_version:
			if len(me.wearing[key]) > 1:
				weardesc = weardesc + str(len(me.wearing[key])) + " " + me.wearing[key][0].getPlural()
			else:
				weardesc = weardesc + me.wearing[key][0].getArticle() + me.wearing[key][0].verbose_name
			# add appropriate punctuation and "and"
			if key is list_version[-1]:
				weardesc = weardesc + "."
			elif key is list_version[-2]:
				weardesc = weardesc + " and "
			else:
				weardesc = weardesc + ", "
		app.printToGUI(weardesc)
		
# replace default verbFunc method
invVerb.verbFunc = invVerbFunc


# LOOK (general)
# intransitive verb
lookVerb = Verb("look")
lookVerb.addSynonym("l")
lookVerb.syntax = [["look"], ["l"]]
lookVerb.hasDobj = False

def lookVerbFunc(me, app):
	"""Look around the current room
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# print location description
	loc = me.getOutermostLocation()
	loc.describe(me, app)

# replace default verbFunc method
lookVerb.verbFunc = lookVerbFunc

# EXAMINE (specific)
# transitive verb, no indirect object
examineVerb = Verb("examine")
examineVerb.addSynonym("x")
examineVerb.addSynonym("look")
examineVerb.syntax = [["examine", "<dobj>"], ["x", "<dobj>"], ["look", "at", "<dobj>"]]
examineVerb.hasDobj = True
examineVerb.dscope = "near"
examineVerb.preposition = ["at"]

def examineVerbFunc(me, app, dobj):
	"""Examine a Thing """
	# print the target's xdesc (examine descripion)
	app.printToGUI(dobj.xdesc)

# replace default verbFunc method
examineVerb.verbFunc = examineVerbFunc

# LOOK AT (Thing)
# transitive verb, no indirect object
lookInVerb = Verb("look")
lookInVerb.syntax = [["look", "in", "<dobj>"]]
lookInVerb.hasDobj = True
lookInVerb.dscope = "near"
lookInVerb.preposition = ["in"]

def lookInVerbFunc(me, app, dobj):
	"""Look inside a Thing """
	# print the target's xdesc (examine descripion)
	if isinstance(dobj, thing.Container):
		list_version = list(dobj.contains.keys())
		if len(list_version) > 0:
			app.printToGUI(dobj.contains_desc)
		else:
			app.printToGUI("The " + dobj.verbose_name + " is empty.")
	else:
		app.printToGUI("You cannot look inside the " + dobj.verbose_name + ".")

lookInVerb.verbFunc = lookInVerbFunc

# ASK (Actor)
# transitive verb with indirect object
# implicit direct object enabled
askVerb = Verb("ask")
askVerb.syntax = [["ask", "<dobj>", "about", "<iobj>"]]
askVerb.hasDobj = True
askVerb.hasIobj = True
askVerb.iscope = "knows"
askVerb.impDobj = True
askVerb.preposition = ["about"]

def getImpAsk(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	# find every Actor in the current location
	for key, items in me.location.contains.items():
		for item in items:
			if isinstance(item, actor.Actor):
				people.append(item)
	if len(people)==0:
		app.printToGUI("There's no one here to ask.")
	elif len(people)==1:
		# ask the only actor in the room
		return people[0]
	elif isinstance(parser.lastTurn.dobj, actor.Actor):
		# ask whomever the player last interracted with
		return parser.lastTurn.dobj
	else:
		app.printToGUI("Please specify a person to ask.")
		# turn disambiguation mode on
		parser.lastTurn.ambiguous = True

# replace the default getImpDobj method
askVerb.getImpDobj = getImpAsk

def askVerbFunc(me, app, dobj, iobj):
	"""Ask an Actor about a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if isinstance(dobj, actor.Actor):
		# try to find the ask topic for iobj
		if iobj in dobj.ask_topics:
			# call the ask function for iobj
			dobj.ask_topics[iobj].func(app)
		else:
			dobj.defaultTopic(app)
	else:
		app.printToGUI("You cannot talk to that.")

# replace the default verbFunc method
askVerb.verbFunc = askVerbFunc

# TELL (Actor)
# transitive verb with indirect object
# implicit direct object enabled
tellVerb = Verb("tell")
tellVerb.syntax = [["tell", "<dobj>", "about", "<iobj>"]]
tellVerb.hasDobj = True
tellVerb.hasIobj = True
tellVerb.iscope = "knows"
tellVerb.impDobj = True
tellVerb.preposition = ["about"]

def getImpTell(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	# find every Actor in the current location
	for p in me.location.contains:
		if isinstance(p, actor.Actor):
			people.append(p)
	if len(people)==0:
		app.printToGUI("There's no one here to tell.")
	elif len(people)==1:
		# ask the only actor in the room
		return people[0]
	elif isinstance(parser.lastTurn.dobj, actor.Actor):
		# ask whomever the player last interracted with
		return parser.lastTurn.dobj
	else:
		# turn disambiguation mode on
		app.printToGUI("Please specify a person to ask.")
		parser.lastTurn.ambiguous = True

# replace default getImpDobj method
tellVerb.getImpDobj = getImpTell

def tellVerbFunc(me, app, dobj, iobj):
	"""Tell an Actor about a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if isinstance(dobj, actor.Actor):
		if iobj in dobj.tell_topics:
			dobj.tell_topics[iobj].func(app)
		else:
			dobj.defaultTopic(app)
	else:
		app.printToGUI("You cannot talk to that.")

# replace default verbFunc method
tellVerb.verbFunc = tellVerbFunc

# GIVE (Actor)
# transitive verb with indirect object
# implicit direct object enabled
giveVerb = Verb("give")
giveVerb.syntax = [["give", "<iobj>", "to", "<dobj>"], ["give", "<dobj>", "<iobj>"]]
giveVerb.hasDobj = True
giveVerb.hasIobj = True
giveVerb.iscope = "inv"
giveVerb.impDobj = True
giveVerb.preposition = ["to"]

def getImpGive(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	# find every Actor in the current location
	for p in me.location.contains:
		if isinstance(p, actor.Actor):
			people.append(p)
	if len(people)==0:
		app.printToGUI("There's no one here to give it to.")
	elif len(people)==1:
		# ask the only actor in the room
		return people[0]
	elif isinstance(parser.lastTurn.dobj, actor.Actor):
		# ask whomever the player last interracted with
		return parser.lastTurn.dobj
	else:
		# turn disambiguation mode on
		app.printToGUI("Please specify a person to give it to.")
		parser.lastTurn.ambiguous = True

# replace default getImpDobj method
giveVerb.getImpDobj = getImpGive

def giveVerbFunc(me, app, dobj, iobj):
	"""Give an Actor a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if isinstance(dobj, actor.Actor):
		if iobj in dobj.give_topics:
			dobj.give_topics[iobj].func(app)
			if iobj.give:
				me.contains[dobj.ix].remove(dobj)
				if me.contains[dobj.ix] == []:
					del me.contains[dobj.ix]
				# remove all nested objects for dobj from contains
				nested = getNested(dobj)
				for t in nested:
					#me.sub_contains.remove(t)
					del me.sub_contains[t.ix][0]
					if me.sub_contains[t.ix] == []:
						del me.sub_contains[t.ix]
					#iobj.sub_contains.append(t)
					if t.ix in iobj.sub_contains:
						iobj.sub_contains[t.ix].append(t)
					else:
						iobj.sub_contains[t.ix] = [t]
				dobj.addIn(iobj)
		else:
			dobj.defaultTopic(app)
	else:
		app.printToGUI("You cannot talk to that.")

# replace default verbFunc method
giveVerb.verbFunc = giveVerbFunc

# SHOW (Actor)
# transitive verb with indirect object
# implicit direct object enabled
showVerb = Verb("show")
showVerb.syntax = [["show", "<iobj>", "to", "<dobj>"], ["show", "<dobj>", "<iobj>"]]
showVerb.hasDobj = True
showVerb.hasIobj = True
showVerb.iscope = "inv"
showVerb.impDobj = True
showVerb.preposition = ["to"]

def getImpShow(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	# find every Actor in the current location
	for p in me.location.contains:
		if isinstance(p, actor.Actor):
			people.append(p)
	if len(people)==0:
		app.printToGUI("There's no one here to show.")
	elif len(people)==1:
		# ask the only actor in the room
		return people[0]
	elif isinstance(parser.lastTurn.dobj, actor.Actor):
		# ask whomever the player last interracted with
		return parser.lastTurn.dobj
	else:
		# turn disambiguation mode on
		app.printToGUI("Please specify a person to show.")
		parser.lastTurn.ambiguous = True

# replace default getImpDobj method
showVerb.getImpDobj = getImpShow

def showVerbFunc(me, app, dobj, iobj):
	"""Show an Actor a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if isinstance(dobj, actor.Actor):
		if iobj in dobj.show_topics:
			dobj.show_topics[iobj].func(app)
		else:
			dobj.defaultTopic(app)
	else:
		app.printToGUI("You cannot talk to that.")

# replace default verbFunc method
showVerb.verbFunc = showVerbFunc

# WEAR/PUT ON
# transitive verb, no indirect object
wearVerb = Verb("wear")
wearVerb.addSynonym("put")
wearVerb.addSynonym("don")
wearVerb.syntax = [["put", "on", "<dobj>"], ["put", "<dobj>", "on"], ["wear", "<dobj>"], ["don", "<dobj>"]]
wearVerb.hasDobj = True
wearVerb.dscope = "inv"
wearVerb.preposition = ["on"]

def wearVerbFunc(me, app, dobj):
	"""Wear a piece of clothing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if isinstance(dobj, thing.Clothing):
		app.printToGUI("You wear " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		#me.contains.remove(dobj)
		me.contains[dobj.ix].remove(dobj)
		if me.contains[dobj.ix] == []:
			del me.contains[dobj.ix]
		#me.wearing.append(dobj)
		if dobj.ix in me.wearing:
			me.wearing[dobj.ix].append(dobj)
		else:
			me.wearing[dobj.ix] = [dobj]
	else:
		app.printToGUI("You cannot wear that.")

# replace default verbFunc method
wearVerb.verbFunc = wearVerbFunc

# TAKE OFF/DOFF
# transitive verb, no indirect object
doffVerb = Verb("take")
doffVerb.addSynonym("doff")
doffVerb.addSynonym("remove")
doffVerb.syntax = [["take", "off", "<dobj>"], ["take", "<dobj>", "off"], ["doff", "<dobj>"], ["remove", "<dobj>"]]
doffVerb.hasDobj = True
doffVerb.dscope = "wearing"
doffVerb.preposition = ["off"]

def doffVerbFunc(me, app, dobj):
	"""Take off a piece of clothing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	app.printToGUI("You take off " + dobj.getArticle(True) + dobj.verbose_name  + ".")
	#me.contains.append(dobj)
	if dobj.ix in me.contains:
		me.contains[dobj.ix].append(dobj)
	else:
		me.contains[dobj.ix] = [dobj]
	#me.wearing.remove(dobj)
	me.wearing[dobj.ix].remove(dobj)
	if me.wearing[dobj.ix] == []:
		del me.wearing[dobj.ix]

# replace default verbFunc method
doffVerb.verbFunc = doffVerbFunc

# LIE DOWN
# intransitive verb
lieDownVerb = Verb("lie")
lieDownVerb.addSynonym("lay")
lieDownVerb.syntax = [["lie", "down"], ["lay", "down"]]
lieDownVerb.preposition = ["down"]

def lieDownVerbFunc(me, app):
	"""Take off a piece of clothing
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app"""
	if me.position != "lying":
		if isinstance(me.location, thing.Thing):
			if not me.location.canLie:
				app.printToGUI("(First getting " + me.location.contains_preposition_inverse + " of " + me.location.getArticle(True) + me.location.verbose_name + ".)")
				outer_loc = me.getOutermostLocation()
				me.location.removeThing(me)
				outer_loc.addThing(me) 
		app.printToGUI("You lie down.")
		me.makeLying()
	else:
		app.printToGUI("You are already lying down.")
# replace default verbFunc method
lieDownVerb.verbFunc = lieDownVerbFunc

# STAND UP
# intransitive verb
standUpVerb = Verb("stand")
standUpVerb.syntax = [["stand", "up"], ["stand"]]
standUpVerb.preposition = ["up"]

def standUpVerbFunc(me, app):
	"""Take off a piece of clothing
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app"""
	if me.position != "standing":
		if isinstance(me.location, thing.Thing):
			if not me.location.canStand:
				app.printToGUI("(First getting " + me.location.contains_preposition_inverse + " of " + me.location.getArticle(True) + me.location.verbose_name + ".)")
				outer_loc = me.getOutermostLocation()
				me.location.removeThing(me)
				outer_loc.addThing(me) 
		app.printToGUI("You stand up.")
		me.makeStanding()
	else:
		app.printToGUI("You are already standing.")

# replace default verbFunc method
standUpVerb.verbFunc = standUpVerbFunc

# SIT DOWN
# intransitive verb
sitDownVerb = Verb("sit")
sitDownVerb.syntax = [["sit", "down"], ["sit"]]
sitDownVerb.preposition = ["down"]

def sitDownVerbFunc(me, app):
	"""Take off a piece of clothing
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app"""
	if me.position != "sitting":
		if isinstance(me.location, thing.Thing):
			if not me.location.canSit:
				app.printToGUI("(First getting " + me.location.contains_preposition_inverse + " of " + me.location.getArticle(True) + me.location.verbose_name + ".)")
				outer_loc = me.getOutermostLocation()
				me.location.removeThing(me)
				outer_loc.addThing(me) 
		app.printToGUI("You sit down.")
		me.makeSitting()
	else:
		app.printToGUI("You are already sitting.")

# replace default verbFunc method
sitDownVerb.verbFunc = sitDownVerbFunc

# STAND ON (SURFACE)
# transitive verb, no indirect object
standOnVerb = Verb("stand")
standOnVerb.syntax = [["stand", "on", "<dobj>"]]
standOnVerb.hasDobj = True
standOnVerb.dscope = "room"
standOnVerb.preposition = ["on"]

def standOnVerbFunc(me, app, dobj):
	"""Sit on a Surface where canSit is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	outer_loc = me.getOutermostLocation()
	if dobj==outer_loc.floor:
		if me.location==outer_loc and me.position=="standing":
			app.printToGUI("You are already standing on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		elif me.location==outer_loc:
			app.printToGUI("You stand on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
			me.makeStanding()
		else:
			me.location.removeThing(me)
			outer_loc.addThing(me)
			app.printToGUI("You stand on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
			me.makeStanding()
		return True
	if me.location==dobj and me.position=="standing" and isinstance(dobj, thing.Surface):
		app.printToGUI("You are already standing on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
	elif isinstance(dobj, thing.Surface) and dobj.canStand:
		app.printToGUI("You stand on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addOn(me)
		me.makeStanding()
	else:
		app.printToGUI("You cannot stand on " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
standOnVerb.verbFunc = standOnVerbFunc

# SIT ON (SURFACE)
# transitive verb, no indirect object
sitOnVerb = Verb("sit")
sitOnVerb.syntax = [["sit", "on", "<dobj>"], ["sit", "down", "on", "<dobj>"]]
sitOnVerb.hasDobj = True
sitOnVerb.dscope = "room"
sitOnVerb.preposition = ["down", "on"]

def sitOnVerbFunc(me, app, dobj):
	"""Stand on a Surface where canStand is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	outer_loc = me.getOutermostLocation()
	if dobj==outer_loc.floor:
		if me.location==outer_loc and me.position=="sitting":
			app.printToGUI("You are already sitting on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		elif me.location==outer_loc:
			app.printToGUI("You sit on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
			me.makeSitting()
		else:
			me.location.removeThing(me)
			outer_loc.addThing(me)
			app.printToGUI("You sit on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
			me.makeSitting()
		return True
	if me.location==dobj and me.position=="sitting" and isinstance(dobj, thing.Surface):
		app.printToGUI("You are already sitting on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
	elif isinstance(dobj, thing.Surface) and dobj.canSit:
		app.printToGUI("You sit on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addOn(me)
		me.makeSitting()
	else:
		app.printToGUI("You cannot sit on " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
sitOnVerb.verbFunc = sitOnVerbFunc

# LIE ON (SURFACE)
# transitive verb, no indirect object
lieOnVerb = Verb("lie")
lieOnVerb.addSynonym("lay")
lieOnVerb.syntax = [["lie", "on", "<dobj>"], ["lie", "down", "on", "<dobj>"], ["lay", "on", "<dobj>"], ["lay", "down", "on", "<dobj>"]]
lieOnVerb.hasDobj = True
lieOnVerb.dscope = "room"
lieOnVerb.preposition = ["down", "on"]

def lieOnVerbFunc(me, app, dobj):
	"""Lie on a Surface where canLie is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	outer_loc = me.getOutermostLocation()
	if dobj==outer_loc.floor:
		if me.location==outer_loc and me.position=="lying":
			app.printToGUI("You are already lying " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		elif me.location==outer_loc:
			app.printToGUI("You lie on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
			me.makeLying()
		else:
			me.location.removeThing(me)
			outer_loc.addThing(me)
			app.printToGUI("You lie on the " + dobj.getArticle(True) + dobj.verbose_name  + ".")
			me.makeLying()
		return True
	if me.location==dobj and me.position=="lying" and isinstance(dobj, thing.Surface):
		app.printToGUI("You are already lying on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
	elif isinstance(dobj, thing.Surface) and dobj.canLie:
		app.printToGUI("You lie on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addOn(me)
		me.makeLying()
	else:
		app.printToGUI("You cannot lie on " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
lieOnVerb.verbFunc = lieOnVerbFunc

# SIT IN (CONTAINER)
# transitive verb, no indirect object
sitInVerb = Verb("sit")
sitInVerb.syntax = [["sit", "in", "<dobj>"], ["sit", "down", "in", "<dobj>"]]
sitInVerb.hasDobj = True
sitInVerb.dscope = "room"
sitInVerb.preposition = ["down", "in"]

# when the Chair subclass of Surface is implemented, redirect to sit on if dobj is a Chair
def sitInVerbFunc(me, app, dobj):
	"""Stand on a Surface where canStand is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if me.location==dobj and me.position=="sitting" and isinstance(dobj, thing.Container):
		app.printToGUI("You are already sitting in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
	elif isinstance(dobj, thing.Container) and dobj.canSit:
		app.printToGUI("You sit in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addIn(me)
		me.makeSitting()
	else:
		app.printToGUI("You cannot sit in " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
sitInVerb.verbFunc = sitInVerbFunc

# STAND IN (CONTAINER)
# transitive verb, no indirect object
standInVerb = Verb("stand")
standInVerb.syntax = [["stand", "in", "<dobj>"]]
standInVerb.hasDobj = True
standInVerb.dscope = "room"
standInVerb.preposition = ["in"]

def standInVerbFunc(me, app, dobj):
	"""Sit on a Surface where canSit is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if me.location==dobj and me.position=="standing" and isinstance(dobj, thing.Container):
		app.printToGUI("You are already standing in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
	elif isinstance(dobj, thing.Container) and dobj.canStand:
		app.printToGUI("You stand in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addIn(me)
		me.makeStanding()
	else:
		app.printToGUI("You cannot stand in " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
standInVerb.verbFunc = standInVerbFunc

# LIE IN (CONTAINER)
# transitive verb, no indirect object
lieInVerb = Verb("lie")
lieInVerb.addSynonym("lay")
lieInVerb.syntax = [["lie", "in", "<dobj>"], ["lie", "down", "in", "<dobj>"], ["lay", "in", "<dobj>"], ["lay", "down", "in", "<dobj>"]]
lieInVerb.hasDobj = True
lieInVerb.dscope = "room"
lieInVerb.preposition = ["down", "in"]

def lieInVerbFunc(me, app, dobj):
	"""Lie on a Surface where canLie is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if me.location==dobj and me.position=="lying" and isinstance(dobj, thing.Container):
		app.printToGUI("You are already lying in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
	elif isinstance(dobj, thing.Container) and dobj.canLie:
		app.printToGUI("You lie in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addIn(me)
		me.makeLying()
	else:
		app.printToGUI("You cannot lie in " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
lieInVerb.verbFunc = lieInVerbFunc

# CLIMB ON (SURFACE)
# transitive verb, no indirect object
climbOnVerb = Verb("climb")
climbOnVerb.addSynonym("get")
climbOnVerb.syntax = [["climb", "on", "<dobj>"], ["get", "on", "<dobj>"], ["climb", "<dobj>"], ["climb", "up", "<dobj>"]]
climbOnVerb.hasDobj = True
climbOnVerb.dscope = "room"
climbOnVerb.preposition = ["on", "up"]

def climbOnVerbFunc(me, app, dobj):
	"""Climb on a Surface where one of more of canStand/canSit/canLie is True
	Will be extended once stairs/ladders are implemented
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if isinstance(dobj, thing.AbstractClimbable):
		if dobj.direction=="u":
			dobj.connection.travel(me, app)
		else:
			app.printToGUI("You can't climb up that.")
	elif isinstance(dobj, thing.Surface) and dobj.canStand:
		standOnVerb.verbFunc(me, app, dobj)
	elif isinstance(dobj, thing.Surface) and dobj.canSit:
		sitOnVerb.verbFunc(me, app, dobj)
	elif isinstance(dobj, thing.Surface) and dobj.canLie:
		lieOnVerb.verbFunc(me, app, dobj)
	else:
		app.printToGUI("You cannot climb on " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
climbOnVerb.verbFunc = climbOnVerbFunc

# CLIMB UP (INTRANSITIVE)
# intransitive verb
climbUpVerb = Verb("climb")
climbUpVerb.syntax = [["climb", "up"], ["climb"]]
climbUpVerb.preposition = ["up"]

def climbUpVerbFunc(me, app):
	"""Climb up to the room above
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from . import travel
	cur_loc = me.getOutermostLocation()
	if cur_loc.up:
		travel.travelU(me, app)
	else:
		app.printToGUI("You cannot climb up from here. ")

# replace default verbFunc method
climbUpVerb.verbFunc = climbUpVerbFunc


# CLIMB DOWN (INTRANSITIVE)
# intransitive verb
climbDownVerb = Verb("climb")
climbDownVerb.addSynonym("get")
climbDownVerb.syntax = [["climb", "off"], ["get", "off"], ["climb", "down"], ["get", "down"]]
climbDownVerb.preposition = ["off", "down"]

def climbDownVerbFunc(me, app):
	"""Climb down from a Surface you currently occupy
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from . import travel
	cur_loc = me.getOutermostLocation()
	if cur_loc.down:
		travel.travelD(me, app)
	elif isinstance(me.location, thing.Surface):
		app.printToGUI("You climb down from " + me.location.getArticle(True) + me.location.verbose_name  + ".")
		outer_loc = me.location.location
		me.location.removeThing(me)
		if isinstance(outer_loc, thing.Surface):
			outer_loc.addOn(me)
		elif isinstance(outer_loc, thing.Container):
			outer_loc.addIn(me)
		elif isinstance(outer_loc, room.Room):
			outer_loc.addThing(me) 
		else:
			print("Unsupported outer location type: " + outer_loc.name)
	else:
		app.printToGUI("You cannot climb down from here. ")

# replace default verbFunc method
climbDownVerb.verbFunc = climbDownVerbFunc

# CLIMB DOWN FROM (SURFACE)
# transitive verb, no indirect object
climbDownFromVerb = Verb("climb")
climbDownFromVerb.addSynonym("get")
climbDownFromVerb.syntax = [["climb", "off", "<dobj>"], ["get", "off", "<dobj>"], ["climb", "down", "from", "<dobj>"], ["get", "down", "from", "<dobj>"], ["climb", "down", "<dobj>"]]
climbDownFromVerb.hasDobj = True
climbDownFromVerb.dscope = "room"
climbDownFromVerb.preposition = ["off", "down", "from"]

def climbDownFromVerbFunc(me, app, dobj):
	"""Climb down from a Surface you currently occupy
	Will be extended once stairs/ladders/up direction/down direction are implemented
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if isinstance(dobj, thing.AbstractClimbable):
		if dobj.direction=="d":
			dobj.connection.travel(me, app)
		else:
			app.printToGUI("You can't climb down from that.")
	elif me.location==dobj:
		if isinstance(me.location, thing.Surface):
			app.printToGUI("You climb down from " + me.location.getArticle(True) + me.location.verbose_name  + ".")
			outer_loc = me.location.location
			me.location.removeThing(me)
			if isinstance(outer_loc, thing.Surface):
				outer_loc.addOn(me)
			elif isinstance(outer_loc, thing.Container):
				outer_loc.addIn(me)
			elif isinstance(outer_loc, room.Room):
				outer_loc.addThing(me) 
			else:
				print("Unsupported outer location type: " + outer_loc.name)
		else:
			app.printToGUI("You cannot climb down from here. ")
	else:
		app.printToGUI("You are not on " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
climbDownFromVerb.verbFunc = climbDownFromVerbFunc

# CLIMB IN (CONTAINER)
# transitive verb, no indirect object
climbInVerb = Verb("climb")
climbInVerb.addSynonym("get")
climbInVerb.syntax = [["climb", "in", "<dobj>"], ["get", "in", "<dobj>"], ["climb", "into", "<dobj>"], ["get", "into", "<dobj>"]]
climbInVerb.hasDobj = True
climbInVerb.dscope = "room"
climbInVerb.preposition = ["in", "into"]

def climbInVerbFunc(me, app, dobj):
	"""Climb in a Container where one of more of canStand/canSit/canLie is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if isinstance(dobj, thing.Container) and dobj.canStand:
		standInVerb.verbFunc(me, app, dobj)
	elif isinstance(dobj, thing.Container) and dobj.canSit:
		sitInVerb.verbFunc(me, app, dobj)
	elif isinstance(dobj, thing.Container) and dobj.canLie:
		lieInVerb.verbFunc(me, app, dobj)
	else:
		app.printToGUI("You cannot climb into " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
climbInVerb.verbFunc = climbInVerbFunc

# CLIMB OUT (INTRANSITIVE)
# intransitive verb
climbOutVerb = Verb("climb")
climbOutVerb.addSynonym("get")
climbOutVerb.syntax = [["climb", "out"], ["get", "out"]]
climbOutVerb.preposition = ["out"]

def climbOutVerbFunc(me, app):
	"""Climb out of a Container you currently occupy
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	if isinstance(me.location, thing.Container):
		app.printToGUI("You climb out of " + me.location.getArticle(True) + me.location.verbose_name  + ".")
		outer_loc = me.location.location
		me.location.removeThing(me)
		if isinstance(outer_loc, thing.Surface):
			outer_loc.addOn(me)
		elif isinstance(outer_loc, thing.Container):
			outer_loc.addIn(me)
		elif isinstance(outer_loc, room.Room):
			outer_loc.addThing(me) 
		else:
			print("Unsupported outer location type: " + outer_loc.name)
	else:
		app.printToGUI("You cannot out of here. ")

# replace default verbFunc method
climbOutVerb.verbFunc = climbOutVerbFunc

# CLIMB OUT OF (CONTAINER)
# transitive verb, no indirect object
climbOutOfVerb = Verb("climb")
climbOutOfVerb.addSynonym("get")
climbOutOfVerb.addSynonym("exit")
climbOutOfVerb.syntax = [["climb", "out", "of", "<dobj>"], ["get", "out", "of", "<dobj>"], ["exit", "<dobj>"]]
climbOutOfVerb.hasDobj = True
climbOutOfVerb.dscope = "room"
climbOutOfVerb.preposition = ["out", "of"]

def climbOutOfVerbFunc(me, app, dobj):
	"""Climb down from a Surface you currently occupy
	Will be extended once stairs/ladders/up direction/down direction are implemented
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if me.location==dobj:
		if isinstance(me.location, thing.Container):
			app.printToGUI("You climb out of " + me.location.getArticle(True) + me.location.verbose_name  + ".")
			outer_loc = me.location.location
			me.location.removeThing(me)
			if isinstance(outer_loc, thing.Surface):
				outer_loc.addOn(me)
			elif isinstance(outer_loc, thing.Container):
				outer_loc.addIn(me)
			elif isinstance(outer_loc, room.Room):
				outer_loc.addThing(me) 
			else:
				print("Unsupported outer location type: " + outer_loc.name)
		else:
			app.printToGUI("You cannot climb out of here. ")
	else:
		app.printToGUI("You are not in " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
climbOutOfVerb.verbFunc = climbOutOfVerbFunc

# OPEN (THING)
# transitive verb, no indirect object
openVerb = Verb("open")
openVerb.syntax = [["open", "<dobj>"]]
openVerb.hasDobj = True
openVerb.dscope = "near"

def openVerbFunc(me, app, dobj):
	"""Open a Thing with an open property
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	try:
		state = dobj.open
	except:
		app.printToGUI("You cannot open " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		return False
	if state==False:
		app.printToGUI("You open " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		dobj.makeOpen()
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already open. ")
	return True
	
# replace default verbFunc method
openVerb.verbFunc = openVerbFunc

# CLOSE (THING)
# transitive verb, no indirect object
closeVerb = Verb("close")
closeVerb.syntax = [["close", "<dobj>"]]
closeVerb.hasDobj = True
closeVerb.dscope = "near"

def closeVerbFunc(me, app, dobj):
	"""Open a Thing with an open property
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	try:
		state = dobj.open
	except:
		app.printToGUI("You cannot close " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		return False
	if state==True:
		app.printToGUI("You close " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		dobj.makeClosed()
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already closed. ")
	return True
	
# replace default verbFunc method
closeVerb.verbFunc = closeVerbFunc

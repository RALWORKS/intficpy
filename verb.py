from . import vocab
from . import actor
from . import player
from . import thing

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
	for item in target.contains:
		lvl = 0
		push = False
		# a dictionary of levels used to keep track of what has not yet been searched
		lvl_dict = {}
		lvl_dict[0] = list(item.contains)
		# a list of the parent items of each level
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
					nested.append(y)
				# if y contains items, push into y.contains 
				if y.contains != []:
					lvl = lvl + 1
					lvl_dict[lvl] = list(y.contains)
					lvl_parent.append(y)
					push = True
					break
				else:
					remove_scanned.append(y)
			# remove scanned items from lvl_dict
			for r in remove_scanned:
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
getVerb.preposition = "up"
getVerb.hasDobj = True

def getVerbFunc(me, app, dobj):
	"""Take a Thing from the room
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	# first check if dobj can be taken
	if dobj.invItem:
		# print the action message
		app.printToGUI("You take " + dobj.getArticle(True) + dobj.verbose_name + ".")
		# get any nested objects
		nested = getNested(dobj)
		for t in nested:
			#dobj.location.sub_contains.remove(t)
			del dobj.location.sub_contains[t.ix][0]
			if dobj.location.sub_contain[t.ix] == []:
				del dobj.location.sub_contains[t.ix]
			#me.sub_inventory.append(t)
			if t.ix in me.inventory:
				me.inventory[t.ix].append(t)
			else:
				me.inventory[t.ix] = [t]
		# if the location of dobj is a Thing, remove it from the Thing
		if isinstance(dobj.location, thing.Thing):
			old_loc = dobj.location
			dobj.location.removeThing(dobj)
			old_loc.containsListUpdate()
		# else assume location is a Room
		else:
			dobj.location.removeThing(dobj)
		#me.inventory.append(dobj)
		if dobj.ix in me.inventory:
			me.inventory[dobj.ix].append(dobj)
		else:
			me.inventory[dobj.ix] = [dobj]
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
dropVerb.preposition = "down"

def dropVerbFunc(me, app, dobj):
	"""Drop a Thing from the inventory
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	# print the action message
	app.printToGUI("You drop " + dobj.getArticle(True) + dobj.verbose_name + ".")
	# if dobj is in sub_inventory, remove it
	if dobj.ix in me.sub_inventory:
		#me.sub_inventory.remove(dobj)
		me.sub_inventory[dobj.ix].remove(dobj)
		if me.sub_inventory[dobj.ix] == []:
			del me.sub_inventory[dobj.ix]
	# get nested Things
	nested = getNested(dobj)
	for thing in nested:
		#me.sub_inventory.remove(thing)
		me.sub_inventory[thing.ix].remove(thing)
		if me.sub_inventory[thing.ix] == []:
			del me.sub_inventory[thing.ix]
		#me.location.sub_contains.append(thing)
		if thing.ix in me.location.sub_contains:
			me.location.sub_contains[thing.ix].append(thing)
		else:
			me.location.sub_contains[thing.ix] = [thing]
	# add the Thing to the player location
	me.location.addThing(dobj)
	#me.inventory.remove(dobj)
	me.inventory[dobj.ix].remove(dobj)
	if me.inventory[dobj.ix] == []:
		del me.inventory[dobj.ix]
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
setOnVerb.preposition = "on"

def setOnVerbFunc(me, app, dobj, iobj):
	"""Put a Thing on a Surface
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if isinstance(iobj, thing.Surface):
		app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " on " + iobj.getArticle(True) + iobj.verbose_name + ".")
		#me.inventory.remove(dobj)
		me.inventory[dobj.ix].remove(dobj)
		if me.inventory[dobj.ix] == []:
			del me.inventory[dobj.ix]
		# remove all nested objects for dobj from inventory
		nested = getNested(dobj)
		for t in nested:
			#me.sub_inventory.remove(t)
			del me.sub_inventory[t.ix][0]
			if me.sub_inventory[t.ix] == []:
				del me.sub_inventory[t.ix]
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
setInVerb.preposition = "in"

def setInVerbFunc(me, app, dobj, iobj):
	"""Put a Thing in a Container
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if isinstance(iobj, thing.Container):
		app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " in " + iobj.getArticle(True) + iobj.verbose_name + ".")
		me.inventory.remove(dobj)
		# remove all nested objects for dobj from inventory
		nested = getNested(dobj)
		for t in nested:
			#me.sub_inventory.remove(t)
			del me.sub_inventory[t][0]
			if me.sub_inventory[t] == []:
				del me.sub_inventory[t]
			#iobj.sub_contains.append(t)
			if t.ix in iobj.sub_contains:
				iobj.sub_contains[t.ix].append(t)
			else:
				iobj.sub_contains[t.ix] = [t]
		iobj.addIn(dobj)
	# if iobj is not a Container
	else:
		app.printToGUI("There is no way to put it inside.")

# replace the default verbFunc method
setInVerb.verbFunc = setInVerbFunc

# VIEW INVENTORY
# intransitive verb
invVerb = Verb("inventory")
invVerb.addSynonym("i")
invVerb.syntax = [["inventory"], ["i"]]
invVerb.hasDobj = False

def invVerbFunc(me, app):
	"""View the player's inventory
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# describe inventory
	if len(me.inventory)==0:
		app.printToGUI("You don't have anything with you.")
	else:
		# the string to print listing the inventory
		invdesc = "You have "
		list_version = list(me.inventory.keys())
		for key in list_version:
			if len(me.inventory[key]) > 1:
				# fix for containers?
				invdesc = invdesc + str(len(me.inventory[key])) + " " + me.inventory[key][0].getPlural()
			else:
				invdesc = invdesc + me.inventory[key][0].getArticle() + me.inventory[key][0].verbose_name
			# if the Thing contains Things, list them
			if me.inventory[key][0].contains != {}:
				# remove capitalization and terminating period from contains_desc
				c = me.inventory[key][0].contains_desc.lower()
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
		for key, things in me.wearing.items():
			for thing in things:
				weardesc = weardesc + thing.getArticle() + thing.verbose_name
				# add appropriate punctuation and "and"
				if thing is me.wearing[-1]:
					weardesc = weardesc + "."
				elif thing is me.wearing[-2]:
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
	me.location.describe(me, app)

# replace default verbFunc method
lookVerb.verbFunc = lookVerbFunc

# EXAMINE (specific)
# transitive verb, no indirect object
examineVerb = Verb("examine")
examineVerb.addSynonym("x")
examineVerb.syntax = [["examine", "<dobj>"], ["x", "<dobj>"]]
examineVerb.hasDobj = True
examineVerb.dscope = "near"

def examineVerbFunc(me, app, dobj):
	"""Examine a Thing """
	# print the target's xdesc (examine descripion)
	app.printToGUI(dobj.xdesc)

# replace default verbFunc method
examineVerb.verbFunc = examineVerbFunc

# ASK (Actor)
# transitive verb with indirect object
# implicit direct object enabled
askVerb = Verb("ask")
askVerb.syntax = [["ask", "<dobj>", "about", "<iobj>"]]
askVerb.hasDobj = True
askVerb.hasIobj = True
askVerb.iscope = "knows"
askVerb.impDobj = True

def getImpAsk(me, app):
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

# WEAR/PUT ON
# transitive verb, no indirect object
wearVerb = Verb("wear")
wearVerb.addSynonym("put")
wearVerb.addSynonym("don")
wearVerb.syntax = [["put", "on", "<dobj>"], ["put", "<dobj>", "on"], ["wear", "<dobj>"], ["don", "<dobj>"]]
wearVerb.hasDobj = True
wearVerb.dscope = "inv"
wearVerb.preposition = "on"

def wearVerbFunc(me, app, dobj):
	"""Wear a piece of clothing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if isinstance(dobj, thing.Clothing):
		app.printToGUI("You wear " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		#me.inventory.remove(dobj)
		me.inventory[dobj.ix].remove(dobj)
		if me.inventory[dobj.ix] == []:
			del me.inventory[dobj.ix]
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
doffVerb.preposition = "off"

def doffVerbFunc(me, app, dobj):
	"""Take off a piece of clothing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	app.printToGUI("You take off " + dobj.getArticle(True) + dobj.verbose_name  + ".")
	#me.inventory.append(dobj)
	if dobj.ix in me.inventory:
		me.inventory[dobj.ix].append(dobj)
	else:
		me.inventory[dobj.ix] = [dobj]
	#me.wearing.remove(dobj)
	me.wearing[dobj.ix].remove(dobj)
	if me.wearing[dobj.ix] == []:
		del me.wearing[dobj.ix]

# replace default verbFunc method
doffVerb.verbFunc = doffVerbFunc

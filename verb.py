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
	def __init__(self, word, list_word=False, exempt_from_list=False):
		"""Set default properties for the Verb instance
		Takes argument word, a one word verb (string)
		The creator can build constructions like "take off" by specifying prepositions and syntax """
		from .parser import aboutGame
		if word in vocab.verbDict:
			vocab.verbDict[word].append(self)
		elif word is not None:
			vocab.verbDict[word] = [self]
		if list_word and list_word not in aboutGame.verbs:
			aboutGame.verbs.append(list_word)
		elif word and word not in aboutGame.verbs and not exempt_from_list:
			aboutGame.verbs.append(word)
		self.word = word
		self.dscope = "room"
		word = ""
		self.far_iobj = False
		self.far_dobj = False
		self.hasDobj = False
		self.hasStrDobj = False
		self.hasStrIobj = False
		self.dtype = None
		self.hasIobj = False
		self.itype = None
		self.impDobj = False
		self.impIobj = False
		self.preposition = []
		self.keywords = []
		self.dobj_direction = False
		self.iobj_direction = False
		self.syntax = []
		# range for direct and indierct objects
		self.dscope = "room" # "knows", "near", "room" or "inv"
		self.iscope = "room"
		# not yet implemented in parser
		self.dobj_contains_iobj = False
		self.iobj_contains_dobj = False

	def addSynonym(self, word):
		from .parser import aboutGame
		"""Add a synonym verb
			Takes argument word, a single verb (string)
			The creator can build constructions like "take off" by specifying prepositions and syntax """
		if word in vocab.verbDict:
			vocab.verbDict[word].append(self)
		else:
			vocab.verbDict[word] = [self]
	
	def discover(self, app, show_msg, list_word=False):
		from .parser import aboutGame
		if list_word and list_word not in aboutGame.discovered_verbs and list_word not in aboutGame.verbs:
			aboutGame.discovered_verbs.append(list_word)
			if show_msg:
				app.printToGUI("Verb discovered: " + list_word)
		elif self.word not in aboutGame.discovered_verbs and word not in aboutGame.verbs:
			aboutGame.discovered_verbs.append(word)
			if show_msg:
				app.printToGUI("Verb discovered: " + word)

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
					lvl_dict[0].append
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
									lvl_dict[lvl].append
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
#getVerb.dscope = "near"
getVerb.dscope = "roomflex"
getVerb.hasDobj = True

def getVerbFunc(me, app, dobj, skip=False):
	"""Take a Thing from the room
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.getVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	# first check if dobj can be taken
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
	if not me.position=="standing":
		app.printToGUI("(First standing up)")
		standUpVerb.verbFunc(me, app)
	if isinstance(dobj, thing.Liquid):
		container = dobj.getContainer()
		if container:
			dobj = container
	if dobj.invItem:
		if me.containsItem(dobj):
			if dobj.location==me:
				app.printToGUI("You already have " + dobj.getArticle(True) + dobj.verbose_name + ".")
				return False
			elif not isinstance(dobj.location, room.Room):
				return removeFromVerb.verbFunc(me, app, dobj, dobj.location)
		# print the action message
		app.printToGUI("You take " + dobj.getArticle(True) + dobj.verbose_name + ".")
		if isinstance(dobj, thing.UnderSpace) and not dobj.contains=={}:
			results = dobj.moveContentsOut()
			msg = results[0]
			plural = results[1]
			if plural:
				msg = msg.capitalize() + " are revealed. "
			else:
				msg = msg.capitalize() + " is revealed. "
			app.printToGUI(msg)
		if dobj.is_composite:
			for item in dobj.child_UnderSpaces:
				if not item.contains=={}:
					results = item.moveContentsOut()
					msg = results[0]
					plural = results[1]
					if plural:
						msg = msg.capitalize() + " are revealed. "
					else:
						msg = msg.capitalize() + " is revealed. "
					app.printToGUI(msg)
		while isinstance(dobj.location, thing.Thing):
			old_loc = dobj.location
			if not isinstance(dobj.location, room.Room):
				dobj.location.removeThing(dobj)
			elif dobj.location.manual_update:
				dobj.location.removeThing(dobj, False, False)
			else:
				dobj.location.removeThing(dobj)
			dobj.location = old_loc.location
			if not isinstance(old_loc, actor.Actor): 
				old_loc.containsListUpdate()
		dobj.location.removeThing(dobj)
		me.addThing(dobj)
		return True
	elif dobj.parent_obj:
		app.printToGUI(dobj.cannotTakeMsg)
		return False
	else:
		# if the dobj can't be taken, print the message
		app.printToGUI(dobj.cannotTakeMsg)
		return False

# replace the default verb function
getVerb.verbFunc = getVerbFunc

# GET/TAKE ALL
# intransitive verb
getAllVerb = Verb("get")
getAllVerb.addSynonym("take")
getAllVerb.syntax = [["get", "all"], ["take", "all"], ["get", "everything"], ["take", "everything"]]
getAllVerb.dscope = "room"
getAllVerb.hasDobj = False
getAllVerb.keywords = ["all", "everything"]

def getAllVerbFunc(me, app):
	"""Take all obvious invItems in the current room
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	loc = me.getOutermostLocation()
	items_found = []
	for key in loc.contains:
		for item in loc.contains[key]:
			if item.invItem and item.known_ix in me.knows_about:
				#getVerb.verbFunc(me, app, item)
				items_found.append(item)
	for key in loc.sub_contains:
		for item in loc.sub_contains[key]:
			if item.invItem and item.known_ix in me.knows_about:
				#getVerb.verbFunc(me, app, item)
				items_found.append(item)
	items_already = 0
	for item in items_found:
		if item.ix in me.contains:
			if not item in me.contains[item.ix]:
				getVerb.verbFunc(me, app, item)
			elif item in me.contains[item.ix]:
				items_already = items_already + 1
			elif item.ix in me.sub_contains:
				if not item in me.sub_contains[item.ix]:
					getVerb.verbFunc(me, app, item)
				else:
					items_already = items_already + 1
		elif item.ix in me.sub_contains:
			if not item in me.sub_contains[item.ix]:
				getVerb.verbFunc(me, app, item)
			else:
				items_already = items_already + 1
		else:
			getVerb.verbFunc(me, app, item)
	if len(items_found)==items_already:
		app.printToGUI("There are no obvious items here to take. ")
		
# replace the default verb function
getAllVerb.verbFunc = getAllVerbFunc

# REMOVE FROM
# move to top inventory level - used by parser for implicit actions
# transitive verb, indirect object
removeFromVerb = Verb(None, exempt_from_list=True)
#removeFromVerb.syntax = [["remove", "<dobj>", "from", "<iobj>"]]
removeFromVerb.hasDobj = True
removeFromVerb.hasIobj = True
removeFromVerb.dscope = "near"
removeFromVerb.iscope = "near"
removeFromVerb.iobj_contains_dobj = True
#removeFromVerb.preposition = ["from"]

def removeFromVerbFunc(me, app, dobj, iobj, skip=True):
	"""Remove a Thing from a Thing
	Mostly intended for implicit use within the inventory """
	prep = iobj.contains_preposition or "in"
	if dobj==me:
		app.printToGUI("You cannot take yourself. ")
		return False
	elif dobj.location != iobj:
		app.printToGUI(dobj.capNameArticle(True) + " is not " + prep + " " + iobj.lowNameArticle(True))
		return False
	elif iobj==me:
		app.printToGUI("You are currently holding " + dobj.lowNameArticle(True) + ". ")
		return True
	if isinstance(iobj, thing.Container):
		if not iobj.is_open:
			app.printToGUI("(First trying to open " + iobj.lowNameArticle(True) + ")")
			success = openVerb.verbFunc(me, app, iobj)
			if not success:
				return False
	if not dobj.invItem:
		print(dobj.cannotTakeMsg)
		return False
	if dobj.parent_obj:
		app.printToGUI(dobj.capNameArticle(True) + " is attached to " + dobj.parent_obj.capNameArticle(True))
		return False
	if dobj.containsItem(me):
		app.printToGUI("You are currently " + dobj.contains_preposition + " " + dobj.lowNameArticle + ", and therefore cannot take it. ")
		return False
	app.printToGUI("You remove " + dobj.lowNameArticle(True) + " from " + iobj.lowNameArticle(True) + ". ")
	iobj.removeThing(dobj)
	me.addThing(dobj)
	if isinstance(dobj, thing.UnderSpace) and not dobj.contains=={}:
		results = dobj.moveContentsOut()
		msg = results[0]
		plural = results[1]
		if plural:
			msg = msg.capitalize() + " are revealed. "
		else:
			msg = msg.capitalize() + " is revealed. "
		app.printToGUI(msg)
		if dobj.is_composite:
			for item in dobj.child_UnderSpaces:
				if not item.contains=={}:
					results = item.moveContentsOut()
					msg = results[0]
					plural = results[1]
					if plural:
						msg = msg.capitalize() + " are revealed. "
					else:
						msg = msg.capitalize() + " is revealed. "
					app.printToGUI(msg)
	return True
removeFromVerb.verbFunc = removeFromVerbFunc

# DROP
# transitive verb, no indirect object
dropVerb = Verb("drop")
dropVerb.addSynonym("put")
dropVerb.syntax = [["drop", "<dobj>"], ["put", "down", "<dobj>"], ["put", "<dobj>", "down"]]
dropVerb.hasDobj = True
dropVerb.dscope = "inv"
dropVerb.preposition = ["down"]

def dropVerbFunc(me, app, dobj, skip=False):
	"""Drop a Thing from the contains
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.dropVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Liquid):
		container = dobj.getContainer()
		if container:
			dobj = container
	if dobj.invItem and me.removeThing(dobj):
		app.printToGUI("You drop " + dobj.getArticle(True) + dobj.verbose_name + ".")
		dobj.location = me.location
		dobj.location.addThing(dobj)
	# if dobj is in sub_contains, remove it
	# set the Thing's location property
	elif dobj.parent_obj:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is attached to " + dobj.parent_obj.getArticle(True) + dobj.parent_obj.verbose_name + ". ")
	elif not dobj.invItem:
		app.printToGUI("Error: not an inventory item. ")
		print(dobj)
	else:
		app.printToGUI("You are not holding " + dobj.getArticle(True) + dobj.verbose_name + ".")
# replace the default verbFunc method
dropVerb.verbFunc = dropVerbFunc

# DROP ALL
# intransitive verb
dropAllVerb = Verb("drop")
dropAllVerb.syntax = [["drop", "all"], ["drop", "everything"]]
dropAllVerb.dscope = "room"
dropAllVerb.hasDobj = False
dropAllVerb.keywords = ["all", "everything"]

def dropAllVerbFunc(me, app):
	"""Drop everything in the inventory
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	inv = list(me.contains.items())
	dropped = 0
	for key, val in inv:
		for item in val:
			if item.ix in me.contains and not item.parent_obj:
				if item in me.contains[item.ix]:
					dropVerb.verbFunc(me, app, item)
					dropped = dropped + 1
	if dropped==0:
		app.printToGUI("Your inventory is empty. ")
		
# replace the default verb function
dropAllVerb.verbFunc = dropAllVerbFunc

# PUT/SET ON
# transitive verb with indirect object
setOnVerb = Verb("set", "set on")
setOnVerb.addSynonym("put")
setOnVerb.addSynonym("drop")
setOnVerb.addSynonym("place")
setOnVerb.syntax = [["put", "<dobj>", "on", "<iobj>"], ["set", "<dobj>", "on", "<iobj>"], ["place", "<dobj>", "on", "<iobj>"], ["drop", "<dobj>", "on", "<iobj>"]]
setOnVerb.hasDobj = True
setOnVerb.dscope = "inv"
setOnVerb.itype = "Surface"
setOnVerb.hasIobj = True
setOnVerb.iscope = "room"
setOnVerb.preposition = ["on"]

def setOnVerbFunc(me, app, dobj, iobj, skip=False):
	"""Put a Thing on a Surface
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if dobj==iobj:
		app.printToGUI("You cannot set something on itself. ")
		return False
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.setOnVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.setOnVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	
	outer_loc = me.getOutermostLocation()
	if iobj==outer_loc.floor:
		if me.removeThing(dobj):	
			app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " on the ground.")
			outer_loc.addThing(dobj)
			return True
		elif dobj.parent_obj:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is attached to " + dobj.parent_obj.getArticle(True) + dobj.parent_obj.verbose_name + ". ")
			return False
		else:
			app.printToGUI("ERROR: cannot remove object from inventory ")
			return False
	if isinstance(iobj, thing.Surface):
		if me.removeThing(dobj):	
			app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " on " + iobj.getArticle(True) + iobj.verbose_name + ".")
			iobj.addThing(dobj)
			return True
		elif dobj.parent_obj:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is attached to " + dobj.parent_obj.getArticle(True) + dobj.parent_obj.verbose_name + ". ")
			return False
		else:
			app.printToGUI("ERROR: cannot remove object from inventory ")
			return False
	# if iobj is not a Surface
	else:
		app.printToGUI("You cannot set anything on that. ")

# replace the default verbFunc method
setOnVerb.verbFunc = setOnVerbFunc

# PUT/SET IN
# transitive verb with indirect object
setInVerb = Verb("set", "set in")
setInVerb.addSynonym("put")
setInVerb.addSynonym("insert")
setInVerb.addSynonym("place")
setInVerb.addSynonym("drop")
setInVerb.syntax = [["put", "<dobj>", "in", "<iobj>"], ["set", "<dobj>", "in", "<iobj>"], ["insert", "<dobj>", "into", "<iobj>"], ["place", "<dobj>", "in", "<iobj>"], ["drop", "<dobj>", "in", "<iobj>"]]
setInVerb.hasDobj = True
setInVerb.dscope = "inv"
setInVerb.itype = "Container"
setInVerb.hasIobj = True
setInVerb.iscope = "near"
setInVerb.preposition = ["in"]

def setInVerbFunc(me, app, dobj, iobj, skip=False):
	"""Put a Thing in a Container
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if iobj==dobj:
		app.printToGUI("You cannot set something in itself. ")
		return False
		
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.setInVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.setInVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if dobj.parent_obj:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is attached to " + dobj.parent_obj.getArticle(True) + dobj.parent_obj.verbose_name + ". ")
		return False
	if isinstance(iobj, thing.Container) and iobj.has_lid:
		if not iobj.is_open:
			app.printToGUI("You cannot put " + dobj.getArticle(True) + dobj.verbose_name + " inside, as " + iobj.getArticle(True) + iobj.verbose_name + " is closed.")
			return False
	if isinstance(iobj, thing.Container) and iobj.size >= dobj.size:
		liquid = iobj.containsLiquid()
		if liquid:
			app.printToGUI("You cannot put " + dobj.getArticle(True) + dobj.verbose_name + " inside, as " + iobj.getArticle(True) + iobj.verbose_name + " has " + liquid.lowNameArticle() + " in it. ")
			return False
		app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " in " + iobj.getArticle(True) + iobj.verbose_name + ".")
		#me.contains.remove(dobj)
		me.removeThing(dobj)
		if iobj.manual_update:
			iobj.addThing(dobj, False, False)
		else:
			iobj.addThing(dobj)
		return True
	elif isinstance(iobj, thing.Container):
		app.printToGUI(dobj.capNameArticle(True) + " is too big to fit inside the " + iobj.verbose_name + ".")
		return False
	else:
		app.printToGUI("There is no way to put it inside the " + iobj.verbose_name + ".")
		return False

# replace the default verbFunc method
setInVerb.verbFunc = setInVerbFunc

# PUT/SET UNDER
# transitive verb with indirect object
setUnderVerb = Verb("set", "set under")
setUnderVerb.addSynonym("put")
setUnderVerb.addSynonym("place")
setUnderVerb.syntax = [["put", "<dobj>", "under", "<iobj>"], ["set", "<dobj>", "under", "<iobj>"], ["place", "<dobj>", "under", "<iobj>"]]
setUnderVerb.hasDobj = True
setUnderVerb.dscope = "inv"
setUnderVerb.hasIobj = True
setUnderVerb.iscope = "room"
setUnderVerb.itype = "UnderSpace"
setUnderVerb.preposition = ["under"]

def setUnderVerbFunc(me, app, dobj, iobj, skip=False):
	"""Put a Thing under an UnderSpace
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if iobj==dobj:
		app.printToGUI("You cannot set something under itself. ")
		return False
	
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.setUnderVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.setUnderVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	outer_loc = me.getOutermostLocation()
	if dobj.parent_obj:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is attached to " + dobj.parent_obj.getArticle(True) + dobj.parent_obj.verbose_name + ". ")
		return False
	if isinstance(iobj, thing.UnderSpace) and dobj.size <= iobj.size:
		app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " " + iobj.contains_preposition + " " + iobj.getArticle(True) + iobj.verbose_name + ".")
		me.removeThing(dobj)
		iobj.addThing(dobj)
		return True
	elif dobj.size > iobj.size:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is too big to fit under " + iobj.getArticle(True) + iobj.verbose_name + ". ")
		return False
	else:
		app.printToGUI("There is no reason to put it under there.")
		return False

# replace the default verbFunc method
setUnderVerb.verbFunc = setUnderVerbFunc

# VIEW INVENTORY
# intransitive verb
invVerb = Verb("inventory")
invVerb.addSynonym("i")
invVerb.syntax = [["inventory"], ["i"]]
invVerb.hasDobj = False

def invVerbFunc(me, app):
	"""View the player's contains
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# describe contains
	if me.contains=={}:
		app.printToGUI("You don't have anything with you.")
	else:
		# the string to print listing the contains
		invdesc = "You have "
		list_version = list(me.contains.keys())
		remove_child = []
		for key in list_version:
			for thing in me.contains[key]:
				if thing.parent_obj:
					#list_version.remove(key)
					remove_child.append(key)
		for key in remove_child:
			if key in list_version:
				list_version.remove(key)
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
				if c[0]==" ":
					c =c[1:-1]
				else:
					c = c[:-1]
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

# VIEW SCORE
# intransitive verb
scoreVerb = Verb("score")
scoreVerb.syntax = [["score"]]
scoreVerb.hasDobj = False

def scoreVerbFunc(me, app):
	"""View the current score
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from . import score
	score.score.score(app)
		
# replace default verbFunc method
scoreVerb.verbFunc = scoreVerbFunc

# VIEW FULL SCORE
# intransitive verb
fullScoreVerb = Verb("fullscore")
fullScoreVerb.addSynonym("full")
fullScoreVerb.syntax = [["fullscore"], ["full", "score"]]
fullScoreVerb.hasDobj = False

def fullScoreVerbFunc(me, app):
	"""View the current score
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from . import score
	score.score.fullscore(app)
		
# replace default verbFunc method
fullScoreVerb.verbFunc = fullScoreVerbFunc

# VIEW ABOUT
# intransitive verb
aboutVerb = Verb("about")
aboutVerb.syntax = [["about"]]
aboutVerb.hasDobj = False

def aboutVerbFunc(me, app):
	"""View the current score
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from .parser import aboutGame
	aboutGame.printAbout(app)
		
# replace default verbFunc method
aboutVerb.verbFunc = aboutVerbFunc

# VIEW HELP
# intransitive verb
helpVerb = Verb("help")
helpVerb.syntax = [["help"]]
helpVerb.hasDobj = False

def helpVerbFunc(me, app):
	"""View the current score
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from .parser import aboutGame
	aboutGame.printHelp(app)
		
# replace default verbFunc method
helpVerb.verbFunc = helpVerbFunc

# VIEW Instructions
# intransitive verb
instructionsVerb = Verb("instructions")
instructionsVerb.syntax = [["instructions"]]
instructionsVerb.hasDobj = False

def instructionVerbFunc(me, app):
	"""View the current score
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from .parser import aboutGame
	aboutGame.printInstructions(app)
		
# replace default verbFunc method
instructionsVerb.verbFunc = instructionVerbFunc

# VIEW VERB LIST
# intransitive verb
verbsVerb = Verb("verbs")
verbsVerb.syntax = [["verbs"]]
verbsVerb.hasDobj = False

def verbsVerbFunc(me, app):
	from .parser import aboutGame
	aboutGame.printVerbs(app)

verbsVerb.verbFunc = verbsVerbFunc

# HELP VERB (Verb)
# transitive verb
helpVerbVerb = Verb("verb", "verb help")
helpVerbVerb.syntax = [["verb", "help", "<dobj>"]]
helpVerbVerb.hasDobj = True
helpVerbVerb.hasStrDobj = True
helpVerbVerb.dtype = "String"

def helpVerbVerbFunc(me, app, dobj):
	"""View the current score
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from .vocab import verbDict
	app.printToGUI("<b>Verb Help: " + " ".join(dobj) + "</b>")
	if dobj[0] in verbDict:
		app.printToGUI("I found the following sentence structures for the verb \"" + dobj[0] + "\":")
		for verb in verbDict[dobj[0]]:
			for form in verb.syntax:
				out = list(form)
				if "<dobj>" in form:
					ix = form.index("<dobj>")
					if verb.dtype=="Actor":
						out[ix] = "(person)"
					elif verb.dscope=="direction":
						out[ix] = "(direction)"
					elif verb.dscope=="text":
						out[ix] = "(word or number)"
					else:
						out[ix] = "(thing)"
				if "<iobj>" in form:
					ix = form.index("<iobj>")
					if verb.itype=="Actor":
						out[ix] = "(person)"
					elif verb.iscope=="direction":
						out[ix] = "(direction)"
					elif verb.iscope=="text":
						out[ix] = "(word or number)"
					else:
						out[ix] = "(thing)"
				out = " ".join(out)
				app.printToGUI(out)
	else:
		app.printToGUI("I found no verb corresponding to the input \"" + " ".join(dobj) + "\". ")
		
# replace default verbFunc method
helpVerbVerb.verbFunc = helpVerbVerbFunc

# VIEW HINT
# intransitive verb
hintVerb = Verb("hint")
hintVerb.syntax = [["hint"]]
hintVerb.hasDobj = False

def hintVerbFunc(me, app):
	"""View the current score
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from .score import hints
	if hints.cur_node:
		if len(hints.cur_node.hints) > 0:
			hints.cur_node.nextHint(app)
			return True
	app.printToGUI("There are no hints currently available. ")
	return False
		
# replace default verbFunc method
hintVerb.verbFunc = hintVerbFunc

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
examineVerb.syntax = [["examine", "<dobj>"], ["x", "<dobj>"], ["look", "at", "<dobj>"], ["look", "<dobj>"]]
examineVerb.hasDobj = True
examineVerb.dscope = "near"
examineVerb.preposition = ["at"]
examineVerb.far_dobj = True

def examineVerbFunc(me, app, dobj, skip=False):
	"""Examine a Thing """
	# print the target's xdesc (examine descripion)
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.examineVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	app.printToGUI(dobj.xdesc)

# replace default verbFunc method
examineVerb.verbFunc = examineVerbFunc

# LOOK THROUGH
# transitive verb, no indirect object
lookThroughVerb = Verb("look")
lookThroughVerb.syntax = [["look", "through", "<dobj>"], ["look", "out", "<dobj>"]]
lookThroughVerb.hasDobj = True
lookThroughVerb.dscope = "near"
lookThroughVerb.preposition = ["through", "out"]
lookThroughVerb.dtype = "Transparent"

def lookThroughVerbFunc(me, app, dobj, skip=False):
	"""look through a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lookThroughVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Transparent):
		dobj.lookThrough(me, app)
		return True
	elif isinstance(dobj, actor.Actor):
		app.printToGUI("You cannot look through a person. ")
		return False
	else:
		app.printToGUI("You cannot look through " + dobj.lowNameArticle(True) + ". ")
		return False

# replace default verbFunc method
lookThroughVerb.verbFunc = lookThroughVerbFunc


# LOOK IN 
# transitive verb, no indirect object
lookInVerb = Verb("look", "look in")
lookInVerb.syntax = [["look", "in", "<dobj>"]]
lookInVerb.hasDobj = True
lookInVerb.dscope = "near"
lookInVerb.dtype = "Container"
lookInVerb.preposition = ["in"]

def lookInVerbFunc(me, app, dobj, skip=False):
	"""Look inside a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lookInVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Container):
		list_version = list(dobj.contains.keys())
		if dobj.has_lid:
			if not dobj.is_open:
				app.printToGUI("You cannot see inside " + dobj.getArticle(True) + dobj.verbose_name + " as it is closed.")
				return False
		if len(list_version) > 0:
			app.printToGUI(dobj.contains_desc)
			for key in dobj.contains:
				if key not in me.knows_about:
					me.knows_about.append(key)
			return True
		else:
			app.printToGUI(dobj.capNameArticle(True) + " is empty.")
			return True
	else:
		app.printToGUI("You cannot look inside " + dobj.getArticle(True) + dobj.verbose_name + ".")
		return False

lookInVerb.verbFunc = lookInVerbFunc

# LOOK UNDER 
# transitive verb, no indirect object
lookUnderVerb = Verb("look", "look under")
lookUnderVerb.syntax = [["look", "under", "<dobj>"]]
lookUnderVerb.hasDobj = True
lookUnderVerb.dscope = "near"
lookUnderVerb.dtype = "UnderSpace"
lookUnderVerb.preposition = ["under"]

def lookUnderVerbFunc(me, app, dobj, skip=False):
	"""Look under a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lookUnderVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.UnderSpace):
		dobj.revealUnder()
		list_version = list(dobj.contains.keys())
		if len(list_version) > 0:
			app.printToGUI(dobj.contains_desc)
			return True
		else:
			app.printToGUI("There is nothing " + dobj.contains_preposition + " " + dobj.getArticle(True) + dobj.verbose_name + ".")
			return True
	elif dobj.invItem:
		getVerbFunc(me, app, dobj)
		app.printToGUI("You find nothing underneath. ")
		return False
	else:
		app.printToGUI("There's no reason to look under " + dobj.getArticle(True) + dobj.verbose_name + ".")
		return False

lookUnderVerb.verbFunc = lookUnderVerbFunc

# READ
# transitive verb, no indirect object
readVerb = Verb("read")
readVerb.syntax = [["read", "<dobj>"]]
readVerb.hasDobj = True
readVerb.dscope = "near"
readVerb.dtype = "Readable"

def readVerbFunc(me, app, dobj, skip=False):
	"""look through a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.readVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Book):
		if not dobj.is_open:
			openVerb.verbFunc(me, app, dobj)
		dobj.readText(me, app)
	elif isinstance(dobj, thing.Readable):
		dobj.readText(me, app)
		return True
	else:
		app.printToGUI("There's nothing written there. ")
		return False

# replace default verbFunc method
readVerb.verbFunc = readVerbFunc

# TALK TO (Actor)
# transitive verb with indirect object
# implicit direct object enabled
talkToVerb = Verb("talk", "talk to")
talkToVerb.addSynonym("greet")
talkToVerb.addSynonym("say")
talkToVerb.addSynonym("hi")
talkToVerb.addSynonym("hello")
talkToVerb.syntax = [["talk", "to", "<dobj>"], ["talk", "with", "<dobj>"], ["talk", "<dobj>"], ["greet", "<dobj>"], ["hi", "<dobj>"], ["hello", "<dobj>"], ["say", "hi", "<dobj>"], ["say", "hi", "to", "<dobj>"], ["say", "hello", "<dobj>"], ["say", "hello", "to", "<dobj>"]]
talkToVerb.hasDobj = True
talkToVerb.impDobj = True
talkToVerb.preposition = ["to", "with"]
talkToVerb.dtype = "Actor"

def getImpTalkTo(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	# find every Actor in the current location
	loc = me.getOutermostLocation()
	for key, items in loc.contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
	if len(people)==0:
		app.printToGUI("There's no one obvious to talk to here.")
	elif len(people)==1:
		# ask the only actor in the room
		if not people[0].ignore_if_ambiguous:
			return people[0]
		app.printToGUI("There's no one obvious to talk to here.")
	elif isinstance(parser.lastTurn.dobj, actor.Actor) and not parser.lastTurn.dobj.ignore_if_ambiguous  and loc.containsItem(parser.lastTurn.dobj):
		# ask whomever the player last interracted with
		return parser.lastTurn.dobj
	else:
		people2 = list(people)
		for p in people:
			if p.ignore_if_ambiguous:
				people2.remove(p)
		if len(people2)==1:
			return people2[0]
		# turn disambiguation mode on
		app.printToGUI("Please specify a person to talk to. ")
		parser.lastTurn.ambiguous = True

# replace default getImpDobj method
talkToVerb.getImpDobj = getImpTalkTo

def talkToVerbFunc(me, app, dobj, skip=False):
	"""Talk to an Actor
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	from .thing import reflexive
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.talkToVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = dobj.talkToVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, actor.Actor):
		if dobj.hermit_topic:
			dobj.hermit_topic.func(app, False)
		elif dobj.sticky_topic:
			dobj.sticky_topic.func(app)
		elif dobj.hi_topic and not dobj.said_hi:
			dobj.hi_topic.func(app)
			dobj.said_hi = True
		elif dobj.return_hi_topic:
			dobj.return_hi_topic.func(app)
		else:
			dobj.defaultTopic(app)
	else:
		app.printToGUI("You cannot talk to that.")

# replace default verbFunc method
talkToVerb.verbFunc = talkToVerbFunc

# ASK (Actor)
# transitive verb with indirect object
# implicit direct object enabled
askVerb = Verb("ask", "ask about")
askVerb.syntax = [["ask", "<dobj>", "about", "<iobj>"]]
askVerb.hasDobj = True
askVerb.hasIobj = True
askVerb.iscope = "knows"
askVerb.impDobj = True
askVerb.preposition = ["about"]
askVerb.dtype = "Actor"

def getImpAsk(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	loc = me.getOutermostLocation()
	# find every Actor in the current location
	for key, items in loc.contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
	if len(people)==0:
		app.printToGUI("There's no one obvious here to ask.")
	elif len(people)==1:
		# ask the only actor in the room
		if not people[0].ignore_if_ambiguous:
			return people[0]
		app.printToGUI("There's no one obvious here to ask.")
	elif isinstance(parser.lastTurn.dobj, actor.Actor)  and not parser.lastTurn.dobj.ignore_if_ambiguous  and loc.containsItem(parser.lastTurn.dobj):
		# ask whomever the player last interracted with
		return parser.lastTurn.dobj
	else:
		people2 = list(people)
		for p in people:
			if p.ignore_if_ambiguous:
				people2.remove(p)
		if len(people2)==1:
			return people2[0]
		app.printToGUI("Please specify a person to ask.")
		# turn disambiguation mode on
		parser.lastTurn.ambiguous = True

# replace the default getImpDobj method
askVerb.getImpDobj = getImpAsk

def askVerbFunc(me, app, dobj, iobj, skip=False):
	"""Ask an Actor about a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	from .thing import reflexive
	if isinstance(dobj, actor.Actor):
		if dobj.hermit_topic:
			dobj.hermit_topic.func(app, False)
			return True
			
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.askVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.askVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, actor.Actor):
		# try to find the ask topic for iobj
		if dobj.hi_topic and not dobj.said_hi:
			dobj.hi_topic.func(app, False)
			dobj.said_hi = True
		if iobj==reflexive:	
			iobj = dobj
		if iobj.ix in dobj.ask_topics:
			# call the ask function for iobj
			if dobj.sticky_topic:
				dobj.ask_topics[iobj.ix].func(app, False)
				dobj.sticky_topic.func(app)
			else:
				dobj.ask_topics[iobj.ix].func(app)
		elif dobj.sticky_topic:
			dobj.defaultTopic(app, False)
			dobj.sticky_topic.func(app)
		else:
			dobj.defaultTopic(app)
	else:
		app.printToGUI("You cannot talk to that.")

# replace the default verbFunc method
askVerb.verbFunc = askVerbFunc

# TELL (Actor)
# transitive verb with indirect object
# implicit direct object enabled
tellVerb = Verb("tell", "tell about")
tellVerb.syntax = [["tell", "<dobj>", "about", "<iobj>"]]
tellVerb.hasDobj = True
tellVerb.hasIobj = True
tellVerb.iscope = "knows"
tellVerb.impDobj = True
tellVerb.preposition = ["about"]
tellVerb.dtype = "Actor"

def getImpTell(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	loc = me.getOutermostLocation()
	# find every Actor in the current location
	for key, items in loc.contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
	if len(people)==0:
		app.printToGUI("There's no one obvious here to tell.")
	elif len(people)==1:
		# ask the only actor in the room
		if not people[0].ignore_if_ambiguous:
			return people[0]
		app.printToGUI("There's no one obvious here to tell.")
	elif isinstance(parser.lastTurn.dobj, actor.Actor) and not parser.lastTurn.dobj.ignore_if_ambiguous  and loc.containsItem(parser.lastTurn.dobj):
		# ask whomever the player last interracted with
		return parser.lastTurn.dobj
	else:
		people2 = list(people)
		for p in people:
			if p.ignore_if_ambiguous:
				people2.remove(p)
		if len(people2)==1:
			return people2[0]
		# turn disambiguation mode on
		app.printToGUI("Please specify a person to ask.")
		parser.lastTurn.ambiguous = True

# replace default getImpDobj method
tellVerb.getImpDobj = getImpTell

def tellVerbFunc(me, app, dobj, iobj, skip=False):
	"""Tell an Actor about a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	from .thing import reflexive
	if isinstance(dobj, actor.Actor):
		if dobj.hermit_topic:
			dobj.hermit_topic.func(app, False)
			return True
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.tellVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = dobj.tellVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, actor.Actor):
		if dobj.hi_topic and not dobj.said_hi:
			dobj.hi_topic.func(app, False)
			dobj.said_hi = True
		if iobj==reflexive:	
				iobj = dobj
		if iobj.ix in dobj.tell_topics:
			if dobj.sticky_topic:
				dobj.tell_topics[iobj.ix].func(app, False)
				dobj.sticky_topic.func(app)
			else:
				dobj.tell_topics[iobj.ix].func(app)
		elif dobj.sticky_topic:
			dobj.defaultTopic(app, False)
			dobj.sticky_topic.func(app)
		else:
			dobj.defaultTopic(app)
	else:
		app.printToGUI("You cannot talk to that.")

# replace default verbFunc method
tellVerb.verbFunc = tellVerbFunc

# GIVE (Actor)
# transitive verb with indirect object
# implicit direct object enabled
giveVerb = Verb("give", "give to")
giveVerb.syntax = [["give", "<iobj>", "to", "<dobj>"], ["give", "<dobj>", "<iobj>"]]
giveVerb.hasDobj = True
giveVerb.hasIobj = True
giveVerb.iscope = "invflex"
giveVerb.impDobj = True
giveVerb.preposition = ["to"]
giveVerb.dtype = "Actor"

def getImpGive(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	loc = me.getOutermostLocation()
	# find every Actor in the current location
	for key, items in loc.contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
	if len(people)==0:
		app.printToGUI("There's no one obvious here to give it to.")
	elif len(people)==1:
		# ask the only actor in the room
		if not people[0].ignore_if_ambiguous:
			return people[0]
		app.printToGUI("There's no one obvious here to give it to.")
	elif isinstance(parser.lastTurn.dobj, actor.Actor)  and not parser.lastTurn.dobj.ignore_if_ambiguous  and loc.containsItem(parser.lastTurn.dobj):
		# ask whomever the player last interracted with
		return parser.lastTurn.dobj
	else:
		people2 = list(people)
		for p in people:
			if p.ignore_if_ambiguous:
				people2.remove(p)
		if len(people2)==1:
			return people2[0]
		# turn disambiguation mode on
		app.printToGUI("Please specify a person to give it to.")
		parser.lastTurn.ambiguous = True

# replace default getImpDobj method
giveVerb.getImpDobj = getImpGive

def giveVerbFunc(me, app, dobj, iobj, skip=False):
	"""Give an Actor a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.giveVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.giveVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, actor.Actor):
		if dobj.hermit_topic:
			dobj.hermit_topic.func(app, False)
			return True
	if iobj is me:
		app.printToGUI("You cannot give yourself away. ")
		return False
	elif isinstance(iobj, actor.Actor):
		app.printToGUI("You cannot give a person away. ")
		return False
	if isinstance(dobj, actor.Actor):
		if dobj.hi_topic and not dobj.said_hi:
			dobj.hi_topic.func(app, False)
			dobj.said_hi = True
		if iobj.ix in dobj.give_topics:
			if dobj.sticky_topic:
				dobj.give_topics[iobj.ix].func(app, False)
				dobj.sticky_topic.func(app)	
			else:
				dobj.give_topics[iobj.ix].func(app)
			if iobj.give:
				me.removeThing(dobj)
				dobj.addThing(iobj)
			return True
		elif dobj.sticky_topic:
			dobj.defaultTopic(app, False)
			dobj.sticky_topic.func(app)	
		else:
			dobj.defaultTopic(app)
			return True
	else:
		app.printToGUI("You cannot talk to that.")

# replace default verbFunc method
giveVerb.verbFunc = giveVerbFunc

# SHOW (Actor)
# transitive verb with indirect object
# implicit direct object enabled
showVerb = Verb("show", "show to")
showVerb.syntax = [["show", "<iobj>", "to", "<dobj>"], ["show", "<dobj>", "<iobj>"]]
showVerb.hasDobj = True
showVerb.hasIobj = True
showVerb.iscope = "invflex"
showVerb.impDobj = True
showVerb.preposition = ["to"]
showVerb.dtype = "Actor"

def getImpShow(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	loc = me.getOutermostLocation()
	# find every Actor in the current location
	for key, items in loc.contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
	if len(people)==0:
		app.printToGUI("There's no one obvious here to show.")
	elif len(people)==1:
		# ask the only actor in the room
		if not people[0].ignore_if_ambiguous:
			return people[0]
		app.printToGUI("There's no one obvious here to show.")
	elif isinstance(parser.lastTurn.dobj, actor.Actor)  and not parser.lastTurn.dobj.ignore_if_ambiguous and loc.containsItem(parser.lastTurn.dobj):
		# ask whomever the player last interracted with
		return parser.lastTurn.dobj
	else:
		people2 = list(people)
		for p in people:
			if p.ignore_if_ambiguous:
				people2.remove(p)
		if len(people2)==1:
			return people2[0]
		# turn disambiguation mode on
		app.printToGUI("Please specify a person to show.")
		parser.lastTurn.ambiguous = True

# replace default getImpDobj method
showVerb.getImpDobj = getImpShow

def showVerbFunc(me, app, dobj, iobj, skip=False):
	"""Show an Actor a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if isinstance(dobj, actor.Actor):
		if dobj.hermit_topic:
			dobj.hermit_topic.func(app, False)
			return True
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.showVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.showVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, actor.Actor):
		if dobj.hi_topic and not dobj.said_hi:
			dobj.hi_topic.func(app, False)
			dobj.said_hi = True
		if iobj.ix in dobj.show_topics:
			if dobj.sticky_topic:
				dobj.show_topics[iobj.ix].func(app, False)
				dobj.sticky_topic.func(app)
			else:
				dobj.show_topics[iobj.ix].func(app)
		elif dobj.sticky_topic:
			dobj.defaultTopic(app, False)
			dobj.sticky_topic.func(app)
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
wearVerb.dtype = "Clothing"
wearVerb.dscope = "inv"
wearVerb.preposition = ["on"]

def wearVerbFunc(me, app, dobj, skip=False):
	"""Wear a piece of clothing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.wearVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
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

def doffVerbFunc(me, app, dobj, skip=False):
	"""Take off a piece of clothing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.doffVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	
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
				app.printToGUI("(First getting " + me.location.contains_preposition_inverse + " of " + me.location.getArticle(True) + me.location.verbose_name + ")")
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
standUpVerb.addSynonym("get")
standUpVerb.syntax = [["stand", "up"], ["stand"], ["get", "up"]]
standUpVerb.preposition = ["up"]

def standUpVerbFunc(me, app):
	"""Take off a piece of clothing
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app"""
	if me.position != "standing":
		if isinstance(me.location, thing.Thing):
			if not me.location.canStand:
				app.printToGUI("(First getting " + me.location.contains_preposition_inverse + " of " + me.location.getArticle(True) + me.location.verbose_name + ")")
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
				app.printToGUI("(First getting " + me.location.contains_preposition_inverse + " of " + me.location.getArticle(True) + me.location.verbose_name + ")")
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
standOnVerb = Verb("stand", "stand on")
standOnVerb.syntax = [["stand", "on", "<dobj>"]]
standOnVerb.hasDobj = True
standOnVerb.dscope = "room"
standOnVerb.dtype = "Surface"
standOnVerb.preposition = ["on"]

def standOnVerbFunc(me, app, dobj, skip=False):
	"""Sit on a Surface where canSit is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.standOnVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
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
		dobj.addThing(me)
		me.makeStanding()
	else:
		app.printToGUI("You cannot stand on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return False

# replace default verbFunc method
standOnVerb.verbFunc = standOnVerbFunc

# SIT ON (SURFACE)
# transitive verb, no indirect object
sitOnVerb = Verb("sit", "sit on")
sitOnVerb.syntax = [["sit", "on", "<dobj>"], ["sit", "down", "on", "<dobj>"]]
sitOnVerb.hasDobj = True
sitOnVerb.dscope = "room"
sitOnVerb.dtype = "Surface"
sitOnVerb.preposition = ["down", "on"]

def sitOnVerbFunc(me, app, dobj, skip=False):
	"""Stand on a Surface where canStand is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.sitOnVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
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
		dobj.addThing(me)
		me.makeSitting()
	else:
		app.printToGUI("You cannot sit on " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
sitOnVerb.verbFunc = sitOnVerbFunc

# LIE ON (SURFACE)
# transitive verb, no indirect object
lieOnVerb = Verb("lie", "lie on")
lieOnVerb.addSynonym("lay")
lieOnVerb.syntax = [["lie", "on", "<dobj>"], ["lie", "down", "on", "<dobj>"], ["lay", "on", "<dobj>"], ["lay", "down", "on", "<dobj>"]]
lieOnVerb.hasDobj = True
lieOnVerb.dscope = "room"
lieOnVerb.dtype = "Surface"
lieOnVerb.preposition = ["down", "on"]

def lieOnVerbFunc(me, app, dobj):
	"""Lie on a Surface where canLie is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	runfunc = True
	try:
		runfunc = dobj.lieOnVerbDobj(me, app)
	except AttributeError:
		pass
	if not runfunc:
		return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
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
		dobj.addThing(me)
		me.makeLying()
		return  True
	else:
		app.printToGUI("You cannot lie on " + dobj.getArticle(True) + dobj.verbose_name  + ".")

# replace default verbFunc method
lieOnVerb.verbFunc = lieOnVerbFunc

# SIT IN (CONTAINER)
# transitive verb, no indirect object
sitInVerb = Verb("sit", "sit in")
sitInVerb.syntax = [["sit", "in", "<dobj>"], ["sit", "down", "in", "<dobj>"]]
sitInVerb.hasDobj = True
sitInVerb.dscope = "room"
sitInVerb.dtype = "Container"
sitInVerb.preposition = ["down", "in"]

# when the Chair subclass of Surface is implemented, redirect to sit on if dobj is a Chair
def sitInVerbFunc(me, app, dobj, skip=False):
	"""Stand on a Surface where canStand is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.sitInVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if me.location==dobj and me.position=="sitting" and isinstance(dobj, thing.Container):
		app.printToGUI("You are already sitting in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return True
	elif isinstance(dobj, thing.Container) and dobj.canSit:
		app.printToGUI("You sit in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addThing(me)
		me.makeSitting()
	else:
		app.printToGUI("You cannot sit in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return False

# replace default verbFunc method
sitInVerb.verbFunc = sitInVerbFunc

# STAND IN (CONTAINER)
# transitive verb, no indirect object
standInVerb = Verb("stand", "stand in")
standInVerb.syntax = [["stand", "in", "<dobj>"]]
standInVerb.hasDobj = True
standInVerb.dscope = "room"
standInVerb.dtype = "Container"
standInVerb.preposition = ["in"]

def standInVerbFunc(me, app, dobj, skip=False):
	"""Sit on a Surface where canSit is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.standInVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if me.location==dobj and me.position=="standing" and isinstance(dobj, thing.Container):
		app.printToGUI("You are already standing in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return True
	elif isinstance(dobj, thing.Container) and dobj.canStand:
		app.printToGUI("You stand in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addThing(me)
		me.makeStanding()
		return True
	else:
		app.printToGUI("You cannot stand in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return False

# replace default verbFunc method
standInVerb.verbFunc = standInVerbFunc

# LIE IN (CONTAINER)
# transitive verb, no indirect object
lieInVerb = Verb("lie", "lie in")
lieInVerb.addSynonym("lay")
lieInVerb.syntax = [["lie", "in", "<dobj>"], ["lie", "down", "in", "<dobj>"], ["lay", "in", "<dobj>"], ["lay", "down", "in", "<dobj>"]]
lieInVerb.hasDobj = True
lieInVerb.dscope = "room"
lieInVerb.dtype = "Container"
lieInVerb.preposition = ["down", "in"]

def lieInVerbFunc(me, app, dobj, skip=False):
	"""Lie on a Surface where canLie is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lieInVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if me.location==dobj and me.position=="lying" and isinstance(dobj, thing.Container):
		app.printToGUI("You are already lying in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return True
	elif isinstance(dobj, thing.Container) and dobj.canLie:
		app.printToGUI("You lie in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addThing(me)
		me.makeLying()
		return True
	else:
		app.printToGUI("You cannot lie in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return False

# replace default verbFunc method
lieInVerb.verbFunc = lieInVerbFunc

# CLIMB ON (SURFACE)
# transitive verb, no indirect object
climbOnVerb = Verb("climb", "climb on")
climbOnVerb.addSynonym("get")
climbOnVerb.syntax = [["climb", "on", "<dobj>"], ["get", "on", "<dobj>"], ["climb", "<dobj>"], ["climb", "up", "<dobj>"]]
climbOnVerb.hasDobj = True
climbOnVerb.dscope = "room"
climbOnVerb.dtype = "Surface"
climbOnVerb.dobj_direction = "u"
climbOnVerb.preposition = ["on", "up"]

def climbOnVerbFunc(me, app, dobj, skip=False):
	"""Climb on a Surface where one of more of canStand/canSit/canLie is True
	Will be extended once stairs/ladders are implemented
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.climbOnVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if dobj.connection:
		if dobj.direction=="u":
			dobj.connection.travel(me, app)
		else:
			app.printToGUI("You can't climb up that.")
			return False
	elif isinstance(dobj, thing.Surface) and dobj.canStand:
		standOnVerb.verbFunc(me, app, dobj)
		return True
	elif isinstance(dobj, thing.Surface) and dobj.canSit:
		sitOnVerb.verbFunc(me, app, dobj)
		return True
	elif isinstance(dobj, thing.Surface) and dobj.canLie:
		lieOnVerb.verbFunc(me, app, dobj)
		return True
	else:
		app.printToGUI("You cannot climb on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return False

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
climbDownVerb = Verb("climb", "climb down")
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
		outer_loc.addThing(me)
	else:
		app.printToGUI("You cannot climb down from here. ")

# replace default verbFunc method
climbDownVerb.verbFunc = climbDownVerbFunc

# CLIMB DOWN FROM (SURFACE)
# transitive verb, no indirect object
climbDownFromVerb = Verb("climb", "climb down from")
climbDownFromVerb.addSynonym("get")
climbDownFromVerb.syntax = [["climb", "off", "<dobj>"], ["get", "off", "<dobj>"], ["climb", "down", "from", "<dobj>"], ["get", "down", "from", "<dobj>"], ["climb", "down", "<dobj>"]]
climbDownFromVerb.hasDobj = True
climbDownFromVerb.dscope = "room"
climbDownFromVerb.preposition = ["off", "down", "from"]
climbDownFromVerb.dobj_direction = "d"

def climbDownFromVerbFunc(me, app, dobj, skip=False):
	"""Climb down from a Surface you currently occupy
	Will be extended once stairs/ladders/up direction/down direction are implemented
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.climbDownFromVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if dobj.connection:
		if dobj.direction=="d":
			dobj.connection.travel(me, app)
			return True
		else:
			app.printToGUI("You can't climb down from that.")
			return False
	elif me.location==dobj:
		if isinstance(me.location, thing.Surface):
			app.printToGUI("You climb down from " + me.location.getArticle(True) + me.location.verbose_name  + ".")
			outer_loc = me.location.location
			me.location.removeThing(me)
			outer_loc.addThing(me) 
		else:
			app.printToGUI("You cannot climb down from here. ")
			return False
	else:
		app.printToGUI("You are not on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return False

# replace default verbFunc method
climbDownFromVerb.verbFunc = climbDownFromVerbFunc

# GO THROUGH (CONNECTOR INTERACTABLE not derived from AbstractClimbable)
# transitive
goThroughVerb = Verb("go", "go through")
goThroughVerb.syntax = [["go", "through", "<dobj>"]]
goThroughVerb.hasDobj = True
goThroughVerb.dscope = "room"
goThroughVerb.preposition = ["through"]

def goThroughVerbFunc(me, app, dobj, skip=False):
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.AbstractClimbable):
		app.printToGUI("You cannot go through " + dobj.lowNameArticle(True) + ". ")
		return False
	elif dobj.connection:
		return dobj.connection.travel(me, app)
	else:
		app.printToGUI("You cannot go through " + dobj.lowNameArticle(True) + ". ")
		return False
goThroughVerb.verbFunc = goThroughVerbFunc

# CLIMB IN (CONTAINER)
# transitive verb, no indirect object
climbInVerb = Verb("climb", "climb in")
climbInVerb.addSynonym("get")
climbInVerb.addSynonym("enter")
climbInVerb.addSynonym("go")
climbInVerb.syntax = [["climb", "in", "<dobj>"], ["get", "in", "<dobj>"], ["climb", "into", "<dobj>"], ["get", "into", "<dobj>"], ["enter", "<dobj>"], ["go", "in", "<dobj>"], ["go", "into", "<dobj>"]]
climbInVerb.hasDobj = True
climbInVerb.dscope = "room"
climbInVerb.preposition = ["in", "into"]

def climbInVerbFunc(me, app, dobj, skip=False):
	"""Climb in a Container where one of more of canStand/canSit/canLie is True
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.climbInVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if dobj.connection:
		dobj.connection.travel(me, app)
		return True
	if isinstance(dobj, thing.Container) and dobj.canStand:
		if dobj.has_lid:
			if not dobj.is_open:
				app.printToGUI("You cannot climb into " + dobj.getArticle(True) + dobj.verbose_name  + ", since it is closed.")
				return False
		standInVerb.verbFunc(me, app, dobj)
		return True
	elif isinstance(dobj, thing.Container) and dobj.canSit:
		if dobj.has_lid:
			if not dobj.is_open:
				app.printToGUI("You cannot climb into " + dobj.getArticle(True) + dobj.verbose_name  + ", since it is closed.")
				return False
		sitInVerb.verbFunc(me, app, dobj)
		return True
	elif isinstance(dobj, thing.Container) and dobj.canLie:
		if dobj.has_lid:
			if not dobj.is_open:
				app.printToGUI("You cannot climb into " + dobj.getArticle(True) + dobj.verbose_name  + ", since it is closed.")
				return False
		lieInVerb.verbFunc(me, app, dobj)
		return True
	else:
		app.printToGUI("You cannot climb into " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return False

# replace default verbFunc method
climbInVerb.verbFunc = climbInVerbFunc

# CLIMB OUT (INTRANSITIVE)
# intransitive verb
climbOutVerb = Verb("climb", "climb out")
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
		outer_loc.addThing(me) 
	else:
		app.printToGUI("You cannot climb out of here. ")

# replace default verbFunc method
climbOutVerb.verbFunc = climbOutVerbFunc

# CLIMB OUT OF (CONTAINER)
# transitive verb, no indirect object
climbOutOfVerb = Verb("climb", "climb out of")
climbOutOfVerb.addSynonym("get")
climbOutOfVerb.addSynonym("exit")
climbOutOfVerb.syntax = [["climb", "out", "of", "<dobj>"], ["get", "out", "of", "<dobj>"], ["exit", "<dobj>"]]
climbOutOfVerb.hasDobj = True
climbOutOfVerb.dscope = "room"
climbOutOfVerb.preposition = ["out", "of"]

def climbOutOfVerbFunc(me, app, dobj, skip=False):
	"""Climb down from a Surface you currently occupy
	Will be extended once stairs/ladders/up direction/down direction are implemented
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.climbOutOfVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	
	if me.location==dobj:
		if isinstance(me.location, thing.Container):
			app.printToGUI("You climb out of " + me.location.getArticle(True) + me.location.verbose_name  + ".")
			outer_loc = me.location.location
			me.location.removeThing(me)
			outer_loc.addThing(me)
			return True
		else:
			app.printToGUI("You cannot climb out of here. ")
			return False
	else:
		app.printToGUI("You are not in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return False

# replace default verbFunc method
climbOutOfVerb.verbFunc = climbOutOfVerbFunc

# OPEN 
# transitive verb, no indirect object
openVerb = Verb("open")
openVerb.syntax = [["open", "<dobj>"]]
openVerb.hasDobj = True
openVerb.dscope = "near"

def openVerbFunc(me, app, dobj, skip=False):
	"""Open a Thing with an open property
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	try:
		lock = dobj.lock_obj
	except:
		lock = None
	if lock:
		if dobj.lock_obj.is_locked:
			try:
				app.printToGUI(dobj.cannotOpenLockedMsg)
			except:
				app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is locked. ")
			return False
	runfunc = True
	
	if not skip:
		try:
			runfunc = dobj.openVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	try:
		state = dobj.is_open
	except AttributeError:
		app.printToGUI("You cannot open " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		return False
	if state==False:
		app.printToGUI("You open " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		dobj.makeOpen()
		if isinstance(dobj, thing.Container):
			lookInVerb.verbFunc(me, app, dobj)
		return True
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already open. ")
	return True
	
# replace default verbFunc method
openVerb.verbFunc = openVerbFunc

# CLOSE 
# transitive verb, no indirect object
closeVerb = Verb("close")
closeVerb.addSynonym("shut")
closeVerb.syntax = [["close", "<dobj>"], ["shut","<dobj>"]]
closeVerb.hasDobj = True
closeVerb.dscope = "near"

def closeVerbFunc(me, app, dobj, skip=False):
	"""Open a Thing with an open property
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing """
	
	if isinstance(dobj, thing.Container):
		if dobj.has_lid:
			if me.ix in dobj.contains or me.ix in dobj.sub_contains:
				app.printToGUI("You cannot close " + dobj.getArticle(True) + dobj.verbose_name + " while you are inside it. ")
				return False
	
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.closeVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	try:
		state = dobj.is_open
	except AttributeError:
		app.printToGUI("You cannot close " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		return False
	if state==True:
		app.printToGUI("You close " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		dobj.makeClosed()
		return True
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already closed. ")
	return True
	
# replace default verbFunc method
closeVerb.verbFunc = closeVerbFunc

# EXIT (INTRANSITIVE)
# intransitive verb
exitVerb = Verb("exit")
exitVerb.syntax = [["exit"]]

def exitVerbFunc(me, app):
	"""Climb out of a Container you currently occupy
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from . import travel
	out_loc = me.getOutermostLocation()
	if isinstance(me.location, thing.Thing):
		climbOutOfVerb.verbFunc(me, app, me.location)
	elif out_loc.exit:
		travel.travelOut(me, app)
	else:
		app.printToGUI("There is no obvious exit. ")

# replace default verbFunc method
exitVerb.verbFunc = exitVerbFunc

# ENTER (INTRANSITIVE)
# intransitive verb
enterVerb = Verb("enter")
enterVerb.syntax = [["enter"]]

def enterVerbFunc(me, app):
	"""Climb out of a Container you currently occupy
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	from . import travel
	out_loc = me.getOutermostLocation()
	if out_loc.entrance:
		travel.travelIn(me, app)
	else:
		app.printToGUI("There is no obvious entrance. ")

# replace default verbFunc method
enterVerb.verbFunc = enterVerbFunc

# UNLOCK 
# transitive verb, no indirect object
unlockVerb = Verb("unlock")
unlockVerb.addSynonym("unbolt")
unlockVerb.syntax = [["unlock", "<dobj>"], ["unbolt", "<dobj>"]]
unlockVerb.hasDobj = True
unlockVerb.dscope = "near"

def unlockVerbFunc(me, app, dobj, skip=False):
	"""Unlock a Door or Container with an lock
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing
	Returns True when the function ends with dobj unlocked, or without a lock. Returns False on failure to unlock. """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.unlockVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Container) or isinstance(dobj, thing.Door):
		if dobj.lock_obj:
			if dobj.lock_obj.is_locked:
				if dobj.lock_obj.key_obj:
					if me.containsItem(dobj.lock_obj.key_obj):
						app.printToGUI("(Using " + dobj.lock_obj.key_obj.getArticle(True) + dobj.lock_obj.key_obj.verbose_name + ")")
						if dobj.lock_obj.key_obj.location != me:
							app.printToGUI("(First removing " + dobj.lock_obj.key_obj.lowNameArticle(True) + " from " + dobj.lock_obj.key_obj.location.lowNameArticle(True) + ".)")
							#dobj.lock_obj.key_obj.location.removeThing(dobj.lock_obj.key_obj)
							#me.addThing(dobj.lock_obj.key_obj)
							removeFromVerb.verbFunc(me, app, dobj.lock_obj.key_obj, dobj.lock_obj.key_obj.location)
						app.printToGUI("You unlock " + dobj.getArticle(True) + dobj.verbose_name + ". ")
						dobj.lock_obj.makeUnlocked()
						return True
					else:
						app.printToGUI("You do not have the correct key. ")
						return False
				else:
					app.printToGUI("You do not have the correct key. ")
					return False
			else:
				app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already unlocked. ")
				return True
		else:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " does not have a lock. ")
			return True
	elif isinstance(dobj, thing.Lock):
		if dobj.is_locked:
			if dobj.key_obj:
				if me.containsItem(dobj.key_obj):
					app.printToGUI("(Using " + dobj.key_obj.getArticle(True) + dobj.key_obj.verbose_name + ")")
					if dobj.key_obj.location != me:
						app.printToGUI("(First removing " + dobj.key_obj.lowNameArticle(True) + " from " + dobj.key_obj.location.lowNameArticle(True) + ".)")
						#dobj.key_obj.location.removeThing(dobj.key_obj)
						#me.addThing(dobj.key_obj)
						removeFromVerb.verbFunc(me, app, dobj.key_obj, dobj.key_obj.location)
					app.printToGUI("You unlock " + dobj.getArticle(True) + dobj.verbose_name + ". ")
					dobj.makeUnlocked()
					return True
				else:
					app.printToGUI("You do not have the correct key. ")
					return False
			else:
				app.printToGUI("You do not have the correct key. ")
				return False
		else:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already unlocked. ")
			return True
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " does not have a lock. ")
		return True
	
# replace default verbFunc method
unlockVerb.verbFunc = unlockVerbFunc

# LOCK 
# transitive verb, no indirect object
lockVerb = Verb("lock")
lockVerb.addSynonym("bolt")
lockVerb.syntax = [["lock", "<dobj>"], ["bolt", "<dobj>"]]
lockVerb.hasDobj = True
lockVerb.dscope = "near"

def lockVerbFunc(me, app, dobj, skip=False):
	"""Lock a Door or Container with an lock
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing
	Returns True when the function ends with dobj locked. Returns False on failure to lock, or when dobj has no lock. """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lockVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Container) or isinstance(dobj, thing.Door):
		if dobj.is_open:
			if not closeVerb.verbFunc(me, app, dobj):
				app.printToGUI("Could not close " + dobj.verbose_name + ". ")
				return False
		if dobj.lock_obj:
			if not dobj.lock_obj.is_locked:
				if dobj.lock_obj.key_obj:
					if me.containsItem(dobj.lock_obj.key_obj):
						app.printToGUI("(Using " + dobj.lock_obj.key_obj.getArticle(True) + dobj.lock_obj.key_obj.verbose_name + ")")
						if dobj.lock_obj.key_obj.location != me:
							app.printToGUI("(First removing " + dobj.lock_obj.key_obj.lowNameArticle(True) + " from " + dobj.lock_obj.key_obj.location.lowNameArticle(True) + ".)")
							#dobj.lock_obj.key_obj.location.removeThing(dobj.lock_obj.key_obj)
							#me.addThing(dobj.lock_obj.key_obj)
							removeFromVerb.verbFunc(me, app, dobj.lock_obj.key_obj, dobj.lock_obj.key_obj.location)
						app.printToGUI("You lock " + dobj.getArticle(True) + dobj.verbose_name + ". ")
						dobj.lock_obj.makeLocked()
						return True
					else:
						app.printToGUI("You do not have the correct key. ")
						return False
				else:
					app.printToGUI("You do not have the correct key. ")
					return False
			else:
				app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already locked. ")
				return True
		else:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " does not have a lock. ")
			return False
	elif isinstance(dobj, thing.Lock):
		if dobj.parent_obj.is_open:
			if not closeVerb.verbFunc(me, app, dobj.parent_obj):
				app.printToGUI("Could not close " + dobj.parent_obj.verbose_name + ". ")
				return False
		if not dobj.is_locked:
			if dobj.key_obj:
				if me.containsItem(dobj.key_obj):
					app.printToGUI("(Using " + dobj.key_obj.getArticle(True) + dobj.key_obj.verbose_name + ")")
					if dobj.key_obj.location != me:
						app.printToGUI("(First removing " + dobj.key_obj.lowNameArticle(True) + " from " + dobj.key_obj.location.lowNameArticle(True) + ".)")
						#dobj.key_obj.location.removeThing(dobj.key_obj)
						#me.addThing(dobj.key_obj)
						removeFromVerb.verbFunc(me, app, dobj.key_obj, dobj.key_obj.location)
					app.printToGUI("You lock " + dobj.getArticle(True) + dobj.verbose_name + ". ")
					dobj.makeLocked()
					return True
				else:
					app.printToGUI("You do not have the correct key. ")
					return False
			else:
				app.printToGUI("You do not have the correct key. ")
				return False
		else:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already locked. ")
			return True
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " does not have a lock. ")
		return True
	
# replace default verbFunc method
lockVerb.verbFunc = lockVerbFunc

# UNLOCK WITH 
# transitive verb with indirect object
unlockWithVerb = Verb("unlock")
unlockWithVerb.addSynonym("unbolt")
unlockWithVerb.addSynonym("open")
unlockWithVerb.syntax = [["unlock", "<dobj>", "using", "<iobj>"], ["unlock", "<dobj>", "with", "<iobj>"], ["unbolt", "<dobj>", "with", "<iobj>"], ["unbolt", "<dobj>", "using", "<iobj>"],\
["open", "<dobj>", "using", "<iobj>"], ["open", "<dobj>", "with", "<iobj>"]]
unlockWithVerb.hasDobj = True
unlockWithVerb.hasIobj = True
unlockWithVerb.preposition = ["with", "using"]
unlockWithVerb.dscope = "near"
unlockWithVerb.iscope = "invflex"

def unlockWithVerbFunc(me, app, dobj, iobj, skip=False):
	"""Unlock a Door or Container with an lock
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing
	Returns True when the function ends with dobj unlocked, or without a lock. Returns False on failure to unlock.  """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.unlockVerbDobj(me, app, iobj)
		except AttributeError:
			supress = False
		try:
			runfunc = iobj.unlockVerbIobj(me, app, dobj)
		except AttributeError:
			supress = False
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(iobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Container) or isinstance(dobj, thing.Door):
		if dobj.lock_obj:
			if dobj.lock_obj.is_locked:
				if iobj is me:
					app.printToGUI("You are not a key. ")
					return False
				elif not isinstance(iobj, thing.Key):
					app.printToGUI((iobj.getArticle(True) + iobj.verbose_name).capitalize() + " is not a key. ")
					return False
				elif dobj.lock_obj.key_obj:
					if iobj==dobj.lock_obj.key_obj:
						app.printToGUI("You unlock " + dobj.getArticle(True) + dobj.verbose_name + " using " +\
						dobj.lock_obj.key_obj.getArticle(True) + dobj.lock_obj.key_obj.verbose_name +". ")
						dobj.lock_obj.makeUnlocked()
						return True
					else:
						app.printToGUI("You do not have the correct key. ")
						return False
				else:
					app.printToGUI("You do not have the correct key. ")
					return False
			else:
				app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already unlocked. ")
				return True
		else:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " does not have a lock. ")
			return True
	
	elif isinstance(dobj, thing.Lock):
		if dobj.is_locked:
			if not isinstance(iobj, thing.Key):
				app.printToGUI((iobj.getArticle(True) + iobj.verbose_name).capitalize() + " is not a key. ")
			elif dobj.key_obj:
				if iobj == dobj.key_obj.ix:
					app.printToGUI("You unlock " + dobj.getArticle(True) + dobj.verbose_name + " using " +\
					dobj.lock_obj.key_obj.getArticle(True) + dobj.lock_obj.key_obj.verbose_name +". ")
					dobj.makeUnlocked()
					return True
				else:
					app.printToGUI("You do not have the correct key. ")
					return False
			else:
				app.printToGUI("You do not have the correct key. ")
				return False
		else:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already unlocked. ")
			return True
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " does not have a lock. ")
		return True
	
# replace default verbFunc method
unlockWithVerb.verbFunc = unlockWithVerbFunc

# LOCK WITH 
# transitive verb with indirect object
lockWithVerb = Verb("lock")
lockWithVerb.addSynonym("bolt")
lockWithVerb.syntax = [["lock", "<dobj>", "using", "<iobj>"], ["lock", "<dobj>", "with", "<iobj>"], ["bolt", "<dobj>", "with", "<iobj>"], ["bolt", "<dobj>", "using", "<iobj>"]]
lockWithVerb.hasDobj = True
lockWithVerb.hasIobj = True
lockWithVerb.preposition = ["with", "using"]
lockWithVerb.dscope = "near"
lockWithVerb.iscope = "invflex"

def lockWithVerbFunc(me, app, dobj, iobj, skip=False):
	"""Unlock a Door or Container with an lock
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing
	Returns True when the function ends with dobj unlocked, or without a lock. Returns False on failure to unlock.  """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lockVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
		try:
			runfunc = dobj.lockVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Container) or isinstance(dobj, thing.Door):
		if dobj.is_open:
			if not closeVerb.verbFunc(me, app, dobj):
				app.printToGUI("Could not close " + dobj.verbose_name + ". ")
				return False
		if dobj.lock_obj:
			if not dobj.lock_obj.is_locked:
				if iobj is me:
					app.printToGUI("You are not a key. ")
					return False
				elif not isinstance(iobj, thing.Key):
					app.printToGUI((iobj.getArticle(True) + iobj.verbose_name).capitalize() + " is not a key. ")
					return False
				elif dobj.lock_obj.key_obj:
					if iobj==dobj.lock_obj.key_obj:
						app.printToGUI("You lock " + dobj.getArticle(True) + dobj.verbose_name + " using " +\
						dobj.lock_obj.key_obj.getArticle(True) + dobj.lock_obj.key_obj.verbose_name +". ")
						dobj.lock_obj.makeLocked()
						return True
					else:
						app.printToGUI("You do not have the correct key. ")
						return False
				else:
					app.printToGUI("You do not have the correct key. ")
					return False
			else:
				app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already locked. ")
				return True
		else:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " does not have a lock. ")
			return False
	
	elif isinstance(dobj, thing.Lock):
		if dobj.parent_obj.is_open:
			if not closeVerb.verbFunc(me, app, dobj.parent_obj):
				app.printToGUI("Could not close " + dobj.parent_obj.verbose_name + ". ")
				return False
		if not dobj.is_locked:
			if not isinstance(iobj, thing.Key):
				app.printToGUI((iobj.getArticle(True) + iobj.verbose_name).capitalize() + " is not a key. ")
			elif dobj.key_obj:
				if iobj == dobj.key_obj.ix:
					app.printToGUI("You lock " + dobj.getArticle(True) + dobj.verbose_name + " using " +\
					dobj.lock_obj.key_obj.getArticle(True) + dobj.lock_obj.key_obj.verbose_name +". ")
					dobj.makeLocked()
					return True
				else:
					app.printToGUI("You do not have the correct key. ")
					return False
			else:
				app.printToGUI("You do not have the correct key. ")
				return False
		else:
			app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is already locked. ")
			return True
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " does not have a lock. ")
		return False
	
# replace default verbFunc method
lockWithVerb.verbFunc = lockWithVerbFunc

# GO (empty verb added to improve "I don't understand" messages for invalid directions)
# transitive verb, no indirect object
goVerb = Verb("go")
goVerb.syntax = [["go", "<dobj>"]]
goVerb.hasDobj = True
goVerb.dscope = "direction"

def goVerbFunc(me, app, dobj):
	"""Empty function which should never be evaluated
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	pass
# replace the default verbFunc method
goVerb.verbFunc = goVerbFunc

# LIGHT (LightSource)
# transitive verb, no indirect object
lightVerb = Verb("light")
lightVerb.syntax = [["light", "<dobj>"]]
lightVerb.hasDobj = True
lightVerb.dscope = "near"
lightVerb.dtype = "LightSource"

def lightVerbFunc(me, app, dobj, skip=False):
	"""Light a LightSource """
	# print the target's xdesc (examine descripion)
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lightVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.LightSource):
		if dobj.player_can_light:
			light = dobj.light(app)
			if light:
				app.printToGUI(dobj.light_msg)
			return light
		else:
			app.printToGUI(dobj.cannot_light_msg)
			return False
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is not a light source. ")
		return False

# replace default verbFunc method
lightVerb.verbFunc = lightVerbFunc

# EXTINGUISH (LightSource)
# transitive verb, no indirect object
extinguishVerb = Verb("extinguish")
extinguishVerb.addSynonym("put")
extinguishVerb.syntax = [["extinguish", "<dobj>"], ["put", "out", "<dobj>"], ["put", "<dobj>", "out"]]
extinguishVerb.hasDobj = True
extinguishVerb.dscope = "near"
extinguishVerb.dtype = "LightSource"
extinguishVerb.preposition = ["out"]

def extinguishVerbFunc(me, app, dobj, skip=False):
	"""Extinguish a LightSource """
	# print the target's xdesc (examine descripion)
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.extinguishVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.LightSource):
		if dobj.player_can_extinguish:
			extinguish = dobj.extinguish(app)
			if extinguish:
				app.printToGUI(dobj.extinguish_msg)
			return extinguish
		else:
			app.printToGUI(dobj.cannot_extinguish_msg)
			return False
	else:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is not a light source. ")
		return False

# replace default verbFunc method
extinguishVerb.verbFunc = extinguishVerbFunc

# WAIT A TURN
# intransitive verb
waitVerb = Verb("wait")
waitVerb.addSynonym("z")
waitVerb.syntax = [["wait"], ["z"]]
waitVerb.hasDobj = False

def waitVerbFunc(me, app):
	"""Wait a turn
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	app.printToGUI("You wait a turn. ")
	return True
		
# replace default verbFunc method
waitVerb.verbFunc = waitVerbFunc

# USE (THING)
# transitive verb, no indirect object
useVerb = Verb("use")
useVerb.syntax = [["use", "<dobj>"]]
useVerb.hasDobj = True
useVerb.dscope = "near"

def useVerbFunc(me, app, dobj, skip=False):
	"""Use a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.useVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
		if isinstance(dobj, thing.LightSource):
			return lightVerb.verbFunc(me, app, dobj)
		elif isinstance(dobj, thing.Key):
			from .parser import lastTurn
			app.printToGUI("What would you like to unlock with " + dobj.lowNameArticle(True) + "?")
			lastTurn.verb = unlockWithVerb
			lastTurn.iobj = dobj
			lastTurn.dobj = False
			lastTurn.ambiguous = True
		elif isinstance(dobj, thing.Transparent):
			return lookThroughVerb.verbFunc(me, app, dobj)
		elif dobj.connection:
			dobj.connection.travel(me, app)
		elif isinstance(dobj, actor.Actor):
			app.printToGUI("You cannot use people. ")
			return False
		else:
			app.printToGUI("You'll have to be more specific about what you want to do with " + dobj.lowNameArticle(True) + ". ")
			return False
# replace the default verbFunc method
useVerb.verbFunc = useVerbFunc

# BUY FROM
# transitive verb with indirect object
buyFromVerb = Verb("buy", "buy from")
buyFromVerb.addSynonym("purchase")
buyFromVerb.syntax = [["buy", "<dobj>", "from", "<iobj>"], ["purchase", "<dobj>", "from", "<iobj>"]]
buyFromVerb.hasDobj = True
buyFromVerb.dscope = "knows"
buyFromVerb.hasIobj = True
buyFromVerb.iscope = "room"
buyFromVerb.itype = "Actor"
buyFromVerb.preposition = ["from"]

def buyFromVerbFunc(me, app, dobj, iobj, skip=False):
	"""Buy something from a person
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.buyFromVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.buyFromVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if not isinstance(iobj, actor.Actor):
		app.printToGUI("You cannot buy anything from " + iobj.lowNameArticle(False) + ". ")
		return False
	elif iobj == me:
		app.printToGUI("You cannot buy anything from yourself. ")
		return False
	elif isinstance(dobj, actor.Actor):
		if not dobj.commodity:
			app.printToGUI("You cannot buy or sell a person. ")
			return False
	if dobj.known_ix not in iobj.for_sale:
		app.printToGUI(iobj.capNameArticle(True) + " doesn't sell " + dobj.lowNameArticle(False) + ". ")
		return False
	elif not iobj.for_sale[dobj.known_ix].number:
		app.printToGUI(iobj.for_sale[dobj.known_ix].out_stock_msg)
		return False
	else:
		currency = iobj.for_sale[dobj.known_ix].currency
		currency_ix = currency.ix
		mycurrency = 0
		if currency_ix in me.contains:
			mycurrency = mycurrency + len(me.contains[currency_ix])
		if currency_ix in me.sub_contains:
			mycurrency = mycurrency + len(me.sub_contains[currency_ix])
		if mycurrency < iobj.for_sale[dobj.known_ix].price:
			app.printToGUI("You don't have enough " + currency.getPlural() + " to purchase " + dobj.lowNameArticle(False) + ". <br> (requires " + str(iobj.for_sale[dobj.known_ix].price) + ") ")
			return False
		else:
			app.printToGUI(iobj.for_sale[dobj.known_ix].purchase_msg)
			iobj.for_sale[dobj.known_ix].beforeBuy(me, app)
			iobj.for_sale[dobj.known_ix].buyUnit(me, app)
			iobj.for_sale[dobj.known_ix].afterBuy(me, app)
			if not iobj.for_sale[dobj.known_ix].number:
				iobj.for_sale[dobj.known_ix].soldOut(me, app)
			return True
	
# replace the default verbFunc method
buyFromVerb.verbFunc = buyFromVerbFunc

# BUY
# transitive verb
buyVerb = Verb("buy")
buyVerb.addSynonym("purchase")
buyVerb.syntax = [["buy", "<dobj>"], ["purchase", "<dobj>"]]
buyVerb.hasDobj = True
buyVerb.dscope = "knows"

def buyVerbFunc(me, app, dobj):
	"""Redriect to buy from
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing """
	from .parser import lastTurn
	people = []
	# find every Actor in the current location
	for key, items in me.getOutermostLocation().contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
	if len(people)==0:
		app.printToGUI("There's no one obvious here to buy from. ")
	elif len(people)==1:
		# ask the only actor in the room
		iobj = people[0]
		return buyFromVerb.verbFunc(me, app, dobj, iobj)
	else:
		remove_list = []
		for p in people:
			if p.ignore_if_ambiguous:
				remove_list.append(p)
		for p in remove_list:
			people.remove(p)
		if len(people)==0:
			app.printToGUI("There's no one obvious here to buy from. ")	
		elif len(people)==1:
			return buyFromVerb.verbFunc(me, app, dobj, people[0])
		elif lastTurn.dobj in people:
			return buyFromVerb.verbFunc(me, app, dobj, lastTurn.dobj)
		elif lastTurn.iobj in people:
			return buyFromVerb.verbFunc(me, app, dobj, lastTurn.iobj)
		listpeople = "Would you like to buy from "
		for p in people:
			listpeople = listpeople + p.lowNameArticle(True)
			if p is people[-1]:
				listpeople = listpeople + "? "
			elif p is people[-2]:
				listpeople = listpeople + " or "
			else:
				listpeople = listpeople + ", "
		app.printToGUI(listpeople)
		lastTurn.verb = buyFromVerb
		lastTurn.dobj = dobj
		lastTurn.iobj = False
		lastTurn.things = people
		lastTurn.ambiguous = True

# replace the default verbFunc method
buyVerb.verbFunc = buyVerbFunc

# SELL TO
# transitive verb with indirect object
sellToVerb = Verb("sell", "sell to")
sellToVerb.syntax = [["sell", "<dobj>", "to", "<iobj>"]]
sellToVerb.hasDobj = True
sellToVerb.dscope = "invflex"
sellToVerb.hasIobj = True
sellToVerb.iscope = "room"
sellToVerb.itype = "Actor"
sellToVerb.preposition = ["to"]

def sellToVerbFunc(me, app, dobj, iobj, skip=False):
	"""Sell something to a person
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.sellToVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.sellToVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if not isinstance(iobj, actor.Actor):
		app.printToGUI("You cannot sell anything to " + iobj.lowNameArticle(False) + ". ")
		return False
	elif iobj == me:
		app.printToGUI("You cannot sell anything to yourself. ")
		return False
	if dobj.ix not in iobj.will_buy:
		if dobj is me:
			app.printToGUI("You cannot sell yourself. ")
			return False
		app.printToGUI(iobj.capNameArticle(True) + " doesn't want to buy " + dobj.lowNameArticle(True) + ". ")
		return False
	elif not iobj.will_buy[dobj.known_ix].number:
		app.printToGUI(iobj.capNameArticle(True) + " will not buy any more " + dobj.getPlural() + ". ")
		return False
	else:
		app.printToGUI(iobj.will_buy[dobj.known_ix].sell_msg)
		iobj.will_buy[dobj.known_ix].beforeSell(me, app)
		iobj.will_buy[dobj.known_ix].sellUnit(me, app)
		iobj.will_buy[dobj.known_ix].afterSell(me, app)
		if not iobj.will_buy[dobj.known_ix].number:
			iobj.will_buy[dobj.known_ix].boughtAll(me, app)
		return True
	
# replace the default verbFunc method
sellToVerb.verbFunc = sellToVerbFunc

# SELL
# transitive verb
sellVerb = Verb("sell")
sellVerb.syntax = [["sell", "<dobj>"]]
sellVerb.hasDobj = True
sellVerb.dscope = "invflex"

def sellVerbFunc(me, app, dobj):
	"""Redriect to sell to
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing """
	from .parser import lastTurn
	people = []
	# find every Actor in the current location
	for key, items in me.getOutermostLocation().contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
	if len(people)==0:
		app.printToGUI("There's no one obvious here to sell to.")
	elif len(people)==1:
		# ask the only actor in the room
		iobj = people[0]
		return sellToVerb.verbFunc(me, app, dobj, iobj)
	else:
		remove_list = []
		for p in people:
			if p.ignore_if_ambiguous:
				remove_list.append(p)
		for p in remove_list:
			people.remove(p) 
		if len(people)==0:
			app.printToGUI("There's no one obvious here to sell to.")
		elif len(people)==1:
			return sellToVerb.verbFunc(me, app, dobj, people[0])
		elif lastTurn.dobj in people:
			return sellToVerb.verbFunc(me, app, dobj, lastTurn.dobj)
		elif lastTurn.iobj in people:
			return sellToVerb.verbFunc(me, app, dobj, lastTurn.iobj)
		listpeople = "Would you like to sell it to "
		for p in people:
			listpeople = listpeople + p.lowNameArticle(True)
			if p is people[-1]:
				listpeople = listpeople + "? "
			elif p is people[-2]:
				listpeople = listpeople + " or "
			else:
				listpeople = listpeople + ", "
		app.printToGUI(listpeople)
		lastTurn.verb = sellToVerb
		lastTurn.dobj = dobj
		lastTurn.iobj = False
		lastTurn.things = people
		lastTurn.ambiguous = True

# replace the default verbFunc method
sellVerb.verbFunc = sellVerbFunc

# RECORD ON
# intransitive verb
recordOnVerb = Verb("record", "record on")
recordOnVerb.addSynonym("recording")
recordOnVerb.syntax = [["record", "on"], ["recording", "on"]]
recordOnVerb.preposition = ["on"]

def recordOnVerbFunc(me, app):
	"""Take all obvious invItems in the current room
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	from .serializer import curSave
	f = app.getRecordFileGUI()
	curSave.recordOn(app, f)
	
# replace the default verb function
recordOnVerb.verbFunc = recordOnVerbFunc

# RECORD OFF
# intransitive verb
recordOffVerb = Verb("record", "record off")
recordOffVerb.addSynonym("recording")
recordOffVerb.syntax = [["record", "off"], ["recording", "off"]]
recordOffVerb.preposition = ["off"]

def recordOffVerbFunc(me, app):
	"""Take all obvious invItems in the current room
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	from .serializer import curSave
	curSave.recordOff(app)
	
# replace the default verb function
recordOffVerb.verbFunc = recordOffVerbFunc

# RECORD OFF
# intransitive verb
playBackVerb = Verb("playback")
playBackVerb.syntax = [["playback"]]

def playBackVerbFunc(me, app):
	"""Take all obvious invItems in the current room
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	from .parser import parseInput, lastTurn, daemons
	f = app.getPlayBackFileGUI()
	if not f:
		app.printToGUI("No file selected. ")
		return False
	play = open(f, "r")
	lines = play.readlines()
	app.printToGUI("**STARTING PLAYBACK** ")
	for line in lines:
		app.newBox(app.box_style2)
		app.printToGUI("> " + line)
		app.newBox(app.box_style1)
		if (not lastTurn.ambiguous) and (not lastTurn.err):
			daemons.runAll(me, app)
		parseInput(me, app, line)
	play.close()
	app.printToGUI("**PLAYBACK COMPLETE** ")
	return True
# replace the default verb function
playBackVerb.verbFunc = playBackVerbFunc

# LEAD (person) (direction)
# transitive verb with indirect object
leadDirVerb = Verb("lead")
leadDirVerb.syntax = [["lead", "<dobj>", "<iobj>"]]
leadDirVerb.hasDobj = True
leadDirVerb.hasIobj = True
leadDirVerb.iscope = "direction"
leadDirVerb.dscope = "room"
leadDirVerb.dtype = "Actor"

def leadDirVerbFunc(me, app, dobj, iobj, skip=False):
	"""Lead an Actor in a direction
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	from .travel import TravelConnector
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.leadDirVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if not isinstance(dobj, actor.Actor):
		app.printToGUI("You cannot lead that. ")
		return False
	elif dobj.can_lead:
		from intficpy.travel import getDirectionFromString, directionDict
		destination = getDirectionFromString(dobj.getOutermostLocation(), iobj)
		if not destination:
			app.printToGUI("You cannot lead " + dobj.lowNameArticle(True) + " that way. ")
			return False
		if isinstance(destination, TravelConnector):
			if not destination.can_pass:
				app.printToGUI(destination.cannot_pass_msg)
				return False
			elif dobj.getOutermostLocation() == destination.pointA:
				destination = destination.pointB
			else:
				destination = destination.pointA
		dobj.location.removeThing(dobj)
		destination.addThing(dobj)
		directionDict[iobj](me, app)
	else:
		app.printToGUI(dobj.capNameArticle(True) + " doesn't want to be led. ")

# replace the default verbFunc method
leadDirVerb.verbFunc = leadDirVerbFunc

# BREAK
# transitive verb, no indirect object
breakVerb = Verb("break")
breakVerb.syntax = [["break", "<dobj>"]]
breakVerb.hasDobj = True
breakVerb.dscope = "near"

def breakVerbFunc(me, app, dobj, skip=False):
	"""break a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.breakVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	app.printToGUI("Violence isn't the answer to this one. ")

# replace default verbFunc method
breakVerb.verbFunc = breakVerbFunc

# KICK
# transitive verb, no indirect object
kickVerb = Verb("kick")
kickVerb.syntax = [["kick", "<dobj>"]]
kickVerb.hasDobj = True
kickVerb.dscope = "near"

def kickVerbFunc(me, app, dobj, skip=False):
	"""kick a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.kickVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	app.printToGUI("Violence isn't the answer to this one. ")

# replace default verbFunc method
kickVerb.verbFunc = kickVerbFunc

# KILL
# transitive verb, no indirect object
killVerb = Verb("kill")
killVerb.syntax = [["kill", "<dobj>"]]
killVerb.hasDobj = True
killVerb.dscope = "near"

def killVerbFunc(me, app, dobj, skip=False):
	"""kill a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.killVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, actor.Actor):
		app.printToGUI("Violence isn't the answer to this one. ")
	else:
		app.printToGUI(dobj.capNameArticle(True) + " cannot be killed, as it is not alive.")

# replace default verbFunc method
killVerb.verbFunc = killVerbFunc

# JUMP
# intransitive verb
jumpVerb = Verb("jump")
jumpVerb.syntax = [["jump"]]

def jumpVerbFunc(me, app):
	"""Jump in place
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app"""
	app.printToGUI("You jump in place. ")
# replace default verbFunc method
jumpVerb.verbFunc = jumpVerbFunc

# JUMP OVER
# transitive verb
jumpOverVerb = Verb("jump")
jumpOverVerb.syntax = [["jump", "over", "<dobj>"], ["jump", "across", "<dobj>"]]
jumpOverVerb.preposition = ["over", "across"]
jumpOverVerb.hasDobj = True
jumpOverVerb.dscope = "room"

def jumpOverVerbFunc(me, app, dobj, skip=False):
	"""Jump over a Thing
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app"""
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.jumpOverVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if dobj==me:
		app.printToGUI("You cannot jump over yourself. ")
	elif dobj.size < 70:
		app.printToGUI("There's no reason to jump over that. ")
	else:
		app.printToGUI(dobj.capNameArticle(True) + " is too big to jump over. ")
	return False
# replace default verbFunc method
jumpOverVerb.verbFunc = jumpOverVerbFunc

# JUMP IN
# transitive verb
jumpInVerb = Verb("jump")
jumpInVerb.syntax = [["jump", "in", "<dobj>"], ["jump", "into", "<dobj>"]]
jumpInVerb.preposition = ["in", "into"]
jumpInVerb.hasDobj = True
jumpInVerb.dscope = "room"

def jumpInVerbFunc(me, app, dobj, skip=False):
	"""Jump in a Thing
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app"""
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.jumpInVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	app.printToGUI("You cannot jump into that. ")
	return False
# replace default verbFunc method
jumpInVerb.verbFunc = jumpInVerbFunc

# JUMP ON
# transitive verb
jumpOnVerb = Verb("jump")
jumpOnVerb.syntax = [["jump", "on", "<dobj>"], ["jump", "onto", "<dobj>"]]
jumpOnVerb.preposition = ["on", "onto"]
jumpOnVerb.hasDobj = True
jumpOnVerb.dscope = "room"

def jumpOnVerbFunc(me, app, dobj, skip=False):
	"""Jump on a Thing
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app"""
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.jumpOnVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	app.printToGUI("You cannot jump onto that. ")
	return False
# replace default verbFunc method
jumpOnVerb.verbFunc = jumpOnVerbFunc

# PRESS
# transitive verb, no indirect object
pressVerb = Verb("press")
pressVerb.addSynonym("depress")
pressVerb.syntax = [["press", "<dobj>"], ["depress", "<dobj>"], ["press", "on", "<dobj>"]]
pressVerb.hasDobj = True
pressVerb.dscope = "near"
pressVerb.preposition = ["on"]
pressVerb.dtype = "Pressable"

def pressVerbFunc(me, app, dobj, skip=False):
	"""press a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.pressVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Pressable):
		app.printToGUI("You press " + dobj.lowNameArticle(True) + ". ")
		dobj.pressThing(me, app)
	else:
		app.printToGUI("Pressing " + dobj.lowNameArticle(True) + " has no effect. ")
		return False

# replace default verbFunc method
pressVerb.verbFunc = pressVerbFunc

# PUSH
# transitive verb, no indirect object
pushVerb = Verb("push")
pushVerb.syntax = [["push", "<dobj>"], ["push", "on", "<dobj>"]]
pushVerb.hasDobj = True
pushVerb.dscope = "near"
pushVerb.preposition = ["on"]

def pushVerbFunc(me, app, dobj, skip=False):
	"""push a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.pushVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Pressable):
		pressVerb.verbFunc(me, app, dobj)
	else:
		app.printToGUI("You push on " + dobj.lowNameArticle(True) + ", to no productive end. ")
		return False

# replace default verbFunc method
pushVerb.verbFunc = pushVerbFunc

# POUR OUT
# transitive verb, no indirect object
pourOutVerb = Verb("pour")
pourOutVerb.addSynonym("dump")
pourOutVerb.syntax = [["pour", "<dobj>"], ["pour", "out", "<dobj>"], ["pour", "<dobj>", "out"], ["dump", "<dobj>"], ["dump", "out", "<dobj>"], ["dump", "<dobj>", "out"]]
pourOutVerb.hasDobj = True
pourOutVerb.dscope = "invflex"
pourOutVerb.preposition = ["out"]

def pourOutVerbFunc(me, app, dobj, skip=False):
	"""Pour a Liquid out of a Container """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.pourOutVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Container):
		loc = me.getOutermostLocation()
		if dobj.has_lid:
			if not dobj.is_open:
				app.printToGUI(dobj.capNameArticle(True) + " is closed. ")
				return False
		if dobj.contains=={}:
			app.printToGUI(dobj.capNameArticle(True) + " is empty. ")
			return True
		liquid = dobj.containsLiquid()
		if not liquid:
			app.printToGUI("You dump the contents of " + dobj.lowNameArticle(True) + " onto the ground. ")
			containslist = []
			for key in dobj.contains:
				for item in dobj.contains[key]:
					containslist.append(item)
			for item in containslist:
				dobj.removeThing(item)
				loc.addThing(item)
			return True
		else:
			dobj = liquid
	if isinstance(dobj, thing.Liquid):
		if not dobj.getContainer:
			app.printToGUI("It isn't in a container you can dump it from. ")
			return False
		elif not dobj.can_pour_out:
			app.printToGUI(dobj.cannot_pour_out_msg)
			return False
		app.printToGUI("You dump out " + dobj.lowNameArticle(True) + ". ")
		dobj.dumpLiquid()
		return True
	app.printToGUI("You can't dump that out. ")
	return False

# replace default verbFunc method
pourOutVerb.verbFunc = pourOutVerbFunc

# DRINK
# transitive verb, no indirect object
drinkVerb = Verb("drink")
drinkVerb.syntax = [["drink", "<dobj>"], ["drink", "from", "<dobj>"], ["drink", "out", "of", "<dobj>"]]
drinkVerb.hasDobj = True
drinkVerb.dscope = "invflex"
drinkVerb.preposition = ["out", "from"]
drinkVerb.keywords = ["of"]

def drinkVerbFunc(me, app, dobj, skip=False):
	"""Drink a Liquid """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.drinkVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Container):
		loc = me.getOutermostLocation()
		if dobj.has_lid:
			if not dobj.is_open:
				app.printToGUI(dobj.capNameArticle(True) + " is closed. ")
				return False
		if dobj.contains=={}:
			app.printToGUI(dobj.capNameArticle(True) + " is empty. ")
			return True
		liquid = dobj.containsLiquid()
		if not liquid:
			app.printToGUI("There is nothing you can drink in " + dobj.lowNameArticle(True) + ". ")
			return False
		else:
			dobj = liquid
	if isinstance(dobj, thing.Liquid):
		container = dobj.getContainer()
		if not dobj.can_drink:
			app.printToGUI(dobj.cannot_drink_msg)
			return False
		app.printToGUI("You drink " + dobj.lowNameArticle(True) + ". ")
		dobj.drinkLiquid(me, app)
		return True
	app.printToGUI("You cannot drink that. ")
	return False

# replace default verbFunc method
drinkVerb.verbFunc = drinkVerbFunc

# POUR INTO
# transitive verb, with indirect object
pourIntoVerb = Verb("pour")
pourIntoVerb.addSynonym("dump")
pourIntoVerb.syntax = [["pour", "<dobj>", "into", "<iobj>"], ["pour", "<dobj>", "in", "<iobj>"], ["dump", "<dobj>", "into", "<iobj>"], ["dump", "<dobj>", "in", "<iobj>"]]
pourIntoVerb.hasDobj = True
pourIntoVerb.hasIobj = True
pourIntoVerb.dscope = "invflex"
pourIntoVerb.iscope = "near"
pourIntoVerb.preposition = ["in", "into"]

def pourIntoVerbFunc(me, app, dobj, iobj, skip=False):
	"""Pour a Liquid from one Container to another """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.pourIntoVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.pourIntoVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(dobj, thing.Container):
		loc = me.getOutermostLocation()
		if dobj.has_lid:
			if not dobj.is_open:
				app.printToGUI(dobj.capNameArticle(True) + " is closed. ")
				return False
		if dobj.contains=={}:
			app.printToGUI(dobj.capNameArticle(True) + " is empty. ")
			return True
		liquid = dobj.containsLiquid()
		if not liquid:
			if not isinstance(iobj, thing.Container):
				app.printToGUI(iobj.capNameArticle(True) + " is not a container. ")
				return False
			app.printToGUI("You dump the contents of " + dobj.lowNameArticle(True) + " into " + iobj.lowNameArticle(True) + ". ")
			containslist = []
			for key in dobj.contains:
				for item in dobj.contains[key]:
					containslist.append(item)
			for item in containslist:
				dobj.removeThing(item)
				if item.size < iobj.size:
					iobj.addThing(item)
				else:
					app.printToGUI(item.capNameArticle(True) + " is too large to fit inside. It falls to the ground.")
					loc.addThing(item)
			return True
		else:
			dobj = liquid
	if isinstance(dobj, thing.Liquid):
		if not dobj.getContainer:
			app.printToGUI("It isn't in a container you can dump it from. ")
			return False
		elif not iobj.holds_liquid:
			app.printToGUI(iobj.capNameArticle(True) + " cannot hold a liquid. ")
			return False		
		spaceleft = iobj.liquidRoomLeft()
		liquid_contents = iobj.containsLiquid()
		if iobj.has_lid:
			if not iobj.is_open:
				app.printToGUI(dobj.capNameArticle(True) + " is closed. ")
				return False
		if iobj.contains != {} and not liquid_contents:
			app.printToGUI("(First attempting to empty " + iobj.lowNameArticle(True)+ ")")
			success = pourOutVerb.verbFunc(me, app, iobj)
			if not success:
				return False
		if liquid_contents and liquid_contents.liquid_type != dobj.liquid_type:
			success = liquid_contents.mixWith(me, app, liquid_contents, dobj)
			if not success:
				app.printToGUI(iobj.capNameArticle(True) + " is already full of " + liquid_contents.lowNameArticle() + ". ")
				return False
			else:
				return True
		elif liquid_contents:
			if liquid_contents.infinite_well:
				app.printToGUI("You pour " + dobj.lowNameArticle(True) + " into " + iobj.lowNameArticle(True) + ". ")
				dobj.location.removeThing(dobj)
				return True
			app.printToGUI(iobj.capNameArticle(True) +  " already has " + liquid_contents.lowNameArticle() + " in it. ")
			return False
		else:
			app.printToGUI("You pour " + dobj.lowNameArticle(True) + " into " + iobj.lowNameArticle(True) + ". ")	
			return dobj.fillVessel(iobj)
	app.printToGUI("You can't dump that out. ")
	return False

# replace default verbFunc method
pourIntoVerb.verbFunc = pourIntoVerbFunc

# FILL FROM
# transitive verb, with indirect object
fillFromVerb = Verb("fill")
fillFromVerb.syntax = [["fill", "<dobj>", "from", "<iobj>"], ["fill", "<dobj>", "in", "<iobj>"]]
fillFromVerb.hasDobj = True
fillFromVerb.hasIobj = True
fillFromVerb.dscope = "invflex"
fillFromVerb.iscope = "near"
fillFromVerb.preposition = ["from", "in"]

def fillFromVerbFunc(me, app, dobj, iobj, skip=False):
	"""Pour a Liquid from one Container to another """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.fillFromVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.fillFromVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	if isinstance(iobj, thing.Container):
		loc = me.getOutermostLocation()
		if iobj.has_lid:
			if not iobj.is_open:
				app.printToGUI(iobj.capNameArticle(True) + " is closed. ")
				return False
		if iobj.contains=={}:
			app.printToGUI(iobj.capNameArticle(True) + " is empty. ")
			return True
		liquid = iobj.containsLiquid()
		if not liquid:
			if iobj is me:
				app.printToGUI("You cannot fill anything from yourself. ")
			else:
				app.printToGUI("There is no liquid in " + dobj.lowNameArticle(True) + ". ")
			return False
		else:
			if not dobj.holds_liquid:
				app.printToGUI(dobj.capNameArticle(True) + " cannot hold a liquid. ")
				return False
			if dobj.has_lid:
				if not dobj.is_open:
					app.printToGUI(dobj.capNameArticle(True) + " is closed. ")
					return False
			spaceleft = dobj.liquidRoomLeft()
			liquid_contents = dobj.containsLiquid()
			if dobj.contains != {} and not liquid_contents:
				app.printToGUI("(First attempting to empty " + iobj.lowNameArticle(True)+ ")")
				success = pourOutVerb.verbFunc(me, app, iobj)
				if not success:
					return False
			if not liquid.can_fill_from:
				app.printToGUI(liquid.cannot_fill_from_msg)
				return False
			if liquid_contents and liquid_contents.liquid_type != liquid.liquid_type:
				success = liquid_contents.mixWith(me, app, liquid_contents, dobj)
				if not success:
					app.printToGUI("There is already " + liquid_contents.lowNameArticle() + " in " + dobj.lowNameArticle(True) + ". ")
					return False
				else:
					return True
			
			elif liquid.infinite_well:
				app.printToGUI("You fill " + dobj.lowNameArticle(True) + " with " + liquid.lowNameArticle() + " from " + iobj.lowNameArticle(True) +  ". ")
			else:
				app.printToGUI("You fill " + dobj.lowNameArticle(True) + " with " + liquid.lowNameArticle() + ", taking all of it. ")
			return liquid.fillVessel(dobj)
	app.printToGUI("You can't fill that. ")
	return False

# replace default verbFunc method
fillFromVerb.verbFunc = fillFromVerbFunc

# FILL WITH
# transitive verb, with indirect object
fillWithVerb = Verb("fill")
fillWithVerb.syntax = [["fill", "<dobj>", "with", "<iobj>"]]
fillWithVerb.hasDobj = True
fillWithVerb.hasIobj = True
fillWithVerb.dscope = "invflex"
fillWithVerb.iscope = "near"
fillWithVerb.preposition = ["with"]

def fillWithVerbFunc(me, app, dobj, iobj, skip=False):
	"""Pour a Liquid from one Container to another """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.fillWithVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		try:
			runfunc = iobj.fillWithVerbIobj(me, app, dobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	if dobj.cannot_interact_msg:
		app.printToGUI(dobj.cannot_interact_msg)
		return False
	elif iobj.cannot_interact_msg:
		app.printToGUI(iobj.cannot_interact_msg)
	if not isinstance(dobj, thing.Container):
		app.printToGUI("You cannot fill " + dobj.lowNameArticle(True) + ". ")
		return False
	if isinstance(iobj, thing.Liquid):
		if not dobj.holds_liquid:
			app.printToGUI(dobj.capNameArticle(True) + " cannot hold a liquid. ")
			return False
		if dobj.has_lid:
			if not dobj.is_open:
				app.printToGUI(dobj.capNameArticle(True) + " is closed. ")
				return False
		spaceleft = dobj.liquidRoomLeft()
		liquid_contents = dobj.containsLiquid()
		if dobj.contains != {} and not liquid_contents:
			app.printToGUI("(First attempting to empty " + iobj.lowNameArticle(True)+ ")")
			success = pourOutVerb.verbFunc(me, app, iobj)
			if not success:
				return False
		if not iobj.can_fill_from:
			app.printToGUI(iobj.cannot_fill_from_msg)
			return False
		if liquid_contents and liquid_contents.liquid_type != iobj.liquid_type:
			success = liquid_contents.mixWith(me, app, liquid_contents, dobj)
			if not success:
				app.printToGUI("There is already " + liquid_contents.lowNameArticle() + " in " + dobj.lowNameArticle(True) + ". ")
				return False
			else:
				return True
		container = iobj.getContainer()
		if iobj.infinite_well:
				app.printToGUI("You fill " + dobj.lowNameArticle(True) + " with " + iobj.lowNameArticle() + ". ")
		else:
			app.printToGUI("You fill " + dobj.lowNameArticle(True) + " with " + iobj.lowNameArticle() + ", taking all of it. ")	
		return iobj.fillVessel(dobj)
	app.printToGUI("You can't fill " + dobj.lowNameArticle(True) + " with that. ")
	return False

# replace default verbFunc method
fillWithVerb.verbFunc = fillWithVerbFunc

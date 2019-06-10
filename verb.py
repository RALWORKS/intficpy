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
		else:
			vocab.verbDict[word] = [self]
		if list_word and list_word not in aboutGame.verbs:
			aboutGame.verbs.append(list_word)
		elif word not in aboutGame.verbs and not exempt_from_list:
			aboutGame.verbs.append(word)
		self.word = word
		self.dscope = "room"
		word = ""
		self.far_iobj = False
		self.far_dobj = False
		self.hasDobj = False
		self.hasStrDobj = False
		self.hasStrIobj = False
		self.dtype = False
		self.hasIobj = False
		self.itype = False
		self.impDobj = False
		self.impIobj = False
		self.preposition = False
		self.dobj_direction = False
		self.iobj_direction = False
		self.syntax = []
		# range for direct and indierct objects
		self.dscope = "room" # "knows", "near", "room" or "inv"
		self.iscope = "room"

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
#getVerb.preposition = ["up"]
getVerb.dscope = "near"
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
	if dobj.invItem:
		if dobj.ix in me.contains:
			if dobj in me.contains[dobj.ix]:
				app.printToGUI("You already have " + dobj.getArticle(True) + dobj.verbose_name + ".")
				return False
		if dobj.ix in me.sub_contains:
			if dobj in me.sub_contains[dobj.ix]:
				app.printToGUI("You already have " + dobj.getArticle(True) + dobj.verbose_name + ".")
				return False
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
			dobj.location.removeThing(dobj)
			dobj.location = old_loc.location
			if not isinstance(old_loc, actor.Actor): 
				old_loc.containsListUpdate()
		dobj.location.removeThing(dobj)
		me.addThing(dobj)
		return True
	elif dobj.parent_obj:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is attached to " + dobj.parent_obj.getArticle(True) + dobj.parent_obj.verbose_name + ". ")
		return False
	else:
		# if the dobj can't be taken, print the message
		app.printToGUI(dobj.cannotTakeMsg)
		return False

# replace the default verb function
getVerb.verbFunc = getVerbFunc

# DROP
# transitive verb, no indirect object
dropVerb = Verb("drop")
dropVerb.addSynonym("put")
dropVerb.syntax = [["drop", "<dobj>"], ["put", "down", "<dobj>"], ["put", "<dobj>", "down"]]
dropVerb.hasDobj = True
dropVerb.dscope = "inv"
#dropVerb.preposition = ["down"]

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
	if dobj.invItem and me.removeThing(dobj):
		app.printToGUI("You drop " + dobj.getArticle(True) + dobj.verbose_name + ".")
		dobj.location = me.location
		if isinstance(dobj.location, thing.Surface):
			dobj.location.addOn(dobj)
		elif isinstance(dobj.location, thing.Container):
			dobj.location.addIn(dobj)
		else:	
			dobj.location.addThing(dobj)
	# if dobj is in sub_contains, remove it
	# set the Thing's location property
	elif dobj.parent_obj:
		app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is attached to " + dobj.parent_obj.getArticle(True) + dobj.parent_obj.verbose_name + ". ")
	elif not dobj.invItem:
		app.printToGUI("Error: not an inventory item. ")
	else:
		app.printToGUI("You are not holding " + dobj.getArticle(True) + dobj.verbose_name + ".")
# replace the default verbFunc method
dropVerb.verbFunc = dropVerbFunc

# PUT/SET ON
# transitive verb with indirect object
setOnVerb = Verb("set", "set on")
setOnVerb.addSynonym("put")
setOnVerb.syntax = [["put", "<dobj>", "on", "<iobj>"], ["set", "<dobj>", "on", "<iobj>"]]
setOnVerb.hasDobj = True
setOnVerb.dscope = "inv"
setOnVerb.itype = "Surface"
setOnVerb.hasIobj = True
setOnVerb.iscope = "room"
#setOnVerb.preposition = ["on"]

def setOnVerbFunc(me, app, dobj, iobj, skip=False):
	"""Put a Thing on a Surface
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
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
setInVerb = Verb("set", "set in")
setInVerb.addSynonym("put")
setInVerb.syntax = [["put", "<dobj>", "in", "<iobj>"], ["set", "<dobj>", "in", "<iobj>"]]
setInVerb.hasDobj = True
setInVerb.dscope = "inv"
setInVerb.itype = "Container"
setInVerb.hasIobj = True
setInVerb.iscope = "room"
#setInVerb.preposition = ["in"]

def setInVerbFunc(me, app, dobj, iobj, skip=False):
	"""Put a Thing in a Container
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
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
	
	if isinstance(iobj, thing.Container) and iobj.has_lid:
		if not iobj.is_open:
			app.printToGUI("You  cannot put " + dobj.getArticle(True) + dobj.verbose_name + " inside, as " + iobj.getArticle(True) + iobj.verbose_name + " is closed.")
			return False
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

# PUT/SET UNDER
# transitive verb with indirect object
setUnderVerb = Verb("set", "set under")
setUnderVerb.addSynonym("put")
setUnderVerb.syntax = [["put", "<dobj>", "under", "<iobj>"], ["set", "<dobj>", "under", "<iobj>"]]
setUnderVerb.hasDobj = True
setUnderVerb.dscope = "inv"
setUnderVerb.hasIobj = True
setUnderVerb.iscope = "room"
setUnderVerb.itype = "UnderSpace"
#setUnderVerb.preposition = ["under"]

def setUnderVerbFunc(me, app, dobj, iobj, skip=False):
	"""Put a Thing under an UnderSpace
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
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
	
	outer_loc = me.getOutermostLocation()
	if isinstance(iobj, thing.UnderSpace) and dobj.size <= iobj.size:
		app.printToGUI("You set " + dobj.getArticle(True) + dobj.verbose_name + " " + iobj.contains_preposition + " " + iobj.getArticle(True) + iobj.verbose_name + ".")
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
		iobj.addUnder(dobj, True)
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
	if len(me.contains)==0:
		app.printToGUI("You don't have anything with you.")
	else:
		# the string to print listing the contains
		invdesc = "You have "
		list_version = list(me.contains.keys())
		for key in list_version:
			for thing in me.contains[key]:
				if thing.parent_obj:
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

# HELP VERB (Verb)
# intransitive verb
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
					elif verb.dtype=="Direction":
						out[ix] = "(direction)"
					elif verb.dtype=="String":
						out[ix] = "(word)"
					else:
						out[ix] = "(thing)"
				if "<iobj>" in form:
					ix = form.index("<iobj>")
					if verb.itype=="Actor":
						out[ix] = "(person)"
					elif verb.itype=="Direction":
						out[ix] = "(direction)"
					elif verb.dtype=="String":
						out[ix] = "(word)"
					else:
						out[ix] = "(thing)"
				out = " ".join(out)
				app.printToGUI(out)
	else:
		app.printToGUI("I found no verb corresponding to the input \"" + " ".join(dobj) + "\". ")
		
# replace default verbFunc method
helpVerbVerb.verbFunc = helpVerbVerbFunc

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
#examineVerb.preposition = ["at"]
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
	app.printToGUI(dobj.xdesc)

# replace default verbFunc method
examineVerb.verbFunc = examineVerbFunc

# LOOK IN 
# transitive verb, no indirect object
lookInVerb = Verb("look", "look in")
lookInVerb.syntax = [["look", "in", "<dobj>"]]
lookInVerb.hasDobj = True
lookInVerb.dscope = "near"
lookInVerb.dtype = "Container"
#lookInVerb.preposition = ["in"]

def lookInVerbFunc(me, app, dobj, skip=False):
	"""Look inside a Thing """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lookInVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		if not runfunc:
			return True
	
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
					me.know_about.append(key)
			return True
		else:
			app.printToGUI("The " + dobj.verbose_name + " is empty.")
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
#lookUnderVerb.preposition = ["under"]

def lookUnderVerbFunc(me, app, dobj, skip=False):
	"""Look under a Thing """
	# print the target's xdesc (examine descripion)
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lookUnderVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	
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

# ASK (Actor)
# transitive verb with indirect object
# implicit direct object enabled
askVerb = Verb("ask", "ask about")
askVerb.syntax = [["ask", "<dobj>", "about", "<iobj>"]]
askVerb.hasDobj = True
askVerb.hasIobj = True
askVerb.iscope = "knows"
askVerb.impDobj = True
#askVerb.preposition = ["about"]
askVerb.dtype = "Actor"

def getImpAsk(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	# find every Actor in the current location
	for key, items in me.location.contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
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

def askVerbFunc(me, app, dobj, iobj, skip=False):
	"""Ask an Actor about a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	from .thing import reflexive
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
	
	if isinstance(dobj, actor.Actor):
		# try to find the ask topic for iobj
		if iobj==reflexive:	
			iobj = dobj
		if iobj.ix in dobj.ask_topics:
			# call the ask function for iobj
			dobj.ask_topics[iobj.ix].func(app)
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
#tellVerb.preposition = ["about"]
tellVerb.dtype = "Actor"

def getImpTell(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	# find every Actor in the current location
	for key, items in me.location.contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
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

def tellVerbFunc(me, app, dobj, iobj, skip=False):
	"""Tell an Actor about a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
	from .thing import reflexive
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
	
	if isinstance(dobj, actor.Actor):
		if iobj==reflexive:	
				iobj = dobj
		if iobj.ix in dobj.tell_topics:
			dobj.tell_topics[iobj.ix].func(app)
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
giveVerb.iscope = "inv"
giveVerb.impDobj = True
#giveVerb.preposition = ["to"]
giveVerb.dtype = "Actor"

def getImpGive(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	# find every Actor in the current location
	for key, items in me.location.contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
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
	
	if isinstance(dobj, actor.Actor):
		if iobj.ix in dobj.give_topics:
			dobj.give_topics[iobj.ix].func(app)
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
			return True
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
showVerb.iscope = "inv"
showVerb.impDobj = True
#showVerb.preposition = ["to"]
showVerb.dtype = "Actor"

def getImpShow(me, app):
	"""If no dobj is specified, try to guess the Actor
	Takes arguments me, pointing to the player, and app, the PyQt5 GUI app """
	# import parser to gain access to the record of the last turn
	from . import parser
	people = []
	# find every Actor in the current location
	for key, items in me.location.contains.items():
		for item in items:
			if isinstance(item, actor.Actor)  and not item==me:
				people.append(item)
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

def showVerbFunc(me, app, dobj, iobj, skip=False):
	"""Show an Actor a Thing
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, dobj, a Thing, and iobj, a Thing """
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
	if isinstance(dobj, actor.Actor):
		if iobj.ix in dobj.show_topics:
			dobj.show_topics[iobj.ix].func(app)
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
#wearVerb.preposition = ["on"]

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
#doffVerb.preposition = ["off"]

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
#lieDownVerb.preposition = ["down"]

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
standUpVerb.addSynonym("get")
standUpVerb.syntax = [["stand", "up"], ["stand"], ["get", "up"]]
#standUpVerb.preposition = ["up"]

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
#sitDownVerb.preposition = ["down"]

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
standOnVerb = Verb("stand", "stand on")
standOnVerb.syntax = [["stand", "on", "<dobj>"]]
standOnVerb.hasDobj = True
standOnVerb.dscope = "room"
#standOnVerb.preposition = ["on"]

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
		return False

# replace default verbFunc method
standOnVerb.verbFunc = standOnVerbFunc

# SIT ON (SURFACE)
# transitive verb, no indirect object
sitOnVerb = Verb("sit", "sit on")
sitOnVerb.syntax = [["sit", "on", "<dobj>"], ["sit", "down", "on", "<dobj>"]]
sitOnVerb.hasDobj = True
sitOnVerb.dscope = "room"
#sitOnVerb.preposition = ["down", "on"]

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
lieOnVerb = Verb("lie", "lie on")
lieOnVerb.addSynonym("lay")
lieOnVerb.syntax = [["lie", "on", "<dobj>"], ["lie", "down", "on", "<dobj>"], ["lay", "on", "<dobj>"], ["lay", "down", "on", "<dobj>"]]
lieOnVerb.hasDobj = True
lieOnVerb.dscope = "room"
#lieOnVerb.preposition = ["down", "on"]

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
#sitInVerb.preposition = ["down", "in"]

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
	
	if me.location==dobj and me.position=="sitting" and isinstance(dobj, thing.Container):
		app.printToGUI("You are already sitting in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return True
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
		return False

# replace default verbFunc method
sitInVerb.verbFunc = sitInVerbFunc

# STAND IN (CONTAINER)
# transitive verb, no indirect object
standInVerb = Verb("stand", "stand in")
standInVerb.syntax = [["stand", "in", "<dobj>"]]
standInVerb.hasDobj = True
standInVerb.dscope = "room"
#standInVerb.preposition = ["in"]

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
	
	if me.location==dobj and me.position=="standing" and isinstance(dobj, thing.Container):
		app.printToGUI("You are already standing in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return True
	elif isinstance(dobj, thing.Container) and dobj.canStand:
		app.printToGUI("You stand in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addIn(me)
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
#lieInVerb.preposition = ["down", "in"]

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
	
	if me.location==dobj and me.position=="lying" and isinstance(dobj, thing.Container):
		app.printToGUI("You are already lying in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return True
	elif isinstance(dobj, thing.Container) and dobj.canLie:
		app.printToGUI("You lie in " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		if me in me.location.contains[me.ix]:
			me.location.contains[me.ix].remove(me)
			if me.location.contains[me.ix] == []:
				del me.location.contains[me.ix]
		dobj.addIn(me)
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
#climbOnVerb.preposition = ["on", "up"]

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
	
	if isinstance(dobj, thing.AbstractClimbable):
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
#climbUpVerb.preposition = ["up"]

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
#climbDownVerb.preposition = ["off", "down"]

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
climbDownFromVerb = Verb("climb", "climb down from")
climbDownFromVerb.addSynonym("get")
climbDownFromVerb.syntax = [["climb", "off", "<dobj>"], ["get", "off", "<dobj>"], ["climb", "down", "from", "<dobj>"], ["get", "down", "from", "<dobj>"], ["climb", "down", "<dobj>"]]
climbDownFromVerb.hasDobj = True
climbDownFromVerb.dscope = "room"
#climbDownFromVerb.preposition = ["off", "down", "from"]
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
	
	if isinstance(dobj, thing.AbstractClimbable):
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
			if isinstance(outer_loc, thing.Surface):
				outer_loc.addOn(me)
				return True
			elif isinstance(outer_loc, thing.Container):
				outer_loc.addIn(me)
				return True
			elif isinstance(outer_loc, room.Room):
				outer_loc.addThing(me) 
				return True
			else:
				print("Unsupported outer location type: " + outer_loc.name)
				return False
		else:
			app.printToGUI("You cannot climb down from here. ")
			return False
	else:
		app.printToGUI("You are not on " + dobj.getArticle(True) + dobj.verbose_name  + ".")
		return False

# replace default verbFunc method
climbDownFromVerb.verbFunc = climbDownFromVerbFunc

# CLIMB IN (CONTAINER)
# transitive verb, no indirect object
climbInVerb = Verb("climb", "climb in")
climbInVerb.addSynonym("get")
climbInVerb.addSynonym("enter")
climbInVerb.addSynonym("go")
climbInVerb.syntax = [["climb", "in", "<dobj>"], ["get", "in", "<dobj>"], ["climb", "into", "<dobj>"], ["get", "into", "<dobj>"], ["enter", "<dobj>"], ["go", "in", "<dobj>"], ["go", "into", "<dobj>"]]
climbInVerb.hasDobj = True
climbInVerb.dscope = "room"
#climbInVerb.preposition = ["in", "into"]

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
#climbOutVerb.preposition = ["out"]

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
#climbOutOfVerb.preposition = ["out", "of"]

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
			if isinstance(outer_loc, thing.Surface):
				outer_loc.addOn(me)
				return True
			elif isinstance(outer_loc, thing.Container):
				outer_loc.addIn(me)
				return True
			elif isinstance(outer_loc, room.Room):
				outer_loc.addThing(me)
				return True
			else:
				print("Unsupported outer location type: " + outer_loc.name)
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
	if dobj.lock_obj:
		if dobj.lock_obj.is_locked:
			try:
				app.printToGUI(dobj.cannotOpenLockedMsg)
			except:
				app.printToGUI((dobj.getArticle(True) + dobj.verbose_name).capitalize() + " is locked. ")
			return False
	runfunc = True
	
	if not skip:
		try:
			runfunc = dobj.openVerbDobj(me, app, iobj)
		except AttributeError:
			pass
		if not runfunc:
			return True

	try:
		state = dobj.is_open
	except AttributeError:
		app.printToGUI("You cannot open " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		return False
	if state==False:
		app.printToGUI("You open " + dobj.getArticle(True) + dobj.verbose_name + ". ")
		dobj.makeOpen()
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
	
	if isinstance(dobj, thing.Container) or isinstance(dobj, thing.Door):
		if dobj.lock_obj:
			if dobj.lock_obj.is_locked:
				if dobj.lock_obj.key_obj:
					if dobj.lock_obj.key_obj.ix in me.contains:
						app.printToGUI("(Using " + dobj.lock_obj.key_obj.getArticle(True) + dobj.lock_obj.key_obj.verbose_name + ")")
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
				if dobj.key_obj.ix in me.contains:
					app.printToGUI("(Using " + dobj.key_obj.getArticle(True) + dobj.key_obj.verbose_name + ")")
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
	
	if isinstance(dobj, thing.Container) or isinstance(dobj, thing.Door):
		if dobj.is_open:
			if not closeVerb.verbFunc(me, app, dobj):
				app.printToGUI("Could not close " + dobj.verbose_name + ". ")
				return False
		if dobj.lock_obj:
			if not dobj.lock_obj.is_locked:
				if dobj.lock_obj.key_obj:
					if dobj.lock_obj.key_obj.ix in me.contains:
						app.printToGUI("(Using " + dobj.lock_obj.key_obj.getArticle(True) + dobj.lock_obj.key_obj.verbose_name + ")")
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
				if dobj.key_obj.ix in me.contains:
					app.printToGUI("(Using " + dobj.key_obj.getArticle(True) + dobj.key_obj.verbose_name + ")")
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
#unlockWithVerb.preposition = ["with", "using"]
unlockWithVerb.dscope = "near"
unlockWithVerb.iscope = "inv"

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
		if not runfunc:
			return True
	
	if isinstance(dobj, thing.Container) or isinstance(dobj, thing.Door):
		if dobj.lock_obj:
			if dobj.lock_obj.is_locked:
				if not isinstance(iobj, thing.Key):
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
#lockWithVerb.preposition = ["with", "using"]
lockWithVerb.dscope = "near"
lockWithVerb.iscope = "inv"

def lockWithVerbFunc(me, app, dobj, iobj, skip=False):
	"""Unlock a Door or Container with an lock
	Takes arguments me, pointing to the player, app, the PyQt5 GUI app, and dobj, a Thing
	Returns True when the function ends with dobj unlocked, or without a lock. Returns False on failure to unlock.  """
	if not skip:
		runfunc = True
		try:
			runfunc = dobj.lockVerbDobj(me, app)
		except AttributeError:
			pass
		if not runfunc:
			return True
	
	if isinstance(dobj, thing.Container) or isinstance(dobj, thing.Door):
		if dobj.is_open:
			if not closeVerb.verbFunc(me, app, dobj):
				app.printToGUI("Could not close " + dobj.verbose_name + ". ")
				return False
		if dobj.lock_obj:
			if not dobj.lock_obj.is_locked:
				if not isinstance(iobj, thing.Key):
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
goVerb.dtype = "Direction"

def goVerbFunc(me, app, dobj):
	"""Empty function which should never be evaluated
	Takes arguments me, pointing to the player, app, the PyQt5 application, and dobj, a Thing """
	pass
# replace the default verbFunc method
goVerb.verbFunc = goVerbFunc


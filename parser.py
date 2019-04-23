#import string
import re

# intficpy framework files
from . import vocab
from . import verb
from . import thing
from . import serializer

##############################################################
# PARSER.PY - the parser for IntFicPy 
# Contains the input loop and parsing functions for the framework
##############################################################

# used for disambiguation mode
class TurnInfo:
	ambiguous = False
	err = False
	verb = False
	dobj = False
	iobj = False
	
lastTurn = TurnInfo

# dictionary of creator-defined functions to be called in strings through <<funcName>> syntax
class InlineFuncs:
	functions = {}

inline = InlineFuncs

# creator-defined functions to be evaluated every turn
class RunEvery:
	def __init__(self):
		self.funcs = []
	
	def runAll(self, app):
		for func in self.funcs:
			func(app)
	
	def add(self, daemon):
		self.funcs.append(daemon)
	
	def remove(self, daemon):
		self.funcs.remove(daemon)

daemons = RunEvery()

# used on player commands to remove punctuation and convert to lowercase
# takes the raw user input (string)
# returns a string
def cleanInput(input_string):
	input_string = input_string.lower()
	input_string = re.sub(r'[^\w\s]','',input_string)
	return input_string

# convert input to a list of tokens
# takes a string as an argument, and returns a list of strings
def tokenize(input_string):
	# tokenize input with spaces
	tokens = input_string.split()
	#app.printToGUI(tokens)
	return tokens

# extract creator-defined inline functions with <<funcName>> syntax embeded in game text output
# called by printToGUI in gui.py, on every string printed
# takes arguments app, pointing to the PyQt application, and output_string, a string to be printed by the GUI
# calls functions
# returns the same string, without <<functions>>, and with the possible addition of string segments from creator-defined inline functions
def extractInline(app, output_string):
	output_tokens = tokenize(output_string)
	remove_func = []
	for i, word in enumerate(output_tokens):
		if word[0:2] == "<<":
			func = word[2:-2]
			if func in inline.functions:
				out = inline.functions[func](app)
				if isinstance(out, str):
					output_tokens[i] = out
				else:
					remove_func.append(word)
	for word in remove_func:
		output_tokens.remove(word)
	
	return " ".join(output_tokens)


# check for direction statement as in "west" or "ne"
# takes arguments app, pointing to the PyQt application, me, pointing to the player object, and input_tokens, a list of strings
# called every turn by parseInput
# returns a Boolean specifying whether the input is a travel command
def getDirection(me, app, input_tokens):
	from . import travel
	d = input_tokens[0]
	# if first word is "go", skip first word, assume next word is a direction
	if input_tokens[0]=="go" and len(input_tokens) > 0:
		d = input_tokens[1]
	if d in travel.directionDict:
		travel.directionDict[d](me, app)
		return True
	else:
		return False

# identify the verb
# takes arguments app, pointing to the PyQt application, and input_tokens, the tokenized player command (list of strings)
# called every turn by parseInput
# returns a two item list of a Verb object and an associated verb form (list of strings), or None
def getVerb(app, input_tokens):
	# look up first word in verb dictionary
	if input_tokens[0] in vocab.verbDict:
		verbs = list(vocab.verbDict[input_tokens[0]])
		verbs = matchPrepositions(verbs, input_tokens)
	else:
		if not lastTurn.ambiguous:
			app.printToGUI("I don't understand: " + input_tokens[0])
			lastTurn.err = True
		return None
	vbo = verbByObjects(app, input_tokens, verbs)
	return vbo

# disambiguates verbs based on syntax used
# takes arguments app, pointing to the PyQt application, input_tokens, the tokenized player command (list of strings), and verbs, a list of Verb objects (verb.py)
# called by getVerb
# iterates through verb list, comparing syntax in input to the entries in the .syntax property of the verb
# returns a two item list of a Verb object and an associated verb form (list of strings), or None 
def verbByObjects(app, input_tokens, verbs):
	nearMatch = []
	for cur_verb in verbs:
		for verb_form in cur_verb.syntax:
			i = len(verb_form)
			for word in verb_form:
				if word[0] != "<":
					if word not in input_tokens:
						break
					else:
						i = i - 1
				else:
					i = i - 1
			if i==0:
				nearMatch.append([cur_verb, verb_form])
	if len(nearMatch) == 0:
		app.printToGUI("Please rephrase")
		lastTurn.err = True
		return None
	else:
		removeMatch = []
		for pair in nearMatch:
			verb = pair[0]
			verb_form = pair[1]
			dobj = analyzeSyntax(app,verb_form, "<dobj>", input_tokens, False)
			iobj = analyzeSyntax(app, verb_form, "<iobj>", input_tokens, False)
			extra = checkExtra(verb_form, dobj, iobj, input_tokens)
			if dobj:
				dbool = len(dobj)!=0
			else:
				dbool = False
			if iobj:
				ibool = len(iobj)!=0
			else:
				ibool = False
			if len(extra) > 0:
				removeMatch.append(pair)
			elif (not verb.impDobj) and (dbool != verb.hasDobj):
				removeMatch.append(pair)
			elif (not verb.impIobj) and (ibool != verb.hasIobj):
				removeMatch.append(pair)
		for x in removeMatch:
			nearMatch.remove(x)
		if len(nearMatch)==1:
			return nearMatch[0]
		elif len(nearMatch) > 1:
			app.printToGUI("Please rephrase")
			lastTurn.err = True
			return None
		else:
			app.printToGUI("Please rephrase")
			lastTurn.err = True
			return None

# checks for words unaccounted for by verb form
# takes argument verb_form, a verb form (list of strings), dobj and iobj, the gramatical direct and indirect objects from the command (lists of strings), and input tokens, the tokenized player command (list of strings)
# called by verbByObjects
# returns a list, empty or containing one word strings (extra words)
def checkExtra(verb_form, dobj, iobj, input_tokens):
	accounted = []
	extra = list(input_tokens)
	for word in extra:
		if word in verb_form:
			accounted.append(word)
		if dobj:
			if word in dobj:
				accounted.append(word)
		if iobj:
			if word in iobj:
				accounted.append(word)
	for word in accounted:
		extra.remove(word)
	return extra

# check for prepositions in the tokenized player command, and remove any candidate verbs whose preposition does not match
# takes arguments verbs, a list of Verb objects (verb.py), and input_tokens, the tokenized player command (list of strings)
# called by getVerb
# returns a list of Verb objects or an empty list
def matchPrepositions(verbs, input_tokens):
	prepositions = ["in", "out", "up", "down", "on", "under", "over", "through", "at", "across", "with", "off"]
	remove_verb = []
	for p in prepositions:
		if p in input_tokens:
			for verb in verbs:
				if not verb.preposition==p:
					remove_verb.append(verb)
	for verb in remove_verb:
		verbs.remove(verb)
	return verbs

# match tokens in input with tokens in verb syntax verb_forms to choose which syntax to assume
# takes arguments app, pointing to the PyQt application, cur_verb, the Verb object (verb.py) being anaylzed, and input_tokens, the tokenized player command (list of strings)
# returns the most probable verb_form (list of strings), or None
def getVerbSyntax(app, cur_verb, input_tokens):
	for verb_form in cur_verb.syntax:
		i = len(verb_form)
		for word in verb_form:
			if word[0] != "<":
				if word not in input_tokens:
					break
				else:
					i = i - 1
			else:
				i = i - 1
		if i==0:
			return verb_form
	app.printToGUI("I don't understand. Try rephrasing.")
	lastTurn.err = True
	return None

# analyze input using the chosen verb_form to find any objects
# takes arguments me, pointing to the player, a Player object (player.py), app, the PyQt application, cur_ver, a Verb object (verb.py), input_tokens, the tokenized player command (list of strings), and verb_form, the assumed syntax of the command (list of strings)
# called by parseInput
# returns None or a list of two items, either lists of strings, or None
def getGrammarObj(me, app, cur_verb, input_tokens, verb_form):
	# first, choose the correct syntax
	if not verb_form:
		return None
	# if verb_object.hasDobj, search verb.syntax for <dobj>, get index
	# get Dobj
	if cur_verb.hasDobj:
		dobj = analyzeSyntax(app, verb_form, "<dobj>", input_tokens)
	else:
		dobj = None
	# get Iobj
	if cur_verb.hasIobj:	
		iobj = analyzeSyntax(app, verb_form, "<iobj>", input_tokens)
	else:
		iobj = None
	return checkObj(me, app, cur_verb, dobj, iobj)

# parse verb form (list of strings) to find the words directly preceding and following object tags, and pass these to getObjWords find the objects in the player's command
# takes arguments app, the PyQt application, verb_form, the assumed syntax of the command (list of strings), 
# tag (string, "<dobj>" or "<iobj>"), input_tokens (list of strings) and print_verb_error (Boolean), False when called by verbByObjects
# NOTE: print_verb_error prevents the duplication of the error message in the event of improper Verb definition. A little bit hacky. 
# called by getVerbSyntax and verbByObjects
# returns None or a list of strings
def analyzeSyntax(app, verb_form, tag, input_tokens, print_verb_error=True):
	# get words before and after
	if tag in verb_form:
		obj_i = verb_form.index(tag)
	else:
		if print_verb_error:
			app.printToGUI("ERROR: Inconsistent verb definitition.")
		return None
	before = verb_form[obj_i - 1]
	if obj_i+1<len(verb_form):
		after = verb_form[obj_i + 1]
	else:
		after = None
	return getObjWords(app, before, after, input_tokens)

# make sure that the player command contains the correct number of grammatical objects, and get implied objects if applicable
# takes arguments me, app, cur_verb (Verb object, verb.py), dobj, the direct object of the command (list of strings or None), and iobj, the indirect object (list of strings or None)
# called by  getGrammarObj
# returns None, or a list of two items, either lists of strings, or None
def checkObj(me, app, cur_verb, dobj, iobj):
	missing = False
	if cur_verb.hasDobj and not dobj:
		if cur_verb.impDobj:
			dobj = cur_verb.getImpDobj(me, app)
			if not dobj:
				missing = True
			else:
				dobj = [dobj.verbose_name]
		else:
			app.printToGUI("Please be more specific")
			lastTurn.err = True
			return None
	if cur_verb.hasIobj and not iobj:
		if cur_verb.impIobj:
			iobj = cur_verb.getImpIobj(me, app)
			if not iobj:
				missing = True
			else:
				iobj = [iobj.verbose_name]
		else:
			app.printToGUI("Please be more specific")
			lastTurn.err = True
			missing = True
	lastTurn.dobj = dobj
	lastTurn.iobj = iobj
	if missing:
		return False
	return [dobj, iobj]
	
# create a list of all nouns and adjectives (strings) referring to a direct or indirect object
# takes arguments app, pointing to the PyQt application, before, the word expected before the grammatical object (string), after, the word expected after the grammatical object (string or None), and input_tokens, the tokenized player command (list of strings)
# called by analyzeSyntax
# returns an array of strings or None
def getObjWords(app, before, after, input_tokens):
	low_bound = input_tokens.index(before)
	# add 1 for non-inclusive indexing
	low_bound = low_bound + 1
	if after:
		high_bound = input_tokens.index(after)
		obj_words = input_tokens[low_bound:high_bound]
	else:
		obj_words = input_tokens[low_bound:]
	if len(obj_words) == 0:
		#app.printToGUI("I don't undertand. Please be more specific.")
		return None
	return obj_words

# eliminates all grammatical object candidates that are not within the scope of the current verb
# takes arguments me, things, a list of Thing objects (thing.py) that are candidates for the target of a player's action, and scope, a string representing the range of the verb
# called by getThing
# returns a list of Thing objects, or an empty list
def checkRange(me, things, scope):
	out_range = []
	if scope=="wearing":
		for thing in things:
			if (thing not in me.wearing):
				out_range.append(thing)
	elif scope=="room":
		for thing in things:
			if (thing not in me.location.contains) and (thing not in me.location.sub_contains):
				out_range.append(thing)
	elif scope=="knows":
		for thing in things:
			if thing not in me.knows_about:
				out_range.append(thing)
	elif scope=="near":
		for thing in things:
			if (thing not in me.location.contains) and (thing not in me.location.sub_contains) and (thing not in me.inventory) and (thing not in me.sub_inventory):
				out_range.append(thing)
	else:
		# assume scope equals "inv"
		for thing in things:
			if (thing not in me.inventory) and (thing not in me.sub_inventory):
				# TODO: things currently being worn should not be eliminated
				out_range.append(thing)
	for thing in out_range:
		things.remove(thing)
	
	return things

# prints the appropriate Thing out of scope message
# takes arguments app, pointing to the PyQt app, scope, a string, and noun_adj_arr, a list of strings
# called by getThing and checkAdjectives
# returns None
def verbScopeError(app, scope, noun_adj_arr):
	noun = " ".join(noun_adj_arr)
	if scope=="wearing":
		app.printToGUI("You aren't wearing any " + noun + ".")
		lastTurn.err = True
		return None
	elif scope=="room" or scope =="near":
		app.printToGUI("I don't see any " + noun + " here.")
		lastTurn.err = True
		return None
	elif scope=="knows":
		# assuming scope = "inv"
		app.printToGUI("You don't know of any " + noun + ".")
		lastTurn.err = True
		return None
	else:
		# assuming scope = "inv"
		app.printToGUI("You don't have any " + noun + ".")
		lastTurn.err = True
		return None

# get the Thing object in range associated with a list of adjectives and a noun
# takes arguments me, app, noun_adj_array, a list of strings referring to an in game item, taken from the player command, and scope, a string specifying the range of the verb
# called by callVerb
# returns a single Thing object (thing.py) or None
def getThing(me, app, noun_adj_arr, scope):
	# get noun (last word)
	noun = noun_adj_arr[-1]
	# get list of associated Things
	if noun in vocab.nounDict:
		# COPY the of list Things associated with a noun to allow for element deletion during disambiguation (in checkAdjectives)
		# the list will usually be fairly small
		things = list(vocab.nounDict[noun])
		things = checkRange(me, things, scope)
	else:
		things = []
	if len(things) == 0:
		return verbScopeError(app, scope, noun_adj_arr)
	elif len(things) == 1:
		return things[0]
	else:
		thing = checkAdjectives(app, noun_adj_arr, noun, things, scope)
		return thing

# if there are multiple Thing objects matching the noun, check the adjectives to narrow down to exactly 1
# takes arguments app, noun_adj_arr, a list of strings referring to an in game item, taken from the player command, noun (string), things, a list of Thing objects (things.py) that are candidates for the target of the player's action, and scope, a string specifying the range of the verb
# called by getThing
# returns a single Thing object or None
def checkAdjectives(app, noun_adj_arr, noun, things, scope):
	adj_i = noun_adj_arr.index(noun) - 1
	not_match = []
	while adj_i>=0 and len(things) > 1:
		# check preceding word as an adjective
		for thing in things:
			#app.printToGUI(thing.adjectives)
			#app.printToGUI(noun_adj_arr[adj_i])
			if noun_adj_arr[adj_i] not in thing.adjectives:
				not_match.append(thing)
				#app.printToGUI("no")
		for item in not_match:
			#app.printToGUI("removing " + item.adjectives[0])
			things.remove(item)
		adj_i = adj_i- 1
	if len(things)==1:
		return things[0]
	elif len(things) >1:
		app.printToGUI("Which " + noun + " do you mean?") # will be modified to allow for input of just noun/adjective pair
		# turn ON disambiguation mode for next turn
		lastTurn.ambiguous = True
		return None
	else:
		return verbScopeError(app, scope, noun_adj_arr)
			
# gets the Thing objects (if any) referred to in the player command, then calls the verb function
# takes arguments me, app, cur_verb, a Verb object (verb.py), and obj_words, a list with two items representing the grammatical direct and indirect objects, either lists of strings, or None
# called by parseInput and disambig
# returns a Boolean, True if a verb function is successfully called, False otherwise
def callVerb(me, app, cur_verb, obj_words):
	if cur_verb.hasDobj and obj_words[0]:
		cur_dobj = getThing(me, app, obj_words[0], cur_verb.dscope)
		lastTurn.dobj = cur_dobj
	else:
		cur_dobj = False
		lastTurn.dobj = False
	if cur_verb.hasIobj and obj_words[1]:
			cur_iobj = getThing(me, app, obj_words[1], cur_verb.iscope)
			lastTurn.iobj = cur_iobj
	else:
		cur_iobj = False
		lastTurn.iobj = False
	# apparent duplicate checking of objects is to allow last.iobj to be set before the turn is aborted in event of incomplete input
	
	if cur_dobj in me.sub_inventory:
		app.printToGUI("(First removing " + cur_dobj.getArticle(True) + cur_dobj.verbose_name + " from " + cur_dobj.location.getArticle(True) + cur_dobj.location.verbose_name + ")")
		cur_dobj.location.removeThing(cur_dobj)
		me.inventory.append(cur_dobj)
	
	if cur_iobj in me.sub_inventory:
		app.printToGUI("(First removing " + cur_iobj.getArticle(True) + cur_iobj.verbose_name + " from " + cur_iobj.location.getArticle(True) + cur_iobj.location.verbose_name + ")")
		cur_iobj.location.removeThing(cur_iobj)
		me.inventory.append(cur_iobj)
	
	if cur_verb.hasIobj:
		if not cur_dobj or not cur_iobj:
			return False
		else:
			cur_verb.verbFunc(me, app, cur_dobj, cur_iobj)
			return True
	elif cur_verb.hasDobj:
		if not cur_dobj:
			return False
		else:
			cur_verb.verbFunc(me, app, cur_dobj)
			return True
	else:
		cur_verb.verbFunc(me, app)
		return True

# when disambiguation mode is active, use the player input to specify the target for the previous turn's ambiguous command
# takes arguments me, app, and input_tokens
# called by parseInput
# returns a Boolean, True if disambiguation successful
def disambig(me, app, input_tokens):
	dobj = lastTurn.dobj
	iobj = lastTurn.iobj
	cur_verb = lastTurn.verb
	if isinstance(dobj, list):
		dobj = getThing(me, app, dobj, cur_verb.dscope)
	if isinstance(iobj, list):
		iobj = getThing(me, app, iobj, cur_verb.iscope)
		
	if not dobj and cur_verb.hasDobj:
		dobj = input_tokens
		if iobj!=False:
			iobj = [iobj.name]
	elif not iobj and cur_verb.hasIobj:
		iobj = input_tokens
		if dobj!=False:
			dobj = [dobj.name]
	obj_words = [dobj, iobj]	
	lastTurn.ambiguous = False
	lastTurn.err = False
	if not obj_words:
		return False
	callVerb(me, app, cur_verb, obj_words)
	return True

# wrapper for room describe function (room.py)
def roomDescribe(me, app):
	me.location.describe(me, app)

# checks if the player has entered a save or load command
# takes arguments input_tokens, the tokenized player command (list of strings), me, the player (Player object, player.py), and app, the PyQt application
# called by parseInput
# returns a Bool
def saveLoadCheck(input_tokens, me, app):
	if len(input_tokens)==2 and input_tokens[0]=="save":
		serializer.curSave.saveState(me, input_tokens[1])
		app.printToGUI("Game saved to " + input_tokens[1] + ".sav")
		return True
	elif input_tokens[0]=="save":
		#app.printToGUI("To save, please type save followed by a file name with no spaces.")
		fname = app.getSaveFileGUI()
		print(fname)
		if len(fname) > 0:
			serializer.curSave.saveState(me, fname)
			app.printToGUI("Game saved to " + fname)
		else:
			app.printToGUI("Could not save game")
		return True
	elif len(input_tokens)==2 and input_tokens[0]=="load":
		if serializer.curSave.loadState(me, input_tokens[1], app):
			app.printToGUI("Game loaded from " + input_tokens[1] + ".sav")
		else:
			app.printToGUI("Error loading game.")
		return True
	elif input_tokens[0]=="load":
		#app.printToGUI("To save, please type save followed by a file name with no spaces.")
		fname = app.getLoadFileGUI()
		
		if serializer.curSave.loadState(me, fname, app):
			app.printToGUI("Game loaded from " + fname)
		else:
			app.printToGUI("Error loading game. Please select a valid .sav file")
		return True
	else:
		return False

# parse player input, and respond to commands each turn
# takes arguments me, the player (Player object, player.py), app, the PyQt application, and input_string, the raw player input
# called by mainLoop in terminal version, turnMain (gui.py) in GUI version
# returns 0 when complete
def parseInput(me, app, input_string):
	# clean and tokenize
	input_string = cleanInput(input_string)
	input_tokens = tokenize(input_string)
	if len(input_tokens)==0:
		#app.printToGUI("I don't understand.")
		#lastTurn.err = True
		return 0
	if saveLoadCheck(input_tokens, me, app):
		return 0
	# if input is a travel command, move player 
	d = getDirection(me, app, input_tokens)
	if d:
		return 0
	gv = getVerb(app, input_tokens)
	if gv:
		cur_verb = gv[0]
	else:
		cur_verb = False
	if not cur_verb:
		if lastTurn.ambiguous:
			disambig(me, app, input_tokens)
			return 0
		return 0
	else:
		lastTurn.verb = cur_verb
	obj_words = getGrammarObj(me, app, cur_verb, input_tokens, gv[1])
	if not obj_words:
		return 0
	# turn OFF disambiguation mode for next turn
	lastTurn.ambiguous = False
	lastTurn.err = False
	callVerb(me, app, cur_verb, obj_words)
	return 0

# called when the game is opened to show opening and describe the first room
# takes arguments me, the player (Player object, player.py) and app, the PyQt application
# called in the creator's main game file 
def initGame(me, app):
	quit = False
	if not me.gameOpening == False:
		me.gameOpening(app)
		app.newBox(1)
	roomDescribe(me, app)
	daemons.runAll(app)

# main loop for terminal version; not used in GUI version
# NOT UP TO DATE. MAY REQUIRE MODIFICATION TO FUNCTION CORRECTLY
# takes arguments me, the player (Player object, player.py) and app, an object defined in the creator's main game file
# app must have a method printToGUI which prints to the TERMINAL. the method is so named for compatibility with the GUI version
def mainLoop(me, app):
	quit = False
	roomDescribe(me, app)
	while not quit:
		# first, print room description
		#me.location.describe()
		input_string = input("> ")
		# check for quit command
		if(input_string=="q" or input_string=="quit"):
			print("Goodbye.")
			quit = True
		elif len(input_string)==0:
			continue
		else:
			# parse string
			if (not lastTurn.ambiguous) and (not lastTurn.err):
				daemons.runAll(app)
			parseInput(me, app, input_string)
print("") # empty line for output formatting

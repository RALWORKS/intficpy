import string
#import re
import importlib

# intficpy framework files
from . import vocab
from . import verb
from . import thing
from . import serializer
from . import room

##############################################################
# PARSER.PY - the parser for IntFicPy 
# Contains the input loop and parsing functions for the framework
##############################################################
# TODO: Fix save system for terminal version

class TurnInfo:
	"""Class of lastTurn, used for disambiguation mode """
	things = []
	ambiguous = False
	err = False
	verb = False
	dobj = False
	iobj = False
	ambig_noun = None
	find_by_loc = False
	turn_list = []
	back = 0
	gameOpening = False
	gameEnding = False
	convNode = False
	specialTopics = {}
	
lastTurn = TurnInfo

class RunEvery:
	"""Class of daemons, an object containing creator-defined functions to be evaluated every turn """
	def __init__(self):
		self.funcs = []
	
	def runAll(self, me, app):
		for func in self.funcs:
			func(me, app)
	
	def add(self, daemon):
		self.funcs.append(daemon)
	
	def remove(self, daemon):
		if daemon in self.funcs:
			self.funcs.remove(daemon)

daemons = RunEvery()

class gameInfo:
	def __init__(self):
		self.title = "IntFicPy Game"
		self.author = "Unnamed"
		self.basic_instructions = "This is a parser-based game, which means the user interacts by typing commands. <br><br>A command should be a simple sentence, starting with a verb, for instance, <br>> JUMP<br>> TAKE UMBRELLA<br>> TURN DIAL TO 7<br><br>The parser is case insensitive, and ignores punctuation and articles (a, an, the). <br><br>It can be difficult at times to figure out the correct verb to perform an action. Even once you have the correct verb, it can be hard to get the right phrasing. In these situations, you can view the full list of verbs in the game using the VERBS command. You can also view the accepted phrasings for a specific verb with the VERB HELP command (for instance, type VERB HELP WEAR).<br><br>This game does not have quit and restart commands. To quit, simply close the program. To restart, open it again.<br><br>Typing SAVE will open a dialogue to create a save file. Typing LOAD will allow you to select a save file to restore. "
		self.game_instructions = None
		self.intFicPyCredit = True
		self.desc = None
		self.showVerbs = True
		self.betaTesterCredit = None
		self.customMsg = None
		self.verbs = []
		self.discovered_verbs = []
		self.help_msg = None
		self.main_file = None
	
	def setInfo(self, title, author):
		self.title = title
		self.author = author
	
	def printAbout(self, app):
		if self.customMsg:
			app.printToGUI(self.customMsg)
		else:
			app.printToGUI("<b>" + self.title + "</b>")
			app.printToGUI("<b>Created by " + self.author + "</b>")
			if self.intFicPyCredit:
				app.printToGUI("Built with JSMaika's IntFicPy parser")
			if self.desc:
				app.printToGUI(self.desc)
			if self.betaTesterCredit:
				app.printToGUI("<b>Beta Testing Credits</b>")
				app.printToGUI(self.betaTesterCredit)
	
	def printInstructions(self, app):
		app.printToGUI("<b>Basic Instructions</b>")
		app.printToGUI(self.basic_instructions)
		if self.game_instructions:
			app.printToGUI("<b>Game Instructions</b>")
			app.printToGUI(self.game_instructions)
				
	def printHelp(self, app):	
		if self.help_msg:
			app.printToGUI(self.help_msg)
		#self.printVerbs(app)
		app.printToGUI("Type INSTRUCTIONS for game instructions, or VERBS for a full list of accepted verbs. ")
	
	def printVerbs(self, app):
		app.printToGUI("<b>This game accepts the following basic verbs: </b>")
		self.verbs = sorted(self.verbs)
		verb_list = ""
		for verb in self.verbs:
			verb_list = verb_list + verb
			if verb!=self.verbs[-1]:
				verb_list = verb_list + ", "
		app.printToGUI(verb_list)
		if len(self.discovered_verbs) > 0:
			app.printToGUI("<b>You have discovered the following additional verbs: ")
			d_verb_list = ""
			for verb in self.discovered_verbs:
				verb_list = verb_list + verb
				if verb!=self.verbs[-1]:
					d_verb_list = d_verb_list + ", "
			app.printToGUI(d_verb_list)
		app.printToGUI("For help with phrasing, type \"verb help\" followed by a verb for a complete list of acceptable sentence structures for that verb. This will work for any verb, regardless of whether it has been discovered. ")
	
aboutGame = gameInfo()

def cleanInput(input_string, record=True):
	"""Used on player commands to remove punctuation and convert to lowercase
	Takes the raw user input (string)
	Returns a string """
	input_string = input_string.lower()
	#input_string = re.sub(r'[^\w\s]','',input_string)
	exclude = set(string.punctuation)
	input_string = ''.join(ch for ch in input_string if ch not in exclude)
	if record:
		from .serializer import curSave
		lastTurn.turn_list.append(input_string)
		if curSave.recfile:
			curSave.recfile.write(input_string + "\n")
			curSave.recfile.flush()
	return input_string

def tokenize(input_string):
	"""Convert input to a list of tokens
	Takes a string as an argument, and returns a list of strings """
	# tokenize input with spaces
	tokens = input_string.split()
	return tokens

def removeArticles(tokens):
	for article in vocab.english.articles:
		while article in tokens:
			tokens.remove(article)
	return tokens

def extractInline(app, output_string, main_file):
	"""Extract creator-defined inline functions with <<funcName>> syntax embeded in game text output
	Called by printToGUI in gui.py, on every string printed
	Takes arguments app, pointing to the PyQt application, and output_string, a string to be printed by the GUI
	Calls functions
	Returns the same string, without <<functions>>, and with the possible addition of string segments from creator-defined inline functions """
	main_module = importlib.import_module(main_file)
	output_tokens = tokenize(output_string)
	i = 0
	while i < len(output_tokens):
		while (i+1) < len(output_tokens) and "<<" in output_tokens[i] and not ">>" in output_tokens[i]:
			output_tokens[i] = output_tokens[i] + " " + output_tokens[i+1]
			del output_tokens[i+1]
		i = i + 1
	remove_func = []
	for word_ix, word in enumerate(output_tokens):
		if word[0:2] == "<<":
			if not word[-2:] == ">>":
				print("Bad inline call \033[1m" + word + "\033[0m -- Missing \">>\" or missing trailing space")
				continue
			func = word[2:-2]
			if len(func)>1:
				func = "main_module." + func
				if "(" in func:
					start_arg = func.index("(") + 1
					end_arg = func.index(")")
					if func[start_arg:end_arg] != " " and func[start_arg:end_arg] != "":
						args = func[start_arg: end_arg]
						args = tokenize(args)
						arg2 = []
						i = 0
						while i < len(args):
							found = True
							try:
								eval(args[i])
							except:
								found = False
							if not found:	
								cur_arg = "main_module." + args[i]
							else:
								cur_arg = args[i]
							arg2.append(cur_arg)
							i = i + 1
						args = " ".join(arg2)
						func = func[:start_arg] + args + ")"
				out = eval(func)
				if isinstance(out, str):
					output_tokens[word_ix] = out
					if (word_ix + 1) < len(output_tokens):
						if output_tokens[word_ix + 1] in vocab.english.no_space_before:
							output_tokens[word_ix] = out + output_tokens[word_ix + 1]
							remove_func.append(output_tokens[word_ix + 1])
				else:
					remove_func.append(word)
	for word in remove_func:
		output_tokens.remove(word)
	return " ".join(output_tokens)

def getDirection(me, app, input_tokens):
	"""Check for direction statement as in "west" or "ne"
	Takes arguments app, pointing to the PyQt application, me, pointing to the player object, and input_tokens, a list of strings
	Called every turn by parseInput
	Returns a Boolean specifying whether the input is a travel command """
	from . import travel
	d = input_tokens[0]
	# if first word is "go", skip first word, assume next word is a direction
	if input_tokens[0]=="go" and len(input_tokens) == 2:
		d = input_tokens[1]
		if d in travel.directionDict:
			travel.directionDict[d](me, app)
			return True
	elif d in travel.directionDict and len(input_tokens)==1:
		if lastTurn.ambiguous:
			for item in lastTurn.things:
				if d in item.adjectives:
					return False
		travel.directionDict[d](me, app)
		return True
	else:
		return False

def getVerb(app, input_tokens):
	"""Identify the verb
	Takes arguments app, pointing to the PyQt application, and input_tokens, the tokenized player command (list of strings)
	Called every turn by parseInput
	Returns a two item list. The first is a Verb object and an associated verb form (list of strings), or None. 
	The second is True if potential verb matches were found, False otherwise  """
	# look up first word in verb dictionary
	if input_tokens[0] in vocab.verbDict:
		verbs = list(vocab.verbDict[input_tokens[0]])
		verbs = matchPrepKeywords(verbs, input_tokens)
	else:
		verbs = None
		if lastTurn.convNode:
			app.printToGUI("\"" + " ".join(input_tokens).capitalize() + "\" is not enough information to match a suggestion. ")
			lastTurn.err = True
		elif not lastTurn.ambiguous:
			app.printToGUI("I don't understand the verb: " + input_tokens[0])
			lastTurn.err = True
		return [None, False]
	vbo = verbByObjects(app, input_tokens, verbs)
	found_verbs = bool(verbs)
	return [vbo, True]

def verbByObjects(app, input_tokens, verbs):
	"""Disambiguates verbs based on syntax used
	Takes arguments app, pointing to the PyQt application, input_tokens, the tokenized player command (list of strings), and verbs, a list of Verb objects (verb.py)
	Called by getVerb
	Iterates through verb list, comparing syntax in input to the entries in the .syntax property of the verb
	Returns a two item list of a Verb object and an associated verb form (list of strings), or None """
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
		ambiguous_verb = False
		if lastTurn.ambig_noun:
			terms = vocab.nounDict[lastTurn.ambig_noun]
			for term in terms:
				if input_tokens[0] in term.adjectives or input_tokens[0] in term.synonyms:
					ambiguous_verb = True
				elif input_tokens[0]==term.name:
					ambiguous_verb = True
		if not ambiguous_verb:
			app.printToGUI("I understood as far as \""+ input_tokens[0] + "\".<br>(Type VERB HELP "+ input_tokens[0].upper() + " for help with phrasing.) ")
		lastTurn.err = True
		return None
	else:
		removeMatch = []
		for pair in nearMatch:
			verb = pair[0]
			verb_form = pair[1]
			# HERE!!!
			# check if dobj and iobj are adjacent
			objects = None
			adjacent = False
			if verb.hasDobj:
				d_ix = verb_form.index("<dobj>")
				if not "<dobj>"== verb_form[-1]:
					if verb_form[d_ix + 1]=="<iobj>":
						adjacent = True
				if verb_form[d_ix - 1]=="<iobj>":
					adjacent = True
			iobj = False
			dobj = False
			# get Dobj
			if adjacent and verb.dscope in ["text", "direction"]:
				objects = adjacentStrObj(app, verb_form, input_tokens, 0)
			elif adjacent and verb.iscope in ["text", "direction"]:
				objects = adjacentStrObj(app, verb_form, input_tokens, 1)
			else:
				dobj = analyzeSyntax(app, verb_form, "<dobj>", input_tokens, False)
				iobj = analyzeSyntax(app, verb_form, "<iobj>", input_tokens, False)
			if objects:
				dobj = objects[0]
				iobj = objects[1]
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
			elif (verb.dscope=="direction" and not directionRangeCheck(dobj)) or (verb.iscope=="direction" and not directionRangeCheck(iobj)):
				removeMatch.append(pair)
		for x in removeMatch:
			nearMatch.remove(x)
		if len(nearMatch)==1:
			return nearMatch[0]
		elif len(nearMatch) > 1:
			ambiguous_verb = False
			if lastTurn.ambig_noun:
				terms = vocab.nounDict[lastTurn.ambig_noun]
				for term in terms:
					if input_tokens[0] in term.adjectives or input_tokens[0] in term.synonyms:
						ambiguous_verb = True
					elif input_tokens[0]==term.name:
						ambiguous_verb = True
			if not ambiguous_verb:
				app.printToGUI("I understood as far as \""+ input_tokens[0] + "\".<br>(Type VERB HELP "+ input_tokens[0].upper() + " for help with phrasing.) ")
			lastTurn.err = True
			return None
		else:
			ambiguous_verb = False
			if lastTurn.ambig_noun:
				terms = vocab.nounDict[lastTurn.ambig_noun]
				for term in terms:
					if input_tokens[0] in term.adjectives or input_tokens[0] in term.synonyms:
						ambiguous_verb = True
					elif input_tokens[0]==term.name:
						ambiguous_verb = True
			if not ambiguous_verb:
				app.printToGUI("I understood as far as \""+ input_tokens[0] + "\".<br>(Type VERB HELP "+ input_tokens[0].upper() + " for help with phrasing.) ")
			lastTurn.err = True
			return None

def checkExtra(verb_form, dobj, iobj, input_tokens):
	"""Checks for words unaccounted for by verb form
	Takes argument verb_form, a verb form (list of strings), dobj and iobj, the gramatical direct and indirect objects from 
	the command (lists of strings), and input tokens, the 	tokenized player command (list of strings)
	Called by verbByObjects
	Returns a list, empty or containing one word strings (extra words)"""
	from . import vocab
	accounted = []
	extra = list(input_tokens)
	for word in extra:
		if word in verb_form:
			accounted.append(word)
		if dobj:
			if word in dobj:
				if word in vocab.english.prepositions or word in vocab.english.keywords:
					noun = dobj[-1]
					exempt = False
					if noun in vocab.nounDict:
						for item in vocab.nounDict[noun]:
							if word in item.adjectives:
								exempt = True
								break
					if exempt:
						accounted.append(word)
				else:
					accounted.append(word)
		if iobj:
			if word in iobj:
				if word in vocab.english.prepositions or word in vocab.english.keywords:
					noun = iobj[-1]
					exempt = False
					if noun in vocab.nounDict:
						for item in vocab.nounDict[noun]:
							if word in item.adjectives:
								exempt = True
								break
					if exempt:
						accounted.append(word)
				else:
					accounted.append(word)
	for word in accounted:
		if word in extra:
			extra.remove(word)
	return extra

def matchPrepKeywords(verbs, input_tokens):
	"""Check for prepositions in the tokenized player command, and remove any candidate verbs whose preposition does not match
	Takes arguments verbs, a list of Verb objects (verb.py), and input_tokens, the tokenized player command (list of strings)
	Not currently used by parser
	Returns a list of Verb objects or an empty list """
	remove_verb = []
	for p in vocab.english.prepositions:
		if p in input_tokens and len(input_tokens) > 1:
			exempt = False
			for verb in verbs:
				ix = input_tokens.index(p) + 1
				if ix<len(input_tokens):
					noun = input_tokens[ix]
					while not noun in vocab.nounDict:
						ix = ix + 1
						if ix >= len(input_tokens):
							break
						noun = input_tokens[ix]
					if noun in vocab.nounDict:
						for item in vocab.nounDict[noun]:
							if p in item.adjectives:
								exempt = True
				if p in ["up", "down", "in", "out"]:
					if verb.iscope=="direction" or verb.dscope=="direction":
						exempt = True
				if not verb.preposition and not exempt:
					remove_verb.append(verb)
				elif not p in verb.preposition and not exempt:
					remove_verb.append(verb)
	for p in vocab.english.keywords:
		if p in input_tokens and len(input_tokens) > 1:
			exempt = False
			for verb in verbs:
				ix = input_tokens.index(p) + 1
				if ix<len(input_tokens):
					noun = input_tokens[ix]
					while not noun in vocab.nounDict:
						ix = ix + 1
						if ix >= len(input_tokens):
							break
						noun = input_tokens[ix]
					if noun in vocab.nounDict:
						for item in vocab.nounDict[noun]:
							if p in item.adjectives:
								exempt = True
				if not verb.keywords and not exempt:
					remove_verb.append(verb)
				elif not p in verb.keywords and not exempt:
					remove_verb.append(verb)
	for verb in remove_verb:
		if verb in verbs:
			verbs.remove(verb)
	return verbs

def getVerbSyntax(app, cur_verb, input_tokens):
	"""Match tokens in input with tokens in verb syntax verb_forms to choose which syntax to assume
	Takes arguments app, pointing to the PyQt application, cur_verb, the Verb object (verb.py) being anaylzed, and input_tokens, the tokenized player command (list of strings)
	Returns the most probable verb_form (list of strings), or None """
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

def getGrammarObj(me, app, cur_verb, input_tokens, verb_form):
	"""Analyze input using the chosen verb_form to find any objects
	Takes arguments me, pointing to the player, a Player object (player.py), app, the PyQt application, cur_ver, a Verb object (verb.py),
	input_tokens, the tokenized player command (list of strings), and verb_form, the assumed syntax of the command (list of strings)
	Called by parseInput
	Returns None or a list of two items, either lists of strings, or None"""
	# first, choose the correct syntax
	if not verb_form:
		return None
	# check if dobj and iobj are adjacent
	objects = None
	adjacent = False
	if cur_verb.hasDobj:
		d_ix = verb_form.index("<dobj>")
		if not "<dobj>"== verb_form[-1]:
			if verb_form[d_ix + 1]=="<iobj>":
				adjacent = True
		if verb_form[d_ix - 1]=="<iobj>":
			adjacent = True
	# if verb_object.hasDobj, search verb.syntax for <dobj>, get index
	# get Dobj
	if adjacent and cur_verb.dscope in ["text", "direction"]:
		objects = adjacentStrObj(app, verb_form, input_tokens, 0)
	elif adjacent and cur_verb.iscope in ["text", "direction"]:
		objects = adjacentStrObj(app, verb_form, input_tokens, 1)
	else:
		if cur_verb.hasDobj:
			dobj = analyzeSyntax(app, verb_form, "<dobj>", input_tokens)
		else:
			dobj = None
		if cur_verb.hasIobj:
			iobj = analyzeSyntax(app, verb_form, "<iobj>", input_tokens)
		else:
			iobj = None
	if objects:
		dobj = objects[0]
		iobj = objects[1]
	return checkObj(me, app, cur_verb, dobj, iobj)

def adjacentStrObj(app, verb_form, input_tokens, strobj):
	vfd = verb_form.index("<dobj>")
	vfi = verb_form.index("<iobj>")
	if verb_form[-1] == "<dobj>":
		before = verb_form[vfi - 1]
		after = None
	elif verb_form[-1] == "<iobj>":
		before = verb_form[vfd -1]
		after = None
	elif vfi < vfd:
		before = verb_form[vfi - 1]
		after = verb_form[vfd + 1]
	else:
		before = verb_form[vfd - 1]
		after = verb_form[vfi + 1]
	b_ix = input_tokens.index(before) + 1
	if not after:
		a_ix = None
		objs = input_tokens[b_ix:]
	else:
		a_ix = input_tokens.index(after)
		objs = input_tokens[b_ix:a_ix]
	x = 0
	if strobj==0: # dobj is string
		if vfd > vfi:
			x = 1
	else: # iobj is string
		if vfd < vfi:
			x = 1
	
	if x==0: # thing follows string
		if not objs[-1] in vocab.nounDict:
			#app.printToGUI("Please rephrase ")
			return [None, None]
		things = vocab.nounDict[objs[-1]]
		i = len(objs) - 2
		while i > 0:
			accounted = False
			for item in things:
				if objs[i] in thing.adjectives:
					accounted = True
			if not accounted:
				end_str = i
				break
			elif i==1:
				end_str = i
			i = i - 1
		strobj = objs[:end_str]
		tobj = objs[end_str:]
	else: # string follows thing 
		noun = None
		for word in objs:
			if word in vocab.nounDict:
				noun = word
				break
		if not noun:
			#app.printToGUI("Please rephrase ")
			return [None, None]
		start_str = objs.index(noun) + 1
		end_str = len(objs) - 1
		strobj = objs[start_str:]
		tobj = objs[:start_str]
	
	if strobj==0:
		return [strobj, tobj]
	else:
		return [tobj, strobj]
		
		

# NOTE: print_verb_error prevents the duplication of the error message in the event of improper Verb definition. A little bit hacky. 
def analyzeSyntax(app, verb_form, tag, input_tokens, print_verb_error=True):
	"""Parse verb form (list of strings) to find the words directly preceding and following object tags, and pass these to getObjWords find the objects in the player's command
	Takes arguments app, the PyQt application, verb_form, the assumed syntax of the command (list of strings), tag (string, "<dobj>" or "<iobj>"),
	input_tokens (list of strings) and print_verb_error (Boolean), False when called by verbByObjects
	Called by getVerbSyntax and verbByObjects
	Returns None or a list of strings """
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

def checkObj(me, app, cur_verb, dobj, iobj):
	"""Make sure that the player command contains the correct number of grammatical objects, and get implied objects if applicable
	Takes arguments me, app, cur_verb (Verb object, verb.py), dobj, the direct object of the command (list of strings or None), and iobj, the indirect object (list of strings or None)
	Called by  getGrammarObj
	Returns None, or a list of two items, either lists of strings, or None"""
	missing = False
	if cur_verb.hasDobj and not dobj:
		if cur_verb.impDobj:
			dobj = cur_verb.getImpDobj(me, app)
			if not dobj:
				missing = True
			else:
				#dobj = [dobj.verbose_name]
				pass
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
				#iobj = [iobj.verbose_name]
				pass
		else:
			app.printToGUI("Please be more specific")
			lastTurn.err = True
			missing = True
	lastTurn.dobj = dobj
	lastTurn.iobj = iobj
	if missing:
		return False
	return [dobj, iobj]

def getObjWords(app, before, after, input_tokens):
	"""Create a list of all nouns and adjectives (strings) referring to a direct or indirect object
	Takes arguments app, pointing to the PyQt application, before, the word expected before the grammatical object (string), after,
	the word expected after the grammatical object (string or None), and input_tokens, the tokenized player command (list of strings)
	Called by analyzeSyntax
	Returns an array of strings or None """
	if before[0]=="<":
		# find the index of the first noun in the noun dict. if there is more than one, reject any that double as adjectives
		nounlist = []
		for word in input_tokens:
			if word in vocab.nounDict:
				nounlist.append(word)
		if len(nounlist)>2:
			i = 0
			delnoun = []
			while i < (len(nounlist) - 1):
				for item in vocab.nounDict[nounlist[i]]:
					if nounlist[i] in item.adjectives and  not nounlist[i] in delnoun:
						delnoun.append(nounlist[i])
			for noun in delnoun:
				nounlist.remove(delnoun)
		if len(nounlist) < 2:
			return None
		# set before to the first noun
		before = nounlist[0]
	if after:
		if after[0]=="<":
			# find the index of the first noun in the noun dict. if there is more than one, reject any that double as adjectives
			nounlist = []
			for word in input_tokens:
				if word in vocab.nounDict:
					nounlist.append(word)
			if len(nounlist)>2:
				i = 0
				delnoun = []
				while i < (len(nounlist) - 1):
					for item in vocab.nounDict[nounlist[i]]:
						if nounlist[i] in item.adjectives and  not nounlist[i] in delnoun:
							delnoun.append(nounlist[i])
				for noun in delnoun:
					nounlist.remove(delnoun)
			if len(nounlist)<2:
				return None
			# set after to directly after the first noun
			after_index = input_tokens.index(nounlist[0]) + 1
			after = input_tokens[after_index]

	low_bound = input_tokens.index(before)
	# add 1 for non-inclusive indexing
	low_bound = low_bound + 1
	if after:
		high_bound = input_tokens.index(after)
		obj_words = input_tokens[low_bound:high_bound]
	else:
		obj_words = input_tokens[low_bound:]
	if len(obj_words) == 0:
		return None
	return obj_words

def wearRangeCheck(me, thing):
	"""Check if the Thing is being worn
	Takes arguments me, pointing to the Player, and thing, a Thing
	Returns True if within range, False otherwise """
	if (thing.ix not in me.wearing):
		return False
	elif thing not in me.wearing[thing.ix]:
		return False
	else:
		return True

def roomRangeCheck(me, thing):
	"""Check if the Thing is in the current room
	Takes arguments me, pointing to the Player, and thing, a Thing
	Returns True if within range, False otherwise """
	out_loc = me.getOutermostLocation()
	if not out_loc.resolveDarkness(me):
		return False
	if thing.ix in me.contains:
		if thing in me.contains[thing.ix]:
			return False
	if thing.ix in me.sub_contains:
		if thing in me.sub_contains[thing.ix]:
			return False
	if thing.ix in out_loc.contains:
		if thing in out_loc.contains[thing.ix]:
			return True
	if thing.ix in out_loc.sub_contains:
		if thing in out_loc.sub_contains[thing.ix]:
			return True
	return False

def knowsRangeCheck(me, thing):
	"""Check if the Player knows about a Thing
	Takes arguments me, pointing to the Player, and thing, a Thing
	Returns True if within range, False otherwise """
	if not thing.known_ix in me.knows_about:
		return False
	else:
		return True

def nearRangeCheck(me, thing):
	"""Check if the Thing is near (room or contains)
	Takes arguments me, pointing to the Player, and thing, a Thing
	Returns True if within range, False otherwise """
	out_loc = me.getOutermostLocation()
	too_dark = not out_loc.resolveDarkness(me)
	found = False
	if thing.ix in out_loc.contains:
		if thing not in out_loc.contains[thing.ix]:
			pass
		elif too_dark:
			pass
		else:
			found = True
	if thing.ix in out_loc.sub_contains:
		if thing not in out_loc.sub_contains[thing.ix]:
			pass
		elif too_dark:
			pass
		else:
			found = True
	if thing.ix in me.contains:
		if thing not in me.contains[thing.ix]:
			pass
		else:
			found = True
	if thing.ix in me.sub_contains:
		if thing not in me.sub_contains[thing.ix]:
			pass
		else:
			found = True
	return found

def invRangeCheck(me, thing):
	"""Check if the Thing is in the Player contains
	Takes arguments me, pointing to the Player, and thing, a Thing
	Returns True if within range, False otherwise """
	if thing.ix in me.contains:
		if thing not in me.contains[thing.ix]:
			pass
		else:
			return True
	if thing.ix in me.sub_contains:
		if thing not in me.sub_contains[thing.ix]:
			return False
		else:
			return True
	return False

def directionRangeCheck(obj):
	from .travel import directionDict
	if isinstance(obj, list):
		if len(obj) > 1:
			return False
		else:
			obj = obj[0]
	if obj in directionDict:
		return True
	else:
		return False

def getUniqueConcepts(things):
	"""Eliminates all items with duplicate known_ix properties. """
	unique = []
	check_list = things
	while check_list:
		ref = check_list.pop()
		unique.append(ref)
		duplicates = []
		for thing in check_list:
			if thing.known_ix == ref.known_ix:
				duplicates.append(thing)
		for thing in duplicates:
			check_list.remove(thing)
	return unique

def checkRange(me, app, things, scope):
	"""Eliminates all grammatical object candidates that are not within the scope of the current verb
	Takes arguments me, things, a list of Thing objects (thing.py) that are candidates for the target of a player's action, and scope, a string representing the range of the verb
	Called by getThing
	Returns a list of Thing objects, or an empty list"""
	out_range = []
	if scope=="wearing":
		for thing in things:
			if not wearRangeCheck(me, thing):
				out_range.append(thing)
	elif scope=="room":
		for thing in things:
			if not roomRangeCheck(me, thing) and invRangeCheck(me, thing):
				#implicit drop
				verb.dropVerb.verbFunc(me, app, thing)
				pass
			elif not roomRangeCheck(me, thing):
				out_range.append(thing)
	elif scope=="knows":
		things = getUniqueConcepts(things)
		for thing in things:
			if not knowsRangeCheck(me, thing):
				out_range.append(thing)
	elif scope=="near" or scope=="roomflex":
		for thing in things:
			if not nearRangeCheck(me, thing):
				out_range.append(thing)
	elif scope=="inv" or scope=="invflex":
		for thing in things:
			if roomRangeCheck(me, thing):
				pass
			elif not invRangeCheck(me, thing):
				out_range.append(thing)
	else:
		print("ERROR: incorrect verb scope \"" + scope + "\".")
		things = []
	# remove items that require implicit actions in the event of ambiguity
	for thing in out_range:
		things.remove(thing)
	things2 = list(things)
	out_range = []
	if len(things) > 1:
		for thing in things:
			if scope in ["room", "roomflex"] and not roomRangeCheck(me, thing):
				out_range.append(thing)
			elif scope in ["inv", "invflex"]  and not invRangeCheck(me, thing):
				out_range.append(thing)
			elif thing.ignore_if_ambiguous:
				out_range.append(thing)
		for thing in out_range:
			things2.remove(thing)
		if len(things2) > 0:
			return things2
	return things

def verbScopeError(app, scope, noun_adj_arr, me):
	"""Prints the appropriate Thing out of scope message
	Takes arguments app, pointing to the PyQt app, scope, a string, and noun_adj_arr, a list of strings
	Called by getThing and checkAdjectives
	Returns None """
	noun = " ".join(noun_adj_arr)
	if scope=="wearing":
		app.printToGUI("You aren't wearing any " + noun + ".")
		lastTurn.err = True
		return None
	elif scope=="room" or scope =="near" or scope=="roomflex":
		out_loc = me.getOutermostLocation()
		if not out_loc.resolveDarkness(me):
			app.printToGUI("It's too dark to see anything. ")
		else:
			app.printToGUI("I don't see any " + noun + " here.")
		lastTurn.err = True
		return None
	elif scope=="knows":
		app.printToGUI("You don't know of any " + noun + ".")
		lastTurn.err = True
		return None
	elif scope=="direction":
		app.printToGUI(noun.capitalize() + " is not a direction I recognize. ")
	else:
		# assuming scope = "inv"/"invflex"
		app.printToGUI("You don't have any " + noun + ".")
		lastTurn.err = True
		return None

def getThing(me, app, noun_adj_arr, scope, far_obj, obj_direction):
	"""Get the Thing object in range associated with a list of adjectives and a noun
	Takes arguments me, app, noun_adj_array, a list of strings referring to an in game item, taken from the player command, 
	and scope, a string specifying the range of the verb
	Called by callVerb
	Returns a single Thing object (thing.py) or None """
	# get noun (last word)
	endnoun = True
	for item in lastTurn.things:
		if noun_adj_arr[-1] in item.adjectives:
			endnoun = False
	try:
		t_ix = int(noun_adj_arr[-1])
	except:
		t_ix = -1
	if lastTurn.things != [] and (noun_adj_arr[-1] not in vocab.nounDict or not endnoun):
		noun = lastTurn.ambig_noun
		if noun:
			noun_adj_arr.append(noun)
		things = lastTurn.things
	elif lastTurn.ambiguous and t_ix <= len(lastTurn.things) and t_ix > 0:
		lastTurn.ambiguous = False
		return lastTurn.things[t_ix - 1]
	else:
		noun = noun_adj_arr[-1]
		# get list of associated Things
		if noun in vocab.nounDict:
			# COPY the of list Things associated with a noun to allow for element deletion during disambiguation (in checkAdjectives)
			# the list will usually be fairly small
			things = list(vocab.nounDict[noun])
		else:
			things = []
	if len(things) == 0:
		return verbScopeError(app, scope, noun_adj_arr, me)
	else:
		thing = checkAdjectives(app, me, noun_adj_arr, noun, things, scope, far_obj, obj_direction)
		return thing

def verboseNamesMatch(things):
	"""Check if any of the potential grammatical objects have identical verbose names
	Takes the list of things associated with the direct or indirect object 
	Returns a list of two items: 
		Item one is True if duplicates are present, else False
		Item two is dictionary mapping verbose names to lists of Things from the input with that name"""
	duplicates_present = False
	name_dict = {}
	for item in things:
		if item.verbose_name in name_dict:
			name_dict[item.verbose_name].append(item)
		else:
			name_dict[item.verbose_name] = [item]
	for name in name_dict:
		if len(name_dict[name]) > 1:
			duplicates_present = True
			break
	return [duplicates_present, name_dict]

def locationsDistinct(things):
	"""Check if identically named items can be distinguished by their locations
	Takes a list of items to check
	Returns False if all locations are the same, True otherwise """
	locs = [item.location for item in things]
	return not locs.count(locs[1]) == len(locs)

def checkAdjectives(app, me, noun_adj_arr, noun, things, scope, far_obj, obj_direction):
	"""If there are multiple Thing objects matching the noun, check the adjectives to narrow down to exactly 1
	Takes arguments app, noun_adj_arr, a list of strings referring to an in game item, taken from the player command,noun (string), things, a list of Thing objects
	(things.py) that are 	candidates for the target of the player's action, and scope, a string specifying the range of the verb
	Called by getThing
	Returns a single Thing object or None"""
	if things==lastTurn.things:
		lastTurn.ambiguous = False
		lastTurn.things = []
		lastTurn.err = False
		lastTurn.ambig_noun = None
		try:
			n_select = int(noun_adj_arr[0])
		except:
			n_select = -1
		if n_select <= len(things) and n_select > 0:
			n_select = n_select - 1
			return things[n_select]
	if noun:
		adj_i = noun_adj_arr.index(noun) - 1
	else:
		adj_i = len(noun_adj_arr) - 1
	not_match = []
	while adj_i>=0 and len(things) > 1:
		# check preceding word as an adjective
		for thing in things:
			if noun_adj_arr[adj_i] not in thing.adjectives:
				not_match.append(thing)
		for item in not_match:
			if item in things:
				things.remove(item)
		adj_i = adj_i- 1
	things = checkRange(me, app, things, scope)
	if len(things) == 1 and things[0].far_away and not far_obj:
		app.printToGUI((things[0].getArticle(True) + things[0].verbose_name).capitalize() + " is too far away. ")
		return False
	elif len(things) > 1 and not far_obj:
		remove_far = []
		for item in things:
			if item.far_away:
				remove_far.append(item)
		if len(things) > len(remove_far):
			for item in remove_far:
				things.remove(item)
	if len(things) > 1 and obj_direction:
		remove_wrong = []
		for item in things:
			if item.direction:
				if item.direction != obj_direction:
					remove_wrong.append(item)
		if len(things) > len(remove_wrong):
			for item in remove_wrong:
				if item in things:
					things.remove(item)
	if len(things) > 1:
		remove_child = []
		for item in things:
			if item.is_composite:
				for item2 in things:
					if item2 in item.children:
						remove_child.append(item2)
		if len(things) > len(remove_child):
			for item in remove_child:
				if item in things:
					things.remove(item)
	if len(things)==1:	
			return things[0]
	elif len(things) >1:
		name_match = verboseNamesMatch(things)
		name_dict = name_match[1] # dictionary of verbose_names from the current set of things
		msg = "Do you mean "
		scanned_keys = []
		if name_match[0]: # there is at least one set of duplicate verbose_names
			things = [] # empty things to reorder elements according to the order printed, since we are using name_dict
			for name in name_dict: # use name_dict for disambiguation message composition rather than things
				scanned_keys.append(name)
				unscanned = list(set(name_dict.keys()) - set(scanned_keys))
				if len(name_dict[name]) > 1:
					if locationsDistinct(name_dict[name]):
						for item in name_dict[name]:
							things.append(item)
							loc = item.location
							if not loc:
								pass
							elif isinstance(loc, room.Room):
								msg += item.lowNameArticle(True) + " on " + loc.floor.lowNameArticle(True) + " (" + str(things.index(item) + 1) + ")"
							elif loc == me:
								msg += item.lowNameArticle(True) + " in your inventory (" + str(things.index(item) + 1) + ")"
							else:
								msg += item.lowNameArticle(True) + " " + loc.contains_preposition + " " + loc.lowNameArticle(True) + " (" + str(things.index(item) + 1) + ")"
							if item is name_dict[name][-1] and not len(unscanned):
								msg += "?"
							elif item is name_dict[name][-1] and len(unscanned) == 1 and len(name_dict[unscanned[0]])==1:
								msg += ", or "
							elif len(name_dict[name]) == 1:
								msg += ", "
							elif item is name_dict[name][-2] and not len(unscanned):
								msg += ", or "
							else:
								msg += ", "
					else:
						for item in name_dict[name]:
							things.append(item)
							msg += item.lowNameArticle(True)  + " (" + str(things.index(item) + 1) + ")"
							if item is name_dict[name][-1] and not len(unscanned):
								msg += "?"
							elif item is name_dict[name][-1] and len(unscanned) == 1 and len(name_dict[unscanned[0]])==1:
								msg += ", or "
							elif len(name_dict[name]) == 1:
								msg += ", "
							elif item is name_dict[name][-2] and not len(unscanned):
								msg += ", or "
							else:
								msg += ", "
				else:
					for item in name_dict[name]:
						things.append(item)
						msg += item.lowNameArticle(True)  + " (" + str(things.index(item) + 1) + ")"
						if item is name_dict[name][-1] and not len(unscanned):
							msg += "?"
						elif item is name_dict[name][-1] and len(unscanned) == 1 and len(name_dict[unscanned[0]])==1:
								msg += ", or "
						elif len(name_dict[name]) == 1:
							msg += ", "
						elif item is name_dict[name][-2] and not len(unscanned):
							msg += ", or "
						else:
							msg += ", "
		else:		
			for thing in things:
				msg = msg + thing.getArticle(True) + thing.verbose_name + " (" + str(things.index(thing) + 1) + ")"
				# add appropriate punctuation and "or"
				if thing is things[-1]:
					msg = msg + "?"
				elif thing is things[-2]:
					msg = msg + ", or "
				else:
					msg = msg + ", "
		app.printToGUI(msg)
		# turn ON disambiguation mode for next turn
		lastTurn.ambiguous = True
		lastTurn.ambig_noun = noun
		lastTurn.things = things
		return None
	else:
		return verbScopeError(app, scope, noun_adj_arr, me)

def callVerb(me, app, cur_verb, obj_words):
	"""Gets the Thing objects (if any) referred to in the player command, then calls the verb function
	Takes arguments me, app, cur_verb, a Verb object (verb.py), and obj_words, a list with two items representing the grammatical
	direct and indirect objects, either lists of strings, or None
	Called by parseInput and disambig
	Returns a Boolean, True if a verb function is successfully called, False otherwise"""
	# FIRST, check if dobj and or iobj have already been found
	# if not, set objs to None
	# checking dobj
	if cur_verb.hasDobj and not isinstance(obj_words[0], list):
		cur_dobj = obj_words[0]
	elif cur_verb.hasDobj and obj_words[0]:
		if isinstance(obj_words[0], thing.Thing):
			cur_dobj = obj_words[0]
		elif cur_verb.dscope=="text"  or cur_verb.dscope=="direction":
			cur_dobj = obj_words[0]
		else:
			cur_dobj = getThing(me, app, obj_words[0], cur_verb.dscope, cur_verb.far_dobj, cur_verb.dobj_direction)
		lastTurn.dobj = cur_dobj
	else:
		cur_dobj = None
		lastTurn.dobj = None
	# checking iobj
	if cur_verb.hasIobj and not isinstance(obj_words[1], list):
		cur_iobj = obj_words[1]
	elif cur_verb.hasIobj and obj_words[1]:
		if isinstance(obj_words[1], thing.Thing):
			cur_iobj = obj_words[1]
		elif cur_verb.iscope=="text" or cur_verb.iscope=="direction":
			cur_iobj = obj_words[1]
		else:
			cur_iobj = getThing(me, app, obj_words[1], cur_verb.iscope, cur_verb.far_iobj, cur_verb.iobj_direction)
		lastTurn.iobj = cur_iobj
	else:
		cur_iobj = None
		lastTurn.iobj = None
	# check if any of the item's component parts should be passed as dobj/iobj instead
	if cur_verb.iscope=="text" or cur_verb.iscope=="direction":
		pass
	if not cur_iobj:
		pass
	elif not isinstance(cur_iobj, thing.Container) and cur_verb.itype=="Container" and cur_iobj.is_composite and not isinstance(obj_words[1], thing.Thing):
		if cur_iobj.child_Containers != []:
			cur_iobj = checkAdjectives(app, me, obj_words[1], False, cur_iobj.child_Containers, cur_verb.iscope, cur_verb.far_iobj, cur_verb.iobj_direction)
			lastTurn.iobj = None
			if cur_iobj:
				app.printToGUI("(Assuming " + cur_iobj.getArticle(True) + cur_iobj.verbose_name + ".)")
				lastTurn.iobj = cur_iobj
	elif not isinstance(cur_iobj, thing.Surface) and cur_verb.itype=="Surface" and cur_iobj.is_composite and not isinstance(obj_words[1], thing.Thing):
		if cur_iobj.child_Surfaces != []:
			cur_iobj = checkAdjectives(app, me, obj_words[1], False, cur_iobj.child_Surfaces, cur_verb.iscope, cur_verb.far_iobj, cur_verb.iobj_direction)
			lastTurn.iobj = None
			if cur_iobj:
				app.printToGUI("(Assuming " + cur_iobj.getArticle(True) + cur_iobj.verbose_name + ".)")
				lastTurn.iobj = cur_iobj
	elif not isinstance(cur_iobj, thing.UnderSpace) and cur_verb.itype=="UnderSpace" and cur_iobj.is_composite and not isinstance(obj_words[1], thing.Thing):
		if cur_iobj.child_UnderSpaces != []:
			cur_iobj = checkAdjectives(app, me, obj_words[1], False, cur_iobj.child_UnderSpaces, cur_verb.iscope, cur_verb.far_iobj, cur_verb.iobj_direction)
			lastTurn.iobj = None
			if cur_iobj:
				#app.printToGUI("(Assuming " + cur_iobj.getArticle(True) + cur_iobj.verbose_name + ".)")
				lastTurn.iobj = cur_iobj
	if cur_verb.dscope=="text" or cur_verb.dscope=="direction":
		pass
	if not cur_dobj:
		pass
	elif not isinstance(cur_dobj, thing.Container) and cur_verb.dtype=="Container" and cur_dobj.is_composite and not isinstance(obj_words[0], thing.Thing):
		if cur_dobj.child_Containers != []:
			cur_dobj = checkAdjectives(app, me, obj_words[0], False, cur_dobj.child_Containers, cur_verb.dscope, cur_verb.far_dobj, cur_verb.dobj_direction)
			lastTurn.dobj = None
			if cur_dobj:
				app.printToGUI("(Assuming " + cur_dobj.getArticle(True) + cur_dobj.verbose_name + ".)")
				lastTurn.iobj = cur_dobj
	elif not isinstance(cur_dobj, thing.Surface) and cur_verb.dtype=="Surface" and cur_dobj.is_composite and not isinstance(obj_words[0], thing.Thing):
		if cur_dobj.child_Surfaces != []:
			cur_dobj = checkAdjectives(app, me, obj_words[0], False, cur_dobj.child_Surfaces, cur_verb.dscope, cur_verb.far_dobj, cur_verb.dobj_direction)
			lastTurn.dobj = False
			if cur_dobj:
				app.printToGUI("(Assuming " + cur_dobj.getArticle(True) + cur_dobj.verbose_name + ".)")
				lastTurn.iobj = cur_dobj
	elif not isinstance(cur_dobj, thing.UnderSpace) and cur_verb.dtype=="UnderSpace" and cur_dobj.is_composite and not isinstance(obj_words[0], thing.Thing):
		if cur_dobj.child_UnderSpaces != []:
			cur_dobj = checkAdjectives(app, me, obj_words[0], False, cur_dobj.child_UnderSpaces, cur_verb.dscope, cur_verb.far_dobj, cur_verb.dobj_direction)
			lastTurn.dobj = False
			if cur_dobj:
				#app.printToGUI("(Assuming " + cur_dobj.getArticle(True) + cur_dobj.verbose_name + ".)")
				lastTurn.iobj = cur_dobj
	# apparent duplicate checking of objects is to allow last.iobj to be set before the turn is aborted in event of incomplete input
	if cur_verb.dscope=="text" or not cur_dobj or cur_verb.dscope=="direction":
		pass
	elif not cur_dobj.location:
		pass
	elif cur_dobj.location.location==me and isinstance(cur_dobj, thing.Liquid):
		cur_dobj = cur_dobj.getContainer()
	elif cur_dobj.location.location==me and cur_verb.dscope=="inv":
		app.printToGUI("(First removing " + cur_dobj.getArticle(True) + cur_dobj.verbose_name + " from " + cur_dobj.location.getArticle(True) + cur_dobj.location.verbose_name + ")")
		success = verb.removeFromVerb.verbFunc(me, app, cur_dobj, cur_dobj.location)
		if not success:
			return False
	if cur_verb.iscope=="text" or not cur_iobj or cur_verb.iscope=="direction":
		pass
	elif not cur_iobj.location:
		pass
	elif cur_iobj.location.location==me and isinstance(cur_iobj, thing.Liquid):
		cur_iobj = cur_iobj.getContainer()
	elif cur_iobj.location.location==me and cur_verb.iscope=="inv":
		app.printToGUI("(First removing " + cur_iobj.getArticle(True) + cur_iobj.verbose_name + " from " + cur_iobj.location.getArticle(True) + cur_iobj.location.verbose_name + ")")
		success = verb.removeFromVerb.verbFunc(me, app, cur_iobj, cur_iobj.location)
		if not success:
			return False

	if cur_verb.hasIobj:
		if not cur_iobj:
			return False
		if cur_verb.iscope=="text" or cur_verb.iscope=="direction":
			pass
		elif cur_verb.iscope == "room" and invRangeCheck(me, cur_iobj):
			verb.dropVerb.verbFunc(me, app, cur_iobj)
		elif (cur_verb.iscope == "inv" or (cur_verb.iscope=="invflex" and cur_iobj is not me)) and roomRangeCheck(me, cur_iobj):
			app.printToGUI("(First attempting to take " + cur_iobj.getArticle(True) + cur_iobj.verbose_name + ") ")
			success = verb.getVerb.verbFunc(me, app, cur_iobj)
			if not success:	
				return False
			if not cur_iobj.invItem:
				app.printToGUI("You cannot take " + cur_iobj.getArticle(True) + cur_iobj.verbose_name + ".")
				return False
		elif cur_verb.iscope == "inv" and wearRangeCheck(me, cur_iobj):
			verb.doffVerb.verbFunc(me, app, cur_iobj)
			if cur_verb.dscope=="text"  or cur_verb.dscope=="direction":
				pass
			elif cur_verb.dscope == "room" and invRangeCheck(me, cur_dobj):
				verb.dropVerb.verbFunc(me, app, cur_dobj)
			elif (cur_verb.dscope == "inv" or (cur_verb.dscope=="invflex"  and cur_dobj is not me)) and roomRangeCheck(me, cur_dobj):
				app.printToGUI("(First attempting to take " + cur_dobj.getArticle(True) + cur_dobj.verbose_name + ") ")
				success = verb.getVerb.verbFunc(me, app, cur_dobj)
				if not success:	
					return False
	if cur_verb.hasDobj:
		if not cur_dobj:
			return False
		else:
			if cur_verb.dscope=="text"  or cur_verb.dscope=="direction":
				pass
			elif cur_verb.dscope == "room" and invRangeCheck(me, cur_dobj):
				verb.dropVerb.verbFunc(me, app, cur_dobj)
			elif (cur_verb.dscope == "inv" or (cur_verb.dscope=="invflex"  and cur_dobj is not me)) and roomRangeCheck(me, cur_dobj):
				app.printToGUI("(First attempting to take " + cur_dobj.getArticle(True) + cur_dobj.verbose_name + ") ")
				success = verb.getVerb.verbFunc(me, app, cur_dobj)
				if not success:
					return False
			elif cur_verb.dscope == "inv" and wearRangeCheck(me, cur_dobj):
				verb.doffVerb.verbFunc(me, app, cur_dobj)
			lastTurn.convNode = False
			lastTurn.specialTopics = {}
			if cur_verb.dscope=="text":
				cur_dobj = " ".join(cur_dobj)
			elif cur_verb.dscope=="direction":
				cur_dobj = " ".join(cur_dobj)
				correct = directionRangeCheck(cur_dobj)
				if not correct:
					app.printToGUI(cur_dobj.capitalize() + " is not a direction I recognize. ")
					return False
	if cur_verb.iscope=="text":
		cur_iobj = " ".join(cur_iobj)
	elif cur_verb.dscope=="text":
		cur_dobj = " ".join(cur_dobj)
	if cur_verb.iscope=="direction":
		cur_iobj = " ".join(cur_iobj)
		correct = directionRangeCheck(cur_iobj)
		if not correct:
			app.printToGUI(cur_iobj.capitalize() + " is not a direction I recognize. ")
			return False
	elif cur_verb.dscope=="direction":
		cur_dobj = " ".join(cur_dobj)
		correct = directionRangeCheck(cur_dobj)
		if not correct:
			app.printToGUI(cur_iobj.capitalize() + " is not a direction I recognize. ")
			return False

	lastTurn.convNode = False
	lastTurn.specialTopics = {}
	
	if cur_verb.hasDobj and cur_verb.hasIobj:
		if (cur_verb.dscope!="inv" or cur_verb.iscope!="inv") and me.position!="standing":
			verb.standUpVerb.verbFunc(me, app)
		cur_verb.verbFunc(me, app, cur_dobj, cur_iobj)
	elif cur_verb.hasDobj:
		if cur_verb.dscope!="inv" and cur_verb.dscope!="invflex" and me.position!="standing":
			verb.standUpVerb.verbFunc(me, app)
		cur_verb.verbFunc(me, app, cur_dobj)
	elif cur_verb.hasIobj:
		if cur_verb.iscope!="inv" and cur_verb.iscope!="invflex"  and me.position!="standing":
			verb.standUpVerb.verbFunc(me, app)
		cur_verb.verbFunc(me, app, cur_iobj)
	else:
		cur_verb.verbFunc(me, app)
	return True

def disambig(me, app, input_tokens):
	"""When disambiguation mode is active, use the player input to specify the target for the previous turn's ambiguous command
	Takes arguments me, app, and input_tokens
	called by parseInput
	Returns a Boolean, True if disambiguation successful """
	dobj = lastTurn.dobj
	iobj = lastTurn.iobj
	cur_verb = lastTurn.verb
	if not dobj and cur_verb.hasDobj:
		dobj = input_tokens
	elif not iobj and cur_verb.hasIobj:
		iobj = input_tokens
	obj_words = [dobj, iobj]	
	if not obj_words:
		return False
	callVerb(me, app, cur_verb, obj_words)
	return True

def roomDescribe(me, app):
	"""Wrapper for room describe function (room.py) """
	out_loc = me.getOutermostLocation()
	out_loc.describe(me, app)

# NOTE: typing "save" with no file specified currently breaks the terminal version
def saveLoadCheck(input_tokens, me, app):
	"""Checks if the player has entered a save or load command
	Takes arguments input_tokens, the tokenized player command (list of strings), me, the player (Player object, player.py), and app, the PyQt application
	Called by parseInput
	Returns a Boolean """
	if input_tokens[0]=="save":
		# app.getSaveFileGUI is not defined for terminal version
		fname = app.getSaveFileGUI()
		if not fname:
			app.newBox(app.box_style1)
			app.printToGUI("Could not save game")
		else:
			serializer.curSave.saveState(me, fname, aboutGame.main_file)
			app.printToGUI("Game saved to " + fname)
		return True
	elif input_tokens[0]=="load":
		fname = app.getLoadFileGUI()
		if serializer.curSave.loadState(me, fname, app, aboutGame.main_file):
			app.printToGUI("Game loaded from " + fname)
		else:
			app.printToGUI("Error loading game. Please select a valid .sav file")
		return True
	else:
		return False

def getConvCommand(me, app, input_tokens):
	possible_topics = list(lastTurn.specialTopics.keys())
	for key in lastTurn.specialTopics:
		tokens = cleanInput(key, False)
		tokens = tokenize(tokens)
		tokens = removeArticles(tokens)
		for tok in input_tokens:
			if tok not in tokens and tok=="i" and "you" in tokens:
				pass
			elif tok not in tokens and tok=="you" and "i" in tokens:
				pass
			elif tok not in tokens:
				possible_topics.remove(key)
				break
	revised_possible_topics = list(possible_topics)
	if len(possible_topics) > 1:
		for topicA in possible_topics:
			for topicB in possible_topics:
				if topicA != topicB and topicB in revised_possible_topics and topicA in revised_possible_topics:
					if lastTurn.specialTopics[topicA] == lastTurn.specialTopics[topicB]:
						revised_possible_topics.remove(topicB)
	if len(revised_possible_topics) != 1:
		return False
	else:
		x = revised_possible_topics[0]
		lastTurn.specialTopics[x].func(app)
		return True

def parseInput(me, app, input_string):
	"""Parse player input, and respond to commands each turn
	Takes arguments me, the player (Player object, player.py), app, the PyQt application, and input_string, the raw player input
	Called by mainLoop in terminal version, turnMain (gui.py) in GUI version
	Returns 0 when complete """
	# clean and tokenize
	input_string = cleanInput(input_string)
	input_tokens = tokenize(input_string)
	input_tokens = removeArticles(input_tokens)
	if not lastTurn.gameEnding:
		if len(input_tokens)==0:
			#app.printToGUI("I don't understand.")
			lastTurn.err = True
			return 0
		if saveLoadCheck(input_tokens, me, app):
			return 0
		if (input_tokens[0:2] == ["help", "verb"] or input_tokens[0:2]==["verb", "help"]) and len(input_tokens) > 2:
			from .verb import helpVerbVerb
			helpVerbVerb.verbFunc(me, app, input_tokens[2:])
			return 0
		elif input_tokens[0:2] == ["help", "verb"] or input_tokens[0:2]==["verb", "help"]:
			app.printToGUI("Please specify a verb for help. ")
			return 0
		# if input is a travel command, move player 
		d = getDirection(me, app, input_tokens)
		if d:
			lastTurn.convNode = False
			lastTurn.specialTopics = {}
			return 0
		if lastTurn.convNode:
			conv_command = getConvCommand(me, app, input_tokens)
			if conv_command:
				lastTurn.ambig_noun = None
				lastTurn.ambig_verb = None
				lastTurn.ambiguous = False
				return 0
			else:
				pass
		gv = getVerb(app, input_tokens)
		if gv[0]:
			cur_verb = gv[0][0]
		else:
			cur_verb = None
		if not cur_verb:
			if lastTurn.ambiguous and (not gv[1] or lastTurn.convNode):
				disambig(me, app, input_tokens)
				return 0
			return 0
		else:
			lastTurn.verb = cur_verb
		obj_words = getGrammarObj(me, app, cur_verb, input_tokens, gv[0][1])
		if not obj_words:
			return 0
		# turn OFF disambiguation mode for next turn
		lastTurn.ambig_noun = None
		lastTurn.ambig_verb = None
		lastTurn.ambiguous = False
		lastTurn.err = False
		callVerb(me, app, cur_verb, obj_words)
		return 0
	else:
		from .verb import scoreVerb, fullScoreVerb
		if input_tokens in [["save"], ["load"]]:
			app.newBox(app.box_style1)
		if input_tokens==["full", "score"]:
			fullScoreVerb.verbFunc(me, app)
		elif input_tokens==["score"]:
			scoreVerb.verbFunc(me, app)
		elif input_tokens==["fullscore"]:
			fullScoreVerb.verbFunc(me, app)
		elif input_tokens==["about"]:
			aboutGame.printAbout(app)
		else:
			app.printToGUI("The game has ended. Commands are SCORE, FULLSCORE, and ABOUT.")

def initGame(me, app, main_file):
	"""Called when the game is opened to show opening and describe the first room
	Takes arguments me, the player (Player object, player.py) and app, the PyQt application
	Called in the creator's main game file """
	quit = False
	aboutGame.main_file = main_file
	if not lastTurn.gameOpening == False:
		#app.newBox(app.box_style1)
		lastTurn.gameOpening(app)
	else:
		app.newBox(app.box_style1)
	roomDescribe(me, app)
	daemons.runAll(me, app)


# NOTE: This function has not been updated recently, and may require modification to accomodate all features
def mainLoop(me, app):
	"""Main loop for terminal version; not used in GUI version
	Takes arguments me, the player (Player object, player.py) and app, an object defined in the creator's main game file
	app must have a method printToGUI which prints to the TERMINAL. the method is so named for compatibility with the GUI version """
	quit = False
	roomDescribe(me, app)
	while not quit:
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
				daemons.runAll(me, app)
			parseInput(me, app, input_string)
	print("") # empty line for output formatting

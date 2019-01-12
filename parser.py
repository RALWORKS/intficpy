import string
import re

# intficpy framework files
import vocab
import verb
import thing
import travel


##############################################################
############### PARSER.PY - the parser for IntFicPy ##################
#### Contains the input loop and parsing functions for the framework #####
##############################################################
# used for disambiguation mode
class TurnInfo:
	ambiguous = False
	verb = False
	dobj = False
	iobj = False
	
lastTurn = TurnInfo

# convert input to a list of tokens
def tokenize(input_string):
	# tokenize input with spaces
	tokens = input_string.split()
	#print(tokens)
	return tokens

# check for direction statement as in "west" or "ne"
def getDirection(me, input_tokens):
	d = input_tokens[0]
	# if first word is "go", skip first word, assume next word is a direction
	if input_tokens[0]=="go" and len(input_tokens) > 0:
		d = input_tokens[1]
	if d in travel.directionDict:
		travel.directionDict[d](me)
		return True
	else:
		return False

# identify the verb
def getVerb(input_tokens):
	# look up first word in verb dictionary
	if input_tokens[0] in vocab.verbDict:
		verbs = list(vocab.verbDict[input_tokens[0]])
		verbs = matchPrepositions(verbs, input_tokens)
	else:
		if not lastTurn.ambiguous:
			print("I don't understand: " + input_tokens[0])
		return False
	if len(verbs)==1:
		return verbs[0]
	else:
		print("Please rephrase")
		return False

def matchPrepositions(verbs, input_tokens):
	prepositions = ["in", "out", "up", "down", "on", "under", "over", "through", "at", "across", "with"]
	remove_verb = []
	for p in prepositions:
		if p in input_tokens:
			for verb in verbs:
				if not verb.preposition==p:
					remove_verb.append(verb)
	for verb in remove_verb:
		verbs.remove(verb)
	return verbs

# match tokens in input with tokens in verb syntax forms to choose which syntax to assume
def getVerbSyntax(cur_verb, input_tokens):
	for form in cur_verb.syntax:
		i = len(form)
		for word in form:
			if word[0] != "<":
				if word not in input_tokens:
					break
				else:
					i = i - 1
			else:
				i = i - 1
		if i==0:
			return form
	print("I don't understand. Try rephrasing.")
	return False

# analyse input using verb syntax form to find any objects
def getGrammarObj(me, cur_verb, input_tokens):
	# first, choose the correct syntax
	form = getVerbSyntax(cur_verb, input_tokens)
	if not form:
		return False
	# if verb_object.hasDobj, search verb.syntax for <dobj>, get index
	# get Dobj
	if cur_verb.hasDobj:
		dobj = analyzeSyntax(form, "<dobj>", input_tokens)
	else:
		dobj = False
	# get Iobj
	if cur_verb.hasIobj:	
		iobj = analyzeSyntax(form, "<iobj>", input_tokens)
	else:
		iobj = False
	return checkObj(me, cur_verb, dobj, iobj)

def analyzeSyntax(verb_form, tag, input_tokens):
	# get words before and after
	if tag in verb_form:
		obj_i = verb_form.index(tag)
	else:
		print("ERROR: Inconsistent verb definitition.")
		return False
	before = verb_form[obj_i - 1]
	if obj_i+1<len(verb_form):
		after = verb_form[obj_i + 1]
	else:
		after = False
	return getObjWords(before, after, input_tokens)

def checkObj(me, cur_verb, dobj, iobj):
	missing = False
	if cur_verb.hasDobj and not dobj:
		if cur_verb.impDobj:
			dobj = cur_verb.getImpDobj(me)
			if not dobj:
				missing = True
			else:
				dobj = [dobj.verbose_name]
		else:
			print("Please be more specific")
			return False
	if cur_verb.hasIobj and not iobj:
		if cur_verb.impIobj:
			iobj = cur_verb.getImpIobj(me)
			if not iobj:
				missing = True
			else:
				iobj = [iobj.verbose_name]
		else:
			print("Please be more specific")
			missing = True
	lastTurn.dobj = dobj
	lastTurn.iobj = iobj
	if missing:
		return False
	return [dobj, iobj]
	
# create an array of all nouns and adjectives referring to a direct or indirect object
def getObjWords(before, after, input_tokens):
	low_bound = input_tokens.index(before)
	# add 1 for non-inclusive indexing
	low_bound = low_bound + 1
	if after:
		high_bound = input_tokens.index(after)
		obj_words = input_tokens[low_bound:high_bound]
	else:
		obj_words = input_tokens[low_bound:]
	if len(obj_words) == 0:
		#print("I don't undertand. Please be more specific.")
		return False
	return obj_words

def checkRange(me, things, scope):
	out_range = []
	if scope=="room":
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
				out_range.append(thing)
	for thing in out_range:
		things.remove(thing)
	
	return things

def getThing(me, noun_adj_arr, scope):
	# get noun (last word)
	noun = noun_adj_arr[-1]
	# get list of associated Things
	if noun in vocab.nounDict:
		# COPY the of list Things associated with a noun to allow for element deletion during disambiguation (in checkAdjectives)
		# the list will usually be fairly small
		things = list(vocab.nounDict[noun])
	else:
		if scope=="room":
			print("I don't see any " + noun + " here.")
			return False
		elif scope=="knows":
			print("You don't know of any " + noun + ".")
			return False
		else:
			# assuming scope = "inv"
			print("You don't have any " + noun + ".")
			return False
	# check if things are in range
	things = checkRange(me, things, scope)
	if len(things) == 0:
		if scope=="room" or scope =="near":
			print("I don't see any " + noun + " here.")
			return False
		elif scope=="knows":
			# assuming scope = "inv"
			print("You don't know of any " + noun + ".")
			return False
		else:
			# assuming scope = "inv"
			print("You don't have any " + noun + ".")
			return False
	elif len(things) == 1:
		return things[0]
	else:
		thing = checkAdjectives(noun_adj_arr, noun, things, scope)
		return thing

# if there are multiple Thing objects matching the noun, check the adjectives
# iterate through the given adjectives, eliminating Things that don't match until there is exactly one matching Thing, or all adjectives have been checked
def checkAdjectives(noun_adj_arr, noun, things, scope):
	adj_i = noun_adj_arr.index(noun) - 1
	not_match = []
	while adj_i>=0 and len(things) > 1:
		# check preceding word as an adjective
		for thing in things:
			#print(thing.adjectives)
			#print(noun_adj_arr[adj_i])
			if noun_adj_arr[adj_i] not in thing.adjectives:
				not_match.append(thing)
				#print("no")
		for item in not_match:
			#print("removing " + item.adjectives[0])
			things.remove(item)
		adj_i = adj_i- 1
	if len(things)==1:
		return things[0]
	elif len(things) >1:
		print("Which " + noun + " do you mean?") # will be modified to allow for input of just noun/adjective pair
		# turn ON disambiguation mode for next turn
		lastTurn.ambiguous = True
		return False
	else:
		if scope=="room":
			print("I don't see any " + " ".join(noun_adj_arr)  + " here.")
			return False
		elif scope=="knows":
			print("You don't know of any " + noun + ".")
			return False
		else:
			# assuming scope is "inv"
			print("You don't have any " + " ".join(noun_adj_arr)  + ".")
			return False
# callVerb calls getThing to get the Thing objects (if any) referred to in input, then calls the verb function
def callVerb(me, cur_verb, obj_words):
	if cur_verb.hasDobj and obj_words[0]:
		cur_dobj = getThing(me, obj_words[0], cur_verb.dscope)
		lastTurn.dobj = cur_dobj
	else:
		cur_dobj = False
		lastTurn.dobj = False
	if cur_verb.hasIobj and obj_words[1]:
			cur_iobj = getThing(me, obj_words[1], cur_verb.iscope)
			lastTurn.iobj = cur_iobj
	else:
		cur_iobj = False
		lastTurn.iobj = False
	# apparent duplicate checking of objects is to allow last.iobj to be set before the turn is aborted in event of incomplete input
	
	if cur_dobj in me.sub_inventory:
		print("(First removing " + cur_dobj.getArticle(True) + cur_dobj.verbose_name + " from " + cur_dobj.location.getArticle(True) + cur_dobj.location.verbose_name + ")")
		cur_dobj.location.removeThing(cur_dobj)
		me.inventory.append(cur_dobj)
	
	if cur_iobj in me.sub_inventory:
		print("(First removing " + cur_iobj.getArticle(True) + cur_iobj.verbose_name + " from " + cur_iobj.location.getArticle(True) + cur_iobj.location.verbose_name + ")")
		cur_iobj.location.removeThing(cur_iobj)
		me.inventory.append(cur_iobj)
	
	if cur_verb.hasIobj:
		if not cur_dobj or not cur_iobj:
			return False
		else:
			cur_verb.verbFunc(me, cur_dobj, cur_iobj)
	elif cur_verb.hasDobj:
		if not cur_dobj:
			return False
		else:
			cur_verb.verbFunc(me, cur_dobj)
	else:
		cur_verb.verbFunc(me)

def disambig(me, input_tokens):
	dobj = lastTurn.dobj
	iobj = lastTurn.iobj
	cur_verb = lastTurn.verb
	if isinstance(dobj, list):
		dobj = getThing(me, dobj, cur_verb.dscope)
	if isinstance(iobj, list):
		iobj = getThing(me, iobj, cur_verb.iscope)
		
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
	if not obj_words:
		return False
	callVerb(me, cur_verb, obj_words)
	
def roomDescribe(me):
	me.location.describe(me)

def parseInput(me, input_string):
	# tokenize at spaces
	input_tokens = tokenize(input_string)
	# if input is a travel command, move player 
	d = getDirection(me, input_tokens)
	if d:
		return 0
	cur_verb = getVerb(input_tokens)
	if not cur_verb:
		if lastTurn.ambiguous:
			disambig(me, input_tokens)
			return 0
		return 0
	else:
		lastTurn.verb = cur_verb
	obj_words = getGrammarObj(me, cur_verb, input_tokens)
	if not obj_words:
		return False
	# turn OFF disambiguation mode for next turn
	lastTurn.ambiguous = False
	callVerb(me, cur_verb, obj_words)
	return 0

# main input loop
def mainLoop(me):
	quit = False
	roomDescribe(me)
	while not quit:
		# first, print room description
		#me.location.describe()
		input_string = raw_input("> ")
		# clean string
		input_string = string.lower(input_string)
		input_string = re.sub(r'[^\w\s]','',input_string)
		# check for quit command
		if(input_string=="q" or input_string=="quit"):
			print("Goodbye.")
			quit = True
		elif len(input_string)==0:
			continue
		else:
			# parse string
			parseInput(me, input_string)
		print("") # empty line for output formatting

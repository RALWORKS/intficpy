import string
import re

# intficpy framework files
import vocab
import verb
import thing
import travel
import settings


##############################################################
############### PARSER.PY - the parser for IntFicPy ##################
#### Contains the input loop and parsing functions for the framework #####
##############################################################
#game.me.location = game.startroom

# convert input to a list of tokens
def tokenize(input_string):
	# tokenize input with spaces
	tokens = input_string.split()
	#print(tokens)
	return tokens

# check for direction statement as in "west" or "ne"
def getDirection(input_tokens):
	d = input_tokens[0]
	# if first word is "go", skip first word, assume next word is a direction
	if input_tokens[0]=="go" and len(input_tokens) > 0:
		d = input_tokens[1]
	if d in travel.directionDict:
		travel.directionDict[d]()
		return True
	else:
		return False

# identify the verb
def getVerb(input_tokens):
	# look up first word in verb dictionary
	if input_tokens[0] in vocab.verbDict:
		cur_verb = vocab.verbDict[input_tokens[0]]
	# if not present, error "I don't understand," return -1
	else:
		print("I don't understand")
		return False
	# else return  verb object
	return cur_verb

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
	print("I don't understand")
	return False
# analyse input using verb syntax form to find any objects
def getGrammarObj(cur_verb, input_tokens):
	# first, choose the correct syntax
	form = getVerbSyntax(cur_verb, input_tokens)
	if not form:
		return False
	# if verb_object.hasDobj, search verb.syntax for <dobj>, get index
	if cur_verb.hasDobj:
		# get words before and after
		dobj_i = form.index("<dobj>")
		before_d = form[dobj_i - 1]
		if dobj_i+1<len(form):
			after_d = form[dobj_i + 1]
		else:
			after_d = False
		dobj = getObjWords(before_d, after_d, input_tokens)
		if not dobj:
			return False
	else:
		dobj = False
	if cur_verb.hasIobj:	
		iobj_i = form.index("<iobj>")
		before_i = form[iobj_i - 1]
		if iobj_i+1<len(form):
			after_i = form[dobj_i + 1]
		else:
			after_i = False
		iobj = getObjWords(before_i, after_i, input_tokens)
		if not iobj:
			return False
	else:
		iobj = False
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
		print("I don't undertand")
		return False
	return obj_words

def checkRange(things, scope):
	game = __import__(settings.main_file)
	out_range = []
	if scope=="room":
		for thing in things:
			if thing not in game.me.location.contains:
				out_range.append(thing)
	else:
		# assume scope equals "inv"
		for thing in things:
			if thing not in game.me.inventory:
				out_range.append(thing)
	for thing in out_range:
		things.remove(thing)
	
	return things

def getThing(noun_adj_arr, scope):
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
		else:
			# assuming scope = "inv"
			print("You don't have any " + noun + ".")
			return False
	# check if things are in range
	things = checkRange(things, scope)
	if len(things) == 0:
		if scope=="room":
			print("I don't see any " + noun + " here.")
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
		return False
	else:
		if scope=="room":
			print("I don't see any " + " ".join(noun_adj_arr)  + " here.")
			return False
		else:
			# assuming scope is "inv"
			print("You don't have any " + " ".join(noun_adj_arr)  + ".")
			return False
# callVerb calls getThing to get the Thing objects (if any) referred to in input, then calls the verb function
def callVerb(cur_verb, obj_words):
	if cur_verb.hasDobj and obj_words[0]:
		cur_dobj = getThing(obj_words[0], cur_verb.scope)
		if cur_dobj == False:
			return 0
		if cur_verb.hasIobj and obj_words[1]:
			cur_iobj = getThing(obj_words[1], cur_verb.scope)
			if cur_iobj==False:
				return 0
			# add later: check if cur_dobj is within range
			#if not, error "I don't see any <dobj phrase> here", abort
			cur_verb.verbFunc(cur_dobj, cur_iobj)
		else:
			# add later: check if cur_dobj is within range
			#if not, error "I don't see any <dobj phrase> here", abort
			cur_verb.verbFunc(cur_dobj)
	else:
		cur_verb.verbFunc()

def roomDescribe():
	game = __import__(settings.main_file)
	game.me.location.describe()

def parseInput(input_string):
	# tokenize at spaces
	input_tokens = tokenize(input_string)
	# if input is a travel command, move player 
	d = getDirection(input_tokens)
	if d:
		return 0
	cur_verb = getVerb(input_tokens)
	if not cur_verb:
		return 0
	obj_words = getGrammarObj(cur_verb, input_tokens)
	if not obj_words:
		return False
	callVerb(cur_verb, obj_words)
	return 0

# main input loop
quit = False
roomDescribe()
while not quit:
	# first, print room description
	#game.me.location.describe()
	input_string = raw_input("> ")
	# clean string
	input_string = string.lower(input_string)
	input_string = re.sub(r'[^\w\s]','',input_string)
	# check for quit command
	if(input_string=="q" or input_string=="quit"):
		print "Goodbye."
		quit = True
	else:
		# parse string
		parseInput(input_string)
	print("") # empty line for output formatting

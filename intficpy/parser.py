import importlib
import string

from .vocab import english
from .vocab import english, verbDict, nounDict
from .verb import (
    scoreVerb,
    fullScoreVerb,
    helpVerbVerb,
    getVerb,
    standUpVerb,
    dropVerb,
)
from .thing_base import Thing
from .things import Container, Surface, UnderSpace, Liquid
from .room import Room
from .travel import directionDict
from .tokenizer import cleanInput, tokenize, removeArticles


##############################################################
# PARSER.PY - the parser for IntFicPy
# Contains the Parser class
##############################################################


class Parser:
    def __init__(self, game):
        self.game = game

    def getTokens(self, input_string, record=True):
        input_string = cleanInput(input_string)
        if record:
            self.recordInput(input_string)
        return removeArticles(tokenize(input_string))

    def recordInput(self, input_string):
        self.game.lastTurn.turn_list.append(input_string)
        if self.game.lastTurn.recfile:
            self.game.lastTurn.recfile.write(input_string + "\n")
            self.game.lastTurn.recfile.flush()
        return input_string

    def getDirection(self, input_tokens):
        """
        Check for direction statement as in "west" or "ne"
        Takes argument input_tokens, a list of strings
        Called every turn by self.parseInput
        Returns a Boolean specifying whether the input is a travel command
        """
        d = input_tokens[0]
        # if first word is "go", skip first word, assume next word is a direction
        if input_tokens[0] == "go" and len(input_tokens) == 2:
            d = input_tokens[1]
            if d in directionDict:
                directionDict[d](self.game)
                return True
        elif d in directionDict and len(input_tokens) == 1:
            if self.game.lastTurn.ambiguous:
                for item in self.game.lastTurn.things:
                    if d in item.adjectives:
                        return False
            directionDict[d](self.game)
            return True
        else:
            return False

    def getCurVerb(self, input_tokens):
        """
        Identify the verb
        Takes argument input_tokens, the 
        self.tokenized player command (list of strings)
        Called every turn by self.parseInput
        Returns a two item list. The first is a Verb object and an associated verb form 
        (list of strings), or None. 
        The second is True if potential verb matches were found, False otherwise
        """
        # look up first word in verb dictionary
        if input_tokens[0] in verbDict:
            verbs = list(verbDict[input_tokens[0]])
            verbs = self.matchPrepKeywords(verbs, input_tokens)
        else:
            verbs = None
            if self.game.lastTurn.convNode:
                self.game.addTextToEvent(
                    "turn",
                    '"'
                    + " ".join(input_tokens).capitalize()
                    + '" is not enough information to match a suggestion. ',
                )
                self.game.lastTurn.err = True
            elif not self.game.lastTurn.ambiguous:
                self.game.addTextToEvent(
                    "turn", "I don't understand the verb: " + input_tokens[0]
                )
                self.game.lastTurn.err = True
            return [None, False]
        vbo = self.verbByObjects(input_tokens, verbs)
        found_verbs = bool(verbs)
        return [vbo, found_verbs]

    def verbByObjects(self, input_tokens, verbs):
        """
        self.disambiguates verbs based on syntax used
        Takes arguments input_tokens, the self.tokenized 
        player command (list of strings), and verbs, a list of Verb objects (verb.py)
        Called by self.getCurVerb
        Iterates through verb list, comparing syntax in input to the entries in the .syntax 
        property of the verb
        Returns a two item list of a Verb object and an associated verb form (list of 
        strings), or None
        """
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
                if i == 0:
                    nearMatch.append([cur_verb, verb_form])
        if len(nearMatch) == 0:
            ambiguous_verb = False
            if self.game.lastTurn.ambig_noun:
                terms = nounDict[self.game.lastTurn.ambig_noun]
                for term in terms:
                    if (
                        input_tokens[0] in term.adjectives
                        or input_tokens[0] in term.synonyms
                    ):
                        ambiguous_verb = True
                    elif input_tokens[0] == term.name:
                        ambiguous_verb = True
            if not ambiguous_verb:
                self.game.addTextToEvent(
                    "turn",
                    'I understood as far as "'
                    + input_tokens[0]
                    + '".<br>(Type VERB HELP '
                    + input_tokens[0].upper()
                    + " for help with phrasing.) ",
                )
            self.game.lastTurn.err = True
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
                    if not "<dobj>" == verb_form[-1]:
                        if verb_form[d_ix + 1] == "<iobj>":
                            adjacent = True
                    if verb_form[d_ix - 1] == "<iobj>":
                        adjacent = True
                iobj = False
                dobj = False
                # get Dobj
                if adjacent and verb.dscope in ["text", "direction"]:
                    objects = self.adjacentStrObj(verb_form, input_tokens, 0)
                elif adjacent and verb.iscope in ["text", "direction"]:
                    objects = self.adjacentStrObj(verb_form, input_tokens, 1)
                else:
                    dobj = self.analyzeSyntax(verb_form, "<dobj>", input_tokens, False)
                    iobj = self.analyzeSyntax(verb_form, "<iobj>", input_tokens, False)
                if objects:
                    dobj = objects[0]
                    iobj = objects[1]
                extra = self.checkExtra(verb_form, dobj, iobj, input_tokens)
                if dobj:
                    dbool = len(dobj) != 0
                else:
                    dbool = False
                if iobj:
                    ibool = len(iobj) != 0
                else:
                    ibool = False
                if len(extra) > 0:
                    removeMatch.append(pair)
                elif (not verb.impDobj) and (dbool != verb.hasDobj):
                    removeMatch.append(pair)
                elif (not verb.impIobj) and (ibool != verb.hasIobj):
                    removeMatch.append(pair)
                elif (
                    verb.dscope == "direction" and not self.directionRangeCheck(dobj)
                ) or (
                    verb.iscope == "direction" and not self.directionRangeCheck(iobj)
                ):
                    removeMatch.append(pair)
            for x in removeMatch:
                nearMatch.remove(x)
            if len(nearMatch) == 1:
                return nearMatch[0]
            elif len(nearMatch) > 1:
                ambiguous_verb = False
                if self.game.lastTurn.ambig_noun:
                    terms = nounDict[self.game.lastTurn.ambig_noun]
                    for term in terms:
                        if (
                            input_tokens[0] in term.adjectives
                            or input_tokens[0] in term.synonyms
                        ):
                            ambiguous_verb = True
                        elif input_tokens[0] == term.name:
                            ambiguous_verb = True
                if not ambiguous_verb:
                    self.game.addTextToEvent(
                        "turn",
                        'I understood as far as "'
                        + input_tokens[0]
                        + '".<br>(Type VERB HELP '
                        + input_tokens[0].upper()
                        + " for help with phrasing.) ",
                    )
                self.game.lastTurn.err = True
                return None
            else:
                ambiguous_verb = False
                if self.game.lastTurn.ambig_noun:
                    terms = nounDict[self.game.lastTurn.ambig_noun]
                    for term in terms:
                        if (
                            input_tokens[0] in term.adjectives
                            or input_tokens[0] in term.synonyms
                        ):
                            ambiguous_verb = True
                        elif input_tokens[0] == term.name:
                            ambiguous_verb = True
                if not ambiguous_verb:
                    self.game.addTextToEvent(
                        "turn",
                        'I understood as far as "'
                        + input_tokens[0]
                        + '".<br>(Type VERB HELP '
                        + input_tokens[0].upper()
                        + " for help with phrasing.) ",
                    )
                self.game.lastTurn.err = True
                return None

    def checkExtra(self, verb_form, dobj, iobj, input_tokens):
        """
        Checks for words unaccounted for by verb form
        Takes argument verb_form, a verb form (list of strings), dobj and iobj, the 
        grammatical direct and indirect objects from 
        the command (lists of strings), and input tokens, the     self.tokenized player command 
        (list of strings)
        Called by self.verbByObjects
        Returns a list, empty or containing one word strings (extra words)"""

        accounted = []
        extra = list(input_tokens)
        for word in extra:
            if word in verb_form:
                accounted.append(word)
            if dobj:
                if word in dobj:
                    if word in english.prepositions or word in english.keywords:
                        noun = dobj[-1]
                        exempt = False
                        if noun in nounDict:
                            for item in nounDict[noun]:
                                if word in item.adjectives:
                                    exempt = True
                                    break
                        if exempt:
                            accounted.append(word)
                    else:
                        accounted.append(word)
            if iobj:
                if word in iobj:
                    if word in english.prepositions or word in english.keywords:
                        noun = iobj[-1]
                        exempt = False
                        if noun in nounDict:
                            for item in nounDict[noun]:
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

    def matchPrepKeywords(self, verbs, input_tokens):
        """
        Check for prepositions in the self.tokenized player command, and remove any candidate 
        verbs whose preposition does not match
        Takes arguments verbs, a list of Verb objects (verb.py), and input_tokens, the 
        self.tokenized player command (list of strings)
        Not currently used by parser
        Returns a list of Verb objects or an empty list
        """
        remove_verb = []
        for p in english.prepositions:
            if p in input_tokens and len(input_tokens) > 1:
                exempt = False
                for verb in verbs:
                    ix = input_tokens.index(p) + 1
                    if ix < len(input_tokens):
                        noun = input_tokens[ix]
                        while not noun in nounDict:
                            ix = ix + 1
                            if ix >= len(input_tokens):
                                break
                            noun = input_tokens[ix]
                        if noun in nounDict:
                            for item in nounDict[noun]:
                                if p in item.adjectives:
                                    exempt = True
                    if p in ["up", "down", "in", "out"]:
                        if verb.iscope == "direction" or verb.dscope == "direction":
                            exempt = True
                    if not verb.preposition and not exempt:
                        remove_verb.append(verb)
                    elif not p in verb.preposition and not exempt:
                        remove_verb.append(verb)
        for p in english.keywords:
            if p in input_tokens and len(input_tokens) > 1:
                exempt = False
                for verb in verbs:
                    ix = input_tokens.index(p) + 1
                    if ix < len(input_tokens):
                        noun = input_tokens[ix]
                        while not noun in nounDict:
                            ix = ix + 1
                            if ix >= len(input_tokens):
                                break
                            noun = input_tokens[ix]
                        if noun in nounDict:
                            for item in nounDict[noun]:
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

    def getVerbSyntax(self, cur_verb, input_tokens):
        """
        Match tokens in input with tokens in verb syntax verb_forms to choose which syntax 
        to assume
        Takes arguments cur_verb, the Verb object 
        (verb.py) being anaylzed, and input_tokens, the self.tokenized player command (list of 
        strings)
        Returns the most probable verb_form (list of strings), or None
        """
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
            if i == 0:
                return verb_form
        self.game.addTextToEvent("turn", "I don't understand. Try rephrasing.")
        self.game.lastTurn.err = True
        return None

    def getGrammarObj(self, cur_verb, input_tokens, verb_form):
        """
        Analyze input using the chosen verb_form to find any objects
        Takes arguments cur_verb, a Verb object (verb.py),
        input_tokens, the self.tokenized player command (list of strings), and verb_form, the 
        assumed syntax of the command (list of strings)
        Called by self.parseInput
        Returns None or a list of two items, either lists of strings, or None
        """
        # first, choose the correct syntax
        if not verb_form:
            return None
        # check if dobj and iobj are adjacent
        objects = None
        adjacent = False
        if cur_verb.hasDobj:
            d_ix = verb_form.index("<dobj>")
            if not "<dobj>" == verb_form[-1]:
                if verb_form[d_ix + 1] == "<iobj>":
                    adjacent = True
            if verb_form[d_ix - 1] == "<iobj>":
                adjacent = True
        # if verb_object.hasDobj, search verb.syntax for <dobj>, get index
        # get Dobj
        if adjacent and cur_verb.dscope in ["text", "direction"]:
            objects = self.adjacentStrObj(verb_form, input_tokens, 0)
        elif adjacent and cur_verb.iscope in ["text", "direction"]:
            objects = self.adjacentStrObj(verb_form, input_tokens, 1)
        else:
            if cur_verb.hasDobj:
                dobj = self.analyzeSyntax(verb_form, "<dobj>", input_tokens)
            else:
                dobj = None
            if cur_verb.hasIobj:
                iobj = self.analyzeSyntax(verb_form, "<iobj>", input_tokens)
            else:
                iobj = None
        if objects:
            dobj = objects[0]
            iobj = objects[1]
        return self.checkObj(cur_verb, dobj, iobj)

    def adjacentStrObj(self, verb_form, input_tokens, strobj):
        vfd = verb_form.index("<dobj>")
        vfi = verb_form.index("<iobj>")
        if verb_form[-1] == "<dobj>":
            before = verb_form[vfi - 1]
            after = None
        elif verb_form[-1] == "<iobj>":
            before = verb_form[vfd - 1]
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
        if strobj == 0:  # dobj is string
            if vfd > vfi:
                x = 1
        else:  # iobj is string
            if vfd < vfi:
                x = 1

        if x == 0:  # thing follows string
            if not objs[-1] in nounDict:
                # self.game.addTextToEvent("turn", "Please rephrase ")
                return [None, None]
            things = nounDict[objs[-1]]
            i = len(objs) - 2
            while i > 0:
                accounted = False
                for item in things:
                    if objs[i] in thing.adjectives:
                        accounted = True
                if not accounted:
                    end_str = i
                    break
                elif i == 1:
                    end_str = i
                i = i - 1
            strobj = objs[:end_str]
            tobj = objs[end_str:]
        else:  # string follows thing
            noun = None
            for word in objs:
                if word in nounDict:
                    noun = word
                    break
            if not noun:
                # self.game.addTextToEvent("turn", "Please rephrase ")
                return [None, None]
            start_str = objs.index(noun) + 1
            end_str = len(objs) - 1
            strobj = objs[start_str:]
            tobj = objs[:start_str]

        if strobj == 0:
            return [strobj, tobj]
        else:
            return [tobj, strobj]

    # NOTE: print_verb_error prevents the duplication of the error message in the event of improper Verb definition. A little bit hacky.
    def analyzeSyntax(self, verb_form, tag, input_tokens, print_verb_error=True):
        """
        Parse verb form (list of strings) to find the words directly preceding and 
        following object tags, and pass these to self.getObjWords find the objects in the 
        player's command
        Takes arguments verb_form, the assumed syntax of the 
        command (list of strings), tag (string, "<dobj>" or "<iobj>"),
        input_tokens (list of strings) and print_verb_error (Boolean), False when called by 
        self.verbByObjects
        Called by self.getVerbSyntax and self.verbByObjects
        Returns None or a list of strings
        """
        # get words before and after
        if tag in verb_form:
            obj_i = verb_form.index(tag)
        else:
            if print_verb_error:
                self.game.addTextToEvent(
                    "turn", "ERROR: Inconsistent verb definitition."
                )
            return None
        before = verb_form[obj_i - 1]
        if obj_i + 1 < len(verb_form):
            after = verb_form[obj_i + 1]
        else:
            after = None
        return self.getObjWords(self.game.app, before, after, input_tokens)

    def checkObj(self, cur_verb, dobj, iobj):
        """
        Make sure that the player command contains the correct number of grammatical 
        objects, and get implied objects if applicable
        Takes arguments cur_verb (Verb object, verb.py), dobj, the direct object 
        of the command (list of strings or None), and iobj, the indirect object (list of 
        strings or None)
        Called by  getGrammarObj
        Returns None, or a list of two items, either lists of strings, or None
        """
        missing = False
        if cur_verb.hasDobj and not dobj:
            if cur_verb.impDobj:
                dobj = cur_verb.getImpDobj(self.game)
                if not dobj:
                    missing = True
                else:
                    # dobj = [dobj.verbose_name]
                    pass
            else:
                self.game.addTextToEvent("turn", "Please be more specific")
                self.game.lastTurn.err = True
                return None
        if cur_verb.hasIobj and not iobj:
            if cur_verb.impIobj:
                iobj = cur_verb.getImpIobj(self.game)
                if not iobj:
                    missing = True
                else:
                    # iobj = [iobj.verbose_name]
                    pass
            else:
                self.game.addTextToEvent("turn", "Please be more specific")
                self.game.lastTurn.err = True
                missing = True
        self.game.lastTurn.dobj = dobj
        self.game.lastTurn.iobj = iobj
        if missing:
            return None
        return [dobj, iobj]

    def getObjWords(self, game, before, after, input_tokens):
        """
        Create a list of all nouns and adjectives (strings) referring to a direct or 
        indirect object
        Takes arguments self.game.app, pointing to the PyQt application, before, the word expected 
        before the grammatical object (string), after,
        the word expected after the grammatical object (string or None), and input_tokens, 
        the self.tokenized player command (list of strings)
        Called by self.analyzeSyntax
        Returns an array of strings or None
        """
        if before[0] == "<":
            # find the index of the first noun in the noun dict. if there is more than one, reject any that double as adjectives
            nounlist = []
            for word in input_tokens:
                if word in nounDict:
                    nounlist.append(word)
            if len(nounlist) > 2:
                i = 0
                delnoun = []
                while i < (len(nounlist) - 1):
                    for item in nounDict[nounlist[i]]:
                        if (
                            nounlist[i] in item.adjectives
                            and not nounlist[i] in delnoun
                        ):
                            delnoun.append(nounlist[i])
                for noun in delnoun:
                    nounlist.remove(delnoun)
            if len(nounlist) < 2:
                return None
            # set before to the first noun
            before = nounlist[0]
        if after:
            if after[0] == "<":
                # find the index of the first noun in the noun dict. if there is more than one, reject any that double as adjectives
                nounlist = []
                for word in input_tokens:
                    if word in nounDict:
                        nounlist.append(word)
                if len(nounlist) > 2:
                    i = 0
                    delnoun = []
                    while i < (len(nounlist) - 1):
                        for item in nounDict[nounlist[i]]:
                            if (
                                nounlist[i] in item.adjectives
                                and not nounlist[i] in delnoun
                            ):
                                delnoun.append(nounlist[i])
                    for noun in delnoun:
                        nounlist.remove(delnoun)
                if len(nounlist) < 2:
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

    def wearRangeCheck(self, thing):
        """
        Check if the Thing is being worn
        Takes arguments self.game.me, pointing to the Player, and thing, a Thing
        Returns True if within range, False otherwise
        """
        if thing.ix not in self.game.me.wearing:
            return False
        elif thing not in self.game.me.wearing[thing.ix]:
            return False
        else:
            return True

    def roomRangeCheck(self, thing):
        """
        Check if the Thing is in the current room
        Takes arguments self.game.me, pointing to the Player, and thing, a Thing
        Returns True if within range, False otherwise
        """
        out_loc = self.game.me.getOutermostLocation()
        if not out_loc.resolveDarkness(self.game):
            return False
        if thing.ix in self.game.me.contains:
            if thing in self.game.me.contains[thing.ix]:
                return False
        if thing.ix in self.game.me.sub_contains:
            if thing in self.game.me.sub_contains[thing.ix]:
                return False
        if thing.ix in out_loc.contains:
            if thing in out_loc.contains[thing.ix]:
                return True
        if thing.ix in out_loc.sub_contains:
            if thing in out_loc.sub_contains[thing.ix]:
                return True
        return False

    def knowsRangeCheck(self, thing):
        """
        Check if the Player knows about a Thing
        Takes arguments self.game.me, pointing to the Player, and thing, a Thing
        Returns True if within range, False otherwise
        """
        if not thing.known_ix in self.game.me.knows_about:
            return False
        else:
            return True

    def nearRangeCheck(self, thing):
        """
        Check if the Thing is near (room or contains)
        Takes arguments self.game.me, pointing to the Player, and thing, a Thing
        Returns True if within range, False otherwise
        """
        out_loc = self.game.me.getOutermostLocation()
        too_dark = not out_loc.resolveDarkness(self.game.me)
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
        if thing.ix in self.game.me.contains:
            if thing not in self.game.me.contains[thing.ix]:
                pass
            else:
                found = True
        if thing.ix in self.game.me.sub_contains:
            if thing not in self.game.me.sub_contains[thing.ix]:
                pass
            else:
                found = True
        return found

    def invRangeCheck(self, thing):
        """
        Check if the Thing is in the Player contains
        Takes arguments self.game.me, pointing to the Player, and thing, a Thing
        Returns True if within range, False otherwise
        """
        if thing.ix in self.game.me.contains:
            if thing not in self.game.me.contains[thing.ix]:
                pass
            else:
                return True
        if thing.ix in self.game.me.sub_contains:
            if thing not in self.game.me.sub_contains[thing.ix]:
                return False
            else:
                return True
        return False

    def directionRangeCheck(self, obj):
        if isinstance(obj, list):
            if len(obj) > 1:
                return False
            else:
                obj = obj[0]
        if obj in directionDict:
            return True
        else:
            return False

    def getUniqueConcepts(self, things):
        """
        Eliminates all items with duplicate known_ix properties.
        """
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

    def checkRange(self, things, scope):
        """
        Eliminates all grammatical object candidates that are not within the scope of the 
        current verb
        Takes arguments self.game.me, things, a list of Thing objects (thing.py) that are candidates 
        for the target of a player's action, and scope, a string representing the range of 
        the verb
        Called by self.getThing
        Returns a list of Thing objects, or an empty list
        """
        out_range = []
        if scope == "wearing":
            for thing in things:
                if not self.wearRangeCheck(thing):
                    out_range.append(thing)
        elif scope == "room":
            for thing in things:
                if not self.roomRangeCheck(thing) and self.invRangeCheck(thing):
                    # implicit drop
                    dropVerb.verbFunc(self.game, thing)
                    pass
                elif not self.roomRangeCheck(thing):
                    out_range.append(thing)
        elif scope == "knows":
            things = self.getUniqueConcepts(things)
            for thing in things:
                if not self.knowsRangeCheck(thing):
                    out_range.append(thing)
        elif scope == "near" or scope == "roomflex":
            for thing in things:
                if not self.nearRangeCheck(thing):
                    out_range.append(thing)
        elif scope == "inv" or scope == "invflex":
            for thing in things:
                if self.roomRangeCheck(thing):
                    pass
                elif not self.invRangeCheck(thing):
                    out_range.append(thing)
        else:
            print('ERROR: incorrect verb scope "' + scope + '".')
            things = []
        # remove items that require implicit actions in the event of ambiguity
        for thing in out_range:
            things.remove(thing)
        things2 = list(things)
        out_range = []
        if len(things) > 1:
            for thing in things:
                if scope in ["room", "roomflex"] and not self.roomRangeCheck(thing):
                    out_range.append(thing)
                elif scope in ["inv", "invflex"] and not self.invRangeCheck(thing):
                    out_range.append(thing)
                elif thing.ignore_if_ambiguous:
                    out_range.append(thing)
            for thing in out_range:
                things2.remove(thing)
            if len(things2) > 0:
                return things2
        return things

    def verbScopeError(self, scope, noun_adj_arr):
        """
        Prints the appropriate Thing out of scope message
        Takes arguments self.game.app, pointing to the PyQt self.game.app, scope, a string, and noun_adj_arr, a 
        list of strings
        Called by self.getThing and self.checkAdjectives
        Returns None
        """
        noun = " ".join(noun_adj_arr)
        if scope == "wearing":
            self.game.addTextToEvent("turn", "You aren't wearing any " + noun + ".")
            self.game.lastTurn.err = True
            return None
        elif scope == "room" or scope == "near" or scope == "roomflex":
            out_loc = self.game.me.getOutermostLocation()
            if not out_loc.resolveDarkness(self.game):
                self.game.addTextToEvent("turn", "It's too dark to see anything. ")
            else:
                self.game.addTextToEvent("turn", "I don't see any " + noun + " here.")
            self.game.lastTurn.err = True
            return None
        elif scope == "knows":
            self.game.addTextToEvent("turn", "You don't know of any " + noun + ".")
            self.game.lastTurn.err = True
            return None
        elif scope == "direction":
            self.game.addTextToEvent(
                "turn", noun.capitalize() + " is not a direction I recognize. "
            )
        else:
            # assuming scope = "inv"/"invflex"
            self.game.addTextToEvent("turn", "You don't have any " + noun + ".")
            self.game.lastTurn.err = True
            return None

    def getThing(self, noun_adj_arr, scope, far_obj, obj_direction):
        """
        Get the Thing object in range associated with a list of adjectives and a noun
        Takes arguments noun_adj_array, a list of strings referring to an in game 
        item, taken from the player command, 
        and scope, a string specifying the range of the verb
        Called by self.callVerb
        Returns a single Thing object (thing.py) or None
        """
        # get noun (last word)
        endnoun = True
        for item in self.game.lastTurn.things:
            if noun_adj_arr[-1] in item.adjectives:
                endnoun = False
        try:
            t_ix = int(noun_adj_arr[-1])
        except:
            t_ix = -1
        if self.game.lastTurn.things != [] and (
            noun_adj_arr[-1] not in nounDict or not endnoun
        ):
            noun = self.game.lastTurn.ambig_noun
            if noun:
                noun_adj_arr.append(noun)
            things = self.game.lastTurn.things
        elif (
            self.game.lastTurn.ambiguous
            and t_ix <= len(self.game.lastTurn.things)
            and t_ix > 0
        ):
            self.game.lastTurn.ambiguous = False
            return self.game.lastTurn.things[t_ix - 1]
        else:
            noun = noun_adj_arr[-1]
            # get list of associated Things
            if noun in nounDict:
                # COPY the of list Things associated with a noun to allow for element deletion during self.disambiguation (in self.checkAdjectives)
                # the list will usually be fairly small
                things = list(nounDict[noun])
            else:
                things = []
        if len(things) == 0:
            return self.verbScopeError(scope, noun_adj_arr)
        else:
            thing = self.checkAdjectives(
                noun_adj_arr, noun, things, scope, far_obj, obj_direction
            )
            return thing

    def verboseNamesMatch(self, things):
        """
        Check if any of the potential grammatical objects have identical verbose names
        Takes the list of things associated with the direct or indirect object 
        Returns a list of two items: 
            Item one is True if duplicates are present, else False
            Item two is dictionary mapping verbose names to lists of Things from the input 
            with that name
        """
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

    def locationsDistinct(self, things):
        """
        Check if identically named items can be distinguished by their locations
        Takes a list of items to check
        Returns False if all locations are the same, True otherwise
        """
        locs = [item.location for item in things]
        return not locs.count(locs[1]) == len(locs)

    def checkAdjectives(
        self, noun_adj_arr, noun, things, scope, far_obj, obj_direction
    ):
        """
        If there are multiple Thing objects matching the noun, check the adjectives to 
        narrow down to exactly 1
        Takes arguments self.game.app, noun_adj_arr, a list of strings referring to an in game item, 
        taken from the player command,noun (string), things, a list of Thing objects
        (things.py) that are     candidates for the target of the player's action, and 
        scope, a string specifying the range of the verb
        Called by self.getThing
        Returns a single Thing object or None
        """
        if things == self.game.lastTurn.things:
            self.game.lastTurn.ambiguous = False
            self.game.lastTurn.things = []
            self.game.lastTurn.err = False
            self.game.lastTurn.ambig_noun = None
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
        while adj_i >= 0 and len(things) > 1:
            # check preceding word as an adjective
            for thing in things:
                if noun_adj_arr[adj_i] not in thing.adjectives:
                    not_match.append(thing)
            for item in not_match:
                if item in things:
                    things.remove(item)
            adj_i = adj_i - 1
        things = self.checkRange(things, scope)
        if len(things) == 1 and things[0].far_away and not far_obj:
            self.game.addTextToEvent(
                "turn",
                (things[0].getArticle(True) + things[0].verbose_name).capitalize()
                + " is too far away. ",
            )
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
        if len(things) == 1:
            return things[0]
        elif len(things) > 1:
            name_match = self.verboseNamesMatch(things)
            name_dict = name_match[
                1
            ]  # dictionary of verbose_names from the current set of things
            msg = "Do you mean "
            scanned_keys = []
            if name_match[0]:  # there is at least one set of duplicate verbose_names
                things = (
                    []
                )  # empty things to reorder elements according to the order printed, since we are using name_dict
                for (
                    name
                ) in (
                    name_dict
                ):  # use name_dict for self.disambiguation message composition rather than things
                    scanned_keys.append(name)
                    unscanned = list(set(name_dict.keys()) - set(scanned_keys))
                    if len(name_dict[name]) > 1:
                        if self.locationsDistinct(name_dict[name]):
                            for item in name_dict[name]:
                                things.append(item)
                                loc = item.location
                                if not loc:
                                    pass
                                elif isinstance(loc, Room):
                                    msg += (
                                        item.lowNameArticle(True)
                                        + " on "
                                        + loc.floor.lowNameArticle(True)
                                        + " ("
                                        + str(things.index(item) + 1)
                                        + ")"
                                    )
                                elif loc == self.game.me:
                                    msg += (
                                        item.lowNameArticle(True)
                                        + " in your inventory ("
                                        + str(things.index(item) + 1)
                                        + ")"
                                    )
                                else:
                                    msg += (
                                        item.lowNameArticle(True)
                                        + " "
                                        + loc.contains_preposition
                                        + " "
                                        + loc.lowNameArticle(True)
                                        + " ("
                                        + str(things.index(item) + 1)
                                        + ")"
                                    )
                                if item is name_dict[name][-1] and not len(unscanned):
                                    msg += "?"
                                elif (
                                    item is name_dict[name][-1]
                                    and len(unscanned) == 1
                                    and len(name_dict[unscanned[0]]) == 1
                                ):
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
                                msg += (
                                    item.lowNameArticle(True)
                                    + " ("
                                    + str(things.index(item) + 1)
                                    + ")"
                                )
                                if item is name_dict[name][-1] and not len(unscanned):
                                    msg += "?"
                                elif (
                                    item is name_dict[name][-1]
                                    and len(unscanned) == 1
                                    and len(name_dict[unscanned[0]]) == 1
                                ):
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
                            msg += (
                                item.lowNameArticle(True)
                                + " ("
                                + str(things.index(item) + 1)
                                + ")"
                            )
                            if item is name_dict[name][-1] and not len(unscanned):
                                msg += "?"
                            elif (
                                item is name_dict[name][-1]
                                and len(unscanned) == 1
                                and len(name_dict[unscanned[0]]) == 1
                            ):
                                msg += ", or "
                            elif len(name_dict[name]) == 1:
                                msg += ", "
                            elif item is name_dict[name][-2] and not len(unscanned):
                                msg += ", or "
                            else:
                                msg += ", "
            else:
                for thing in things:
                    msg = (
                        msg
                        + thing.getArticle(True)
                        + thing.verbose_name
                        + " ("
                        + str(things.index(thing) + 1)
                        + ")"
                    )
                    # add appropriate punctuation and "or"
                    if thing is things[-1]:
                        msg = msg + "?"
                    elif thing is things[-2]:
                        msg = msg + ", or "
                    else:
                        msg = msg + ", "
            self.game.addTextToEvent("turn", msg)
            # turn ON self.disambiguation mode for next turn
            self.game.lastTurn.ambiguous = True
            self.game.lastTurn.ambig_noun = noun
            self.game.lastTurn.things = things
            return None
        else:
            return self.verbScopeError(scope, noun_adj_arr)

    def callVerb(self, cur_verb, obj_words):
        """
        Gets the Thing objects (if any) referred to in the player command, then calls
        the verb function
        Takes arguments cur_verb, a Verb object (verb.py), and obj_words, a list
        with two items representing the grammatical
        direct and indirect objects, either lists of strings, or None
        Called by self.parseInput and self.disambig
        Returns a Boolean, True if a verb function is successfully called, False 
        otherwise
        """
        # FIRST, check if dobj and or iobj have already been found
        # if not, set objs to None
        # checking dobj
        if cur_verb.hasDobj and not isinstance(obj_words[0], list):
            cur_dobj = obj_words[0]
        elif cur_verb.hasDobj and obj_words[0]:
            if isinstance(obj_words[0], Thing):
                cur_dobj = obj_words[0]
            elif cur_verb.dscope == "text" or cur_verb.dscope == "direction":
                cur_dobj = obj_words[0]
            else:
                cur_dobj = self.getThing(
                    obj_words[0],
                    cur_verb.dscope,
                    cur_verb.far_dobj,
                    cur_verb.dobj_direction,
                )
            self.game.lastTurn.dobj = cur_dobj
        else:
            cur_dobj = None
            self.game.lastTurn.dobj = None
        # checking iobj
        if cur_verb.hasIobj and not isinstance(obj_words[1], list):
            cur_iobj = obj_words[1]
        elif cur_verb.hasIobj and obj_words[1]:
            if isinstance(obj_words[1], Thing):
                cur_iobj = obj_words[1]
            elif cur_verb.iscope == "text" or cur_verb.iscope == "direction":
                cur_iobj = obj_words[1]
            else:
                cur_iobj = self.getThing(
                    obj_words[1],
                    cur_verb.iscope,
                    cur_verb.far_iobj,
                    cur_verb.iobj_direction,
                )
            self.game.lastTurn.iobj = cur_iobj
        else:
            cur_iobj = None
            self.game.lastTurn.iobj = None
        # check if any of the item's component parts should be passed as dobj/iobj instead
        if cur_verb.iscope == "text" or cur_verb.iscope == "direction":
            pass
        if not cur_iobj:
            pass
        elif (
            not isinstance(cur_iobj, Container)
            and cur_verb.itype == "Container"
            and cur_iobj.is_composite
            and not isinstance(obj_words[1], Thing)
        ):
            if cur_iobj.child_Containers != []:
                cur_iobj = self.checkAdjectives(
                    obj_words[1],
                    False,
                    cur_iobj.child_Containers,
                    cur_verb.iscope,
                    cur_verb.far_iobj,
                    cur_verb.iobj_direction,
                )
                self.game.lastTurn.iobj = None
                if cur_iobj:
                    self.game.addTextToEvent(
                        "turn",
                        "(Assuming "
                        + cur_iobj.getArticle(True)
                        + cur_iobj.verbose_name
                        + ".)",
                    )
                    self.game.lastTurn.iobj = cur_iobj
        elif (
            not isinstance(cur_iobj, Surface)
            and cur_verb.itype == "Surface"
            and cur_iobj.is_composite
            and not isinstance(obj_words[1], Thing)
        ):
            if cur_iobj.child_Surfaces != []:
                cur_iobj = self.checkAdjectives(
                    self.game.app,
                    self.game.me,
                    obj_words[1],
                    False,
                    cur_iobj.child_Surfaces,
                    cur_verb.iscope,
                    cur_verb.far_iobj,
                    cur_verb.iobj_direction,
                )
                self.game.lastTurn.iobj = None
                if cur_iobj:
                    self.game.addTextToEvent(
                        "turn",
                        "(Assuming "
                        + cur_iobj.getArticle(True)
                        + cur_iobj.verbose_name
                        + ".)",
                    )
                    self.game.lastTurn.iobj = cur_iobj
        elif (
            not isinstance(cur_iobj, UnderSpace)
            and cur_verb.itype == "UnderSpace"
            and cur_iobj.is_composite
            and not isinstance(obj_words[1], Thing)
        ):
            if cur_iobj.child_UnderSpaces != []:
                cur_iobj = self.checkAdjectives(
                    obj_words[1],
                    False,
                    cur_iobj.child_UnderSpaces,
                    cur_verb.iscope,
                    cur_verb.far_iobj,
                    cur_verb.iobj_direction,
                )
                self.game.lastTurn.iobj = None
                if cur_iobj:
                    # self.game.addTextToEvent("turn", "(Assuming " + cur_iobj.getArticle(True) + cur_iobj.verbose_name + ".)")
                    self.game.lastTurn.iobj = cur_iobj
        if cur_verb.dscope == "text" or cur_verb.dscope == "direction":
            pass
        if not cur_dobj:
            pass
        elif (
            not isinstance(cur_dobj, Container)
            and cur_verb.dtype == "Container"
            and cur_dobj.is_composite
            and not isinstance(obj_words[0], Thing)
        ):
            if cur_dobj.child_Containers != []:
                cur_dobj = self.checkAdjectives(
                    obj_words[0],
                    False,
                    cur_dobj.child_Containers,
                    cur_verb.dscope,
                    cur_verb.far_dobj,
                    cur_verb.dobj_direction,
                )
                self.game.lastTurn.dobj = None
                if cur_dobj:
                    self.game.addTextToEvent(
                        "turn",
                        "(Assuming "
                        + cur_dobj.getArticle(True)
                        + cur_dobj.verbose_name
                        + ".)",
                    )
                    self.game.lastTurn.iobj = cur_dobj
        elif (
            not isinstance(cur_dobj, Surface)
            and cur_verb.dtype == "Surface"
            and cur_dobj.is_composite
            and not isinstance(obj_words[0], Thing)
        ):
            if cur_dobj.child_Surfaces != []:
                cur_dobj = self.checkAdjectives(
                    obj_words[0],
                    False,
                    cur_dobj.child_Surfaces,
                    cur_verb.dscope,
                    cur_verb.far_dobj,
                    cur_verb.dobj_direction,
                )
                self.game.lastTurn.dobj = False
                if cur_dobj:
                    self.game.addTextToEvent(
                        "turn",
                        "(Assuming "
                        + cur_dobj.getArticle(True)
                        + cur_dobj.verbose_name
                        + ".)",
                    )
                    self.game.lastTurn.iobj = cur_dobj
        elif (
            not isinstance(cur_dobj, UnderSpace)
            and cur_verb.dtype == "UnderSpace"
            and cur_dobj.is_composite
            and not isinstance(obj_words[0], Thing)
        ):
            if cur_dobj.child_UnderSpaces != []:
                cur_dobj = self.checkAdjectives(
                    obj_words[0],
                    False,
                    cur_dobj.child_UnderSpaces,
                    cur_verb.dscope,
                    cur_verb.far_dobj,
                    cur_verb.dobj_direction,
                )
                self.game.lastTurn.dobj = False
                if cur_dobj:
                    # self.game.addTextToEvent("turn", "(Assuming " + cur_dobj.getArticle(True) +
                    # cur_dobj.verbose_name + ".)")
                    self.game.lastTurn.iobj = cur_dobj
        # apparent duplicate checking of objects is to allow last.iobj to be set before the
        # turn is aborted in event of incomplete input
        if cur_verb.dscope == "text" or not cur_dobj or cur_verb.dscope == "direction":
            pass
        elif not cur_dobj.location:
            pass
        elif cur_dobj.location.location == self.game.me and isinstance(
            cur_dobj, Liquid
        ):
            cur_dobj = cur_dobj.getContainer()
        elif cur_dobj.location.location == self.game.me and cur_verb.dscope == "inv":
            self.game.addTextToEvent(
                "turn",
                "(First removing "
                + cur_dobj.getArticle(True)
                + cur_dobj.verbose_name
                + " from "
                + cur_dobj.location.getArticle(True)
                + cur_dobj.location.verbose_name
                + ")",
            )
            success = verb.removeFromVerb.verbFunc(
                self.game, cur_dobj, cur_dobj.location
            )
            if not success:
                return False
        if cur_verb.iscope == "text" or not cur_iobj or cur_verb.iscope == "direction":
            pass
        elif not cur_iobj.location:
            pass
        elif cur_iobj.location.location == self.game.me and isinstance(
            cur_iobj, Liquid
        ):
            cur_iobj = cur_iobj.getContainer()
        elif cur_iobj.location.location == self.game.me and cur_verb.iscope == "inv":
            self.game.addTextToEvent(
                "turn",
                "(First removing "
                + cur_iobj.getArticle(True)
                + cur_iobj.verbose_name
                + " from "
                + cur_iobj.location.getArticle(True)
                + cur_iobj.location.verbose_name
                + ")",
            )
            success = verb.removeFromVerb.verbFunc(
                self.game, cur_iobj, cur_iobj.location
            )
            if not success:
                return False

        if cur_verb.hasIobj:
            if not cur_iobj:
                return False
            if cur_verb.iscope == "text" or cur_verb.iscope == "direction":
                pass
            elif cur_verb.iscope == "room" and self.invRangeCheck(cur_iobj):
                dropVerb.verbFunc(self.game, cur_iobj)
            elif (
                cur_verb.iscope == "inv"
                or (cur_verb.iscope == "invflex" and cur_iobj is not self.game.me)
            ) and self.roomRangeCheck(cur_iobj):
                self.game.addTextToEvent(
                    "turn",
                    "(First attempting to take "
                    + cur_iobj.getArticle(True)
                    + cur_iobj.verbose_name
                    + ") ",
                )
                success = getVerb.verbFunc(self.game, cur_iobj)
                if not success:
                    return False
                if not cur_iobj.invItem:
                    self.game.addTextToEvent(
                        "turn",
                        "You cannot take "
                        + cur_iobj.getArticle(True)
                        + cur_iobj.verbose_name
                        + ".",
                    )
                    return False
            elif cur_verb.iscope == "inv" and self.wearRangeCheck(cur_iobj):
                verb.doffVerb.verbFunc(self.game, cur_iobj)
                if cur_verb.dscope == "text" or cur_verb.dscope == "direction":
                    pass
                elif cur_verb.dscope == "room" and self.invRangeCheck(cur_dobj):
                    dropVerb.verbFunc(self.game, cur_dobj)
                elif (
                    cur_verb.dscope == "inv"
                    or (cur_verb.dscope == "invflex" and cur_dobj is not self.game.me)
                ) and self.roomRangeCheck(cur_dobj):
                    self.game.addTextToEvent(
                        "turn",
                        "(First attempting to take "
                        + cur_dobj.getArticle(True)
                        + cur_dobj.verbose_name
                        + ") ",
                    )
                    success = getVerb.verbFunc(self.game, cur_dobj)
                    if not success:
                        return False
        if cur_verb.hasDobj:
            if not cur_dobj:
                return False
            else:
                if cur_verb.dscope == "text" or cur_verb.dscope == "direction":
                    pass
                elif cur_verb.dscope == "room" and self.invRangeCheck(cur_dobj):
                    dropVerb.verbFunc(self.game, cur_dobj)
                elif (
                    cur_verb.dscope == "inv"
                    or (cur_verb.dscope == "invflex" and cur_dobj is not self.game.me)
                ) and self.roomRangeCheck(cur_dobj):
                    self.game.addTextToEvent(
                        "turn",
                        "(First attempting to take "
                        + cur_dobj.getArticle(True)
                        + cur_dobj.verbose_name
                        + ") ",
                    )
                    success = getVerb.verbFunc(self.game, cur_dobj)
                    if not success:
                        return False
                elif cur_verb.dscope == "inv" and self.wearRangeCheck(cur_dobj):
                    verb.doffVerb.verbFunc(self.game, cur_dobj)
                self.game.lastTurn.convNode = False
                self.game.lastTurn.specialTopics = {}
                if cur_verb.dscope == "text":
                    cur_dobj = " ".join(cur_dobj)
                elif cur_verb.dscope == "direction":
                    cur_dobj = " ".join(cur_dobj)
                    correct = self.directionRangeCheck(cur_dobj)
                    if not correct:
                        self.game.addTextToEvent(
                            "turn",
                            cur_dobj.capitalize() + " is not a direction I recognize. ",
                        )
                        return False
        if cur_verb.iscope == "text":
            cur_iobj = " ".join(cur_iobj)
        elif cur_verb.dscope == "text":
            cur_dobj = " ".join(cur_dobj)
        if cur_verb.iscope == "direction":
            cur_iobj = " ".join(cur_iobj)
            correct = self.directionRangeCheck(cur_iobj)
            if not correct:
                self.game.addTextToEvent(
                    "turn", cur_iobj.capitalize() + " is not a direction I recognize. "
                )
                return False
        elif cur_verb.dscope == "direction":
            cur_dobj = " ".join(cur_dobj)
            correct = self.directionRangeCheck(cur_dobj)
            if not correct:
                self.game.addTextToEvent(
                    "turn", cur_iobj.capitalize() + " is not a direction I recognize. "
                )
                return False

        self.game.lastTurn.convNode = False
        self.game.lastTurn.specialTopics = {}

        if cur_verb.hasDobj and cur_verb.hasIobj:
            if (
                cur_verb.dscope != "inv" or cur_verb.iscope != "inv"
            ) and self.game.me.position != "standing":
                standUpVerb.verbFunc(self.self.game)
            cur_verb.verbFunc(self.game, cur_dobj, cur_iobj)
        elif cur_verb.hasDobj:
            if (
                cur_verb.dscope != "inv"
                and cur_verb.dscope != "invflex"
                and self.game.me.position != "standing"
            ):
                standUpVerb.verbFunc(self.game)
            cur_verb.verbFunc(self.game, cur_dobj)
        elif cur_verb.hasIobj:
            if (
                cur_verb.iscope != "inv"
                and cur_verb.iscope != "invflex"
                and self.game.me.position != "standing"
            ):
                standUpVerb.verbFunc(self.game)
            cur_verb.verbFunc(self.game, cur_iobj)
        else:
            cur_verb.verbFunc(self.game)
        return True

    def disambig(self, input_tokens):
        """
        When self.disambiguation mode is active, use the player input to specify the target for 
        the previous turn's ambiguous command
        Takes arguments and input_tokens
        called by self.parseInput
        Returns a Boolean, True if self.disambiguation successful
        """
        dobj = self.game.lastTurn.dobj
        iobj = self.game.lastTurn.iobj
        cur_verb = self.game.lastTurn.verb
        if not dobj and cur_verb.hasDobj:
            dobj = input_tokens
        elif not iobj and cur_verb.hasIobj:
            iobj = input_tokens
        obj_words = [dobj, iobj]
        if not obj_words:
            return False
        self.callVerb(cur_verb, obj_words)
        return True

    def roomDescribe(self):
        """
        Wrapper for room describe function (room.py)
        """
        out_loc = self.game.me.getOutermostLocation()
        out_loc.describe(self.game)

    def getConvCommand(self, input_tokens):
        possible_topics = list(self.game.lastTurn.specialTopics.keys())
        for key in self.game.lastTurn.specialTopics:
            tokens = cleanInput(key, False)
            tokens = tokenize(tokens)
            tokens = removeArticles(tokens)
            for tok in input_tokens:
                if tok not in tokens and tok == "i" and "you" in tokens:
                    pass
                elif tok not in tokens and tok == "you" and "i" in tokens:
                    pass
                elif tok not in tokens:
                    possible_topics.remove(key)
                    break
        revised_possible_topics = list(possible_topics)
        if len(possible_topics) > 1:
            for topicA in possible_topics:
                for topicB in possible_topics:
                    if (
                        topicA != topicB
                        and topicB in revised_possible_topics
                        and topicA in revised_possible_topics
                    ):
                        if (
                            self.game.lastTurn.specialTopics[topicA]
                            == self.game.lastTurn.specialTopics[topicB]
                        ):
                            revised_possible_topics.remove(topicB)
        if len(revised_possible_topics) != 1:
            return False
        else:
            x = revised_possible_topics[0]
            self.game.lastTurn.specialTopics[x].func(self.game)
            return True

    def parseInput(self, input_string):
        """
        Parse player input, and respond to commands each turn
        Takes argument input_string, the raw player input
        Called by mainLoop in terminal version, turnMain (gui.py) in GUI version
        Returns 0 when complete
        """
        # clean and self.tokenize
        input_tokens = self.getTokens(input_string)
        if not self.game.lastTurn.gameEnding:
            if len(input_tokens) == 0:
                # self.game.addTextToEvent("turn", "I don't understand.")
                self.game.lastTurn.err = True
                return 0
            if (
                input_tokens[0:2] == ["help", "verb"]
                or input_tokens[0:2] == ["verb", "help"]
            ) and len(input_tokens) > 2:
                helpVerbVerb.verbFunc(self.game, input_tokens[2:])
                return 0
            elif input_tokens[0:2] == ["help", "verb"] or input_tokens[0:2] == [
                "verb",
                "help",
            ]:
                self.game.addTextToEvent("turn", "Please specify a verb for help. ")
                return 0
            # if input is a travel command, move player
            d = self.getDirection(input_tokens)
            if d:
                self.game.lastTurn.convNode = False
                self.game.lastTurn.specialTopics = {}
                return 0
            if self.game.lastTurn.convNode:
                conv_command = self.getConvCommand(input_tokens)
                if conv_command:
                    self.game.lastTurn.ambig_noun = None
                    self.game.lastTurn.ambig_verb = None
                    self.game.lastTurn.ambiguous = False
                    return 0
                else:
                    pass
            gv = self.getCurVerb(input_tokens)
            if gv[0]:
                cur_verb = gv[0][0]
            else:
                cur_verb = None
            if not cur_verb:
                if self.game.lastTurn.ambiguous and (
                    not gv[1] or self.game.lastTurn.convNode
                ):
                    self.disambig(input_tokens)
                    return 0
                return 0
            else:
                self.game.lastTurn.verb = cur_verb
            obj_words = self.getGrammarObj(cur_verb, input_tokens, gv[0][1])
            if not obj_words:
                return 0
            # turn OFF self.disambiguation mode for next turn
            self.game.lastTurn.ambig_noun = None
            self.game.lastTurn.ambig_verb = None
            self.game.lastTurn.ambiguous = False
            self.game.lastTurn.err = False
            self.callVerb(cur_verb, obj_words)
            return 0
        else:
            # TODO: this was a hack. make sure it's fixed with Events
            #            if input_tokens in [["save"], ["load"]]:
            #                self.game.app.newBox(self.game.app.box_style1)
            if input_tokens == ["full", "score"]:
                fullScoreVerb.verbFunc(self.game)
            elif input_tokens == ["score"]:
                scoreVerb.verbFunc(self.game)
            elif input_tokens == ["fullscore"]:
                fullScoreVerb.verbFunc(self.game)
            elif input_tokens == ["about"]:
                self.game.aboutGame.printAbout(self.game)
            else:
                self.game.addTextToEvent(
                    "turn",
                    "The game has ended. Commands are SCORE, FULLSCORE, and ABOUT.",
                )

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
from .exceptions import (
    VerbDefinitionError,
    VerbMatchError,
    ObjectMatchError,
    ParserError,
    OutOfRange,
    AbortTurn,
)


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
        self.game.turn_list.append(input_string)

        if self.game.recfile:
            with open(self.game.recfile, "a") as recfile:
                recfile.write(input_string + "\n")

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
            vbo = self.verbByObjects(input_tokens, verbs)
            found_verbs = bool(verbs)
            return [vbo, found_verbs]

        self.game.lastTurn.err = True
        if self.game.lastTurn.convNode:
            raise ParserError(
                f"{' '.join(input_tokens).capitalize()} is not enough information "
                "to match a suggestion. "
            )

        if self.game.lastTurn.ambiguous or self.game.lastTurn.convNode:
            self.disambig(input_tokens)
            return None

        raise VerbMatchError(f"I don't understand the verb: {input_tokens[0]}")

    def verbByObjects(self, input_tokens, verbs):
        """
        Disambiguates verbs based on syntax used
        Takes arguments input_tokens, the self.tokenized 
        player command (list of strings), and verbs, a list of Verb objects (verb.py)
        Called by self.getCurVerb
        Iterates through verb list, comparing syntax in input to the entries in the .syntax 
        property of the verb
        Returns a two item list of a Verb object and an associated verb form (list of 
        strings), or None
        """
        near_match = []
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
                    near_match.append([cur_verb, verb_form])
        if not near_match:
            ambiguous_noun = False
            if self.game.lastTurn.ambig_noun:
                terms = nounDict[self.game.lastTurn.ambig_noun]
                for term in terms:
                    if (
                        input_tokens[0] in term.adjectives
                        or input_tokens[0] in term.synonyms
                        or input_tokens[0] == term.name
                    ):
                        ambiguous_noun = True

            self.game.lastTurn.err = True

            if not ambiguous_noun:
                raise ParserError(
                    'I understood as far as "'
                    + input_tokens[0]
                    + '".<br>(Type VERB HELP '
                    + input_tokens[0].upper()
                    + " for help with phrasing.) ",
                )

            return None

        removeMatch = []
        for pair in near_match:
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
                dobj = self._analyzeSyntax(verb_form, "<dobj>", input_tokens)
                iobj = self._analyzeSyntax(verb_form, "<iobj>", input_tokens)
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
            ) or (verb.iscope == "direction" and not self.directionRangeCheck(iobj)):
                removeMatch.append(pair)

        for x in removeMatch:
            near_match.remove(x)

        if len(near_match) == 1:
            return near_match[0]

        raise ParserError(
            'I understood as far as "'
            + input_tokens[0]
            + '".<br>(Type VERB HELP '
            + input_tokens[0].upper()
            + " for help with phrasing.) ",
        )

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
            dobj = None
            iobj = None
            if cur_verb.hasDobj:
                dobj = self._analyzeSyntax(verb_form, "<dobj>", input_tokens)
                if not dobj and not cur_verb.impDobj:
                    raise VerbDefinitionError(
                        f"<dobj> tag was not found in verb form {verb_form}, "
                        f"but associated verb {cur_verb} has dobj=True"
                    )
            if cur_verb.hasIobj:
                iobj = self._analyzeSyntax(verb_form, "<iobj>", input_tokens)
                if not iobj and not cur_verb.imp_dobj:
                    raise VerbDefinitionError(
                        f"<iobj> tag was not found in verb form {verb_form}, "
                        f"but associated verb {cur_verb} has iobj=True"
                    )
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

    def _analyzeSyntax(self, verb_form, tag, input_tokens):
        """
        Parse verb form (list of strings) to find the words directly preceding and 
        following object tags, and pass these to self.getObjWords find the objects in the 
        player's command
        Takes arguments:
        - verb_form, the assumed syntax of the command (list of strings),
        - tag (string, "<dobj>" or "<iobj>"),
        - input_tokens (list of strings)
        Returns None or a list of strings
        """
        # get words before and after
        if tag in verb_form:
            obj_i = verb_form.index(tag)

        else:
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

        Takes arguments:
        - cur_verb (Verb object, verb.py),
        - dobj, the direct object of the command (list of strings or None),
        - iobj, the indirect object

        Raises AbortTurn in the event of a missing direct or indirect
        object.

        Returns None, or a list of two items, either lists of strings, or None
        """
        missing = False
        if cur_verb.hasDobj and not dobj:
            if cur_verb.impDobj:
                dobj = cur_verb.getImpDobj(self.game)
            if not dobj:
                missing = True

        if cur_verb.hasIobj and not iobj:
            if cur_verb.impIobj:
                iobj = cur_verb.getImpIobj(self.game)
            if not iobj:
                missing = True

        self.game.lastTurn.dobj = dobj
        self.game.lastTurn.iobj = iobj

        if missing:
            self.game.lastTurn.err = True
            raise AbortTurn(f"Missing object for verb {cur_verb}")

        return [dobj, iobj]

    def getObjWords(self, game, before, after, input_tokens):
        """
        Create a list of all nouns and adjectives (strings) referring to a direct or 
        indirect object
        Takes arguments
        - before, the word expected before the grammatical object (string), 
        - after, the word expected after the grammatical object (string or None),
        - input_tokens, the self.tokenized player command (list of strings)
        Called by self._analyzeSyntax
        Returns an array of strings or None
        """
        if before[0] == "<":
            # find the index of the first noun in the noun dict.
            # if there is more than one, reject any that double as adjectives
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
                # we have eliminated all adjectives
                # if there are at least 2 words, we can assume that the first
                # is part of the other object
                return None
            # set before to the first noun
            before = nounlist[0]
        if after:
            if after[0] == "<":
                # find the index of the first noun in the noun dict.
                # if there is more than one, reject any that double as adjectives
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
            raise VerbDefinitionError(f"Unrecognized object scope {scope}")
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

    def generateVerbScopeErrorMsg(self, scope, noun_adj_arr):
        """
        Prints the appropriate Thing out of scope message
        Takes arguments self.game.app, pointing to the PyQt self.game.app, scope, a string, and noun_adj_arr, a 
        list of strings
        Called by self.getThing and self.checkAdjectives
        Returns None
        """
        noun = " ".join(noun_adj_arr)

        self.game.lastTurn.err = True

        if scope == "wearing":
            self.game.addTextToEvent("turn",)
            self.game.lastTurn.err = True
            return f"You aren't wearing any {noun}."

        if scope == "room" or scope == "near" or scope == "roomflex":
            out_loc = self.game.me.getOutermostLocation()
            if not out_loc.resolveDarkness(self.game):
                return "It's too dark to see anything."
            return f"I don't see any {noun} here."

        if scope == "knows":
            return f"You don't know of any {noun}."

        elif scope == "direction":
            return f"{noun.capitalize()} is not a direction I recognize."

        return f"You don't have any {noun}."

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
        except ValueError:
            t_ix = None
        if self.game.lastTurn.things and (
            noun_adj_arr[-1] not in nounDict or not endnoun
        ):
            noun = self.game.lastTurn.ambig_noun
            if noun:
                noun_adj_arr.append(noun)
            things = self.game.lastTurn.things
        elif (
            self.game.lastTurn.ambiguous
            and t_ix is not None
            and t_ix <= len(self.game.lastTurn.things)
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
            raise ObjectMatchError(self.generateVerbScopeErrorMsg(scope, noun_adj_arr))
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

    def _disambigMsgNextJoiner(self, item, name_dict, name, unscanned):
        if item is name_dict[name][-1] and not len(unscanned):
            return "?"
        if (
            item is name_dict[name][-1]
            and len(unscanned) == 1
            and len(name_dict[unscanned[0]]) == 1
        ):
            return ", or "
        if len(name_dict[name]) == 1:
            return ", "
        if item is name_dict[name][-2] and not len(unscanned):
            return ", or "
        return ", "

    def _itemWithDisambigIndex(self, item, ix, location=None):
        msg = item.lowNameArticle(True)
        if isinstance(location, Room):
            location = location.floor
        if location == self.game.me:
            msg += " in your inventory"
        elif location:
            msg += f" {location.contains_preposition} {location.lowNameArticle(True)}"
        return msg + f" ({ix + 1})"

    def _disambigMsgNextItem(self, item, name_dict, name, unscanned, ix, location=None):
        return self._itemWithDisambigIndex(
            item, ix, location
        ) + self._disambigMsgNextJoiner(item, name_dict, name, unscanned)

    def _generateDisambigMsg(self, things):
        """
        Generate the disambiguation message for a list of things
        """
        name_match = self.verboseNamesMatch(things)
        # dictionary of verbose_names from the current set of things
        name_dict = name_match[1]
        msg = "Do you mean "
        scanned_keys = []

        if not name_match[0]:
            for thing in things:
                msg += self._itemWithDisambigIndex(thing, things.index(thing))
                if thing is things[-1]:
                    msg += "?"
                elif len(things) > -2 and thing is things[-2]:
                    msg += ", or "
                else:
                    msg += ", "
            return msg

        things = []
        # empty things to reorder elements according to the order printed,
        # since we are using name_dict
        for name in name_dict:
            # use name_dict for self.disambiguation message composition rather than things
            scanned_keys.append(name)
            unscanned = list(set(name_dict.keys()) - set(scanned_keys))
            if len(name_dict[name]) > 1:
                if self.locationsDistinct(name_dict[name]):
                    for item in name_dict[name]:
                        things.append(item)
                        loc = item.location
                        if not loc:
                            pass
                        msg += self._disambigMsgNextItem(
                            item, name_dict, name, unscanned, things.index(item), loc
                        )
                    return msg

                for item in name_dict[name]:
                    things.append(item)
                    msg += self._disambigMsgNextItem(
                        item, name_dict, name, unscanned, things.index(item)
                    )
                return msg

            for item in name_dict[name]:
                things.append(item)
                msg += self._disambigMsgNextItem(
                    item, name_dict, name, unscanned, things.index(item)
                )
            return msg

            return msg

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
            except ValueError:
                n_select = None
            if n_select is not None and n_select <= len(things):
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

        if len(things) == 0:
            raise OutOfRange(self.generateVerbScopeErrorMsg(scope, noun_adj_arr))

        if len(things) > 1:
            msg = self._generateDisambigMsg(things)
            # turn ON self.disambiguation mode for next turn
            self.game.lastTurn.ambiguous = True
            self.game.lastTurn.ambig_noun = noun
            self.game.lastTurn.things = things
            raise ObjectMatchError(msg)

    def prepareGrammarObjects(self, cur_verb, obj_words):
        (dobj, iobj) = self.getObjectThings(cur_verb, obj_words)
        (dobj, iobj) = self.checkComponentObjects(cur_verb, obj_words, dobj, iobj)
        self.resolveGrammarObjLocations(cur_verb, dobj, iobj)

        return dobj, iobj

    def callVerb(self, cur_verb, cur_dobj, cur_iobj):
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
        if not isinstance(dobj, Thing) and cur_verb.hasDobj:
            dobj = input_tokens
        elif not isinstance(iobj, Thing) and cur_verb.hasIobj:
            iobj = input_tokens
        (dobj, iobj) = self.prepareGrammarObjects(cur_verb, [dobj, iobj])
        self.callVerb(cur_verb, dobj, iobj)
        return True

    def checkComponentObjects(self, cur_verb, obj_words, initial_dobj, initial_iobj):
        """
        Check if any of the identified objects have subcomponents that are better
        candidates as objects of the current verb.
        """
        dobj = self._checkComponentObject(obj_words[0], cur_verb, "dobj", initial_dobj)
        self.game.lastTurn.dobj = dobj
        iobj = self._checkComponentObject(obj_words[1], cur_verb, "iobj", initial_iobj)
        self.game.lastTurn.iobj = iobj

        if dobj != initial_dobj:
            self.game.addTextToEvent(
                "turn", "(Assuming " + dobj.lowNameArticle(True) + ".)",
            )

        if iobj != initial_iobj:
            self.game.addTextToEvent(
                "turn", "(Assuming " + iobj.lowNameArticle(True) + ".)",
            )

        return dobj, iobj

    def _checkComponentObject(self, obj_words, cur_verb, which_obj, obj):
        """
        Check if the given object has a subcomponent that is a better candidate for
        object of the current verb.
        
        Takes arguments
        - obj_words, the words from the player comman that specify the object
        - cur_verb, the current verb
        - which_obj, a string "dobj" or "iobj" specifying whether this object is direc
          or indirect
        - obj, the Thing instance to examine

        Raises TypeError if passed an invalid parameter for which_obj
        """

        COMPONENT_CLASSES = (
            {"class": Container, "component_holder": "child_Containers"},
            {"class": Surface, "component_holder": "child_Surfaces"},
            {"class": UnderSpace, "component_holder": "child_UnderSpaces"},
        )

        if not which_obj in ("dobj", "iobj"):
            raise TypeError(f'Invalid object specifier "{which_obj}".')

        scope = getattr(cur_verb, f"{which_obj[:1]}scope")
        far_obj = getattr(cur_verb, f"far_{which_obj}")
        obj_direction = getattr(cur_verb, f"{which_obj}_direction")
        obj_type = getattr(cur_verb, f"{which_obj[:1]}type")

        if scope == "text" or scope == "direction" or not obj:
            return obj

        for section in COMPONENT_CLASSES:
            if (
                not isinstance(obj, section["class"])
                and obj_type == section["class"].__name__
            ):
                composite_section = getattr(obj, section["component_holder"])
                if not composite_section:
                    continue
                obj = self.checkAdjectives(
                    obj_words, False, composite_section, scope, far_obj, obj_direction
                )
                return obj
        return obj

    def implicitRemoveNestedInventory(self, cur_verb, cur_dobj, cur_iobj):
        cur_dobj = self._liquidContainerRedirect(cur_verb, "dobj", cur_dobj)
        if (
            cur_dobj
            and cur_dobj.location
            and cur_dobj.location.location == self.game.me
            and cur_verb.dscope == "inv"
        ):
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
                raise AbortTurn(
                    f"Implicit removal failed. Could not remove {cur_dobj} from "
                    f"{cur_dobj.location}"
                )

        cur_iobj = self._liquidContainerRedirect(cur_verb, "iobj", cur_dobj)
        if (
            cur_iobj
            and cur_iobj.location
            and cur_iobj.location.location == self.game.me
            and cur_verb.iscope == "inv"
        ):
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
                raise AbortTurn(
                    f"Implicit removal failed. Could not remove {cur_dobj} from "
                    f"{cur_dobj.location}"
                )

    def _liquidContainerRedirect(self, cur_verb, which_obj, obj):
        scope = getattr(cur_verb, f"{which_obj[:1]}scope")

        if scope in ("text", "direction") or not obj or not obj.location:
            return obj

        if isinstance(obj, Liquid):
            return obj.getContainer()

        return obj

    def resolveGrammarObjLocations(self, cur_verb, dobj, iobj):
        """
        Perform implicit actions to bring the objects into verb range where possible.
        """
        self.implicitRemoveNestedInventory(cur_verb, dobj, iobj)

        if cur_verb.hasIobj:
            if not iobj:
                raise ObjectMatchError("I don't understand.")
            self._resolveGrammarObjLocation(cur_verb.iscope, iobj)

        if cur_verb.hasDobj:
            if not dobj:
                return False
            self._resolveGrammarObjLocation(cur_verb.dscope, dobj)

    def _resolveGrammarObjLocation(self, scope, obj):
        if scope == "text":
            return " ".join(obj)

        if scope == "direction":
            obj = " ".join(obj)
            correct = self.directionRangeCheck(obj)
            if not correct:
                raise ObjectMatchError(
                    f"{obj.capitalize} is not a direction I recognize."
                )
            return obj

        if scope == "room" and self.invRangeCheck(obj):
            dropVerb.verbFunc(self.game, obj)
        elif (
            scope in ("inv", "invflex")
            and obj is not self.game.me
            and self.roomRangeCheck(obj)
        ):
            self.game.addTextToEvent(
                "turn",
                "(First attempting to take "
                + obj.getArticle(True)
                + obj.verbose_name
                + ") ",
            )
            success = getVerb.verbFunc(self.game, obj)
            if not success:
                raise AbortTurn(f"Implicit take failed. Could not take {obj}")

        elif scope == "inv" and self.wearRangeCheck(obj):
            success = verb.doffVerb.verbFunc(self.game, obj)
            if not success:
                raise AbortTurn(f"Implicit doff failed. Could not doff {obj}")

    def getObjectThings(self, cur_verb, obj_words):
        """
        Get the IFPObject instances for each of the grammar objects, if applicable

        Arguments:
        - cur_verb, the current verb
        - obj_words, array of words or IFPObjects for dobj, iobj
        """
        if cur_verb.hasDobj:
            cur_dobj = self._getObjectThing(cur_verb, "dobj", obj_words[0])
        else:
            cur_dobj = None
        self.game.lastTurn.dobj = cur_dobj

        if cur_verb.hasIobj:
            cur_iobj = self._getObjectThing(cur_verb, "iobj", obj_words[1])
        else:
            cur_iobj = None
        self.game.lastTurn.iobj = cur_iobj

        return (cur_dobj, cur_iobj)

    def _getObjectThing(self, cur_verb, which_obj, obj_words):
        """
        Get the target IFPObject for a list of words, if applicable
        """
        scope = getattr(cur_verb, f"{which_obj[:1]}scope")
        far_obj = getattr(cur_verb, f"far_{which_obj}")
        obj_direction = getattr(cur_verb, f"{which_obj}_direction")

        if not isinstance(obj_words, list):
            # assume that obj_words already contains the IFPObject
            return obj_words

        if scope in ("text", "direction"):
            return obj_words

        return self.getThing(obj_words, scope, far_obj, obj_direction,)

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

    def runTurnCommand(self, input_tokens):
        if len(input_tokens) == 0:
            self.game.lastTurn.err = True
            return

        if (
            input_tokens[0:2] == ["help", "verb"]
            or input_tokens[0:2] == ["verb", "help"]
        ) and len(input_tokens) > 2:
            helpVerbVerb.verbFunc(self.game, input_tokens[2:])
            return
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
            return
        if self.game.lastTurn.convNode:
            conv_command = self.getConvCommand(input_tokens)
            if conv_command:
                self.game.lastTurn.ambig_noun = None
                self.game.lastTurn.ambig_verb = None
                self.game.lastTurn.ambiguous = False
                return
            else:
                pass

        gv = self.getCurVerb(input_tokens)
        if not gv:
            # gv is None only for disambig mode
            return
        cur_verb = gv[0][0]

        self.game.lastTurn.verb = cur_verb
        obj_words = self.getGrammarObj(cur_verb, input_tokens, gv[0][1])
        # turn OFF self.disambiguation mode for next turn
        self.game.lastTurn.ambig_noun = None
        self.game.lastTurn.ambig_verb = None
        self.game.lastTurn.ambiguous = False
        self.game.lastTurn.err = False
        (dobj, iobj) = self.prepareGrammarObjects(cur_verb, obj_words)
        self.callVerb(cur_verb, dobj, iobj)

    def parseInput(self, input_string):
        """
        Parse player input, and respond to commands each turn
        Takes argument input_string, the raw player input
        Called by mainLoop in terminal version, turnMain (gui.py) in GUI version
        Returns 0 when complete
        """
        # print back the player's command
        self.game.addEvent(
            "command", 0, text=input_string, style=self.game.command_event_style
        )
        # clean and self.tokenize
        input_tokens = self.getTokens(input_string)
        if not self.game.lastTurn.gameEnding:
            try:
                self.runTurnCommand(input_tokens)
            except ParserError as e:
                self.game.addTextToEvent(
                    "turn", e.__str__(),
                )
            except AbortTurn:
                return
            return

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
                "turn", "The game has ended. Commands are SCORE, FULLSCORE, and ABOUT.",
            )

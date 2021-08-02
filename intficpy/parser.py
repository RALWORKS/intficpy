import importlib
import string
import re

from .vocab import english
from .grammar import Command, GrammarObject
from .verb import (
    ScoreVerb,
    FullScoreVerb,
    HelpVerbVerb,
    GetVerb,
    StandUpVerb,
    DropVerb,
    RemoveFromVerb,
)
from .thing_base import Thing
from .things import Container, Surface, UnderSpace, Liquid
from .room import Room
from .travel import directionDict
from .tokenizer import cleanInput, tokenize, removeArticles
from .exceptions import (
    NoMatchingSuggestion,
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
        self.command = Command()
        self.previous_command = Command()
        self.previous_command.dobj = GrammarObject()
        self.previous_command.iobj = GrammarObject()
        self.turns = 0

    def recordInput(self, input_string):
        self.game.turn_list.append(input_string)

        if self.game.recfile:
            with open(self.game.recfile, "a") as recfile:
                recfile.write(input_string + "\n")

        return input_string

    def clearCommand(self):
        if self.previous_command:
            del self.previous_command
        self.previous_command = self.command
        self.command = None

    def replace_string_vars(self, text):
        """
        Perform string replacements for text in the format
        <<main_module.module.attribute ... >>

        This should be called by the Game instance when text is
        added to an event
        """
        if not ("<<" in text and ">>" in text):
            return text
        tokens = re.split(r"(<<[a-zA-Z0-9\.\(\)_]+>>)", text)
        text = ""
        for tok in tokens:
            if tok.startswith("<<") and tok.endswith(">>"):
                if "(" in tok:
                    raise NotImplementedError(
                        f"IntFicPy cannot perform the replacement `{tok}`. "
                        "<<syntax>>> string replacement does not support inserting "
                        "return values from functions or callables"
                    )

                nested_attrs = tok[2:-2]
                nested_attrs = nested_attrs.split(".")
                obj = self.game.main
                for attr in nested_attrs:
                    obj = getattr(obj, attr)
                tok = str(obj)
            text += tok

        return text

    def getDirection(self):
        """
        Check for direction statement as in "west" or "ne"
        Called every turn by self.parseInput
        Raises AbortTurn on discovering & executing a travel command
        """
        d = self.command.tokens[0]
        if d in directionDict and len(self.command.tokens) == 1:
            if self.previous_command.ambiguous:
                candidates = []
                for obj in self.previous_command.things:
                    if d in obj.adjectives:
                        return False
            directionDict[d]["func"](self.game)

            raise AbortTurn("Executed direction statement")
        return

    def getCurVerb(self):
        """
        Identify the verb
        Called every turn by self.parseInput
        Returns a two item list. The first is a Verb object and an associated verb form
        (list of strings), or None.
        The second is True if potential verb matches were found, False otherwise
        """
        # look up first word in verb dictionary
        if self.command.primary_verb_token in self.game.verbs:
            self.command.verb_matches = list(
                self.game.verbs[self.command.primary_verb_token]
            )
            self.matchPrepKeywords()
            self.verbByObjects()
            if self.command.verb:
                return
        self.checkForConvCommand()

        self.command.err = True
        if self.previous_command.specialTopics or (
            self.previous_command.sequence and self.previous_command.sequence.options
        ):
            raise ParserError(
                f"{' '.join(self.command.tokens).capitalize()} is not enough information "
                "to match a suggestion. "
            )

        if self.previous_command.ambiguous or self.previous_command.specialTopics:
            self.disambig()
            raise AbortTurn("Disambiguation complete.")

        self.getDirection()

        raise VerbMatchError(
            f"I don't understand the verb: {self.command.primary_verb_token}"
        )

    def checkForConvCommand(self):
        self.sendTokensToCurrentSequence()
        if self.previous_command.specialTopics and self.getConvCommand():
            raise AbortTurn("Accepted conversation suggestion")

    def verbByObjects(self):
        """
        Disambiguates verbs based on syntax used
        Iterates through verb list, comparing syntax in input to the entries in the
        .syntax attribute of the verb
        """
        self.checkForConvCommand()

        match_pairs = []
        for cur_verb in self.command.verb_matches:
            for verb_form in cur_verb.syntax:
                i = len(verb_form)
                for word in verb_form:
                    if word[0] != "<":
                        if word not in self.command.tokens:
                            break
                        else:
                            i = i - 1
                    else:
                        i = i - 1
                if i == 0:
                    match_pairs.append([cur_verb, verb_form])

        removeMatch = []
        for pair in match_pairs:
            verb = pair[0]
            verb_form = pair[1]
            adjacent = False
            if verb.hasDobj:
                d_ix = verb_form.index("<dobj>")
                if not "<dobj>" == verb_form[-1]:
                    if verb_form[d_ix + 1] == "<iobj>":
                        adjacent = True
                if verb_form[d_ix - 1] == "<iobj>":
                    adjacent = True

            if adjacent and verb.dscope in ["text", "direction"]:
                (dobj, iobj) = self._adjacentStrObj(verb_form, "<dobj>") or (None, None)
            elif adjacent and verb.iscope in ["text", "direction"]:
                (dobj, iobj) = self._adjacentStrObj(verb_form, "<iobj>") or (None, None)
            else:
                dobj = self._analyzeSyntax(verb_form, "<dobj>")
                iobj = self._analyzeSyntax(verb_form, "<iobj>")

            pair += [dobj, iobj]

            extra = self.checkExtra(verb, verb_form, dobj, iobj)

            if len(extra) > 0:
                removeMatch.append(pair)

            elif verb.hasDobj and not verb.impDobj and not dobj:
                removeMatch.append(pair)
            elif verb.hasIobj and not verb.impIobj and not iobj:
                removeMatch.append(pair)
            elif (
                verb.dscope == "direction" and not self.directionRangeCheck(dobj)
            ) or (verb.iscope == "direction" and not self.directionRangeCheck(iobj)):
                removeMatch.append(pair)

        for x in removeMatch:
            match_pairs.remove(x)

        if len(match_pairs) == 1:
            self.command.verb = match_pairs[0][0]
            self.command.verb_form = match_pairs[0][1]

            self.command.dobj = GrammarObject(match_pairs[0][2])
            self.command.iobj = GrammarObject(match_pairs[0][3])
            return

        raise ParserError(
            'I understood as far as "'
            + self.command.primary_verb_token
            + '".<br>(Type VERB HELP '
            + self.command.primary_verb_token.upper()
            + " for help with phrasing.) ",
        )

    def checkExtra(self, verb, verb_form, dobj, iobj):
        """
        Checks for words unaccounted for by verb form

        Returns a list, empty or containing one word strings (extra words)
        """

        accounted = []
        extra = list(self.command.tokens)

        for word in extra:
            if word in english.prepositions or word in english.keywords:

                if word in verb_form:
                    accounted.append(word)
                    continue

                for obj in [dobj, iobj]:
                    if not obj:
                        break
                    noun = obj[-1]
                    if noun in self.game.nouns:
                        for item in self.game.nouns[noun]:
                            if word in item.adjectives:
                                accounted.append(word)
                                break
                        if word in accounted:
                            break

                if (
                    word in ("up", "down", "in", "out")
                    and verb.iscope == "direction"
                    and (
                        (iobj and len(iobj) == 1 and word in iobj)
                        or (dobj and len(dobj) == 1 and word in dobj)
                    )
                ):
                    accounted.append(word)

            elif word in verb_form:
                accounted.append(word)

            elif dobj and word in dobj:
                accounted.append(word)

            elif iobj and word in iobj:
                accounted.append(word)

        for word in accounted:
            if word in extra:
                extra.remove(word)
        return extra

    def matchPrepKeywords(self):
        """
        Check for prepositions in the self.tokenized player command, and remove any candidate
        verbs whose preposition does not match
        Returns a list of Verb objects or an empty list
        """
        remove_verb = []
        for p in english.prepositions:
            if p in self.command.tokens and len(self.command.tokens) > 1:
                exempt = False
                for verb in self.command.verb_matches:
                    ix = self.command.tokens.index(p) + 1
                    if ix < len(self.command.tokens):
                        noun = self.command.tokens[ix]
                        while not noun in self.game.nouns:
                            ix = ix + 1
                            if ix >= len(self.command.tokens):
                                break
                            noun = self.command.tokens[ix]
                        if noun in self.game.nouns:
                            for item in self.game.nouns[noun]:
                                if p in item.adjectives:
                                    exempt = True
                    if p in ["up", "down", "in", "out"]:
                        if verb.iscope == "direction" or verb.dscope == "direction":
                            exempt = True
                    if (
                        not (verb.preposition or not p in verb.preposition)
                        and not exempt
                    ):
                        remove_verb.append(verb)
        for p in english.keywords:
            if p in self.command.tokens and len(self.command.tokens) > 1:
                exempt = False
                for verb in self.command.verb_matches:
                    ix = self.command.tokens.index(p) + 1
                    if ix < len(self.command.tokens):
                        noun = self.command.tokens[ix]
                        while not noun in self.game.nouns:
                            ix = ix + 1
                            if ix >= len(self.command.tokens):
                                break
                            noun = self.command.tokens[ix]
                        if noun in self.game.nouns:
                            for item in self.game.nouns[noun]:
                                if p in item.adjectives:
                                    exempt = True
                    if not (verb.keywords or not p in verb.keywords) and not exempt:
                        remove_verb.append(verb)
        for verb in remove_verb:
            if verb in self.command.verb_matches:
                self.command.verb_matches.remove(verb)

    def getGrammarObj(self):
        """
        Analyze input using the chosen verb_form to find any objects
        """
        # first, choose the correct syntax
        if not self.command.verb_form:
            return None
        # check if dobj and iobj are adjacent
        adjacent = False
        if self.command.verb.hasDobj:
            d_ix = self.command.verb_form.index("<dobj>")
            if not "<dobj>" == self.command.verb_form[-1]:
                if self.command.verb_form[d_ix + 1] == "<iobj>":
                    adjacent = True
            if self.command.verb_form[d_ix - 1] == "<iobj>":
                adjacent = True

        if self.command.verb.hasDobj and not self.command.dobj:
            self.command.dobj = GrammarObject(
                self._analyzeSyntax(self.command.verb_form, "<dobj>")
            )
            if not self.command.dobj.tokens and not self.command.verb.impDobj:
                raise VerbDefinitionError(
                    f"<dobj> tag was not found in verb form {verb_form}, "
                    f"but associated verb {self.command.verb} has dobj=True"
                )
        if self.command.verb.hasIobj and not self.command.iobj:
            self.command.iobj = GrammarObject(
                self._analyzeSyntax(self.command.verb_form, "<iobj>")
            )
            if not self.command.iobj.tokens and not self.command.verb.imp_dobj:
                raise VerbDefinitionError(
                    f"<iobj> tag was not found in verb form {verb_form}, "
                    f"but associated verb {self.command.verb} has iobj=True"
                )
        self.checkForImplicitObjects()

    def _adjacentStrObj(self, verb_form, strobj_tag):
        dobj_ix = verb_form.index("<dobj>")
        iobj_ix = verb_form.index("<iobj>")
        if verb_form[-1] == "<dobj>":
            before = verb_form[iobj_ix - 1]
            after = None
        elif verb_form[-1] == "<iobj>":
            before = verb_form[dobj_ix - 1]
            after = None
        elif iobj_ix < dobj_ix:
            before = verb_form[iobj_ix - 1]
            after = verb_form[dobj_ix + 1]
        else:
            before = verb_form[dobj_ix - 1]
            after = verb_form[iobj_ix + 1]
        b_ix = self.command.tokens.index(before) + 1
        if not after:
            a_ix = None
            objs = self.command.tokens[b_ix:]
        else:
            a_ix = self.command.tokens.index(after)
            objs = self.command.tokens[b_ix:a_ix]

        thing_follows_string = True
        if (strobj_tag == "<dobj>" and dobj_ix > iobj_ix) or (
            strobj_tag == "<iobj>" and iobj_ix > dobj_ix
        ):
            thing_follows_string = False

        if thing_follows_string:
            if not objs[-1] in self.game.nouns or len(objs) < 2:
                return None
            things = self.game.nouns[objs[-1]]
            end_str = len(objs) - 1
            while end_str > 1:
                accounted = False
                for item in things:
                    tokens_in_adjectives = [
                        tok in item.adjectives for tok in objs[end_str:-1]
                    ]
                    if all(tokens_in_adjectives):
                        accounted = True
                if not accounted:
                    break
                end_str -= 1
            strobj = objs[:end_str]
            tobj = objs[end_str:]

        else:  # string follows thing
            noun = None
            for word in objs:
                if word in self.game.nouns:
                    noun = word
                    break
            if not noun:
                return
            start_str = objs.index(noun) + 1
            end_str = len(objs) - 1
            strobj = objs[start_str:]
            tobj = objs[:start_str]

        if strobj_tag == "<dobj>":
            return (strobj, tobj)
        else:
            return (tobj, strobj)

    def _analyzeSyntax(self, verb_form, tag):
        """
        Parse verb form (list of strings) to find the words directly preceding and
        following object tags, and pass these to self.getObjWords find the objects in the
        player's command
        Takes arguments:
        - verb_form, the assumed syntax of the command (list of strings),
        - tag (string, "<dobj>" or "<iobj>")
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
        return self.getObjWords(self.game.app, before, after)

    def checkForImplicitObjects(self):
        """
        Raises AbortTurn in the event of a missing direct or indirect
        object.

        Returns None, or a list of two items, either lists of strings, or None
        """
        implicit_get_failed = False
        if (
            self.command.verb.hasDobj
            and not self.command.dobj.tokens
            and self.command.verb.impDobj
        ):
            self.command.dobj.target = self.command.verb().getImpDobj(self.game)
            if not self.command.dobj.target:
                implicit_get_failed = True

        if (
            self.command.verb.hasIobj
            and not self.command.iobj.tokens
            and self.command.verb.impIobj
        ):
            self.command.iobj.target = self.command.verb().getImpIobj(self.game)
            if not self.command.iobj.target:
                implicit_get_failed = True

        if implicit_get_failed:
            self.command.err = True
            raise AbortTurn(f"Missing object for verb {self.command.verb}")

    def getObjWords(self, game, before, after):
        """
        Create a list of all nouns and adjectives (strings) referring to a direct or
        indirect object
        Takes arguments
        - before, the word expected before the grammatical object (string),
        - after, the word expected after the grammatical object (string or None),
        Called by self._analyzeSyntax
        Returns an array of strings or None
        """
        if before[0] == "<":
            # find the index of the first noun in the noun dict.
            # if there is more than one, reject any that double as adjectives
            nounlist = []
            for word in self.command.tokens:
                if word in self.game.nouns:
                    nounlist.append(word)
            if len(nounlist) > 2:
                i = 0
                delnoun = []
                while i < (len(nounlist) - 1):
                    for item in self.game.nouns[nounlist[i]]:
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
                for word in self.command.tokens:
                    if word in self.game.nouns:
                        nounlist.append(word)
                if len(nounlist) > 2:
                    i = 0
                    delnoun = []
                    while i < (len(nounlist) - 1):
                        for item in self.game.nouns[nounlist[i]]:
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
                after_index = self.command.tokens.index(nounlist[0]) + 1
                after = self.command.tokens[after_index]

        low_bound = self.command.tokens.index(before)
        # add 1 for non-inclusive indexing
        low_bound = low_bound + 1
        if after:
            high_bound = self.command.tokens.index(after)
            obj_words = self.command.tokens[low_bound:high_bound]
        else:
            obj_words = self.command.tokens[low_bound:]
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
        too_dark = not out_loc.resolveDarkness(self.game)
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
                    DropVerb().verbFunc(self.game, thing)
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
        Takes arguments, scope, a string, and noun_adj_arr, a
        list of strings
        Returns None
        """
        noun = " ".join(noun_adj_arr)

        self.command.err = True

        if scope == "wearing":
            self.command.err = True
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
        adj_disambig_candidates = []
        for item in self.previous_command.things:
            if noun_adj_arr[-1] in item.adjectives:
                adj_disambig_candidates.append(item)
                thing = self.checkAdjectives(
                    noun_adj_arr + [item.name],
                    item.name,
                    [item],
                    scope,
                    far_obj,
                    obj_direction,
                )
                if thing:
                    adj_disambig_candidates.append(thing)

        t_ix = self.getDisambigIndexFromCommand()

        noun = noun_adj_arr[-1]
        # get list of associated Things
        if noun in self.game.nouns:
            things = list(self.game.nouns[noun])

        elif self.previous_command.things and adj_disambig_candidates:
            # assume tokens are adjectives for a Thing from the previous command
            noun = self.previous_command.ambig_noun
            if noun:
                noun_adj_arr.append(noun)
            things = adj_disambig_candidates

        elif t_ix and t_ix < len(self.previous_command.tokens):
            # assume tokens are adjectives for a Thing from the previous command
            return self.previous_command.things[t_ix - 1]

        else:
            things = []

        if not things:
            raise ObjectMatchError(self.generateVerbScopeErrorMsg(scope, noun_adj_arr))

        thing = self.checkAdjectives(
            noun_adj_arr, noun, things, scope, far_obj, obj_direction
        )

        if not thing:
            raise ObjectMatchError(self.generateVerbScopeErrorMsg(scope, noun_adj_arr))

        return thing

    def getDisambigIndexFromCommand(self):
        if len(self.command.tokens) != 1:
            return None
        try:
            return int(self.command.tokens[-1])
        except ValueError:
            return None

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

    def _generateDisambigMsg(self, things, msg):
        """
        Generate the disambiguation message for a list of things
        """
        name_match = self.verboseNamesMatch(things)
        # dictionary of verbose_names from the current set of things
        name_dict = name_match[1]
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
            # use name_dict for disambiguation message composition rather than things
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
        Returns a single Thing object or None
        """
        if things == self.previous_command.things:
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
            return None

        if len(things) > 1:
            if len(set([thing.ix for thing in things])) == 1:
                loc = things[0].location
                same_loc = True
                for thing in things:
                    if thing.location is not loc:
                        same_loc = False
                if same_loc:
                    return things[0]

            msg = self._generateDisambigMsg(things, "Do you mean ")
            # turn ON disambiguation mode for next turn
            self.command.ambiguous = True
            self.command.ambig_noun = noun
            self.command.things = things
            raise ObjectMatchError(msg)

    def _prepareGrammarObjects(self):
        self.getObjectTargets()
        self.checkComponentObjects()
        self.resolveGrammarObjLocations()

    def callVerb(self):
        """
        Gets the Thing objects (if any) referred to in the player command, then calls
        the verb function

        Returns a Boolean, True if a verb function is successfully called, False
        otherwise
        """
        if self.command.verb.hasDobj and self.command.verb.hasIobj:
            if (
                self.command.verb.dscope != "inv" or self.command.verb.iscope != "inv"
            ) and self.game.me.position != "standing":
                StandUpVerb().verbFunc(self.game)
            self.command.verb().verbFunc(
                self.game, self.command.dobj.target, self.command.iobj.target
            )
        elif self.command.verb.hasDobj:
            if (
                self.command.verb.dscope != "inv"
                and self.command.verb.dscope != "invflex"
                and self.game.me.position != "standing"
            ):
                StandUpVerb().verbFunc(self.game)
            self.command.verb().verbFunc(self.game, self.command.dobj.target)
        elif self.command.verb.hasIobj:
            if (
                self.command.verb.iscope != "inv"
                and self.command.verb.iscope != "invflex"
                and self.game.me.position != "standing"
            ):
                StandUpVerb().verbFunc(self.game)
            self.command.verb().verbFunc(self.game, self.command.iobj.target)
        else:
            self.command.verb().verbFunc(self.game)
        return True

    def disambig(self):
        """
        When disambiguation mode is active, use the player input to specify the target for
        the previous turn's ambiguous command
        called by self.parseInput
        Returns a Boolean, True if disambiguation
        """
        self.command.dobj = self.previous_command.dobj
        self.command.iobj = self.previous_command.iobj
        self.command.verb = self.previous_command.verb
        if not self.command.dobj.target and self.command.verb.hasDobj:
            self.command.dobj.tokens = self.command.tokens
        elif not self.command.iobj.target and self.command.verb.hasIobj:
            self.command.iobj.tokens = self.command.tokens
        self._prepareGrammarObjects()
        self.callVerb()

    def checkComponentObjects(self):
        """
        Check if any of the identified objects have subcomponents that are better
        candidates as objects of the current verb.
        """
        dobj = self._checkComponentObject("dobj", self.command.dobj.target)
        iobj = self._checkComponentObject("iobj", self.command.iobj.target)

        if dobj and self.command.dobj and dobj != self.command.dobj.target:
            self.game.addTextToEvent(
                "turn", "(Assuming " + dobj.lowNameArticle(True) + ".)",
            )
            self.command.dobj.target = dobj

        if iobj and self.command.iobj and iobj != self.command.iobj.target:
            self.game.addTextToEvent(
                "turn", "(Assuming " + iobj.lowNameArticle(True) + ".)",
            )
            self.command.iobj.target = iobj

    def _checkComponentObject(self, which_obj, obj):
        """
        Check if the given object has a subcomponent that is a better candidate for
        object of the current verb.

        Takes arguments
        - obj_words, the words from the player comman that specify the object
        - which_obj, a string "dobj" or "iobj" specifying whether this object is direc
          or indirect
        - obj, the Thing instance to examine

        Raises TypeError if passed an invalid parameter for which_obj
        """

        COMPONENT_CLASSES = {
            "Container": {"class": Container, "component_holder": "child_Containers"},
            "Surface": {"class": Surface, "component_holder": "child_Surfaces"},
            "UnderSpace": {
                "class": UnderSpace,
                "component_holder": "child_UnderSpaces",
            },
        }

        if not which_obj in ("dobj", "iobj"):
            raise TypeError(f'Invalid object specifier "{which_obj}".')

        scope = getattr(self.command.verb, f"{which_obj[:1]}scope")
        far_obj = getattr(self.command.verb, f"far_{which_obj}")
        obj_direction = getattr(self.command.verb, f"{which_obj}_direction")
        obj_type = getattr(self.command.verb, f"{which_obj[:1]}type")
        grammar_obj = getattr(self.command, which_obj)

        if scope == "text" or scope == "direction" or not obj:
            return obj

        if (
            obj_type
            and not obj.__class__.__name__ == obj_type
            and obj_type in COMPONENT_CLASSES
        ):
            components = getattr(obj, COMPONENT_CLASSES[obj_type]["component_holder"])
            matched_component = self.checkAdjectives(
                grammar_obj.tokens,
                grammar_obj.noun_token,
                components,
                scope,
                far_obj,
                obj_direction,
            )
            if matched_component:
                return matched_component

        return obj

    def implicitRemoveNestedInventory(self):
        if self.command.dobj and not self.command.verb.dscope in ["text", "direction"]:
            if (
                self.command.dobj.target
                and self.command.dobj.target.location
                and self.command.dobj.target.location.location == self.game.me
                and self.command.verb.dscope == "inv"
                and not (
                    self.command.dobj.target.liquid_type
                    and self.command.dobj.target.getContainer()
                )
            ):
                self.game.addTextToEvent(
                    "turn",
                    "(First removing "
                    + self.command.dobj.target.getArticle(True)
                    + self.command.dobj.target.verbose_name
                    + " from "
                    + self.command.dobj.target.location.getArticle(True)
                    + self.command.dobj.target.location.verbose_name
                    + ")",
                )
                success = RemoveFromVerb().verbFunc(
                    self.game,
                    self.command.dobj.target,
                    self.command.dobj.target.location,
                )
                if not success:
                    raise AbortTurn(
                        f"Implicit removal failed. Could not remove "
                        f"{self.command.dobj.target} from "
                        f"{self.command.dobj.target.location}"
                    )

        if self.command.iobj and not self.command.verb.iscope in ["text", "direction"]:
            if (
                self.command.iobj.target
                and self.command.iobj.target.location
                and self.command.iobj.target.location.location == self.game.me
                and self.command.verb.iscope == "inv"
                and not (
                    self.command.iobj.target.liquid_type
                    and self.command.iobj.target.getContainer()
                )
            ):
                self.game.addTextToEvent(
                    "turn",
                    "(First removing "
                    + self.command.iobj.target.getArticle(True)
                    + self.command.iobj.target.verbose_name
                    + " from "
                    + self.command.iobj.target.location.getArticle(True)
                    + self.command.iobj.target.location.verbose_name
                    + ")",
                )
                success = verb.removeFromVerb().verbFunc(
                    self.game,
                    self.command.iobj.target,
                    self.command.iobj.target.location,
                )
                if not success:
                    raise AbortTurn(
                        f"Implicit removal failed. Could not remove "
                        f"{self.command.iobj.target} from "
                        f"{self.command.iobj.target.location}"
                    )

    def _liquidContainerRedirect(self, which_obj, obj):
        scope = getattr(self.command.verb, f"{which_obj[:1]}scope")

        if scope in ("text", "direction") or not obj or not obj.location:
            return obj

        if isinstance(obj, Liquid):
            return obj.getContainer()

        return obj

    def resolveGrammarObjLocations(self):
        """
        Perform implicit actions to bring the objects into verb range where possible.
        """
        self.implicitRemoveNestedInventory()

        if self.command.verb.hasIobj:
            if not self.command.iobj.target:
                raise ObjectMatchError("I don't understand.")
            self._resolveTargetLocation(
                self.command.iobj.target, self.command.verb.iscope
            )

        if self.command.verb.hasDobj:
            if not self.command.dobj.target:
                return False
            self._resolveTargetLocation(
                self.command.dobj.target, self.command.verb.dscope
            )

    def _resolveTargetLocation(self, obj, scope):
        if scope == "text":
            return " ".join(obj)

        if scope == "direction":
            correct = self.directionRangeCheck(obj)
            if not correct:
                raise ObjectMatchError(
                    f"{obj.capitalize()} is not a direction I recognize."
                )
            return obj

        if scope == "room" and self.invRangeCheck(obj):
            DropVerb().verbFunc(self.game, obj)
        elif (
            scope in ("inv", "invflex")
            and obj is not self.game.me
            and self.command.verb.allow_implicit_take
            and self.roomRangeCheck(obj)
        ):
            self.game.addTextToEvent(
                "turn",
                "(First attempting to take "
                + obj.getArticle(True)
                + obj.verbose_name
                + ") ",
            )
            success = GetVerb().verbFunc(self.game, obj)
            if not success:
                raise AbortTurn(f"Implicit take failed. Could not take {obj}")

        elif scope == "inv" and self.wearRangeCheck(obj):
            success = verb.doffVerb().verbFunc(self.game, obj)
            if not success:
                raise AbortTurn(f"Implicit doff failed. Could not doff {obj}")

    def getObjectTargets(self):
        """
        Get the IFPObject instances for each of the grammar objects, if applicable

        Arguments:
        - obj_words, array of words or IFPObjects for dobj, iobj
        """
        if (
            self.command.verb.hasDobj
            and self.command.dobj
            and not self.command.dobj.target
        ):
            self.command.dobj.target = self._getObjectTarget(
                "dobj", self.command.dobj.tokens
            )

        if (
            self.command.verb.hasIobj
            and self.command.iobj
            and not self.command.iobj.target
        ):
            self.command.iobj.target = self._getObjectTarget(
                "iobj", self.command.iobj.tokens
            )

        if (
            self.command.dobj.target
            and self.command.iobj.target
            and self.command.iobj.target is self.game.reflexive
        ):
            self.command.iobj.target = self.command.dobj.target

    def _getObjectTarget(self, which_obj, obj_words):
        """
        Get the target IFPObject for a list of words, if applicable
        """
        scope = getattr(self.command.verb, f"{which_obj[:1]}scope")
        far_obj = getattr(self.command.verb, f"far_{which_obj}")
        obj_direction = getattr(self.command.verb, f"{which_obj}_direction")

        if not isinstance(obj_words, list):
            # assume that obj_words already contains the IFPObject
            return obj_words

        if scope in ("text", "direction"):
            return " ".join(obj_words)

        return self.getThing(obj_words, scope, far_obj, obj_direction,)

    def roomDescribe(self):
        """
        Wrapper for room describe function (room.py)
        """
        out_loc = self.game.me.getOutermostLocation()
        out_loc.describe(self.game)

    def getConvCommand(self):
        possible_topics = list(self.previous_command.specialTopics.keys())
        for key in self.previous_command.specialTopics:
            tokens = cleanInput(key, False)
            tokens = tokenize(tokens)
            tokens = removeArticles(tokens)
            for tok in self.command.tokens:
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
                            self.previous_command.specialTopics[topicA]
                            == self.previous_command.specialTopics[topicB]
                        ):
                            revised_possible_topics.remove(topicB)
        if len(revised_possible_topics) != 1:
            return False
        else:
            x = revised_possible_topics[0]
            self.previous_command.specialTopics[x].func(self.game)
            return True

    def sendTokensToCurrentSequence(self):
        """
        If there is a sequence in progress, pass in current tokens

        """
        if not self.previous_command.sequence:
            return
        try:
            self.previous_command.sequence.accept_input(self.command.tokens)
        except NoMatchingSuggestion:
            return

        raise AbortTurn("Input handled by current Sequence")

    def runTurnCommand(self):
        if len(self.command.tokens) == 0:
            self.command.err = True
            return

        if (
            self.command.tokens[0:2] == ["help", "verb"]
            or self.command.tokens[0:2] == ["verb", "help"]
        ) and len(self.command.tokens) > 2:
            HelpVerbVerb().verbFunc(self.game, self.command.tokens[2:])
            return
        elif self.command.tokens[0:2] == ["help", "verb"] or self.command.tokens[
            0:2
        ] == ["verb", "help",]:
            self.game.addTextToEvent("turn", "Please specify a verb for help. ")
            return 0
        # if input is a travel command, move player

        self.getCurVerb()
        if not self.command.verb:
            return

        self.getGrammarObj()
        self._prepareGrammarObjects()
        self.callVerb()

    def parseInput(self, input_string):
        """
        Parse player input, and respond to commands each turn
        Takes argument input_string, the raw player input
        Called by mainLoop in terminal version, turnMain (gui.py) in GUI version
        Returns 0 when complete
        """
        self.clearCommand()

        self.turns += 1
        # print back the player's command
        self.game.addEvent(
            "command", 0, text=input_string, style=self.game.command_event_style
        )
        # clean and self.tokenize
        input_string = cleanInput(input_string)
        self.recordInput(input_string)

        self.command = Command(input_string)
        if self.previous_command.has_sticky_sequence:
            self.command.sequence = self.previous_command.sequence

        if not self.game.ended:
            try:
                self.runTurnCommand()
            except ParserError as e:
                self.game.addTextToEvent(
                    "turn", e.__str__(),
                )
                if self.previous_command.has_active_sequence:
                    self.previous_command.sequence.play()
            except AbortTurn:
                pass
            return

        if self.command.tokens == ["full", "score"]:
            FullScoreVerb().verbFunc(self.game)
        elif self.command.tokens == ["score"]:
            ScoreVerb().verbFunc(self.game)
        elif self.command.tokens == ["fullscore"]:
            FullScoreVerb().verbFunc(self.game)
        elif self.command.tokens == ["about"]:
            self.game.aboutGame.printAbout(self.game)
        else:
            self.game.addTextToEvent(
                "turn", "The game has ended. Commands are SCORE, FULLSCORE, and ABOUT.",
            )

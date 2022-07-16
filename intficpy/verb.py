from abc import ABC

from .actor import Actor
from .thing_base import Thing
from .things import (
    Container,
    Surface,
    Liquid,
    UnderSpace,
    Transparent,
    Book,
    Readable,
    AbstractClimbable,
    Clothing,
    Door,
    Lock,
    Key,
    LightSource,
    Pressable,
)
from .room import Room
from .serializer import SaveGame, LoadGame

##############################################################
# VERB.PY - verbs for IntFicPy
# Defines the Verb class,  and the default verbs
##############################################################
# TODO: sort out circular imports for travel.travel, parser.parser
# currently importing from travel inside functions as a workaround
# move the most common implicit verbs into their own module?


class Verb(ABC):
    """Verb objects represent actions the player can take """

    allow_implicit_take = True
    list_word = None
    list_by_default = True
    word = None
    word = None
    synonyms = []
    far_iobj = False
    far_dobj = False
    hasDobj = False
    hasStrDobj = False
    hasStrIobj = False
    dtype = None
    hasIobj = False
    itype = None
    impDobj = False
    impIobj = False
    preposition = []
    keywords = []
    dobj_direction = False
    iobj_direction = False
    syntax = [[word]]
    # range for direct and indirect objects
    dscope = "room"  # "knows", "near", "room" or "inv"
    iscope = "room"

    allow_in_sequence = False

    failure_msg = "You cannot do that"

    def verbFunc(self, game, skip=False):
        """
        The default verb function
        """
        pass

    def _runVerbFuncAndEvents(self, game, *args):
        """
        This method is mainly used for testing.
        Game creators should generally allow IntFicPy to handle running turn events
        """
        success = self.verbFunc(game, *args)
        game.runTurnEvents()
        return success

    def getImpDobj(self, game):
        """Get the implicit direct object
        The creator should overwrite this if planning to use implicit objects
        View the ask verb for an example """
        raise NotImplementedError(
            f"getImpDobj not implemented for {self.__class__.__name} "
            "Implement this to use implicit objects with this verb"
        )

    def getImpIobj(self, game):
        """"Get the implicit indirect object
        The creator should overwrite this if planning to use implicit objects """
        raise NotImplementedError(
            f"getImpIobj not implemented for {self.__class__.__name} "
            "Implement this to use implicit objects with this verb"
        )

    @staticmethod
    def disambiguateActor(game, len0_msg, base_disambig_msg):
        """
        Disambiguate Actors. Excludes the Player.
        room - the room to search
        len0_msg - message to print in the case of no Actors
        base_disambig_msg - base message for disambiguation
        """
        room = game.me.getOutermostLocation()
        people = room.contentsByClass(Actor)
        people = list(
            filter(
                lambda item: not item.ignore_if_ambiguous and item is not game.me,
                people,
            )
        )

        if len(people) == 1:
            return people
        if len(people) == 0:
            game.addTextToEvent("turn", len0_msg)
        elif (
            game.parser.previous_command.dobj
            and game.parser.previous_command.dobj.target in people
            and isinstance(game.parser.previous_command.dobj.target, Actor)
        ):
            return [game.parser.previous_command.dobj.target]
        elif (
            game.parser.previous_command.iobj
            and game.parser.previous_command.iobj.target in people
            and isinstance(game.parser.previous_command.iobj.target, Actor)
        ):
            return [game.parser.previous_command.iobj.target]
        else:
            msg = game.parser._generateDisambigMsg(people, base_disambig_msg)
            game.addTextToEvent("turn", msg)
        return people

    def getImpTalkTo(self, game):
        """
        If no dobj is specified, try to guess the Actor
        """
        from .grammar import GrammarObject

        people = Verb.disambiguateActor(
            game,
            "There's no one obvious here to talk to. ",
            "Would you like to talk to ",
        )

        if len(people) == 0:
            return None

        elif len(people) == 1:
            game.parser.previous_command.dobj = GrammarObject(target=people[0])
            return people[0]

        game.parser.command.things = people
        game.parser.command.ambiguous = True
        return None


class DirectObjectVerb(Verb):
    word = None
    hasDobj = True
    syntax = [[word, "<dobj>"]]
    main_func_name = None
    pre_func_name = None

    def verbFunc(self, game, dobj, skip=False):
        """
        Base verb function for verbs with a direct object

        Checks for a verbFunc override on the direct object, and evaluates it if found.
        Returns immediately if the override returns True.
        Checks if the direct object as a cannot_interract_msg specified. Adds the text
        to the turn and returns if found.

        API:
        Subclasses should generally return True on success, and False on failure.

        Dobj/Iobj overrides (methods on the dobj/iobj in the form
        wordVerbDobj or wordVerbIobj) should return False to tell the core verbFunc
        to finish evaluating after perfroming the override func, and True to have the
        verbFunc return True (success) immediately after evaluating the override.
        There is currently no way to override the verbFunc to evaluate the override
        and return False (failure).

        skip parameter specifies whether or not to check for verb overrides on the
        direct object. The parser does not use skip, but skip=True may be useful for
        certain uses of the verbFunc by game authors
        """
        # TODO(#126): skip parameter: rename? refactor? remove?
        # TODO(#126): API for verbFunc overrides causing main verb func to evaluate vs
        #             immediately return is unclear & arbitrary. refactor

        pre = getattr(dobj, self.pre_func_name, None) if self.pre_func_name else None

        if pre and not pre(event="turn"):
            return False

        if not skip:
            abort_main_verb_func = False
            dfunc = getattr(
                dobj,
                f"{self.__class__.__name__[:1].lower() + self.__class__.__name__[1:]}Dobj",
                None,
            )
            if dfunc:
                abort_main_verb_func = dfunc(game)
            if abort_main_verb_func:
                return True

        if (
            not (self.hasStrDobj or self.dscope == "direction")
            and dobj.cannot_interact_msg
        ):
            game.addTextToEvent("turn", dobj.cannot_interact_msg)
            return False

        if not self.main_func_name:
            return

        func = getattr(dobj, self.main_func_name, None)

        if not func:
            game.addTextToEvent("turn", self.failure_msg.format(dobj=dobj))
            return False

        return func(event="turn")


class IndirectObjectVerb(DirectObjectVerb):
    word = None
    hasIobj = True
    preposition = ["with"]
    syntax = [[word, "<dobj>", "with", "<iobj>"]]
    iobj_target = False

    def verbFunc(self, game, dobj, iobj, skip=False):
        """
        Base verb function for verbs with a direct object and an indirect object

        Checks for a verbFunc override on the direct and indirecte objects, and
        evaluates them if found.
        After attempting to run both possible overrides, returns True immediately
        if either override returns True.
        Checks if the direct object or indirect object has a cannot_interract_msg
        specified. Adds the text to the turn and returns if found.

        API:
        Subclasses should generally return True on success, and False on failure.

        Dobj/Iobj overrides (methods on the dobj/iobj in the form
        wordVerbDobj or wordVerbIobj) should return False to tell the core verbFunc
        to finish evaluating after perfroming the override func, and True to have the
        verbFunc return True (success) immediately after evaluating the override.
        There is currently no way to override the verbFunc to evaluate the override
        and return False (failure).

        skip parameter specifies whether or not to check for verb overrides on the
        direct object. The parser does not use skip, but skip=True may be useful for
        certain uses of the verbFunc by game authors
        """
        if self.iobj_target:
            pre = (
                getattr(iobj, self.pre_func_name, None) if self.pre_func_name else None
            )
            item = dobj
        else:
            pre = (
                getattr(dobj, self.pre_func_name, None) if self.pre_func_name else None
            )
            item = iobj

        if pre and not pre(item, event="turn"):
            return False
        if not skip:
            abort_main_verb_func = False
            dfunc = getattr(
                dobj,
                f"{self.__class__.__name__[:1].lower() + self.__class__.__name__[1:]}Dobj",
                None,
            )
            ifunc = getattr(
                iobj,
                f"{self.__class__.__name__[:1].lower() + self.__class__.__name__[1:]}Iobj",
                None,
            )
            if dfunc:
                abort_main_verb_func = dfunc(game, iobj)
            if ifunc:
                abort_main_verb_func = ifunc(game, dobj) or abort_main_verb_func
            if abort_main_verb_func:
                return True

        if (
            not (self.hasStrDobj or self.dscope == "direction")
            and dobj.cannot_interact_msg
        ):
            game.addTextToEvent("turn", dobj.cannot_interact_msg)
            return False
        elif (
            not (self.hasStrIobj or self.iscope == "direction")
            and iobj.cannot_interact_msg
        ):
            game.addTextToEvent("turn", dobj.cannot_interact_msg)
            return False

        if not self.main_func_name:
            return

        if self.iobj_target:
            func = getattr(iobj, self.main_func_name, None)
        else:
            func = getattr(dobj, self.main_func_name, None)

        if not func:
            game.addTextToEvent("turn", self.failure_msg.format(dobj=dobj, iobj=iobj))
            return False

        return func(item, event="turn")


# Below are .IFP's built in verbs
###########################################################################

# GET/TAKE
# transitive verb, no indirect object
class GetVerb(DirectObjectVerb):
    word = "get"
    synonyms = ["take", "pick"]
    syntax = [
        ["get", "<dobj>"],
        ["take", "<dobj>"],
        ["pick", "up", "<dobj>"],
        ["pick", "<dobj>", "up"],
    ]
    preposition = ["up"]
    dscope = "roomflex"

    def verbFunc(self, game, dobj, skip=False):
        """
        Take a Thing from the Room.
        """
        super().verbFunc(game, dobj, skip=skip)

        if not dobj.playerAboutToTake(event="turn"):
            return False

        return dobj.playerTakes(event="turn")


# GET/TAKE ALL
# intransitive verb
class GetAllVerb(Verb):
    word = "get"
    list_word = "get all"
    synonyms = ["take"]
    syntax = [
        ["get", "all"],
        ["take", "all"],
        ["get", "everything"],
        ["take", "everything"],
    ]
    dscope = "room"
    keywords = ["all", "everything"]

    def verbFunc(self, game):
        """
        Take all obvious invItems in the current room
        """
        super().verbFunc(game)

        loc = game.me.getOutermostLocation()
        items_found = []
        for key in loc.contains:
            for item in loc.contains[key]:
                if item.invItem and item.known_ix in game.me.knows_about:
                    items_found.append(item)
        for key in loc.sub_contains:
            for item in loc.sub_contains[key]:
                if item.invItem and item.known_ix in game.me.knows_about:
                    items_found.append(item)
        items_already = 0
        for item in items_found:
            if game.me.containsItem(item):
                items_already += 1
            else:
                GetVerb().verbFunc(game, item)

        if len(items_found) == items_already:
            game.addTextToEvent("turn", "There are no obvious items here to take. ")


# REMOVE FROM
# move to top inventory level - used by parser for implicit actions
class RemoveFromVerb(IndirectObjectVerb):
    word = "remove"
    syntax = [["remove", "<dobj>", "from", "<iobj>"]]
    dscope = "near"
    preposition = ["from"]

    def _revealUnderSpace(self, game, item):
        if not item.contains:
            return
        msg, plural = item.moveContentsOut()
        if plural:
            msg = msg.capitalize() + " are revealed. "
        else:
            msg = msg.capitalize() + " is revealed. "
        game.addTextToEvent("turn", msg)

    def verbFunc(self, game, dobj, iobj, skip=True):
        """Remove a Thing from a Thing
        Mostly intended for implicit use within the inventory """
        prep = iobj.contains_preposition or "in"
        if dobj == game.me:
            game.addTextToEvent("turn", "You cannot take yourself. ")
            return False
        if dobj.location != iobj:
            game.addTextToEvent(
                "turn",
                f"{dobj.capNameArticle(True)} is not {prep} {iobj.lowNameArticle(True)}. ",
            )
            return False
        if iobj == game.me:
            game.addTextToEvent(
                "turn", f"You are currently holding {dobj.lowNameArticle(True)}. "
            )
            return True
        if isinstance(iobj, Container) and iobj.has_lid and not iobj.is_open:
            game.addTextToEvent(
                "turn", f"(First trying to open {iobj.lowNameArticle(True)})"
            )
            success = OpenVerb().verbFunc(game, iobj)
            if not success:
                return False
        if not dobj.invItem:
            game.addTextToEvent("turn", dobj.cannotTakeMsg)
            return False
        if dobj.containsItem(game.me):
            game.addTextToEvent(
                "turn",
                f"You are currently {dobj.contains_preposition} "
                f"{dobj.lowNameArticle(True)}, and therefore cannot take it. ",
            )
            return False
        game.addTextToEvent(
            "turn",
            f"You remove {dobj.lowNameArticle(True)} from {iobj.lowNameArticle(True)}. ",
        )
        if isinstance(dobj, UnderSpace):
            self._revealUnderSpace(game, dobj)
        if dobj.is_composite:
            for item in dobj.child_UnderSpaces:
                self._revealUnderSpace(game, item)

        iobj.removeThing(dobj)
        game.me.addThing(dobj)

        return True


# DROP
# transitive verb, no indirect object
class DropVerb(DirectObjectVerb):
    word = "drop"
    synonyms = ["put"]
    syntax = [
        ["drop", "<dobj>"],
        ["put", "down", "<dobj>"],
        ["put", "<dobj>", "down"],
    ]
    dscope = "inv"
    preposition = ["down"]
    allow_implicit_take = False

    def verbFunc(self, game, dobj, skip=False):
        """
        Drop a Thing from the contains
        """
        super().verbFunc(game, dobj, skip=skip)

        if isinstance(dobj, Liquid):
            container = dobj.getContainer()
            if container:
                dobj = container

        if not game.me.containsItem(dobj):
            game.addTextToEvent(
                "turn",
                "You are not holding "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
            return False

        if dobj.parent_obj:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " is attached to "
                + dobj.parent_obj.getArticle(True)
                + dobj.parent_obj.verbose_name
                + ". ",
            )
            return False

        game.me.removeThing(dobj)
        game.addTextToEvent(
            "turn", "You drop " + dobj.getArticle(True) + dobj.verbose_name + ". "
        )
        dobj.location = game.me.location
        dobj.location.addThing(dobj)
        return True


# DROP ALL
# intransitive verb
class DropAllVerb(Verb):
    word = "drop"
    syntax = [["drop", "all"], ["drop", "everything"]]
    dscope = "room"
    keywords = ["all", "everything"]

    def verbFunc(self, game):
        """
        Drop everything in the inventory
        """
        inv = [item for key, sublist in game.me.contains.items() for item in sublist]
        dropped = 0

        for item in inv:
            if game.me.containsItem(item):
                part = DropVerb()
                part.verbFunc(game, item)
                dropped = dropped + 1
        if dropped == 0:
            game.addTextToEvent("turn", "Your inventory is empty. ")


# PUT/SET ON
# transitive verb with indirect object
class SetOnVerb(IndirectObjectVerb):
    word = "set"
    list_word = "set on"
    synonyms = ["put", "drop", "place"]
    syntax = [
        ["put", "<dobj>", "on", "<iobj>"],
        ["set", "<dobj>", "on", "<iobj>"],
        ["place", "<dobj>", "on", "<iobj>"],
        ["drop", "<dobj>", "on", "<iobj>"],
    ]
    dscope = "inv"
    itype = "Surface"
    iscope = "room"
    preposition = ["on"]

    def verbFunc(self, game, dobj, iobj, skip=False):
        """
        Put a Thing on a Surface
        """
        if dobj == iobj:
            game.addTextToEvent("turn", "You cannot set something on itself. ")
            return False

        super().verbFunc(game, dobj, iobj, skip=skip)

        if not iobj.playerAboutToAddItem(dobj, "on", event="turn"):
            return False

        return iobj.playerAddsItem(
            dobj,
            "on",
            event="turn",
            success_msg=f"You set {dobj.lowNameArticle(True)} on {iobj.lowNameArticle(True)}.",
        )


# PUT/SET IN
# transitive verb with indirect object
class SetInVerb(IndirectObjectVerb):
    word = "set"
    list_word = "set in"
    synonyms = ["put", "insert", "place", "drop"]
    syntax = [
        ["put", "<dobj>", "in", "<iobj>"],
        ["set", "<dobj>", "in", "<iobj>"],
        ["insert", "<dobj>", "into", "<iobj>"],
        ["place", "<dobj>", "in", "<iobj>"],
        ["drop", "<dobj>", "in", "<iobj>"],
    ]
    dscope = "inv"
    itype = "Container"
    iscope = "near"
    preposition = ["in"]

    def verbFunc(self, game, dobj, iobj, skip=False):
        """
        Put a Thing in a Container
        """
        if iobj == dobj:
            game.addTextToEvent("turn", "You cannot set something in itself. ")
            return False

        super().verbFunc(game, dobj, iobj, skip=skip)

        if not iobj.playerAboutToAddItem(dobj, "in", event="turn"):
            return False

        return iobj.playerAddsItem(
            dobj,
            "in",
            event="turn",
            success_msg=f"You set {dobj.lowNameArticle(True)} in {iobj.lowNameArticle(True)}.",
        )


# PUT/SET UNDER
# transitive verb with indirect object
class SetUnderVerb(IndirectObjectVerb):
    word = "set"
    list_word = "set under"
    synonyms = ["put", "place"]
    syntax = [
        ["put", "<dobj>", "under", "<iobj>"],
        ["set", "<dobj>", "under", "<iobj>"],
        ["place", "<dobj>", "under", "<iobj>"],
    ]
    dscope = "inv"
    iscope = "room"
    itype = "UnderSpace"
    preposition = ["under"]

    def verbFunc(self, game, dobj, iobj, skip=False):
        """
        Put a Thing under an UnderSpace
        """
        if iobj == dobj:
            game.addTextToEvent("turn", "You cannot set something under itself. ")
            return False

        super().verbFunc(game, dobj, iobj, skip=skip)

        if not iobj.playerAboutToAddItem(dobj, "under", event="turn"):
            return False

        return iobj.playerAddsItem(
            dobj,
            "under",
            event="turn",
            success_msg=f"You set {dobj.lowNameArticle(True)} in {iobj.lowNameArticle(True)}.",
        )


# VIEW INVENTORY
# intransitive verb
class InvVerb(Verb):
    word = "inventory"
    synonyms = ["i"]
    syntax = [["inventory"], ["i"]]

    allow_in_sequence = True

    def verbFunc(self, game):
        """View the player's contains
         """
        # describe contains
        if game.me.contains == {}:
            game.addTextToEvent("turn", "You don't have anything with you. ")
        else:
            # the string to print listing the contains
            invdesc = "You have "
            list_version = list(game.me.contains.keys())
            remove_child = []
            for key in list_version:
                for thing in game.me.contains[key]:
                    if thing.parent_obj:
                        # list_version.remove(key)
                        remove_child.append(key)
            for key in remove_child:
                if key in list_version:
                    list_version.remove(key)
            for key in list_version:
                if len(game.me.contains[key]) > 1:
                    # fix for containers?
                    invdesc = (
                        invdesc
                        + str(len(game.me.contains[key]))
                        + " "
                        + game.me.contains[key][0].plural
                    )
                else:
                    invdesc = (
                        invdesc
                        + game.me.contains[key][0].getArticle()
                        + game.me.contains[key][0].verbose_name
                    )
                # if the Thing contains Things, list them
                contents_desc = game.me.contains[key][0].contains_desc.lower().strip()
                if contents_desc:
                    invdesc = invdesc + " (" + contents_desc + ")"
                # add appropriate punctuation and "and"
                if key is list_version[-1]:
                    invdesc = invdesc + ". "
                else:
                    invdesc = invdesc + ", "
                if len(list_version) > 1:
                    if key is list_version[-2]:
                        invdesc = invdesc + " and "
            game.addTextToEvent("turn", invdesc)
        # describe clothing
        if game.me.wearing != {}:
            # the string to print listing clothing
            weardesc = "You are wearing "
            list_version = list(game.me.wearing.keys())
            for key in list_version:
                if len(game.me.wearing[key]) > 1:
                    weardesc = (
                        weardesc
                        + str(len(game.me.wearing[key]))
                        + " "
                        + game.me.wearing[key][0].plural
                    )
                else:
                    weardesc = (
                        weardesc
                        + game.me.wearing[key][0].getArticle()
                        + game.me.wearing[key][0].verbose_name
                    )
                # add appropriate punctuation and "and"
                if key is list_version[-1]:
                    weardesc = weardesc + ". "
                elif key is list_version[-2]:
                    weardesc = weardesc + " and "
                else:
                    weardesc = weardesc + ", "
            game.addTextToEvent("turn", weardesc)


# VIEW SCORE
# intransitive verb
class ScoreVerb(Verb):
    word = "score"
    syntax = [["score"]]

    allow_in_sequence = True

    def verbFunc(self, game):
        """
        View the current score
        """

        game.score.score(game)


# VIEW FULL SCORE
# intransitive verb
class FullScoreVerb(Verb):
    word = "fullscore"
    synonyms = ["full"]
    syntax = [["fullscore"], ["full", "score"]]

    allow_in_sequence = True

    def verbFunc(self, game):
        """View the current score
         """
        game.score.fullscore(game)


# VIEW ABOUT
# intransitive verb
class AboutVerb(Verb):
    word = "about"
    syntax = [["about"]]

    def verbFunc(self, game):
        """View the current score
         """
        game.aboutGame.printAbout(game)


# VIEW HELP
# intransitive verb
class HelpVerb(Verb):
    word = "help"
    syntax = [["help"]]

    def verbFunc(self, game):
        game.aboutGame.printHelp(game)


# VIEW Instructions
# intransitive verb
class InstructionsVerb(Verb):
    word = "instructions"
    syntax = [["instructions"]]

    def verbFunc(self, game):
        """View the current score
         """
        game.aboutGame.printInstructions(game)


# VIEW VERB LIST
# intransitive verb
class VerbsVerb(Verb):
    word = "verbs"
    syntax = [["verbs"]]

    def verbFunc(self, game):
        game.aboutGame.printVerbs(game)


# HELP VERB (Verb)
# transitive verb
class HelpVerbVerb(DirectObjectVerb):
    word = "verb"
    list_word = "verb help"
    syntax = [["verb", "help", "<dobj>"]]
    hasStrDobj = True
    dtype = "String"

    def verbFunc(self, game, dobj):
        """View the current score
         """

        game.addTextToEvent("turn", "<b>Verb Help: " + " ".join(dobj) + "</b>")
        if dobj[0] in game.verbs:
            game.addTextToEvent(
                "turn",
                'I found the following sentence structures for the verb "'
                + dobj[0]
                + '":',
            )
            for verb in game.verbs[dobj[0]]:
                for form in verb.syntax:
                    out = list(form)
                    if "<dobj>" in form:
                        ix = form.index("<dobj>")
                        if verb.dtype == "Actor":
                            out[ix] = "(person)"
                        elif verb.dscope == "direction":
                            out[ix] = "(direction)"
                        elif verb.dscope == "text":
                            out[ix] = "(word or number)"
                        else:
                            out[ix] = "(thing)"
                    if "<iobj>" in form:
                        ix = form.index("<iobj>")
                        if verb.itype == "Actor":
                            out[ix] = "(person)"
                        elif verb.iscope == "direction":
                            out[ix] = "(direction)"
                        elif verb.iscope == "text":
                            out[ix] = "(word or number)"
                        else:
                            out[ix] = "(thing)"
                    out = " ".join(out)
                    game.addTextToEvent("turn", out)
        else:
            game.addTextToEvent(
                "turn",
                'I found no verb corresponding to the input "' + " ".join(dobj) + '". ',
            )


# VIEW HINT
# intransitive verb
class HintVerb(Verb):
    word = "hint"
    syntax = [["hint"]]

    def verbFunc(self, game):
        """View the current score
         """
        if game.hints.cur_node:
            if len(game.hints.cur_node.hints) > 0:
                game.hints.cur_node.nextHint(game)
                return True
        game.addTextToEvent("turn", "There are no hints currently available. ")
        return False


# LOOK (general)
# intransitive verb
class LookVerb(Verb):
    word = "look"
    synonyms = ["l"]
    syntax = [["look"], ["l"]]

    def verbFunc(self, game):
        """Look around the current room
         """
        # print location description
        loc = game.me.getOutermostLocation()
        loc.describe(game)
        return True


# EXAMINE (specific)
# transitive verb, no indirect object
class ExamineVerb(DirectObjectVerb):
    word = "examine"
    synonyms = ["x", "look"]
    syntax = [
        ["examine", "<dobj>"],
        ["x", "<dobj>"],
        ["look", "at", "<dobj>"],
        ["look", "on", "<dobj>"],
        ["look", "<dobj>"],
    ]
    dscope = "near"
    preposition = ["at"]
    far_dobj = True

    def verbFunc(self, game, dobj, skip=False):
        """Examine a Thing """
        # print the target's xdesc (examine descripion)
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        game.addTextToEvent("turn", dobj.xdesc)
        return True


# LOOK THROUGH
# transitive verb, no indirect object
class LookThroughVerb(DirectObjectVerb):
    word = "look"
    syntax = [["look", "through", "<dobj>"], ["look", "out", "<dobj>"]]
    dscope = "near"
    preposition = ["through", "out"]
    dtype = "Transparent"
    main_func_name = "playerLooksThrough"
    failure_msg = "You cannot look through the {dobj.verbose_name}. "


# LOOK IN
# transitive verb, no indirect object
class LookInVerb(DirectObjectVerb):
    word = "look"
    list_word = "look in"
    syntax = [["look", "in", "<dobj>"]]
    dscope = "near"
    dtype = "Container"
    preposition = ["in"]
    main_func_name = "playerLooksIn"
    pre_func_name = "playerAboutToLookIn"
    failure_msg = "You cannot look inside the {dobj.verbose_name}. "


# LOOK UNDER
# transitive verb, no indirect object
class LookUnderVerb(DirectObjectVerb):
    word = "look"
    list_word = "look under"
    syntax = [["look", "under", "<dobj>"]]
    dscope = "near"
    dtype = "UnderSpace"
    preposition = ["under"]
    main_func_name = "playerLooksUnder"


# READ
# transitive verb, no indirect object
class ReadVerb(DirectObjectVerb):
    word = "read"
    syntax = [["read", "<dobj>"]]
    hasDobj = True
    dscope = "near"
    dtype = "Readable"
    main_func_name = "playerReads"
    pre_func_name = "playerAboutToRead"
    failure_msg = "There's nothing written there. "


# TALK TO (Actor)
# transitive verb with indirect object
# implicit direct object enabled
class TalkToVerb(DirectObjectVerb):
    word = "talk"
    list_word = "talk to"
    synonyms = ["greet", "say", "hi", "hello"]
    syntax = [
        ["talk", "to", "<dobj>"],
        ["talk", "with", "<dobj>"],
        ["talk", "<dobj>"],
        ["greet", "<dobj>"],
        ["hi", "<dobj>"],
        ["hello", "<dobj>"],
        ["say", "hi", "<dobj>"],
        ["say", "hi", "to", "<dobj>"],
        ["say", "hello", "<dobj>"],
        ["say", "hello", "to", "<dobj>"],
    ]
    impDobj = True
    preposition = ["to", "with"]
    dtype = "Actor"
    main_func_name = "playerTalksTo"
    failure_msg = "You cannot talk to that. "

    def getImpDobj(self, game):
        """If no dobj is specified, try to guess the Actor
         """
        from .grammar import GrammarObject

        people = Verb.disambiguateActor(
            game,
            "There's no one obvious here to talk to. ",
            "Would you like to talk to ",
        )

        if len(people) == 0:
            return None

        elif len(people) == 1:
            game.parser.previous_command.dobj = GrammarObject(target=people[0])
            return people[0]

        game.parser.command.things = people
        game.parser.command.ambiguous = True
        return None


# ASK (Actor)
# transitive verb with indirect object
# implicit direct object enabled
class AskVerb(IndirectObjectVerb):
    word = "ask"
    list_word = "ask about"
    syntax = [["ask", "<dobj>", "about", "<iobj>"]]
    iscope = "knows"
    impDobj = True
    preposition = ["about"]
    dtype = "Actor"
    main_func_name = "playerAsksAbout"
    pre_func_name = "playerAboutToAskAbout"
    failure_msg = "You cannot talk to that. "

    def getImpDobj(self, game):
        return self.getImpTalkTo(game)


# TELL (Actor)
# transitive verb with indirect object
# implicit direct object enabled
class TellVerb(IndirectObjectVerb):
    word = "tell"
    list_word = "tell about"
    syntax = [["tell", "<dobj>", "about", "<iobj>"]]
    iscope = "knows"
    impDobj = True
    preposition = ["about"]
    dtype = "Actor"
    main_func_name = "playerTellsAbout"
    pre_func_name = "playerAboutToTellAbout"
    failure_msg = "You cannot talk to that. "

    def getImpDobj(self, game):
        return self.getImpTalkTo(game)


# GIVE (Actor)
# transitive verb with indirect object
# implicit direct object enabled
class GiveVerb(IndirectObjectVerb):
    word = "give"
    list_word = "give to"
    syntax = [["give", "<iobj>", "to", "<dobj>"], ["give", "<dobj>", "<iobj>"]]
    iscope = "invflex"
    impDobj = True
    preposition = ["to"]
    dtype = "Actor"
    main_func_name = "playerGivesItem"
    pre_func_name = "playerAboutToGiveItem"
    failure_msg = "You cannot talk to that. "

    def getImpDobj(self, game):
        return self.getImpTalkTo(game)


# SHOW (Actor)
# transitive verb with indirect object
# implicit direct object enabled
class ShowVerb(IndirectObjectVerb):
    word = "show"
    list_word = "show to"
    syntax = [["show", "<iobj>", "to", "<dobj>"], ["show", "<dobj>", "<iobj>"]]
    iscope = "invflex"
    impDobj = True
    preposition = ["to"]
    dtype = "Actor"
    main_func_name = "playerShows"
    pre_func_name = "playerAboutToShow"
    failure_msg = "You cannot talk to that. "

    def getImpDobj(self, game):
        return self.getImpTalkTo(game)


# WEAR/PUT ON
# transitive verb, no indirect object
class WearVerb(DirectObjectVerb):
    word = "wear"
    synonyms = ["put", "don"]
    syntax = [
        ["put", "on", "<dobj>"],
        ["put", "<dobj>", "on"],
        ["wear", "<dobj>"],
        ["don", "<dobj>"],
    ]
    dtype = "Clothing"
    dscope = "inv"
    preposition = ["on"]
    main_func_name = "playerWears"
    pre_func_name = "playerAboutToWear"
    failure_msg = "You cannot wear that. "


# TAKE OFF/DOFF
# transitive verb, no indirect object
class DoffVerb(DirectObjectVerb):
    word = "take"
    synonyms = ["doff", "remove"]
    syntax = [
        ["take", "off", "<dobj>"],
        ["take", "<dobj>", "off"],
        ["doff", "<dobj>"],
        ["remove", "<dobj>"],
    ]
    dscope = "wearing"
    preposition = ["off"]
    main_func_name = "playerDoffs"
    pre_func_name = "playerAboutDoff"
    failure_msg = "You cannot doff that. "


# LIE DOWN
# intransitive verb
class LieDownVerb(Verb):
    word = "lie"
    synonyms = ["lay"]
    syntax = [["lie", "down"], ["lay", "down"]]
    preposition = ["down"]

    def verbFunc(self, game):
        if game.me.position == "lying":
            game.addTextToEvent("turn", "You are already lying down. ")
            return True

        climb_out = ClimbOutVerb()

        while (
            isinstance(game.me.location, Thing)
            and not game.me.location.can_contain_lying_player
        ):
            success = climb_out.verbFunc(game)
            if not success:
                game.addText("You can't lie down here. ")
                return False

        game.addTextToEvent("turn", "You lie down. ")
        game.me.makeLying()

        return True


# STAND UP
# intransitive verb
class StandUpVerb(Verb):
    word = "stand"
    synonyms = ["get"]
    syntax = [["stand", "up"], ["stand"], ["get", "up"]]
    preposition = ["up"]

    def verbFunc(self, game):
        if game.me.position != "standing":
            if isinstance(game.me.location, Thing):
                if not game.me.location.can_contain_standing_player:
                    game.addTextToEvent(
                        "turn",
                        "(First getting "
                        + game.me.location.contains_preposition_inverse
                        + " of "
                        + game.me.location.getArticle(True)
                        + game.me.location.verbose_name
                        + ")",
                    )
                    outer_loc = game.me.getOutermostLocation()
                    game.me.location.removeThing(game.me)
                    outer_loc.addThing(game.me)
            game.addTextToEvent("turn", "You stand up. ")
            game.me.makeStanding()
        else:
            game.addTextToEvent("turn", "You are already standing. ")


# SIT DOWN
# intransitive verb
class SitDownVerb(Verb):
    word = "sit"
    syntax = [["sit", "down"], ["sit"]]
    preposition = ["down"]

    def verbFunc(self, game):
        if game.me.position == "sitting":
            game.addTextToEvent("turn", "You are already sitting. ")
            return True

        climb_out = ClimbOutVerb()

        while (
            isinstance(game.me.location, Thing)
            and not game.me.location.can_contain_sitting_player
        ):
            success = climb_out.verbFunc(game)
            if not success:
                game.addText("You can't sit down here. ")
                return False

        game.addTextToEvent("turn", "You sit down. ")
        game.me.makeSitting()

        return True


# STAND ON (SURFACE)
# transitive verb, no indirect object
class StandOnVerb(DirectObjectVerb):
    word = "stand"
    list_word = "stand on"
    syntax = [["stand", "on", "<dobj>"]]
    dscope = "room"
    dtype = "Surface"
    preposition = ["on"]

    def verbFunc(self, game, dobj, skip=False):
        """
        Stand on a Surface where can_contain_sitting_player is True
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        outer_loc = game.me.getOutermostLocation()
        if dobj == outer_loc.floor:
            if game.me.location == outer_loc and game.me.position == "standing":
                game.addTextToEvent(
                    "turn",
                    "You are already standing on "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + ". ",
                )
            elif game.me.location == outer_loc:
                game.addTextToEvent(
                    "turn",
                    "You stand on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
                )
                game.me.makeStanding()
            else:
                game.me.location.removeThing(game.me)
                outer_loc.addThing(game.me)
                game.addTextToEvent(
                    "turn",
                    "You stand on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
                )
                game.me.makeStanding()
            return True
        if (
            game.me.location == dobj
            and game.me.position == "standing"
            and isinstance(dobj, Surface)
        ):
            game.addTextToEvent(
                "turn",
                "You are already standing on "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
        elif isinstance(dobj, Surface) and dobj.can_contain_standing_player:
            game.addTextToEvent(
                "turn",
                "You stand on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )
            if game.me in game.me.location.contains[game.me.ix]:
                game.me.location.contains[game.me.ix].remove(game.me)
                if game.me.location.contains[game.me.ix] == []:
                    del game.me.location.contains[game.me.ix]
            dobj.addThing(game.me)
            game.me.makeStanding()
        else:
            game.addTextToEvent(
                "turn",
                "You cannot stand on "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
            return False


# SIT ON (SURFACE)
# transitive verb, no indirect object
class SitOnVerb(DirectObjectVerb):
    word = "sit"
    list_word = "sit on"
    syntax = [["sit", "on", "<dobj>"], ["sit", "down", "on", "<dobj>"]]
    hasDobj = True
    dscope = "room"
    dtype = "Surface"
    preposition = ["down", "on"]

    def verbFunc(self, game, dobj, skip=False):
        """
        Sit on a Surface where can_contain_standing_player is True
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        outer_loc = game.me.getOutermostLocation()
        if dobj == outer_loc.floor:
            if game.me.location == outer_loc and game.me.position == "sitting":
                game.addTextToEvent(
                    "turn",
                    "You are already sitting on "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + ". ",
                )
            elif game.me.location == outer_loc:
                game.addTextToEvent(
                    "turn",
                    "You sit on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
                )
                game.me.makeSitting()
            else:
                game.me.location.removeThing(game.me)
                outer_loc.addThing(game.me)
                game.addTextToEvent(
                    "turn",
                    "You sit on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
                )
                game.me.makeSitting()
            return True
        if (
            game.me.location == dobj
            and game.me.position == "sitting"
            and isinstance(dobj, Surface)
        ):
            game.addTextToEvent(
                "turn",
                "You are already sitting on "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
        elif isinstance(dobj, Surface) and dobj.can_contain_sitting_player:
            game.addTextToEvent(
                "turn", "You sit on " + dobj.getArticle(True) + dobj.verbose_name + ". "
            )
            if game.me in game.me.location.contains[game.me.ix]:
                game.me.location.contains[game.me.ix].remove(game.me)
                if game.me.location.contains[game.me.ix] == []:
                    del game.me.location.contains[game.me.ix]
            dobj.addThing(game.me)
            game.me.makeSitting()
        else:
            game.addTextToEvent(
                "turn",
                "You cannot sit on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )


# LIE ON (SURFACE)
# transitive verb, no indirect object
class LieOnVerb(DirectObjectVerb):
    words = "lie"
    list_word = "lie on"
    synonyms = ["lay"]
    syntax = [
        ["lie", "on", "<dobj>"],
        ["lie", "down", "on", "<dobj>"],
        ["lay", "on", "<dobj>"],
        ["lay", "down", "on", "<dobj>"],
    ]
    hasDobj = True
    dscope = "room"
    dtype = "Surface"
    preposition = ["down", "on"]

    def verbFunc(self, game, dobj, skip=False):
        """
        Lie on a Surface where can_contain_lying_player is True
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        outer_loc = game.me.getOutermostLocation()
        if dobj == outer_loc.floor:
            if game.me.location == outer_loc and game.me.position == "lying":
                game.addTextToEvent(
                    "turn",
                    "You are already lying "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + ". ",
                )
            elif game.me.location == outer_loc:
                game.addTextToEvent(
                    "turn",
                    "You lie on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
                )
                game.me.makeLying()
            else:
                game.me.location.removeThing(game.me)
                outer_loc.addThing(game.me)
                game.addTextToEvent(
                    "turn",
                    "You lie on the "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + ". ",
                )
                game.me.makeLying()
            return True
        if (
            game.me.location == dobj
            and game.me.position == "lying"
            and isinstance(dobj, Surface)
        ):
            game.addTextToEvent(
                "turn",
                "You are already lying on "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
        elif isinstance(dobj, Surface) and dobj.can_contain_lying_player:
            game.addTextToEvent(
                "turn", "You lie on " + dobj.getArticle(True) + dobj.verbose_name + ". "
            )
            if game.me in game.me.location.contains[game.me.ix]:
                game.me.location.contains[game.me.ix].remove(game.me)
                if game.me.location.contains[game.me.ix] == []:
                    del game.me.location.contains[game.me.ix]
            dobj.addThing(game.me)
            game.me.makeLying()
            return True
        else:
            game.addTextToEvent(
                "turn",
                "You cannot lie on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )


# SIT IN (CONTAINER)
# transitive verb, no indirect object
class SitInVerb(DirectObjectVerb):
    word = "sit"
    list_word = "sit in"
    syntax = [["sit", "in", "<dobj>"], ["sit", "down", "in", "<dobj>"]]
    dscope = "room"
    dtype = "Container"
    preposition = ["down", "in"]

    # when the Chair subclass of Surface is implemented, redirect to sit on if dobj is a Chair
    def verbFunc(self, game, dobj, skip=False):
        """
        Stand in a Container where can_contain_standing_player is True
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if (
            game.me.location == dobj
            and game.me.position == "sitting"
            and isinstance(dobj, Container)
        ):
            game.addTextToEvent(
                "turn",
                "You are already sitting in "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
            return True
        elif isinstance(dobj, Container) and dobj.can_contain_sitting_player:
            game.addTextToEvent(
                "turn", "You sit in " + dobj.getArticle(True) + dobj.verbose_name + ". "
            )
            if game.me in game.me.location.contains[game.me.ix]:
                game.me.location.contains[game.me.ix].remove(game.me)
                if game.me.location.contains[game.me.ix] == []:
                    del game.me.location.contains[game.me.ix]
            dobj.addThing(game.me)
            game.me.makeSitting()
        else:
            game.addTextToEvent(
                "turn",
                "You cannot sit in " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )
            return False


# STAND IN (CONTAINER)
# transitive verb, no indirect object
class StandInVerb(DirectObjectVerb):
    word = "stand"
    list_word = "stand in"
    syntax = [["stand", "in", "<dobj>"]]
    dscope = "room"
    dtype = "Container"
    preposition = ["in"]

    def verbFunc(self, game, dobj, skip=False):
        """
        Sit on a Surface where can_contain_sitting_player is True
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if (
            game.me.location == dobj
            and game.me.position == "standing"
            and isinstance(dobj, Container)
        ):
            game.addTextToEvent(
                "turn",
                "You are already standing in "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
            return True
        elif isinstance(dobj, Container) and dobj.can_contain_standing_player:
            game.addTextToEvent(
                "turn",
                "You stand in " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )
            if game.me in game.me.location.contains[game.me.ix]:
                game.me.location.contains[game.me.ix].remove(game.me)
                if game.me.location.contains[game.me.ix] == []:
                    del game.me.location.contains[game.me.ix]
            dobj.addThing(game.me)
            game.me.makeStanding()
            return True
        else:
            game.addTextToEvent(
                "turn",
                "You cannot stand in "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
            return False


# LIE IN (CONTAINER)
# transitive verb, no indirect object
class LieInVerb(DirectObjectVerb):
    word = "lie"
    list_word = "lie in"
    synonyms = ["lay"]
    syntax = [
        ["lie", "in", "<dobj>"],
        ["lie", "down", "in", "<dobj>"],
        ["lay", "in", "<dobj>"],
        ["lay", "down", "in", "<dobj>"],
    ]
    dscope = "room"
    dtype = "Container"
    preposition = ["down", "in"]

    def verbFunc(self, game, dobj, skip=False):
        """
        Lie on a Surface where can_contain_lying_player is True
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if (
            game.me.location == dobj
            and game.me.position == "lying"
            and isinstance(dobj, Container)
        ):
            game.addTextToEvent(
                "turn",
                "You are already lying in "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
            return True
        elif isinstance(dobj, Container) and dobj.can_contain_lying_player:
            game.addTextToEvent(
                "turn", "You lie in " + dobj.getArticle(True) + dobj.verbose_name + ". "
            )
            if game.me in game.me.location.contains[game.me.ix]:
                game.me.location.contains[game.me.ix].remove(game.me)
                if game.me.location.contains[game.me.ix] == []:
                    del game.me.location.contains[game.me.ix]
            dobj.addThing(game.me)
            game.me.makeLying()
            return True
        else:
            game.addTextToEvent(
                "turn",
                "You cannot lie in " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )
            return False


# CLIMB ON (SURFACE)
# transitive verb, no indirect object
class ClimbOnVerb(DirectObjectVerb):
    word = "climb"
    list_word = "climb on"
    synonyms = ["get"]
    syntax = [
        ["climb", "on", "<dobj>"],
        ["get", "on", "<dobj>"],
        ["climb", "<dobj>"],
        ["climb", "up", "<dobj>"],
    ]
    dscope = "room"
    dtype = "Surface"
    dobj_direction = "u"
    preposition = ["on", "up"]

    def verbFunc(self, game, dobj, skip=False):
        """
        Climb on a Surface where one of more of can_contain_standing_player/
        can_contain_sitting_player/can_contain_lying_player is True
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if dobj.connection:
            if dobj.direction == "u":
                dobj.connection.travel(game)
            else:
                game.addTextToEvent("turn", "You can't climb up that. ")
                return False
        elif isinstance(dobj, Surface) and dobj.can_contain_standing_player:
            redirect = StandOnVerb()
            redirect.verbFunc(game, dobj)
            return True
        elif isinstance(dobj, Surface) and dobj.can_contain_sitting_player:
            redirect = SitOnVerb()
            redirect.verbFunc(game, dobj)
            return True
        elif isinstance(dobj, Surface) and dobj.can_contain_lying_player:
            redirect = LieOnVerb()
            redirect.verbFunc(game, dobj)
            return True

        game.addTextToEvent(
            "turn",
            "You cannot climb on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
        )
        return False


# CLIMB UP (INTRANSITIVE)
# intransitive verb
class ClimbUpVerb(Verb):
    word = "climb"
    syntax = [["climb", "up"], ["climb"]]
    preposition = ["up"]

    def verbFunc(self, game, skip=False):
        """
        Climb up to the room above
        """
        from .travel import travelU

        cur_loc = game.me.getOutermostLocation()
        if cur_loc.up:
            travelU(game)
        else:
            game.addTextToEvent("turn", "You cannot climb up from here. ")


# CLIMB DOWN (INTRANSITIVE)
# intransitive verb
class ClimbDownVerb(Verb):
    word = "climb"
    list_word = "climb down"
    synonyms = ["get"]
    syntax = [
        ["climb", "off"],
        ["get", "off"],
        ["climb", "down"],
        ["get", "down"],
    ]
    preposition = ["off", "down"]

    def verbFunc(self, game, skip=False):
        """
        Climb down from a Surface you currently occupy
        """
        from .travel import travelD

        cur_loc = game.me.getOutermostLocation()
        if cur_loc.down:
            travelD(game)
        elif isinstance(game.me.location, Surface):
            game.addTextToEvent(
                "turn",
                "You climb down from "
                + game.me.location.getArticle(True)
                + game.me.location.verbose_name
                + ". ",
            )
            outer_loc = game.me.location.location
            game.me.location.removeThing(game.me)
            outer_loc.addThing(game.me)
        else:
            game.addTextToEvent("turn", "You cannot climb down from here. ")


# CLIMB DOWN FROM (SURFACE)
# transitive verb, no indirect object
class ClimbDownFromVerb(DirectObjectVerb):
    word = "climb"
    list_word = "climb down from"
    synonyms = ["get"]
    syntax = [
        ["climb", "off", "<dobj>"],
        ["get", "off", "<dobj>"],
        ["climb", "down", "from", "<dobj>"],
        ["get", "down", "from", "<dobj>"],
        ["climb", "down", "<dobj>"],
    ]
    dscope = "room"
    preposition = ["off", "down", "from"]
    dobj_direction = "d"

    def verbFunc(self, game, dobj, skip=False):
        """
        Climb down from a Surface you currently occupy
        Will be extended once stairs/ladders/up direction/down direction are implemented
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if dobj.connection:
            if dobj.direction == "d":
                dobj.connection.travel(game)
                return True
            else:
                game.addTextToEvent("turn", "You can't climb down from that. ")
                return False
        elif game.me.location == dobj:
            if isinstance(game.me.location, Surface):
                game.addTextToEvent(
                    "turn",
                    "You climb down from "
                    + game.me.location.getArticle(True)
                    + game.me.location.verbose_name
                    + ". ",
                )
                outer_loc = game.me.location.location
                game.me.location.removeThing(game.me)
                outer_loc.addThing(game.me)
            else:
                game.addTextToEvent("turn", "You cannot climb down from here. ")
                return False
        else:
            game.addTextToEvent(
                "turn",
                "You are not on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )
            return False


# GO THROUGH (CONNECTOR INTERACTABLE not derived from AbstractClimbable)
# transitive
class GoThroughVerb(DirectObjectVerb):
    word = "go"
    list_word = "go through"
    syntax = [["go", "through", "<dobj>"]]
    dscope = "room"
    preposition = ["through"]

    def verbFunc(self, game, dobj, skip=False):
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, AbstractClimbable):
            game.addTextToEvent(
                "turn", "You cannot go through " + dobj.lowNameArticle(True) + ". "
            )
            return False
        elif dobj.connection:
            return dobj.connection.travel(game)
        else:
            game.addTextToEvent(
                "turn", "You cannot go through " + dobj.lowNameArticle(True) + ". "
            )
            return False


# CLIMB IN (CONTAINER)
# transitive verb, no indirect object
class ClimbInVerb(DirectObjectVerb):
    word = "climb"
    list_word = "climb in"
    synonyms = ["get", "enter", "go"]
    syntax = [
        ["climb", "in", "<dobj>"],
        ["get", "in", "<dobj>"],
        ["climb", "into", "<dobj>"],
        ["get", "into", "<dobj>"],
        ["enter", "<dobj>"],
        ["go", "in", "<dobj>"],
        ["go", "into", "<dobj>"],
    ]
    dscope = "room"
    preposition = ["in", "into"]

    def verbFunc(self, game, dobj, skip=False):
        """Climb in a Container where one of more of can_contain_standing_player/can_contain_sitting_player/can_contain_lying_player is True
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if dobj.connection:
            dobj.connection.travel(game)
            return True

        if isinstance(dobj, Container):
            if dobj.has_lid and not dobj.is_open:
                game.addTextToEvent(
                    "turn",
                    "You cannot climb into "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + ", since it is closed. ",
                )
                return False

            if dobj.can_contain_standing_player:
                redirect = StandInVerb()
                return redirect.verbFunc(game, dobj)

            elif dobj.can_contain_sitting_player:
                redirect = SitInVerb()
                return redirect.verbFunc(game, dobj)

            elif dobj.can_contain_lying_player:
                redirect = LieInVerb()
                return redirect.verbFunc(game, dobj)

        game.addTextToEvent(
            "turn",
            "You cannot climb into " + dobj.getArticle(True) + dobj.verbose_name + ". ",
        )
        return False


# CLIMB OUT (INTRANSITIVE)
# intransitive verb
class ClimbOutVerb(Verb):
    word = "climb"
    list_word = "climb out"
    synonyms = ["get"]
    syntax = [["climb", "out"], ["get", "out"]]
    preposition = ["out"]

    def verbFunc(self, game, skip=True):
        """
        Climb out of a Container you currently occupy
        """
        ret = super().verbFunc(game, skip=skip)
        if ret is not None:
            return ret

        if isinstance(game.me.location, Container) or isinstance(game.me, UnderSpace):
            game.addTextToEvent(
                "turn",
                "You climb out of "
                + game.me.location.getArticle(True)
                + game.me.location.verbose_name
                + ". ",
            )
            outer_loc = game.me.location.location
            game.me.location.removeThing(game.me)
            outer_loc.addThing(game.me)
            return True
        else:
            game.addTextToEvent("turn", "You cannot climb out of here. ")


# CLIMB OUT OF (CONTAINER)
# transitive verb, no indirect object
class ClimbOutOfVerb(DirectObjectVerb):
    word = "climb"
    list_word = "climb out of"
    synonyms = ["get", "exit"]
    syntax = [
        ["climb", "out", "of", "<dobj>"],
        ["get", "out", "of", "<dobj>"],
        ["exit", "<dobj>"],
    ]
    dscope = "room"
    preposition = ["out", "of"]

    def verbFunc(self, game, dobj, skip=False):
        """
        Climb down from a Surface you currently occupy
        Will be extended once stairs/ladders/up direction/down direction are implemented
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if game.me.location == dobj:
            if isinstance(game.me.location, Container) or isinstance(
                game.me, UnderSpace
            ):
                game.addTextToEvent(
                    "turn",
                    "You climb out of "
                    + game.me.location.getArticle(True)
                    + game.me.location.verbose_name
                    + ". ",
                )
                game.me.moveTo(dobj.location)
                return True
            else:
                game.addTextToEvent("turn", "You cannot climb out of here. ")
                return False
        else:
            game.addTextToEvent(
                "turn",
                "You are not in " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )
            return False


# OPEN
# transitive verb, no indirect object
class OpenVerb(DirectObjectVerb):
    word = "open"
    syntax = [["open", "<dobj>"]]
    dscope = "near"

    def verbFunc(self, game, dobj, skip=False):
        """
        Open a Thing with an is_open attribute
        """
        try:
            lock = dobj.lock_obj
        except:
            lock = None
        if lock:
            if dobj.lock_obj.is_locked:
                try:
                    game.addTextToEvent("turn", dobj.cannotOpenLockedMsg)
                except:
                    game.addTextToEvent(
                        "turn",
                        (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                        + " is locked. ",
                    )
                return False

        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        try:
            state = dobj.is_open
        except AttributeError:
            game.addTextToEvent(
                "turn",
                "You cannot open " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )
            return False
        if state == False:
            game.addTextToEvent(
                "turn", "You open " + dobj.getArticle(True) + dobj.verbose_name + ". "
            )
            dobj.makeOpen()
            if isinstance(dobj, Container):
                after = LookInVerb()
                after.verbFunc(game, dobj)
            return True

        else:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " is already open. ",
            )
        return True


# CLOSE
# transitive verb, no indirect object
class CloseVerb(DirectObjectVerb):
    word = "close"
    synonyms = ["shut"]
    syntax = [["close", "<dobj>"], ["shut", "<dobj>"]]
    dscope = "near"

    def verbFunc(self, game, dobj, skip=False):
        """
        Open a Thing with an open property
        """

        if isinstance(dobj, Container):
            if dobj.has_lid:
                if game.me.ix in dobj.contains or game.me.ix in dobj.sub_contains:
                    game.addTextToEvent(
                        "turn",
                        "You cannot close "
                        + dobj.getArticle(True)
                        + dobj.verbose_name
                        + " while you are inside it. ",
                    )
                    return False

        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        try:
            state = dobj.is_open
        except AttributeError:
            game.addTextToEvent(
                "turn",
                "You cannot close " + dobj.getArticle(True) + dobj.verbose_name + ". ",
            )
            return False
        if state == True:
            game.addTextToEvent(
                "turn", "You close " + dobj.getArticle(True) + dobj.verbose_name + ". "
            )
            dobj.makeClosed()
            return True
        else:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " is already closed. ",
            )
        return True


# EXIT (INTRANSITIVE)
# intransitive verb
class ExitVerb(Verb):
    word = "exit"
    syntax = [["exit"]]

    def verbFunc(self, game):
        """Climb out of a Container you currently occupy
         """
        from .travel import travelOut

        out_loc = game.me.getOutermostLocation()
        if isinstance(game.me.location, Container) or isinstance(game.me, UnderSpace):
            ClimbOutOfVerb().verbFunc(game, game.me.location)
        if isinstance(game.me.location, Surface):
            ClimbDownFromVerb().verbFunc(game, game.me.location)
        elif out_loc.exit:
            travelOut(game)
        else:
            game.addTextToEvent("turn", "There is no obvious exit. ")


# ENTER (INTRANSITIVE)
# intransitive verb
class EnterVerb(Verb):
    word = "enter"
    syntax = [["enter"]]

    def verbFunc(self, game):
        from .travel import travelIn

        out_loc = game.me.getOutermostLocation()
        if out_loc.entrance:
            travelIn(game)
        else:
            game.addTextToEvent("turn", "There is no obvious entrance. ")


# UNLOCK
# transitive verb, no indirect object
# TODO(#126): clean up logic in verbFunc
class UnlockVerb(DirectObjectVerb):
    word = "unlock"
    synonyms = ["unbolt"]
    syntax = [["unlock", "<dobj>"], ["unbolt", "<dobj>"]]
    dscope = "near"

    def verbFunc(self, game, dobj, skip=False):
        """
        Unlock a Door or Container with an lock
        Returns True when the function ends with dobj unlocked, or without a lock.
        Returns False on failure to unlock.
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, Container) or isinstance(dobj, Door):
            if dobj.lock_obj:
                if dobj.lock_obj.is_locked:
                    if dobj.lock_obj.key_obj:
                        if game.me.containsItem(dobj.lock_obj.key_obj):
                            game.addTextToEvent(
                                "turn",
                                "(Using "
                                + dobj.lock_obj.key_obj.getArticle(True)
                                + dobj.lock_obj.key_obj.verbose_name
                                + ")",
                            )
                            if dobj.lock_obj.key_obj.location != game.me:
                                game.addTextToEvent(
                                    "turn",
                                    "(First removing "
                                    + dobj.lock_obj.key_obj.lowNameArticle(True)
                                    + " from "
                                    + dobj.lock_obj.key_obj.location.lowNameArticle(
                                        True
                                    )
                                    + ".)",
                                )
                                # dobj.lock_obj.key_obj.location.removeThing(dobj.lock_obj.key_obj)
                                # game.me.addThing(dobj.lock_obj.key_obj)
                                before = RemoveFromVerb()
                                before.verbFunc(
                                    game.me,
                                    game.app,
                                    dobj.lock_obj.key_obj,
                                    dobj.lock_obj.key_obj.location,
                                )
                            game.addTextToEvent(
                                "turn",
                                "You unlock "
                                + dobj.getArticle(True)
                                + dobj.verbose_name
                                + ". ",
                            )
                            dobj.lock_obj.makeUnlocked()
                            return True
                        else:
                            game.addTextToEvent(
                                "turn", "You do not have the correct key. "
                            )
                            return False
                    else:
                        game.addTextToEvent("turn", "You do not have the correct key. ")
                        return False
                else:
                    game.addTextToEvent(
                        "turn",
                        (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                        + " is already unlocked. ",
                    )
                    return True
            else:
                game.addTextToEvent(
                    "turn",
                    (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                    + " does not have a lock. ",
                )
                return True
        elif isinstance(dobj, Lock):
            if dobj.is_locked:
                if dobj.key_obj:
                    if game.me.containsItem(dobj.key_obj):
                        game.addTextToEvent(
                            "turn",
                            "(Using "
                            + dobj.key_obj.getArticle(True)
                            + dobj.key_obj.verbose_name
                            + ")",
                        )
                        if dobj.key_obj.location != game.me:
                            game.addTextToEvent(
                                "turn",
                                "(First removing "
                                + dobj.key_obj.lowNameArticle(True)
                                + " from "
                                + dobj.key_obj.location.lowNameArticle(True)
                                + ".)",
                            )
                            # dobj.key_obj.location.removeThing(dobj.key_obj)
                            # game.me.addThing(dobj.key_obj)
                            before = RemoveFromVerb()
                            before.verbFunc(game, dobj.key_obj, dobj.key_obj.location)
                        game.addTextToEvent(
                            "turn",
                            "You unlock "
                            + dobj.getArticle(True)
                            + dobj.verbose_name
                            + ". ",
                        )
                        dobj.makeUnlocked()
                        return True
                    else:
                        game.addTextToEvent("turn", "You do not have the correct key. ")
                        return False
                else:
                    game.addTextToEvent("turn", "You do not have the correct key. ")
                    return False
            else:
                game.addTextToEvent(
                    "turn",
                    (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                    + " is already unlocked. ",
                )
                return True
        else:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " does not have a lock. ",
            )
            return True


# LOCK
# TODO(#126): clean up logic in verbFunc
# transitive verb, no indirect object
class LockVerb(DirectObjectVerb):
    word = "lock"
    synonyms = ["bolt"]
    syntax = [["lock", "<dobj>"], ["bolt", "<dobj>"]]
    dscope = "near"

    def verbFunc(self, game, dobj, skip=False):
        """
        Lock a Door or Container with an lock
        Returns True when the function ends with dobj locked.
        Returns False on failure to lock, or when dobj has no lock.
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, Container) or isinstance(dobj, Door):
            if dobj.is_open:
                if not CloseVerb().verbFunc(game, dobj):
                    game.addTextToEvent(
                        "turn", "Could not close " + dobj.verbose_name + ". "
                    )
                    return False
            if dobj.lock_obj:
                if not dobj.lock_obj.is_locked:
                    if dobj.lock_obj.key_obj:
                        if game.me.containsItem(dobj.lock_obj.key_obj):
                            game.addTextToEvent(
                                "turn",
                                "(Using "
                                + dobj.lock_obj.key_obj.getArticle(True)
                                + dobj.lock_obj.key_obj.verbose_name
                                + ")",
                            )
                            if dobj.lock_obj.key_obj.location != game.me:
                                game.addTextToEvent(
                                    "turn",
                                    "(First removing "
                                    + dobj.lock_obj.key_obj.lowNameArticle(True)
                                    + " from "
                                    + dobj.lock_obj.key_obj.location.lowNameArticle(
                                        True
                                    )
                                    + ".)",
                                )
                                # dobj.lock_obj.key_obj.location.removeThing(dobj.lock_obj.key_obj)
                                # game.me.addThing(dobj.lock_obj.key_obj)
                                before = RemoveFromVerb()
                                before.verbFunc(
                                    game.me,
                                    game.app,
                                    dobj.lock_obj.key_obj,
                                    dobj.lock_obj.key_obj.location,
                                )
                            game.addTextToEvent(
                                "turn",
                                "You lock "
                                + dobj.getArticle(True)
                                + dobj.verbose_name
                                + ". ",
                            )
                            dobj.lock_obj.makeLocked()
                            return True
                        else:
                            game.addTextToEvent(
                                "turn", "You do not have the correct key. "
                            )
                            return False
                    else:
                        game.addTextToEvent("turn", "You do not have the correct key. ")
                        return False
                else:
                    game.addTextToEvent(
                        "turn",
                        (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                        + " is already locked. ",
                    )
                    return True
            else:
                game.addTextToEvent(
                    "turn",
                    (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                    + " does not have a lock. ",
                )
                return False
        elif isinstance(dobj, Lock):
            if dobj.parent_obj.is_open:
                if not verbFunc(self, game, dobj.parent_obj):
                    game.addTextToEvent(
                        "turn", "Could not close " + dobj.parent_obj.verbose_name + ". "
                    )
                    return False
            if not dobj.is_locked:
                if dobj.key_obj:
                    if game.me.containsItem(dobj.key_obj):
                        game.addTextToEvent(
                            "turn",
                            "(Using "
                            + dobj.key_obj.getArticle(True)
                            + dobj.key_obj.verbose_name
                            + ")",
                        )
                        if dobj.key_obj.location != game.me:
                            game.addTextToEvent(
                                "turn",
                                "(First removing "
                                + dobj.key_obj.lowNameArticle(True)
                                + " from "
                                + dobj.key_obj.location.lowNameArticle(True)
                                + ".)",
                            )
                            # dobj.key_obj.location.removeThing(dobj.key_obj)
                            # game.me.addThing(dobj.key_obj)
                            before = RemoveFromVerb()
                            before.verbFunc(game, dobj.key_obj, dobj.key_obj.location)
                        game.addTextToEvent(
                            "turn",
                            "You lock "
                            + dobj.getArticle(True)
                            + dobj.verbose_name
                            + ". ",
                        )
                        dobj.makeLocked()
                        return True
                    else:
                        game.addTextToEvent("turn", "You do not have the correct key. ")
                        return False
                else:
                    game.addTextToEvent("turn", "You do not have the correct key. ")
                    return False
            else:
                game.addTextToEvent(
                    "turn",
                    (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                    + " is already locked. ",
                )
                return True
        else:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " does not have a lock. ",
            )
            return True


# UNLOCK WITH
# TODO(#126): clean up logic in verbFunc
# transitive verb with indirect object
class UnlockWithVerb(IndirectObjectVerb):
    word = "unlock"
    synonyms = ["unbolt", "open"]
    syntax = [
        ["unlock", "<dobj>", "using", "<iobj>"],
        ["unlock", "<dobj>", "with", "<iobj>"],
        ["unbolt", "<dobj>", "with", "<iobj>"],
        ["unbolt", "<dobj>", "using", "<iobj>"],
        ["open", "<dobj>", "using", "<iobj>"],
        ["open", "<dobj>", "with", "<iobj>"],
    ]
    preposition = ["with", "using"]
    dscope = "near"
    iscope = "invflex"

    def verbFunc(self, game, dobj, iobj, skip=False):
        """
        Unlock a Door or Container with an lock
        Returns True when the function ends with dobj unlocked, or without a lock.
        Returns False on failure to unlock.
        """
        ret = super().verbFunc(game, dobj, iobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, Container) or isinstance(dobj, Door):
            if dobj.lock_obj:
                if dobj.lock_obj.is_locked:
                    if iobj is game.me:
                        game.addTextToEvent("turn", "You are not a key. ")
                        return False
                    elif not isinstance(iobj, Key):
                        game.addTextToEvent(
                            "turn",
                            (iobj.getArticle(True) + iobj.verbose_name).capitalize()
                            + " is not a key. ",
                        )
                        return False
                    elif dobj.lock_obj.key_obj:
                        if iobj == dobj.lock_obj.key_obj:
                            game.addTextToEvent(
                                "turn",
                                "You unlock "
                                + dobj.getArticle(True)
                                + dobj.verbose_name
                                + " using "
                                + dobj.lock_obj.key_obj.getArticle(True)
                                + dobj.lock_obj.key_obj.verbose_name
                                + ". ",
                            )
                            dobj.lock_obj.makeUnlocked()
                            return True
                        else:
                            game.addTextToEvent(
                                "turn", "You do not have the correct key. "
                            )
                            return False
                    else:
                        game.addTextToEvent("turn", "You do not have the correct key. ")
                        return False
                else:
                    game.addTextToEvent(
                        "turn",
                        (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                        + " is already unlocked. ",
                    )
                    return True
            else:
                game.addTextToEvent(
                    "turn",
                    (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                    + " does not have a lock. ",
                )
                return True

        elif isinstance(dobj, Lock):
            if dobj.is_locked:
                if not isinstance(iobj, Key):
                    game.addTextToEvent(
                        "turn",
                        (iobj.getArticle(True) + iobj.verbose_name).capitalize()
                        + " is not a key. ",
                    )
                elif dobj.key_obj:
                    if iobj == dobj.key_obj.ix:
                        game.addTextToEvent(
                            "turn",
                            "You unlock "
                            + dobj.getArticle(True)
                            + dobj.verbose_name
                            + " using "
                            + dobj.lock_obj.key_obj.getArticle(True)
                            + dobj.lock_obj.key_obj.verbose_name
                            + ". ",
                        )
                        dobj.makeUnlocked()
                        return True
                    else:
                        game.addTextToEvent("turn", "You do not have the correct key. ")
                        return False
                else:
                    game.addTextToEvent("turn", "You do not have the correct key. ")
                    return False
            else:
                game.addTextToEvent(
                    "turn",
                    (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                    + " is already unlocked. ",
                )
                return True
        else:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " does not have a lock. ",
            )
            return True


# LOCK WITH
# TODO(#126): clean up logic in verbFunc
# transitive verb with indirect object
class LockWithVerb(IndirectObjectVerb):
    word = "lock"
    synonyms = ["bolt"]
    syntax = [
        ["lock", "<dobj>", "using", "<iobj>"],
        ["lock", "<dobj>", "with", "<iobj>"],
        ["bolt", "<dobj>", "with", "<iobj>"],
        ["bolt", "<dobj>", "using", "<iobj>"],
    ]
    preposition = ["with", "using"]
    dscope = "near"
    iscope = "invflex"

    def verbFunc(self, game, dobj, iobj, skip=False):
        """
        Unlock a Door or Container with a lock
        Returns True when the function ends with dobj unlocked, or without a lock.
        Returns False on failure to unlock.
        """
        ret = super().verbFunc(game, dobj, iobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, Container) or isinstance(dobj, Door):
            if dobj.is_open:
                if not verbFunc(self, game, dobj):
                    game.addTextToEvent(
                        "turn", "Could not close " + dobj.verbose_name + ". "
                    )
                    return False
            if dobj.lock_obj:
                if not dobj.lock_obj.is_locked:
                    if iobj is game.me:
                        game.addTextToEvent("turn", "You are not a key. ")
                        return False
                    elif not isinstance(iobj, Key):
                        game.addTextToEvent(
                            "turn",
                            (iobj.getArticle(True) + iobj.verbose_name).capitalize()
                            + " is not a key. ",
                        )
                        return False
                    elif dobj.lock_obj.key_obj:
                        if iobj == dobj.lock_obj.key_obj:
                            game.addTextToEvent(
                                "turn",
                                "You lock "
                                + dobj.getArticle(True)
                                + dobj.verbose_name
                                + " using "
                                + dobj.lock_obj.key_obj.getArticle(True)
                                + dobj.lock_obj.key_obj.verbose_name
                                + ". ",
                            )
                            dobj.lock_obj.makeLocked()
                            return True
                        else:
                            game.addTextToEvent(
                                "turn", "You do not have the correct key. "
                            )
                            return False
                    else:
                        game.addTextToEvent("turn", "You do not have the correct key. ")
                        return False
                else:
                    game.addTextToEvent(
                        "turn",
                        (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                        + " is already locked. ",
                    )
                    return True
            else:
                game.addTextToEvent(
                    "turn",
                    (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                    + " does not have a lock. ",
                )
                return False

        elif isinstance(dobj, Lock):
            if dobj.parent_obj.is_open:
                if not verbFunc(self, game, dobj.parent_obj):
                    game.addTextToEvent(
                        "turn", "Could not close " + dobj.parent_obj.verbose_name + ". "
                    )
                    return False
            if not dobj.is_locked:
                if not isinstance(iobj, Key):
                    game.addTextToEvent(
                        "turn",
                        (iobj.getArticle(True) + iobj.verbose_name).capitalize()
                        + " is not a key. ",
                    )
                elif dobj.key_obj:
                    if iobj == dobj.key_obj.ix:
                        game.addTextToEvent(
                            "turn",
                            "You lock "
                            + dobj.getArticle(True)
                            + dobj.verbose_name
                            + " using "
                            + dobj.lock_obj.key_obj.getArticle(True)
                            + dobj.lock_obj.key_obj.verbose_name
                            + ". ",
                        )
                        dobj.makeLocked()
                        return True
                    else:
                        game.addTextToEvent("turn", "You do not have the correct key. ")
                        return False
                else:
                    game.addTextToEvent("turn", "You do not have the correct key. ")
                    return False
            else:
                game.addTextToEvent(
                    "turn",
                    (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                    + " is already locked. ",
                )
                return True
        else:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " does not have a lock. ",
            )
            return False


# transitive verb, no indirect object
class GoVerb(DirectObjectVerb):
    word = "go"
    syntax = [["go", "<dobj>"]]
    dscope = "direction"

    def verbFunc(self, game, dobj):
        from .travel import directionDict

        directionDict[dobj]["func"](game)


# LIGHT (LightSource)
# transitive verb, no indirect object
class LightVerb(DirectObjectVerb):
    word = "light"
    syntax = [["light", "<dobj>"]]
    dscope = "near"
    dtype = "LightSource"

    def verbFunc(self, game, dobj, skip=False):
        """Light a LightSource """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, LightSource):
            if dobj.player_can_light:
                light = dobj.light(game)
                if light:
                    game.addTextToEvent("turn", dobj.light_msg)
                return light
            else:
                game.addTextToEvent("turn", dobj.cannot_light_msg)
                return False
        else:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " is not a light source. ",
            )
            return False


# EXTINGUISH (LightSource)
# transitive verb, no indirect object
class ExtinguishVerb(DirectObjectVerb):
    word = "extinguish"
    synonyms = ["put"]
    syntax = [
        ["extinguish", "<dobj>"],
        ["put", "out", "<dobj>"],
        ["put", "<dobj>", "out"],
    ]
    dscope = "near"
    dtype = "LightSource"
    preposition = ["out"]

    def verbFunc(self, game, dobj, skip=False):
        """Extinguish a LightSource """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, LightSource):
            if dobj.player_can_extinguish:
                extinguish = dobj.extinguish(game)
                if extinguish:
                    game.addTextToEvent("turn", dobj.extinguish_msg)
                return extinguish
            else:
                game.addTextToEvent("turn", dobj.cannot_extinguish_msg)
                return False
        else:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " is not a light source. ",
            )
            return False


# WAIT A TURN
# intransitive verb
class WaitVerb(Verb):
    word = "wait"
    synonyms = ["z"]
    syntax = [["wait"], ["z"]]

    def verbFunc(self, game):
        """Wait a turn
         """
        game.addTextToEvent("turn", "You wait a turn. ")
        return True


# USE (THING)
# transitive verb, no indirect object
class UseVerb(DirectObjectVerb):
    word = "use"
    syntax = [["use", "<dobj>"]]
    dscope = "near"

    def verbFunc(self, game, dobj, skip=False):
        """
        Use a Thing
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, LightSource):
            redirect = LightVerb()
            return redirect(game, dobj)

        elif isinstance(dobj, Key):
            game.addTextToEvent(
                "turn",
                "What would you like to unlock with " + dobj.lowNameArticle(True) + "?",
            )
            game.parser.command.verb = unlockWithVerb()
            game.parser.command.ambiguous = True

        elif isinstance(dobj, Transparent):
            redirect = LookThroughVerb()
            return redirect.verbFunc(game, dobj)

        elif dobj.connection:
            dobj.connection.travel(game)

        elif isinstance(dobj, Actor):
            game.addTextToEvent("turn", "You cannot use people. ")
            return False
        else:
            game.addTextToEvent(
                "turn",
                "You'll have to be more specific about what you want to do with "
                + dobj.lowNameArticle(True)
                + ". ",
            )
            return False


# BUY FROM
# transitive verb with indirect object
class BuyFromVerb(IndirectObjectVerb):
    word = "buy"
    list_word = "buy from"
    synonym = ["purchase"]
    syntax = [
        ["buy", "<dobj>", "from", "<iobj>"],
        ["purchase", "<dobj>", "from", "<iobj>"],
    ]
    dscope = "knows"
    iscope = "room"
    itype = "Actor"
    preposition = ["from"]

    def verbFunc(self, game, dobj, iobj, skip=False):
        """
        Buy something from a person
        """
        ret = super().verbFunc(game, dobj, iobj, skip=skip)
        if ret is not None:
            return ret

        if not isinstance(iobj, Actor):
            game.addTextToEvent(
                "turn",
                "You cannot buy anything from " + iobj.lowNameArticle(False) + ". ",
            )
            return False
        elif iobj == game.me:
            game.addTextToEvent("turn", "You cannot buy anything from yourself. ")
            return False
        elif isinstance(dobj, Actor):
            if not dobj.commodity:
                game.addTextToEvent("turn", "You cannot buy or sell a person. ")
                return False
        if dobj.known_ix not in iobj.for_sale:
            game.addTextToEvent(
                "turn",
                iobj.capNameArticle(True)
                + " doesn't sell "
                + dobj.lowNameArticle(False)
                + ". ",
            )
            return False
        elif not iobj.for_sale[dobj.known_ix].number:
            game.addTextToEvent("turn", iobj.for_sale[dobj.known_ix].out_stock_msg)
            return False
        else:
            currency = iobj.for_sale[dobj.known_ix].currency
            currency_ix = currency.ix
            mycurrency = 0
            if currency_ix in game.me.contains:
                mycurrency = mycurrency + len(game.me.contains[currency_ix])
            if currency_ix in game.me.sub_contains:
                mycurrency = mycurrency + len(game.me.sub_contains[currency_ix])
            if mycurrency < iobj.for_sale[dobj.known_ix].price:
                game.addTextToEvent(
                    "turn",
                    "You don't have enough "
                    + currency.plural
                    + " to purchase "
                    + dobj.lowNameArticle(False)
                    + ". <br> (requires "
                    + str(iobj.for_sale[dobj.known_ix].price)
                    + ") ",
                )
                return False
            else:
                game.addTextToEvent("turn", iobj.for_sale[dobj.known_ix].purchase_msg)
                iobj.for_sale[dobj.known_ix].beforeBuy(game)
                iobj.for_sale[dobj.known_ix].buyUnit(game)
                iobj.for_sale[dobj.known_ix].afterBuy(game)
                if not iobj.for_sale[dobj.known_ix].number:
                    iobj.for_sale[dobj.known_ix].soldOut(game)
                return True


# BUY
# transitive verb
class BuyVerb(DirectObjectVerb):
    word = "buy"
    synonyms = ["purchase"]
    syntax = [["buy", "<dobj>"], ["purchase", "<dobj>"]]
    dscope = "knows"

    def verbFunc(self, game, dobj):
        """
        Redirect to buy from
        """
        people = Verb.disambiguateActor(
            game,
            "There's no one obvious here to buy from. ",
            "Would you like to buy from ",
        )
        if len(people) > 1:
            game.parser.command.verb = BuyFromVerb
            game.parser.command.things = people
            game.parser.command.ambiguous = True
            return False

        elif len(people) == 0:
            return False

        redirect = BuyFromVerb()

        return redirect.verbFunc(game, dobj, people[0])


# SELL TO
# transitive verb with indirect object
class SellToVerb(IndirectObjectVerb):
    word = "sell"
    list_word = "sell to"
    syntax = [["sell", "<dobj>", "to", "<iobj>"]]
    dscope = "invflex"
    iscope = "room"
    itype = "Actor"
    preposition = ["to"]

    def verbFunc(self, game, dobj, iobj, skip=False):
        """
        Sell something to a person
        """
        ret = super().verbFunc(game, dobj, iobj, skip=skip)
        if ret is not None:
            return ret

        if not isinstance(iobj, Actor):
            game.addTextToEvent(
                "turn",
                "You cannot sell anything to " + iobj.lowNameArticle(False) + ". ",
            )
            return False
        elif iobj == game.me:
            game.addTextToEvent("turn", "You cannot sell anything to yourself. ")
            return False
        if dobj.ix not in iobj.will_buy:
            if dobj is game.me:
                game.addTextToEvent("turn", "You cannot sell yourself. ")
                return False
            game.addTextToEvent(
                "turn",
                iobj.capNameArticle(True)
                + " doesn't want to buy "
                + dobj.lowNameArticle(True)
                + ". ",
            )
            return False
        elif not iobj.will_buy[dobj.known_ix].number:
            game.addTextToEvent(
                "turn",
                iobj.capNameArticle(True)
                + " will not buy any more "
                + dobj.plural
                + ". ",
            )
            return False
        else:
            game.addTextToEvent("turn", iobj.will_buy[dobj.known_ix].sell_msg)
            iobj.will_buy[dobj.known_ix].beforeSell(game)
            iobj.will_buy[dobj.known_ix].sellUnit(game)
            iobj.will_buy[dobj.known_ix].afterSell(game)
            if not iobj.will_buy[dobj.known_ix].number:
                iobj.will_buy[dobj.known_ix].boughtAll(game)
            return True


# SELL
# transitive verb
class SellVerb(DirectObjectVerb):
    word = "sell"
    syntax = [["sell", "<dobj>"]]
    dscope = "invflex"

    def verbFunc(self, game, dobj, skip=False):
        """
        Redrirect to sell to
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        people = Verb.disambiguateActor(
            game,
            "There's no one obvious here to sell to. ",
            "Would you like to sell it to ",
        )

        if len(people) == 1:
            # ask the only actor in the room
            iobj = people[0]
            redirect = SellToVerb()
            return redirect.verbFunc(game, dobj, iobj)

        if len(people) > 1:
            game.parser.command.things = people
            game.parser.command.ambiguous = True

        return False


# RECORD ON
# intransitive verb
class RecordOnVerb(Verb):
    word = "record"
    list_word = "record on"
    synonyms = ["recording"]
    syntax = [["record", "on"], ["recording", "on"]]
    preposition = ["on"]

    def verbFunc(self, game):
        f = game.app.saveFilePrompt(".txt", "Text files", "Enter a file to record to")
        success = game.recordOn(f)
        if success:
            game.addTextToEvent("turn", "**RECORDING ON**")
        else:
            game.addTextToEvent("turn", "Could not open file for recording.")
        return success


# RECORD OFF
# intransitive verb
class RecordOffVerb(Verb):
    word = "record"
    list_word = "record off"
    synonyms = ["recording"]
    syntax = [["record", "off"], ["recording", "off"]]
    preposition = ["off"]

    def verbFunc(self, game):
        game.recordOff()
        game.addTextToEvent("turn", "**RECORDING OFF**")


# RECORD OFF
# intransitive verb
class PlayBackVerb(Verb):
    word = "playback"
    syntax = [["playback"]]

    def verbFunc(self, game):
        f = game.app.openFilePrompt(
            ".txt", "Text files", "Enter a filename for the new recording"
        )
        if not f:
            game.addTextToEvent("turn", "No file selected. ")
            return False
        with open(f, "r") as play:
            lines = play.readlines()
            game.addTextToEvent("turn", "**STARTING PLAYBACK** ")
            game.runTurnEvents()
            for line in lines:
                game.turnMain(line[:-1])

        game.addTextToEvent("turn", "**PLAYBACK COMPLETE** ")
        game.parser.command = game.parser.previous_command
        return True


# LEAD (person) (direction)
# transitive verb with indirect object
class LeadDirVerb(IndirectObjectVerb):
    word = "lead"
    syntax = [["lead", "<dobj>", "<iobj>"]]
    iscope = "direction"
    dscope = "room"
    dtype = "Actor"

    def verbFunc(self, game, dobj, iobj, skip=False):
        """
        Lead an Actor in a direction
        """
        from .travel import TravelConnector

        ret = super().verbFunc(game, dobj, iobj, skip=skip)
        if ret is not None:
            return ret

        if not isinstance(dobj, Actor):
            game.addTextToEvent("turn", "You cannot lead that. ")
            return False
        elif dobj.can_be_led:
            from .travel import getDirectionFromString, directionDict

            destination = getDirectionFromString(dobj.getOutermostLocation(), iobj)
            if not destination:
                game.addTextToEvent(
                    "turn",
                    "You cannot lead " + dobj.lowNameArticle(True) + " that way. ",
                )
                return False
            if isinstance(destination, TravelConnector):
                if not destination.can_pass:
                    game.addTextToEvent("turn", destination.cannot_pass_msg)
                    return False
                elif dobj.getOutermostLocation() == destination.pointA:
                    destination = destination.pointB
                else:
                    destination = destination.pointA
            dobj.location.removeThing(dobj)
            destination.addThing(dobj)
            directionDict[iobj]["func"](game)
        else:
            game.addTextToEvent(
                "turn", dobj.capNameArticle(True) + " doesn't want to be led. "
            )


# SAVE
class SaveVerb(Verb):
    word = "save"
    syntax = [["save"]]

    allow_in_sequence = True

    def verbFunc(self, game):
        f = game.app.saveFilePrompt(".sav", "Save files", "Enter a file to save to")

        if f:
            SaveGame(game, f)
            game.addTextToEvent("turn", "Game saved.")
            return True
        game.addTextToEvent("turn", "Could not save game.")
        return False


# LOAD
class LoadVerb(Verb):
    word = "load"
    syntax = [["load"]]

    allow_in_sequence = True

    def verbFunc(self, game):
        f = game.app.openFilePrompt(".sav", "Save files", "Enter a file to load")

        if not f:
            game.addTextToEvent("turn", "Choose a valid save file to load a game.")
            return False

        try:
            l = LoadGame(game, f)
        except FileNotFoundError:
            game.addTextToEvent("turn", f"File {f} does not exist.")
            return False

        if not l.is_valid():
            game.addTextToEvent("turn", "Cannot load game file.")
            return False

        l.load()
        game.addTextToEvent("turn", "Game loaded.")
        return True


# BREAK
# transitive verb, no indirect object
class BreakVerb(DirectObjectVerb):
    word = "break"
    syntax = [["break", "<dobj>"]]
    dscope = "near"

    def verbFunc(self, game, dobj, skip=False):
        """break a Thing """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        game.addTextToEvent("turn", "Violence isn't the answer to this one. ")


# KICK
# transitive verb, no indirect object
class KickVerb(DirectObjectVerb):
    word = "kick"
    syntax = [["kick", "<dobj>"]]
    dscope = "near"

    def verbFunc(self, game, dobj, skip=False):
        """kick a Thing """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        game.addTextToEvent("turn", "Violence isn't the answer to this one. ")


# KILL
# transitive verb, no indirect object
class KillVerb(DirectObjectVerb):
    word = "kill"
    syntax = [["kill", "<dobj>"]]
    dscope = "near"

    def verbFunc(self, game, dobj, skip=False):
        """kill a Thing """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, Actor):
            game.addTextToEvent("turn", "Violence isn't the answer to this one. ")
        else:
            game.addTextToEvent(
                "turn",
                dobj.capNameArticle(True) + " cannot be killed, as it is not alive. ",
            )


# JUMP
# intransitive verb
class JumpVerb(Verb):
    word = "jump"
    syntax = [["jump"]]

    def verbFunc(self, game):
        """
        Jump in place
        """
        game.addTextToEvent("turn", "You jump in place. ")


# JUMP OVER
# transitive verb
class JumpOverVerb(DirectObjectVerb):
    word = "jump"
    syntax = [["jump", "over", "<dobj>"], ["jump", "across", "<dobj>"]]
    preposition = ["over", "across"]
    dscope = "room"

    def verbFunc(self, game, dobj, skip=False):
        """
        Jump over a Thing
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if dobj == game.me:
            game.addTextToEvent("turn", "You cannot jump over yourself. ")
        elif dobj.size < 70:
            game.addTextToEvent("turn", "There's no reason to jump over that. ")
        else:
            game.addTextToEvent(
                "turn", dobj.capNameArticle(True) + " is too big to jump over. "
            )
        return False


# JUMP IN
# transitive verb
class JumpInVerb(DirectObjectVerb):
    word = "jump"
    syntax = [["jump", "in", "<dobj>"], ["jump", "into", "<dobj>"]]
    preposition = ["in", "into"]
    dscope = "room"

    def verbFunc(self, game, dobj, skip=False):
        """
        Jump in a Thing
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        game.addTextToEvent("turn", "You cannot jump into that. ")
        return False


# JUMP ON
# transitive verb
class JumpOnVerb(DirectObjectVerb):
    word = "jump"
    syntax = [["jump", "on", "<dobj>"], ["jump", "onto", "<dobj>"]]
    preposition = ["on", "onto"]
    dscope = "room"

    def verbFunc(self, game, dobj, skip=False):
        """
        Jump on a Thing
        """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        game.addTextToEvent("turn", "You cannot jump onto that. ")
        return False


# PRESS
# transitive verb, no indirect object
class PressVerb(DirectObjectVerb):
    word = "press"
    synonyms = ["depress"]
    syntax = [
        ["press", "<dobj>"],
        ["depress", "<dobj>"],
        ["press", "on", "<dobj>"],
    ]
    dscope = "near"
    preposition = ["on"]
    dtype = "Pressable"

    def verbFunc(self, game, dobj, skip=False):
        """press a Thing """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, Pressable):
            game.addTextToEvent("turn", "You press " + dobj.lowNameArticle(True) + ". ")
            dobj.pressThing(game)
        else:
            game.addTextToEvent(
                "turn", "Pressing " + dobj.lowNameArticle(True) + " has no effect. "
            )
            return False


# PUSH
# transitive verb, no indirect object
class PushVerb(DirectObjectVerb):
    word = "push"
    syntax = [["push", "<dobj>"], ["push", "on", "<dobj>"]]
    dscope = "near"
    preposition = ["on"]

    def verbFunc(self, game, dobj, skip=False):
        """push a Thing """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, Pressable):
            redirect = PressVerb()
            redirect.verbFunc(game, dobj)
        else:
            game.addTextToEvent(
                "turn",
                "You push on " + dobj.lowNameArticle(True) + ", to no productive end. ",
            )
            return False


# POUR OUT
# transitive verb, no indirect object
class PourOutVerb(DirectObjectVerb):
    word = "pour"
    synonyms = ["dump"]
    syntax = [
        ["pour", "<dobj>"],
        ["pour", "out", "<dobj>"],
        ["pour", "<dobj>", "out"],
        ["dump", "<dobj>"],
        ["dump", "out", "<dobj>"],
        ["dump", "<dobj>", "out"],
    ]
    dscope = "invflex"
    preposition = ["out"]

    def verbFunc(self, game, dobj, skip=False):
        """Pour a Liquid out of a Container """
        ret = super().verbFunc(game, dobj, skip=skip)
        if ret is not None:
            return ret

        if isinstance(dobj, Container):
            loc = game.me.getOutermostLocation()
            if dobj.has_lid:
                if not dobj.is_open:
                    game.addTextToEvent(
                        "turn", dobj.capNameArticle(True) + " is closed. "
                    )
                    return False
            if dobj.contains == {}:
                game.addTextToEvent("turn", dobj.capNameArticle(True) + " is empty. ")
                return True
            liquid = dobj.containsLiquid()
            if not liquid:
                game.addTextToEvent(
                    "turn",
                    "You dump the contents of "
                    + dobj.lowNameArticle(True)
                    + " onto the ground. ",
                )
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
        if isinstance(dobj, Liquid):
            if not dobj.getContainer():
                game.addTextToEvent(
                    "turn", "It isn't in a container you can dump it from. "
                )
                return False
            elif not dobj.can_pour_out:
                game.addTextToEvent("turn", dobj.cannot_pour_out_msg)
                return False
            game.addTextToEvent(
                "turn", "You dump out " + dobj.lowNameArticle(True) + ". "
            )
            dobj.dumpLiquid()
            return True
        game.addTextToEvent("turn", "You can't dump that out. ")
        return False


# DRINK
# transitive verb, no indirect object
class DrinkVerb(Verb):
    word = "drink"
    syntax = [
        ["drink", "<dobj>"],
        ["drink", "from", "<dobj>"],
        ["drink", "out", "of", "<dobj>"],
    ]
    dscope = "invflex"
    preposition = ["out", "from"]
    keywords = ["of"]

    def verbFunc(self, game, dobj, skip=False):
        """Drink a Liquid """

        if isinstance(dobj, Container):
            loc = game.me.getOutermostLocation()
            if dobj.has_lid:
                if not dobj.is_open:
                    game.addTextToEvent(
                        "turn", dobj.capNameArticle(True) + " is closed. "
                    )
                    return False
            if dobj.contains == {}:
                game.addTextToEvent("turn", dobj.capNameArticle(True) + " is empty. ")
                return True
            liquid = dobj.containsLiquid()
            if not liquid:
                game.addTextToEvent(
                    "turn",
                    "There is nothing you can drink in "
                    + dobj.lowNameArticle(True)
                    + ". ",
                )
                return False
            else:
                dobj = liquid
        if isinstance(dobj, Liquid):
            container = dobj.getContainer()
            if not dobj.can_drink:
                game.addTextToEvent("turn", dobj.cannot_drink_msg)
                return False
            game.addTextToEvent("turn", "You drink " + dobj.lowNameArticle(True) + ". ")
            dobj.drinkLiquid(game)
            return True
        game.addTextToEvent("turn", "You cannot drink that. ")
        return False


# POUR INTO
# transitive verb, with indirect object
class PourIntoVerb(IndirectObjectVerb):
    word = "pour"
    synonyms = ["dump"]
    syntax = [
        ["pour", "<dobj>", "into", "<iobj>"],
        ["pour", "<dobj>", "in", "<iobj>"],
        ["dump", "<dobj>", "into", "<iobj>"],
        ["dump", "<dobj>", "in", "<iobj>"],
    ]
    dscope = "invflex"
    iscope = "near"
    preposition = ["in", "into"]

    success_msg = "You dump the {dobj.verbose_name} {iobj.contains_preposition} the {iobj.verbose_name}. "

    def verbFunc(self, game, dobj, iobj, skip=False):
        """Pour a Liquid from one Container to another """
        ret = super().verbFunc(game, dobj, iobj, skip=skip)
        if ret is not None:
            return ret

        return dobj.playerDumpsItems(
            into_location=iobj,
            success_msg=self.success_msg.format(dobj=dobj, iobj=iobj),
        )


# FILL FROM
# transitive verb, with indirect object
class FillFromVerb(IndirectObjectVerb):
    word = "fill"
    syntax = [
        ["fill", "<dobj>", "from", "<iobj>"],
        ["fill", "<dobj>", "in", "<iobj>"],
        ["fill", "<dobj>", "with", "<iobj>"],
    ]
    dscope = "invflex"
    iscope = "near"
    preposition = ["from", "in", "with"]

    def verbFunc(self, game, dobj, iobj, skip=False):
        """Pour a Liquid from one Container to another """
        ret = super().verbFunc(game, dobj, iobj, skip=skip)
        if ret is not None:
            return ret

        liquid = None
        container = None
        if isinstance(iobj, Container):
            container = iobj
            liquid = iobj.containsLiquid()
        elif isinstance(iobj, Liquid):
            container = iobj.getContainer()
            liquid = iobj
        if not liquid:
            if iobj is game.me:
                game.addTextToEvent("turn", "You cannot fill anything from yourself. ")
            else:
                game.addTextToEvent(
                    "turn", "There is no liquid in " + iobj.lowNameArticle(True) + ". ",
                )
            return False

        if not isinstance(dobj, Container):
            game.addTextToEvent("turn", "You can't fill that. ")
            return False

            loc = game.me.getOutermostLocation()

        if not liquid.can_fill_from:
            game.addTextToEvent("turn", liquid.cannot_fill_from_msg)
            return False

        if container.has_lid and not iobj.is_open:
            game.addTextToEvent("turn", container.capNameArticle(True) + " is closed. ")
            return False

        if dobj.has_lid and not iobj.is_open:
            game.addTextToEvent("turn", dobj.capNameArticle(True) + " is closed. ")
            return False

        if not dobj.holds_liquid:
            game.addTextToEvent(
                "turn", dobj.capNameArticle(True) + " cannot hold a liquid. "
            )
            return False

        spaceleft = dobj.liquidRoomLeft()

        liquid_contents = dobj.containsLiquid()

        if dobj.contains != {} and not liquid_contents:
            game.addTextToEvent(
                "turn", "(First attempting to empty " + dobj.lowNameArticle(True) + ")",
            )
            success = PourOutVerb().verbFunc(game, dobj)

            if not success:
                return False

        if liquid_contents and liquid_contents.liquid_type == liquid.liquid_type:
            game.addTextToEvent(
                "turn",
                f"There is already {liquid_contents.liquid_type} in "
                f"{dobj.lowNameArticle(True)}. ",
            )
            return False

        elif liquid_contents:
            success = liquid_contents.mixWith(game, liquid_contents, liquid)
            if not success:
                game.addTextToEvent(
                    "turn",
                    "There is already "
                    + liquid_contents.lowNameArticle()
                    + " in "
                    + dobj.lowNameArticle(True)
                    + ". ",
                )
                return False
            else:
                return True

        if liquid.infinite_well:
            game.addTextToEvent(
                "turn",
                "You fill "
                + dobj.lowNameArticle(True)
                + " with "
                + liquid.lowNameArticle()
                + " from "
                + iobj.lowNameArticle(True)
                + ". ",
            )
        else:
            game.addTextToEvent(
                "turn",
                "You fill "
                + dobj.lowNameArticle(True)
                + " with "
                + liquid.lowNameArticle()
                + ", taking all of it. ",
            )
        return liquid.fillVessel(dobj)


def get_base_verbset():
    verbs = [
        v
        for v in (
            Verb.__subclasses__()
            + DirectObjectVerb.__subclasses__()
            + IndirectObjectVerb.__subclasses__()
        )
        if v.word
    ]

    verb_map = {}
    for v in verbs:
        for key in [v.word, *v.synonyms]:
            if key in verb_map:
                verb_map[key].append(v)
            else:
                verb_map[key] = [v]
    return verb_map

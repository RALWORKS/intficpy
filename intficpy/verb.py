from .actor import Actor
from .thing_base import Thing
from .things import (
    reflexive,
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
from .score import score, hints
from .vocab import verbDict
from .serializer import SaveGame, LoadGame

##############################################################
# VERB.PY - verbs for IntFicPy
# Defines the Verb class,  and the default verbs
##############################################################
# TODO: sort out circular imports for travel.travel, parser.parser
# currently importing from travel inside functions as a workaround
# move the most common implicit verbs into their own module?


class Verb:
    """Verb objects represent actions the player can take """

    def __init__(self, word, list_word=None, list_by_default=True):
        """Set default properties for the Verb instance
		Takes argument word, a one word verb (string)
		The creator can build constructions like "take off" by specifying prepositions and syntax """
        if word in verbDict:
            verbDict[word].append(self)
        elif word is not None:
            verbDict[word] = [self]

        self.list_word = list_word or word
        self.list_by_default = list_by_default
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
        self.dscope = "room"  # "knows", "near", "room" or "inv"
        self.iscope = "room"
        # not yet implemented in parser
        self.dobj_contains_iobj = False
        self.iobj_contains_dobj = False

    def addSynonym(self, word):
        """Add a synonym verb
			Takes argument word, a single verb (string)
			The creator can build constructions like "take off" by specifying prepositions and syntax """
        if word in verbDict:
            verbDict[word].append(self)
        else:
            verbDict[word] = [self]

    def verbFunc(self, game):
        """The default verb function
		Takes arguments game.me, pointing to the player, game.app, pointing to the GUI game.app, and dobj, the direct object
		Should generally be overwritten by the game creator
		Optionally add arguments dobj and iobj, and set hasDobj and hasIobj appropriately """
        game.addTextToEvent("turn", "You " + self.word + ". ")

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
        game.addTextToEvent("turn", "Error: no implicit direct object defined")

    def getImpIobj(self, game):
        """"Get the implicit indirect object
		The creator should overwrite this if planning to use implicit objects """
        game.addTextToEvent("turn", "Error: no implicit indirect object defined")

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
        people.remove(game.me)
        people = list(filter(lambda item: not item.ignore_if_ambiguous, people))

        if len(people) == 1:
            return people
        if len(people) == 0:
            game.addTextToEvent("turn", len0_msg)
        elif game.lastTurn.dobj in people and isinstance(game.lastTurn.dobj, Actor):
            return [game.lastTurn.dobj]
        elif game.lastTurn.iobj in people and isinstance(game.lastTurn.iobj, Actor):
            return [game.lastTurn.iobj]
        else:
            msg = base_disambig_msg
            for p in people:
                msg = msg + p.lowNameArticle(True)
                if p is people[-1]:
                    msg = msg + "? "
                elif p is people[-2]:
                    msg = msg + " or "
                else:
                    msg = msg + ", "
            game.addTextToEvent("turn", msg)
        return people


# Below are .s built in verbs
###########################################################################

# GET/TAKE
# transitive verb, no indirect object
getVerb = Verb("get")
getVerb.addSynonym("take")
getVerb.addSynonym("pick")
getVerb.syntax = [
    ["get", "<dobj>"],
    ["take", "<dobj>"],
    ["pick", "up", "<dobj>"],
    ["pick", "<dobj>", "up"],
]
getVerb.preposition = ["up"]
# getVerb.dscope = "near"
getVerb.dscope = "roomflex"
getVerb.hasDobj = True


def getVerbFunc(game, dobj, skip=False):
    """Take a Thing from the room
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 application, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.getVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    # first check if dobj can be taken
    while game.me.ix in dobj.sub_contains:
        if isinstance(game.me.location, Container):
            climbOutOfVerb.verbFunc(game, dobj)
        elif isinstance(game.me.location, Surface):
            climbDownFromVerb.verbFunc(game, dobj)
        else:
            game.addTextToEvent(
                "turn", "Could not move player out of " + dobj.verbose_name
            )
            return False
    if game.me.ix in dobj.contains:
        if isinstance(dobj, Container):
            climbOutOfVerb.verbFunc(game, dobj)
        elif isinstance(dobj, Surface):
            climbDownFromVerb.verbFunc(game, dobj)
        else:
            game.addTextToEvent(
                "turn", "Could not move player out of " + dobj.verbose_name
            )
            return False
    if not game.me.position == "standing":
        game.addTextToEvent("turn", "(First standing up)")
        standUpVerb.verbFunc(game)
    if isinstance(dobj, Liquid):
        container = dobj.getContainer()
        if container:
            dobj = container
    if dobj.invItem:
        if game.me.containsItem(dobj):
            if dobj.location == game.me:
                game.addTextToEvent(
                    "turn",
                    "You already have "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + ". ",
                )
                return False
            elif not isinstance(dobj.location, Room):
                return removeFromVerb.verbFunc(game, dobj, dobj.location)
        # print the action message
        game.addTextToEvent(
            "turn", "You take " + dobj.getArticle(True) + dobj.verbose_name + ". "
        )
        if isinstance(dobj, UnderSpace) and not dobj.contains == {}:
            results = dobj.moveContentsOut()
            msg = results[0]
            plural = results[1]
            if plural:
                msg = msg.capitalize() + " are revealed. "
            else:
                msg = msg.capitalize() + " is revealed. "
            game.addTextToEvent("turn", msg)
        if dobj.is_composite:
            for item in dobj.child_UnderSpaces:
                if not item.contains == {}:
                    results = item.moveContentsOut()
                    msg = results[0]
                    plural = results[1]
                    if plural:
                        msg = msg.capitalize() + " are revealed. "
                    else:
                        msg = msg.capitalize() + " is revealed. "
                    game.addTextToEvent("turn", msg)
        while isinstance(dobj.location, Thing):
            old_loc = dobj.location
            if not isinstance(dobj.location, Room):
                dobj.location.removeThing(dobj)
            elif dobj.location.manual_update:
                dobj.location.removeThing(dobj, False, False)
            else:
                dobj.location.removeThing(dobj)
            dobj.location = old_loc.location
            if not isinstance(old_loc, Actor):
                old_loc.containsListUpdate()
        dobj.location.removeThing(dobj)
        game.me.addThing(dobj)
        return True
    elif dobj.parent_obj:
        game.addTextToEvent("turn", dobj.cannotTakeMsg)
        return False
    else:
        # if the dobj can't be taken, print the message
        game.addTextToEvent("turn", dobj.cannotTakeMsg)
        return False


# replace the default verb function
getVerb.verbFunc = getVerbFunc

# GET/TAKE ALL
# intransitive verb
getAllVerb = Verb("get")
getAllVerb.addSynonym("take")
getAllVerb.syntax = [
    ["get", "all"],
    ["take", "all"],
    ["get", "everything"],
    ["take", "everything"],
]
getAllVerb.dscope = "room"
getAllVerb.hasDobj = False
getAllVerb.keywords = ["all", "everything"]


def getAllVerbFunc(game):
    """Take all obvious invItems in the current room
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 application, and dobj, a Thing """
    loc = game.me.getOutermostLocation()
    items_found = []
    for key in loc.contains:
        for item in loc.contains[key]:
            if item.invItem and item.known_ix in game.me.knows_about:
                # getVerb.verbFunc(game, item)
                items_found.append(item)
    for key in loc.sub_contains:
        for item in loc.sub_contains[key]:
            if item.invItem and item.known_ix in game.me.knows_about:
                # getVerb.verbFunc(game, item)
                items_found.append(item)
    items_already = 0
    for item in items_found:
        if item.ix in game.me.contains:
            if not item in game.me.contains[item.ix]:
                getVerb.verbFunc(game, item)
            elif item in game.me.contains[item.ix]:
                items_already = items_already + 1
            elif item.ix in game.me.sub_contains:
                if not item in game.me.sub_contains[item.ix]:
                    getVerb.verbFunc(game, item)
                else:
                    items_already = items_already + 1
        elif item.ix in game.me.sub_contains:
            if not item in game.me.sub_contains[item.ix]:
                getVerb.verbFunc(game, item)
            else:
                items_already = items_already + 1
        else:
            getVerb.verbFunc(game, item)
    if len(items_found) == items_already:
        game.addTextToEvent("turn", "There are no obvious items here to take. ")


# replace the default verb function
getAllVerb.verbFunc = getAllVerbFunc

# REMOVE FROM
# move to top inventory level - used by parser for implicit actions
# transitive verb, indirect object
removeFromVerb = Verb(None, list_by_default=False)
# removeFromVerb.syntax = [["remove", "<dobj>", "from", "<iobj>"]]
removeFromVerb.hasDobj = True
removeFromVerb.hasIobj = True
removeFromVerb.dscope = "near"
removeFromVerb.iscope = "near"
removeFromVerb.iobj_contains_dobj = True
# removeFromVerb.preposition = ["from"]


def removeFromVerbFunc(game, dobj, iobj, skip=True):
    """Remove a Thing from a Thing
	Mostly intended for implicit use within the inventory """
    prep = iobj.contains_preposition or "in"
    if dobj == game.me:
        game.addTextToEvent("turn", "You cannot take yourself. ")
        return False
    elif dobj.location != iobj:
        game.addTextToEvent(
            "turn",
            dobj.capNameArticle(True)
            + " is not "
            + prep
            + " "
            + iobj.lowNameArticle(True),
        )
        return False
    elif iobj == game.me:
        game.addTextToEvent(
            "turn", "You are currently holding " + dobj.lowNameArticle(True) + ". "
        )
        return True
    if isinstance(iobj, Container):
        if not iobj.is_open:
            game.addTextToEvent(
                "turn", "(First trying to open " + iobj.lowNameArticle(True) + ")"
            )
            success = openVerb.verbFunc(game, iobj)
            if not success:
                return False
    if not dobj.invItem:
        print(dobj.cannotTakeMsg)
        return False
    if dobj.parent_obj:
        game.addTextToEvent(
            "turn",
            dobj.capNameArticle(True)
            + " is attached to "
            + dobj.parent_obj.capNameArticle(True),
        )
        return False
    if dobj.containsItem(game):
        game.addTextToEvent(
            "turn",
            "You are currently "
            + dobj.contains_preposition
            + " "
            + dobj.lowNameArticle
            + ", and therefore cannot take it. ",
        )
        return False
    game.addTextToEvent(
        "turn",
        "You remove "
        + dobj.lowNameArticle(True)
        + " from "
        + iobj.lowNameArticle(True)
        + ". ",
    )
    iobj.removeThing(dobj)
    game.me.addThing(dobj)
    if isinstance(dobj, UnderSpace) and not dobj.contains == {}:
        results = dobj.moveContentsOut()
        msg = results[0]
        plural = results[1]
        if plural:
            msg = msg.capitalize() + " are revealed. "
        else:
            msg = msg.capitalize() + " is revealed. "
        game.addTextToEvent("turn", msg)
        if dobj.is_composite:
            for item in dobj.child_UnderSpaces:
                if not item.contains == {}:
                    results = item.moveContentsOut()
                    msg = results[0]
                    plural = results[1]
                    if plural:
                        msg = msg.capitalize() + " are revealed. "
                    else:
                        msg = msg.capitalize() + " is revealed. "
                    game.addTextToEvent("turn", msg)
    return True


removeFromVerb.verbFunc = removeFromVerbFunc

# DROP
# transitive verb, no indirect object
dropVerb = Verb("drop")
dropVerb.addSynonym("put")
dropVerb.syntax = [
    ["drop", "<dobj>"],
    ["put", "down", "<dobj>"],
    ["put", "<dobj>", "down"],
]
dropVerb.hasDobj = True
dropVerb.dscope = "inv"
dropVerb.preposition = ["down"]


def dropVerbFunc(game, dobj, skip=False):
    """Drop a Thing from the contains
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 application, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.dropVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Liquid):
        container = dobj.getContainer()
        if container:
            dobj = container
    if dobj.invItem and game.me.removeThing(dobj):
        game.addTextToEvent(
            "turn", "You drop " + dobj.getArticle(True) + dobj.verbose_name + ". "
        )
        dobj.location = game.me.location
        dobj.location.addThing(dobj)
        return True
    elif dobj.parent_obj:
        game.addTextToEvent(
            "turn",
            (dobj.getArticle(True) + dobj.verbose_name).capitalize()
            + " is attached to "
            + dobj.parent_obj.getArticle(True)
            + dobj.parent_obj.verbose_name
            + ". ",
        )
        return False
    elif not dobj.invItem:
        game.addTextToEvent("turn", "Error: not an inventory item. ")
        print(dobj)
    else:
        game.addTextToEvent(
            "turn",
            "You are not holding " + dobj.getArticle(True) + dobj.verbose_name + ". ",
        )
        return False


# replace the default verbFunc method
dropVerb.verbFunc = dropVerbFunc

# DROP ALL
# intransitive verb
dropAllVerb = Verb("drop")
dropAllVerb.syntax = [["drop", "all"], ["drop", "everything"]]
dropAllVerb.dscope = "room"
dropAllVerb.hasDobj = False
dropAllVerb.keywords = ["all", "everything"]


def dropAllVerbFunc(game):
    """Drop everything in the inventory
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 application, and dobj, a Thing """
    inv = [item for key, sublist in game.me.contains.items() for item in sublist]
    dropped = 0
    for item in inv:
        if game.me.containsItem(item):
            dropVerb.verbFunc(game, item)
            dropped = dropped + 1
    if dropped == 0:
        game.addTextToEvent("turn", "Your inventory is empty. ")


# replace the default verb function
dropAllVerb.verbFunc = dropAllVerbFunc

# PUT/SET ON
# transitive verb with indirect object
setOnVerb = Verb("set", "set on")
setOnVerb.addSynonym("put")
setOnVerb.addSynonym("drop")
setOnVerb.addSynonym("place")
setOnVerb.syntax = [
    ["put", "<dobj>", "on", "<iobj>"],
    ["set", "<dobj>", "on", "<iobj>"],
    ["place", "<dobj>", "on", "<iobj>"],
    ["drop", "<dobj>", "on", "<iobj>"],
]
setOnVerb.hasDobj = True
setOnVerb.dscope = "inv"
setOnVerb.itype = "Surface"
setOnVerb.hasIobj = True
setOnVerb.iscope = "room"
setOnVerb.preposition = ["on"]


def setOnVerbFunc(game, dobj, iobj, skip=False):
    """Put a Thing on a Surface
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """
    if dobj == iobj:
        game.addTextToEvent("turn", "You cannot set something on itself. ")
        return False
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.setOnVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.setOnVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True

    outer_loc = game.me.getOutermostLocation()
    if iobj == outer_loc.floor:
        if game.me.removeThing(dobj):
            game.addTextToEvent(
                "turn",
                "You set "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + " on the ground. ",
            )
            outer_loc.addThing(dobj)
            return True
        elif dobj.parent_obj:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " is attached to "
                + dobj.parent_obj.getArticle(True)
                + dobj.parent_obj.verbose_name
                + ". ",
            )
            return False
        else:
            game.addTextToEvent("turn", "ERROR: cannot remove object from inventory ")
            return False
    if isinstance(iobj, Surface):
        if game.me.removeThing(dobj):
            game.addTextToEvent(
                "turn",
                "You set "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + " on "
                + iobj.getArticle(True)
                + iobj.verbose_name
                + ". ",
            )
            iobj.addThing(dobj)
            return True
        elif dobj.parent_obj:
            game.addTextToEvent(
                "turn",
                (dobj.getArticle(True) + dobj.verbose_name).capitalize()
                + " is attached to "
                + dobj.parent_obj.getArticle(True)
                + dobj.parent_obj.verbose_name
                + ". ",
            )
            return False
        else:
            game.addTextToEvent("turn", "ERROR: cannot remove object from inventory ")
            return False
    # if iobj is not a Surface
    else:
        game.addTextToEvent("turn", "You cannot set anything on that. ")


# replace the default verbFunc method
setOnVerb.verbFunc = setOnVerbFunc

# PUT/SET IN
# transitive verb with indirect object
setInVerb = Verb("set", "set in")
setInVerb.addSynonym("put")
setInVerb.addSynonym("insert")
setInVerb.addSynonym("place")
setInVerb.addSynonym("drop")
setInVerb.syntax = [
    ["put", "<dobj>", "in", "<iobj>"],
    ["set", "<dobj>", "in", "<iobj>"],
    ["insert", "<dobj>", "into", "<iobj>"],
    ["place", "<dobj>", "in", "<iobj>"],
    ["drop", "<dobj>", "in", "<iobj>"],
]
setInVerb.hasDobj = True
setInVerb.dscope = "inv"
setInVerb.itype = "Container"
setInVerb.hasIobj = True
setInVerb.iscope = "near"
setInVerb.preposition = ["in"]


def setInVerbFunc(game, dobj, iobj, skip=False):
    """Put a Thing in a Container
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """
    if iobj == dobj:
        game.addTextToEvent("turn", "You cannot set something in itself. ")
        return False

    if not skip:
        runfunc = True
        try:
            runfunc = dobj.setInVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.setInVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
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
    if isinstance(iobj, Container) and iobj.has_lid:
        if not iobj.is_open:
            game.addTextToEvent(
                "turn",
                "You cannot put "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + " inside, as "
                + iobj.getArticle(True)
                + iobj.verbose_name
                + " is closed. ",
            )
            return False
    if isinstance(iobj, Container) and iobj.size >= dobj.size:
        liquid = iobj.containsLiquid()
        if liquid:
            game.addTextToEvent(
                "turn",
                "You cannot put "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + " inside, as "
                + iobj.getArticle(True)
                + iobj.verbose_name
                + " has "
                + liquid.lowNameArticle()
                + " in it. ",
            )
            return False
        game.addTextToEvent(
            "turn",
            "You set "
            + dobj.getArticle(True)
            + dobj.verbose_name
            + " in "
            + iobj.getArticle(True)
            + iobj.verbose_name
            + ". ",
        )
        # game.me.contains.remove(dobj)
        game.me.removeThing(dobj)
        if iobj.manual_update:
            iobj.addThing(dobj, False, False)
        else:
            iobj.addThing(dobj)
        return True
    elif isinstance(iobj, Container):
        game.addTextToEvent(
            "turn",
            dobj.capNameArticle(True)
            + " is too big to fit inside the "
            + iobj.verbose_name
            + ". ",
        )
        return False
    else:
        game.addTextToEvent(
            "turn", "There is no way to put it inside the " + iobj.verbose_name + ". "
        )
        return False


# replace the default verbFunc method
setInVerb.verbFunc = setInVerbFunc

# PUT/SET UNDER
# transitive verb with indirect object
setUnderVerb = Verb("set", "set under")
setUnderVerb.addSynonym("put")
setUnderVerb.addSynonym("place")
setUnderVerb.syntax = [
    ["put", "<dobj>", "under", "<iobj>"],
    ["set", "<dobj>", "under", "<iobj>"],
    ["place", "<dobj>", "under", "<iobj>"],
]
setUnderVerb.hasDobj = True
setUnderVerb.dscope = "inv"
setUnderVerb.hasIobj = True
setUnderVerb.iscope = "room"
setUnderVerb.itype = "UnderSpace"
setUnderVerb.preposition = ["under"]


def setUnderVerbFunc(game, dobj, iobj, skip=False):
    """Put a Thing under an UnderSpace
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """
    if iobj == dobj:
        game.addTextToEvent("turn", "You cannot set something under itself. ")
        return False

    if not skip:
        runfunc = True
        try:
            runfunc = dobj.setUnderVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.setUnderVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    outer_loc = game.me.getOutermostLocation()
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
    if isinstance(iobj, UnderSpace) and dobj.size <= iobj.size:
        game.addTextToEvent(
            "turn",
            "You set "
            + dobj.getArticle(True)
            + dobj.verbose_name
            + " "
            + iobj.contains_preposition
            + " "
            + iobj.getArticle(True)
            + iobj.verbose_name
            + ". ",
        )
        game.me.removeThing(dobj)
        iobj.addThing(dobj)
        return True
    elif dobj.size > iobj.size:
        game.addTextToEvent(
            "turn",
            (dobj.getArticle(True) + dobj.verbose_name).capitalize()
            + " is too big to fit under "
            + iobj.getArticle(True)
            + iobj.verbose_name
            + ". ",
        )
        return False
    else:
        game.addTextToEvent("turn", "There is no reason to put it under there. ")
        return False


# replace the default verbFunc method
setUnderVerb.verbFunc = setUnderVerbFunc

# VIEW INVENTORY
# intransitive verb
invVerb = Verb("inventory")
invVerb.addSynonym("i")
invVerb.syntax = [["inventory"], ["i"]]
invVerb.hasDobj = False


def invVerbFunc(game):
    """View the player's contains
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
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
                    + game.me.contains[key][0].getPlural()
                )
            else:
                invdesc = (
                    invdesc
                    + game.me.contains[key][0].getArticle()
                    + game.me.contains[key][0].verbose_name
                )
            # if the Thing contains Things, list them
            if game.me.contains[key][0].contains != {}:
                # remove capitalization and terminating period from contains_desc
                c = game.me.contains[key][0].contains_desc.lower()
                if c[0] == " ":
                    c = c[1:-1]
                else:
                    c = c[:-1]
                invdesc = invdesc + " (" + c + ")"
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
                    + game.me.wearing[key][0].getPlural()
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


# replace default verbFunc method
invVerb.verbFunc = invVerbFunc

# VIEW SCORE
# intransitive verb
scoreVerb = Verb("score")
scoreVerb.syntax = [["score"]]
scoreVerb.hasDobj = False


def scoreVerbFunc(game):
    """
    View the current score
    Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app
    """

    score.score(game)


# replace default verbFunc method
scoreVerb.verbFunc = scoreVerbFunc

# VIEW FULL SCORE
# intransitive verb
fullScoreVerb = Verb("fullscore")
fullScoreVerb.addSynonym("full")
fullScoreVerb.syntax = [["fullscore"], ["full", "score"]]
fullScoreVerb.hasDobj = False


def fullScoreVerbFunc(game):
    """View the current score
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """

    score.fullscore(game)


# replace default verbFunc method
fullScoreVerb.verbFunc = fullScoreVerbFunc

# VIEW ABOUT
# intransitive verb
aboutVerb = Verb("about")
aboutVerb.syntax = [["about"]]
aboutVerb.hasDobj = False


def aboutVerbFunc(game):
    """View the current score
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    game.aboutGame.printAbout(game)


# replace default verbFunc method
aboutVerb.verbFunc = aboutVerbFunc

# VIEW HELP
# intransitive verb
helpVerb = Verb("help")
helpVerb.syntax = [["help"]]
helpVerb.hasDobj = False


def helpVerbFunc(game):
    """View the current score
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    game.aboutGame.printHelp(game)


# replace default verbFunc method
helpVerb.verbFunc = helpVerbFunc

# VIEW Instructions
# intransitive verb
instructionsVerb = Verb("instructions")
instructionsVerb.syntax = [["instructions"]]
instructionsVerb.hasDobj = False


def instructionVerbFunc(game):
    """View the current score
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    game.aboutGame.printInstructions(game)


# replace default verbFunc method
instructionsVerb.verbFunc = instructionVerbFunc

# VIEW VERB LIST
# intransitive verb
verbsVerb = Verb("verbs")
verbsVerb.syntax = [["verbs"]]
verbsVerb.hasDobj = False


def verbsVerbFunc(game):
    game.aboutGame.printVerbs(game)


verbsVerb.verbFunc = verbsVerbFunc

# HELP VERB (Verb)
# transitive verb
helpVerbVerb = Verb("verb", "verb help")
helpVerbVerb.syntax = [["verb", "help", "<dobj>"]]
helpVerbVerb.hasDobj = True
helpVerbVerb.hasStrDobj = True
helpVerbVerb.dtype = "String"


def helpVerbVerbFunc(game, dobj):
    """View the current score
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """

    game.addTextToEvent("turn", "<b>Verb Help: " + " ".join(dobj) + "</b>")
    if dobj[0] in verbDict:
        game.addTextToEvent(
            "turn",
            'I found the following sentence structures for the verb "' + dobj[0] + '":',
        )
        for verb in verbDict[dobj[0]]:
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


# replace default verbFunc method
helpVerbVerb.verbFunc = helpVerbVerbFunc

# VIEW HINT
# intransitive verb
hintVerb = Verb("hint")
hintVerb.syntax = [["hint"]]
hintVerb.hasDobj = False


def hintVerbFunc(game):
    """View the current score
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """

    if hints.cur_node:
        if len(hints.cur_node.hints) > 0:
            hints.cur_node.nextHint(game)
            return True
    game.addTextToEvent("turn", "There are no hints currently available. ")
    return False


# replace default verbFunc method
hintVerb.verbFunc = hintVerbFunc

# LOOK (general)
# intransitive verb
lookVerb = Verb("look")
lookVerb.addSynonym("l")
lookVerb.syntax = [["look"], ["l"]]
lookVerb.hasDobj = False


def lookVerbFunc(game):
    """Look around the current room
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    # print location description
    loc = game.me.getOutermostLocation()
    loc.describe(game)
    return True


# replace default verbFunc method
lookVerb.verbFunc = lookVerbFunc

# EXAMINE (specific)
# transitive verb, no indirect object
examineVerb = Verb("examine")
examineVerb.addSynonym("x")
examineVerb.addSynonym("look")
examineVerb.syntax = [
    ["examine", "<dobj>"],
    ["x", "<dobj>"],
    ["look", "at", "<dobj>"],
    ["look", "<dobj>"],
]
examineVerb.hasDobj = True
examineVerb.dscope = "near"
examineVerb.preposition = ["at"]
examineVerb.far_dobj = True


def examineVerbFunc(game, dobj, skip=False):
    """Examine a Thing """
    # print the target's xdesc (examine descripion)
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.examineVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    game.addTextToEvent("turn", dobj.xdesc)
    return True


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


def lookThroughVerbFunc(game, dobj, skip=False):
    """look through a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.lookThroughVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Transparent):
        dobj.lookThrough(game)
        return True
    elif isinstance(dobj, Actor):
        game.addTextToEvent("turn", "You cannot look through a person. ")
        return False
    else:
        game.addTextToEvent(
            "turn", "You cannot look through " + dobj.lowNameArticle(True) + ". "
        )
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


def lookInVerbFunc(game, dobj, skip=False):
    """Look inside a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.lookInVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Container):
        list_version = list(dobj.contains.keys())
        if dobj.has_lid:
            if not dobj.is_open:
                game.addTextToEvent(
                    "turn",
                    "You cannot see inside "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + " as it is closed. ",
                )
                return False
        if len(list_version) > 0:
            game.addTextToEvent("turn", dobj.contains_desc)
            for key in dobj.contains:
                if key not in game.me.knows_about:
                    game.me.knows_about.append(key)
            return True
        else:
            game.addTextToEvent("turn", dobj.capNameArticle(True) + " is empty. ")
            return True
    else:
        game.addTextToEvent(
            "turn",
            "You cannot look inside "
            + dobj.getArticle(True)
            + dobj.verbose_name
            + ". ",
        )
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


def lookUnderVerbFunc(game, dobj, skip=False):
    """Look under a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.lookUnderVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, UnderSpace):
        dobj.revealUnder()
        list_version = list(dobj.contains.keys())
        if len(list_version) > 0:
            game.addTextToEvent("turn", dobj.contains_desc)
            return True
        else:
            game.addTextToEvent(
                "turn",
                "There is nothing "
                + dobj.contains_preposition
                + " "
                + dobj.getArticle(True)
                + dobj.verbose_name
                + ". ",
            )
            return True
    elif dobj.invItem:
        getVerbFunc(game, dobj)
        game.addTextToEvent("turn", "You find nothing underneath. ")
        return False
    else:
        game.addTextToEvent(
            "turn",
            "There's no reason to look under "
            + dobj.getArticle(True)
            + dobj.verbose_name
            + ". ",
        )
        return False


lookUnderVerb.verbFunc = lookUnderVerbFunc

# READ
# transitive verb, no indirect object
readVerb = Verb("read")
readVerb.syntax = [["read", "<dobj>"]]
readVerb.hasDobj = True
readVerb.dscope = "near"
readVerb.dtype = "Readable"


def readVerbFunc(game, dobj, skip=False):
    """look through a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.readVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Book):
        if not dobj.is_open:
            openVerb.verbFunc(game, dobj)
        dobj.readText(game)
    elif isinstance(dobj, Readable):
        dobj.readText(game)
        return True
    else:
        game.addTextToEvent("turn", "There's nothing written there. ")
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
talkToVerb.syntax = [
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
talkToVerb.hasDobj = True
talkToVerb.impDobj = True
talkToVerb.preposition = ["to", "with"]
talkToVerb.dtype = "Actor"


def getImpTalkTo(game):
    """If no dobj is specified, try to guess the Actor
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """

    people = Verb.disambiguateActor(
        game, "There's no one obvious here to talk to. ", "Would you like to talk to ",
    )

    if len(people) == 0:
        return None

    elif len(people) == 1:
        return people[0]

    game.lastTurn.things = people
    game.lastTurn.ambiguous = True
    return None


# replace default getImpDobj method
talkToVerb.getImpDobj = getImpTalkTo


def talkToVerbFunc(game, dobj, skip=False):
    """Talk to an Actor
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """

    if not skip:
        runfunc = True
        try:
            runfunc = dobj.talkToVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = dobj.talkToVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Actor):
        if dobj.hermit_topic:
            dobj.hermit_topic.func(game, False)
        elif dobj.sticky_topic:
            dobj.sticky_topic.func(game)
        elif dobj.hi_topic and not dobj.said_hi:
            dobj.hi_topic.func(game)
            dobj.said_hi = True
        elif dobj.return_hi_topic:
            dobj.return_hi_topic.func(game)
        else:
            dobj.defaultTopic(game)
    else:
        game.addTextToEvent("turn", "You cannot talk to that. ")


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


# replace the default getImpDobj method
askVerb.getImpDobj = getImpTalkTo


def askVerbFunc(game, dobj, iobj, skip=False):
    """
    Ask an Actor about a Thing
    Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing,
    and iobj, a Thing
    """

    if isinstance(dobj, Actor):
        if dobj.hermit_topic:
            dobj.hermit_topic.func(game, False)
            return True

    if not skip:
        runfunc = True
        try:
            runfunc = dobj.askVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.askVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Actor):
        # try to find the ask topic for iobj
        if dobj.hi_topic and not dobj.said_hi:
            dobj.hi_topic.func(game, False)
            dobj.said_hi = True
        if iobj == reflexive:
            iobj = dobj
        if iobj.ix in dobj.ask_topics:
            # call the ask function for iobj
            if dobj.sticky_topic:
                dobj.ask_topics[iobj.ix].func(game, False)
                dobj.sticky_topic.func(game)
            else:
                dobj.ask_topics[iobj.ix].func(game)
        elif dobj.sticky_topic:
            dobj.defaultTopic(game, False)
            dobj.sticky_topic.func(game)
        else:
            dobj.defaultTopic(game)
    else:
        game.addTextToEvent("turn", "You cannot talk to that. ")


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

# replace default getImpDobj method
tellVerb.getImpDobj = getImpTalkTo


def tellVerbFunc(game, dobj, iobj, skip=False):
    """Tell an Actor about a Thing
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """

    if isinstance(dobj, Actor):
        if dobj.hermit_topic:
            dobj.hermit_topic.func(game, False)
            return True
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.tellVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = dobj.tellVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Actor):
        if dobj.hi_topic and not dobj.said_hi:
            dobj.hi_topic.func(game, False)
            dobj.said_hi = True
        if iobj == reflexive:
            iobj = dobj
        if iobj.ix in dobj.tell_topics:
            if dobj.sticky_topic:
                dobj.tell_topics[iobj.ix].func(game, False)
                dobj.sticky_topic.func(game)
            else:
                dobj.tell_topics[iobj.ix].func(game)
        elif dobj.sticky_topic:
            dobj.defaultTopic(game, False)
            dobj.sticky_topic.func(game)
        else:
            dobj.defaultTopic(game)
    else:
        game.addTextToEvent("turn", "You cannot talk to that. ")


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


# replace default getImpDobj method
giveVerb.getImpDobj = getImpTalkTo


def giveVerbFunc(game, dobj, iobj, skip=False):
    """Give an Actor a Thing
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.giveVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.giveVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Actor):
        if dobj.hermit_topic:
            dobj.hermit_topic.func(game, False)
            return True
    if iobj is game.me:
        game.addTextToEvent("turn", "You cannot give yourself away. ")
        return False
    elif isinstance(iobj, Actor):
        game.addTextToEvent("turn", "You cannot give a person away. ")
        return False
    if isinstance(dobj, Actor):
        if dobj.hi_topic and not dobj.said_hi:
            dobj.hi_topic.func(game, False)
            dobj.said_hi = True
        if iobj.ix in dobj.give_topics:
            if dobj.sticky_topic:
                dobj.give_topics[iobj.ix].func(game, False)
                dobj.sticky_topic.func(game)
            else:
                dobj.give_topics[iobj.ix].func(game)
            if iobj.give:
                game.me.removeThing(dobj)
                dobj.addThing(iobj)
            return True
        elif dobj.sticky_topic:
            dobj.defaultTopic(game, False)
            dobj.sticky_topic.func(game)
        else:
            dobj.defaultTopic(game)
            return True
    else:
        game.addTextToEvent("turn", "You cannot talk to that. ")


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

# replace default getImpDobj method
showVerb.getImpDobj = getImpTalkTo


def showVerbFunc(game, dobj, iobj, skip=False):
    """Show an Actor a Thing
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """
    if isinstance(dobj, Actor):
        if dobj.hermit_topic:
            dobj.hermit_topic.func(game, False)
            return True
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.showVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.showVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Actor):
        if dobj.hi_topic and not dobj.said_hi:
            dobj.hi_topic.func(game, False)
            dobj.said_hi = True
        if iobj.ix in dobj.show_topics:
            if dobj.sticky_topic:
                dobj.show_topics[iobj.ix].func(game, False)
                dobj.sticky_topic.func(game)
            else:
                dobj.show_topics[iobj.ix].func(game)
        elif dobj.sticky_topic:
            dobj.defaultTopic(game, False)
            dobj.sticky_topic.func(game)
        else:
            dobj.defaultTopic(game)

    else:
        game.addTextToEvent("turn", "You cannot talk to that. ")


# replace default verbFunc method
showVerb.verbFunc = showVerbFunc

# WEAR/PUT ON
# transitive verb, no indirect object
wearVerb = Verb("wear")
wearVerb.addSynonym("put")
wearVerb.addSynonym("don")
wearVerb.syntax = [
    ["put", "on", "<dobj>"],
    ["put", "<dobj>", "on"],
    ["wear", "<dobj>"],
    ["don", "<dobj>"],
]
wearVerb.hasDobj = True
wearVerb.dtype = "Clothing"
wearVerb.dscope = "inv"
wearVerb.preposition = ["on"]


def wearVerbFunc(game, dobj, skip=False):
    """Wear a piece of clothing
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.wearVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Clothing):
        game.addTextToEvent(
            "turn", "You wear " + dobj.getArticle(True) + dobj.verbose_name + ". "
        )
        # game.me.contains.remove(dobj)
        game.me.contains[dobj.ix].remove(dobj)
        if game.me.contains[dobj.ix] == []:
            del game.me.contains[dobj.ix]
        # game.me.wearing.append(dobj)
        if dobj.ix in game.me.wearing:
            game.me.wearing[dobj.ix].append(dobj)
        else:
            game.me.wearing[dobj.ix] = [dobj]
    else:
        game.addTextToEvent("turn", "You cannot wear that. ")


# replace default verbFunc method
wearVerb.verbFunc = wearVerbFunc

# TAKE OFF/DOFF
# transitive verb, no indirect object
doffVerb = Verb("take")
doffVerb.addSynonym("doff")
doffVerb.addSynonym("remove")
doffVerb.syntax = [
    ["take", "off", "<dobj>"],
    ["take", "<dobj>", "off"],
    ["doff", "<dobj>"],
    ["remove", "<dobj>"],
]
doffVerb.hasDobj = True
doffVerb.dscope = "wearing"
doffVerb.preposition = ["off"]


def doffVerbFunc(game, dobj, skip=False):
    """Take off a piece of clothing
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.doffVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True

    game.addTextToEvent(
        "turn", "You take off " + dobj.getArticle(True) + dobj.verbose_name + ". "
    )
    # game.me.contains.append(dobj)
    if dobj.ix in game.me.contains:
        game.me.contains[dobj.ix].append(dobj)
    else:
        game.me.contains[dobj.ix] = [dobj]
    # game.me.wearing.remove(dobj)
    game.me.wearing[dobj.ix].remove(dobj)
    if game.me.wearing[dobj.ix] == []:
        del game.me.wearing[dobj.ix]


# replace default verbFunc method
doffVerb.verbFunc = doffVerbFunc

# LIE DOWN
# intransitive verb
lieDownVerb = Verb("lie")
lieDownVerb.addSynonym("lay")
lieDownVerb.syntax = [["lie", "down"], ["lay", "down"]]
lieDownVerb.preposition = ["down"]


def lieDownVerbFunc(game):
    """Take off a piece of clothing
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app"""
    if game.me.position != "lying":
        if isinstance(game.me.location, Thing):
            if not game.me.location.canLie:
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
        game.addTextToEvent("turn", "You lie down. ")
        game.me.makeLying()
    else:
        game.addTextToEvent("turn", "You are already lying down. ")


# replace default verbFunc method
lieDownVerb.verbFunc = lieDownVerbFunc

# STAND UP
# intransitive verb
standUpVerb = Verb("stand")
standUpVerb.addSynonym("get")
standUpVerb.syntax = [["stand", "up"], ["stand"], ["get", "up"]]
standUpVerb.preposition = ["up"]


def standUpVerbFunc(game):
    """Take off a piece of clothing
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app"""
    if game.me.position != "standing":
        if isinstance(game.me.location, Thing):
            if not game.me.location.canStand:
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


# replace default verbFunc method
standUpVerb.verbFunc = standUpVerbFunc

# SIT DOWN
# intransitive verb
sitDownVerb = Verb("sit")
sitDownVerb.syntax = [["sit", "down"], ["sit"]]
sitDownVerb.preposition = ["down"]


def sitDownVerbFunc(game):
    """Take off a piece of clothing
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app"""
    if game.me.position != "sitting":
        if isinstance(game.me.location, Thing):
            if not game.me.location.canSit:
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
        game.addTextToEvent("turn", "You sit down. ")
        game.me.makeSitting()
    else:
        game.addTextToEvent("turn", "You are already sitting. ")


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


def standOnVerbFunc(game, dobj, skip=False):
    """Sit on a Surface where canSit is True
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.standOnVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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
    elif isinstance(dobj, Surface) and dobj.canStand:
        game.addTextToEvent(
            "turn", "You stand on " + dobj.getArticle(True) + dobj.verbose_name + ". "
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
            "You cannot stand on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
        )
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


def sitOnVerbFunc(game, dobj, skip=False):
    """Stand on a Surface where canStand is True
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.sitOnVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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
                "turn", "You sit on " + dobj.getArticle(True) + dobj.verbose_name + ". "
            )
            game.me.makeSitting()
        else:
            game.me.location.removeThing(game.me)
            outer_loc.addThing(game.me)
            game.addTextToEvent(
                "turn", "You sit on " + dobj.getArticle(True) + dobj.verbose_name + ". "
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
    elif isinstance(dobj, Surface) and dobj.canSit:
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


# replace default verbFunc method
sitOnVerb.verbFunc = sitOnVerbFunc

# LIE ON (SURFACE)
# transitive verb, no indirect object
lieOnVerb = Verb("lie", "lie on")
lieOnVerb.addSynonym("lay")
lieOnVerb.syntax = [
    ["lie", "on", "<dobj>"],
    ["lie", "down", "on", "<dobj>"],
    ["lay", "on", "<dobj>"],
    ["lay", "down", "on", "<dobj>"],
]
lieOnVerb.hasDobj = True
lieOnVerb.dscope = "room"
lieOnVerb.dtype = "Surface"
lieOnVerb.preposition = ["down", "on"]


def lieOnVerbFunc(game, dobj):
    """Lie on a Surface where canLie is True
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    runfunc = True
    try:
        runfunc = dobj.lieOnVerbDobj(game)
    except AttributeError:
        pass
    if not runfunc:
        return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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
                "turn", "You lie on " + dobj.getArticle(True) + dobj.verbose_name + ". "
            )
            game.me.makeLying()
        else:
            game.me.location.removeThing(game.me)
            outer_loc.addThing(game.me)
            game.addTextToEvent(
                "turn",
                "You lie on the " + dobj.getArticle(True) + dobj.verbose_name + ". ",
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
    elif isinstance(dobj, Surface) and dobj.canLie:
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
def sitInVerbFunc(game, dobj, skip=False):
    """Stand on a Surface where canStand is True
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.sitInVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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
    elif isinstance(dobj, Container) and dobj.canSit:
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


def standInVerbFunc(game, dobj, skip=False):
    """Sit on a Surface where canSit is True
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.standInVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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
    elif isinstance(dobj, Container) and dobj.canStand:
        game.addTextToEvent(
            "turn", "You stand in " + dobj.getArticle(True) + dobj.verbose_name + ". "
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
            "You cannot stand in " + dobj.getArticle(True) + dobj.verbose_name + ". ",
        )
        return False


# replace default verbFunc method
standInVerb.verbFunc = standInVerbFunc

# LIE IN (CONTAINER)
# transitive verb, no indirect object
lieInVerb = Verb("lie", "lie in")
lieInVerb.addSynonym("lay")
lieInVerb.syntax = [
    ["lie", "in", "<dobj>"],
    ["lie", "down", "in", "<dobj>"],
    ["lay", "in", "<dobj>"],
    ["lay", "down", "in", "<dobj>"],
]
lieInVerb.hasDobj = True
lieInVerb.dscope = "room"
lieInVerb.dtype = "Container"
lieInVerb.preposition = ["down", "in"]


def lieInVerbFunc(game, dobj, skip=False):
    """Lie on a Surface where canLie is True
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.lieInVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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
    elif isinstance(dobj, Container) and dobj.canLie:
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


# replace default verbFunc method
lieInVerb.verbFunc = lieInVerbFunc

# CLIMB ON (SURFACE)
# transitive verb, no indirect object
climbOnVerb = Verb("climb", "climb on")
climbOnVerb.addSynonym("get")
climbOnVerb.syntax = [
    ["climb", "on", "<dobj>"],
    ["get", "on", "<dobj>"],
    ["climb", "<dobj>"],
    ["climb", "up", "<dobj>"],
]
climbOnVerb.hasDobj = True
climbOnVerb.dscope = "room"
climbOnVerb.dtype = "Surface"
climbOnVerb.dobj_direction = "u"
climbOnVerb.preposition = ["on", "up"]


def climbOnVerbFunc(game, dobj, skip=False):
    """Climb on a Surface where one of more of canStand/canSit/canLie is True
	Will be extended once stairs/ladders are implemented
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.climbOnVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if dobj.connection:
        if dobj.direction == "u":
            dobj.connection.travel(game)
        else:
            game.addTextToEvent("turn", "You can't climb up that. ")
            return False
    elif isinstance(dobj, Surface) and dobj.canStand:
        standOnVerb.verbFunc(game, dobj)
        return True
    elif isinstance(dobj, Surface) and dobj.canSit:
        sitOnVerb.verbFunc(game, dobj)
        return True
    elif isinstance(dobj, Surface) and dobj.canLie:
        lieOnVerb.verbFunc(game, dobj)
        return True
    else:
        game.addTextToEvent(
            "turn",
            "You cannot climb on " + dobj.getArticle(True) + dobj.verbose_name + ". ",
        )
        return False


# replace default verbFunc method
climbOnVerb.verbFunc = climbOnVerbFunc

# CLIMB UP (INTRANSITIVE)
# intransitive verb
climbUpVerb = Verb("climb")
climbUpVerb.syntax = [["climb", "up"], ["climb"]]
climbUpVerb.preposition = ["up"]


def climbUpVerbFunc(game):
    """Climb up to the room above
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    from .travel import travel

    cur_loc = game.me.getOutermostLocation()
    if cur_loc.up:
        travel.travelU(game)
    else:
        game.addTextToEvent("turn", "You cannot climb up from here. ")


# replace default verbFunc method
climbUpVerb.verbFunc = climbUpVerbFunc


# CLIMB DOWN (INTRANSITIVE)
# intransitive verb
climbDownVerb = Verb("climb", "climb down")
climbDownVerb.addSynonym("get")
climbDownVerb.syntax = [
    ["climb", "off"],
    ["get", "off"],
    ["climb", "down"],
    ["get", "down"],
]
climbDownVerb.preposition = ["off", "down"]


def climbDownVerbFunc(game):
    """Climb down from a Surface you currently occupy
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    from . import travel

    cur_loc = game.me.getOutermostLocation()
    if cur_loc.down:
        travel.travelD(game)
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


# replace default verbFunc method
climbDownVerb.verbFunc = climbDownVerbFunc

# CLIMB DOWN FROM (SURFACE)
# transitive verb, no indirect object
climbDownFromVerb = Verb("climb", "climb down from")
climbDownFromVerb.addSynonym("get")
climbDownFromVerb.syntax = [
    ["climb", "off", "<dobj>"],
    ["get", "off", "<dobj>"],
    ["climb", "down", "from", "<dobj>"],
    ["get", "down", "from", "<dobj>"],
    ["climb", "down", "<dobj>"],
]
climbDownFromVerb.hasDobj = True
climbDownFromVerb.dscope = "room"
climbDownFromVerb.preposition = ["off", "down", "from"]
climbDownFromVerb.dobj_direction = "d"


def climbDownFromVerbFunc(game, dobj, skip=False):
    """Climb down from a Surface you currently occupy
	Will be extended once stairs/ladders/up direction/down direction are implemented
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.climbDownFromVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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
            "turn", "You are not on " + dobj.getArticle(True) + dobj.verbose_name + ". "
        )
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


def goThroughVerbFunc(game, dobj, skip=False):
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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


goThroughVerb.verbFunc = goThroughVerbFunc

# CLIMB IN (CONTAINER)
# transitive verb, no indirect object
climbInVerb = Verb("climb", "climb in")
climbInVerb.addSynonym("get")
climbInVerb.addSynonym("enter")
climbInVerb.addSynonym("go")
climbInVerb.syntax = [
    ["climb", "in", "<dobj>"],
    ["get", "in", "<dobj>"],
    ["climb", "into", "<dobj>"],
    ["get", "into", "<dobj>"],
    ["enter", "<dobj>"],
    ["go", "in", "<dobj>"],
    ["go", "into", "<dobj>"],
]
climbInVerb.hasDobj = True
climbInVerb.dscope = "room"
climbInVerb.preposition = ["in", "into"]


def climbInVerbFunc(game, dobj, skip=False):
    """Climb in a Container where one of more of canStand/canSit/canLie is True
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.climbInVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if dobj.connection:
        dobj.connection.travel(game)
        return True
    if isinstance(dobj, Container) and dobj.canStand:
        if dobj.has_lid:
            if not dobj.is_open:
                game.addTextToEvent(
                    "turn",
                    "You cannot climb into "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + ", since it is closed. ",
                )
                return False
        standInVerb.verbFunc(game, dobj)
        return True
    elif isinstance(dobj, Container) and dobj.canSit:
        if dobj.has_lid:
            if not dobj.is_open:
                game.addTextToEvent(
                    "turn",
                    "You cannot climb into "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + ", since it is closed. ",
                )
                return False
        sitInVerb.verbFunc(game, dobj)
        return True
    elif isinstance(dobj, Container) and dobj.canLie:
        if dobj.has_lid:
            if not dobj.is_open:
                game.addTextToEvent(
                    "turn",
                    "You cannot climb into "
                    + dobj.getArticle(True)
                    + dobj.verbose_name
                    + ", since it is closed. ",
                )
                return False
        lieInVerb.verbFunc(game, dobj)
        return True
    else:
        game.addTextToEvent(
            "turn",
            "You cannot climb into " + dobj.getArticle(True) + dobj.verbose_name + ". ",
        )
        return False


# replace default verbFunc method
climbInVerb.verbFunc = climbInVerbFunc

# CLIMB OUT (INTRANSITIVE)
# intransitive verb
climbOutVerb = Verb("climb", "climb out")
climbOutVerb.addSynonym("get")
climbOutVerb.syntax = [["climb", "out"], ["get", "out"]]
climbOutVerb.preposition = ["out"]


def climbOutVerbFunc(game):
    """Climb out of a Container you currently occupy
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    if isinstance(game.me.location, Container):
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
    else:
        game.addTextToEvent("turn", "You cannot climb out of here. ")


# replace default verbFunc method
climbOutVerb.verbFunc = climbOutVerbFunc

# CLIMB OUT OF (CONTAINER)
# transitive verb, no indirect object
climbOutOfVerb = Verb("climb", "climb out of")
climbOutOfVerb.addSynonym("get")
climbOutOfVerb.addSynonym("exit")
climbOutOfVerb.syntax = [
    ["climb", "out", "of", "<dobj>"],
    ["get", "out", "of", "<dobj>"],
    ["exit", "<dobj>"],
]
climbOutOfVerb.hasDobj = True
climbOutOfVerb.dscope = "room"
climbOutOfVerb.preposition = ["out", "of"]


def climbOutOfVerbFunc(game, dobj, skip=False):
    """Climb down from a Surface you currently occupy
	Will be extended once stairs/ladders/up direction/down direction are implemented
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.climbOutOfVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True

    if game.me.location == dobj:
        if isinstance(game.me.location, Container):
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
            return False
    else:
        game.addTextToEvent(
            "turn", "You are not in " + dobj.getArticle(True) + dobj.verbose_name + ". "
        )
        return False


# replace default verbFunc method
climbOutOfVerb.verbFunc = climbOutOfVerbFunc

# OPEN
# transitive verb, no indirect object
openVerb = Verb("open")
openVerb.syntax = [["open", "<dobj>"]]
openVerb.hasDobj = True
openVerb.dscope = "near"


def openVerbFunc(game, dobj, skip=False):
    """Open a Thing with an open property
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """
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
    runfunc = True

    if not skip:
        try:
            runfunc = dobj.openVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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
            lookInVerb.verbFunc(game, dobj)
        return True
    else:
        game.addTextToEvent(
            "turn",
            (dobj.getArticle(True) + dobj.verbose_name).capitalize()
            + " is already open. ",
        )
    return True


# replace default verbFunc method
openVerb.verbFunc = openVerbFunc

# CLOSE
# transitive verb, no indirect object
closeVerb = Verb("close")
closeVerb.addSynonym("shut")
closeVerb.syntax = [["close", "<dobj>"], ["shut", "<dobj>"]]
closeVerb.hasDobj = True
closeVerb.dscope = "near"


def closeVerbFunc(game, dobj, skip=False):
    """Open a Thing with an open property
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing """

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

    if not skip:
        runfunc = True
        try:
            runfunc = dobj.closeVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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


# replace default verbFunc method
closeVerb.verbFunc = closeVerbFunc

# EXIT (INTRANSITIVE)
# intransitive verb
exitVerb = Verb("exit")
exitVerb.syntax = [["exit"]]


def exitVerbFunc(game):
    """Climb out of a Container you currently occupy
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    from .travel import travel

    out_loc = game.me.getOutermostLocation()
    if isinstance(game.me.location, Thing):
        climbOutOfVerb.verbFunc(game, game.me.location)
    elif out_loc.exit:
        travel.travelOut(game)
    else:
        game.addTextToEvent("turn", "There is no obvious exit. ")


# replace default verbFunc method
exitVerb.verbFunc = exitVerbFunc

# ENTER (INTRANSITIVE)
# intransitive verb
enterVerb = Verb("enter")
enterVerb.syntax = [["enter"]]


def enterVerbFunc(game):
    """Climb out of a Container you currently occupy
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    from .travel import travel

    out_loc = game.me.getOutermostLocation()
    if out_loc.entrance:
        travel.travelIn(game)
    else:
        game.addTextToEvent("turn", "There is no obvious entrance. ")


# replace default verbFunc method
enterVerb.verbFunc = enterVerbFunc

# UNLOCK
# transitive verb, no indirect object
unlockVerb = Verb("unlock")
unlockVerb.addSynonym("unbolt")
unlockVerb.syntax = [["unlock", "<dobj>"], ["unbolt", "<dobj>"]]
unlockVerb.hasDobj = True
unlockVerb.dscope = "near"


def unlockVerbFunc(game, dobj, skip=False):
    """Unlock a Door or Container with an lock
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing
	Returns True when the function ends with dobj unlocked, or without a lock. Returns False on failure to unlock. """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.unlockVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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
                                + dobj.lock_obj.key_obj.location.lowNameArticle(True)
                                + ".)",
                            )
                            # dobj.lock_obj.key_obj.location.removeThing(dobj.lock_obj.key_obj)
                            # game.me.addThing(dobj.lock_obj.key_obj)
                            removeFromVerb.verbFunc(
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
                        removeFromVerb.verbFunc(
                            game, dobj.key_obj, dobj.key_obj.location
                        )
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


# replace default verbFunc method
unlockVerb.verbFunc = unlockVerbFunc

# LOCK
# transitive verb, no indirect object
lockVerb = Verb("lock")
lockVerb.addSynonym("bolt")
lockVerb.syntax = [["lock", "<dobj>"], ["bolt", "<dobj>"]]
lockVerb.hasDobj = True
lockVerb.dscope = "near"


def lockVerbFunc(game, dobj, skip=False):
    """Lock a Door or Container with an lock
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing
	Returns True when the function ends with dobj locked. Returns False on failure to lock, or when dobj has no lock. """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.lockVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Container) or isinstance(dobj, Door):
        if dobj.is_open:
            if not closeVerb.verbFunc(game, dobj):
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
                                + dobj.lock_obj.key_obj.location.lowNameArticle(True)
                                + ".)",
                            )
                            # dobj.lock_obj.key_obj.location.removeThing(dobj.lock_obj.key_obj)
                            # game.me.addThing(dobj.lock_obj.key_obj)
                            removeFromVerb.verbFunc(
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
    elif isinstance(dobj, Lock):
        if dobj.parent_obj.is_open:
            if not closeVerb.verbFunc(game, dobj.parent_obj):
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
                        removeFromVerb.verbFunc(
                            game, dobj.key_obj, dobj.key_obj.location
                        )
                    game.addTextToEvent(
                        "turn",
                        "You lock " + dobj.getArticle(True) + dobj.verbose_name + ". ",
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


# replace default verbFunc method
lockVerb.verbFunc = lockVerbFunc

# UNLOCK WITH
# transitive verb with indirect object
unlockWithVerb = Verb("unlock")
unlockWithVerb.addSynonym("unbolt")
unlockWithVerb.addSynonym("open")
unlockWithVerb.syntax = [
    ["unlock", "<dobj>", "using", "<iobj>"],
    ["unlock", "<dobj>", "with", "<iobj>"],
    ["unbolt", "<dobj>", "with", "<iobj>"],
    ["unbolt", "<dobj>", "using", "<iobj>"],
    ["open", "<dobj>", "using", "<iobj>"],
    ["open", "<dobj>", "with", "<iobj>"],
]
unlockWithVerb.hasDobj = True
unlockWithVerb.hasIobj = True
unlockWithVerb.preposition = ["with", "using"]
unlockWithVerb.dscope = "near"
unlockWithVerb.iscope = "invflex"


def unlockWithVerbFunc(game, dobj, iobj, skip=False):
    """Unlock a Door or Container with an lock
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing
	Returns True when the function ends with dobj unlocked, or without a lock. Returns False on failure to unlock.  """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.unlockVerbDobj(game, iobj)
        except AttributeError:
            supress = False
        try:
            runfunc = iobj.unlockVerbIobj(game, dobj)
        except AttributeError:
            supress = False
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", iobj.cannot_interact_msg)
        return False
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


# replace default verbFunc method
unlockWithVerb.verbFunc = unlockWithVerbFunc

# LOCK WITH
# transitive verb with indirect object
lockWithVerb = Verb("lock")
lockWithVerb.addSynonym("bolt")
lockWithVerb.syntax = [
    ["lock", "<dobj>", "using", "<iobj>"],
    ["lock", "<dobj>", "with", "<iobj>"],
    ["bolt", "<dobj>", "with", "<iobj>"],
    ["bolt", "<dobj>", "using", "<iobj>"],
]
lockWithVerb.hasDobj = True
lockWithVerb.hasIobj = True
lockWithVerb.preposition = ["with", "using"]
lockWithVerb.dscope = "near"
lockWithVerb.iscope = "invflex"


def lockWithVerbFunc(game, dobj, iobj, skip=False):
    """Unlock a Door or Container with an lock
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, and dobj, a Thing
	Returns True when the function ends with dobj unlocked, or without a lock. Returns False on failure to unlock.  """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.lockVerbDobj(game, iobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
        try:
            runfunc = dobj.lockVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Container) or isinstance(dobj, Door):
        if dobj.is_open:
            if not closeVerb.verbFunc(game, dobj):
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

    elif isinstance(dobj, Lock):
        if dobj.parent_obj.is_open:
            if not closeVerb.verbFunc(game, dobj.parent_obj):
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


# replace default verbFunc method
lockWithVerb.verbFunc = lockWithVerbFunc

# GO (empty verb added to improve "I don't understand" messages for invalid directions)
# transitive verb, no indirect object
goVerb = Verb("go")
goVerb.syntax = [["go", "<dobj>"]]
goVerb.hasDobj = True
goVerb.dscope = "direction"


def goVerbFunc(game, dobj):
    """Empty function which should never be evaluated
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 application, and dobj, a Thing """
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


def lightVerbFunc(game, dobj, skip=False):
    """Light a LightSource """
    # print the target's xdesc (examine descripion)
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.lightVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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


# replace default verbFunc method
lightVerb.verbFunc = lightVerbFunc

# EXTINGUISH (LightSource)
# transitive verb, no indirect object
extinguishVerb = Verb("extinguish")
extinguishVerb.addSynonym("put")
extinguishVerb.syntax = [
    ["extinguish", "<dobj>"],
    ["put", "out", "<dobj>"],
    ["put", "<dobj>", "out"],
]
extinguishVerb.hasDobj = True
extinguishVerb.dscope = "near"
extinguishVerb.dtype = "LightSource"
extinguishVerb.preposition = ["out"]


def extinguishVerbFunc(game, dobj, skip=False):
    """Extinguish a LightSource """
    # print the target's xdesc (examine descripion)
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.extinguishVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
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


# replace default verbFunc method
extinguishVerb.verbFunc = extinguishVerbFunc

# WAIT A TURN
# intransitive verb
waitVerb = Verb("wait")
waitVerb.addSynonym("z")
waitVerb.syntax = [["wait"], ["z"]]
waitVerb.hasDobj = False


def waitVerbFunc(game):
    """Wait a turn
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app """
    game.addTextToEvent("turn", "You wait a turn. ")
    return True


# replace default verbFunc method
waitVerb.verbFunc = waitVerbFunc

# USE (THING)
# transitive verb, no indirect object
useVerb = Verb("use")
useVerb.syntax = [["use", "<dobj>"]]
useVerb.hasDobj = True
useVerb.dscope = "near"


def useVerbFunc(game, dobj, skip=False):
    """Use a Thing
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 application, and dobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.useVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
        if isinstance(dobj, LightSource):
            return lightVerb.verbFunc(game, dobj)
        elif isinstance(dobj, Key):

            game.addTextToEvent(
                "turn",
                "What would you like to unlock with " + dobj.lowNameArticle(True) + "?",
            )
            game.lastTurn.verb = unlockWithVerb
            game.lastTurn.iobj = dobj
            game.lastTurn.dobj = False
            game.lastTurn.ambiguous = True
        elif isinstance(dobj, Transparent):
            return lookThroughVerb.verbFunc(game, dobj)
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


# replace the default verbFunc method
useVerb.verbFunc = useVerbFunc

# BUY FROM
# transitive verb with indirect object
buyFromVerb = Verb("buy", "buy from")
buyFromVerb.addSynonym("purchase")
buyFromVerb.syntax = [
    ["buy", "<dobj>", "from", "<iobj>"],
    ["purchase", "<dobj>", "from", "<iobj>"],
]
buyFromVerb.hasDobj = True
buyFromVerb.dscope = "knows"
buyFromVerb.hasIobj = True
buyFromVerb.iscope = "room"
buyFromVerb.itype = "Actor"
buyFromVerb.preposition = ["from"]


def buyFromVerbFunc(game, dobj, iobj, skip=False):
    """Buy something from a person
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.buyFromVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.buyFromVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if not isinstance(iobj, Actor):
        game.addTextToEvent(
            "turn", "You cannot buy anything from " + iobj.lowNameArticle(False) + ". "
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
                + currency.getPlural()
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


# replace the default verbFunc method
buyFromVerb.verbFunc = buyFromVerbFunc

# BUY
# transitive verb
buyVerb = Verb("buy")
buyVerb.addSynonym("purchase")
buyVerb.syntax = [["buy", "<dobj>"], ["purchase", "<dobj>"]]
buyVerb.hasDobj = True
buyVerb.dscope = "knows"


def buyVerbFunc(game, dobj):
    """Redriect to buy from
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing """

    people = Verb.disambiguateActor(
        game,
        "There's no one obvious here to buy from. ",
        "Would you like to buy from ",
    )
    if len(people) > 1:
        game.lastTurn.verb = buyFromVerb
        game.lastTurn.dobj = dobj
        game.lastTurn.iobj = None
        game.lastTurn.things = people
        game.lastTurn.ambiguous = True
        return False

    elif len(people) == 0:
        return False

    return buyFromVerb.verbFunc(game, dobj, people[0])


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


def sellToVerbFunc(game, dobj, iobj, skip=False):
    """Sell something to a person
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.sellToVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.sellToVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if not isinstance(iobj, Actor):
        game.addTextToEvent(
            "turn", "You cannot sell anything to " + iobj.lowNameArticle(False) + ". "
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
            + dobj.getPlural()
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


# replace the default verbFunc method
sellToVerb.verbFunc = sellToVerbFunc

# SELL
# transitive verb
sellVerb = Verb("sell")
sellVerb.syntax = [["sell", "<dobj>"]]
sellVerb.hasDobj = True
sellVerb.dscope = "invflex"


def sellVerbFunc(game, dobj):
    """Redriect to sell to
    Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing """

    people = Verb.disambiguateActor(
        game,
        "There's no one obvious here to sell to. ",
        "Would you like to sell it to ",
    )

    if len(people) == 1:
        # ask the only actor in the room
        iobj = people[0]
        return sellToVerb.verbFunc(game, dobj, iobj)

    if len(people) > 1:
        game.lastTurn.verb = sellToVerb
        game.lastTurn.dobj = dobj
        game.lastTurn.iobj = None
        game.lastTurn.things = people
        game.lastTurn.ambiguous = True

    return False


# replace the default verbFunc method
sellVerb.verbFunc = sellVerbFunc

# RECORD ON
# intransitive verb
recordOnVerb = Verb("record", "record on")
recordOnVerb.addSynonym("recording")
recordOnVerb.syntax = [["record", "on"], ["recording", "on"]]
recordOnVerb.preposition = ["on"]


def recordOnVerbFunc(game):
    f = game.app.saveFilePrompt(".txt", "Text files", "Enter a file to record to")
    success = game.recordOn(f)
    if success:
        game.addTextToEvent("turn", "**RECORDING ON**")
    else:
        game.addTextToEvent("turn", "Could not open file for recording.")
    return success


# replace the default verb function
recordOnVerb.verbFunc = recordOnVerbFunc

# RECORD OFF
# intransitive verb
recordOffVerb = Verb("record", "record off")
recordOffVerb.addSynonym("recording")
recordOffVerb.syntax = [["record", "off"], ["recording", "off"]]
recordOffVerb.preposition = ["off"]


def recordOffVerbFunc(game):
    game.recordOff()
    game.addTextToEvent("turn", "**RECORDING OFF**")


# replace the default verb function
recordOffVerb.verbFunc = recordOffVerbFunc

# RECORD OFF
# intransitive verb
playBackVerb = Verb("playback")
playBackVerb.syntax = [["playback"]]


def playBackVerbFunc(game):
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


# SAVE
saveVerb = Verb("save")
saveVerb.syntax = [["save"]]


def saveVerbFunc(game):
    f = game.app.saveFilePrompt(".sav", "Save files", "Enter a file to save to")

    if f:
        SaveGame(f)
        game.addTextToEvent("turn", "Game saved.")
        return True
    game.addTextToEvent("turn", "Could not save game.")
    return False


saveVerb.verbFunc = saveVerbFunc


# LOAD
loadVerb = Verb("load")
loadVerb.syntax = [["load"]]


def loadVerbFunc(game):
    f = game.app.openFilePrompt(".sav", "Save files", "Enter a file to load")

    if not f:
        game.addTextToEvent("turn", "Choose a valid save file to load a game.")
        return False

    l = LoadGame(f)
    if not l.is_valid():
        game.addTextToEvent("turn", "Cannot load game file.")
        return False

    l.load()
    game.addTextToEvent("turn", "Game loaded.")
    return True


loadVerb.verbFunc = loadVerbFunc


def leadDirVerbFunc(game, dobj, iobj, skip=False):
    """Lead an Actor in a direction
	Takes arguments game.me, pointing to the player, game.app, the PyQt5 GUI game.app, dobj, a Thing, and iobj, a Thing """
    from .travel import TravelConnector

    if not skip:
        runfunc = True
        try:
            runfunc = dobj.leadDirVerbDobj(game, iobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if not isinstance(dobj, Actor):
        game.addTextToEvent("turn", "You cannot lead that. ")
        return False
    elif dobj.can_lead:
        from .travel import getDirectionFromString, directionDict

        destination = getDirectionFromString(dobj.getOutermostLocation(), iobj)
        if not destination:
            game.addTextToEvent(
                "turn", "You cannot lead " + dobj.lowNameArticle(True) + " that way. "
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
        directionDict[iobj](game)
    else:
        game.addTextToEvent(
            "turn", dobj.capNameArticle(True) + " doesn't want to be led. "
        )


# replace the default verbFunc method
leadDirVerb.verbFunc = leadDirVerbFunc

# BREAK
# transitive verb, no indirect object
breakVerb = Verb("break")
breakVerb.syntax = [["break", "<dobj>"]]
breakVerb.hasDobj = True
breakVerb.dscope = "near"


def breakVerbFunc(game, dobj, skip=False):
    """break a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.breakVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    game.addTextToEvent("turn", "Violence isn't the answer to this one. ")


# replace default verbFunc method
breakVerb.verbFunc = breakVerbFunc

# KICK
# transitive verb, no indirect object
kickVerb = Verb("kick")
kickVerb.syntax = [["kick", "<dobj>"]]
kickVerb.hasDobj = True
kickVerb.dscope = "near"


def kickVerbFunc(game, dobj, skip=False):
    """kick a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.kickVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    game.addTextToEvent("turn", "Violence isn't the answer to this one. ")


# replace default verbFunc method
kickVerb.verbFunc = kickVerbFunc

# KILL
# transitive verb, no indirect object
killVerb = Verb("kill")
killVerb.syntax = [["kill", "<dobj>"]]
killVerb.hasDobj = True
killVerb.dscope = "near"


def killVerbFunc(game, dobj, skip=False):
    """kill a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.killVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Actor):
        game.addTextToEvent("turn", "Violence isn't the answer to this one. ")
    else:
        game.addTextToEvent(
            "turn",
            dobj.capNameArticle(True) + " cannot be killed, as it is not alive. ",
        )


# replace default verbFunc method
killVerb.verbFunc = killVerbFunc

# JUMP
# intransitive verb
jumpVerb = Verb("jump")
jumpVerb.syntax = [["jump"]]


def jumpVerbFunc(game):
    """Jump in place
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app"""
    game.addTextToEvent("turn", "You jump in place. ")


# replace default verbFunc method
jumpVerb.verbFunc = jumpVerbFunc

# JUMP OVER
# transitive verb
jumpOverVerb = Verb("jump")
jumpOverVerb.syntax = [["jump", "over", "<dobj>"], ["jump", "across", "<dobj>"]]
jumpOverVerb.preposition = ["over", "across"]
jumpOverVerb.hasDobj = True
jumpOverVerb.dscope = "room"


def jumpOverVerbFunc(game, dobj, skip=False):
    """Jump over a Thing
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app"""
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.jumpOverVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if dobj == game.me:
        game.addTextToEvent("turn", "You cannot jump over yourself. ")
    elif dobj.size < 70:
        game.addTextToEvent("turn", "There's no reason to jump over that. ")
    else:
        game.addTextToEvent(
            "turn", dobj.capNameArticle(True) + " is too big to jump over. "
        )
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


def jumpInVerbFunc(game, dobj, skip=False):
    """Jump in a Thing
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app"""
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.jumpInVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    game.addTextToEvent("turn", "You cannot jump into that. ")
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


def jumpOnVerbFunc(game, dobj, skip=False):
    """Jump on a Thing
	Takes arguments game.me, pointing to the player, and game.app, the PyQt5 GUI game.app"""
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.jumpOnVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    game.addTextToEvent("turn", "You cannot jump onto that. ")
    return False


# replace default verbFunc method
jumpOnVerb.verbFunc = jumpOnVerbFunc

# PRESS
# transitive verb, no indirect object
pressVerb = Verb("press")
pressVerb.addSynonym("depress")
pressVerb.syntax = [
    ["press", "<dobj>"],
    ["depress", "<dobj>"],
    ["press", "on", "<dobj>"],
]
pressVerb.hasDobj = True
pressVerb.dscope = "near"
pressVerb.preposition = ["on"]
pressVerb.dtype = "Pressable"


def pressVerbFunc(game, dobj, skip=False):
    """press a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.pressVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Pressable):
        game.addTextToEvent("turn", "You press " + dobj.lowNameArticle(True) + ". ")
        dobj.pressThing(game)
    else:
        game.addTextToEvent(
            "turn", "Pressing " + dobj.lowNameArticle(True) + " has no effect. "
        )
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


def pushVerbFunc(game, dobj, skip=False):
    """push a Thing """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.pushVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Pressable):
        pressVerb.verbFunc(game, dobj)
    else:
        game.addTextToEvent(
            "turn",
            "You push on " + dobj.lowNameArticle(True) + ", to no productive end. ",
        )
        return False


# replace default verbFunc method
pushVerb.verbFunc = pushVerbFunc

# POUR OUT
# transitive verb, no indirect object
pourOutVerb = Verb("pour")
pourOutVerb.addSynonym("dump")
pourOutVerb.syntax = [
    ["pour", "<dobj>"],
    ["pour", "out", "<dobj>"],
    ["pour", "<dobj>", "out"],
    ["dump", "<dobj>"],
    ["dump", "out", "<dobj>"],
    ["dump", "<dobj>", "out"],
]
pourOutVerb.hasDobj = True
pourOutVerb.dscope = "invflex"
pourOutVerb.preposition = ["out"]


def pourOutVerbFunc(game, dobj, skip=False):
    """Pour a Liquid out of a Container """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.pourOutVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Container):
        loc = game.me.getOutermostLocation()
        if dobj.has_lid:
            if not dobj.is_open:
                game.addTextToEvent("turn", dobj.capNameArticle(True) + " is closed. ")
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
        if not dobj.getContainer:
            game.addTextToEvent(
                "turn", "It isn't in a container you can dump it from. "
            )
            return False
        elif not dobj.can_pour_out:
            game.addTextToEvent("turn", dobj.cannot_pour_out_msg)
            return False
        game.addTextToEvent("turn", "You dump out " + dobj.lowNameArticle(True) + ". ")
        dobj.dumpLiquid()
        return True
    game.addTextToEvent("turn", "You can't dump that out. ")
    return False


# replace default verbFunc method
pourOutVerb.verbFunc = pourOutVerbFunc

# DRINK
# transitive verb, no indirect object
drinkVerb = Verb("drink")
drinkVerb.syntax = [
    ["drink", "<dobj>"],
    ["drink", "from", "<dobj>"],
    ["drink", "out", "of", "<dobj>"],
]
drinkVerb.hasDobj = True
drinkVerb.dscope = "invflex"
drinkVerb.preposition = ["out", "from"]
drinkVerb.keywords = ["of"]


def drinkVerbFunc(game, dobj, skip=False):
    """Drink a Liquid """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.drinkVerbDobj(game)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Container):
        loc = game.me.getOutermostLocation()
        if dobj.has_lid:
            if not dobj.is_open:
                game.addTextToEvent("turn", dobj.capNameArticle(True) + " is closed. ")
                return False
        if dobj.contains == {}:
            game.addTextToEvent("turn", dobj.capNameArticle(True) + " is empty. ")
            return True
        liquid = dobj.containsLiquid()
        if not liquid:
            game.addTextToEvent(
                "turn",
                "There is nothing you can drink in " + dobj.lowNameArticle(True) + ". ",
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


# replace default verbFunc method
drinkVerb.verbFunc = drinkVerbFunc

# POUR INTO
# transitive verb, with indirect object
pourIntoVerb = Verb("pour")
pourIntoVerb.addSynonym("dump")
pourIntoVerb.syntax = [
    ["pour", "<dobj>", "into", "<iobj>"],
    ["pour", "<dobj>", "in", "<iobj>"],
    ["dump", "<dobj>", "into", "<iobj>"],
    ["dump", "<dobj>", "in", "<iobj>"],
]
pourIntoVerb.hasDobj = True
pourIntoVerb.hasIobj = True
pourIntoVerb.dscope = "invflex"
pourIntoVerb.iscope = "near"
pourIntoVerb.preposition = ["in", "into"]


def pourIntoVerbFunc(game, dobj, iobj, skip=False):
    """Pour a Liquid from one Container to another """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.pourIntoVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.pourIntoVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(dobj, Container):
        loc = game.me.getOutermostLocation()
        if dobj.has_lid:
            if not dobj.is_open:
                game.addTextToEvent("turn", dobj.capNameArticle(True) + " is closed. ")
                return False
        if dobj.contains == {}:
            game.addTextToEvent("turn", dobj.capNameArticle(True) + " is empty. ")
            return True
        liquid = dobj.containsLiquid()
        if not liquid:
            if not isinstance(iobj, Container):
                game.addTextToEvent(
                    "turn", iobj.capNameArticle(True) + " is not a container. "
                )
                return False
            game.addTextToEvent(
                "turn",
                "You dump the contents of "
                + dobj.lowNameArticle(True)
                + " into "
                + iobj.lowNameArticle(True)
                + ". ",
            )
            containslist = []
            for key in dobj.contains:
                for item in dobj.contains[key]:
                    containslist.append(item)
            for item in containslist:
                dobj.removeThing(item)
                if item.size < iobj.size:
                    iobj.addThing(item)
                else:
                    game.addTextToEvent(
                        "turn",
                        item.capNameArticle(True)
                        + " is too large to fit inside. It falls to the ground. ",
                    )
                    loc.addThing(item)
            return True
        else:
            dobj = liquid
    if isinstance(dobj, Liquid):
        if not dobj.getContainer:
            game.addTextToEvent(
                "turn", "It isn't in a container you can dump it from. "
            )
            return False
        elif not iobj.holds_liquid:
            game.addTextToEvent(
                "turn", iobj.capNameArticle(True) + " cannot hold a liquid. "
            )
            return False
        spaceleft = iobj.liquidRoomLeft()
        liquid_contents = iobj.containsLiquid()
        if iobj.has_lid:
            if not iobj.is_open:
                game.addTextToEvent("turn", dobj.capNameArticle(True) + " is closed. ")
                return False
        if iobj.contains != {} and not liquid_contents:
            game.addTextToEvent(
                "turn", "(First attempting to empty " + iobj.lowNameArticle(True) + ")"
            )
            success = pourOutVerb.verbFunc(game, iobj)
            if not success:
                return False
        if liquid_contents and liquid_contents.liquid_type != dobj.liquid_type:
            success = liquid_contents.mixWith(game, liquid_contents, dobj)
            if not success:
                game.addTextToEvent(
                    "turn",
                    iobj.capNameArticle(True)
                    + " is already full of "
                    + liquid_contents.lowNameArticle()
                    + ". ",
                )
                return False
            else:
                return True
        elif liquid_contents:
            if liquid_contents.infinite_well:
                game.addTextToEvent(
                    "turn",
                    "You pour "
                    + dobj.lowNameArticle(True)
                    + " into "
                    + iobj.lowNameArticle(True)
                    + ". ",
                )
                dobj.location.removeThing(dobj)
                return True
            game.addTextToEvent(
                "turn",
                iobj.capNameArticle(True)
                + " already has "
                + liquid_contents.lowNameArticle()
                + " in it. ",
            )
            return False
        else:
            game.addTextToEvent(
                "turn",
                "You pour "
                + dobj.lowNameArticle(True)
                + " into "
                + iobj.lowNameArticle(True)
                + ". ",
            )
            return dobj.fillVessel(iobj)
    game.addTextToEvent("turn", "You can't dump that out. ")
    return False


# replace default verbFunc method
pourIntoVerb.verbFunc = pourIntoVerbFunc

# FILL FROM
# transitive verb, with indirect object
fillFromVerb = Verb("fill")
fillFromVerb.syntax = [
    ["fill", "<dobj>", "from", "<iobj>"],
    ["fill", "<dobj>", "in", "<iobj>"],
]
fillFromVerb.hasDobj = True
fillFromVerb.hasIobj = True
fillFromVerb.dscope = "invflex"
fillFromVerb.iscope = "near"
fillFromVerb.preposition = ["from", "in"]


def fillFromVerbFunc(game, dobj, iobj, skip=False):
    """Pour a Liquid from one Container to another """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.fillFromVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.fillFromVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    if isinstance(iobj, Container):
        loc = game.me.getOutermostLocation()
        if iobj.has_lid:
            if not iobj.is_open:
                game.addTextToEvent("turn", iobj.capNameArticle(True) + " is closed. ")
                return False
        if iobj.contains == {}:
            game.addTextToEvent("turn", iobj.capNameArticle(True) + " is empty. ")
            return True
        liquid = iobj.containsLiquid()
        if not liquid:
            if iobj is game.me:
                game.addTextToEvent("turn", "You cannot fill anything from yourself. ")
            else:
                game.addTextToEvent(
                    "turn", "There is no liquid in " + dobj.lowNameArticle(True) + ". "
                )
            return False
        else:
            if not dobj.holds_liquid:
                game.addTextToEvent(
                    "turn", dobj.capNameArticle(True) + " cannot hold a liquid. "
                )
                return False
            if dobj.has_lid:
                if not dobj.is_open:
                    game.addTextToEvent(
                        "turn", dobj.capNameArticle(True) + " is closed. "
                    )
                    return False
            spaceleft = dobj.liquidRoomLeft()
            liquid_contents = dobj.containsLiquid()
            if dobj.contains != {} and not liquid_contents:
                game.addTextToEvent(
                    "turn",
                    "(First attempting to empty " + iobj.lowNameArticle(True) + ")",
                )
                success = pourOutVerb.verbFunc(game, iobj)
                if not success:
                    return False
            if not liquid.can_fill_from:
                game.addTextToEvent("turn", liquid.cannot_fill_from_msg)
                return False
            if liquid_contents and liquid_contents.liquid_type != liquid.liquid_type:
                success = liquid_contents.mixWith(game, liquid_contents, dobj)
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

            elif liquid.infinite_well:
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
    game.addTextToEvent("turn", "You can't fill that. ")
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


def fillWithVerbFunc(game, dobj, iobj, skip=False):
    """Pour a Liquid from one Container to another """
    if not skip:
        runfunc = True
        try:
            runfunc = dobj.fillWithVerbDobj(game, iobj)
        except AttributeError:
            pass
        try:
            runfunc = iobj.fillWithVerbIobj(game, dobj)
        except AttributeError:
            pass
        if not runfunc:
            return True
    if dobj.cannot_interact_msg:
        game.addTextToEvent("turn", dobj.cannot_interact_msg)
        return False
    elif iobj.cannot_interact_msg:
        game.addTextToEvent("turn", iobj.cannot_interact_msg)
    if not isinstance(dobj, Container):
        game.addTextToEvent(
            "turn", "You cannot fill " + dobj.lowNameArticle(True) + ". "
        )
        return False
    if isinstance(iobj, Liquid):
        if not dobj.holds_liquid:
            game.addTextToEvent(
                "turn", dobj.capNameArticle(True) + " cannot hold a liquid. "
            )
            return False
        if dobj.has_lid:
            if not dobj.is_open:
                game.addTextToEvent("turn", dobj.capNameArticle(True) + " is closed. ")
                return False
        spaceleft = dobj.liquidRoomLeft()
        liquid_contents = dobj.containsLiquid()
        if dobj.contains != {} and not liquid_contents:
            game.addTextToEvent(
                "turn", "(First attempting to empty " + iobj.lowNameArticle(True) + ")"
            )
            success = pourOutVerb.verbFunc(game, iobj)
            if not success:
                return False
        if not iobj.can_fill_from:
            game.addTextToEvent("turn", iobj.cannot_fill_from_msg)
            return False
        if liquid_contents and liquid_contents.liquid_type != iobj.liquid_type:
            success = liquid_contents.mixWith(game, liquid_contents, dobj)
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
        container = iobj.getContainer()
        if iobj.infinite_well:
            game.addTextToEvent(
                "turn",
                "You fill "
                + dobj.lowNameArticle(True)
                + " with "
                + iobj.lowNameArticle()
                + ". ",
            )
        else:
            game.addTextToEvent(
                "turn",
                "You fill "
                + dobj.lowNameArticle(True)
                + " with "
                + iobj.lowNameArticle()
                + ", taking all of it. ",
            )
        return iobj.fillVessel(dobj)
    game.addTextToEvent(
        "turn", "You can't fill " + dobj.lowNameArticle(True) + " with that. "
    )
    return False


# replace default verbFunc method
fillWithVerb.verbFunc = fillWithVerbFunc

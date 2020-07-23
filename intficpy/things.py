import copy

from .vocab import nounDict
from .actor import Actor, Player
from .thing_base import Thing
from .daemons import Daemon


class Openable(Thing):
    """
    An item that can be opened.
    Inheriting from this class means that instances can be made openable
    """

    IS_OPEN_DESC_KEY = "is_open_desc"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._is_open_desc__true = "It is open. "
        self._is_open_desc__false = "It is closed. "

    @property
    def is_open_desc(self):
        """
        Describes the objects open/closed state in words
        """
        return self._is_open_desc__true if self.is_open else self._is_open_desc__false

    @property
    def is_locked_desc(self):
        if not self.lock_obj:
            return ""
        return self.lock_obj.is_locked_desc

    def makeOpen(self):
        self.is_open = True

    def makeClosed(self):
        self.is_open = False


class Unremarkable(Thing):
    """
    An item that does not need to be explicitly brought to the Player's attention
    most of the time.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invItem = False
        self.known_ix = None

    @property
    def default_desc(self):
        """
        By default, do not describe in the room description.
        """
        return ""


class Surface(Thing):
    """Class for Things that can have other Things placed on them """

    def __init__(self, name, game):
        """Sets the essential properties for a new Surface object """
        super().__init__(name)

        self._me = game.me
        self.contains_preposition = "on"
        self.contains_on = True
        self.contains_preposition_inverse = "off"

        self.canSit = False
        self.canStand = False
        self.canLie = False

        self.desc_reveal = True


# NOTE: Container duplicates a lot of code from Surface. Consider a parent class for Things with a contains property
class Container(Openable):
    """Things that can contain other Things """

    def __init__(self, name, game):
        """
        Set basic properties for the Container instance
        Takes argument name, a single noun (string)
        """
        super().__init__(name)
        self.size = 50
        self.desc_reveal = True
        self.xdesc_reveal = True
        self.contains_preposition = "in"
        self.contains_in = True
        self.contains_preposition_inverse = "out"

        self._me = game.me

    @property
    def contains_desc(self):
        """
        Describe the contents of an item
        """
        if self.has_lid and not self.is_open:
            return ""
        return super().contains_desc

    def revealContents(self):
        list_version = list(self.contains.keys())
        for key in list_version:
            for item in self.contains[key]:
                nested = item.getNested()
                next_loc = self.location
                while next_loc:
                    for x in nested:
                        if x.ix in next_loc.sub_contains:
                            next_loc.sub_contains[x.ix].append(x)
                        else:
                            next_loc.sub_contains[x.ix] = [x]
                    if item.ix in next_loc.sub_contains:
                        next_loc.sub_contains[item.ix].append(item)
                    else:
                        next_loc.sub_contains[item.ix] = [item]
                    next_loc = next_loc.location

    def hideContents(self):
        self.desc_reveal = True
        self.xdesc_reveal = True

    def setLock(self, lock_obj):
        if not isinstance(lock_obj, Lock):
            raise ValueError("Cannot set lock_obj for {self.verbose_name}: not a Lock")

        if not self.has_lid:
            raise ValueError(f"Cannot set lock_obj for {self.verbose_name}: no lid")

        if lock_obj.parent_obj:
            raise ValueError(
                f"Cannot set lock_obj for {self.verbose_name}: lock_obj.parent already set"
            )

        self.lock_obj = lock_obj
        lock_obj.parent_obj = self
        if self.location:
            self.location.addThing(lock_obj)
        lock_obj.setAdjectives(lock_obj.adjectives + self.adjectives + [self.name])
        self.state_descriptors.append(lock_obj.IS_LOCKED_DESC_KEY)

    def containsLiquid(self):
        """Returns  the first Liquid found in the Container or None"""
        for key in self.contains:
            for item in self.contains[key]:
                if isinstance(item, Liquid):
                    return item
        return None

    def liquidRoomLeft(self):
        """Returns the portion of the Container's size not taken up by a liquid"""
        liquid = self.containsLiquid()
        if not liquid:
            return self.size
        return self.size - liquid.size

    def giveLid(self):
        self.has_lid = True
        self.is_open = False
        if not self.IS_OPEN_DESC_KEY in self.state_descriptors:
            self.state_descriptors.append(self.IS_OPEN_DESC_KEY)

    def makeOpen(self):
        super().makeOpen()
        self.revealContents()

    def makeClosed(self):
        super().makeClosed()
        self.hideContents()


# NOTE: May not be necessary as a distinct class. Consider just using the wearable property.
class Clothing(Thing):
    """Class for Things that can be worn """

    # all clothing is wearable
    wearable = True
    # uses __init__ from Thing


class LightSource(Thing):
    """Class for Things that are light sources """

    IS_LIT_DESC_KEY = "is_lit_desc"

    def __init__(self, name):
        """
        Set basic properties for the LightSource instance
        Takes argument name, a single noun (string)
        """
        super().__init__(name)

        # LightSource properties
        self.is_lit = False
        self.player_can_light = True
        self.player_can_extinguish = True
        self.consumable = False
        self.turns_left = 20
        self.room_lit_msg = "The " + self.name + " lights your way. "
        self.light_msg = "You light the " + self.name + ". "
        self.already_lit_msg = "The " + self.name + " is already lit. "
        self.extinguish_msg = "You extinguish the " + self.name + ". "
        self.already_extinguished_msg = "The " + self.name + " is not lit. "
        self.cannot_light_msg = "You cannot light the " + self.name + ". "
        self.cannot_extinguish_msg = "You cannot extinguish the " + self.name + ". "
        self.cannot_light_expired_msg = "The " + self.name + " is used up. "
        self.extinguishing_expired_msg = (
            "The light of the " + self.name + " dims to nothing. "
        )
        self.expiry_warning = "The " + self.name + " flickers. "
        self.lit_desc = "It is currently lit. "
        self.not_lit_desc = "It is currently not lit. "
        self.expired_desc = "It is burnt out. "

        self.consumeLightSourceDaemon = Daemon(self.consumeLightSourceDaemonFunc)

        self.state_descriptors.append(self.IS_LIT_DESC_KEY)

    @property
    def is_lit_desc(self):
        """
        Describe whether the light source is lit, not lit, or burnt out
        """
        if turns_left == 0:
            return self.expired_desc
        return self.lit_desc if self.is_lit else self.not_lit_desc

    def light(self, game):
        if self.is_lit:
            game.addTextToEvent("turn", self.already_lit_msg)
            return True
        elif self.consumable and not self.turns_left:
            game.addTextToEvent("turn", self.cannot_light_expired_msg)
            return False

        if self.consumable:
            game.daemons.add(self.consumeLightSourceDaemon)

        self.is_lit = True
        return True

    def extinguish(self, game):
        if not self.is_lit:
            game.addTextToEvent("turn", self.already_extinguished_msg)
            return True

        if self.consumable and self.consumeLightSourceDaemon in game.daemons.active:
            game.daemons.remove(self.consumeLightSourceDaemon)
        self.is_lit = False

    def consumeLightSourceDaemonFunc(self, game):
        """
        Runs every turn while a consumable light source is active, to keep track of
        time left.
        """
        from .verb import helpVerb, helpVerbVerb, aboutVerb

        if not (
            game.parser.previous_command.verb == helpVerb
            or game.parser.previous_command.verb == helpVerbVerb
            or game.parser.previous_command.verb == aboutVerb
            or game.parser.previous_command.ambiguous
            or game.parser.previous_command.err
        ):
            self.turns_left = self.turns_left - 1
            if self.turns_left == 0:
                if game.me.getOutermostLocation() == self.getOutermostLocation():
                    game.addTextToEvent("turn", self.extinguishing_expired_msg)
                self.is_lit = False

                if self.consumeLightSourceDaemon in game.daemons.active:
                    game.daemons.remove(self.consumeLightSourceDaemon)
            elif game.me.getOutermostLocation() == self.getOutermostLocation():
                if self.turns_left < 5:
                    game.addTextToEvent(
                        "turn",
                        self.expiry_warning + str(self.turns_left) + " turns left. ",
                    )
                elif (self.turns_left % 5) == 0:
                    game.addTextToEvent(
                        "turn",
                        self.expiry_warning + str(self.turns_left) + " turns left. ",
                    )


class AbstractClimbable(Thing):
    """Represents one end of a staircase or ladder.
	Creators should generally use a LadderConnector or StaircaseConnector (travel.py) rather than directly creating AbstractClimbable instances. """

    def __init__(self, name):
        """Sets essential properties for the AbstractClimbable instance """
        super().__init__(name)
        self.invItem = False


class Door(Openable):
    """
    Represents one side of a door. Always define with a twin, and set a direction.
    Can be open or closed.
    Creators should generally use DoorConnectors (travel.py) rather than defining Doors
    directly.
    """

    def __init__(self, name):
        """Sets essential properties for the Door instance """
        super().__init__(name)
        self.invItem = False

        self.state_descriptors.append(self.IS_OPEN_DESC_KEY)

    def makeOpen(self):
        super().makeOpen()

        if self.twin:
            if not self.twin.is_open:
                self.twin.makeOpen()

    def makeClosed(self):
        super().makeClosed()

        if self.twin:
            if not self.twin.is_open:
                self.twin.makeClosed()


class Key(Thing):
    """Class for keys """

    def __init__(self, name="key"):
        """Sets essential properties for the Thing instance """
        super().__init__(name)


class Lock(Thing):
    """Lock is the class for lock items in the game  """

    IS_LOCKED_DESC_KEY = "is_locked_desc"

    def __init__(self, is_locked, key_obj, name="lock"):
        """Sets essential properties for the Lock instance """
        super().__init__(name)

        self.is_locked = is_locked
        self.key_obj = key_obj
        self.invItem = False

        self._is_locked_desc__true = "It is currently locked. "
        self._is_locked_desc__flase = "It is currently unlocked. "
        self.state_descriptors.append(self.IS_LOCKED_DESC_KEY)

    @property
    def is_locked_desc(self):
        """
        Descripe the item's locked/unlocked state in words
        """
        return (
            self._is_locked_desc__true
            if self.is_locked
            else self._is_locked_desc__false
        )

    def makeUnlocked(self):
        self.is_locked = False

        if self.twin:
            if self.twin.is_locked:
                self.twin.makeUnlocked()

    def makeLocked(self):
        self.is_locked = True

        if self.twin:
            if not self.twin.is_locked:
                self.twin.makeLocked()


class Abstract(Thing):
    """Class for abstract game items with no location, such as ideas"""

    def __init__(self, name):
        super().__init__(name)


class UnderSpace(Thing):
    """Things that can have other Things underneath """

    def __init__(self, name, game):
        super().__init__(name)

        self._me = game.me
        self.size = 50
        self.contains_preposition = "under"
        self.contains_under = True
        self.contains_preposition_inverse = "out"

    @property
    def component_desc(self):
        """
        How the item is described when it is a component of another item

        UnderSpaces that are a component of another item are only described
        if they are given an explicit description.

        This avoids descriptions like, "There is a dresser. Under the dresser is here."
        being produced by default.
        """
        return self.desc if self.description else ""

    def revealUnder(self):
        self.revealed = True
        for key in self.contains:
            next_loc = self.location
            for item in self.contains[key]:
                contentshidden = False
                if isinstance(item, Container):
                    if item.has_lid:
                        if item.is_open == False:
                            contentshidden = True
                while next_loc:
                    if not contentshidden:
                        nested = item.getNested()
                        if not isinstance(item, Actor):
                            for t in nested:
                                if t.ix in next_loc.sub_contains:
                                    if not t in next_loc.sub_contains[t.ix]:
                                        next_loc.sub_contains[t.ix].append(t)
                                else:
                                    next_loc.sub_contains[t.ix] = [t]
                    if item.ix in next_loc.sub_contains:
                        if not item in next_loc.sub_contains[item.ix]:
                            next_loc.sub_contains[item.ix].append(item)
                    else:
                        next_loc.sub_contains[item.ix] = [item]
                    next_loc = next_loc.location

    def moveContentsOut(self):
        contents = copy.copy(self.contains)
        out = ""
        list_version = list(contents.keys())
        counter = 0
        for key in contents:
            if len(contents[key]) == 1:
                out = (
                    out + contents[key][0].getArticle() + contents[key][0].verbose_name
                )
            else:
                n_things = str(len(contents[key]))
                out = out + n_things + contents[key][0].verbose_name
                counter = counter + 1
            if len(list_version) > 1:
                if key == list_version[-2]:
                    out = out + ", and "
                elif key != list_version[-1]:
                    out = out + ", "
            elif key != list_version[-1]:
                out = out + ", "
            for item in contents[key]:
                self.removeThing(item)
                self.location.addThing(item)
            counter = counter + 1
        if counter > 1:
            return [out, True]
        else:
            return [out, False]


class Transparent(Thing):
    """Transparent Things
	Set the look_through_desc property to print the same string every time look through [instance as dobj] is used
	Replace default lookThrough method for more complicated behaviour """

    def __init__(self, name):
        """Sets essential properties for the Transparent instance """
        super().__init__(name)

    def lookThrough(self, game):
        """Called when the Transparent instance is dobj for verb look through
		Creators should overwrite for more complex behaviour """
        game.addTextToEvent("turn", self.look_through_desc)


class Readable(Thing):
    """
    Readable Things
    Set the read_desc property to print the same string every time
    READ [instance as dobj] is used.

    Replace default readText method for more complicated behaviour
    """

    def __init__(self, name, text="There's nothing written here. "):
        """Sets essential properties for the Readable instance """
        super().__init__(name)

        self.read_desc = text  # the default description for the examine command

    def readText(self, game):
        """Called when the Transparent instance is dobj for verb look through
		Creators should overwrite for more complex behaviour """
        game.addTextToEvent("turn", self.read_desc)


class Book(Openable, Readable):
    """Readable that can be opened """

    def __init__(self, name, text="There's nothing written here. "):
        """Sets essential properties for the Book instance """
        super().__init__(name, text)
        self.is_open = False
        self.state_descriptors.append(self.IS_OPEN_DESC_KEY)


class Pressable(Thing):
    """
    Things that do something when pressed
    Game creators should redefine the pressThing method for the instance to trigger
    events when the PRESS/PUSH verb is used
    """

    def __init__(self, name):
        """Sets essential properties for the Pressable instance """
        super().__init__(name)

    def pressThing(self, game):
        """Game creators should redefine this method for their Pressable instances """
        game.addTextToEvent("turn", self.capNameArticle(True) + " has been pressed. ")


class Liquid(Thing):
    """
    Can fill a container where holds_liquid is True, can be poured, and can
    optionally be drunk

    Game creators should redefine the pressThing method for the instance to
    trigger events when the press/push verb is used
    """

    def __init__(self, name, liquid_type):
        """
        Sets essential properties for the Liquid instance

        The liquid_type property should be a short description
        of what the liquid is, such as "water" or "motor oil"
        This will be used to determine what liquids can be merged and mixed
        Replace the mixWith property to allow mixing of Liquids
        """
        super().__init__(name)

        self.can_drink = True
        self.can_pour_out = True
        self.can_fill_from = True
        self.infinite_well = False
        self.liquid_for_transfer = self
        self.liquid_type = liquid_type
        self.cannot_fill_from_msg = (
            "You are unable to collect any of the spilled " + name + ". "
        )
        self.cannot_pour_out_msg = "You shouldn't dump that out. "
        self.cannot_drink_msg = "You shouldn't drink that. "

        self.is_numberless = True

    def getContainer(self):
        """Redirect to the Container rather than the Liquid for certain verbs (i.e. take) """
        if isinstance(self.location, Container):
            return self.location
        else:
            return None

    def dumpLiquid(self):
        """Defines what happens when the Liquid is dumped out"""
        loc = self.getOutermostLocation()
        if not isinstance(self.location, Container) or not self.can_pour_out:
            return False
        self.location.removeThing(self)
        loc.addThing(self)
        self.describeThing(
            self.capNameArticle() + " has been spilled on the ground here. "
        )
        self.invItem = False
        self.can_fill_from = False
        return True

    def fillVessel(self, vessel):
        """Used for verbs fill from and pour into """
        vessel_liquid = vessel.containsLiquid()
        vessel_left = vessel.liquidRoomLeft()
        if vessel_liquid:
            if vessel_left == 0:
                return False
            if not self.can_fill_from:
                return False
            elif vessel_liquid.liquid_type != self.liquid_type:
                return self.mixWith(vessel_liquid)
            else:
                return False
        else:
            if self.infinite_well:
                vessel_liquid = self.liquid_for_transfer.copyThing()
                # vessel_liquid.infinite_well = False
                # vessel_liquid.size = vessel.size
                vessel.addThing(vessel_liquid)
                return True
            else:
                self.location.removeThing(self)
                vessel.addThing(self.liquid_for_transfer)
                return True

    def mixWith(self, game, base_liquid, mix_in):
        """Replace to allow mixing of specific Liquids
		Return True when a mixture is allowed, False otherwise """
        return False

    def drinkLiquid(self, game):
        """Replace for custom effects for drinking the Liquid """
        self.location.removeThing(self)
        return True


# hacky solution for reflexive pronouns (himself/herself/itself)
reflexive = Abstract("itself")
reflexive.addSynonym("himself")
reflexive.addSynonym("herself")
reflexive.addSynonym("themself")
reflexive.addSynonym("themselves")

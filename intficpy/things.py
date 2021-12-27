import copy

from .actor import Actor, Player
from .thing_base import Thing
from .daemons import Daemon


class Holder(Thing):
    """
    An item that can hold or contain another item.

    This is the base class for Surfaces, Container,
    UnderSpaces, etc.
    """

    contains_preposition = "in"

    def revealContents(self):
        self.revealed = True
        for item in self.topLevelContentsList:
            item.makeKnown(self.game.me)

    def playerAboutToAddItem(self, item, preposition, event="turn", **kwargs):
        """
        The prepartations we make when the player is about to try to add an item
        to this item. Performs any implicit actions needed to add the item.
        Returns True if the item addition is allowed, False otherwise.
        :param item: the item to attempt to add
        :type item: Thing
        :param preposition: the contains preposition the player wants to add the item with
            (in/on/etc.)
        :type preposition: str
        """
        if preposition == self.contains_preposition:
            if not item.playerAboutToMoveTo(self, event=event, **kwargs):
                return False
            return True
        return super().playerAboutToAddItem(item, preposition, event=event, **kwargs)

    def playerAddsItem(
        self, item, preposition, event="turn", success_msg=None, **kwargs
    ):
        """
        The result of a player trying to add an item to this item's contents.
        If the player is attempting to add an item "in" this item (or, in the case of
        customized contains preposition, if the the preposition matches that of this
        item), we move the item to our `contains`.

        Returns True on success, else False.

        :param item: the item to attempt to add
        :type item: Thing
        :param preposition: the contains preposition the player wants to add the item with
            (in/on/etc.)
        :type preposition: str
        """
        if success_msg:
            self.game.addTextToEvent(event, success_msg)

        return item.playerMovesTo(self, event=event, **kwargs)


class Openable(Thing):
    """
    An item that can be opened.
    Inheriting from this class means that instances can be made openable
    """

    is_open_desc__true = "It is open. "
    is_open_desc__false = "It is closed. "

    IS_OPEN_DESC_KEY = "is_open_desc"

    @property
    def is_open_desc(self):
        """
        Describes the objects open/closed state in words
        """
        return self.is_open_desc__true if self.is_open else self.is_open_desc__false

    @property
    def is_locked_desc(self):
        if not self.lock_obj:
            return ""
        return self.lock_obj.is_locked_desc

    def playerAboutToOpen(self, event="turn"):
        """
        Events run when the player is about to try to open this item.
        Returns True to allow opening, and False to deny.

        :param event: the event to print messages to
        :type event: str
        """
        if self.lock_obj and self.lock_obj.is_locked:
            self.game.addTextToEvent(event, f"{self.capNameArticle(True)} is locked. ")
            return False
        return True

    def playerOpens(self, event="turn"):
        """
        Events run when the player tries to open this item. Returns True on success,
        and False on failure.

        :param event: the event to print messages to
        :type event: str
        """
        self.game.addTextToEvent(event, f"You open {self.lowNameArticle(True)}. ")
        self.makeOpen()
        return True

    def makeOpen(self):
        self.is_open = True

    def makeClosed(self):
        self.is_open = False


class Unremarkable(Thing):
    """
    An item that does not need to be explicitly brought to the Player's attention
    most of the time.
    """

    invItem = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.known_ix = None

    @property
    def default_desc(self):
        """
        By default, do not describe in the room description.
        """
        return ""


class Surface(Holder):
    """Class for Things that can have other Things placed on them """

    contains_preposition = "on"
    contains_on = True
    contains_preposition_inverse = "off"

    can_contain_sitting_player = False
    can_contain_standing_player = False
    can_contain_lying_player = False

    desc_reveal = True


class Container(Holder, Openable):
    """Things that can contain other Things """

    holds_liquid = False

    size = 50
    desc_reveal = True
    xdesc_reveal = True
    contains_preposition = "in"
    contains_in = True
    contains_preposition_inverse = "out"
    closed_msg = "The {self.verbose_name} is closed."
    does_not_fit_msg = (
        "The {item.verbose_name} is too big to fit inside the {self.verbose_name}. "
    )

    @property
    def contains_desc(self):
        """
        Describe the contents of an item
        """
        if self.has_lid and not self.is_open:
            return ""
        return super().contains_desc

    def tryOpeningLid(self, event="turn"):
        """
        If the lid is currently closed, try to open it, returning False on failure.
        Otherwise return True

        :param event: the event name to print to
        :type event: str
        """
        if self.has_lid and not self.is_open:
            self.game.addTextToEvent(
                event, f"(First trying to open {self.lowNameArticle(True)})"
            )
            if not self.playerAboutToOpen(event=event) or not self.playerOpens(
                event=event
            ):
                return False
        return True

    def playerAboutToAddItem(self, item, preposition, event="turn", **kwargs):
        """
        The prepartations we make when the player is about to try to add an item
        to this item. Performs any implicit actions needed to add the item.
        Returns True if the item addition is allowed, False otherwise.
        :param item: the item to attempt to add
        :type item: Thing
        :param preposition: the contains preposition the player wants to add the item with
            (in/on/etc.)
        :type preposition: str
        """
        if not self.tryOpeningLid(event=event):
            return False
        if item.size > self.size:
            self.game.addTextToEvent(
                event, self.does_not_fit_msg.format(self=self, item=item)
            )
            return False
        existing_liquid = self.containsLiquid()
        if existing_liquid and not getattr(item, "liquid_type", None):
            self.game.addTextToEvent(
                event,
                f"{self.capNameArticle(True)} is already full of {existing_liquid.liquid_type}. ",
            )
            return False
        return super().playerAboutToAddItem(item, preposition, event=event, **kwargs)

    def playerAboutToRemoveItem(self, item, event="turn", **kwargs):
        """
        Actions carried out when the player is about to try and remove an item contained
        by this item.

        :param event: the event name to print to
        :type event: str
        """
        if not self.tryOpeningLid(event=event):
            return False
        return True

    def playerDumpsItems(self, event="turn", **kwargs):
        """
        The result of a player trying to dump the items.

        Returns True on success, else False.

        :param event: the event name to print to
        :type event: str
        """
        if self.has_lid and not self.is_open:
            self.game.addTextToEvent(event, self.closed_msg.format(self=self))
            return False
        return super().playerDumpsItems(event=event, **kwargs)

    def playerAboutToLookIn(self, event="turn", **kwargs):
        """
        Actions carried out when the player is about to try and look inside this item.

        :param event: the event name to print to
        :type event: str
        """
        if not self.tryOpeningLid(event=event):
            return False
        return True

    def playerLooksIn(self, event="turn", **kwargs):
        """
        The result of a player trying to look in this item.

        Returns True on success, else False.

        :param event: the event name to print to
        :type event: str
        """
        self.game.addTextToEvent(event, self.contains_desc)
        self.revealContents()
        return True

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

    def giveLid(self):
        self.has_lid = True
        self.is_open = False
        self.revealed = False
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

    def playerAboutToWear(self, event="turn", **kwargs):
        """
        Actions carried out when the player is about to wear this item

        :param event: the event name to print to
        :type event: str
        """
        return True

    def playerWears(self, event="turn", **kwargs):
        """
        The result of a player trying to wear the item.

        Returns True on success, else False.

        :param event: the event name to print to
        :type event: str
        """
        self.game.addTextToEvent(event, f"You wear {self.lowNameArticle(True)}. ")
        self.game.me.makeWearing(self)
        return True

    def playerAboutToDoff(self, event="turn", **kwargs):
        """
        Actions carried out when the player is about to doff this item

        :param event: the event name to print to
        :type event: str
        """
        return True

    def playerDoffs(self, event="turn", **kwargs):
        """
        The result of a player trying to doff the item.

        Returns True on success, else False.

        :param event: the event name to print to
        :type event: str
        """
        self.game.addTextToEvent(event, f"You take off {self.lowNameArticle(True)}. ")
        self.game.me.removeWearing(self)
        self.moveTo(self.game.me)
        return True


class LightSource(Thing):
    """Class for Things that are light sources """

    IS_LIT_DESC_KEY = "is_lit_desc"

    is_lit = False
    player_can_light = True
    player_can_extinguish = True
    consumable = False
    turns_left = 20

    room_lit_msg = None
    light_msg = None
    already_lit_msg = None
    extinguish_msg = None
    already_extinguished_msg = None
    cannot_light_msg = None
    cannot_extinguish_msg = None
    cannot_light_expired_msg = None
    extinguishing_expired_msg = None
    expiry_warning = None
    lit_desc = "It is currently lit. "
    not_lit_desc = "It is currently not lit. "
    expired_desc = "It is burnt out. "

    def __init__(self, game, name):
        """
        Set basic properties for the LightSource instance
        Takes argument name, a single noun (string)
        """
        super().__init__(game, name)

        # LightSource properties

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

        self.consumeLightSourceDaemon = Daemon(
            self.game, self.consumeLightSourceDaemonFunc
        )

        self.state_descriptors.append(self.IS_LIT_DESC_KEY)

    @property
    def is_lit_desc(self):
        """
        Describe whether the light source is lit, not lit, or burnt out
        """
        if not self.turns_left:
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
        return True

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

    invItem = False


class Door(Openable):
    """
    Represents one side of a door. Always define with a twin, and set a direction.
    Can be open or closed.
    Creators should generally use DoorConnectors (travel.py) rather than defining Doors
    directly.
    """

    invItem = False

    def __init__(self, game, name):
        """Sets essential properties for the Door instance """
        super().__init__(game, name)

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

    def __init__(self, game, name="key"):
        """Sets essential properties for the Thing instance """
        super().__init__(game, name)


class Lock(Thing):
    """Lock is the class for lock items in the game  """

    IS_LOCKED_DESC_KEY = "is_locked_desc"

    invItem = False

    is_locked = False
    key_obj = None

    is_locked_desc__true = "It is currently locked. "
    is_locked_desc__false = "It is currently unlocked. "

    def __init__(self, game, is_locked, key_obj, name="lock"):
        """Sets essential properties for the Lock instance """
        super().__init__(game, name)

        self.is_locked = is_locked
        self.key_obj = key_obj
        self.state_descriptors.append(self.IS_LOCKED_DESC_KEY)

    @property
    def is_locked_desc(self):
        """
        Descripe the item's locked/unlocked state in words
        """
        return (
            self.is_locked_desc__true if self.is_locked else self.is_locked_desc__false
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

    pass


class UnderSpace(Holder):
    """Things that can have other Things underneath """

    size = 50
    contains_preposition = "under"
    contains_under = True
    contains_preposition_inverse = "out"
    revealed = False

    does_not_fit_msg = (
        "The {item.verbose_name} is too big to fit under the {self.verbose_name}. "
    )

    @property
    def component_desc(self):
        """
        How the item is described when it is a component of another item

        UnderSpaces that are a component of another item are only described
        if they are given an explicit description.

        This avoids descriptions like, "There is a dresser. Under the dresser is here."
        being produced by default.
        """
        return self.desc if self.description is not None else ""

    def revealUnder(self):
        super().revealContents()

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

    def playerLifts(self, event="turn", **kwargs):
        """
        The UnderSpace has been lifted up by the player, revealing its contents.
        :param event: the event name to print to
        :type event: str
        """
        msg, plural = self.moveContentsOut()
        if plural:
            msg = msg.capitalize() + " are revealed. "
        else:
            msg = msg.capitalize() + " is revealed. "
        self.game.addTextToEvent(event, msg)
        return True

    def playerTakes(self, event="turn", **kwargs):
        """
        The result of the player taking this item.

        :param event: the event name to print to
        :type event: str
        """
        success = super().playerTakes(event=event)
        if not success:
            return False
        self.playerLifts(event=event)
        return True

    def playerTakesParentObject(self, event="turn", **kwargs):
        """
        The result of the player taking the composite parent of this item.
        :param event: the event name to print to
        :type event: str
        """
        success = super().playerTakesParentObject(event=event)
        if not success:
            return False
        self.playerLifts(event=event)
        return True

    def playerAboutToAddItem(self, item, preposition, event="turn", **kwargs):
        """
        The prepartations we make when the player is about to try to add an item
        to this item. Performs any implicit actions needed to add the item.
        Returns True if the item addition is allowed, False otherwise.
        :param item: the item to attempt to add
        :type item: Thing
        :param preposition: the contains preposition the player wants to add the item with
            (in/on/etc.)
        :type preposition: str
        """
        if item.size > self.size:
            self.game.addTextToEvent(
                event, self.does_not_fit_msg.format(self=self, item=item)
            )
            return False
        return super().playerAboutToAddItem(item, preposition, event=event, **kwargs)

    def playerLooksUnder(self, event="turn", **kwargs):
        """
        The result of the player trying to look under this item

        :param event: the key of the event to print text to
        :type event: str
        :rtype: bool
        """
        self.revealUnder()
        if len(self.contains):
            self.game.addTextToEvent(event, self.contains_desc)
        else:
            self.game.addTextToEvent(
                event,
                f"There is nothing {self.contains_preposition} {self.lowNameArticle(True)}. ",
            )
        return True


class Transparent(Thing):
    """Transparent Things
	Set the look_through_desc property to print the same string every time look through [instance as dobj] is used
	Replace default lookThrough method for more complicated behaviour """

    look_through_desc = "Looking through reveals nothing in particular. "

    def playerLooksThrough(self, **kwargs):
        return self.lookThrough(self.game)

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

    read_desc = "There's nothing written here. "

    def __init__(self, game, name, text="There's nothing written here. "):
        """Sets essential properties for the Readable instance """
        super().__init__(game, name)

        self.read_desc = text  # the default description for the examine command

    def playerAboutToRead(self, event="turn"):
        """
        What happens before the player tries to read this?

        :param event: the key of the event to print text to
        :type event: str
        :rtype: bool
        """
        return True

    def playerReads(self, event="turn", **kwargs):
        """
        The result of the player trying to read this item

        :param event: the key of the event to print text to
        :type event: str
        :rtype: bool
        """
        self.readText(self.game)
        return True

    def readText(self, game):
        """Called when the Transparent instance is dobj for verb look through
		Creators should overwrite for more complex behaviour """
        game.addTextToEvent("turn", self.read_desc)


class Book(Openable, Readable):
    """Readable that can be opened """

    is_open = False

    def __init__(self, game, name, text="There's nothing written here. "):
        """Sets essential properties for the Book instance """
        super().__init__(game, name, text)
        self.state_descriptors.append(self.IS_OPEN_DESC_KEY)

    def playerAboutToRead(self, event="turn"):
        """
        What happens before the player tries to read this?
        (In this case, the player tries to open the book first)

        :param event: the key of the event to print text to
        :type event: str
        :rtype: bool
        """
        if not self.is_open:
            if not self.playerAboutToOpen(event=event) or not self.playerOpens(
                event=event
            ):
                return False
        return True


class Pressable(Thing):
    """
    Things that do something when pressed
    Game creators should redefine the pressThing method for the instance to trigger
    events when the PRESS/PUSH verb is used
    """

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

    liquid_type = None
    liquid_for_transfer = None
    can_drink = True
    can_pour_out = True
    can_fill_from = True
    infinite_well = False
    cannot_pour_out_msg = "You shouldn't dump that out. "
    cannot_drink_msg = "You shouldn't drink that. "
    cannot_fill_from_msg = None
    cannot_take_no_container_msg = None
    mix_with_liquid_type_allowed = None

    is_numberless = True

    def __init__(self, game, name, liquid_type):
        """
        Sets essential properties for the Liquid instance

        The liquid_type property should be a short description
        of what the liquid is, such as "water" or "motor oil"
        This will be used to determine what liquids can be merged and mixed
        Replace the mixWith property to allow mixing of Liquids
        """
        super().__init__(game, name)
        self.liquid_for_transfer = self
        self.liquid_type = liquid_type
        self.cannot_fill_from_msg = (
            "You are unable to collect any of the spilled " + name + ". "
        )
        self.cannot_take_no_container_msg = (
            "You are unable to collect any of the spilled " + name + ". "
        )
        self.mix_with_liquid_type_allowed = []

    def playerAboutToMoveTo(self, item, event="turn", **kwargs):
        """
        The preparations we make when the player tries to move this item to another item.
        Returns True to allow the moveTo, else False.

        :param item: the item the player is trying to add this Thing into
        :type item: Thing
        :rtype: bool
        """
        if not getattr(item, "holds_liquid", None):
            self.game.addTextToEvent(
                event, f"{item.capNameArticle(True)} cannot hold a liquid. "
            )
            return False

        existing_liquid = (
            item if getattr(item, "liquid_type", None) else item.containsLiquid()
        )

        if existing_liquid:
            if (
                existing_liquid.liquid_type not in self.mix_with_liquid_type_allowed
                and (
                    not existing_liquid.liquid_type == self.liquid_type
                    or not existing_liquid.infinite_well
                )
            ):
                self.game.addTextToEvent(
                    event,
                    f"There is already {existing_liquid.liquid_type} in {item.lowNameArticle(True)}. ",
                )
                return False

        elif item.contains:
            self.game.addTextToEvent(
                event,
                text=(
                    f"(First trying to dump out {item.lowNameArticle(True)} to make room for "
                    f"{self.lowNameArticle(True)})"
                ),
            )
            if not item.playerDumpsItems(
                event=event, success_msg=f"You dump out {item.lowNameArticle(True)}. ",
            ):
                return False

        return super().playerAboutToMoveTo(item, event=event, **kwargs)

    def playerMovesTo(self, item, event="turn", **kwargs):
        """
        The result of a player trying to add this item to some other item's contains.
        Returns True if this can be done, otherwise, prints a rejection message for
        the player, and returns False.

        :param item: the item the player is trying to add this Thing into
        :type item: Thing
        :rtype: bool
        """
        existing_liquid = (
            item if getattr(item, "liquid_type", None) else item.containsLiquid()
        )

        if (
            existing_liquid
            and existing_liquid.liquid_type == self.liquid_type
            and existing_liquid.infinite_well
        ):
            self.location.removeThing(self)
            return True

        if existing_liquid:
            success = self.mixWith(self.game, existing_liquid, self,)
            return success

        return super().playerMovesTo(item, event=event, **kwargs)

    def playerDumpsItems(self, event="turn", **kwargs):
        """
        The result of a player trying to dump the items.

        Returns True on success, else False.

        :param into_location: the location to dump items into
        :type into_location: Thing
        """
        container = self.getContainer()
        if not container:
            self.game.addTextToEvent(event, self.cannot_take_no_container_msg)
            return False
        return container.playerDumpsItems(event=event, **kwargs)

    def playerAboutToTake(self, event="turn", **kwargs):
        """
        The result of the player taking this item.

        :param event: the event name to print to
        :type event: str
        """
        container = self.getContainer()
        if not container:
            self.game.addTextToEvent(event, self.cannot_take_no_container_msg)
            return False
        return container.playerAboutToTake(event=event)

    def playerTakes(self, event="turn", **kwargs):
        """
        The result of the player taking this item.

        :param event: the event name to print to
        :type event: str
        """
        container = self.getContainer()
        if not container:
            return False
        return container.playerTakes(event=event)

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

    def mixWith(self, game, base_liquid, mix_in, event="turn"):
        """Replace to allow mixing of specific Liquids
        Return True when a mixture is allowed, False otherwise """
        return False

    def drinkLiquid(self, game):
        """Replace for custom effects for drinking the Liquid """
        self.location.removeThing(self)
        return True

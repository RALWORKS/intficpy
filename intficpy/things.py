import copy

from .vocab import nounDict
from .actor import Actor, Player
from .thing_base import Thing
from .daemons import Daemon


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

    def containsListUpdate(self, update_desc=True, update_xdesc=True):
        """Update description of contents
		Called when a Thing is added or removed """
        onlist = " On the " + self.name + " is "
        if update_desc:
            self.compositeBaseDesc()
        if update_xdesc:
            self.compositeBasexDesc()
        # iterate through contents, appending the verbose_name of each to onlist
        list_version = list(self.contains.keys())
        player_here = False
        for key in list_version:
            for item in self.contains[key]:
                if isinstance(item, Player):
                    list_version.remove(key)
                    player_here = True
                elif item.parent_obj:
                    list_version.remove(key)
        for key in list_version:
            if len(self.contains[key]) > 1:
                onlist = (
                    onlist + str(len(things)) + " " + self.contains[key][0].getPlural()
                )
            else:
                onlist = (
                    onlist
                    + self.contains[key][0].getArticle()
                    + self.contains[key][0].verbose_name
                )
            if key is list_version[-1]:
                onlist = onlist + "."
            elif key is list_version[-2]:
                onlist = onlist + " and "
            else:
                onlist = onlist + ", "
            if key not in self._me.knows_about:
                self._me.knows_about.append(key)
        # if contains is empty, there should be no onlist
        # TODO: consider rewriting this logic to avoid contructing an empty onlist, then deleting it
        if len(list_version) == 0:
            onlist = ""
        if player_here:
            if onlist != "":
                onlist = onlist + "<br>"
            onlist = (
                onlist + "You are on " + self.getArticle(True) + self.verbose_name + "."
            )
        # append onlist to description
        if self.is_composite:
            if self.children_desc:
                self.desc = self.desc + self.children_desc
                self.xdesc = self.xdesc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.xdesc = self.xdesc + item.desc
                    self.desc = self.desc + item.desc
            if self.desc_reveal and update_desc:
                self.desc = self.desc + onlist
            if update_xdesc:
                self.xdesc = self.xdesc + onlist
        else:
            if self.desc_reveal and update_desc:
                self.desc = self.base_desc + onlist
            if update_xdesc:
                self.xdesc = self.base_xdesc + onlist
        self.contains_desc = onlist

    def compositeBaseDesc(self):
        if self.is_composite:
            if self.children_desc:
                self.desc = self.base_desc + self.children_desc
            else:
                self.desc = self.base_desc
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        else:
            self.desc = self.base_desc

    def compositeBasexDesc(self):
        if self.is_composite:
            if self.children_desc:
                self.xdesc = self.xdesc + self.children_desc
            else:
                self.xdesc = self.base_xdesc
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        else:
            self.xdesc = self.base_xdesc

    def describeThing(self, description):
        self.base_desc = description
        if self.is_composite:
            if self.children_desc:
                self.desc = self.base_desc + self.children_desc
            else:
                self.desc = self.base_desc
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        self.containsListUpdate()

    def xdescribeThing(self, description):
        self.base_xdesc = description
        if self.is_composite:
            if self.children_desc:
                self.xdesc = self.xdesc + self.children_desc
            else:
                self.xdesc = self.base_xdesc
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        self.containsListUpdate()

    def addThing(self, item):
        super().addThing(item)
        self.containsListUpdate()

    def removeThing(self, item):
        super().removeThing(item)
        self.containsListUpdate()


# NOTE: Container duplicates a lot of code from Surface. Consider a parent class for Things with a contains property
class Container(Thing):
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

    def updateDesc(self):
        self.containsListUpdate(True, True)

    def containsListUpdate(self, update_desc=True, update_xdesc=True):
        """Update description for addition/removal of items from the Container instance """
        from .actor import Player

        # desc = self.base_desc
        # xdesc = self.base_xdesc
        if update_desc:
            self.compositeBaseDesc()
        if update_xdesc:
            self.compositeBasexDesc()
        desc = self.desc
        xdesc = self.xdesc
        if self.has_lid:
            desc = desc + self.state_desc
            xdesc = xdesc + self.state_desc
            if not self.is_open:
                self.desc = desc
                self.xdesc = xdesc + self.lock_desc
                self.contains_desc = (
                    "You cannot see inside "
                    + self.getArticle(True)
                    + self.verbose_name
                    + " as it is closed."
                )
                return False
        inlist = " In the " + self.name + " is "
        # iterate through contents, appending the verbose_name of each to onlist
        list_version = list(self.contains.keys())
        player_here = False
        for key in list_version:
            for item in self.contains[key]:
                if isinstance(item, Player):
                    list_version.remove(key)
                    player_here = True
                elif item.parent_obj:
                    list_version.remove(key)
        for key in list_version:
            if len(self.contains[key]) > 1:
                inlist = (
                    inlist + str(len(things)) + " " + self.contains[key][0].verbose_name
                )
            else:
                inlist = (
                    inlist
                    + self.contains[key][0].getArticle()
                    + self.contains[key][0].verbose_name
                )
            if key is list_version[-1]:
                inlist = inlist + "."
            elif key is list_version[-2]:
                inlist = inlist + " and "
            else:
                inlist = inlist + ", "
            if key not in self._me.knows_about:
                self._me.knows_about.append(key)
        # remove the empty inlist in the case of no contents
        # TODO: consider rewriting this logic to avoid contructing an empty inlist, then deleting it
        if len(list_version) == 0:
            inlist = ""
        if player_here:
            if inlist != "":
                inlist = inlist + "<br>"
            inlist = (
                inlist + "You are in " + self.getArticle(True) + self.verbose_name + "."
            )
        # update descriptions
        if self.is_composite:
            if self.children_desc:
                self.desc = self.base_desc + self.children_desc
                self.xdesc = self.base_xdesc + self.children_desc
            else:
                self.xdesc = self.base_xdesc
                self.desc = self.base_desc
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.xdesc = self.xdesc + item.desc
                    self.desc = self.desc + item.desc
            if update_desc and self.desc_reveal:
                self.desc = self.desc + inlist
            if update_xdesc and self.xdesc_reveal:
                self.xdesc = self.xdesc + inlist
        else:
            if update_desc and self.desc_reveal:
                self.desc = self.desc + inlist
            if update_xdesc and self.xdesc_reveal:
                self.xdesc = self.xdesc + self.lock_desc + inlist
        self.contains_desc = inlist
        return True

    def compositeBaseDesc(self):
        if self.is_composite:
            if self.children_desc:
                self.desc = self.base_desc + self.children_desc
            else:
                self.desc = self.base_desc
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        else:
            self.desc = self.base_desc

    def compositeBasexDesc(self):
        if self.is_composite:
            if self.children_desc:
                self.xdesc = self.xdesc + self.children_desc
            else:
                self.xdesc = self.base_xdesc
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        else:
            self.xdesc = self.base_xdesc

    def addThing(self, item):
        super().addThing(item)
        self.containsListUpdate()

    def removeThing(self, item):
        super().removeThing(item)
        self.containsListUpdate()

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
        list_version = list(self.contains.keys())
        for key in list_version:
            for item in self.contains[key]:
                nested = item.getNested()
                next_loc = self.location
                while next_loc:
                    for x in nested:
                        if x.ix in next_loc.sub_contains:
                            next_loc.sub_contains[x.ix].remove(x)
                            if next_loc.sub_contains[x.ix] == []:
                                del next_loc.sub_contains[x.ix]
                    if item.ix in next_loc.sub_contains:
                        next_loc.sub_contains[item.ix].remove(item)
                        if next_loc.sub_contains[item.ix] == []:
                            del next_loc.sub_contains[item.ix]
                    next_loc = next_loc.location

    def setLock(self, lock_obj):
        if isinstance(lock_obj, Lock) and self.has_lid:
            if not lock_obj.parent_obj:
                self.lock_obj = lock_obj
                lock_obj.parent_obj = self
                if self.location:
                    self.location.addThing(lock_obj)
                lock_obj.setAdjectives(
                    lock_obj.adjectives + self.adjectives + [self.name]
                )
                if lock_obj.is_locked:
                    self.lock_desc = " It is locked. "
                else:
                    self.lock_desc = " It is unlocked. "
                lock_obj.describeThing("")
                lock_obj.xdescribeThing(
                    "You notice nothing remarkable about "
                    + lock_obj.getArticle(True)
                    + lock_obj.verbose_name
                    + ". "
                )
                self.containsListUpdate()
            else:
                print(
                    "Cannot set lock_obj for "
                    + self.verbose_name
                    + ": lock_obj.parent already set "
                )
        elif not self.has_lid:
            print("Cannot set lock_obj for " + self.verbose_name + ": no lid ")
        else:
            print("Cannot set lock_obj for " + self.verbose_name + ": not a Lock ")

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

    def describeThing(self, description):
        self.base_desc = description
        self.desc = self.base_desc + self.state_desc
        if self.is_composite:
            if self.children_desc:
                self.desc = self.desc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        self.containsListUpdate()

    def xdescribeThing(self, description):
        self.base_xdesc = description
        self.xdesc = self.base_xdesc + self.state_desc + self.lock_desc
        if self.is_composite:
            if self.children_desc:
                self.xdesc = self.xdesc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.xdesc = self.xdesc + item.desc
        self.containsListUpdate()

    def giveLid(self):
        self.has_lid = True
        self.is_open = False
        self.state_desc = " It is currently closed. "
        self.containsListUpdate()

    def makeOpen(self):
        self.is_open = True
        self.state_desc = " It is currently open. "
        self.containsListUpdate()
        self.revealContents()
        if self.parent_obj:
            self.parent_obj.describeThing(self.parent_obj.base_desc)
            self.parent_obj.xdescribeThing(self.parent_obj.base_xdesc)

    def makeClosed(self):
        self.is_open = False
        self.state_desc = " It is currently closed. "
        self.containsListUpdate()
        self.hideContents()
        if self.parent_obj:
            self.parent_obj.describeThing(self.parent_obj.base_desc)
            self.parent_obj.xdescribeThing(self.parent_obj.base_xdesc)


# NOTE: May not be necessary as a distinct class. Consider just using the wearable property.
class Clothing(Thing):
    """Class for Things that can be worn """

    # all clothing is wearable
    wearable = True
    # uses __init__ from Thing


class LightSource(Thing):
    """Class for Things that are light sources """

    def __init__(self, name):
        """
        Set basic properties for the LightSource instance
        Takes argument name, a single noun (string)
        """
        super().__init__(name)

        self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
        self.base_xdesc = self.base_desc
        self.desc = self.base_desc + "It is currently not lit. "
        self.xdesc = self.base_xdesc + "It is currently not lit. "

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

    def describeThing(self, description):
        self.base_desc = description
        if self.is_lit:
            self.desc = self.base_desc + self.lit_desc
        elif self.consumable and not self.turns_left:
            self.desc = self.base_desc + self.expired_desc
        else:
            self.desc = self.base_desc + self.not_lit_desc

    def xdescribeThing(self, description):
        self.base_xdesc = description
        if self.is_lit:
            self.xdesc = self.base_xdesc + self.lit_desc
        elif self.consumable and not self.turns_left:
            self.xdesc = self.base_xdesc + self.expired_desc
        else:
            self.xdesc = self.base_xdesc + self.not_lit_desc

    def light(self, game):
        if self.is_lit:
            game.addTextToEvent("turn", self.already_lit_msg)
            return True
        elif self.consumable and not self.turns_left:
            game.addTextToEvent("turn", self.cannot_light_expired_msg)
            return False
        else:
            if self.consumable:
                game.daemons.add(self.consumeLightSourceDaemon)

            self.is_lit = True
            self.desc = self.base_desc + self.lit_desc
            self.xdesc = self.base_xdesc + self.lit_desc

    def extinguish(self, game):
        if not self.is_lit:
            game.addTextToEvent("turn", self.already_extinguished_msg)
            return True
        else:
            if self.consumable and self.consumeLightSourceDaemon in game.daemons.active:
                game.daemons.remove(self.consumeLightSourceDaemon)
            self.is_lit = False
            self.desc = self.base_desc + self.not_lit_desc
            self.xdesc = self.base_xdesc + self.not_lit_desc

    def consumeLightSourceDaemonFunc(self, game):
        """Runs every turn while a consumable light source is active, to keep track of time left. """
        from .verb import helpVerb, helpVerbVerb, aboutVerb

        if not (
            game.lastTurn.verb == helpVerb
            or game.lastTurn.verb == helpVerbVerb
            or game.lastTurn.verb == aboutVerb
            or game.lastTurn.ambiguous
            or game.lastTurn.err
        ):
            self.turns_left = self.turns_left - 1
            if self.turns_left == 0:
                if game.me.getOutermostLocation() == self.getOutermostLocation():
                    game.addTextToEvent("turn", self.extinguishing_expired_msg)
                self.is_lit = False
                self.desc = self.base_desc + self.expired_desc
                self.xdesc = self.base_xdesc + self.expired_desc
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


class Door(Thing):
    """Represents one side of a door. Always define with a twin, and set a direction. Can be open or closed.
	Creators should generally use DoorConnectors (travel.py) rather than defining Doors  directly. """

    def __init__(self, name):
        """Sets essential properties for the Door instance """
        super().__init__(name)
        self.invItem = False

        # TODO: create instance properties closed_desc and open_desc - possibly on Thing
        self.state_desc = "It is currently closed. "

    def makeOpen(self):
        self.is_open = True
        self.state_desc = "It is currently open. "
        self.desc = self.base_desc + self.state_desc
        self.xdesc = self.base_xdesc + self.state_desc
        if self.twin:
            if not self.twin.is_open:
                self.twin.makeOpen()
        if self.parent_obj:
            self.parent_obj.describeThing(self.parent_obj.base_desc)
            self.parent_obj.xdescribeThing(self.parent_obj.base_xdesc)

    def makeClosed(self):
        self.is_open = False
        self.state_desc = "It is currently closed. "
        self.desc = self.base_desc + self.state_desc
        self.xdesc = self.base_xdesc + self.state_desc
        if self.twin:
            if self.twin.is_open:
                self.twin.makeClosed()
        if self.parent_obj:
            self.parent_obj.describeThing(self.parent_obj.base_desc)
            self.parent_obj.xdescribeThing(self.parent_obj.base_xdesc)

    def describeThing(self, description):
        self.base_desc = description
        self.desc = description + self.state_desc
        if self.is_composite:
            if self.children_desc:
                self.desc = self.desc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc

    def xdescribeThing(self, description):
        self.base_xdesc = description
        self.xdesc = description + self.state_desc + self.lock_desc
        if self.is_composite:
            if self.children_desc:
                self.xdesc = self.xdesc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.xdesc = self.xdesc + item.desc

    def updateDesc(self):
        self.xdesc = self.base_xdesc + self.state_desc + self.lock_desc
        self.desc = self.base_desc + self.state_desc
        if self.is_composite:
            if self.children_desc:
                self.desc = self.desc + self.children_desc
                self.xdesc = self.xdesc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
                    self.xdesc = self.xdesc + item.desc


class Key(Thing):
    """Class for keys """

    def __init__(self, name="key"):
        """Sets essential properties for the Thing instance """
        super().__init__(name)


class Lock(Thing):
    """Lock is the class for lock items in the game  """

    def __init__(self, is_locked, key_obj, name="lock"):
        """Sets essential properties for the Lock instance """
        super().__init__(name)

        self.is_locked = is_locked
        self.key_obj = key_obj

        # TODO: extract strings into instance properties
        if self.is_locked:
            self.state_desc = " It is currently locked. "
        else:
            self.state_desc = "It is currently unlocked. "

    def makeUnlocked(self):
        self.is_locked = False
        self.state_desc = "It is currently unlocked. "
        self.xdesc = self.base_xdesc + self.state_desc
        if self.parent_obj:
            self.parent_obj.lock_desc = " It is unlocked. "
            self.parent_obj.updateDesc()
        if self.twin:
            if self.twin.is_locked:
                self.twin.makeUnlocked()

    def makeLocked(self):
        self.is_locked = True
        self.state_desc = "It is currently locked. "
        self.xdesc = self.base_xdesc + self.state_desc
        if self.parent_obj:
            self.parent_obj.lock_desc = " It is locked. "
            self.parent_obj.updateDesc()
        if self.twin:
            if not self.twin.is_locked:
                self.twin.makeLocked()

    def describeThing(self, description):
        self.base_desc = description
        self.desc = self.base_desc
        if self.is_composite:
            if self.children_desc:
                self.desc = self.desc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc

    def xdescribeThing(self, description):
        self.base_xdesc = description
        self.xdesc = self.base_xdesc + self.state_desc
        if self.is_composite:
            if self.children_desc:
                self.xdesc = self.xdesc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.xdesc = self.xdesc + item.desc


class Abstract(Thing):
    """Class for abstract game items with no location, such as ideas"""

    def __init__(self, name):
        super().__init__(name)


class UnderSpace(Thing):
    """Things that can have other Things underneath """

    def __init__(self, name, game):
        """Set basic properties for the UnderSpace instance
		Takes argument name, a single noun (string)"""
        super().__init__(name)

        self._me = game.me
        self.size = 50
        self.contains_preposition = "under"
        self.contains_under = True
        self.contains_preposition_inverse = "out"

    def compositeBaseDesc(self):
        if self.is_composite:
            if self.children_desc:
                self.desc = self.base_desc + self.children_desc
            else:
                self.desc = self.base_desc
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        else:
            self.desc = self.base_desc

    def compositeBasexDesc(self):
        if self.is_composite:
            if self.children_desc:
                self.xdesc = self.xdesc + self.children_desc
            else:
                self.xdesc = self.base_xdesc
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        else:
            self.xdesc = self.base_xdesc

    def containsListUpdate(self, update_desc=True, update_xdesc=True):
        """Update description for addition/removal of items from the UnderSpace instance """
        from .actor import Player

        # desc = self.base_desc
        # xdesc = self.base_xdesc
        self.compositeBaseDesc()
        self.compositeBasexDesc()
        if not self.revealed:
            return False
        inlist = (
            " "
            + self.contains_preposition.capitalize()
            + " "
            + self.getArticle(True)
            + self.verbose_name
            + " is "
        )
        # iterate through contents, appending the verbose_name of each to onlist
        list_version = list(self.contains.keys())
        player_here = False
        for key in list_version:
            for item in self.contains[key]:
                if key in list_version:
                    if isinstance(item, Player):
                        list_version.remove(key)
                        player_here = True
                    elif item.parent_obj:
                        list_version.remove(key)
        for key in list_version:
            if len(self.contains[key]) > 1:
                inlist = (
                    inlist + str(len(things)) + " " + self.contains[key][0].verbose_name
                )
            else:
                inlist = (
                    inlist
                    + self.contains[key][0].getArticle()
                    + self.contains[key][0].verbose_name
                )
            if key is list_version[-1]:
                inlist = inlist + "."
            elif key is list_version[-2]:
                inlist = inlist + " and "
            else:
                inlist = inlist + ", "
            if key not in self._me.knows_about:
                self._me.knows_about.append(key)
        # remove the empty inlist in the case of no contents
        # TODO: consider rewriting this logic to avoid contructing an empty inlist, then deleting it
        if len(list_version) == 0:
            inlist = ""
        if player_here:
            if inlist != "":
                inlist = inlist + "<br>"
            inlist = (
                inlist + "You are in " + self.getArticle(True) + self.verbose_name + "."
            )
        # update descriptions
        if self.is_composite:
            if self.children_desc:
                self.desc = self.desc + self.children_desc
                self.xdesc = self.xdesc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
                    self.xdesc = self.xdesc + item.desc
            # self.desc = self.desc + inlist
            # self.xdesc = self.xdesc + inlist
        if update_desc and self.desc_reveal:
            self.desc = self.desc + inlist
        if update_xdesc and self.xdesc_reveal:
            self.xdesc = self.xdesc + inlist
        self.contains_desc = inlist
        return True

    def addThing(self, item):
        super().addThing(item)
        self.containsListUpdate()

    def removeThing(self, item):
        super().removeThing(item)
        self.containsListUpdate()

    def revealUnder(self):
        self.revealed = True
        self.containsListUpdate()
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

    def describeThing(self, description):
        self.base_desc = description
        self.desc = self.base_desc + self.state_desc
        if self.is_composite:
            if self.children_desc:
                self.desc = self.desc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.desc = self.desc + item.desc
        self.containsListUpdate()

    def xdescribeThing(self, description):
        self.base_xdesc = description
        self.xdesc = self.base_xdesc
        if self.is_composite:
            if self.children_desc:
                self.xdesc = self.xdesc + self.children_desc
            else:
                for item in self.children:
                    if item in self.child_UnderSpaces:
                        continue
                    self.xdesc = self.xdesc + item.desc
        self.containsListUpdate()

    def updateDesc(self):
        self.containsListUpdate()


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


class Book(Readable):
    """Readable that can be opened """

    def __init__(self, name, text="There's nothing written here. "):
        """Sets essential properties for the Book instance """
        super().__init__(name, text)
        self.is_open = False

    def makeOpen(self):
        self.is_open = True
        self.desc = self.base_desc + "It is open. "
        self.xdesc = self.base_xdesc + "It is open. "

    def makeClosed(self):
        self.is_open = False
        self.desc = self.base_desc
        self.xdesc = self.base_xdesc


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

        self.base_desc = "There is " + self.getArticle() + self.verbose_name + " here. "
        self.base_xdesc = self.base_desc
        self.desc = self.base_desc
        self.xdesc = self.base_xdesc

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

    def getArticle(self, definite=False):
        """Gets the correct article for a Thing
		Takes argument definite (defaults to False), which specifies whether the article is definite
		Returns a string """
        if not self.hasArticle:
            return ""
        elif definite or self.isDefinite:
            return "the "
        elif self.is_numberless:
            return ""
        else:
            if self.verbose_name[0] in ["a", "e", "i", "o", "u"]:
                return "an "
            else:
                return "a "


# hacky solution for reflexive pronouns (himself/herself/itself)
reflexive = Abstract("itself")
reflexive.addSynonym("himself")
reflexive.addSynonym("herself")
reflexive.addSynonym("themself")
reflexive.addSynonym("themselves")

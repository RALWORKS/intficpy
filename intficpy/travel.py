from .ifp_object import IFPObject
from .thing_base import Thing
from .things import Door, Lock, AbstractClimbable, Surface
from .verb import openVerb, standUpVerb
from .room import Room

##############################################################
# ROOM.PY - travel functions for IntFicPy
# Defines travel functions and the direction vocab dictionary
##############################################################


class TravelConnector(IFPObject):
    """Base class for travel connectors
	Links two rooms together"""

    def __init__(self, room1, direction1, room2, direction2, name="doorway", prep=0):
        super().__init__()
        self.prep = prep
        self.pointA = room1
        self.pointB = room2
        self.entranceA_msg = None
        self.entranceB_msg = None
        self.can_pass = True
        self.cannot_pass_msg = "The way is blocked. "
        r = [room1, room2]
        d = [direction1, direction2]
        interactables = []
        self.entranceA = Thing(name)
        self.entranceB = Thing(name)
        self.entranceA.invItem = False
        self.entranceB.invItem = False
        self.entranceA.connection = self
        self.entranceB.connection = self
        self.entranceA.direction = direction1
        self.entranceB.direction = direction2
        interactables.append(self.entranceA)
        interactables.append(self.entranceB)
        for x in range(0, 2):
            r[x].addThing(interactables[x])
            if d[x] == "n":
                r[x].north = self
                interactables[x].setAdjectives(["north"])
                interactables[x].describeThing("There is a " + name + " to the north. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about "
                    + interactables[x].getArticle(True)
                    + interactables[x].verbose_name
                    + "."
                )
            elif d[x] == "s":
                r[x].south = self
                interactables[x].setAdjectives(["south"])
                interactables[x].describeThing("There is a " + name + " to the south. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about "
                    + interactables[x].getArticle(True)
                    + interactables[x].verbose_name
                    + "."
                )
            elif d[x] == "e":
                r[x].east = self
                interactables[x].setAdjectives(["east"])
                interactables[x].describeThing("There is a " + name + " to the east. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about "
                    + interactables[x].getArticle(True)
                    + interactables[x].verbose_name
                    + "."
                )
            elif d[x] == "w":
                r[x].west = self
                interactables[x].setAdjectives(["west"])
                interactables[x].describeThing("There is a " + name + " to the west. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about "
                    + interactables[x].getArticle(True)
                    + interactables[x].verbose_name
                    + "."
                )
            elif d[x] == "ne":
                r[x].northeast = self
                interactables[x].setAdjectives(["northeast"])
                interactables[x].describeThing(
                    "There is a " + name + " to the northeast. "
                )
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about "
                    + interactables[x].getArticle(True)
                    + interactables[x].verbose_name
                    + "."
                )
            elif d[x] == "nw":
                r[x].northwest = self
                interactables[x].setAdjectives(["northwest"])
                interactables[x].describeThing(
                    "There is a " + name + " to the northwest. "
                )
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about  "
                    + interactables[x].getArticle(True)
                    + interactables[x].verbose_name
                    + "."
                )
            elif d[x] == "se":
                r[x].southeast = self
                interactables[x].setAdjectives(["southeast"])
                interactables[x].describeThing(
                    "There is a " + name + " to the southeast. "
                )
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about "
                    + interactables[x].getArticle(True)
                    + interactables[x].verbose_name
                    + "."
                )
            elif d[x] == "sw":
                r[x].southwest = self
                interactables[x].setAdjectives(["southwest"])
                interactables[x].describeThing(
                    "There is a " + name + " to the southwest. "
                )
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about "
                    + interactables[x].getArticle(True)
                    + interactables[x].verbose_name
                    + "."
                )
            elif d[x] == "u":
                r[x].up = self
                interactables[x].setAdjectives(["upward"])
                interactables[x].describeThing("There is a " + name + " leading up. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the "
                    + interactables[x].getArticle(True)
                    + name
                    + "."
                )
            elif d[x] == "d":
                r[x].down = self
                interactables[x].setAdjectives(["downward"])
                interactables[x].describeThing("There is a " + name + " leading down. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about  "
                    + interactables[x].getArticle(True)
                    + name
                    + "."
                )
            else:
                print("error: invalid direction input for TravelConnector: " + d[x])

    def setFromPrototype(self, connector):
        from .vocab import vocab

        x = 0
        self.entranceA_msg = connector.entranceA_msg
        self.entranceB_msg = connector.entranceB_msg
        for x in range(0, 2):
            print(x)
            for synonym in self.interactables[x].synonyms:
                if synonym in vocab.nounDict:
                    if self.interactables[x] in vocab.nounDict[synonym]:
                        vocab.nounDict[synonym].remove(self.interactables[x])
                        if vocab.nounDict[synonym] == []:
                            del vocab.nounDict[synonym]
            for adj in self.interactables[x].adjectives:
                remove_list = []
                if adj not in directionDict and adj != "upward" and adj != "downward":
                    remove_list.append(adj)
                for adj in remove_list:
                    if adj in self.interactables[x].adjectives:
                        self.interactables[x].adjectives.remove(adj)
                for adj in connector.interactables[x].adjectives:
                    if (
                        adj not in directionDict
                        and adj != "upward"
                        and adj != "downward"
                        and adj not in self.interactables[x].adjectives
                    ):
                        self.interactables[x].adjectives.append(adj)

            for attr, value in connector.interactables[x].__dict__.items():
                if attr == "direction" or attr == "adjectives" or attr == "ix":
                    pass
                else:
                    setattr(self.interactables[x], attr, value)

            add = self.interactables[x].synonyms + [self.interactables[x].name]
            for noun in add:
                if noun in vocab.nounDict:
                    if self.interactables[x] not in vocab.nounDict[noun]:
                        vocab.nounDict[noun].append(self.interactables[x])
                else:
                    vocab.nounDict[noun] = [self.interactables[x]]
            x = x + 1

    def travel(self, game):
        try:
            barrier = self.barrierFunc(game)
        except:
            barrier = False
        if barrier:
            return False
        outer_loc = game.me.getOutermostLocation()
        if not self.can_pass:
            game.app.printToGUI(self.cannot_pass_msg)
            return False
        if outer_loc == self.pointA:
            if not outer_loc.resolveDarkness(game.me) and (
                self.entranceA.direction not in outer_loc.dark_visible_exits
            ):
                game.app.printToGUI(outer_loc.dark_msg)
                return False
            preRemovePlayer(game)
            if game.me.location:
                game.me.location.removeThing(game.me)
                game.me.location = self.pointB
                game.me.location.addThing(game.me)
                if self.entranceA_msg:
                    game.app.printToGUI(self.entranceA_msg)
                else:
                    if self.prep == 0:
                        x = "through "
                    elif self.prep == 1:
                        x = "into "
                    else:
                        x = "up "
                    game.app.printToGUI(
                        "You go "
                        + x
                        + self.entranceA.getArticle(True)
                        + self.entranceA.name
                        + "."
                    )
                game.me.location.describe(game)
                return True
        elif outer_loc == self.pointB:
            if not outer_loc.resolveDarkness(game.me) and (
                self.entranceB.direction not in outer_loc.dark_visible_exits
            ):
                game.app.printToGUI(outer_loc.dark_msg)
                return False
            preRemovePlayer(game)
            if game.me.location:
                game.me.location.removeThing(game.me)
                game.me.location = self.pointA
                game.me.location.addThing(game.me)
                if self.entranceB_msg:
                    game.app.printToGUI(self.entranceB_msg)
                else:
                    if self.prep == 0:
                        x = "through "
                    elif self.prep == 1:
                        x = "out of "
                    else:
                        x = "down "
                    game.app.printToGUI(
                        "You go "
                        + x
                        + self.entranceB.getArticle(True)
                        + self.entranceB.name
                        + "."
                    )
                game.me.location.describe(game)
                return True
        else:
            game.app.printToGUI("You cannot go that way. ")
            return False


class DoorConnector(TravelConnector):
    """Base class for travel connectors
	Links two rooms together"""

    def __init__(self, room1, direction1, room2, direction2):
        self.registerNewIndex()
        self.is_top_level_location = False
        self.pointA = room1
        self.pointB = room2
        self.entranceA_msg = None
        self.entranceB_msg = None
        r = [room1, room2]
        d = [direction1, direction2]
        interactables = []
        self.can_pass = True
        self.cannot_pass_msg = "The way is blocked. "
        self.entranceA = Door("door")
        self.entranceB = Door("door")
        self.entranceA.twin = self.entranceB
        self.entranceB.twin = self.entranceA
        self.entranceA.connection = self
        self.entranceB.connection = self
        self.entranceA.direction = direction1
        self.entranceB.direction = direction2
        interactables.append(self.entranceA)
        interactables.append(self.entranceB)
        for x in range(0, 2):
            r[x].addThing(interactables[x])
            if d[x] == "n":
                r[x].north = self
                interactables[x].setAdjectives(["north"])
                interactables[x].describeThing("There is a door to the north. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the north door. "
                )
            elif d[x] == "s":
                r[x].south = self
                interactables[x].setAdjectives(["south"])
                interactables[x].describeThing("There is a door to the south. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the south door. "
                )
            elif d[x] == "e":
                r[x].east = self
                interactables[x].setAdjectives(["east"])
                interactables[x].describeThing("There is a door to the east. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the east door. "
                )
            elif d[x] == "w":
                r[x].west = self
                interactables[x].setAdjectives(["west"])
                interactables[x].describeThing("There is a door to the west. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the west door.  "
                )
            elif d[x] == "ne":
                r[x].northeast = self
                interactables[x].setAdjectives(["northeast"])
                interactables[x].describeThing(
                    "You notice nothing remarkable about the northeast door. "
                )
            elif d[x] == "nw":
                r[x].northwest = self
                interactables[x].setAdjectives(["northwest"])
                interactables[x].describeThing("There is a door to the northwest. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the northwest door. "
                )
            elif d[x] == "se":
                r[x].southeast = self
                interactables[x].setAdjectives(["southeast"])
                interactables[x].describeThing("There is a door to the southeast. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the southeast door. "
                )
            elif d[x] == "sw":
                r[x].southwest = self
                interactables[x].setAdjectives(["southwest"])
                interactables[x].describeThing("There is a door to the southwest. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the southwest door. "
                )
            else:
                print("error: invalid direction input for DoorConnector: " + d[x])

    def setLock(self, lock_obj):
        if isinstance(lock_obj, Lock):
            if not lock_obj.parent_obj:
                self.entranceA.lock_obj = lock_obj
                self.entranceB.lock_obj = lock_obj.copyThingUniqueIx()
                self.entranceA.lock_obj.twin = self.entranceB.lock_obj
                self.entranceB.lock_obj.twin = self.entranceA.lock_obj
                self.entranceA.lock_obj.parent_obj = self.entranceA
                self.entranceB.lock_obj.parent_obj = self.entranceB
                self.pointA.addThing(self.entranceA.lock_obj)
                self.pointB.addThing(self.entranceB.lock_obj)
                self.entranceA.lock_obj.setAdjectives(
                    self.entranceA.lock_obj.adjectives
                    + self.entranceA.adjectives
                    + [self.entranceA.name]
                )
                self.entranceB.lock_obj.setAdjectives(
                    self.entranceB.lock_obj.adjectives
                    + self.entranceB.adjectives
                    + [self.entranceB.name]
                )
                self.entranceA.lock_obj.describeThing("")
                self.entranceB.lock_obj.describeThing("")
                self.entranceA.lock_obj.xdescribeThing(
                    "You notice nothing remarkable about "
                    + self.entranceA.lock_obj.getArticle(True)
                    + self.entranceA.lock_obj.name
                    + ". "
                )
                self.entranceB.lock_obj.xdescribeThing(
                    "You notice nothing remarkable about "
                    + self.entranceB.lock_obj.getArticle(True)
                    + self.entranceB.lock_obj.name
                    + ". "
                )
                if lock_obj.is_locked:
                    self.entranceA.lock_desc = " It is locked. "
                    self.entranceB.lock_desc = " It is locked. "
                else:
                    self.entranceA.lock_desc = " It is unlocked. "
                    self.entranceB.lock_desc = " It is unlocked. "
                self.entranceA.xdesc = self.entranceA.xdesc + self.entranceA.lock_desc
                self.entranceB.xdesc = self.entranceB.xdesc + self.entranceB.lock_desc
            else:
                print(
                    "Cannot set lock_obj for "
                    + self.entranceA.verbose_name
                    + ": lock_obj.parent already set "
                )
        else:
            print(
                "Cannot set lock_obj for "
                + self.entranceA.verbose_name
                + ": not a Lock "
            )

    def travel(self, game):
        outer_loc = game.me.getOutermostLocation()
        preRemovePlayer(game)
        if outer_loc == self.pointA:
            if not outer_loc.resolveDarkness(game.me) and (
                self.entranceA.direction not in outer_loc.dark_visible_exits
            ):
                game.app.printToGUI(outer_loc.dark_msg)
                return False
        else:
            if not outer_loc.resolveDarkness(game.me) and (
                self.entranceB.direction not in outer_loc.dark_visible_exits
            ):
                game.app.printToGUI(outer_loc.dark_msg)
                return False

        if not self.can_pass:
            game.app.printToGUI(self.cannot_pass_msg)
            return False
        elif outer_loc == self.pointA:
            if not self.entranceA.is_open:
                opened = openVerb.verbFunc(game, self.entranceA)
                if not opened:
                    return False
            try:
                barrier = self.barrierFunc(game)
            except:
                barrier = False
            if barrier:
                return False
            # preRemovePlayer(game)
            if game.me.location:
                game.me.location.removeThing(game.me)
            game.me.location = self.pointB
            game.me.location.addThing(game.me)
            if self.entranceA_msg:
                game.app.printToGUI(self.entranceA_msg)
            else:
                game.app.printToGUI(
                    "You go through "
                    + self.entranceA.getArticle(True)
                    + self.entranceA.verbose_name
                    + ". "
                )
            game.me.location.describe(game)
            return True
        elif outer_loc == self.pointB:
            if not self.entranceB.is_open:
                opened = openVerb.verbFunc(game, self.entranceB)
                if not opened:
                    return False
            try:
                barrier = self.barrierFunc(game)
            except:
                barrier = False
            if barrier:
                return False
            # preRemovePlayer(game)
            if game.me.location:
                game.me.location.removeThing(game.me)
            game.me.location = self.pointA
            game.me.location.addThing(game.me)
            if self.entranceB_msg:
                game.app.printToGUI(self.entranceB_msg)
            else:
                game.app.printToGUI(
                    "You go through "
                    + self.entranceB.getArticle(True)
                    + self.entranceB.verbose_name
                    + ". "
                )

            game.me.location.describe(game)
            return True
        else:
            game.app.printToGUI("You cannot go that way. ")
            return False


class LadderConnector(TravelConnector):
    """Class for ladder travel connectors (up/down)
	Links two rooms together"""

    def __init__(self, room1, room2):
        self.registerNewIndex()
        self.is_top_level_location = False
        self.pointA = room1
        self.pointB = room2
        self.entranceA_msg = None
        self.entranceB_msg = None
        r = [room1, room2]
        d = ["u", "d"]
        interactables = []
        self.can_pass = True
        self.cannot_pass_msg = "The way is blocked. "
        self.entranceA = AbstractClimbable("ladder")
        self.entranceB = AbstractClimbable("ladder")
        self.interactables = [self.entranceA, self.entranceB]
        self.entranceA.connection = self
        self.entranceB.connection = self
        self.entranceA.direction = "u"
        self.entranceB.direction = "d"
        interactables.append(self.entranceA)
        interactables.append(self.entranceB)
        for x in range(0, 2):
            r[x].addThing(interactables[x])
            if d[x] == "u":
                r[x].up = self
                interactables[x].setAdjectives(["upward"])
                interactables[x].describeThing("There is a ladder leading up. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the ladder. "
                )
            elif d[x] == "d":
                r[x].down = self
                interactables[x].setAdjectives(["downward"])
                interactables[x].describeThing("There is a ladder leading down. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the ladder. "
                )
            else:
                print("error: invalid direction input for LadderConnector: " + d[x])

    def travel(self, game):
        try:
            barrier = self.barrierFunc(game)
        except:
            barrier = False
        if barrier:
            return False
        outer_loc = game.me.getOutermostLocation()
        if outer_loc == self.pointA:
            if not outer_loc.resolveDarkness(game.me) and (
                self.entranceA.direction not in outer_loc.dark_visible_exits
            ):
                game.app.printToGUI(outer_loc.dark_msg)
                return False
            preRemovePlayer(game)
            if game.me.location:
                game.me.location.removeThing(game.me)
            game.me.location = self.pointB
            game.me.location.addThing(game.me)
            if self.entranceA_msg:
                game.app.printToGUI(self.entranceA_msg)
            else:
                game.app.printToGUI("You climb the ladder. ")

            game.me.location.describe(game)
            return True
        elif outer_loc == self.pointB:
            if not outer_loc.resolveDarkness(game.me) and (
                self.entranceB.direction not in outer_loc.dark_visible_exits
            ):
                game.app.printToGUI(outer_loc.dark_msg)
                return False
            preRemovePlayer(game)
            if game.me.location:
                game.me.location.removeThing(game.me)
            game.me.location = self.pointA
            game.me.location.addThing(game.me)
            if self.entranceB_msg:
                game.app.printToGUI(self.entranceB_msg)
            else:
                game.app.printToGUI("You climb the ladder. ")

            game.me.location.describe(game)
            return True
        else:
            game.app.printToGUI("You cannot go that way. ")
            return False


class StaircaseConnector(TravelConnector):
    """Class for staircase travel connectors (up/down)
	Links two rooms together"""

    def __init__(self, room1, room2):
        self.registerNewIndex()
        self.is_top_level_location = False
        self.pointA = room1
        self.pointB = room2
        self.entranceA_msg = False
        self.entranceB_msg = False
        r = [room1, room2]
        d = ["u", "d"]
        interactables = []
        self.can_pass = True
        self.cannot_pass_msg = "The way is blocked. "
        self.entranceA = AbstractClimbable("staircase")
        self.entranceB = AbstractClimbable("staircase")
        self.entranceA.addSynonym("stairway")
        self.entranceB.addSynonym("stairway")
        self.entranceA.addSynonym("stairs")
        self.entranceB.addSynonym("stairs")
        self.entranceA.addSynonym("stair")
        self.entranceB.addSynonym("stair")
        self.entranceA.connection = self
        self.entranceB.connection = self
        self.entranceA.direction = "u"
        self.entranceB.direction = "d"
        interactables.append(self.entranceA)
        interactables.append(self.entranceB)
        for x in range(0, 2):
            r[x].addThing(interactables[x])
            if d[x] == "u":
                r[x].up = self
                interactables[x].setAdjectives(["upward"])
                interactables[x].describeThing("There is a staircase leading up. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the staircase "
                )
            elif d[x] == "d":
                r[x].down = self
                interactables[x].setAdjectives(["downward"])
                interactables[x].describeThing("There is a staircase leading down. ")
                interactables[x].xdescribeThing(
                    "You notice nothing remarkable about the staircase. "
                )
            else:
                print("error: invalid direction input for StaircaseConnector: " + d[x])

    def travel(self, game):
        try:
            barrier = self.barrierFunc(game)
        except:
            barrier = False
        if barrier:
            return False
        outer_loc = game.me.getOutermostLocation()
        if not self.can_pass:
            game.app.printToGUI(self.cannot_pass_msg)
            return False
        elif outer_loc == self.pointA:
            if not outer_loc.resolveDarkness(game.me) and (
                self.entranceA.direction not in outer_loc.dark_visible_exits
            ):
                game.app.printToGUI(outer_loc.dark_msg)
                return False
            preRemovePlayer(game)
            if game.me.location:
                game.me.location.removeThing(game.me)
            game.me.location = self.pointB
            game.me.location.addThing(game.me)
            if self.entranceA_msg:
                game.app.printToGUI(self.entranceA_msg)
            else:
                game.app.printToGUI("You climb the staircase. ")

            game.me.location.describe(game)
            return True
        elif outer_loc == self.pointB:
            if not outer_loc.resolveDarkness(game.me) and (
                self.entranceB.direction not in outer_loc.dark_visible_exits
            ):
                game.app.printToGUI(outer_loc.dark_msg)
                return False
            preRemovePlayer(game)
            if game.me.location:
                game.me.location.removeThing(game.me)
            game.me.location = self.pointA
            game.me.location.addThing(game.me)
            if self.entranceB_msg:
                game.app.printToGUI(self.entranceB_msg)
            else:
                game.app.printToGUI("You climb the staircase. ")

            game.me.location.describe(game)
            return True
        else:
            game.app.printToGUI("You cannot go that way. ")
            return False


# travel functions, called by getDirection in parser.py
def preRemovePlayer(game):
    """Remove the Player from the current room
	Called by travel functions
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    x = game.me.location
    if isinstance(x, Thing):
        x.removeThing(game.me)
        x.containsListUpdate()
        if isinstance(x, Surface):
            game.app.printToGUI(
                "You get off of " + x.getArticle(True) + x.verbose_name + "."
            )
        else:
            game.app.printToGUI(
                "You get out of " + x.getArticle(True) + x.verbose_name + "."
            )
        x = x.location
        while not isinstance(x, Room):
            x.sub_contains[game.me.ix].remove(game.me)
            if x.sub_contains[game.me.ix] == []:
                del x.sub_contains[game.me.ix]
            x = x.location


def getDirectionFromString(loc, input_string):
    if input_string in ["n", "north"]:
        return loc.north
    elif input_string in ["ne", "northeast"]:
        return loc.northeast
    elif input_string in ["e", "east"]:
        return loc.east
    elif input_string in ["se", "southeast"]:
        return loc.southeast
    elif input_string in ["s", "south"]:
        return loc.south
    elif input_string in ["sw", "southwest"]:
        return loc.southwest
    elif input_string in ["w", "west"]:
        return loc.west
    elif input_string in ["nw", "northwest"]:
        return loc.northwest
    elif input_string in ["u", "up", "upward"]:
        return loc.up
    elif input_string in ["d", "down", "downward"]:
        return loc.down
    elif input_string == "in":
        return loc.entrance
    elif input_string == "out":
        return loc.exit
    else:
        print(input_string + "not a direction")
        return False


def travelN(game):
    """Travel north
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("n" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.north:
        game.app.printToGUI(loc.n_false_msg)
    elif isinstance(loc.north, TravelConnector):
        loc.north.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.north
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.n_msg)

        game.me.location.describe(game)


def travelNE(game):
    """Travel northeast
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("ne" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.northeast:
        game.app.printToGUI(loc.ne_false_msg)
    elif isinstance(loc.northeast, TravelConnector):
        loc.northeast.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.northeast
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.ne_msg)

        game.me.location.describe(game)


def travelE(game):
    """Travel east
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("e" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.east:
        game.app.printToGUI(loc.e_false_msg)
    elif isinstance(loc.east, TravelConnector):
        loc.east.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.east
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.e_msg)

        game.me.location.describe(game)


def travelSE(game):
    """Travel southeast
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("se" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.southeast:
        game.app.printToGUI(loc.se_false_msg)
    elif isinstance(loc.southeast, TravelConnector):
        loc.southeast.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.southeast
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.se_msg)

        game.me.location.describe(game)


def travelS(game):
    """Travel south
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("s" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.south:
        game.app.printToGUI(loc.s_false_msg)
    elif isinstance(loc.south, TravelConnector):
        loc.south.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.south
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.s_msg)

        game.me.location.describe(game)


def travelSW(game):
    """Travel southwest
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("sw" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.southwest:
        game.app.printToGUI(loc.sw_false_msg)
    elif isinstance(loc.southwest, TravelConnector):
        loc.southwest.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.southwest
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.sw_msg)

        game.me.location.describe(game)


def travelW(game):
    """Travel west
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("w" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.west:
        game.app.printToGUI(loc.w_false_msg)
    elif isinstance(loc.west, TravelConnector):
        loc.west.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.west
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.w_msg)

        game.me.location.describe(game)


# travel northwest
def travelNW(game):
    """Travel northwest
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("nw" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.northwest:
        game.app.printToGUI(loc.nw_false_msg)
    elif isinstance(loc.northwest, TravelConnector):
        loc.northwest.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.northwest
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.nw_msg)

        game.me.location.describe(game)


# travel up
def travelU(game):
    """Travel upward
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("u" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.up:
        game.app.printToGUI(loc.u_false_msg)
    elif isinstance(loc.up, TravelConnector):
        loc.up.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.up
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.u_msg)

        game.me.location.describe(game)


# travel down
def travelD(game):
    """Travel downward
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("d" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.down:
        game.app.printToGUI(loc.d_false_msg)
    elif isinstance(loc.down, TravelConnector):
        loc.down.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.down
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.d_msg)

        game.me.location.describe(game)


# go out
# synonym "exit" implemented as a verb
def travelOut(game):
    """Travel out
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("exit" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.exit:
        game.app.printToGUI(loc.exit_false_msg)
    elif isinstance(loc.exit, TravelConnector):
        loc.exit.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.exit
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.exit_msg)

        game.me.location.describe(game)


# go in
# synonym "enter" implemented as a verb
def travelIn(game):
    """Travel through entance
	Takes arguments game.me, pointing to the player, and game.app, pointing to the GUI game.app """
    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        standUpVerb.verbFunc(game)
    if not loc.resolveDarkness(game.me) and ("entrance" not in loc.dark_visible_exits):
        game.app.printToGUI(loc.dark_msg)
    elif not loc.entrance:
        game.app.printToGUI(loc.entrance_false_msg)
    elif isinstance(loc.entrance, TravelConnector):
        loc.entrance.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = loc.entrance
        game.me.location.addThing(game.me)
        game.app.printToGUI(loc.entrance_msg)

        game.me.location.describe(game)


# maps user input to travel functions
directionDict = {
    "n": travelN,
    "north": travelN,
    "ne": travelNE,
    "northeast": travelNE,
    "e": travelE,
    "east": travelE,
    "se": travelSE,
    "southeast": travelSE,
    "s": travelS,
    "south": travelS,
    "sw": travelSW,
    "southwest": travelSW,
    "w": travelW,
    "west": travelW,
    "nw": travelNW,
    "northwest": travelNW,
    "up": travelU,
    "u": travelU,
    "upward": travelU,
    "down": travelD,
    "d": travelD,
    "downward": travelD,
    "in": travelIn,
    "out": travelOut,
}

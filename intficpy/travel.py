from .exceptions import IFPError
from .ifp_object import IFPObject
from .thing_base import Thing
from .things import Door, Lock, AbstractClimbable, Surface
from .verb import OpenVerb, StandUpVerb
from .room import Room

##############################################################
# TRAVEL.PY - travel functions for IntFicPy
# Defines travel functions and the direction vocab dictionary
##############################################################


class TravelConnector(IFPObject):
    """
    Base class for travel connectors. Links two rooms together, with an interactable
    Thing on each end.

    By default, this creates a "doorway" on either end, without an opening and closing
    door.

    :param game: the current game
    :type game: IFPGame
    :param room1: the first Room to connect
    :type room1: Room
    :param direction1: the direction from `room1` this connector attatches to (ex, pass
        in "n" to set room1.north to this connector)
    :type direction1: valid direction string (n/north/se/southeast, etc.)
    :param room2: the other Room to connect
    :type room2: Room
    :param direction1: the direction from `room2` this connector attatches to (ex, pass
        in "s" to set room2.south to this connector)
    :type direction1: valid direction string (n/north/se/southeast, etc.)
    """

    EntranceAType = Thing
    EntranceBType = Thing
    can_pass = True
    cannot_pass_msg = "The way is blocked. "
    default_travel_msg = "You go {preposition} the {entrance.verbose_name}. "
    entrance_a_msg = None
    entrance_b_msg = None
    entrance_synonyms = []
    entrance_a_preposition = "through"
    entrance_b_preposition = "through"
    entrance_name = "doorway"
    default_description = "There is a {name} to the {full_direction}. "

    def __init__(self, game, room1, direction1, room2, direction2):
        super().__init__(game)
        self.point_a = room1
        self.point_b = room2
        r = [room1, room2]
        d = [direction1, direction2]
        interactables = []
        self.entrance_a = self.EntranceAType(self.game, self.entrance_name)
        self.entrance_b = self.EntranceBType(self.game, self.entrance_name)
        self.entrance_a.invItem = False
        self.entrance_b.invItem = False
        self.entrance_a.connection = self
        self.entrance_b.connection = self
        self.entrance_a.direction = direction1
        self.entrance_b.direction = direction2
        interactables.append(self.entrance_a)
        interactables.append(self.entrance_b)

        for s in self.entrance_synonyms:
            self.entrance_a.addSynonym(s)
        for s in self.entrance_synonyms:
            self.entrance_b.addSynonym(s)

        for x in range(0, 2):
            r[x].addThing(interactables[x])
            try:
                short = directionDict[d[x]]["short"]
                full = directionDict[d[x]]["full"]
                adj = directionDict[d[x]]["adj"]
            except KeyError as e:
                raise IFPError(
                    f"Tried to create {self.__class__.__name__}, but string {d[x]} not "
                    "a valid direction string. Use one of: {directionDict.keys()}"
                )

            setattr(r[x], full, self)
            interactables[x].setAdjectives([adj])
            interactables[x].describeThing(
                self.default_description.format(
                    name=self.entrance_name, full_direction=full,
                )
            )

    def setFromPrototype(self, connector):
        x = 0
        self.entrance_a_msg = connector.entrance_a_msg
        self.entrance_b_msg = connector.entrance_b_msg
        for x in range(0, 2):
            print(x)
            for synonym in self.interactables[x].synonyms:
                if synonym in self.game.nouns:
                    if self.interactables[x] in self.game.nouns[synonym]:
                        self.game.nouns[synonym].remove(self.interactables[x])
                        if self.game.nouns[synonym] == []:
                            del self.game.nouns[synonym]
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
                if noun in self.game.nouns:
                    if self.interactables[x] not in self.game.nouns[noun]:
                        self.game.nouns[noun].append(self.interactables[x])
                else:
                    self.game.nouns[noun] = [self.interactables[x]]
            x = x + 1

    def _prepareToCross(self, entrance):
        return True

    def _travelEntrance(self, game, outer_loc, entrance_marker):
        new_loc = getattr(self, f"point_{'a' if entrance_marker=='b' else 'b'}")
        msg = getattr(self, f"entrance_{entrance_marker}_msg")
        entrance = getattr(self, f"entrance_{entrance_marker}")

        can_cross = self._prepareToCross(self.entrance_a)
        if not can_cross:
            return False

        if not outer_loc.resolveDarkness(game) and (
            self.entrance_a.direction not in outer_loc.dark_visible_exits
        ):
            return False

        preRemovePlayer(game)
        game.me.moveTo(new_loc)
        if msg:
            game.addTextToEvent("turn", msg)
        else:
            game.addTextToEvent(
                "turn",
                self.default_travel_msg.format(
                    entrance=entrance,
                    preposition=getattr(
                        self, f"entrance_{entrance_marker}_preposition"
                    ),
                ),
            )
        game.me.location.describe(game)
        return True

    def travel(self, game):
        """
        The player travels through this connector.

        Determine if the player is able to pass, and if so, move the player.

        :param game: the current game
        :type game: IFPGame
        """
        try:
            barrier = self.barrierFunc(game)
        except:
            barrier = False
        if barrier:
            return False
        outer_loc = game.me.getOutermostLocation()
        if not self.can_pass:
            game.addTextToEvent("turn", self.cannot_pass_msg)
            return False
        if outer_loc == self.point_a:
            return self._travelEntrance(game, outer_loc, "a")
        if outer_loc == self.point_b:
            return self._travelEntrance(game, outer_loc, "b")


class DoorConnector(TravelConnector):
    """
    A TravelConnector with a door that opens and closes.

    A lock can be added to the door using setLock

    :param game: the current game
    :type game: IFPGame
    :param room1: the first Room to connect
    :type room1: Room
    :param direction1: the direction from `room1` this connector attatches to (ex, pass
        in "n" to set room1.north to this connector)
    :type direction1: valid direction string (n/north/se/southeast, etc.)
    :param room2: the other Room to connect
    :type room2: Room
    :param direction1: the direction from `room2` this connector attatches to (ex, pass
        in "s" to set room2.south to this connector)
    :type direction1: valid direction string (n/north/se/southeast, etc.)
    """

    EntranceAType = Door
    EntranceBType = Door
    entrance_name = "door"

    def _prepareToCross(self, entrance):
        if not entrance.is_open:
            opened = OpenVerb().verbFunc(self.game, entrance)
            if not opened:
                return False
        return True

    def setLock(self, lock_obj):
        """
        Add a lock to this door.

        :param lock_obj: the Lock to place on this door. Must not already be attached to
            something.
        :type game: Lock
        """
        if not isinstance(lock_obj, Lock):
            raise IFPError(
                "Cannot set lock_obj for "
                + self.entrance_a.verbose_name
                + ": not a Lock "
            )

        if lock_obj.parent_obj:
            raise IFPError(
                "Cannot set lock_obj for "
                + self.entrance_a.verbose_name
                + ": lock_obj.parent already set "
            )

        self.entrance_a.lock_obj = lock_obj
        self.entrance_b.lock_obj = lock_obj.copyThingUniqueIx()
        self.entrance_a.lock_obj.twin = self.entrance_b.lock_obj
        self.entrance_b.lock_obj.twin = self.entrance_a.lock_obj
        self.entrance_a.lock_obj.parent_obj = self.entrance_a
        self.entrance_b.lock_obj.parent_obj = self.entrance_b
        self.point_a.addThing(self.entrance_a.lock_obj)
        self.point_b.addThing(self.entrance_b.lock_obj)
        self.entrance_a.lock_obj.setAdjectives(
            self.entrance_a.lock_obj.adjectives
            + self.entrance_a.adjectives
            + [self.entrance_a.name]
        )
        self.entrance_b.lock_obj.setAdjectives(
            self.entrance_b.lock_obj.adjectives
            + self.entrance_b.adjectives
            + [self.entrance_b.name]
        )


class LadderConnector(TravelConnector):
    """
    A ladder to connect two rooms, one above, and one below.

    :param game: the current game
    :type game: IFPGame
    :param room1: the lower room
    :type room1: Room
    :param room2: the upper room
    :type room2: Room
    """

    entrance_name = "ladder"
    default_travel_msg = "You climb {preposition} the {entrance.verbose_name}. "
    entrance_a_preposition = "up"
    entrance_b_preposition = "down"
    default_description = "A {name} leads {full_direction}. "

    def __init__(self, game, room1, room2):
        super().__init__(game, room1, "up", room2, "d")


class StaircaseConnector(TravelConnector):
    """
    A staircase to connect two rooms, one above, and one below.

    :param game: the current game
    :type game: IFPGame
    :param room1: the lower room
    :type room1: Room
    :param room2: the upper room
    :type room2: Room
    """

    entrance_synonyms = ["stairway", "stairs", "stair"]
    entrance_name = "staircase"
    default_travel_msg = "You climb {preposition} the {entrance.verbose_name}. "
    entrance_a_preposition = "up"
    entrance_b_preposition = "down"
    default_description = "A {name} leads {full_direction}. "

    def __init__(self, game, room1, room2):
        super().__init__(game, room1, "up", room2, "d")


# travel functions, called by getDirection in parser.py
def preRemovePlayer(game):
    """
    Remove the Player from all nested locations to prepare for travel
    """
    from .verb import ExitVerb

    x = game.me.location
    while isinstance(game.me.location, Thing):
        ExitVerb().verbFunc(game)


def getDirectionFromString(loc, input_string):
    """
    Given a direction string (n/nw/east, etc.), return the corresponding direction
    attribute of a given Room

    :param loc: the Room we're in
    :type loc: Room
    :param input_string: the string to interpret as direction input
    :type input_string: str
    """
    try:
        return getattr(loc, directionDict[input_string]["full"])
    except KeyError as e:
        raise IFPError(
            f"Tried to get direction from string, but string {input_string} not a direction."
        )
    # if we somehow receive something that isn't a Room, just let the attribute error happen


def travelDirection(game, direction):
    """
    Travel in the specified direction, from the player's current location

    :param game: the current game
    :type game: IFPGame
    :param direction: the direction input
    :type direction: str
    """
    short = directionDict[direction]["short"]
    full = directionDict[direction]["full"]

    loc = game.me.getOutermostLocation()
    if game.me.position != "standing":
        StandUpVerb().verbFunc(game)
    if not loc.resolveDarkness(game) and (short not in loc.dark_visible_exits):
        game.addTextToEvent("turn", loc.dark_msg)

    connector = getattr(loc, full)

    if not connector:
        game.addTextToEvent("turn", getattr(loc, f"{short}_false_msg"))
        return

    if isinstance(connector, TravelConnector):
        connector.travel(game)
    else:
        preRemovePlayer(game)
        if game.me.location:
            game.me.location.removeThing(game.me)
        game.me.location = connector
        game.me.location.addThing(game.me)
        game.addTextToEvent("turn", getattr(loc, f"{short}_msg"))

        game.me.location.describe(game)


def travelN(game):
    """Travel north
    """
    return travelDirection(game, "n")


def travelNE(game):
    """Travel northeast
    """
    return travelDirection(game, "ne")


def travelE(game):
    """Travel east
    """
    return travelDirection(game, "e")


def travelSE(game):
    """Travel southeast
    """
    return travelDirection(game, "se")


def travelS(game):
    """Travel south
    """
    return travelDirection(game, "s")


def travelSW(game):
    """Travel southwest
    """
    return travelDirection(game, "sw")


def travelW(game):
    """Travel west
    """
    return travelDirection(game, "w")


# travel northwest
def travelNW(game):
    """Travel northwest
    """
    return travelDirection(game, "nw")


# travel up
def travelU(game):
    """Travel upward
    """
    return travelDirection(game, "u")


# travel down
def travelD(game):
    """Travel downward
    """
    return travelDirection(game, "d")


# go out
# synonym "exit" implemented as a verb
def travelOut(game):
    """Travel out
    """
    return travelDirection(game, "out")


# go in
# synonym "enter" implemented as a verb
def travelIn(game):
    """Travel through entance
    """
    return travelDirection(game, "in")


# maps user input to travel functions
directionDict = {
    "n": {"func": travelN, "full": "north", "short": "n", "adj": "north"},
    "north": {"func": travelN, "full": "north", "short": "n", "adj": "north"},
    "ne": {"func": travelNE, "full": "northeast", "short": "ne", "adj": "northeast"},
    "northeast": {
        "func": travelNE,
        "full": "northeast",
        "short": "ne",
        "adj": "northeast",
    },
    "e": {"func": travelE, "full": "east", "short": "e", "adj": "east"},
    "east": {"func": travelE, "full": "east", "short": "e", "adj": "east"},
    "se": {"func": travelSE, "full": "southeast", "short": "se", "adj": "southeast"},
    "southeast": {
        "func": travelSE,
        "full": "southeast",
        "short": "se",
        "adj": "southeast",
    },
    "s": {"func": travelS, "full": "south", "short": "s", "adj": "south"},
    "south": {"func": travelS, "full": "south", "short": "s", "adj": "south"},
    "sw": {"func": travelSW, "full": "southwest", "short": "sw", "adj": "southwest"},
    "southwest": {
        "func": travelSW,
        "full": "southwest",
        "short": "sw",
        "adj": "southwest",
    },
    "w": {"func": travelW, "full": "west", "short": "w", "adj": "west"},
    "west": {"func": travelW, "full": "west", "short": "w", "adj": "west"},
    "nw": {"func": travelNW, "full": "northwest", "short": "nw", "adj": "northwest"},
    "northwest": {
        "func": travelNW,
        "full": "northwest",
        "short": "nw",
        "adj": "northwest",
    },
    "up": {"func": travelU, "full": "up", "short": "u", "adj": "upward"},
    "u": {"func": travelU, "full": "up", "short": "u", "adj": "upward"},
    "upward": {"func": travelU, "full": "up", "short": "u", "adj": "upward"},
    "down": {"func": travelD, "full": "down", "short": "d", "adj": "downward"},
    "d": {"func": travelD, "full": "down", "short": "d", "adj": "downward"},
    "downward": {"func": travelD, "full": "down", "short": "d", "adj": "downward"},
    "in": {"func": travelIn, "full": "entrance", "short": "in", "adj": "in"},
    "out": {"func": travelOut, "full": "exit", "short": "out", "adj": "out"},
}

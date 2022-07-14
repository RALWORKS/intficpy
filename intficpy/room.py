from .physical_entity import PhysicalEntity
from .ifp_object import IFPObject
from .thing_base import Thing
from .things import Container, LightSource, Unremarkable

##############################################################
# ROOM.PY - verbs for IntFicPy
# Defines the Room class
##############################################################


class Room(PhysicalEntity):
    """A Room is a top-level location in the game.

    By default, a Room is assumed to be an indoor location with four walls,
    (north, south, east, and west), a floor, and a ceiling.

    Rooms can be connected directly to other Rooms by setting the direction
    attributes (north, northeast, etc.) of the Room.

    If a Room's `dark` attribute is set to True, the player will not be able
    to see while in the Room, unless a LightSource is present.

    :param game: the current game
    :type game: IFPObject
    :param name: the title of the room, to print when the player enters or looks
        around. Spaces are allowed. This name will *not* become a part of the
        parser's vocabulary.
    :type name: str
    :param desc: the base Room description, to be printed when the player enters this
        Room, or looks around. The descriptions of any Things the Room contains will
        be appeneded to this base.
    """

    def __init__(self, game, name, desc):
        super().__init__(game)
        self.is_top_level_location = True

        self.discovered = False
        # area or room type
        self.room_group = None
        # travel connections can be set to other Rooms after initialization
        self.north = None
        self.n_false_msg = "You cannot go north from here. "
        self.n_msg = "You go north. "
        self.northeast = None
        self.ne_false_msg = "You cannot go northeast from here. "
        self.ne_msg = "You go northeast. "
        self.east = None
        self.e_false_msg = "You cannot go east from here. "
        self.e_msg = "You go east. "
        self.southeast = None
        self.se_false_msg = "You cannot go southeast from here. "
        self.se_msg = "You go southeast. "
        self.south = None
        self.s_false_msg = "You cannot go south from here. "
        self.s_msg = "You go south. "
        self.southwest = None
        self.sw_false_msg = "You cannot go southwest from here. "
        self.sw_msg = "You go southwest. "
        self.west = None
        self.w_false_msg = "You cannot go west from here. "
        self.w_msg = "You go west. "
        self.northwest = None
        self.nw_false_msg = "You cannot go northwest from here. "
        self.nw_msg = "You go northwest. "
        self.up = None
        self.u_false_msg = "You cannot go up from here. "
        self.u_msg = "You go up. "
        self.down = None
        self.d_false_msg = "You cannot go down from here. "
        self.d_msg = "You go down. "
        self.entrance = None
        self.in_false_msg = "There is no obvious entrance here. "
        self.in_msg = "You enter. "
        self.exit = None
        self.out_false_msg = "There is no obvious exit here. "
        self.out_msg = "You exit. "

        # room properties
        self.name = name
        self.desc = desc
        self.fulldesc = ""
        self.hasWalls = False
        self.dark = False
        self.dark_desc = "It's too dark to see. "
        self.dark_msg = "It's too dark to find your way. "
        self.dark_visible_exits = []
        self.walls = []

        self.floor = Unremarkable(self.game, "floor")
        self.floor.addSynonym("ground")
        self.addThing(self.floor)

        self.ceiling = Unremarkable(self.game, "ceiling")
        self.addThing(self.ceiling)

        self.north_wall = Unremarkable(self.game, "wall")
        self.north_wall.addSynonym("walls")
        self.north_wall.setAdjectives(["north"])

        self.addThing(self.north_wall)
        self.walls.append(self.north_wall)

        self.south_wall = Unremarkable(self.game, "wall")
        self.south_wall.addSynonym("walls")
        self.south_wall.setAdjectives(["south"])

        self.addThing(self.south_wall)
        self.walls.append(self.south_wall)

        self.east_wall = Unremarkable(self.game, "wall")
        self.east_wall.addSynonym("walls")
        self.east_wall.setAdjectives(["east"])

        self.addThing(self.east_wall)
        self.walls.append(self.east_wall)

        self.west_wall = Unremarkable(self.game, "wall")
        self.west_wall.addSynonym("walls")
        self.west_wall.setAdjectives(["west"])

        self.addThing(self.west_wall)
        self.walls.append(self.west_wall)
        for wall in self.walls:
            wall.known_ix = None

    def getLocContents(self, game):
        """
        Create a sentence listing the other items in the player's immediate location,
        aside from the player.

        This is used in describing the Room when the player is inside/on top of/underneath
        or otherwise nested in a Thing inside this Room.

        :param game: the current game
        :type game: IFPGame
        :rtype: str, None
        """
        if len(game.me.location.contains.items()) > 1:
            onlist = (
                "Also "
                + game.me.location.contains_preposition
                + " "
                + game.me.location.getArticle(True)
                + game.me.location.verbose_name
                + " is "
            )
            # iterate through contents, appending the verbose_name of each to onlist
            list_version = list(game.me.location.contains.keys())
            list_version.remove(game.me.ix)
            for key in list_version:
                if len(game.me.location.contains[key]) > 1:
                    onlist = (
                        onlist
                        + str(len(things))
                        + " "
                        + game.me.location.contains[key][0].verbose_name
                    )
                else:
                    onlist = (
                        onlist
                        + game.me.location.contains[key][0].getArticle()
                        + game.me.location.contains[key][0].verbose_name
                    )
                if key is list_version[-1]:
                    onlist = onlist + "."
                elif key is list_version[-2]:
                    onlist = onlist + " and "
                else:
                    onlist = onlist + ", "
            self.fulldesc = self.fulldesc + onlist

    def resolveDarkness(self, game):
        """
        Determine if the player can see, based on this Room's `dark` attribute, and
        whether there is a lit LightSource present

        :param game: the current game
        :type game: IFPGame
        """
        can_see = True
        if self.dark:
            lightsource = None
            for key in self.contains:
                for item in self.contains[key]:
                    if isinstance(item, LightSource):
                        if item.is_lit:
                            lightsource = item
                            break
            for key in game.me.contains:
                for item in game.me.contains[key]:
                    if isinstance(item, LightSource):
                        if item.is_lit:
                            lightsource = item
                            break
            if not lightsource:
                can_see = False
        return can_see

    def describeDark(self, game):
        """
        If this Room is currently dark, describe the darkness. If the Room
        is lit by a LightSource, describe how the LightSource lights the
        Room.

        Return True if the player will be unable to see anything but darkness,
        and False otherwise.

        :param game: the current game
        :type game: IFPGame
        :rtype: bool
        """
        if not self.dark:
            return False

        lightsource = (
            (
                [
                    item
                    for key, sublist in self.contains.items()
                    for item in sublist
                    if getattr(item, "is_lit", False)
                ]
                + [
                    item
                    for key, sublist in game.me.contains.items()
                    for item in sublist
                    if getattr(item, "is_lit", False)
                ]
            )
            or [None]
        )[0]

        if lightsource:
            game.addTextToEvent("turn", lightsource.room_lit_msg)
            return False

        game.addTextToEvent("turn", self.dark_desc)
        return True

    def describe(self, game):
        """Generates and prints the Room description shown when the player enters this
        Room, or looks around.

        If it is too dark to see, only describe the darkness.
        Otherwise, print the Room description, and the descriptions of the Things that
        that are currently here.

        Returns False if it is too dark to see, and True otherwise.

        :param game: the current game
        :type game: IFPGame
        :rtype: bool
        """
        if self.describeDark(game):
            return False

        self.arriveFunc(game)
        self.updateDiscovered(game)

        self.fulldesc = self.desc
        desc_loc = False
        child_items = []
        for key, things in self.contains.items():
            for item in things:
                if item == game.me.location:
                    desc_loc = key
                elif item.parent_obj:
                    child_items.append(item.ix)
                # give player "knowledge" of a thing upon having it described
                if item.known_ix not in game.me.knows_about:
                    # game.me.knows_about.append(item.known_ix)
                    item.makeKnown(game.me)
                if item.desc_reveal:
                    for sub_item in item.topLevelContentsList:
                        sub_item.makeKnown(game.me)
            if desc_loc != key and key not in child_items and len(things) > 1:
                self.fulldesc = (
                    self.fulldesc
                    + " There are "
                    + str(len(things))
                    + " "
                    + things[0].plural
                    + " here. "
                )
            elif desc_loc != key and key not in child_items and len(things) > 0:
                self.fulldesc = self.fulldesc + things[0].desc
        if desc_loc:
            self.fulldesc = self.fulldesc + "<br>"
            if len(self.contains[desc_loc]) > 2:
                self.fulldesc = self.fulldesc + (
                    "You are "
                    + game.me.position
                    + " "
                    + game.me.location.contains_preposition
                    + " "
                    + game.me.location.getArticle()
                    + game.me.location.verbose_name
                    + ". "
                )
                self.getLocContents(game.me)
                self.fulldesc = self.fulldesc + (
                    "There are "
                    + str(len(self.contains[desc_loc]) - 1)
                    + " more "
                    + self.contains[desc_loc][0].plural
                    + " nearby. "
                )
            elif len(self.contains[desc_loc]) > 1:
                self.fulldesc = self.fulldesc + (
                    "You are "
                    + game.me.position
                    + " "
                    + game.me.location.contains_preposition
                    + " "
                    + game.me.location.getArticle()
                    + game.me.location.verbose_name
                    + ". "
                )
                self.getLocContents(game)
                self.fulldesc = self.fulldesc + (
                    "There is another "
                    + self.contains[desc_loc][0].verbose_name
                    + " nearby. "
                )
            else:
                self.fulldesc = self.fulldesc + (
                    "You are "
                    + game.me.position
                    + " "
                    + game.me.location.contains_preposition
                    + " "
                    + game.me.location.getArticle()
                    + game.me.location.verbose_name
                    + ". "
                )
                self.getLocContents(game)
        game.addTextToEvent("turn", "<b>" + self.name + "</b>")
        game.addTextToEvent("turn", self.fulldesc)
        self.descFunc(game)
        return True

    def updateDiscovered(self, game):
        """Check if the player has discovered this Room before. If not, carry out any
        behaviour that the creator has specified should occur on this Room's discovery,
        and mark this Room as discovered.

        :param game: the current game
        :type game: IFPGame
        """
        if not self.discovered:
            self.onDiscover(game)
            self.discovered = True

    def onDiscover(self, game):
        """Override this to trigger custom behaviour when the player "discovers" this
        Room.

        Discovery is not triggered until the player receives the description of this
        Room with full light, i.e. by entering/looking while *either* this Room's
        `dark` attribute is set to False (default), *or* a lit LightSource is present.

        :param game: the current game
        :type game: IFPGame
        """
        pass

    def arriveFunc(self, game):
        """Override this to trigger custom behaviour when the player enters this room
        or looks around, *before* the room description is printed.

        This will *not* trigger unless a LightSource is present if the Room is set
        to `dark=True`.

        :param game: the current game
        :type game: IFPGame
        """
        pass

    def descFunc(self, game):
        """Override this to trigger custom behaviour when the player enters this room
        or looks around, *after* the room description is printed.

        This will *not* trigger unless a LightSource is present if the Room is set
        to `dark=True`.

        :param game: the current game
        :type game: IFPGame
        """
        pass

    def contentsByClass(self, class_ref):
        """Get every Thing in the top level contents of this Room (i.e., not inside
        another Thing) that is an instance of a given Thing subclass. (For instance,
        get all top level Surfaces.)

        :param game: the current game
        :type game: IFPGame
        :param class_ref: the class to filter items on
        :type class_ref: type
        :rtype: list
        """
        return list(filter(lambda item: isinstance(item, class_ref), self.contentsList))


class OutdoorRoom(Room):
    """An OutdoorRoom is a Room with no walls, with ground instead of a floor, and with
    sky instead of a ceiling.

    :param game: the current game
    :type game: IFPObject
    :param name: the title of the room, to print when the player enters or looks
        around. Spaces are allowed. This name will *not* become a part of the
        parser's vocabulary.
    :type name: str
    :param desc: the base Room description, to be printed when the player enters this
        Room, or looks around. The descriptions of any Things the Room contains will
        be appeneded to this base.
    """

    def __init__(self, game, name, desc):
        """Initially set basic properties for the OutdoorRoom instance """
        # indexing for save
        super().__init__(game, name, desc)

        for wall in self.walls:
            self.removeThing(wall)
        self.walls = []

        self.floor.addSynonym("ground")
        self.floor.name = "ground"
        self.floor.full_name = "ground"
        self.floor.removeSynonym("floor")
        self.floor.xdescribeThing("You notice nothing remarkable about the ground. ")

        self.ceiling = Thing(self.game, "sky")
        self.ceiling.known_ix = None
        self.ceiling.invItem = False
        self.ceiling.far_away = True
        self.ceiling.describeThing("")
        self.ceiling.xdescribeThing("You notice nothing remarkable about the sky. ")
        self.addThing(self.ceiling)


class RoomGroup(IFPObject):
    """RoomGroup provides convenience features for modifying aspects of several Rooms
    at once. In particular, it allows creators to quickly set & update the ceilings and
    or floors of all Rooms in the group at once.

    This can be useful for making larger scale changes during play. For instance,
    RoomGroup allows the creator to update the skies of a group of OutdoorRooms all
    at once, identically, to reflect weather.

    Member Rooms can be added individually with `addMember`, or in a bulk with `setMembers`.
    The members can be updated all at once with `updateMembers`

    :param game: the current game
    :type game: IFPObject
    """

    def __init__(self, game):
        super().__init__(game)
        self.members = []
        self.ceiling = None
        self.floor = None
        # not yet implemented
        self.listen_desc = None
        self.smell_desc = None

    def setGroupCeiling(self, ceiling):
        """Change the ceiling/sky for all member Rooms to match the ceiling (Thing) provided.

        :param ceiling: a Thing instance with attributes set to the desired values. The
            ceilings/skies of all Rooms and OutdoorRooms in this RoomGroup will have their
            attributes set to match those of the Thing provided.
        :type ceiling: Thing
        """
        self.ceiling = ceiling
        if self.ceiling:
            for item in self.members:
                item.ceiling.setFromPrototype(ceiling)

    def setGroupFloor(self, floor):
        """Change the floor/ground for all member Rooms to match the floor (Thing) provided.

        :param floor: a Thing instance with attributes set to the desired values. The
            floors/ground of all Rooms and OutdoorRooms in this RoomGroup will have their
            attributes set to match those of the Thing provided.
        :type floor: Thing
        """
        self.floor = floor
        if self.floor:
            for item in self.members:
                item.floor.setFromPrototype(floor)

    def updateMembers(self):
        """Refresh the member Rooms to match the current ceiling, floor, etc. for this
        RoomGroup
        """
        self.setGroupFloor(self.floor)
        self.setGroupCeiling(self.floor)

    def addMember(self, member):
        """Add a single Room to this RoomGroup

        :param member: the Room or OutdoorRoom to add to this RoomGroup
        :type member: Room
        """
        self.members.append(member)
        if self.ceiling:
            member.ceiling.setFromPrototype(self.ceiling)
        if self.floor:
            member.floor.setFromPrototype(self.floor)
        member.room_group = self

    def setMembers(self, members_arr):
        """Add a list of Rooms to this RoomGroup

        :param members_arr: the list of Rooms to add to this RoomGroup
        :type members_arr: list of Room objects
        """
        self.members = []
        for item in members_arr:
            self.addMember(item)

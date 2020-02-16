from .physical_entity import PhysicalEntity
from .ifp_object import IFPObject
from .thing_base import Thing
from .things import Container, LightSource

##############################################################
# ROOM.PY - verbs for IntFicPy
# Defines the Room class
##############################################################


class Room(PhysicalEntity):
    """Room is the overarching class for all locations in an .game """

    def __init__(self, name, desc):
        super().__init__()
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
        self.entrance_false_msg = "There is no obvious entrance here. "
        self.entrance_msg = "You enter. "
        self.exit = None
        self.exit_false_msg = "There is no obvious exit here. "
        self.exit_msg = "You exit. "

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

        self.floor = Thing("floor")
        self.floor.known_ix = None
        self.floor.addSynonym("ground")
        self.floor.invItem = False
        self.floor.describeThing("")
        self.floor.xdescribeThing("You notice nothing remarkable about the floor. ")
        self.addThing(self.floor)

        self.ceiling = Thing("ceiling")
        self.ceiling.known_ix = None
        self.ceiling.invItem = False
        self.ceiling.far_away = True
        self.ceiling.describeThing("")
        self.ceiling.xdescribeThing("You notice nothing remarkable about the ceiling. ")
        self.addThing(self.ceiling)

        self.north_wall = Thing("wall")
        self.north_wall.addSynonym("walls")
        self.north_wall.setAdjectives(["north"])
        self.north_wall.invItem = False
        self.north_wall.describeThing("")
        self.north_wall.xdescribeThing(
            "You notice nothing remarkable about the north wall. "
        )
        self.addThing(self.north_wall)
        self.walls.append(self.north_wall)

        self.south_wall = Thing("wall")
        self.south_wall.addSynonym("walls")
        self.south_wall.setAdjectives(["south"])
        self.south_wall.invItem = False
        self.south_wall.describeThing("")
        self.south_wall.xdescribeThing(
            "You notice nothing remarkable about the south wall. "
        )
        self.addThing(self.south_wall)
        self.walls.append(self.south_wall)

        self.east_wall = Thing("wall")
        self.east_wall.addSynonym("walls")
        self.east_wall.setAdjectives(["east"])
        self.east_wall.invItem = False
        self.east_wall.describeThing("")
        self.east_wall.xdescribeThing(
            "You notice nothing remarkable about the east wall. "
        )
        self.addThing(self.east_wall)
        self.walls.append(self.east_wall)

        self.west_wall = Thing("wall")
        self.west_wall.addSynonym("walls")
        self.west_wall.setAdjectives(["west"])
        self.west_wall.invItem = False
        self.west_wall.describeThing("")
        self.west_wall.xdescribeThing(
            "You notice nothing remarkable about the west wall. "
        )
        self.addThing(self.west_wall)
        self.walls.append(self.west_wall)
        for wall in self.walls:
            wall.known_ix = None

    def getLocContents(self, game):
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

    def describe(self, game):
        """Prints the Room title and description and lists items in the Room """
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
            if lightsource:
                game.addTextToEvent("turn", lightsource.room_lit_msg)
            else:
                game.addTextToEvent("turn", self.dark_desc)
                return False
        self.updateDiscovered(game)
        self.arriveFunc(game)
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
            if desc_loc != key and key not in child_items and len(things) > 1:
                self.fulldesc = (
                    self.fulldesc
                    + " There are "
                    + str(len(things))
                    + " "
                    + things[0].getPlural()
                    + " here. "
                )
            elif desc_loc != key and key not in child_items and len(things) > 0:
                self.fulldesc = self.fulldesc + " " + things[0].desc
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
                    + self.contains[desc_loc][0].getPlural
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
        """Call onDiscovery if not discovered yet. Set discovered to true. """
        if not self.discovered:
            self.onDiscover(game)
            self.discovered = True

    def onDiscover(self, game):
        """Operations to perform the first time the room is described. Empty by default. Override for custom events. """
        pass

    def arriveFunc(self, game):
        """Operations to perform each time the player arrives in the room, before the description is printed. Empty by default. Override for custom events. """
        pass

    def descFunc(self, game):
        """Operations to perform immediately after printing the room description. Empty by default. Override for custom events. """
        pass

    def contentsByClass(self, class_ref):
        """
        Get all top level contents of a given class
        """
        return list(filter(lambda item: isinstance(item, class_ref), self.contentsList))

    @property
    def contentsList(self):
        """
        Return the room contents as a flattened list
        """
        return [item for ix, sublist in self.contains.items() for item in sublist] + [
            item for ix, sublist in self.sub_contains.items() for item in sublist
        ]


class OutdoorRoom(Room):
    """Room is the class for outdoor locations in an .game
	OutdoorRooms have no walls, and the floor is called ground"""

    def __init__(self, name, desc):
        """Initially set basic properties for the OutdoorRoom instance """
        # indexing for save
        super().__init__(name, desc)

        for wall in self.walls:
            self.removeThing(wall)
        self.walls = []

        self.floor.addSynonym("ground")
        self.floor.name = "ground"
        self.floor.verbose_name = "ground"
        self.floor.removeSynonym("floor")
        self.floor.xdescribeThing("You notice nothing remarkable about the ground. ")

        self.ceiling = Thing("sky")
        self.ceiling.known_ix = None
        self.ceiling.invItem = False
        self.ceiling.far_away = True
        self.ceiling.describeThing("")
        self.ceiling.xdescribeThing("You notice nothing remarkable about the sky. ")
        self.addThing(self.ceiling)


class RoomGroup(IFPObject):
    """Group similar Rooms and OutdoorRooms to modify shared features """

    def __init__(self):
        super().__init__
        self.members = []
        self.ceiling = None
        self.floor = None
        # not yet implemented
        self.listen_desc = None
        self.smell_desc = None

    def setGroupCeiling(self, ceiling):
        self.ceiling = ceiling
        if self.ceiling:
            for item in self.members:
                item.ceiling.setFromPrototype(ceiling)

    def setGroupFloor(self, floor):
        self.floor = floor
        if self.floor:
            for item in self.members:
                item.floor.setFromPrototype(floor)

    def updateMembers(self):
        self.setGroupFloor(self.floor)
        self.setGroupCeiling(self.floor)

    def addMember(self, member):
        self.members.append(member)
        if self.ceiling:
            member.ceiling.setFromPrototype(self.ceiling)
        if self.floor:
            member.floor.setFromPrototype(self.floor)
        member.room_group = self

    def setMembers(self, members_arr):
        self.members = []
        for item in members_arr:
            self.addMember(item)

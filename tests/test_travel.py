from .helpers import IFPTestCase

from intficpy.exceptions import IFPError
from intficpy.room import Room
from intficpy.things import Container, Surface, Lock
from intficpy.travel import (
    travelN,
    travelNE,
    travelE,
    travelSE,
    travelS,
    travelSW,
    travelW,
    travelNW,
    travelU,
    travelD,
    travelIn,
    travelOut,
    TravelConnector,
    DoorConnector,
    LadderConnector,
    StaircaseConnector,
)


class TestDirectionTravel(IFPTestCase):
    def test_cannot_travel_if_not_connection(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        self.assertTrue(
            (
                not room1.north
                and not room1.northeast
                and not room1.east
                and not room1.southeast
                and not room1.south
                and not room1.southwest
                and not room1.west
                and not room1.northwest
                and not room1.up
                and not room1.down
                and not room1.entrance
                and not room1.exit
            ),
            "This test needs room1 to have no directional connections.",
        )
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)

        self.game.turnMain("n")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.n_false_msg)

        self.game.turnMain("ne")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.ne_false_msg)

        self.game.turnMain("e")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.e_false_msg)

        self.game.turnMain("se")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.se_false_msg)

        self.game.turnMain("s")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.s_false_msg)

        self.game.turnMain("sw")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.sw_false_msg)

        self.game.turnMain("w")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.w_false_msg)

        self.game.turnMain("nw")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.nw_false_msg)

        self.game.turnMain("u")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.u_false_msg)

        self.game.turnMain("d")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.d_false_msg)

        self.game.turnMain("in")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.in_false_msg)

        self.game.turnMain("out")
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.out_false_msg)

    def test_travel_north_south(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        room1.north = room2
        room2.south = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        self.game.turnMain("go n")
        self.assertEqual(self.app.print_stack[-3], room1.n_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel north to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        self.game.turnMain("s")

        self.assertEqual(self.app.print_stack[-3], room1.s_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel south to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_northeast_southwest(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        room1.northeast = room2
        room2.southwest = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        self.game.turnMain("go northeast")

        self.assertEqual(self.app.print_stack[-3], room1.ne_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel northeast to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        self.game.turnMain("southwest")

        self.assertEqual(self.app.print_stack[-3], room1.sw_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel southwest to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_east_west(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        room1.east = room2
        room2.west = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        self.game.turnMain("go e")

        self.assertEqual(self.app.print_stack[-3], room1.e_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel east to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        self.game.turnMain("w")

        self.assertEqual(self.app.print_stack[-3], room1.w_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel west to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_southeast_northwest(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        room1.southeast = room2
        room2.northwest = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        self.game.turnMain("go southeast")

        self.assertEqual(self.app.print_stack[-3], room1.se_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel southeast to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        self.game.turnMain("go northwest")

        self.assertEqual(self.app.print_stack[-3], room1.nw_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel northwest to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_up_down(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        room1.up = room2
        room2.down = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        self.game.turnMain("u")

        self.assertEqual(self.app.print_stack[-3], room1.u_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel up to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        self.game.turnMain("go d")
        self.assertEqual(self.app.print_stack[-3], room1.d_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel down to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_in_out(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        room1.entrance = room2
        room2.exit = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        self.game.turnMain("enter")

        self.assertEqual(self.app.print_stack[-3], room1.in_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel in to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        self.game.turnMain("exit")

        self.assertEqual(self.app.print_stack[-3], room1.out_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel out to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )


class TestTravelConnectors(IFPTestCase):
    def _assert_can_travel(self, room1, room2, command, return_command):
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        self.game.turnMain(command)
        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        self.game.turnMain(return_command)
        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_create_TravelConnector_with_invalid_direction(self):
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        with self.assertRaises(IFPError):
            c = TravelConnector(
                self.game, self.start_room, "lllllllrrrrrkkkk", room2, "s"
            )

    def test_cannot_travel_blocked_connector(self):
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = TravelConnector(self.game, self.start_room, "n", room2, "s")
        c.can_pass = False

        self.assertItemIn(
            self.me, self.start_room.contains, "test needs player to start here"
        )
        self.assertIs(self.start_room.north, c)

        self.game.turnMain("n")

        self.assertIn(c.cannot_pass_msg, self.app.print_stack)

        self.assertIs(self.me.location, self.start_room)
        self.assertItemIn(
            self.me, self.start_room.contains, "player should not have moved"
        )

    def test_cannot_travel_if_barrier_function_blocks(self):
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = TravelConnector(self.game, self.start_room, "n", room2, "s")
        c.barrierFunc = lambda g: True

        self.assertItemIn(
            self.me, self.start_room.contains, "test needs player to start here"
        )
        self.assertIs(self.start_room.north, c)

        self.game.turnMain("n")

        self.assertIs(self.me.location, self.start_room)
        self.assertItemIn(
            self.me, self.start_room.contains, "player should not have moved"
        )

    def test_cannot_travel_in_darkness(self):
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = TravelConnector(self.game, self.start_room, "n", room2, "s")
        self.start_room.dark = True

        self.assertItemIn(
            self.me, self.start_room.contains, "test needs player to start here"
        )
        self.assertIs(self.start_room.north, c)

        self.game.turnMain("n")

        self.assertIn("It's too dark to find your way. ", self.app.print_stack)

        self.assertIs(self.me.location, self.start_room)
        self.assertItemIn(
            self.me, self.start_room.contains, "player should not have moved"
        )

    def test_can_travel_TravelConnector(self):
        self.me.position = "sitting"
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = TravelConnector(self.game, room1, "n", room2, "s")
        c.entrance_a_msg = "You creep north. "

        self._assert_can_travel(room1, room2, "n", "s")
        self.assertIn("You stand up. ", self.app.print_stack)
        self.assertEqual(self.me.position, "standing")
        self.assertIn(c.entrance_a_msg, self.app.print_stack)
        self.assertIn("You go through the south doorway. ", self.app.print_stack)
        self.assertIn(
            room1.desc + "There is a doorway to the north. ", self.app.print_stack
        )

    def test_can_travel_DoorConnector(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = DoorConnector(self.game, room1, "n", room2, "s")
        c.entrance_a.makeClosed()

        self._assert_can_travel(room1, room2, "n", "s")
        self.assertIn("You open the north door. ", self.app.print_stack)
        self.assertIn("You go through the north door. ", self.app.print_stack)
        self.assertIn("You go through the south door. ", self.app.print_stack)
        self.assertIn(
            room1.desc + "There is a door to the north. It is open. ",
            self.app.print_stack,
        )

    def test_cannot_travel_closed_and_locked_door(self):
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = DoorConnector(self.game, self.start_room, "n", room2, "s")
        lock = Lock(self.game, is_locked=True, key_obj=None)
        c.setLock(lock)

        self.assertItemIn(
            self.me, self.start_room.contains, "test needs player to start here"
        )
        self.assertIs(self.start_room.north, c)

        self.game.turnMain("n")

        self.assertIn(
            f"{c.entrance_a.capNameArticle(True)} is locked. ", self.app.print_stack
        )

        self.assertIs(self.me.location, self.start_room)
        self.assertItemIn(
            self.me, self.start_room.contains, "player should not have moved"
        )

    def test_cannot_set_non_lock_as_door_lock(self):
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = DoorConnector(self.game, self.start_room, "n", room2, "s")
        lock = Surface(self.game, "lock?")
        with self.assertRaises(IFPError):
            c.setLock(lock)

    def test_lock_already_attached_to_something_cannot_be_applied_to_a_door(self):
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = DoorConnector(self.game, self.start_room, "n", room2, "s")
        lock = Lock(self.game, is_locked=True, key_obj=None)
        c.setLock(lock)
        c2 = DoorConnector(self.game, self.start_room, "e", room2, "w")
        with self.assertRaises(IFPError):
            c2.setLock(lock)

    def test_can_travel_LadderConnector(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = LadderConnector(self.game, room1, room2)

        self._assert_can_travel(room1, room2, "u", "d")
        self.assertIn("You climb up the upward ladder. ", self.app.print_stack)
        self.assertIn("You climb down the downward ladder. ", self.app.print_stack)
        self.assertIn(room1.desc + "A ladder leads up. ", self.app.print_stack)

    def test_can_travel_StaircaseConnector(self):
        room1 = Room(self.game, "A place", "Description of a place. ")
        room2 = Room(
            self.game, "A different place", "Description of a different place. "
        )
        c = StaircaseConnector(self.game, room1, room2)

        self._assert_can_travel(room1, room2, "u", "d")
        self.assertIn("You climb up the upward staircase. ", self.app.print_stack)
        self.assertIn("You climb down the downward staircase. ", self.app.print_stack)
        self.assertIn(room1.desc + "A staircase leads up. ", self.app.print_stack)


class TestExitVerb(IFPTestCase):
    def test_exit_container(self):
        thing = Container(self.game, "box")
        thing.moveTo(self.start_room)
        self.game.me.moveTo(thing)

        self.game.turnMain("exit")

        self.assertFalse(
            thing.containsItem(self.game.me), "Player should have left the Container"
        )

    def test_exit_surface(self):
        thing = Surface(self.game, "tray")
        thing.moveTo(self.start_room)
        self.game.me.moveTo(thing)

        self.game.turnMain("exit")

        self.assertFalse(
            thing.containsItem(self.game.me), "Player should have left the Container"
        )


class TestNestedPlayer(IFPTestCase):
    def test_implicit_exit_container(self):
        meta_thing = Container(self.game, "metabox")
        thing = Container(self.game, "box")
        thing.moveTo(meta_thing)
        meta_thing.moveTo(self.start_room)
        self.game.me.moveTo(thing)

        room2 = Room(self.game, "new place", "You are in a new place.")
        self.start_room.east = room2

        self.assertTrue(self.start_room.subLevelContainsItem(self.game.me))

        self.game.turnMain("e")

        self.assertFalse(
            thing.containsItem(self.game.me), "Player should have left the Container"
        )
        self.assertFalse(self.start_room.subLevelContainsItem(self.game.me))

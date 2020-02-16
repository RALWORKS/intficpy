import unittest

from .helpers import IFPTestCase

from intficpy.room import Room
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
        room1 = Room("A place", "Description of a place. ")
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

        travelN(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.n_false_msg)

        travelNE(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.ne_false_msg)

        travelE(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.e_false_msg)

        travelSE(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.se_false_msg)

        travelS(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.s_false_msg)

        travelSW(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.sw_false_msg)

        travelW(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.w_false_msg)

        travelNW(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.nw_false_msg)

        travelU(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.u_false_msg)

        travelD(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.d_false_msg)

        travelIn(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.entrance_false_msg)

        travelOut(self.game)
        self.game.runTurnEvents()
        self.assertIs(self.me.location, room1)
        self.assertEqual(self.app.print_stack.pop(), room1.exit_false_msg)

    def test_travel_north_south(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        room1.north = room2
        room2.south = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        travelN(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.n_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel north to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        travelS(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.s_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel south to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_northeast_southwest(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        room1.northeast = room2
        room2.southwest = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        travelNE(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.ne_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel northeast to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        travelSW(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.sw_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel southwest to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_east_west(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        room1.east = room2
        room2.west = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        travelE(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.e_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel east to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        travelW(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.w_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel west to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_southeast_northwest(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        room1.southeast = room2
        room2.northwest = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        travelSE(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.se_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel southeast to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        travelNW(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.nw_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel northwest to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_up_down(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        room1.up = room2
        room2.down = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        travelU(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.u_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel up to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        travelD(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.d_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel down to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_travel_in_out(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        room1.entrance = room2
        room2.exit = room1
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        travelIn(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.entrance_msg)

        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel in to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        travelOut(self.game)
        self.game.runTurnEvents()

        self.assertEqual(self.app.print_stack[-3], room1.exit_msg)

        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel out to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )


class TestTravelConnectors(IFPTestCase):
    def _assert_can_travel(self, room1, room2, connector):
        self.me.location.removeThing(self.me)
        room1.addThing(self.me)
        self.assertIs(
            self.me.location, room1, "This test needs the user to start in room1"
        )

        connector.travel(self.game)
        self.assertIs(
            self.me.location,
            room2,
            f"Tried to travel {connector} to {room2}, '{room2.name}', but player in "
            f"{self.me.location}",
        )

        connector.travel(self.game)
        self.assertIs(
            self.me.location,
            room1,
            f"Tried to travel {connector} to {room1}, '{room1.name}', but player in "
            f"{self.me.location}",
        )

    def test_can_travel_TravelConnector(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        c = TravelConnector(room1, "n", room2, "s")

        self._assert_can_travel(room1, room2, c)

    def test_can_travel_DoorConnector(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        c = DoorConnector(room1, "n", room2, "s")

        self._assert_can_travel(room1, room2, c)

    def test_can_travel_LadderConnector(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        c = LadderConnector(room1, room2)

        self._assert_can_travel(room1, room2, c)

    def test_can_travel_StaircaseConnector(self):
        room1 = Room("A place", "Description of a place. ")
        room2 = Room("A different place", "Description of a different place. ")
        c = StaircaseConnector(room1, room2)

        self._assert_can_travel(room1, room2, c)


if __name__ == "__main__":
    unittest.main()

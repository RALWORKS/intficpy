from ..helpers import IFPTestCase

from intficpy.room import Room
from intficpy.thing_base import Thing
from intficpy.things import (
    Surface,
    Container,
    UnderSpace,
    Readable,
)


class TestLookVerbs(IFPTestCase):
    def test_look(self):
        room = Room(self.game, "Strange Room", "It's strange in here. ")
        item = Thing(self.game, "hullabaloo")
        item.describeThing("All around is a hullabaloo. ")
        room.addThing(item)

        self.me.location.removeThing(self.me)
        room.addThing(self.me)

        self.game.turnMain("look")
        look_desc = self.app.print_stack.pop()
        look_title = self.app.print_stack.pop()

        self.assertIn(room.name, look_title, f"Room title printed incorrectly")
        self.assertIn(room.desc, look_desc, "Room description not printed by look")
        self.assertIn(item.desc, look_desc, "Item description not printed by look")

    def test_examine(self):
        item = Thing(self.game, "widget")
        item.xdescribeThing("It's a shiny little widget. ")
        item.moveTo(self.start_room)

        self.game.turnMain("x widget")

        examine_desc = self.app.print_stack.pop()

        self.assertEqual(
            examine_desc,
            item.xdesc,
            f"Examine desc printed incorrectly. Expecting {item.xdesc}, got {examine_desc}",
        )

    def test_look_in(self):
        parent = Container(self.game, "shoebox")
        child = Thing(self.game, "penny")
        parent.addThing(child)
        parent.moveTo(self.start_room)

        self.game.turnMain("look in shoebox")

        look_in_desc = self.app.print_stack.pop()

        self.assertEqual(
            look_in_desc,
            parent.contains_desc,
            f"Contains desc printed incorrectly. Expected {parent.contains_desc} got "
            f"{look_in_desc}",
        )

    def test_look_under(self):
        parent = UnderSpace(self.game, "table")
        child = Thing(self.game, "penny")
        parent.addThing(child)
        parent.moveTo(self.start_room)

        self.game.turnMain("look under table")

        look_under_desc = self.app.print_stack.pop()

        self.assertEqual(
            look_under_desc,
            parent.contains_desc,
            f"Contains desc printed incorrectly. Expected {parent.contains_desc} got "
            f"{look_under_desc}",
        )

    def test_look_under_empty_underspace(self):
        parent = UnderSpace(self.game, "table")
        parent.moveTo(self.start_room)

        self.game.turnMain("look under table")

        self.assertIn("There is nothing under the table. ", self.app.print_stack)

    def test_look_under_non_underspace_inv_item(self):
        child = Thing(self.game, "penny")
        child.moveTo(self.start_room)

        self.game.turnMain("look under penny")

        self.assertIn("You take the penny. ", self.app.print_stack)
        self.assertIn("You find nothing underneath. ", self.app.print_stack)

    def test_look_under_non_underspace_non_inv_item(self):
        child = Thing(self.game, "mountain")
        child.invItem = False
        child.moveTo(self.start_room)

        self.game.turnMain("look under mountain")

        self.assertIn(
            "There's no reason to look under the mountain. ", self.app.print_stack
        )

    def test_read(self):
        item = Readable(self.game, "note", "I'm sorry, but I have to do this. ")
        item.moveTo(self.start_room)

        self.game.turnMain("read note")

        read_desc = self.app.print_stack.pop()

        self.assertEqual(
            read_desc,
            item.read_desc,
            f"Item text printed incorrectly. Expecting {item.read_desc}, got {read_desc}",
        )

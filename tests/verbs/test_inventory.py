from ..helpers import IFPTestCase

from intficpy.things import (
    Thing,
    Container,
    Clothing,
)


class TestEmptyInventory(IFPTestCase):
    def test_view_empty_inv(self):
        self.game.turnMain("drop all")
        self.assertEqual(
            len(self.me.contains), 0, "This test requires an empty player inventory"
        )

        EMPTY_INV_MSG = "You don't have anything with you. "

        self.game.turnMain("i")
        inv_msg = self.app.print_stack.pop()

        self.assertEqual(
            inv_msg,
            EMPTY_INV_MSG,
            "Viewed empty inventory. Message does not match expected. ",
        )


class TestFullInventory(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.parent = Thing(self.game, "cube")
        self.child = Container(self.game, "slot")
        self.container = Container(self.game, "box")
        self.nested_item = Thing(self.game, "bead")
        self.nested_item.moveTo(self.container)
        self.parent.addComposite(self.child)
        self.stacked1 = Thing(self.game, "tile")
        self.stacked2 = self.stacked1.copyThing()
        self.clothing = Clothing(self.game, "scarf")
        self.clothing1 = Clothing(self.game, "mitten")
        self.clothing2 = self.clothing1.copyThing()
        self.clothing3 = Clothing(self.game, "hat")

        self.me.addThing(self.parent)
        self.me.addThing(self.child)
        self.me.addThing(self.container)
        self.me.addThing(self.stacked1)
        self.me.addThing(self.stacked2)
        self.me.addThing(self.clothing)
        self.me.addThing(self.clothing1)
        self.me.addThing(self.clothing2)
        self.me.addThing(self.clothing3)

        self.game.turnMain("wear scarf")
        self.game.turnMain("wear hat")
        self.game.turnMain("wear mitten")
        self.game.turnMain("wear mitten")

    def strip_desc(self, desc):
        desc = desc.replace(". ", "").replace(",", "").replace("and", "")
        return " ".join(desc.split())

    def test_inventory_items_desc(self):
        BASE_MSG = "You have"

        self.game.turnMain("i")
        self.app.print_stack.pop()
        inv_desc = self.app.print_stack.pop()

        self.assertIn("You have", inv_desc)

        stacked_desc = (
            f"{len(self.me.contains[self.stacked1.ix])} {self.stacked1.plural}"
        )
        self.assertIn(
            stacked_desc, inv_desc, "Stacked item description should be in inv desc"
        )

        self.assertIn(
            "a cube", inv_desc,
        )

        self.assertIn("a box (in the box is a bead.)", inv_desc)

    def test_inventory_wearing_desc(self):
        BASE_MSG = "You are wearing"

        self.game.turnMain("i")
        wearing_desc = self.app.print_stack.pop()

        self.assertIn(
            "a hat", wearing_desc, "Clothing item description should be in inv desc",
        )
        self.assertIn(
            "a scarf", wearing_desc, "Clothing item description should be in inv desc",
        )
        self.assertIn(
            "mittens",
            wearing_desc,
            "Stacked clothing item description should be in inv desc",
        )

from ..helpers import IFPTestCase

from intficpy.thing_base import Thing


class TestInventoryVerbs(IFPTestCase):
    def test_get_all_drop(self):
        item1 = Thing(self.game, "miracle")
        item2 = Thing(self.game, "wonder")
        item1.invItem = True
        item2.invItem = True
        item3 = item2.copyThing()
        item1.makeKnown(self.me)
        item3.makeKnown(self.me)
        self.start_room.addThing(item1)
        self.start_room.addThing(item3)
        self.me.addThing(item2)

        self.assertNotIn(item1.ix, self.me.contains)
        self.assertIn(item2.ix, self.me.contains)
        self.assertNotIn(item3, self.me.contains[item2.ix])

        self.game.turnMain("take all")
        getall_msg = self.app.print_stack.pop()

        self.assertIn(
            item1.ix,
            self.me.contains,
            f"Item not added to inv with get all. Msg: '{getall_msg}'",
        )
        self.assertIn(item1, self.me.contains[item1.ix])
        self.assertIn(
            item2.ix,
            self.me.contains,
            f"Item not added to inv with get all. Msg: '{getall_msg}'",
        )
        self.assertIn(item2, self.me.contains[item2.ix])

        self.game.turnMain("take all")
        getall_msg = self.app.print_stack.pop()
        self.assertEqual(getall_msg, "There are no obvious items here to take. ")

    def test_drop_all(self):
        item1 = Thing(self.game, "miracle")
        item2 = Thing(self.game, "wonder")
        item1.invItem = True
        item2.invItem = True
        item1.makeKnown(self.me)
        item2.makeKnown(self.me)
        self.me.addThing(item1)
        self.me.addThing(item2)

        self.assertIs(
            self.me.location,
            self.start_room,
            "This test needs the Player to be in the start room",
        )

        self.game.turnMain("drop all")
        dropall_msg = self.app.print_stack.pop()

        self.assertEqual(
            len(self.me.contains),
            0,
            f"Expected empty inv, but found {self.me.contains}",
        )

        self.assertIn(item1.ix, self.start_room.contains)
        self.assertIn(item1, self.start_room.contains[item1.ix])
        self.assertIn(item2.ix, self.start_room.contains)
        self.assertIn(item2, self.start_room.contains[item2.ix])
        self.game.turnMain("drop all")
        dropall_msg = self.app.print_stack.pop()
        self.assertEqual(dropall_msg, "Your inventory is empty. ")

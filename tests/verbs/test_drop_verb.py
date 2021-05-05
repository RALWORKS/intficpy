from ..helpers import IFPTestCase

from intficpy.things import Thing, Container, Liquid


class TestDropVerb(IFPTestCase):
    def test_verb_func_drops_item(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        self.assertIn(item.ix, self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

        self.game.turnMain(f"drop {item.verbose_name}")

        self.assertItemNotIn(
            item, self.me.contains, "Dropped item, but item still in inventory"
        )

    def test_drop_item_not_in_inv(self):
        item = Thing(self.game, "shoe")
        item.invItem = True
        self.start_room.addThing(item)
        self.assertFalse(self.me.containsItem(item))

        self.game.turnMain(f"drop {item.verbose_name}")
        self.assertIn("You are not holding", self.app.print_stack.pop())

    def test_drop_liquid_in_container(self):
        cup = Container(self.game, "cup")
        water = Liquid(self.game, "water", "water")
        water.moveTo(cup)
        cup.moveTo(self.me)
        self.game.turnMain("drop water")
        self.assertIn("You drop the cup", self.app.print_stack.pop())
        self.assertFalse(self.game.me.containsItem(cup))
        self.assertTrue(cup.containsItem(water))

    def test_drop_composite_child(self):
        machine = Thing(self.game, "machine")
        wheel = Thing(self.game, "wheel")
        machine.addComposite(wheel)
        machine.moveTo(self.me)
        self.game.turnMain("drop wheel")
        self.assertIn("wheel is attached to the machine", self.app.print_stack.pop())
        self.assertTrue(self.me.containsItem(wheel))

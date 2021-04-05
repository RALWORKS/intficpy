from ..helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import Surface, Container
from intficpy.verb import GetVerb


class TestGetVerb(IFPTestCase):
    def test_verb_func_adds_invitem_to_inv(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.start_room.addThing(item)

        success = GetVerb()._runVerbFuncAndEvents(self.game, item)
        self.assertTrue(success)

        self.assertIn(item.ix, self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

    def test_verb_func_does_not_add_to_inv_where_invitem_false(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = False
        self.start_room.addThing(item)

        self.assertFalse(item.ix in self.me.contains)

        success = GetVerb()._runVerbFuncAndEvents(self.game, item)
        self.assertFalse(success)

        self.assertNotIn(item.ix, self.me.contains)

    def test_verb_func_does_not_add_to_inv_where_already_in_inv(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        self.assertTrue(item.ix in self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

        success = GetVerb()._runVerbFuncAndEvents(self.game, item)
        self.assertFalse(success)

        self.assertEqual(len(self.me.contains[item.ix]), 1)

    def test_get_item_when_pc_is_in_container(self):
        loc = Container(self.game, "box")
        loc.moveTo(self.start_room)
        loc.can_contain_standing_player = True

        sub_loc = Container(self.game, "vase")
        sub_loc.moveTo(loc)
        sub_loc.can_contain_standing_player = True

        self.game.me.moveTo(sub_loc)

        self.game.turnMain(f"take box")

        self.assertIn("You climb out of the box. ", self.app.print_stack)

    def test_get_item_when_pc_is_on_surface(self):
        loc = Surface(self.game, "desk")
        loc.moveTo(self.start_room)
        loc.can_contain_standing_player = True

        sub_loc = Surface(self.game, "box")
        sub_loc.moveTo(loc)
        sub_loc.can_contain_standing_player = True

        self.game.me.moveTo(sub_loc)

        self.game.turnMain(f"take desk")

        self.assertIn("You climb down from the desk. ", self.app.print_stack)

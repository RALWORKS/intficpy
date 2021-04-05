from ..helpers import IFPTestCase

from intficpy.thing_base import Thing
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

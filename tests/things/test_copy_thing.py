from ..helpers import IFPTestCase

from intficpy.thing_base import Thing


class TestCopyThing(IFPTestCase):
    def test_new_thing_has_empty_contains_and_sub_contains(self):
        orig = Thing(self.app.game, "bulb")
        child = Thing(self.app.game, "seed")
        sub_child = Thing(self.app.game, "life")
        sub_child.moveTo(child)
        child.moveTo(orig)
        self.assertTrue(orig.contains)
        self.assertTrue(orig.sub_contains)
        replica = orig.copyThing()
        self.assertFalse(replica.contains)
        self.assertFalse(replica.sub_contains)


class TestCopyThingUniqueIx(IFPTestCase):
    def test_new_thing_has_empty_contains_and_sub_contains(self):
        orig = Thing(self.app.game, "bulb")
        child = Thing(self.app.game, "seed")
        sub_child = Thing(self.app.game, "life")
        sub_child.moveTo(child)
        child.moveTo(orig)
        self.assertTrue(orig.contains)
        self.assertTrue(orig.sub_contains)
        replica = orig.copyThingUniqueIx()
        self.assertFalse(replica.contains)
        self.assertFalse(replica.sub_contains)

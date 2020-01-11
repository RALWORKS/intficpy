import unittest

from .helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.object_maps import things, actors
from intficpy.things import Surface, Container, UnderSpace, Liquid, Lock
from intficpy.actor import Actor


def make_thing_instantiation_test(thing_class):
    requires_me_classes = (Surface, Container, UnderSpace)

    def test(self):
        if thing_class in requires_me_classes:
            item = thing_class(thing_class.__name__, self.me)
        else:
            item = thing_class(thing_class.__name__)
        self.assertTrue(item.ix)
        self.assertIn(
            item.ix,
            things.dict,
            f"Tried to create a {thing_class.__name__}, but index not in "
            "things obj_map",
        )
        self.assertIs(
            things.dict[item.ix],
            item,
            f"New {thing_class.__name__} index successfully added to "
            f"object_map, but {things.dict[item.ix]} found under key instead of "
            f"the new instance {item}",
        )

    return test


def add_thing_instantiation_tests():
    ignore = [Actor, Liquid, Lock]
    thing_classes = Thing.__subclasses__()
    for thing_class in thing_classes:
        if thing_class in ignore:
            continue
        func = make_thing_instantiation_test(thing_class)
        setattr(TestCreateAllTypes, f"test_create_{thing_class.__name__}", func)


class TestCreateAllTypes(IFPTestCase):
    def test_create_Liquid(self):
        item = Liquid(Liquid.__name__, "water")
        self.assertTrue(item.ix)
        self.assertIn(
            item.ix,
            things.dict,
            f"Tried to create a {Liquid.__name__}, but index not in " "things obj_map",
        )
        self.assertIs(
            things.dict[item.ix],
            item,
            f"New {Liquid.__name__} index successfully added to "
            f"object_map, but {things.dict[item.ix]} found under key instead of "
            f"the new instance {item}",
        )

    def test_create_Actor(self):
        item = Actor(Actor.__name__)
        self.assertTrue(item.ix)
        self.assertIn(
            item.ix,
            actors.dict,
            f"Tried to create a {Actor.__name__}, but index not in " "things obj_map",
        )
        self.assertIs(
            actors.dict[item.ix],
            item,
            f"New {Actor.__name__} index successfully added to "
            f"object_map, but {actors.dict[item.ix]} found under key instead of "
            f"the new instance {item}",
        )


class TestAddRemoveThing(IFPTestCase):
    def _assert_can_add_remove(self, parent, child):
        self.assertNotIn(child.ix, parent.contains)

        self.assertNotIn(
            child.verbose_name,
            parent.xdesc,
            "This test needs the child verbose_name to not intially be in "
            "the parent xdesc",
        )

        parent.addThing(child)
        self.assertIn(
            child.ix,
            parent.contains,
            f"Tried to add item to {parent} but ix not in contains",
        )
        self.assertIn(
            child,
            parent.contains[child.ix],
            f"Tried to add item to {parent}. ix in contains, but item not "
            "found under key",
        )

        self.assertIn(
            child.verbose_name,
            parent.xdesc,
            f"Item added to {parent}, but item verbose_name not found in xdesc",
        )

        parent.removeThing(child)
        self.assertNotIn(
            child.ix,
            parent.contains,
            f"Tried to remove unique item from {parent} but ix still in " "contains",
        )
        self.assertNotIn(
            child.verbose_name,
            parent.xdesc,
            f"Item removed from {parent}, but item verbose_name still in xdesc",
        )

    def test_add_remove_from_Surface(self):
        parent = Surface("parent", self.me)
        child = Thing("child")
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_from_Container(self):
        parent = Container("parent", self.me)
        child = Thing("child")
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_from_UnderSpace(self):
        parent = Surface("parent", self.me)
        child = Thing("child")
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)


class TestComposite(IFPTestCase):
    pass


add_thing_instantiation_tests()

if __name__ == "__main__":
    unittest.main()

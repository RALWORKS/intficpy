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


class TestThing(IFPTestCase):
    pass


class TestAddRemoveThing(IFPTestCase):
    pass


class TestComposite(IFPTestCase):
    pass


add_thing_instantiation_tests()

if __name__ == "__main__":
    unittest.main()

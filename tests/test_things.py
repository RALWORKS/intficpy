import unittest

from .helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.object_maps import things, actors
from intficpy.things import Surface, Container, UnderSpace, Liquid, Lock
from intficpy.actor import Actor
from intficpy.room import Room


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
            f"Tried to create a {Liquid.__name__}, but index not in things obj_map",
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
            f"Tried to create a {Actor.__name__}, but index not in things obj_map",
        )
        self.assertIs(
            actors.dict[item.ix],
            item,
            f"New {Actor.__name__} index successfully added to "
            f"object_map, but {actors.dict[item.ix]} found under key instead of "
            f"the new instance {item}",
        )

    def test_create_Lock(self):
        item = Lock(Lock.__name__, None)
        self.assertTrue(item.ix)
        self.assertIn(
            item.ix,
            things.dict,
            f"Tried to create a {Lock.__name__}, but index not in things obj_map",
        )
        self.assertIs(
            things.dict[item.ix],
            item,
            f"New {Lock.__name__} index successfully added to "
            f"object_map, but {things.dict[item.ix]} found under key instead of "
            f"the new instance {item}",
        )


class TestAddRemoveThing(IFPTestCase):
    def _get_full_desc(self, subject):
        if hasattr(subject, "describe"):
            subject.describe(self.me, self.app)
            return self.app.print_stack.pop()
        return subject.xdesc

    def _assert_can_add_remove(self, parent, child):
        self.assertNotIn(child.ix, parent.contains)

        parent_desc = self._get_full_desc(parent)

        self.assertNotIn(
            child.verbose_name,
            parent_desc,
            "This test needs the child verbose_name to not intially be in "
            "the parent description",
        )

        if child.lock_obj:
            self.assertNotIn(child.lock_obj.ix, parent.contains)
        for sub_item in child.children:
            self.assertNotIn(sub_item.ix, parent.contains)

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

        parent_desc = self._get_full_desc(parent)

        self.assertIn(
            child.verbose_name,
            parent_desc,
            f"Item added to {parent}, but item verbose_name not found in description",
        )

        if child.lock_obj:
            self.assertIn(
                child.lock_obj.ix,
                parent.contains,
                f"Added item to {parent}, but lock_obj not added",
            )
            self.assertIn(
                child.lock_obj,
                parent.contains[child.lock_obj.ix],
                f"Item lock_obj ix in {parent}, but lock_obj not found under ix",
            )
        for sub_item in child.children:
            self.assertIn(
                sub_item.ix,
                parent.contains,
                f"Added item to {parent}, but composite {sub_item} not added",
            )
            self.assertIn(
                sub_item,
                parent.contains[sub_item.ix],
                f"Composite {sub_item} ix in {parent}, but item not found " "under ix",
            )

        parent.removeThing(child)
        self.assertNotIn(
            child.ix,
            parent.contains,
            f"Tried to remove unique item from {parent} but ix still in " "contains",
        )
        parent_desc = self._get_full_desc(parent)
        self.assertNotIn(
            child.verbose_name,
            parent_desc,
            f"Item removed from {parent}, but item verbose_name still in xdesc",
        )

        if child.lock_obj:
            self.assertNotIn(
                child.lock_obj.ix,
                parent.contains,
                f"lock_obj {child.lock_obj} not removed from {parent}",
            )
        for sub_item in child.children:
            self.assertNotIn(
                sub_item.ix,
                parent.contains,
                f"composite child {sub_item} not removed from {parent}",
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
        parent = UnderSpace("parent", self.me)
        parent.revealed = True
        child = Thing("child")
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_from_Room(self):
        parent = Room("parent", "This is a room. ")
        child = Thing("child")
        self._assert_can_add_remove(parent, child)

    def test_add_remove_composite_item_from_Surface(self):
        parent = Surface("parent", self.me)
        child = Thing("child")
        sub = Thing("sub")
        child.addComposite(sub)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_composite_item_from_Container(self):
        parent = Container("parent", self.me)
        child = Thing("child")
        sub = Thing("sub")
        child.addComposite(sub)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_composite_item_from_UnderSpace(self):
        parent = UnderSpace("parent", self.me)
        parent.revealed = True
        child = Thing("child")
        sub = Thing("sub")
        child.addComposite(sub)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_composite_item_from_Room(self):
        parent = Room("parent", "This is a room. ")
        child = Thing("child")
        sub = Thing("sub")
        child.addComposite(sub)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_item_with_lock_from_Surface(self):
        parent = Surface("parent", self.me)
        child = Container("child", self.me)
        child.has_lid = True
        lock = Lock("lock", None)
        child.setLock(lock)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_item_with_lock_from_Container(self):
        parent = Container("parent", self.me)
        child = Container("child", self.me)
        child.has_lid = True
        lock = Lock("lock", None)
        child.setLock(lock)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_item_with_lock_from_UnderSpace(self):
        parent = UnderSpace("parent", self.me)
        parent.revealed = True
        child = Container("child", self.me)
        child.has_lid = True
        lock = Lock("lock", None)
        child.setLock(lock)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_item_with_lock_from_Room(self):
        parent = Room("parent", "This is a room. ")
        parent.revealed = True
        child = Container("child", self.me)
        child.has_lid = True
        lock = Lock("lock", None)
        child.setLock(lock)
        self._assert_can_add_remove(parent, child)


add_thing_instantiation_tests()

if __name__ == "__main__":
    unittest.main()

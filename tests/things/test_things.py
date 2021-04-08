from ..helpers import IFPTestCase

from intficpy.ifp_object import IFPObject
from intficpy.thing_base import Thing
from intficpy.things import Surface, Container, UnderSpace, Liquid, Lock
from intficpy.actor import Actor
from intficpy.room import Room


def make_thing_instantiation_test(thing_class):
    def test(self):
        item = thing_class(self.game, thing_class.__name__)
        self.assertTrue(item.ix)
        self.assertIn(
            item.ix,
            self.game.ifp_objects,
            f"Tried to create a {thing_class.__name__}, but index not in "
            "things obj_map",
        )
        self.assertIs(
            self.game.ifp_objects[item.ix],
            item,
            f"New {thing_class.__name__} index successfully added to "
            f"object_map, but {self.game.ifp_objects[item.ix]} found under key instead of "
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
        item = Liquid(self.game, Liquid.__name__, "water")
        self.assertTrue(item.ix)
        self.assertIn(
            item.ix,
            self.game.ifp_objects,
            f"Tried to create a {Liquid.__name__}, but index not in things obj_map",
        )
        self.assertIs(
            self.game.ifp_objects[item.ix],
            item,
            f"New {Liquid.__name__} index successfully added to "
            f"object_map, but {self.game.ifp_objects[item.ix]} found under key instead of "
            f"the new instance {item}",
        )

    def test_create_Actor(self):
        item = Actor(self.game, Actor.__name__)
        self.assertTrue(item.ix)
        self.assertIn(
            item.ix,
            self.game.ifp_objects,
            f"Tried to create a {Actor.__name__}, but index not in things obj_map",
        )
        self.assertIs(
            self.game.ifp_objects[item.ix],
            item,
            f"New {Actor.__name__} index successfully added to "
            f"object_map, but {self.game.ifp_objects[item.ix]} found under key instead of "
            f"the new instance {item}",
        )

    def test_create_Lock(self):
        item = Lock(self.game, self.game, Lock.__name__, None)
        self.assertTrue(item.ix)
        self.assertIn(
            item.ix,
            self.game.ifp_objects,
            f"Tried to create a {Lock.__name__}, but index not in things obj_map",
        )
        self.assertIs(
            self.game.ifp_objects[item.ix],
            item,
            f"New {Lock.__name__} index successfully added to "
            f"object_map, but {self.game.ifp_objects[item.ix]} found under key instead of "
            f"the new instance {item}",
        )


class TestAddRemoveThing(IFPTestCase):
    def describe(self, subject):
        if isinstance(subject, Room):
            self.game.turnMain("l")
            return self.app.print_stack.pop()
        return subject.desc

    def _assert_can_add_remove(self, parent, child):
        self.assertNotIn(child.ix, parent.contains)

        parent.desc_reveal = True

        self.assertNotIn(
            child.verbose_name,
            self.describe(parent),
            "This test needs the child verbose_name to not intially be in "
            "the parent description",
        )

        if child.lock_obj:
            self.assertNotIn(child.lock_obj.ix, parent.contains)
        for sub_item in child.children:
            self.assertNotIn(sub_item.ix, parent.contains)

        parent.addThing(child)
        self.assertItemIn(
            child,
            parent.contains,
            f"Tried to add item to {parent}, but item not found in `contains`",
        )

        if child.lock_obj:
            self.assertItemIn(
                child.lock_obj,
                parent.contains,
                f"Added item with lock to {parent}, but lock_obj not found in `contains`",
            )

        for sub_item in child.children:
            self.assertItemIn(
                sub_item,
                parent.contains,
                f"Tried to add item to {parent}, but composite child item not found in "
                "`contains`",
            )

        parent.removeThing(child)
        self.assertItemNotIn(
            child,
            parent.contains,
            f"Tried to remove item from {parent}, but item still found in `contains`",
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
        parent = Surface(self.game, "parent")
        child = Thing(self.game, "child")
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_from_Container(self):
        parent = Container(self.game, "parent")
        child = Thing(self.game, "child")
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_from_UnderSpace(self):
        parent = UnderSpace(self.game, "parent")
        parent.revealed = True
        child = Thing(self.game, "child")
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_from_Room(self):
        parent = Room(self.game, "parent", "This is a room. ")
        child = Thing(self.game, "child")
        self._assert_can_add_remove(parent, child)

    def test_add_remove_composite_item_from_Surface(self):
        parent = Surface(self.game, "parent")
        child = Thing(self.game, "child")
        sub = Thing(self.game, "sub")
        child.addComposite(sub)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_composite_item_from_Container(self):
        parent = Container(self.game, "parent")
        child = Thing(self.game, "child")
        sub = Thing(self.game, "sub")
        child.addComposite(sub)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_composite_item_from_UnderSpace(self):
        parent = UnderSpace(self.game, "parent")
        parent.revealed = True
        child = Thing(self.game, "child")
        sub = Thing(self.game, "sub")
        child.addComposite(sub)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_composite_item_from_Room(self):
        parent = Room(self.game, "parent", "This is a room. ")
        child = Thing(self.game, "child")
        sub = Thing(self.game, "sub")
        child.addComposite(sub)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_item_with_lock_from_Surface(self):
        parent = Surface(self.game, "parent")
        child = Container(self.game, "child")
        child.has_lid = True
        lock = Lock(self.game, "lock", None)
        child.setLock(lock)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_item_with_lock_from_Container(self):
        parent = Container(self.game, "parent")
        child = Container(self.game, "child")
        child.has_lid = True
        lock = Lock(self.game, "lock", None)
        child.setLock(lock)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_item_with_lock_from_UnderSpace(self):
        parent = UnderSpace(self.game, "parent")
        parent.revealed = True
        child = Container(self.game, "child")
        child.has_lid = True
        lock = Lock(self.game, "lock", None)
        child.setLock(lock)
        self.start_room.addThing(parent)
        self._assert_can_add_remove(parent, child)

    def test_add_remove_item_with_lock_from_Room(self):
        parent = Room(self.game, "parent", "This is a room. ")
        parent.revealed = True
        child = Container(self.game, "child")
        child.has_lid = True
        lock = Lock(self.game, "lock", None)
        child.setLock(lock)
        self._assert_can_add_remove(parent, child)


class TestMoveTo(IFPTestCase):
    def test_move_to_removes_item_from_old_location_and_adds_to_new_location(self):
        old = Room(self.game, "old", "It is old")
        child = Thing(self.game, "child")
        old.addThing(child)

        new = Container(self.game, "new")
        child.moveTo(new)

        self.assertItemIn(child, new.contains, "Item not added to new location")
        self.assertItemNotIn(child, old.contains, "Item not removed from old location")
        self.assertIs(child.location, new, "Item not added to new location")

    def test_move_to_removes_item_from_old_superlocation_subcontains(self):
        room = Room(self.game, "old", "It is old")
        old = Container(self.game, "box")
        room.addThing(old)
        child = Thing(self.game, "child")
        old.addThing(child)

        new = Container(self.game, "new")

        self.assertItemIn(
            child, room.sub_contains, "Item not removed from old location"
        )

        child.moveTo(new)

        self.assertItemNotIn(
            child, room.sub_contains, "Item not removed from old location"
        )
        self.assertIs(child.location, new, "Item not added to new location")

    def test_adds_to_new_location_if_no_previous_location(self):
        child = Thing(self.game, "child")

        new = Container(self.game, "new")
        child.moveTo(new)

        self.assertItemIn(child, new.contains, "Item not added to new location")
        self.assertIs(child.location, new, "Item not added to new location")

    def test_move_item_to_nested_adding_container_first_then_item(self):
        container = Container(self.game, "cup")
        item = Thing(self.game, "bead")

        container.moveTo(self.start_room)
        self.assertIs(container.location, self.start_room)

        item.moveTo(container)

        self.assertIs(item.location, container)
        self.assertTrue(container.topLevelContainsItem(item))

    def test_move_item_to_nested_adding_item_first_then_container(self):
        container = Container(self.game, "cup")
        item = Thing(self.game, "bead")

        item.moveTo(container)
        self.assertIs(
            item.location,
            container,
            "Move item to container failed to set item location when container location was None",
        )

        container.moveTo(self.start_room)

        self.assertIs(item.location, container)
        self.assertTrue(container.topLevelContainsItem(item))

    def test_move_nested_item_between_locations(self):
        room2 = Room(self.game, "room", "here")
        container = Container(self.game, "cup")
        item = Thing(self.game, "bead")

        item.moveTo(container)
        container.moveTo(self.start_room)

        self.assertIs(container.location, self.start_room)
        self.assertIs(item.location, container)
        self.assertTrue(container.topLevelContainsItem(item))

        container.moveTo(room2)

        self.assertIs(container.location, room2)
        self.assertIs(
            item.location,
            container,
            "Nested item location was updated when container was moved",
        )
        self.assertTrue(container.topLevelContainsItem(item))


add_thing_instantiation_tests()

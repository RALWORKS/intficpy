import unittest

from .helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import Surface, Container, UnderSpace, Readable
from intficpy.room import Room
from intficpy.parser import getThing, getCurVerb, getGrammarObj, callVerb
from intficpy.verb import (
    getVerb,
    dropVerb,
    lookVerb,
    examineVerb,
    setInVerb,
    setOnVerb,
    setUnderVerb,
    lookVerb,
    examineVerb,
    lookInVerb,
    lookUnderVerb,
    readVerb,
    getAllVerb,
    dropAllVerb,
    invVerb,
)


class TestGetVerb(IFPTestCase):
    def test_verb_func_adds_invitem_to_inv(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.start_room.addThing(item)

        success = getVerb.verbFunc(self.me, self.app, item)
        self.assertTrue(success)

        self.assertIn(item.ix, self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

    def test_verb_func_does_not_add_to_inv_where_invitem_false(self):
        item = Thing(self._get_unique_noun())
        item.invItem = False
        self.start_room.addThing(item)

        self.assertFalse(item.ix in self.me.contains)

        success = getVerb.verbFunc(self.me, self.app, item)
        self.assertFalse(success)

        self.assertNotIn(item.ix, self.me.contains)

    def test_verb_func_does_not_add_to_inv_where_already_in_inv(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        self.assertTrue(item.ix in self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

        success = getVerb.verbFunc(self.me, self.app, item)
        self.assertFalse(success)

        self.assertEqual(len(self.me.contains[item.ix]), 1)


class TestDropVerb(IFPTestCase):
    def test_verb_func_drops_item(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        self.assertIn(item.ix, self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

        success = dropVerb.verbFunc(self.me, self.app, item)
        self.assertTrue(success)

        self.assertNotIn(item.ix, self.me.contains)

    def test_drop_item_not_in_inv(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.start_room.addThing(item)
        self.assertNotIn(item.ix, self.me.contains)

        success = dropVerb.verbFunc(self.me, self.app, item)
        self.assertFalse(success)


class TestExamineVerb(IFPTestCase):
    def test_verb_func_prints_xdesc(self):
        item = Thing(self._get_unique_noun())
        self.start_room.addThing(item)

        success = examineVerb.verbFunc(self.me, self.app, item)
        self.assertTrue(success)

        printed = self.app.print_stack[-1]

        self.assertEqual(printed, item.xdesc)


class TestLookVerb(IFPTestCase):
    def test_look_verb_prints_room_desc(self):
        self.start_room.desc = "You are in a bright, wonderful room."
        self.assertEqual(self.me.location, self.start_room)

        success = lookVerb.verbFunc(self.me, self.app)
        self.assertTrue(success)

        printed = self.app.print_stack[-1]

        self.assertIn(self.start_room.desc, printed)

    def test_look_verb_prints_item_desc(self):
        item = Thing(self._get_unique_noun())
        item.desc = f"A {item.verbose_name} lurks in the corner. "
        self.start_room.addThing(item)

        success = lookVerb.verbFunc(self.me, self.app)
        self.assertTrue(success)

        printed = self.app.print_stack[-1]

        self.assertIn(item.desc, printed)


class TestSetVerbs(IFPTestCase):
    def test_set_in_adds_item(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        container = Container(self._get_unique_noun(), self.me)
        self.start_room.addThing(container)

        self.assertNotIn(item.ix, container.contains)

        success = setInVerb.verbFunc(self.me, self.app, item, container)
        self.assertTrue(success)

        self.assertIn(item.ix, container.contains)
        self.assertIn(item, container.contains[item.ix])

    def test_set_on_adds_item(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        surface = Surface(self._get_unique_noun(), self.me)
        self.start_room.addThing(surface)

        self.assertNotIn(item.ix, surface.contains)

        success = setOnVerb.verbFunc(self.me, self.app, item, surface)
        self.assertTrue(success)

        self.assertIn(item.ix, surface.contains)
        self.assertIn(item, surface.contains[item.ix])

    def test_set_under_adds_item(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        underspace = UnderSpace(self._get_unique_noun(), self.me)
        self.start_room.addThing(underspace)

        self.assertNotIn(item.ix, underspace.contains)

        success = setUnderVerb.verbFunc(self.me, self.app, item, underspace)
        self.assertTrue(success)

        self.assertIn(item.ix, underspace.contains)
        self.assertIn(item, underspace.contains[item.ix])

    def test_cannot_set_in_non_container(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        success = setInVerb.verbFunc(self.me, self.app, item, invalid_iobj)
        self.assertFalse(success)

        self.assertNotIn(item.ix, invalid_iobj.contains)

    def test_cannot_set_on_non_surface(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        success = setOnVerb.verbFunc(self.me, self.app, item, invalid_iobj)
        self.assertFalse(success)

        self.assertNotIn(item.ix, invalid_iobj.contains)

    def test_cannot_set_under_non_underspace(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        success = setUnderVerb.verbFunc(self.me, self.app, item, invalid_iobj)
        self.assertFalse(success)

        self.assertNotIn(item.ix, invalid_iobj.contains)


class TestLookVerbs(IFPTestCase):
    def test_look(self):
        room = Room("Strange Room", "It's strange in here. ")
        item = Thing("hullabaloo")
        item.describeThing("All around is a hullabaloo. ")
        room.addThing(item)

        self.me.location.removeThing(self.me)
        room.addThing(self.me)

        lookVerb.verbFunc(self.me, self.app)
        look_desc = self.app.print_stack.pop()
        look_title = self.app.print_stack.pop()

        self.assertIn(room.name, look_title, f"Room title printed incorrectly")
        self.assertIn(room.desc, look_desc, "Room description not printed by look")
        self.assertIn(item.desc, look_desc, "Item description not printed by look")

    def test_examine(self):
        item = Thing("widget")
        item.xdescribeThing("It's a shiny little widget. ")

        examineVerb.verbFunc(self.me, self.app, item)

        examine_desc = self.app.print_stack.pop()

        self.assertEqual(
            examine_desc,
            item.xdesc,
            f"Examine desc printed incorrectly. Expecting {item.xdesc}, got {examine_desc}",
        )

    def test_look_in(self):
        parent = Container("shoebox", self.me)
        child = Thing("penny")
        parent.addThing(child)

        lookInVerb.verbFunc(self.me, self.app, parent)

        look_in_desc = self.app.print_stack.pop()

        self.assertEqual(
            look_in_desc,
            parent.contains_desc,
            f"Contains desc printed incorrectly. Expected {parent.contains_desc} got "
            f"{look_in_desc}"
        )

    def test_look_under(self):
        parent = UnderSpace("table", self.me)
        child = Thing("penny")
        parent.addThing(child)

        lookUnderVerb.verbFunc(self.me, self.app, parent)

        look_under_desc = self.app.print_stack.pop()

        self.assertEqual(
            look_under_desc,
            parent.contains_desc,
            f"Contains desc printed incorrectly. Expected {parent.contains_desc} got "
            f"{look_under_desc}"
        )

    def test_read(self):
        item = Readable("note", "I'm sorry, but I have to do this. ")

        readVerb.verbFunc(self.me, self.app, item)

        read_desc = self.app.print_stack.pop()

        self.assertEqual(
            read_desc,
            item.read_desc,
            f"Item text printed incorrectly. Expecting {item.read_desc}, got {read_desc}"
        )


class TestInventoryVerbs(IFPTestCase):
    def test_get_all_drop_all(self):
        item1 = Thing("miracle")
        item2 = Thing("wonder")
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

        getAllVerb.verbFunc(self.me, self.app)
        getall_msg = self.app.print_stack.pop()

        self.assertIn(
            item1.ix,
            self.me.contains,
            f"Item not added to inv with get all. Msg: '{getall_msg}'"
        )
        self.assertIn(item1, self.me.contains[item1.ix])
        self.assertIn(
            item2.ix,
            self.me.contains,
            f"Item not added to inv with get all. Msg: '{getall_msg}'"
        )
        self.assertIn(item2, self.me.contains[item2.ix])

        getAllVerb.verbFunc(self.me, self.app)
        getall_msg = self.app.print_stack.pop()
        self.assertEqual(getall_msg, "There are no obvious items here to take. ")

        dropAllVerb.verbFunc(self.me, self.app)
        dropall_msg = self.app.print_stack.pop()

        self.assertEqual(
            len(self.me.contains),
            0,
            f"Expected empty inv, but found {self.me.contains}"
        )

        self.assertIn(item1.ix, self.start_room.contains)
        self.assertIn(item1, self.start_room.contains[item1.ix])
        self.assertIn(item2.ix, self.start_room.contains)
        self.assertIn(item2, self.start_room.contains[item2.ix])
        self.assertIn(item3, self.start_room.contains[item2.ix])

        dropAllVerb.verbFunc(self.me, self.app)
        dropall_msg = self.app.print_stack.pop()
        self.assertEqual(dropall_msg, "Your inventory is empty. ")


if __name__ == "__main__":
    unittest.main()

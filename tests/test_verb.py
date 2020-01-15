import unittest

from .helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import Surface, Container, UnderSpace, Readable, Lock, Key
from intficpy.actor import Actor, Topic
from intficpy.room import Room
from intficpy.travel import DoorConnector
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
    openVerb,
    closeVerb,
    lockVerb,
    lockWithVerb,
    unlockVerb,
    unlockWithVerb,
    askVerb,
    tellVerb,
    giveVerb,
    showVerb,
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
            f"{look_in_desc}",
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
            f"{look_under_desc}",
        )

    def test_read(self):
        item = Readable("note", "I'm sorry, but I have to do this. ")

        readVerb.verbFunc(self.me, self.app, item)

        read_desc = self.app.print_stack.pop()

        self.assertEqual(
            read_desc,
            item.read_desc,
            f"Item text printed incorrectly. Expecting {item.read_desc}, got {read_desc}",
        )


class TestInventoryVerbs(IFPTestCase):
    def test_get_all_drop(self):
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
            f"Item not added to inv with get all. Msg: '{getall_msg}'",
        )
        self.assertIn(item1, self.me.contains[item1.ix])
        self.assertIn(
            item2.ix,
            self.me.contains,
            f"Item not added to inv with get all. Msg: '{getall_msg}'",
        )
        self.assertIn(item2, self.me.contains[item2.ix])

        getAllVerb.verbFunc(self.me, self.app)
        getall_msg = self.app.print_stack.pop()
        self.assertEqual(getall_msg, "There are no obvious items here to take. ")

    def test_drop_all(self):
        item1 = Thing("miracle")
        item2 = Thing("wonder")
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

        dropAllVerb.verbFunc(self.me, self.app)
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
        dropAllVerb.verbFunc(self.me, self.app)
        dropall_msg = self.app.print_stack.pop()
        self.assertEqual(dropall_msg, "Your inventory is empty. ")

    def test_view_inv_with_items(self):
        item1 = Thing("miracle")
        item2 = Thing("wonder")
        item1.invItem = True
        item2.invItem = True
        item3 = item2.copyThing()
        self.me.addThing(item1)
        self.me.addThing(item3)
        self.me.addThing(item2)

        invVerb.verbFunc(self.me, self.app)
        inv_msg = self.app.print_stack.pop()

        self.assertEqual(
            len(self.me.contains[item2.ix]),
            2,
            f"This test assumes two {item2.ix} items in the inventory ",
        )

        BASE_INV_MSG = "You have"
        itemstr1 = f"{item1.lowNameArticle()}"
        itemstr2 = f"{len(self.me.contains[item2.ix])} {item2.getPlural()}"

        self.assertIn(
            itemstr1,
            inv_msg,
            "Single item added to inventory, but message does not match expected",
        )

        self.assertIn(
            itemstr1,
            inv_msg,
            "Stacked item added to inventory, but message does not match expected",
        )

        inv_msg = inv_msg.replace(itemstr1, "")
        inv_msg = inv_msg.replace(itemstr2, "")
        inv_msg = inv_msg.replace("and", "")
        inv_msg = inv_msg.replace(",", "")
        inv_msg = inv_msg.replace(".", "")
        inv_msg = " ".join(inv_msg.split())

        self.assertEqual(inv_msg, BASE_INV_MSG, "Inv message in unexpected format")

    def test_view_empty_inv(self):
        dropAllVerb.verbFunc(self.me, self.app)
        self.assertEqual(
            len(self.me.contains), 0, "This test requires an empty player inventory"
        )

        EMPTY_INV_MSG = "You don't have anything with you."

        invVerb.verbFunc(self.me, self.app)
        inv_msg = self.app.print_stack.pop()

        self.assertEqual(
            inv_msg,
            EMPTY_INV_MSG,
            "Viewed empty inventory. Message does not match expected.",
        )


class TestDoorVerbs(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.room1 = Room("A cold room", "This room is cold. ")
        self.room2 = Room("A hot room", "This room is uncomfortably hot. ")
        self.door = DoorConnector(self.room1, "se", self.room2, "nw")
        self.key = Key("key")
        self.me.addThing(self.key)
        self.lock = Lock(False, self.key)
        self.lock.is_locked = False
        self.door.setLock(self.lock)

    def test_open_door(self):
        self.assertFalse(
            self.door.entranceA.is_open,
            "This test needs the door to be initially closed",
        )
        self.assertFalse(
            self.door.entranceA.lock_obj.is_locked,
            "This test needs the door to be initially unlocked",
        )

        openVerb.verbFunc(self.me, self.app, self.door.entranceA)

        self.assertTrue(
            self.door.entranceA.is_open,
            "Performed open verb on unlocked door, but door is closed."
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_close_door(self):
        self.door.entranceA.makeOpen()
        self.assertTrue(
            self.door.entranceA.is_open, "This test needs the door to be initially open"
        )

        closeVerb.verbFunc(self.me, self.app, self.door.entranceA)

        self.assertFalse(
            self.door.entranceA.is_open,
            "Performed close verb on open door, but door is open."
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_lock_door(self):
        self.lock.is_locked = False
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        lockVerb.verbFunc(self.me, self.app, self.door.entranceA)

        self.assertTrue(
            self.lock.is_locked,
            "Performed lock verb with key in inv, but lock is unlocked."
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_unlock_door(self):
        self.lock.is_locked = True
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        unlockVerb.verbFunc(self.me, self.app, self.door.entranceA)

        self.assertFalse(
            self.lock.is_locked,
            "Performed unlock verb with key in inv, but lock is locked."
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_lock_door_with(self):
        self.lock.is_locked = False
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        lockWithVerb.verbFunc(self.me, self.app, self.door.entranceA, self.key)

        self.assertTrue(
            self.lock.is_locked,
            "Performed lock with verb with key, but lock is unlocked."
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_unlock_door_with(self):
        self.lock.is_locked = True
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        unlockWithVerb.verbFunc(self.me, self.app, self.door.entranceA, self.key)

        self.assertFalse(
            self.lock.is_locked,
            "Performed unlock verb with key, but lock is locked."
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_open_locked_door(self):
        self.lock.is_locked = True
        self.assertFalse(
            self.door.entranceA.is_open,
            "This test needs the door to be initially closed",
        )
        self.assertTrue(
            self.door.entranceA.lock_obj.is_locked,
            "This test needs the door to be initially locked",
        )

        openVerb.verbFunc(self.me, self.app, self.door.entranceA)

        self.assertFalse(
            self.door.entranceA.is_open,
            "Performed open verb on locked door, but door is open."
            f"Msg: {self.app.print_stack[-1]}",
        )


class TestLidVerbs(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("chest", self.me)
        self.container.has_lid = True
        self.container.is_open = False
        self.key = Key("key")
        self.me.addThing(self.key)
        self.lock = Lock(False, self.key)
        self.lock.is_locked = False
        self.container.setLock(self.lock)

    def test_open_container(self):
        self.assertFalse(
            self.container.is_open,
            "This test needs the container to be initially closed",
        )
        self.assertFalse(
            self.container.lock_obj.is_locked,
            "This test needs the container to be initially unlocked",
        )

        openVerb.verbFunc(self.me, self.app, self.container)

        self.assertTrue(
            self.container.is_open,
            "Performed open verb on unlocked container, but lid is closed."
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_close_container(self):
        self.container.is_open = True
        self.assertTrue(
            self.container.is_open, "This test needs the container to be initially open"
        )

        closeVerb.verbFunc(self.me, self.app, self.container)

        self.assertFalse(
            self.container.is_open,
            "Performed close verb on open container, but lid is open."
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_open_locked_container(self):
        self.lock.is_locked = True
        self.assertFalse(
            self.container.is_open,
            "This test needs the container to be initially closed",
        )
        self.assertTrue(
            self.container.lock_obj.is_locked,
            "This test needs the container to be initially locked",
        )

        openVerb.verbFunc(self.me, self.app, self.container)

        self.assertFalse(
            self.container.is_open,
            "Performed open verb on locked container, but lid is open."
            f"Msg: {self.app.print_stack[-1]}",
        )


class TestConversationVerbs(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.item = Thing("mess")
        self.actor = Actor("Jenny")
        self.start_room.addThing(self.item)
        self.start_room.addThing(self.actor)
        self.CANNOT_TALK_MSG = "You cannot talk to that."
        self.topic = Topic('"Ah, yes," says Jenny mysteriously. ')

    def test_ask_inanimate(self):
        askVerb.verbFunc(self.me, self.app, self.item, self.actor)
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )

    def test_tell_inanimate(self):
        tellVerb.verbFunc(self.me, self.app, self.item, self.actor)
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )

    def test_give_inanimate(self):
        giveVerb.verbFunc(self.me, self.app, self.item, self.item)
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )

    def test_show_inanimate(self):
        showVerb.verbFunc(self.me, self.app, self.item, self.item)
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )

    def test_ask_no_defined_topic(self):
        self.actor.defaultTopic(self.app)
        default = self.app.print_stack.pop()

        self.assertNotIn(
            self.item.ix, self.actor.ask_topics,
        )

        askVerb.verbFunc(self.me, self.app, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            default,
            "Tried ask verb for topic not in ask topics. Expected default topic "
            f"{default}, received {msg}",
        )

    def test_tell_no_defined_topic(self):
        self.actor.defaultTopic(self.app)
        default = self.app.print_stack.pop()

        self.assertNotIn(
            self.item.ix, self.actor.tell_topics,
        )

        tellVerb.verbFunc(self.me, self.app, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            default,
            "Tried tell verb for topic not in tell topics. Expected default topic "
            f"{default}, received {msg}",
        )

    def test_give_no_defined_topic(self):
        self.actor.defaultTopic(self.app)
        default = self.app.print_stack.pop()

        self.assertNotIn(
            self.item.ix, self.actor.give_topics,
        )

        giveVerb.verbFunc(self.me, self.app, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            default,
            "Tried give verb for topic not in give topics. Expected default topic "
            f"{default}, received {msg}",
        )

    def test_show_no_defined_topic(self):
        self.actor.defaultTopic(self.app)
        default = self.app.print_stack.pop()

        self.assertNotIn(
            self.item.ix, self.actor.show_topics,
        )

        showVerb.verbFunc(self.me, self.app, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            default,
            "Tried show verb for topic not in show topics. Expected default topic "
            f"{default}, received {msg}",
        )

    def test_ask_with_topic(self):
        self.actor.addTopic("ask", self.topic, self.item)

        askVerb.verbFunc(self.me, self.app, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_tell_with_topic(self):
        self.actor.addTopic("tell", self.topic, self.item)

        tellVerb.verbFunc(self.me, self.app, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried tell verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_give_with_topic(self):
        self.actor.addTopic("give", self.topic, self.item)

        giveVerb.verbFunc(self.me, self.app, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried give verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_show_with_topic(self):
        self.actor.addTopic("show", self.topic, self.item)

        showVerb.verbFunc(self.me, self.app, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried show verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )


if __name__ == "__main__":
    unittest.main()

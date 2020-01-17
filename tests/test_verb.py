import unittest

from .helpers import IFPTestCase

from intficpy.game_info import lastTurn
from intficpy.thing_base import Thing
from intficpy.things import (
    Surface,
    Container,
    UnderSpace,
    Readable,
    Lock,
    Key,
    Clothing,
)
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
    wearVerb,
    climbOnVerb,
    climbDownFromVerb,
    climbDownVerb,
    climbInVerb,
    climbOutVerb,
    climbOutOfVerb,
    buyVerb,
    buyFromVerb,
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
            "Performed open verb on unlocked door, but door is closed. "
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
            "Performed close verb on open door, but door is open. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_lock_door(self):
        self.lock.is_locked = False
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        lockVerb.verbFunc(self.me, self.app, self.door.entranceA)

        self.assertTrue(
            self.lock.is_locked,
            "Performed lock verb with key in inv, but lock is unlocked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_unlock_door(self):
        self.lock.is_locked = True
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        unlockVerb.verbFunc(self.me, self.app, self.door.entranceA)

        self.assertFalse(
            self.lock.is_locked,
            "Performed unlock verb with key in inv, but lock is locked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_lock_door_with(self):
        self.lock.is_locked = False
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        lockWithVerb.verbFunc(self.me, self.app, self.door.entranceA, self.key)

        self.assertTrue(
            self.lock.is_locked,
            "Performed lock with verb with key, but lock is unlocked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_unlock_door_with(self):
        self.lock.is_locked = True
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        unlockWithVerb.verbFunc(self.me, self.app, self.door.entranceA, self.key)

        self.assertFalse(
            self.lock.is_locked,
            "Performed unlock verb with key, but lock is locked. "
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
            "Performed open verb on locked door, but door is open. "
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
            "Performed open verb on unlocked container, but lid is closed. "
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
            "Performed close verb on open container, but lid is open. "
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
            "Performed open verb on locked container, but lid is open. "
            f"Msg: {self.app.print_stack[-1]}",
        )


class TestConversationVerbs(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.item = Thing("mess")
        self.actor = Actor("Jenny")
        self.start_room.addThing(self.item)
        self.start_room.addThing(self.actor)
        self.CANNOT_TALK_MSG = "You cannot talk to that. "
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


class TestEmptyInventory(IFPTestCase):
    def test_view_empty_inv(self):
        dropAllVerb.verbFunc(self.me, self.app)
        self.assertEqual(
            len(self.me.contains), 0, "This test requires an empty player inventory"
        )

        EMPTY_INV_MSG = "You don't have anything with you. "

        invVerb.verbFunc(self.me, self.app)
        inv_msg = self.app.print_stack.pop()

        self.assertEqual(
            inv_msg,
            EMPTY_INV_MSG,
            "Viewed empty inventory. Message does not match expected. ",
        )


class TestFullInventory(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.parent = Thing("cube")
        self.child = Container("slot", self.me)
        self.parent.addComposite(self.child)
        self.stacked1 = Thing("tile")
        self.stacked2 = self.stacked1.copyThing()
        self.clothing = Clothing("scarf")
        self.clothing1 = Clothing("mitten")
        self.clothing2 = self.clothing1.copyThing()

        self.me.addThing(self.parent)
        self.me.addThing(self.child)
        self.me.addThing(self.stacked1)
        self.me.addThing(self.stacked2)
        self.me.addThing(self.clothing)
        self.me.addThing(self.clothing1)
        self.me.addThing(self.clothing2)

        wearVerb.verbFunc(self.me, self.app, self.clothing)
        wearVerb.verbFunc(self.me, self.app, self.clothing1)
        wearVerb.verbFunc(self.me, self.app, self.clothing2)

    def strip_desc(self, desc):
        desc = desc.replace(". ", "").replace(",", "").replace("and", "")
        return " ".join(desc.split())

    def test_inventory_items_desc(self):
        BASE_MSG = "You have"

        invVerb.verbFunc(self.me, self.app)
        self.app.print_stack.pop()
        inv_desc = self.app.print_stack.pop()

        parent_desc = self.parent.lowNameArticle()
        stacked_desc = (
            f"{len(self.me.contains[self.stacked1.ix])} " f"{self.stacked1.getPlural()}"
        )

        self.assertIn(
            parent_desc, inv_desc, "Composite item description should be in inv desc"
        )
        inv_desc = inv_desc.replace(parent_desc, "")

        self.assertIn(
            stacked_desc, inv_desc, "Stacked item description should be in inv desc"
        )
        inv_desc = inv_desc.replace(stacked_desc, "")

        inv_desc = self.strip_desc(inv_desc)
        self.assertEqual(
            inv_desc, BASE_MSG, "Remaining inv desc should match base message"
        )

    def test_inventory_wearing_desc(self):
        BASE_MSG = "You are wearing"

        invVerb.verbFunc(self.me, self.app)
        wearing_desc = self.app.print_stack.pop()

        clothing_desc = self.clothing.lowNameArticle()
        stacked_clothing_desc = (
            f"{len(self.me.wearing[self.clothing1.ix])} "
            f"{self.clothing1.getPlural()}"
        )

        self.assertIn(
            clothing_desc,
            wearing_desc,
            "Clothing item description should be in inv desc",
        )
        wearing_desc = wearing_desc.replace(clothing_desc, "")

        self.assertIn(
            stacked_clothing_desc,
            wearing_desc,
            "Stacked clothing item description should be in inv desc",
        )
        wearing_desc = wearing_desc.replace(stacked_clothing_desc, "")

        wearing_desc = self.strip_desc(wearing_desc)
        self.assertEqual(
            wearing_desc, BASE_MSG, "Remaining wearing desc should match base message"
        )


class TestPlayerGetOn(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.surface = Surface("bench", self.me)
        self.start_room.addThing(self.surface)

    def test_climb_on_cannot_sit_stand_lie(self):
        FAILURE_MSG = f"You cannot climb on {self.surface.lowNameArticle(True)}. "

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbOnVerb.verbFunc(self.me, self.app, self.surface)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_on_can_lie(self):
        SUCCESS_MSG = f"You lie on {self.surface.lowNameArticle(True)}. "

        self.surface.canLie = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbOnVerb.verbFunc(self.me, self.app, self.surface)
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_on_can_sit(self):
        SUCCESS_MSG = f"You sit on {self.surface.lowNameArticle(True)}. "

        self.surface.canSit = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbOnVerb.verbFunc(self.me, self.app, self.surface)
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_on_can_stand(self):
        SUCCESS_MSG = f"You stand on {self.surface.lowNameArticle(True)}. "

        self.surface.canStand = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbOnVerb.verbFunc(self.me, self.app, self.surface)
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetOff(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.surface = Surface("bench", self.me)
        self.surface.canStand = True
        self.start_room.addThing(self.surface)
        climbOnVerb.verbFunc(self.me, self.app, self.surface)
        self.assertIs(self.me.location, self.surface)

    def test_climb_down_from(self):
        SUCCESS_MSG = f"You climb down from {self.surface.lowNameArticle(True)}. "

        climbDownFromVerb.verbFunc(self.me, self.app, self.surface)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_down(self):
        SUCCESS_MSG = f"You climb down from {self.surface.lowNameArticle(True)}. "

        climbDownVerb.verbFunc(self.me, self.app)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetIn(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("box", self.me)
        self.start_room.addThing(self.container)

    def test_climb_in_cannot_sit_stand_lie(self):
        FAILURE_MSG = f"You cannot climb into {self.container.lowNameArticle(True)}. "

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_lie(self):
        SUCCESS_MSG = f"You lie in {self.container.lowNameArticle(True)}. "

        self.container.canLie = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_sit(self):
        SUCCESS_MSG = f"You sit in {self.container.lowNameArticle(True)}. "

        self.container.canSit = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_stand(self):
        SUCCESS_MSG = f"You stand in {self.container.lowNameArticle(True)}. "

        self.container.canStand = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetInOpenLid(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("box", self.me)
        self.container.has_lid = True
        self.container.is_open = True
        self.start_room.addThing(self.container)

    def test_climb_in_can_lie(self):
        SUCCESS_MSG = f"You lie in {self.container.lowNameArticle(True)}. "

        self.container.canLie = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_sit(self):
        SUCCESS_MSG = f"You sit in {self.container.lowNameArticle(True)}. "

        self.container.canSit = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_stand(self):
        SUCCESS_MSG = f"You stand in {self.container.lowNameArticle(True)}. "

        self.container.canStand = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetInClosedLid(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("box", self.me)
        self.container.has_lid = True
        self.container.is_open = False
        self.start_room.addThing(self.container)

    def test_climb_in_can_lie(self):
        FAILURE_MSG = (
            f"You cannot climb into {self.container.lowNameArticle(True)}, "
            "since it is closed. "
        )

        self.container.canLie = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_sit(self):
        FAILURE_MSG = (
            f"You cannot climb into {self.container.lowNameArticle(True)}, "
            "since it is closed. "
        )

        self.container.canSit = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_stand(self):
        FAILURE_MSG = (
            f"You cannot climb into {self.container.lowNameArticle(True)}, "
            "since it is closed. "
        )

        self.container.canStand = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)


class TestPlayerGetOut(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("box", self.me)
        self.container.canStand = True
        self.start_room.addThing(self.container)
        climbInVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.container)

    def test_climb_out_of(self):
        SUCCESS_MSG = f"You climb out of {self.container.lowNameArticle(True)}. "

        climbOutOfVerb.verbFunc(self.me, self.app, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_out(self):
        SUCCESS_MSG = f"You climb out of {self.container.lowNameArticle(True)}. "

        climbOutVerb.verbFunc(self.me, self.app)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestBuyFiniteStock(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing("widget")
        self.actor = Actor("Dmitri")
        self.currency = Thing("penny")
        self.me.addThing(self.currency)
        self.actor.addSelling(self.sale_item, self.currency, 1, 1)
        self.start_room.addThing(self.actor)

        self.OUT_STOCK_MSG = "That item is out of stock. "

    def test_buy(self):
        buyVerb.verbFunc(self.me, self.app, self.sale_item)

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(msg, expected, "Unexpected msg after attempting to buy item")

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )

        buyVerb.verbFunc(self.me, self.app, self.sale_item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.OUT_STOCK_MSG,
            "Tried to buy item which should be out of stock. Received unexpected msg",
        )
        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy out of stock item. Number in inventory should not have "
            "changed. ",
        )

    def test_buy_from(self):
        buyFromVerb.verbFunc(self.me, self.app, self.sale_item, self.actor)

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(msg, expected, "Unexpected msg after attempting to buy item")

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )

        buyFromVerb.verbFunc(self.me, self.app, self.sale_item, self.actor)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.OUT_STOCK_MSG,
            "Tried to buy item which should be out of stock. Received unexpected msg",
        )
        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy out of stock item. Number in inventory should not have "
            "changed. ",
        )


class TestBuyInfiniteStock(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing("widget")
        self.actor = Actor("Dmitri")
        self.currency = Thing("penny")
        self.me.addThing(self.currency)
        self.actor.addSelling(self.sale_item, self.currency, 1, True)
        self.start_room.addThing(self.actor)

    def test_buy(self):
        stock_before = self.actor.for_sale[self.sale_item.ix].number

        buyVerb.verbFunc(self.me, self.app, self.sale_item)

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(msg, expected, "Unexpected msg after attempting to buy item")

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )

        stock_after = self.actor.for_sale[self.sale_item.ix].number

        self.assertIs(
            stock_before,
            stock_after,
            "Stock of infinite item should not have changed after buying",
        )


class TestBuyNotEnoughMoney(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing("widget")
        self.actor = Actor("Dmitri")
        self.currency = Thing("penny")
        self.me.addThing(self.currency)
        self.actor.addSelling(self.sale_item, self.currency, 2, 1)
        self.start_room.addThing(self.actor)

    def test_buy(self):
        buyVerb.verbFunc(self.me, self.app, self.sale_item)

        msg = self.app.print_stack.pop()
        BASE_FAILURE_MSG = "You don't have enough"
        self.assertIn(
            BASE_FAILURE_MSG,
            msg,
            "Unexpected message after attempting to buy item with insufficient funds",
        )

        self.assertItemNotIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item with insufficient money.",
        )


class TestBuyNotSelling(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing("widget")
        self.actor = Actor("Dmitri")
        self.currency = Thing("penny")
        self.me.addThing(self.currency)

        self.start_room.addThing(self.actor)

    def test_buy(self):
        buyVerb.verbFunc(self.me, self.app, self.sale_item)

        msg = self.app.print_stack.pop()
        BASE_FAILURE_MSG = f"{self.actor.capNameArticle(True)} doesn't sell"
        self.assertIn(
            BASE_FAILURE_MSG,
            msg,
            "Unexpected message after attempting to buy item not for sale",
        )

        self.assertItemNotIn(
            self.sale_item, self.me.contains, "Attempted to buy item not for sale."
        )


class TestBuyWithNoActorsInRoom(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing("widget")
        self.actor = Thing("statue")
        self.currency = Thing("penny")
        self.me.addThing(self.currency)
        self.start_room.addThing(self.actor)

    def test_buy_from(self):
        buyFromVerb.verbFunc(self.me, self.app, self.sale_item, self.actor)

        msg = self.app.print_stack.pop()
        BASE_FAILURE_MSG = "You cannot buy anything from"
        self.assertIn(
            BASE_FAILURE_MSG,
            msg,
            "Unexpected message after attempting to buy item from non-Actor",
        )

        self.assertItemNotIn(
            self.sale_item, self.me.contains, "Attempted to buy item from non-Actor."
        )

    def test_buy(self):
        buyVerb.verbFunc(self.me, self.app, self.sale_item)

        msg = self.app.print_stack.pop()
        FAILURE_MSG = "There's no one obvious here to buy from. "
        self.assertEqual(
            FAILURE_MSG,
            msg,
            "Unexpected message after attempting to buy item in a room with no Actors",
        )

        self.assertItemNotIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item in a room with no Actors.",
        )


class TestBuyNotEnoughMoney(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Actor("Kate")
        self.actor = Actor("Dmitri")
        self.currency = Thing("penny")
        self.me.addThing(self.currency)
        self.actor.addSelling(self.sale_item, self.currency, 2, 1)
        self.start_room.addThing(self.actor)

    def test_buy(self):
        buyVerb.verbFunc(self.me, self.app, self.sale_item)

        msg = self.app.print_stack.pop()
        FAILURE_MSG = "You cannot buy or sell a person. "
        self.assertEqual(
            FAILURE_MSG, msg, "Unexpected message after attempting to buy an Actor"
        )

        self.assertItemNotIn(
            self.sale_item, self.me.contains, "Attempted to buy an Actor."
        )


class TestBuyRoomWithMultipleActors(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing("bulb")
        self.actor1 = Actor("Dmitri")
        self.actor2 = Actor("Kate")
        self.currency = Thing("penny")
        self.me.addThing(self.currency)
        self.actor1.addSelling(self.sale_item, self.currency, 1, 1)
        self.start_room.addThing(self.actor1)
        self.start_room.addThing(self.actor2)

    def test_buy(self):
        buyVerb.verbFunc(self.me, self.app, self.sale_item)

        msg = self.app.print_stack.pop()
        BASE_DISAMBIG_MSG = "Would you like to buy from"
        self.assertIn(
            BASE_DISAMBIG_MSG,
            msg,
            "Unexpected message after attempting to buy from ambiguous Actor",
        )

        self.assertItemNotIn(
            self.sale_item, self.me.contains, "Attempted to buy from ambiguous Actor."
        )

    def test_buy_with_lastTurn_dobj_actor(self):
        lastTurn.dobj = self.actor1

        buyVerb.verbFunc(self.me, self.app, self.sale_item)

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(
            msg, expected, "Unexpected msg after attempting to buy from ambigous Actor"
        )

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )

    def test_buy_with_lastTurn_iobj_actor(self):
        lastTurn.iobj = self.actor1

        buyVerb.verbFunc(self.me, self.app, self.sale_item)

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(
            msg, expected, "Unexpected msg after attempting to buy from ambigous Actor"
        )

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )


if __name__ == "__main__":
    unittest.main()

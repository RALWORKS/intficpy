import unittest

from .helpers import IFPTestCase

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
from intficpy.actor import Actor
from intficpy.exceptions import AbortTurn, ObjectMatchError
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
    wearVerb,
    climbOnVerb,
    climbDownFromVerb,
    climbDownVerb,
    climbInVerb,
    climbOutVerb,
    climbOutOfVerb,
    talkToVerb,
)


class TestGetVerb(IFPTestCase):
    def test_verb_func_adds_invitem_to_inv(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.start_room.addThing(item)

        success = getVerb._runVerbFuncAndEvents(self.game, item)
        self.assertTrue(success)

        self.assertIn(item.ix, self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

    def test_verb_func_does_not_add_to_inv_where_invitem_false(self):
        item = Thing(self._get_unique_noun())
        item.invItem = False
        self.start_room.addThing(item)

        self.assertFalse(item.ix in self.me.contains)

        success = getVerb._runVerbFuncAndEvents(self.game, item)
        self.assertFalse(success)

        self.assertNotIn(item.ix, self.me.contains)

    def test_verb_func_does_not_add_to_inv_where_already_in_inv(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        self.assertTrue(item.ix in self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

        success = getVerb._runVerbFuncAndEvents(self.game, item)
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

        self.game.turnMain(f"drop {item.verbose_name}")

        self.assertItemNotIn(
            item, self.me.contains, "Dropped item, but item still in inventory"
        )

    def test_drop_item_not_in_inv(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.start_room.addThing(item)
        self.assertNotIn(item.ix, self.me.contains)

        success = dropVerb._runVerbFuncAndEvents(self.game, item)
        self.assertFalse(success)


class TestSetVerbs(IFPTestCase):
    def test_set_in_adds_item(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        container = Container(self._get_unique_noun())
        self.start_room.addThing(container)

        self.assertNotIn(item.ix, container.contains)

        success = setInVerb._runVerbFuncAndEvents(self.game, item, container)
        self.assertTrue(success)

        self.assertIn(item.ix, container.contains)
        self.assertIn(item, container.contains[item.ix])

    def test_set_on_adds_item(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        surface = Surface(self._get_unique_noun())
        self.start_room.addThing(surface)

        self.assertNotIn(item.ix, surface.contains)

        success = setOnVerb._runVerbFuncAndEvents(self.game, item, surface)
        self.assertTrue(success)

        self.assertIn(item.ix, surface.contains)
        self.assertIn(item, surface.contains[item.ix])

    def test_set_under_adds_item(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        underspace = UnderSpace(self._get_unique_noun())
        self.start_room.addThing(underspace)

        self.assertNotIn(item.ix, underspace.contains)

        success = setUnderVerb._runVerbFuncAndEvents(self.game, item, underspace)
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

        success = setInVerb._runVerbFuncAndEvents(self.game, item, invalid_iobj)
        self.assertFalse(success)

        self.assertNotIn(item.ix, invalid_iobj.contains)

    def test_cannot_set_on_non_surface(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        success = setOnVerb._runVerbFuncAndEvents(self.game, item, invalid_iobj)
        self.assertFalse(success)

        self.assertNotIn(item.ix, invalid_iobj.contains)

    def test_cannot_set_under_non_underspace(self):
        item = Thing(self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        success = setUnderVerb._runVerbFuncAndEvents(self.game, item, invalid_iobj)
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

        lookVerb._runVerbFuncAndEvents(self.game)
        look_desc = self.app.print_stack.pop()
        look_title = self.app.print_stack.pop()

        self.assertIn(room.name, look_title, f"Room title printed incorrectly")
        self.assertIn(room.desc, look_desc, "Room description not printed by look")
        self.assertIn(item.desc, look_desc, "Item description not printed by look")

    def test_examine(self):
        item = Thing("widget")
        item.xdescribeThing("It's a shiny little widget. ")

        examineVerb._runVerbFuncAndEvents(self.game, item)

        examine_desc = self.app.print_stack.pop()

        self.assertEqual(
            examine_desc,
            item.xdesc,
            f"Examine desc printed incorrectly. Expecting {item.xdesc}, got {examine_desc}",
        )

    def test_look_in(self):
        parent = Container("shoebox")
        child = Thing("penny")
        parent.addThing(child)

        lookInVerb._runVerbFuncAndEvents(self.game, parent)

        look_in_desc = self.app.print_stack.pop()

        self.assertEqual(
            look_in_desc,
            parent.contains_desc,
            f"Contains desc printed incorrectly. Expected {parent.contains_desc} got "
            f"{look_in_desc}",
        )

    def test_look_under(self):
        parent = UnderSpace("table")
        child = Thing("penny")
        parent.addThing(child)

        lookUnderVerb._runVerbFuncAndEvents(self.game, parent)

        look_under_desc = self.app.print_stack.pop()

        self.assertEqual(
            look_under_desc,
            parent.contains_desc,
            f"Contains desc printed incorrectly. Expected {parent.contains_desc} got "
            f"{look_under_desc}",
        )

    def test_read(self):
        item = Readable("note", "I'm sorry, but I have to do this. ")

        readVerb._runVerbFuncAndEvents(self.game, item)

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

        getAllVerb._runVerbFuncAndEvents(self.game)
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

        getAllVerb._runVerbFuncAndEvents(self.game)
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

        dropAllVerb._runVerbFuncAndEvents(self.game)
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
        dropAllVerb._runVerbFuncAndEvents(self.game)
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

        openVerb._runVerbFuncAndEvents(self.game, self.door.entranceA)

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

        closeVerb._runVerbFuncAndEvents(self.game, self.door.entranceA)

        self.assertFalse(
            self.door.entranceA.is_open,
            "Performed close verb on open door, but door is open. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_lock_door(self):
        self.lock.is_locked = False
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        lockVerb._runVerbFuncAndEvents(self.game, self.door.entranceA)

        self.assertTrue(
            self.lock.is_locked,
            "Performed lock verb with key in inv, but lock is unlocked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_unlock_door(self):
        self.lock.is_locked = True
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        unlockVerb._runVerbFuncAndEvents(self.game, self.door.entranceA)

        self.assertFalse(
            self.lock.is_locked,
            "Performed unlock verb with key in inv, but lock is locked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_lock_door_with(self):
        self.lock.is_locked = False
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        lockWithVerb._runVerbFuncAndEvents(self.game, self.door.entranceA, self.key)

        self.assertTrue(
            self.lock.is_locked,
            "Performed lock with verb with key, but lock is unlocked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_unlock_door_with(self):
        self.lock.is_locked = True
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        unlockWithVerb._runVerbFuncAndEvents(self.game, self.door.entranceA, self.key)

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

        openVerb._runVerbFuncAndEvents(self.game, self.door.entranceA)

        self.assertFalse(
            self.door.entranceA.is_open,
            "Performed open verb on locked door, but door is open. "
            f"Msg: {self.app.print_stack[-1]}",
        )


class TestLidVerbs(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("chest")
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

        openVerb._runVerbFuncAndEvents(self.game, self.container)

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

        closeVerb._runVerbFuncAndEvents(self.game, self.container)

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

        openVerb._runVerbFuncAndEvents(self.game, self.container)

        self.assertFalse(
            self.container.is_open,
            "Performed open verb on locked container, but lid is open. "
            f"Msg: {self.app.print_stack[-1]}",
        )


class TestEmptyInventory(IFPTestCase):
    def test_view_empty_inv(self):
        dropAllVerb._runVerbFuncAndEvents(self.game)
        self.assertEqual(
            len(self.me.contains), 0, "This test requires an empty player inventory"
        )

        EMPTY_INV_MSG = "You don't have anything with you. "

        invVerb._runVerbFuncAndEvents(self.game)
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
        self.child = Container("slot")
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

        wearVerb._runVerbFuncAndEvents(self.game, self.clothing)
        wearVerb._runVerbFuncAndEvents(self.game, self.clothing1)
        wearVerb._runVerbFuncAndEvents(self.game, self.clothing2)

    def strip_desc(self, desc):
        desc = desc.replace(". ", "").replace(",", "").replace("and", "")
        return " ".join(desc.split())

    def test_inventory_items_desc(self):
        BASE_MSG = "You have"

        invVerb._runVerbFuncAndEvents(self.game)
        self.app.print_stack.pop()
        inv_desc = self.app.print_stack.pop()

        parent_desc = self.parent.lowNameArticle()
        stacked_desc = (
            f"{len(self.me.contains[self.stacked1.ix])} " f"{self.stacked1.plural}"
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

        invVerb._runVerbFuncAndEvents(self.game)
        wearing_desc = self.app.print_stack.pop()

        clothing_desc = self.clothing.lowNameArticle()
        stacked_clothing_desc = (
            f"{len(self.me.wearing[self.clothing1.ix])} " f"{self.clothing1.plural}"
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
        self.surface = Surface("bench")
        self.start_room.addThing(self.surface)

    def test_climb_on_cannot_sit_stand_lie(self):
        FAILURE_MSG = f"You cannot climb on {self.surface.lowNameArticle(True)}. "

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbOnVerb._runVerbFuncAndEvents(self.game, self.surface)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_on_can_lie(self):
        SUCCESS_MSG = f"You lie on {self.surface.lowNameArticle(True)}. "

        self.surface.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbOnVerb._runVerbFuncAndEvents(self.game, self.surface)
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_on_can_sit(self):
        SUCCESS_MSG = f"You sit on {self.surface.lowNameArticle(True)}. "

        self.surface.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbOnVerb._runVerbFuncAndEvents(self.game, self.surface)
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_on_can_stand(self):
        SUCCESS_MSG = f"You stand on {self.surface.lowNameArticle(True)}. "

        self.surface.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbOnVerb._runVerbFuncAndEvents(self.game, self.surface)
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetOff(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.surface = Surface("bench")
        self.surface.can_contain_standing_player = True
        self.start_room.addThing(self.surface)
        climbOnVerb._runVerbFuncAndEvents(self.game, self.surface)
        self.assertIs(self.me.location, self.surface)

    def test_climb_down_from(self):
        SUCCESS_MSG = f"You climb down from {self.surface.lowNameArticle(True)}. "

        climbDownFromVerb._runVerbFuncAndEvents(self.game, self.surface)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_down(self):
        SUCCESS_MSG = f"You climb down from {self.surface.lowNameArticle(True)}. "

        climbDownVerb._runVerbFuncAndEvents(self.game)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetIn(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("box")
        self.start_room.addThing(self.container)

    def test_climb_in_cannot_sit_stand_lie(self):
        FAILURE_MSG = f"You cannot climb into {self.container.lowNameArticle(True)}. "

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_lie(self):
        SUCCESS_MSG = f"You lie in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_sit(self):
        SUCCESS_MSG = f"You sit in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_stand(self):
        SUCCESS_MSG = f"You stand in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetInOpenLid(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("box")
        self.container.has_lid = True
        self.container.is_open = True
        self.start_room.addThing(self.container)

    def test_climb_in_can_lie(self):
        SUCCESS_MSG = f"You lie in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_sit(self):
        SUCCESS_MSG = f"You sit in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_stand(self):
        SUCCESS_MSG = f"You stand in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetInClosedLid(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("box")
        self.container.has_lid = True
        self.container.is_open = False
        self.start_room.addThing(self.container)

    def test_climb_in_can_lie(self):
        FAILURE_MSG = (
            f"You cannot climb into {self.container.lowNameArticle(True)}, "
            "since it is closed. "
        )

        self.container.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_sit(self):
        FAILURE_MSG = (
            f"You cannot climb into {self.container.lowNameArticle(True)}, "
            "since it is closed. "
        )

        self.container.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_stand(self):
        FAILURE_MSG = (
            f"You cannot climb into {self.container.lowNameArticle(True)}, "
            "since it is closed. "
        )

        self.container.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)


class TestPlayerGetOut(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container("box")
        self.container.can_contain_standing_player = True
        self.start_room.addThing(self.container)
        climbInVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.container)

    def test_climb_out_of(self):
        SUCCESS_MSG = f"You climb out of {self.container.lowNameArticle(True)}. "

        climbOutOfVerb._runVerbFuncAndEvents(self.game, self.container)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_out(self):
        SUCCESS_MSG = f"You climb out of {self.container.lowNameArticle(True)}. "

        climbOutVerb._runVerbFuncAndEvents(self.game)
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


if __name__ == "__main__":
    unittest.main()

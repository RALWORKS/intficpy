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
from intficpy.exceptions import AbortTurn, ObjectMatchError
from intficpy.room import Room
from intficpy.travel import DoorConnector


class TestDropVerb(IFPTestCase):
    def test_verb_func_drops_item(self):
        item = Thing(self.game, self._get_unique_noun())
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
        item = Thing(self.game, "shoe")
        item.invItem = True
        self.start_room.addThing(item)
        self.assertFalse(self.me.containsItem(item))

        self.game.turnMain(f"drop {item.verbose_name}")
        self.assertIn("You are not holding", self.app.print_stack.pop())


class TestSetVerbs(IFPTestCase):
    def test_set_in_adds_item(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        container = Container(self.game, self._get_unique_noun())
        self.start_room.addThing(container)

        self.assertNotIn(item.ix, container.contains)

        self.game.turnMain(f"set {item.verbose_name} in {container.verbose_name}")

        self.assertIn(item.ix, container.contains)
        self.assertIn(item, container.contains[item.ix])

    def test_set_on_adds_item(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        surface = Surface(self.game, self._get_unique_noun())
        self.start_room.addThing(surface)

        self.assertNotIn(item.ix, surface.contains)

        self.game.turnMain(f"set {item.verbose_name} on {surface.verbose_name}")

        self.assertIn(item.ix, surface.contains)
        self.assertIn(item, surface.contains[item.ix])

    def test_set_under_adds_item(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        underspace = UnderSpace(self.game, self._get_unique_noun())
        self.start_room.addThing(underspace)

        self.assertNotIn(item.ix, underspace.contains)

        self.game.turnMain(f"set {item.verbose_name} under {underspace.verbose_name}")

        self.assertIn(item.ix, underspace.contains)
        self.assertIn(item, underspace.contains[item.ix])

    def test_cannot_set_in_non_container(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self.game, self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        self.game.turnMain(f"set {item.verbose_name} in {invalid_iobj.verbose_name}")

        self.assertNotIn(item.ix, invalid_iobj.contains)

    def test_cannot_set_on_non_surface(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self.game, self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        self.game.turnMain(f"set {item.verbose_name} on {invalid_iobj.verbose_name}")

        self.assertNotIn(item.ix, invalid_iobj.contains)

    def test_cannot_set_under_non_underspace(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self.game, self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        self.game.turnMain(f"set {item.verbose_name} under {invalid_iobj.verbose_name}")

        self.assertNotIn(item.ix, invalid_iobj.contains)


class TestInventoryVerbs(IFPTestCase):
    def test_get_all_drop(self):
        item1 = Thing(self.game, "miracle")
        item2 = Thing(self.game, "wonder")
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

        self.game.turnMain("take all")
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

        self.game.turnMain("take all")
        getall_msg = self.app.print_stack.pop()
        self.assertEqual(getall_msg, "There are no obvious items here to take. ")

    def test_drop_all(self):
        item1 = Thing(self.game, "miracle")
        item2 = Thing(self.game, "wonder")
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

        self.game.turnMain("drop all")
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
        self.game.turnMain("drop all")
        dropall_msg = self.app.print_stack.pop()
        self.assertEqual(dropall_msg, "Your inventory is empty. ")


class TestDoorVerbs(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.room2 = Room(self.game, "A hot room", "This room is uncomfortably hot. ")
        self.door = DoorConnector(self.game, self.start_room, "se", self.room2, "nw")
        self.key = Key(self.game, "key")
        self.me.addThing(self.key)
        self.lock = Lock(self.game, False, self.key)
        self.lock.is_locked = False
        self.door.setLock(self.lock)

    def test_open_door(self):
        self.assertFalse(
            self.door.entrance_a.is_open,
            "This test needs the door to be initially closed",
        )
        self.assertFalse(
            self.door.entrance_a.lock_obj.is_locked,
            "This test needs the door to be initially unlocked",
        )

        self.game.turnMain("open door")

        self.assertTrue(
            self.door.entrance_a.is_open,
            "Performed open verb on unlocked door, but door is closed. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_close_door(self):
        self.door.entrance_a.makeOpen()
        self.assertTrue(
            self.door.entrance_a.is_open,
            "This test needs the door to be initially open",
        )

        self.game.turnMain("close door")

        self.assertFalse(
            self.door.entrance_a.is_open,
            "Performed close verb on open door, but door is open. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_lock_door(self):
        self.lock.is_locked = False
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        self.game.turnMain("lock door")

        self.assertTrue(
            self.lock.is_locked,
            "Performed lock verb with key in inv, but lock is unlocked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_unlock_door(self):
        self.lock.is_locked = True
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        self.game.turnMain("unlock door")

        self.assertFalse(
            self.lock.is_locked,
            "Performed unlock verb with key in inv, but lock is locked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_lock_door_with(self):
        self.lock.is_locked = False
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        self.game.turnMain("lock door with key")

        self.assertTrue(
            self.lock.is_locked,
            "Performed lock with verb with key, but lock is unlocked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_unlock_door_with(self):
        self.lock.is_locked = True
        self.assertIn(self.key.ix, self.me.contains)
        self.assertIn(self.key, self.me.contains[self.key.ix])

        self.game.turnMain("unlock door with key")

        self.assertFalse(
            self.lock.is_locked,
            "Performed unlock verb with key, but lock is locked. "
            f"Msg: {self.app.print_stack[-1]}",
        )

    def test_open_locked_door(self):
        self.lock.is_locked = True
        self.assertFalse(
            self.door.entrance_a.is_open,
            "This test needs the door to be initially closed",
        )
        self.assertTrue(
            self.door.entrance_a.lock_obj.is_locked,
            "This test needs the door to be initially locked",
        )

        self.game.turnMain("open door")

        self.assertFalse(
            self.door.entrance_a.is_open,
            "Performed open verb on locked door, but door is open. "
            f"Msg: {self.app.print_stack[-1]}",
        )


class TestLidVerbs(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container(self.game, "chest")
        self.container.has_lid = True
        self.container.is_open = False
        self.key = Key(self.game, "key")
        self.me.addThing(self.key)
        self.lock = Lock(self.game, False, self.key)
        self.lock.is_locked = False
        self.container.setLock(self.lock)
        self.container.moveTo(self.start_room)

    def test_open_container(self):
        self.assertFalse(
            self.container.is_open,
            "This test needs the container to be initially closed",
        )
        self.assertFalse(
            self.container.lock_obj.is_locked,
            "This test needs the container to be initially unlocked",
        )

        self.game.turnMain("open chest")

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

        self.game.turnMain("close chest")

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

        self.game.turnMain("open chest")

        self.assertFalse(
            self.container.is_open,
            "Performed open verb on locked container, but lid is open. "
            f"Msg: {self.app.print_stack[-1]}",
        )


class TestEmptyInventory(IFPTestCase):
    def test_view_empty_inv(self):
        self.game.turnMain("drop all")
        self.assertEqual(
            len(self.me.contains), 0, "This test requires an empty player inventory"
        )

        EMPTY_INV_MSG = "You don't have anything with you. "

        self.game.turnMain("i")
        inv_msg = self.app.print_stack.pop()

        self.assertEqual(
            inv_msg,
            EMPTY_INV_MSG,
            "Viewed empty inventory. Message does not match expected. ",
        )


class TestFullInventory(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.parent = Thing(self.game, "cube")
        self.child = Container(self.game, "slot")
        self.parent.addComposite(self.child)
        self.stacked1 = Thing(self.game, "tile")
        self.stacked2 = self.stacked1.copyThing()
        self.clothing = Clothing(self.game, "scarf")
        self.clothing1 = Clothing(self.game, "mitten")
        self.clothing2 = self.clothing1.copyThing()

        self.me.addThing(self.parent)
        self.me.addThing(self.child)
        self.me.addThing(self.stacked1)
        self.me.addThing(self.stacked2)
        self.me.addThing(self.clothing)
        self.me.addThing(self.clothing1)
        self.me.addThing(self.clothing2)

        self.game.turnMain("wear scarf")
        self.game.turnMain("wear mitten")
        self.game.turnMain("wear mitten")

    def strip_desc(self, desc):
        desc = desc.replace(". ", "").replace(",", "").replace("and", "")
        return " ".join(desc.split())

    def test_inventory_items_desc(self):
        BASE_MSG = "You have"

        self.game.turnMain("i")
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

        self.game.turnMain("i")
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
        self.surface = Surface(self.game, "bench")
        self.start_room.addThing(self.surface)

    def test_climb_on_cannot_sit_stand_lie(self):
        FAILURE_MSG = f"You cannot climb on {self.surface.lowNameArticle(True)}. "

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_on_can_lie(self):
        SUCCESS_MSG = f"You lie on {self.surface.lowNameArticle(True)}. "

        self.surface.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_on_can_sit(self):
        SUCCESS_MSG = f"You sit on {self.surface.lowNameArticle(True)}. "

        self.surface.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_on_can_stand(self):
        SUCCESS_MSG = f"You stand on {self.surface.lowNameArticle(True)}. "

        self.surface.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetOff(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.surface = Surface(self.game, "bench")
        self.surface.can_contain_standing_player = True
        self.start_room.addThing(self.surface)
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.surface)

    def test_climb_down_from(self):
        SUCCESS_MSG = f"You climb down from {self.surface.lowNameArticle(True)}. "

        self.game.turnMain("climb down from bench")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_down(self):
        SUCCESS_MSG = f"You climb down from {self.surface.lowNameArticle(True)}. "

        self.game.turnMain("climb down")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetIn(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container(self.game, "box")
        self.start_room.addThing(self.container)

    def test_climb_in_cannot_sit_stand_lie(self):
        FAILURE_MSG = f"You cannot climb into {self.container.lowNameArticle(True)}. "

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_lie(self):
        SUCCESS_MSG = f"You lie in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_sit(self):
        SUCCESS_MSG = f"You sit in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_stand(self):
        SUCCESS_MSG = f"You stand in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetInOpenLid(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container(self.game, "box")
        self.container.has_lid = True
        self.container.is_open = True
        self.start_room.addThing(self.container)

    def test_climb_in_can_lie(self):
        SUCCESS_MSG = f"You lie in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_sit(self):
        SUCCESS_MSG = f"You sit in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_stand(self):
        SUCCESS_MSG = f"You stand in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetInClosedLid(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container(self.game, "box")
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
        self.game.turnMain("climb in box")
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
        self.game.turnMain("climb in box")
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
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)


class TestPlayerGetOut(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container(self.game, "box")
        self.container.can_contain_standing_player = True
        self.start_room.addThing(self.container)
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

    def test_climb_out_of(self):
        SUCCESS_MSG = f"You climb out of {self.container.lowNameArticle(True)}. "

        self.game.turnMain("climb out of box")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_out(self):
        SUCCESS_MSG = f"You climb out of {self.container.lowNameArticle(True)}. "

        self.game.turnMain("climb out")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

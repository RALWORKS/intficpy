from ..helpers import IFPTestCase

from intficpy.things import (
    Container,
    Lock,
    Key,
)
from intficpy.travel import DoorConnector
from intficpy.room import Room


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

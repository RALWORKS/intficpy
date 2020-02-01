import os

from .helpers import IFPTestCase

from intficpy.serializer import SaveGame, LoadGame
from intficpy.daemons import Daemon
from intficpy.thing_base import Thing
from intficpy.things import Surface, Container


class TestSaveLoadOneRoomWithPlayer(IFPTestCase):
    def setUp(self):
        super().setUp()
        FILENAME = "_ifp_tests_saveload__0001.sav"

        path = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(path, FILENAME)

    def test_save_file_size_does_not_grow(self):
        size = []

        for i in range(0, 5):
            SaveGame(self.path)
            size.append(os.path.getsize(self.path))
            l = LoadGame(self.path)
            l.is_valid()
            l.load()

        self.assertTrue(
            size[-1] - size[0] < 300,
            f"Save files appear to be growing in size. Sizes: {size}",
        )

    def tearDown(self):
        super().tearDown()
        os.remove(self.path)


class TestSaveLoadNested(IFPTestCase):
    def setUp(self):
        super().setUp()
        FILENAME = "_ifp_tests_saveload__0002.sav"

        path = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(path, FILENAME)

        self.item1 = Surface("table", self.game)
        self.item2 = Container("box", self.game)
        self.item3 = Container("cup", self.game)
        self.item4 = Thing("bean")
        self.item5 = Thing("spider")

        self.start_room.addThing(self.item1)
        self.item1.addThing(self.item2)
        self.item2.addThing(self.item3)
        self.item3.addThing(self.item4)
        self.item2.addThing(self.item5)

        SaveGame(self.path)
        self.start_room.removeThing(self.item1)
        self.item1.removeThing(self.item2)
        self.item2.removeThing(self.item3)
        self.item3.removeThing(self.item4)
        self.item2.removeThing(self.item5)

    def test_load(self):
        l = LoadGame(self.path)
        self.assertTrue(l.is_valid(), "Save file invalid. Cannot proceed.")
        l.load()

        self.assertItemExactlyOnceIn(
            self.item1, self.start_room.contains, "Failed to load top level item."
        )

        self.assertItemExactlyOnceIn(
            self.item2, self.item1.contains, "Failed to load item nested with depth 1."
        )

        self.assertItemExactlyOnceIn(
            self.item3, self.item2.contains, "Failed to load item nested with depth 2."
        )

        self.assertItemExactlyOnceIn(
            self.item5, self.item2.contains, "Failed to load item nested with depth 2."
        )

        self.assertItemExactlyOnceIn(
            self.item4, self.item3.contains, "Failed to load item nested with depth 3."
        )

    def tearDown(self):
        super().tearDown()
        os.remove(self.path)


class TestSaveLoadComplexAttribute(IFPTestCase):
    def setUp(self):
        super().setUp()
        FILENAME = "_ifp_tests_saveload__0003.sav"

        path = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(path, FILENAME)

        self.item1 = Surface("table", self.game)
        self.item2 = Container("box", self.game)

        self.EXPECTED_ATTR = {
            "data": {"sarah_has_seen": True, "containers": [self.item1],},
            "owner": self.me,
        }

        self.item1.custom_attr = self.EXPECTED_ATTR.copy()

        SaveGame(self.path)
        self.item1.custom_attr.clear()

    def test_load(self):
        self.assertFalse(
            self.item1.custom_attr,
            "This test needs custom_attr to be intitially empty.",
        )

        l = LoadGame(self.path)
        self.assertTrue(l.is_valid(), "Save file invalid. Cannot proceed.")
        l.load()

        self.assertTrue(
            self.item1.custom_attr,
            "Loaded save file, but custom attribute still empty.",
        )
        self.assertEqual(
            self.item1.custom_attr,
            self.EXPECTED_ATTR,
            "Custom attribute does not match expected",
        )

    def tearDown(self):
        super().tearDown()
        os.remove(self.path)


class TestSaveLoadDaemon(IFPTestCase):
    def setUp(self):
        super().setUp()
        FILENAME = "_ifp_tests_saveload__0004.sav"

        path = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(path, FILENAME)

        self.initial_counter = 0
        self.daemon = Daemon(self._daemon_func)
        self.daemon.counter = 0
        self.game.daemons.add(self.daemon)

        SaveGame(self.path)
        self.daemon.counter = 67
        self.game.daemons.remove(self.daemon)

    def _daemon_func(self, me, app):
        app.printToGUI(f"Turn #{self.daemon.counter}")
        self.daemon.counter += 1

    def test_load(self):
        self.assertNotEqual(
            self.daemon.counter,
            self.initial_counter,
            "This test needs the daemon counter to start at a different value from "
            "The value to load",
        )
        self.assertNotIn(
            self.daemon, self.game.daemons.active, "Daemon should start as inactive."
        )

        l = LoadGame(self.path)
        self.assertTrue(l.is_valid(), "Save file invalid. Cannot proceed.")
        l.load()

        self.assertIn(
            self.daemon,
            self.game.daemons.active,
            "Daemon was not re-added to active after loading.",
        )
        self.assertEqual(
            self.daemon.counter,
            self.initial_counter,
            "Daemon counter does not match expected.",
        )

    def tearDown(self):
        super().tearDown()
        os.remove(self.path)

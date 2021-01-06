import os
import pickle
import uuid

from intficpy.serializer import SaveGame, LoadGame
from intficpy.daemons import Daemon
from intficpy.thing_base import Thing
from intficpy.things import Surface, Container

from .helpers import IFPTestCase


class TestSaveLoadOneRoomWithPlayer(IFPTestCase):
    def setUp(self):
        super().setUp()
        FILENAME = f"_ifp_tests_saveload__{uuid.uuid4()}.sav"

        path = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(path, FILENAME)

    def test_save_file_size_does_not_grow(self):
        size = []
        locs_bytes = []
        locs_keys = []
        ifp_obj_bytes = []
        ifp_obj_keys = []

        initial_obj = None

        for i in range(0, 5):
            SaveGame(self.game, self.path)
            size.append(os.path.getsize(self.path))
            l = LoadGame(self.game, self.path)
            self.assertTrue(l.is_valid())

            locs_bytes.append(len(pickle.dumps(l.validated_data["locations"])))
            ifp_obj_bytes.append(len(pickle.dumps(l.validated_data["ifp_objects"])))

            locs_keys.append(len(l.validated_data["locations"]))
            ifp_obj_keys.append(len(l.validated_data["ifp_objects"]))

            if i == 0:
                initial_obj = l.validated_data
            elif i == 4:
                latest_obj = l.validated_data

            l.load()

        initial_obj_sizes = {}
        for key, value in initial_obj["ifp_objects"].items():
            initial_obj_sizes[key] = len(pickle.dumps(value))

        initial_loc_sizes = {}
        for key, value in initial_obj["locations"].items():
            initial_loc_sizes[key] = len(pickle.dumps(value))

        final_obj_sizes = {}
        for key, value in latest_obj["ifp_objects"].items():
            final_obj_sizes[key] = len(pickle.dumps(value))

        final_loc_sizes = {}
        for key, value in latest_obj["locations"].items():
            final_loc_sizes[key] = len(pickle.dumps(value))

        obj_deltas = {}
        for key, value in final_obj_sizes.items():
            if value == initial_obj_sizes[key]:
                continue
            obj_deltas[abs(value - initial_loc_sizes[key])] = (
                initial_obj["ifp_objects"][key],
                latest_obj["ifp_objects"][key],
            )

        if obj_deltas:
            max_obj_delta = max(obj_deltas.keys())
            most_changed_obj = obj_deltas[max_obj_delta]
        else:
            max_obj_delta = 0
            most_changed_obj = (None, None)

        loc_deltas = {}
        for key, value in final_loc_sizes.items():
            if value == initial_loc_sizes[key]:
                continue
            loc_deltas[abs(value - initial_loc_sizes[key])] = (
                initial_obj["locations"][key],
                latest_obj["locations"][key],
            )

        if loc_deltas:
            max_loc_delta = max(loc_deltas.keys())
            most_changed_loc = loc_deltas[max_loc_delta]
        else:
            max_loc_delta = 0
            most_changed_loc = (None, None)

        self.assertTrue(
            size[-1] - size[0] < 300,
            f"Save files appear to be growing in size. Sizes: {size}\n"
            f"Locations: {locs_bytes}\n"
            f"Location keys: {locs_keys}\n"
            f"IFP_Objects: {ifp_obj_bytes}\n"
            f"IFP_Object keys: {ifp_obj_keys}\n\n"
            f"IFP_Object with greatest change in size (delta = {max_obj_delta}):\n\n"
            f"{most_changed_obj[0]}\n\n-->\n\n{most_changed_obj[1]}\n\n"
            f"Location with greatest change in size (delta = {max_loc_delta}):\n"
            f"{most_changed_loc[0]}\n\n-->\n\n{most_changed_loc[1]}",
        )

        self.assertEqual(
            initial_obj, latest_obj, "Initial and final loaded data did not match."
        )

    def tearDown(self):
        super().tearDown()
        os.remove(self.path)


class TestSaveLoadNested(IFPTestCase):
    def setUp(self):
        super().setUp()
        FILENAME = f"_ifp_tests_saveload__{uuid.uuid4()}.sav"

        path = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(path, FILENAME)

        self.item1 = Surface(self.game, "table")
        self.item2 = Container(self.game, "box")
        self.item3 = Container(self.game, "cup")
        self.item4 = Thing(self.game, "bean")
        self.item5 = Thing(self.game, "spider")

        self.start_room.addThing(self.item1)
        self.item1.addThing(self.item2)
        self.item2.addThing(self.item3)
        self.item3.addThing(self.item4)
        self.item2.addThing(self.item5)

        SaveGame(self.game, self.path)
        self.start_room.removeThing(self.item1)
        self.item1.removeThing(self.item2)
        self.item2.removeThing(self.item3)
        self.item3.removeThing(self.item4)
        self.item2.removeThing(self.item5)

    def test_load(self):
        l = LoadGame(self.game, self.path)
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

        self.item1 = Surface(self.game, "table")
        self.item2 = Container(self.game, "box")

        self.EXPECTED_ATTR = {
            "data": {"sarah_has_seen": True, "containers": [self.item1],},
            "owner": self.me,
        }

        self.item1.custom_attr = self.EXPECTED_ATTR.copy()

        SaveGame(self.game, self.path)
        self.item1.custom_attr.clear()

    def test_load(self):
        self.assertFalse(
            self.item1.custom_attr,
            "This test needs custom_attr to be intitially empty.",
        )

        l = LoadGame(self.game, self.path)
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
        self.daemon = Daemon(self.game, self._daemon_func)
        self.daemon.counter = 0
        self.game.daemons.add(self.daemon)

        SaveGame(self.game, self.path)
        self.daemon.counter = 67
        self.game.daemons.remove(self.daemon)

    def _daemon_func(self, game):
        game.addText(f"Turn #{self.daemon.counter}")
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

        l = LoadGame(self.game, self.path)
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

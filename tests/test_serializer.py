import os

from .helpers import IFPTestCase

from intficpy.serializer import curSave
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
            curSave.saveState(self.me, self.path, __name__)
            size.append(os.path.getsize(self.path))
            curSave.loadState(self.me, self.path, self.app, __name__)

        self.assertTrue(
            size[-1] - size[0] < 300,
            f"Save files appear to be growing in size. Sizes: {size}",
        )

        os.remove(self.path)


class TestSaveLoadNested(IFPTestCase):
    def setUp(self):
        super().setUp()
        FILENAME = "_ifp_tests_saveload__0002.sav"

        path = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(path, FILENAME)

        self.item1 = Surface("table", self.me)
        self.item2 = Container("box", self.me)
        self.item3 = Container("cup", self.me)
        self.item4 = Thing("bean")
        self.item5 = Thing("spider")

        self.start_room.addThing(self.item1)
        self.item1.addThing(self.item2)
        self.item2.addThing(self.item3)
        self.item3.addThing(self.item4)
        self.item2.addThing(self.item5)

        curSave.saveState(self.me, self.path, __name__)
        self.start_room.removeThing(self.item1)
        self.item1.removeThing(self.item2)
        self.item2.removeThing(self.item3)
        self.item3.removeThing(self.item4)
        self.item2.removeThing(self.item5)

    def test_load(self):
        curSave.loadState(self.me, self.path, self.app, __name__)

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

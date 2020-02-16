from unittest import TestCase
import random

from intficpy.actor import Player
from intficpy.room import Room
from intficpy.vocab import nounDict
from intficpy.ifp_game import IFPGame


class TestApp:
    def __init__(self):
        self.print_stack = []

    def printEventText(self, event):
        for t in event.text:
            self.print_stack.append(t)


class IFPTestCase(TestCase):
    def setUp(self):
        self.app = TestApp()
        self.me = Player("me")
        self.game = IFPGame(self.me, self.app)
        self.start_room = Room("room", "desc")
        self.start_room.addThing(self.me)
        self.me.setPlayer()
        self.game.initGame()

    def _insert_dobj_into_phrase(self, phrase, dobj):
        ix = phrase.index("<dobj>")
        phrase = phrase[:ix] + dobj + phrase[ix + 1 :]
        return phrase

    def _insert_iobj_into_phrase(self, phrase, iobj):
        ix = phrase.index("<iobj>")
        phrase = phrase[:ix] + iobj + phrase[ix + 1 :]
        return phrase

    def _insert_objects_into_phrase(self, phrase, dobj, iobj):
        phrase = self._insert_dobj_into_phrase(phrase, dobj)
        phrase = self._insert_iobj_into_phrase(phrase, iobj)
        return phrase

    def _get_unique_noun(self):
        noun = str(random.getrandbits(128))
        if noun in nounDict:
            noun = self._get_unique_noun()
        return noun

    def assertItemIn(self, item, contains_dict, msg):
        self.assertIn(item.ix, contains_dict, f"Index not in dictionary: {msg}")
        self.assertIn(
            item,
            contains_dict[item.ix],
            f"Index in dictionary, but item not found under index: {msg}",
        )

    def assertItemNotIn(self, item, contains_dict, msg):
        if item.ix in contains_dict:
            self.assertNotIn(
                item,
                contains_dict[item.ix],
                f"Item unexpectedly found in dictionary: {msg}",
            )

    def assertItemExactlyOnceIn(self, item, contains_dict, msg):
        self.assertIn(item.ix, contains_dict, f"Index not in dictionary: {msg}")
        n = len(contains_dict[item.ix])
        self.assertEqual(
            n, 1, f"Expected a single occurrence of item {item}, found {n}: {msg}"
        )

from unittest import TestCase
import random

from intficpy.actor import Player
from intficpy.room import Room
from intficpy.vocab import nounDict

class TestApp:
    def __init__(self):
        pass

    def printToGUI(self, msg, *args):
        print(f"APP PRINT: {msg}")

class IFPTestCase(TestCase):
    def setUp(self):
        self.app = TestApp()
        self.me = Player("me")
        self.start_room = Room("room", "desc")
        self.start_room.addThing(self.me)
        self.me.setPlayer()

    def _insert_dobj_into_phrase(self, phrase, dobj):
        ix = phrase.index("<dobj>")
        phrase = phrase[:ix] + dobj + phrase[ix+1:]
        return phrase

    def _insert_iobj_into_phrase(self, phrase, iobj):
        ix = phrase.index("<iobj>")
        phrase = phrase[:ix] + iobj + phrase[ix+1:]
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

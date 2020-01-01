from unittest import main, TestCase

from intficpy.thing_base import Thing
from intficpy.actor import Player
from intficpy.room import Room
from intficpy.vocab import english, verbDict, nounDict
from intficpy.parser import getThing, initGame


class TestParser(TestCase):
    def setUp(self):
        class App:
            def __init__(self):
                pass

            def printToGUI(self, msg, *args):
                print(f"APP PRINT: {msg}")

        self.app = App()
        self.me = Player("me")
        self.room = Room("room", "desc")
        self.room.addThing(self.me)
        self.me.setPlayer()

    def test_get_thing(self):
        noun = "neverseenthisonebefore"
        self.assertNotIn(
            noun,
            nounDict,
            f"This test needs the value of noun ({noun}) to be such that it does not "
            "initially exist in nounDict",
        )
        item1 = Thing(noun)
        self.room.addThing(item1)
        self.assertTrue(
            noun in nounDict, "Name was not added to nounDict after Thing creation"
        )

        matched_item1 = getThing(self.me, self.app, [noun], "room", None, None)
        self.assertIs(
            matched_item1, item1, "Failed to match item from unambiguous noun"
        )

        item2 = Thing(noun)
        self.room.addThing(item2)
        self.assertEqual(len(nounDict[noun]), 2)

        adj1 = "unique"
        adj2 = "special"
        self.assertNotEqual(
            adj1, adj2, "This test requires that adj1 and adj2 are not equal"
        )

        item1.setAdjectives([adj1])
        item2.setAdjectives([adj2])

        matched_item1 = getThing(self.me, self.app, [noun], "room", None, None)
        self.assertIsNone(
            matched_item1,
            "Matched single item with input that should have been ambiguous",
        )

        matched_item1 = getThing(self.me, self.app, [adj1, noun], "room", None, None)
        self.assertIs(
            matched_item1,
            item1,
            "Noun adjective array should have been unambiguous, but failed to match "
            "Thing",
        )


if __name__ == "__main__":
    main()

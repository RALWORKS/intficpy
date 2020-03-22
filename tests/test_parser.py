import unittest

from .helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import Surface, UnderSpace
from intficpy.vocab import nounDict
from intficpy.actor import Actor, SpecialTopic
from intficpy.verb import (
    getVerb,
    lookVerb,
    setOnVerb,
    leadDirVerb,
    jumpOverVerb,
    giveVerb,
    examineVerb,
)
from intficpy.exceptions import ObjectMatchError


class TestParser(IFPTestCase):
    def test_verb_with_no_objects(self):
        self.game.turnMain("look")

        self.assertIs(self.game.parser.previous_command.verb, lookVerb)
        self.assertIsNone(self.game.parser.previous_command.dobj.target)
        self.assertIsNone(self.game.parser.previous_command.iobj.target)

    def test_verb_with_dobj_only(self):
        dobj = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj)

        self.game.turnMain(f"get {dobj.name}")

        self.assertIs(self.game.parser.previous_command.verb, getVerb)
        self.assertIs(self.game.parser.previous_command.dobj.target, dobj)
        self.assertIsNone(self.game.parser.previous_command.iobj.target)

    def test_gets_correct_verb_with_dobj_and_direction_iobj(self):
        dobj = Actor(self._get_unique_noun())
        self.start_room.addThing(dobj)
        iobj = "east"
        self.start_room.east = self.start_room

        self.game.turnMain(f"lead {dobj.name} {iobj}")

        self.assertIs(self.game.parser.previous_command.verb, leadDirVerb)
        self.assertIs(self.game.parser.previous_command.dobj.target, dobj)
        self.assertEqual(self.game.parser.previous_command.iobj.target, [iobj])

    def test_gets_correct_verb_with_preposition_dobj_only(self):
        dobj = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj)

        self.game.turnMain(f"jump over {dobj.name}")

        self.assertIs(self.game.parser.previous_command.verb, jumpOverVerb)
        self.assertIs(self.game.parser.previous_command.dobj.target, dobj)
        self.assertIsNone(self.game.parser.previous_command.iobj.target)

    def test_gets_correct_verb_with_preposition_dobj_and_iobj(self):
        dobj = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj)
        iobj = Surface(self._get_unique_noun(), self.game)
        self.start_room.addThing(iobj)

        self.game.turnMain(f"set {dobj.name} on {iobj.name}")

        self.assertIs(self.game.parser.previous_command.verb, setOnVerb)
        self.assertIs(self.game.parser.previous_command.dobj.target, dobj)
        self.assertIs(self.game.parser.previous_command.iobj.target, iobj)


class TestGetGrammarObj(IFPTestCase):
    def test_gets_correct_objects_with_adjacent_dobj_iobj(self):
        dobj_item = Actor(self._get_unique_noun())
        self.start_room.addThing(dobj_item)
        iobj_item = Thing(self._get_unique_noun())
        self.start_room.addThing(iobj_item)

        self.game.turnMain(f"give {dobj_item.name} {iobj_item.name}")

        self.assertEqual(self.game.parser.previous_command.dobj.target, dobj_item)
        self.assertEqual(self.game.parser.previous_command.iobj.target, iobj_item)


class TestGetThing(IFPTestCase):
    def test_get_thing(self):
        noun = self._get_unique_noun()
        self.assertNotIn(
            noun,
            nounDict,
            f"This test needs the value of noun ({noun}) to be such that it does not "
            "initially exist in nounDict",
        )
        item1 = Thing(noun)
        self.start_room.addThing(item1)
        self.assertTrue(
            noun in nounDict, "Name was not added to nounDict after Thing creation"
        )

        self.game.turnMain(f"examine {noun}")
        self.assertIs(
            self.game.parser.previous_command.dobj.target,
            item1,
            "Failed to match item from unambiguous noun",
        )

        item2 = Thing(noun)
        self.start_room.addThing(item2)
        self.assertEqual(len(nounDict[noun]), 2)

        adj1 = "unique"
        adj2 = "special"
        self.assertNotEqual(
            adj1, adj2, "This test requires that adj1 and adj2 are not equal"
        )

        item1.setAdjectives([adj1])
        item2.setAdjectives([adj2])

        self.game.turnMain(f"examine {noun}")

        self.assertEqual(self.game.parser.previous_command.dobj.tokens, [noun])

        self.game.turnMain(f"examine {adj1} {noun}")
        self.assertIs(
            self.game.parser.previous_command.dobj.target,
            item1,
            "Noun adjective array should have been unambiguous, but failed to match "
            "Thing",
        )


class TestParserError(IFPTestCase):
    def test_verb_not_understood(self):
        self.game.turnMain("thisverbwillnevereverbedefined")

        msg = self.app.print_stack.pop()
        expected = "I don't understand the verb:"

        self.assertIn(expected, msg, "Unexpected response to unrecognized verb.")

    def test_suggestion_not_understood(self):
        topic = SpecialTopic(
            "tell sarah to grow a beard", "You tell Sarah to grow a beard."
        )

        self.game.parser.previous_command.specialTopics[
            "tell sarah to grow a beard"
        ] = topic

        self.game.turnMain("thisverbwillnevereverbedefined")

        msg = self.app.print_stack.pop()
        expected = "is not enough information to match a suggestion"

        self.assertIn(expected, msg, "Unexpected response to unrecognized suggestion.")

    def test_noun_not_understood(self):
        self.game.turnMain("take thisnounwillnevereverbedefined")

        msg = self.app.print_stack.pop()
        expected = "I don't see any"

        self.assertIn(expected, msg, "Unexpected response to unrecognized noun.")

    def test_verb_by_objects_unrecognized_noun(self):
        self.game.turnMain("lead sarah")

        msg = self.app.print_stack.pop()
        expected = "I understood as far as"

        self.assertIn(
            expected,
            msg,
            "Unexpected response attempting to disambiguate verb with unrecognized "
            "noun.",
        )

    def test_verb_by_objects_no_near_matches_unrecognized_noun(self):
        sarah1 = Actor("teacher")
        sarah1.setAdjectives(["good"])
        self.start_room.addThing(sarah1)

        sarah2 = Actor("teacher")
        sarah2.setAdjectives(["bad"])
        self.start_room.addThing(sarah2)

        self.game.turnMain("hi teacher")
        self.assertTrue(self.game.parser.previous_command.ambiguous)

        self.game.turnMain("set green sarah")

        msg = self.app.print_stack.pop()
        expected = "I understood as far as"

        self.assertIn(
            expected,
            msg,
            "Unexpected response attempting to disambiguate verb with unrecognized "
            "noun.",
        )


class TestCompositeObjectRedirection(IFPTestCase):
    def test_composite_object_redirection(self):
        bench = Surface("bench", self.game)
        self.start_room.addThing(bench)
        underbench = UnderSpace("space", self.game)
        bench.addComposite(underbench)

        widget = Thing("widget")
        underbench.addThing(widget)

        self.game.turnMain("look under bench")
        msg = self.app.print_stack.pop()

        self.assertIn(
            widget.verbose_name,
            msg,
            "Unexpected response attempting to use a component redirection",
        )


if __name__ == "__main__":
    unittest.main()

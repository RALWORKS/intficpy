import unittest

from .helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import Surface
from intficpy.vocab import nounDict
from intficpy.parser import getThing, getCurVerb, getGrammarObj, callVerb
from intficpy.verb import (
    getVerb,
    lookVerb,
    setOnVerb,
    leadDirVerb,
    jumpOverVerb,
    giveVerb,
    examineVerb,
)


class TestGetCurVerb(IFPTestCase):
    def test_gets_correct_verb_with_no_objects(self):
        tokens = lookVerb.syntax[0]

        expected_verb_tokens = lookVerb.syntax[0]

        gcv = getCurVerb(self.app, tokens)
        found_verbs = gcv[1]
        verb = gcv[0][0]
        verb_tokens = gcv[0][1]

        self.assertTrue(found_verbs)
        self.assertEqual(verb_tokens, expected_verb_tokens)
        self.assertIs(verb, lookVerb)

    def test_gets_correct_verb_with_dobj_only(self):
        tokens = self._insert_dobj_into_phrase(getVerb.syntax[0], ["yellow", "fish"])

        expected_verb_tokens = getVerb.syntax[0]

        gcv = getCurVerb(self.app, tokens)
        found_verbs = gcv[1]
        verb = gcv[0][0]
        verb_tokens = gcv[0][1]

        self.assertTrue(found_verbs)
        self.assertEqual(verb_tokens, expected_verb_tokens)
        self.assertIs(verb, getVerb)

    def test_gets_correct_verb_with_dobj_and_direction_iobj(self):

        dobj = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj)

        tokens = self._insert_objects_into_phrase(
            leadDirVerb.syntax[0], [dobj.name], ["north"]
        )

        expected_verb_tokens = leadDirVerb.syntax[0]

        gcv = getCurVerb(self.app, tokens)
        found_verbs = gcv[1]
        verb = gcv[0][0]
        verb_tokens = gcv[0][1]

        self.assertTrue(found_verbs)
        self.assertEqual(verb_tokens, expected_verb_tokens)
        self.assertIs(verb, leadDirVerb)

    def test_gets_correct_verb_with_prepopsition_dobj_only(self):
        tokens = self._insert_dobj_into_phrase(
            jumpOverVerb.syntax[0], ["tall", "mountain"]
        )

        expected_verb_tokens = jumpOverVerb.syntax[0]

        gcv = getCurVerb(self.app, tokens)
        found_verbs = gcv[1]
        verb = gcv[0][0]
        verb_tokens = gcv[0][1]

        self.assertTrue(found_verbs)
        self.assertEqual(verb_tokens, expected_verb_tokens)
        self.assertIs(verb, jumpOverVerb)

    def test_gets_correct_verb_with_preposition_dobj_and_iobj(self):
        tokens = self._insert_objects_into_phrase(
            setOnVerb.syntax[0], ["yellow", "fish"], ["red", "shelf"]
        )

        expected_verb_tokens = setOnVerb.syntax[0]

        gcv = getCurVerb(self.app, tokens)
        found_verbs = gcv[1]
        verb = gcv[0][0]
        verb_tokens = gcv[0][1]

        self.assertTrue(found_verbs)
        self.assertEqual(verb_tokens, expected_verb_tokens)
        self.assertIs(verb, setOnVerb)


class TestGetGrammarObj(IFPTestCase):
    def test_gets_correct_dobj(self):
        expected_dobj = ["marvelous", "object"]

        tokens = self._insert_dobj_into_phrase(getVerb.syntax[0], expected_dobj)
        ggo = getGrammarObj(self.me, self.app, getVerb, tokens, getVerb.syntax[0])

        self.assertTrue(ggo)
        (dobj, iobj) = ggo

        self.assertEqual(dobj, expected_dobj)

    def test_gets_correct_objects_with_preposition(self):
        expected_dobj = ["marvelous", "object"]
        expected_iobj = ["wonderful", "item"]

        tokens = self._insert_objects_into_phrase(
            setOnVerb.syntax[0], expected_dobj, expected_iobj
        )
        ggo = getGrammarObj(self.me, self.app, setOnVerb, tokens, setOnVerb.syntax[0])

        self.assertTrue(ggo)
        (dobj, iobj) = ggo

        self.assertEqual(dobj, expected_dobj)
        self.assertEqual(iobj, expected_iobj)

    def test_gets_correct_objects_with_adjacent_dobj_iobj(self):
        dobj_item = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj_item)
        iobj_item = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj_item)

        expected_dobj = [dobj_item.name]
        expected_iobj = [iobj_item.name]

        tokens = self._insert_objects_into_phrase(
            giveVerb.syntax[1], expected_dobj, expected_iobj
        )
        ggo = getGrammarObj(self.me, self.app, giveVerb, tokens, giveVerb.syntax[1])

        self.assertTrue(ggo)
        (dobj, iobj) = ggo

        self.assertEqual(dobj, expected_dobj)
        self.assertEqual(iobj, expected_iobj)

    def test_gets_string_object(self):
        dobj_item = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj_item)

        expected_dobj = [dobj_item.name]
        expected_iobj = ["west"]

        tokens = self._insert_objects_into_phrase(
            leadDirVerb.syntax[0], expected_dobj, expected_iobj
        )
        ggo = getGrammarObj(
            self.me, self.app, leadDirVerb, tokens, leadDirVerb.syntax[0]
        )

        self.assertTrue(ggo)
        (dobj, iobj) = ggo

        self.assertEqual(dobj, expected_dobj)
        self.assertEqual(iobj, expected_iobj)


class TestCallVerb(IFPTestCase):
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

        matched_item1 = getThing(self.me, self.app, [noun], "room", None, None)
        self.assertIs(
            matched_item1, item1, "Failed to match item from unambiguous noun"
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

    def test_call_verb_with_no_objects(self):
        obj_words = [None, None]

        success = callVerb(self.me, self.app, lookVerb, obj_words)
        self.assertTrue(success)

    def test_call_verb_with_dobj(self):
        dobj_item = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj_item)

        dobj = [dobj_item.name]

        obj_words = [dobj, None]

        success = callVerb(self.me, self.app, examineVerb, obj_words)
        self.assertTrue(success)

    def test_call_verb_with_dobj_and_iobj(self):
        dobj_item = Thing(self._get_unique_noun())
        self.start_room.addThing(dobj_item)
        iobj_item = Surface(self._get_unique_noun(), self.me)
        self.start_room.addThing(iobj_item)

        dobj = [dobj_item.name]
        iobj = [iobj_item.name]

        obj_words = [dobj, iobj]

        success = callVerb(self.me, self.app, setOnVerb, obj_words)
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()

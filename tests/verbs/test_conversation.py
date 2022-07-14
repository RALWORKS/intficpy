import unittest

from ..helpers import IFPTestCase
from intficpy.actor import Actor, Topic, SpecialTopic
from intficpy.thing_base import Thing
from intficpy.verb import AskVerb, TellVerb, GiveVerb, ShowVerb
from intficpy.room import Room


class TestLeadDirection(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.actor1 = Actor(self.game, "grocer")
        self.actor1.can_be_led = True
        self.start_room.addThing(self.actor1)
        self.room2 = Room(self.game, "Place", "Words")
        self.start_room.north = self.room2

    def test_can_lead_actor(self):
        self.game.turnMain("lead grocer n")
        self.assertIs(self.me.location, self.room2)
        self.assertIs(self.actor1.location, self.room2)

    def test_cannot_lead_actor_invalid_direction(self):
        FAKE = "reft"
        self.game.turnMain(f"lead grocer {FAKE}")
        self.assertIn(f"I understood as far as", self.app.print_stack.pop())
        self.assertIs(self.me.location, self.start_room)
        self.assertIs(self.actor1.location, self.start_room)


class TestGetImpTalkToNobodyNear(IFPTestCase):
    def test_get_implicit(self):
        self.game.turnMain("hi")
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg, "There's no one obvious here to talk to. ",
        )


class TestGetImpTalkToAmbiguous(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.actor1 = Actor(self.game, "grocer")
        self.actor2 = Actor(self.game, "patron")
        self.start_room.addThing(self.actor1)
        self.start_room.addThing(self.actor2)

    def test_get_implicit(self):
        self.game.turnMain("hi")
        msg = self.app.print_stack.pop()
        self.assertIn("Would you like to talk to ", msg)

    def test_get_implicit_with_lastTurn_dobj(self):
        self.game.turnMain(f"hi {self.actor1.verbose_name}")
        self.game.turnMain("hi")
        self.assertIs(self.game.parser.previous_command.dobj.target, self.actor1)


class TestGetImpTalkToUnambiguous(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.actor1 = Actor(self.game, "grocer")
        self.start_room.addThing(self.actor1)

    def test_get_implicit(self):
        self.game.turnMain("hi")
        self.assertIs(self.game.parser.previous_command.dobj.target, self.actor1)


class TestSpecialTopic(IFPTestCase):
    def setUp(self):
        super().setUp()

        self.actor = Actor(self.game, "shepherd")
        self.actor.moveTo(self.start_room)

        self.verb_keyword = "ask"
        self.subject_phrase = "how come"
        suggestion = " ".join([self.verb_keyword, self.subject_phrase])

        self.text = "He shakes his head sadly."

        topic = SpecialTopic(self.game, suggestion, self.text)
        self.actor.addSpecialTopic(topic)

        self.game.turnMain("hi")

    def test_take_conversation_suggestion_with_verb_keyword(self):
        self.game.turnMain(self.verb_keyword)
        self.assertIn(self.text, self.app.print_stack)

    def test_take_conversation_suggestion_without_verb_keyword(self):
        self.game.turnMain(self.subject_phrase)
        self.assertIn(self.text, self.app.print_stack)


class TestTalkTo(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.actor = Actor(self.game, "girl")
        self.actor.moveTo(self.start_room)

    def test_talk_to_non_actor_thing(self):
        item = Thing(self.game, "bit")
        item.moveTo(self.start_room)
        self.game.turnMain("talk to bit")
        self.assertIn("cannot talk to", self.app.print_stack.pop())

    def test_talk_to_actor_with_sticky_topic(self):
        self.actor.sticky_topic = Topic(
            self.game, "Weren't you that guy from yesterday?"
        )
        self.game.turnMain("hi girl")
        self.assertIn(self.actor.sticky_topic.text, self.app.print_stack)

    def test_talk_to_actor_with_hermit_topic(self):
        self.actor.hermit_topic = Topic(self.game, "Go away.")
        self.game.turnMain("hi girl")
        self.assertIn(self.actor.hermit_topic.text, self.app.print_stack)

    def test_talk_to_actor_with_hi_topic(self):
        self.actor.hi_topic = Topic(self.game, "Oh. Hi.")
        self.game.turnMain("hi girl")
        self.assertIn(self.actor.hi_topic.text, self.app.print_stack)

    def test_talk_to_actor_with_returning_hi_topic(self):
        self.actor.return_hi_topic = Topic(self.game, "You're back. Great.")
        self.game.turnMain("hi girl")
        self.assertIn(self.actor.return_hi_topic.text, self.app.print_stack)


class TestAskAbout(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.actor = Actor(self.game, "girl")
        self.actor.moveTo(self.start_room)
        self.item = Thing(self.game, "mess")
        self.item.moveTo(self.start_room)
        self.CANNOT_TALK_MSG = "You cannot talk to that. "
        self.topic = Topic(self.game, '"Ah, yes," says the girl mysteriously. ')
        self.sticky_topic = Topic(
            self.game, '"But remember about the thing!" insists the girl. '
        )
        self.game.turnMain("l")

    def test_ask_with_topic(self):
        self.actor.addTopic("ask", self.topic, self.item)

        self.game.turnMain("ask girl about mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_ask_with_topic_and_sticky_topic(self):
        self.actor.addTopic("ask", self.topic, self.item)
        self.actor.sticky_topic = self.sticky_topic

        self.game.turnMain("ask girl about mess")
        msg2 = self.app.print_stack.pop()
        msg1 = self.app.print_stack.pop()

        self.assertEqual(
            msg1,
            self.topic.text,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg1}",
        )
        self.assertEqual(
            msg2,
            self.sticky_topic.text,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg2}",
        )

    def test_ask_actor_about_themselves(self):
        self.actor.addTopic("ask", self.topic, self.actor)

        self.game.turnMain("ask girl about herself")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_ask_no_defined_topic(self):
        self.assertNotIn(
            self.item.ix, self.actor.ask_topics,
        )

        self.game.turnMain("ask girl about mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.actor.default_topic,
            "Tried ask verb for topic not in ask topics. Expected default topic "
            f"{self.actor.default_topic}, received {msg}",
        )

    def test_ask_with_no_defined_topic_and_sticky_topic(self):
        self.actor.sticky_topic = self.sticky_topic

        self.game.turnMain("ask girl about mess")
        msg2 = self.app.print_stack.pop()
        msg1 = self.app.print_stack.pop()

        self.assertEqual(
            msg1,
            self.actor.default_topic,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg1}",
        )
        self.assertEqual(
            msg2,
            self.sticky_topic.text,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg2}",
        )

    def test_ask_inanimate(self):
        self.game.turnMain("ask mess about girl")
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )

    def test_ask_with_hermit_topic(self):
        self.actor.hermit_topic = self.topic

        self.assertNotIn(
            self.item.ix, self.actor.ask_topics,
        )  # make sure this topic isn't triggered because it was added for the item

        self.game.turnMain("ask girl about mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_ask_with_hi_topic(self):
        self.actor.hi_topic = self.topic

        self.assertNotIn(
            self.item.ix, self.actor.ask_topics,
        )  # make sure this topic isn't triggered because it was added for the item

        self.game.turnMain("ask girl about mess")
        msg = self.app.print_stack.pop(-2)  # last response will be default_topic3

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )


class TestTellAbout(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.actor = Actor(self.game, "girl")
        self.actor.moveTo(self.start_room)
        self.item = Thing(self.game, "mess")
        self.item.moveTo(self.start_room)
        self.CANNOT_TALK_MSG = "You cannot talk to that. "
        self.topic = Topic(self.game, '"Ah, yes," says the girl mysteriously. ')
        self.sticky_topic = Topic(
            self.game, '"But remember about the thing!" insists the girl. '
        )
        self.game.turnMain("l")

    def test_tell_with_topic(self):
        self.actor.addTopic("tell", self.topic, self.item)

        self.game.turnMain("tell girl about mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried tell verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_tell_with_topic_and_sticky_topic(self):
        self.actor.addTopic("tell", self.topic, self.item)
        self.actor.sticky_topic = self.sticky_topic

        self.game.turnMain("tell girl about mess")
        msg2 = self.app.print_stack.pop()
        msg1 = self.app.print_stack.pop()

        self.assertEqual(
            msg1,
            self.topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg1}",
        )
        self.assertEqual(
            msg2,
            self.sticky_topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg2}",
        )

    def test_tell_actor_about_themselves(self):
        self.actor.addTopic("tell", self.topic, self.actor)

        self.game.turnMain("tell girl about herself")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg}",
        )

    def test_tell_no_defined_topic(self):
        self.assertNotIn(
            self.item.ix, self.actor.tell_topics,
        )

        self.game.turnMain("tell girl about mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.actor.default_topic,
            "Tried tell verb for topic not in tell topics. Expected default topic "
            f"{self.actor.default_topic}, received {msg}",
        )

    def test_tell_with_no_defined_topic_and_sticky_topic(self):
        self.actor.sticky_topic = self.sticky_topic

        self.game.turnMain("tell girl about mess")
        msg2 = self.app.print_stack.pop()
        msg1 = self.app.print_stack.pop()

        self.assertEqual(
            msg1,
            self.actor.default_topic,
            "Expected topic text " f"{self.topic.text}, received {msg1}",
        )
        self.assertEqual(
            msg2,
            self.sticky_topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg2}",
        )

    def test_tell_with_hermit_topic(self):
        self.actor.hermit_topic = self.topic

        self.assertNotIn(
            self.item.ix, self.actor.tell_topics,
        )  # make sure this topic isn't triggered because it was added for the item

        self.game.turnMain("tell girl about mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg}",
        )

    def test_tell_with_hi_topic(self):
        self.actor.hi_topic = self.topic

        self.assertNotIn(
            self.item.ix, self.actor.tell_topics,
        )  # make sure this topic isn't triggered because it was added for the item

        self.game.turnMain("tell girl about mess")
        msg = self.app.print_stack.pop(-2)  # last response will be default_topic3

        self.assertEqual(
            msg,
            self.topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg}",
        )

    def test_tell_inanimate(self):
        self.game.turnMain("tell mess about girl")
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )


class TestGive(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.actor = Actor(self.game, "girl")
        self.actor.moveTo(self.start_room)
        self.item = Thing(self.game, "mess")
        self.item.invItem = True
        self.item.moveTo(self.start_room)
        self.CANNOT_TALK_MSG = "You cannot talk to that. "
        self.topic = Topic(self.game, '"Ah, yes," says the girl mysteriously. ')
        self.sticky_topic = Topic(
            self.game, '"But remember about the thing!" insists the girl. '
        )
        self.game.turnMain("l")

    def test_give_no_defined_topic(self):
        default = self.actor.default_topic

        self.assertNotIn(
            self.item.ix, self.actor.give_topics,
        )

        GiveVerb()._runVerbFuncAndEvents(self.game, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            default,
            "Tried give verb for topic not in give topics. Expected default topic "
            f"{default}, received {msg}",
        )

    def test_give_with_topic_and_sticky_topic(self):
        self.actor.addTopic("give", self.topic, self.item)
        self.actor.sticky_topic = self.sticky_topic

        self.game.turnMain("give girl mess")
        msg2 = self.app.print_stack.pop()
        msg1 = self.app.print_stack.pop()

        self.assertEqual(
            msg1,
            self.topic.text,
            "Tried show verb for topic in show topics. Expected topic text "
            f"{self.topic.text}, received {msg1}",
        )
        self.assertEqual(
            msg2,
            self.sticky_topic.text,
            "Tried show verb for topic in show topics. Expected topic text "
            f"{self.topic.text}, received {msg2}",
        )

    def test_give_actor_you(self):
        self.game.turnMain("give girl me")
        msg = self.app.print_stack.pop()

        self.assertIn(
            "cannot give yourself away", msg,
        )

    def test_give_actor_person(self):
        self.game.turnMain("give girl to girl")
        msg = self.app.print_stack.pop()

        self.assertIn(
            "cannot take a person", msg,
        )

    def test_give_with_topic(self):
        self.actor.addTopic("give", self.topic, self.item)

        self.game.turnMain("give girl mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried give verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_give_with_topic_and_give_enabled(self):
        self.actor.addTopic("give", self.topic, self.item)
        self.item.give = True

        self.game.turnMain("give girl mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried give verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )
        self.assertTrue(self.actor.containsItem(self.item))

    def test_give_with_no_defined_topic_and_sticky_topic(self):
        self.actor.sticky_topic = self.sticky_topic

        self.game.turnMain("give girl mess")
        msg2 = self.app.print_stack.pop()
        msg1 = self.app.print_stack.pop()

        self.assertEqual(
            msg1,
            self.actor.default_topic,
            "Expected topic text " f"{self.topic.text}, received {msg1}",
        )
        self.assertEqual(
            msg2,
            self.sticky_topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg2}",
        )

    def test_give_with_hermit_topic(self):
        self.actor.hermit_topic = self.topic

        self.assertNotIn(
            self.item.ix, self.actor.give_topics,
        )  # make sure this topic isn't triggered because it was added for the item

        self.game.turnMain("give girl mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg}",
        )

    def test_give_with_hi_topic(self):
        self.actor.hi_topic = self.topic

        self.assertNotIn(
            self.item.ix, self.actor.give_topics,
        )  # make sure this topic isn't triggered because it was added for the item

        self.game.turnMain("give girl mess")
        msg = self.app.print_stack.pop(-2)  # last response will be default_topic3

        self.assertEqual(
            msg,
            self.topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg}",
        )

    def test_give_inanimate(self):
        GiveVerb()._runVerbFuncAndEvents(self.game, self.item, self.item)
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )


class TestShow(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.actor = Actor(self.game, "girl")
        self.actor.moveTo(self.start_room)
        self.item = Thing(self.game, "mess")
        self.item.invItem = True
        self.item.moveTo(self.start_room)
        self.CANNOT_TALK_MSG = "You cannot talk to that. "
        self.topic = Topic(self.game, '"Ah, yes," says the girl mysteriously. ')
        self.sticky_topic = Topic(
            self.game, '"But remember about the thing!" insists the girl. '
        )
        self.game.turnMain("l")

    def test_show_with_topic(self):
        self.actor.addTopic("show", self.topic, self.item)

        ShowVerb()._runVerbFuncAndEvents(self.game, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried show verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_show_with_topic_and_sticky_topic(self):
        self.actor.addTopic("show", self.topic, self.item)
        self.actor.sticky_topic = self.sticky_topic

        self.game.turnMain("show girl mess")
        msg2 = self.app.print_stack.pop()
        msg1 = self.app.print_stack.pop()

        self.assertEqual(
            msg1,
            self.topic.text,
            "Tried show verb for topic in show topics. Expected topic text "
            f"{self.topic.text}, received {msg1}",
        )
        self.assertEqual(
            msg2,
            self.sticky_topic.text,
            "Tried show verb for topic in show topics. Expected topic text "
            f"{self.topic.text}, received {msg2}",
        )

    @unittest.expectedFailure
    def test_show_actor_themselves(self):
        self.actor.addTopic("show", self.topic, self.actor)

        self.game.turnMain("show girl herself")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried show verb for topic in show topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_show_no_defined_topic(self):
        default = self.actor.default_topic

        self.assertNotIn(
            self.item.ix, self.actor.show_topics,
        )

        ShowVerb()._runVerbFuncAndEvents(self.game, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            default,
            "Tried show verb for topic not in show topics. Expected default topic "
            f"{default}, received {msg}",
        )

    def test_show_with_no_defined_topic_and_sticky_topic(self):
        self.actor.sticky_topic = self.sticky_topic

        self.game.turnMain("show girl mess")
        msg2 = self.app.print_stack.pop()
        msg1 = self.app.print_stack.pop()

        self.assertEqual(
            msg1,
            self.actor.default_topic,
            "Expected topic text " f"{self.topic.text}, received {msg1}",
        )
        self.assertEqual(
            msg2,
            self.sticky_topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg2}",
        )

    def test_show_with_hermit_topic(self):
        self.actor.hermit_topic = self.topic

        self.assertNotIn(
            self.item.ix, self.actor.show_topics,
        )  # make sure this topic isn't triggered because it was added for the item

        self.game.turnMain("show girl mess")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg}",
        )

    def test_show_with_hi_topic(self):
        self.actor.hi_topic = self.topic

        self.assertNotIn(
            self.item.ix, self.actor.show_topics,
        )  # make sure this topic isn't triggered because it was added for the item

        self.game.turnMain("show girl mess")
        msg = self.app.print_stack.pop(-2)  # last response will be default_topic3

        self.assertEqual(
            msg,
            self.topic.text,
            "Expected topic text " f"{self.topic.text}, received {msg}",
        )

    def test_show_inanimate(self):
        ShowVerb()._runVerbFuncAndEvents(self.game, self.item, self.item)
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )

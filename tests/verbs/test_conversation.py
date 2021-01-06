from ..helpers import IFPTestCase
from intficpy.actor import Actor, Topic, SpecialTopic
from intficpy.thing_base import Thing
from intficpy.verb import AskVerb, TellVerb, GiveVerb, ShowVerb


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


class TestConversationVerbs(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.item = Thing(self.game, "mess")
        self.actor = Actor(self.game, "Jenny")
        self.start_room.addThing(self.item)
        self.start_room.addThing(self.actor)
        self.CANNOT_TALK_MSG = "You cannot talk to that. "
        self.topic = Topic(self.game, '"Ah, yes," says Jenny mysteriously. ')

    def test_ask_inanimate(self):
        AskVerb()._runVerbFuncAndEvents(self.game, self.item, self.actor)
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )

    def test_tell_inanimate(self):
        TellVerb()._runVerbFuncAndEvents(self.game, self.item, self.actor)
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
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

    def test_show_inanimate(self):
        ShowVerb()._runVerbFuncAndEvents(self.game, self.item, self.item)
        msg = self.app.print_stack.pop()
        self.assertEqual(
            msg,
            self.CANNOT_TALK_MSG,
            "Tried ask verb with an inanimate dobj. Expected msg "
            f"{self.CANNOT_TALK_MSG}, received {msg}",
        )

    def test_ask_no_defined_topic(self):
        self.actor.defaultTopic(self.game)
        self.game.runTurnEvents()
        default = self.app.print_stack.pop()

        self.assertNotIn(
            self.item.ix, self.actor.ask_topics,
        )

        AskVerb()._runVerbFuncAndEvents(self.game, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            default,
            "Tried ask verb for topic not in ask topics. Expected default topic "
            f"{default}, received {msg}",
        )

    def test_tell_no_defined_topic(self):
        self.actor.defaultTopic(self.game)
        self.game.runTurnEvents()
        default = self.app.print_stack.pop()

        self.assertNotIn(
            self.item.ix, self.actor.tell_topics,
        )

        TellVerb()._runVerbFuncAndEvents(self.game, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            default,
            "Tried tell verb for topic not in tell topics. Expected default topic "
            f"{default}, received {msg}",
        )

    def test_give_no_defined_topic(self):
        self.actor.defaultTopic(self.game)
        self.game.runTurnEvents()
        default = self.app.print_stack.pop()

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

    def test_show_no_defined_topic(self):
        self.actor.defaultTopic(self.game)
        self.game.runTurnEvents()
        default = self.app.print_stack.pop()

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

    def test_ask_with_topic(self):
        self.actor.addTopic("ask", self.topic, self.item)

        AskVerb()._runVerbFuncAndEvents(self.game, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried ask verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_tell_with_topic(self):
        self.actor.addTopic("tell", self.topic, self.item)

        TellVerb()._runVerbFuncAndEvents(self.game, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried tell verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

    def test_give_with_topic(self):
        self.actor.addTopic("give", self.topic, self.item)

        GiveVerb()._runVerbFuncAndEvents(self.game, self.actor, self.item)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.topic.text,
            "Tried give verb for topic in ask topics. Expected topic text "
            f"{self.topic.text}, received {msg}",
        )

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

from ..helpers import IFPTestCase


class TestHelpVerb(IFPTestCase):
    def test_help_prints_help_msg(self):
        self.game.turnMain("help")

        self.assertIn("Type INSTRUCTIONS", self.app.print_stack.pop())

    def test_instructions_prints_instructions(self):
        self.game.turnMain("instructions")

        self.assertIn(self.game.aboutGame.basic_instructions, self.app.print_stack)


class TestScoreVerb(IFPTestCase):
    def test_help_prints_current_score(self):
        self.game.turnMain("score")

        self.assertIn("0 points", self.app.print_stack.pop())


class TestFullScoreVerb(IFPTestCase):
    def test_help_prints_current_score(self):
        self.game.turnMain("fullscore")

        self.assertIn("You haven't scored any points", self.app.print_stack.pop())


class TestVerbsVerb(IFPTestCase):
    def test_verbs_verb_prints_verbs(self):
        self.game.turnMain("verbs")

        self.assertIn("For help with phrasing", self.app.print_stack.pop())
        # for now, make sure we are printing *some* verbs at least
        self.assertIn("set on", self.app.print_stack.pop())
        self.assertIn("accepts the following basic verbs", self.app.print_stack.pop())


class TestVerbHelpVerb(IFPTestCase):
    def test_verb_help_ask_verb(self):
        self.game.turnMain("verb help ask")
        self.assertIn("ask (person) about (thing)", self.app.print_stack.pop())

    def test_verb_help_go_verb(self):
        self.game.turnMain("verb help go")
        self.assertIn("go (direction)", self.app.print_stack.pop())

    def test_verb_help_lead_verb(self):
        self.game.turnMain("verb help lead")
        self.assertIn("lead (person) (direction)", self.app.print_stack.pop())

    def test_verb_help_nonexistent_verb(self):
        self.game.turnMain("verb help nevernevernevernevernononono")
        self.assertIn("I found no verb corresponding to", self.app.print_stack.pop())

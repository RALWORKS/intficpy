from intficpy.score import HintNode, Hint

from ..helpers import IFPTestCase


class TestHintVerb(IFPTestCase):
    def test_hint_call_with_no_hint_gives_no_hint_message(self):
        self.game.turnMain("hint")
        self.assertIn("no hints currently available", self.app.print_stack.pop())

    def test_hint_call_with_available_hints_gives_next_hint(self):
        HINT_TEXT = "Try this!"
        hint = Hint(self.game, HINT_TEXT)
        node = HintNode(self.game, [hint])
        self.game.hints.setNode(self.game, node)
        self.game.turnMain("hint")
        self.assertIn("1/1", self.app.print_stack.pop())
        self.assertIn(HINT_TEXT, self.app.print_stack.pop())

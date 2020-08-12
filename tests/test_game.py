from .helpers import IFPTestCase


class TestAddText(IFPTestCase):
    def test_add_text_with_no_turn_raises(self):
        del self.game.next_events["turn"]
        with self.assertRaises(KeyError):
            self.game.addText("Geraldine smiles.")

    def test_add_text(self):
        text = "Geraldine smiles."
        self.game.addText(text)
        self.assertIn(text, self.game.next_events["turn"].text)

        self.game.turnMain("l")

        self.assertIn(text, self.app.print_stack)

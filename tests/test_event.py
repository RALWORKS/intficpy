from .helpers import IFPTestCase


class TestNestedEvents(IFPTestCase):
    def test_nested_events_text_prints_in_order(self):
        FIRST = "first"
        SECOND = "second"
        THIRD = "third"

        self.game.addSubEvent("turn", "implicit")
        self.game.addText(THIRD)
        self.game.addTextToEvent("implicit", FIRST)
        self.game.addTextToEvent("implicit", SECOND)

        self.game.runTurnEvents()
        self.assertEqual(self.app.print_stack.pop(), THIRD)
        self.assertEqual(self.app.print_stack.pop(), SECOND)
        self.assertEqual(self.app.print_stack.pop(), FIRST)

    def test_text_property(self):
        self.assertFalse(self.game.next_events["turn"].text)

        self.game.addSubEvent("turn", "implicit")
        self.assertFalse(self.game.next_events["turn"].text)

        self.game.addTextToEvent("implicit", "text")
        self.assertEqual(len(self.game.next_events["turn"].text), 1)

        self.game.addText("more text")
        self.assertEqual(len(self.game.next_events["turn"].text), 2)

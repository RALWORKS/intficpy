from ..helpers import IFPTestCase

from intficpy.thing_base import Thing


class TestDoff(IFPTestCase):
    def test_doff_player_not_wearing_gives_player_not_wearing_message(self):
        item = Thing(self.game, "item")
        item.moveTo(self.start_room)
        self.game.turnMain("doff item")
        self.assertIn("aren't wearing", self.app.print_stack.pop(), "Did not receive expected 'not wearing' scope message")
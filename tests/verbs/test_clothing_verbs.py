from ..helpers import IFPTestCase

from intficpy.things import Thing, Clothing


class TestDoff(IFPTestCase):
    def test_doff_player_not_wearing_gives_player_not_wearing_message(self):
        item = Thing(self.game, "item")
        item.moveTo(self.start_room)
        self.game.turnMain("doff item")
        self.assertIn(
            "aren't wearing",
            self.app.print_stack.pop(),
            "Did not receive expected 'not wearing' scope message",
        )

    def test_doff_player_wearing_doffs_item(self):
        item = Clothing(self.game, "item")
        self.me.wearing[item.ix] = [item]
        self.game.turnMain("doff item")
        self.assertIn("You take off", self.app.print_stack.pop())
        self.assertItemNotIn(item, self.me.wearing, "Item not removed from wearing")
        self.assertItemIn(item, self.me.contains, "Item not added to main inv")

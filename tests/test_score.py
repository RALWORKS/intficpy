from .helpers import IFPTestCase

from intficpy.score import Achievement, Ending, Hint, HintNode
from intficpy.things import Thing


class TestAchevement(IFPTestCase):
    def test_award_achievement(self):
        ach = Achievement(self.game, 3, "getting the disc")
        item = Thing(self.game, "disc")
        item.moveTo(self.start_room)
        item.getVerbDobj = lambda x: ach.award(self.game)

        self.assertEqual(self.game.score.total, 0)

        self.game.turnMain("take disc")

        self.assertEqual(self.game.score.total, 3)
        self.game.turnMain("score")
        self.game.turnMain("fullscore")


class TestEnding(IFPTestCase):
    def test_end_game(self):
        end = Ending(self.game, True, "Won!", "You won!")

        item = Thing(self.game, "disc")
        item.moveTo(self.start_room)
        item.getVerbDobj = lambda x: end.endGame(self.game)

        self.assertFalse(self.game.ended)

        self.game.turnMain("take disc")

        self.assertTrue(self.game.ended)

        self.game.turnMain("drop disc")

        self.assertIn("The game has ended", self.app.print_stack.pop())

        self.game.turnMain("score")
        self.assertNotIn("The game has ended", self.app.print_stack.pop())

        self.game.turnMain("fullscore")
        self.assertNotIn("The game has ended", self.app.print_stack.pop())

        self.game.turnMain("full score")
        self.assertNotIn("The game has ended", self.app.print_stack.pop())

        self.game.turnMain("about")
        self.assertNotIn("The game has ended", self.app.print_stack.pop())


class TestHints(IFPTestCase):
    def setUp(self):
        super().setUp()

        self.ach = Achievement(self.game, 3, "escaping the room")

        hint1 = Hint(self.game, "Hmm. How can I get out of here?", self.ach, 1)
        hint2 = Hint(self.game, "Exit through the door", self.ach, 1)
        self.node = HintNode(self.game, [hint1, hint2])

    def test_get_hint(self):
        self.game.hints.setNode(self.game, self.node)

        ACH_REWARD = self.ach.points

        self.game.turnMain("hint")

        self.assertEqual(self.ach.points, ACH_REWARD - 1)

        self.game.turnMain("hint")

        self.assertEqual(self.ach.points, ACH_REWARD - 2)

        self.game.hints.closeNode(self.game, self.node)

    def test_pending_hint(self):
        self.game.hints.addPending(self.game, self.node)

        self.game.turnMain("hint")

        self.assertIn("no hint", self.app.print_stack.pop())
        self.game.turnMain("hint")
        self.assertIn("Exit through", self.app.print_stack[-2])

    def test_required_incomplete(self):
        hint3 = Hint(self.game, "Eagles in the roof")
        node2 = HintNode(self.game, [hint3])
        node2.open_require_nodes_incomplete = [self.node]

        self.node.complete = True
        self.game.hints.addPending(self.game, node2)

        self.assertIn(node2, self.game.hints.pending)

        self.game.turnMain("hint")
        self.assertIn("no hint", self.app.print_stack.pop())

        self.assertNotIn(node2, self.game.hints.pending)

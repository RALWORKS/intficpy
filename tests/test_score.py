from .helpers import IFPTestCase

from intficpy.score import Achievement, Ending
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

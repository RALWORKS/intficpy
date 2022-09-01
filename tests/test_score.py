from .helpers import IFPTestCase

from intficpy.score import Achievement
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

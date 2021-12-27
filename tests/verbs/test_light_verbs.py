from ..helpers import IFPTestCase

from intficpy.things import LightSource


class TestLightVerb(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.source = LightSource(self.game, "lamp")
        self.source.moveTo(self.me)
        self.start_room.dark = True
        self.start_room.desc = "A spooky forest"

    def test_lighting_source_allows_player_to_see(self):
        self.game.turnMain("look")
        self.assertNotIn(self.start_room.desc, self.app.print_stack)
        self.assertIn("dark", self.app.print_stack.pop())
        self.game.turnMain("light lamp")
        self.assertIn("You light the lamp. ", self.app.print_stack)
        self.game.turnMain("look")
        self.assertIn(self.start_room.desc, self.app.print_stack)

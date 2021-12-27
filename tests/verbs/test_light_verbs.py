from ..helpers import IFPTestCase

from intficpy.things import LightSource, Thing


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

    def test_player_cannot_light_source_if_player_lighting_disabled(self):
        self.source.player_can_light = False
        self.game.turnMain("look")
        self.assertNotIn(self.start_room.desc, self.app.print_stack)
        self.assertIn("dark", self.app.print_stack.pop())
        self.game.turnMain("light lamp")
        self.assertIn(self.source.cannot_light_msg, self.app.print_stack)
        self.game.turnMain("look")
        self.assertNotIn(self.start_room.desc, self.app.print_stack)

    def test_player_cannot_light_non_light_source(self):
        item = Thing(self.game, "ball")
        item.moveTo(self.me)
        self.game.turnMain("look")
        self.assertNotIn(self.start_room.desc, self.app.print_stack)
        self.assertIn("dark", self.app.print_stack.pop())
        self.game.turnMain("light ball")
        self.assertIn("not a light source", self.app.print_stack.pop())
        self.game.turnMain("look")
        self.assertNotIn(self.start_room.desc, self.app.print_stack)


class TestExtinguishVerb(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.source = LightSource(self.game, "lamp")
        self.source.moveTo(self.me)
        self.source.light(self.game)
        self.start_room.dark = True
        self.start_room.desc = "A spooky forest"

    def test_extinguishing_source_removes_light(self):
        self.game.turnMain("look")
        self.assertIn(self.start_room.desc, self.app.print_stack)
        self.game.turnMain("put out lamp")
        self.assertIn(self.source.extinguish_msg, self.app.print_stack)
        self.app.print_stack = []
        self.game.turnMain("look")
        self.assertIn("dark", self.app.print_stack.pop())
        self.assertNotIn(self.start_room.desc, self.app.print_stack)

    def test_player_cannot_light_source_if_player_extinguishing_disabled(self):
        self.source.player_can_extinguish = False
        self.game.turnMain("look")
        self.assertIn(self.start_room.desc, self.app.print_stack)
        self.game.turnMain("put out lamp")
        self.assertIn(self.source.cannot_extinguish_msg, self.app.print_stack)
        self.app.print_stack = []
        self.game.turnMain("look")
        self.assertIn(self.start_room.desc, self.app.print_stack)

    def test_player_cannot_extinguish_non_light_source(self):
        item = Thing(self.game, "ball")
        item.moveTo(self.me)
        self.game.turnMain("put out ball")
        self.assertIn("not a light source", self.app.print_stack.pop())

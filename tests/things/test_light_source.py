from ..helpers import IFPTestCase
from intficpy.things import LightSource, Thing


class TestDarkness(IFPTestCase):
    def setUp(self):
        super().setUp()

        self.start_room.dark = True
        self.item = Thing(self.game, "item")
        self.start_room.addThing(self.item)

        self.light = LightSource(self.game, "light")

    def test_can_see_items_if_room_is_not_dark(self):
        self.start_room.dark = False

        self.game.turnMain("l")
        desc = self.app.print_stack.pop()

        self.assertIn(self.item.verbose_name, desc)

    def test_cannot_see_items_if_room_is_dark(self):
        self.game.turnMain("l")
        desc = self.app.print_stack.pop()

        self.assertNotIn(self.item.verbose_name, desc)

    def test_cannot_see_items_if_room_is_dark_and_light_not_lit(self):
        self.start_room.addThing(self.light)
        self.assertFalse(self.light.is_lit)

        self.game.turnMain("l")
        desc = self.app.print_stack.pop()

        self.assertNotIn(self.item.verbose_name, desc)

    def test_can_see_items_if_room_is_dark_and_light_is_lit(self):
        self.start_room.addThing(self.light)
        self.light.light(self.game)
        self.assertTrue(self.light.is_lit)
        self.assertFalse(self.start_room.describeDark(self.game))

        self.game.turnMain("l")
        desc = self.app.print_stack.pop()

        self.assertIn(self.item.verbose_name, desc)


class TestLightSource(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.light = LightSource(self.game, "light")

    def test_is_lit_state_desc_show_in_desc_when_light_is_lit(self):
        self.light.light(self.game)
        self.assertIn(self.light.lit_desc, self.light.desc)

    def test_is_lit_state_desc_show_in_desc_when_light_is_not_lit(self):
        self.light.light(self.game)
        self.light.extinguish(self.game)
        self.assertIn(self.light.not_lit_desc, self.light.desc)

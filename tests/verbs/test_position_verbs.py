from tests.helpers import IFPTestCase

from intficpy.things import Container


LYING = "lying"
SITTING = "sitting"


class TestLieDownVerb(IFPTestCase):
    def test_cannot_lie_down_if_already_lying_down(self):
        self.me.position = LYING
        self.game.turnMain("lie down")
        response = self.app.print_stack[-1]
        self.assertIn("already lying down", response)

    def test_must_get_out_if_nested_location_does_not_allow_lying(self):
        inner_loc = Container(self.game, "box")
        inner_loc.moveTo(self.start_room)
        self.me.moveTo(inner_loc)
        self.assertFalse(inner_loc.can_contain_sitting_player)

        self.game.turnMain("lie down")
        first_getting_out = self.app.print_stack[-2]
        self.assertIn("climb out", first_getting_out)
        self.assertEqual(self.me.location, inner_loc.location)
        self.assertEqual(self.me.position, LYING)

    def test_deeply_nested_player(self):
        locs = [
            Container(self.game, "box0"),
            Container(self.game, "box1"),
            Container(self.game, "box2"),
            Container(self.game, "box3"),
        ]
        locs[0].moveTo(self.start_room)
        locs[1].moveTo(locs[0])
        locs[2].moveTo(locs[1])
        locs[3].moveTo(locs[2])
        self.me.moveTo(locs[3])

        for loc in locs:
            self.assertFalse(loc.can_contain_sitting_player)

        self.game.turnMain("lie down")
        action = self.app.print_stack.pop()
        self.assertIn("You lie down", action)

        for ix in range(len(locs)):
            implied = self.app.print_stack.pop()
            self.assertIn("climb out", implied, ix)

        self.assertEqual(self.me.location, self.start_room)
        self.assertEqual(self.me.position, LYING)

    def test_can_lie_down(self):
        self.assertNotEqual(self.me.position, LYING)
        self.game.turnMain("lie down")
        self.assertEqual(self.me.position, LYING)


class TestSitDownVerb(IFPTestCase):
    def test_cannot_sit_down_if_already_lying_down(self):
        self.me.position = SITTING
        self.game.turnMain("sit down")
        response = self.app.print_stack[-1]
        self.assertIn("already sitting", response)

    def test_must_get_out_if_nested_location_does_not_allow_sitting(self):
        inner_loc = Container(self.game, "box")
        inner_loc.moveTo(self.start_room)
        self.me.moveTo(inner_loc)
        self.assertFalse(inner_loc.can_contain_sitting_player)

        self.game.turnMain("sit down")
        first_getting_out = self.app.print_stack[-2]
        self.assertIn("climb out", first_getting_out)
        self.assertEqual(self.me.location, inner_loc.location)
        self.assertEqual(self.me.position, SITTING)

    def test_deeply_nested_player(self):
        locs = [
            Container(self.game, "box0"),
            Container(self.game, "box1"),
            Container(self.game, "box2"),
            Container(self.game, "box3"),
        ]
        locs[0].moveTo(self.start_room)
        locs[1].moveTo(locs[0])
        locs[2].moveTo(locs[1])
        locs[3].moveTo(locs[2])
        self.me.moveTo(locs[3])

        for loc in locs:
            self.assertFalse(loc.can_contain_sitting_player)

        self.game.turnMain("sit down")
        action = self.app.print_stack.pop()

        self.assertIn("You sit down", action)

        for ix in range(len(locs)):
            implied = self.app.print_stack.pop()
            self.assertIn("climb out", implied, ix)

        self.assertEqual(self.me.location, self.start_room)
        self.assertEqual(self.me.position, SITTING)

    def test_can_sit_down(self):
        self.assertNotEqual(self.me.position, SITTING)
        self.game.turnMain("sit down")
        self.assertEqual(self.me.position, SITTING)

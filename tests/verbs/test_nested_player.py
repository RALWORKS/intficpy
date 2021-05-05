from ..helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import (
    Surface,
    Container,
)


class TestPlayerGetOn(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.surface = Surface(self.game, "bench")
        self.start_room.addThing(self.surface)

    def test_climb_on_cannot_sit_stand_lie(self):
        FAILURE_MSG = f"You cannot climb on {self.surface.lowNameArticle(True)}. "

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_on_can_lie(self):
        SUCCESS_MSG = f"You lie on {self.surface.lowNameArticle(True)}. "

        self.surface.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_on_can_sit(self):
        SUCCESS_MSG = f"You sit on {self.surface.lowNameArticle(True)}. "

        self.surface.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_on_can_stand(self):
        SUCCESS_MSG = f"You stand on {self.surface.lowNameArticle(True)}. "

        self.surface.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.surface)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetOff(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.surface = Surface(self.game, "bench")
        self.surface.can_contain_standing_player = True
        self.start_room.addThing(self.surface)
        self.game.turnMain("climb on bench")
        self.assertIs(self.me.location, self.surface)

    def test_climb_down_from(self):
        SUCCESS_MSG = f"You climb down from {self.surface.lowNameArticle(True)}. "

        self.game.turnMain("climb down from bench")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_down(self):
        SUCCESS_MSG = f"You climb down from {self.surface.lowNameArticle(True)}. "

        self.game.turnMain("climb down")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetIn(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container(self.game, "box")
        self.start_room.addThing(self.container)

    def test_climb_in_cannot_sit_stand_lie(self):
        FAILURE_MSG = f"You cannot climb into {self.container.lowNameArticle(True)}. "

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_lie(self):
        SUCCESS_MSG = f"You lie in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_sit(self):
        SUCCESS_MSG = f"You sit in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_stand(self):
        SUCCESS_MSG = f"You stand in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetInOpenLid(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container(self.game, "box")
        self.container.has_lid = True
        self.container.is_open = True
        self.start_room.addThing(self.container)

    def test_climb_in_can_lie(self):
        SUCCESS_MSG = f"You lie in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_sit(self):
        SUCCESS_MSG = f"You sit in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_in_can_stand(self):
        SUCCESS_MSG = f"You stand in {self.container.lowNameArticle(True)}. "

        self.container.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)


class TestPlayerGetInClosedLid(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container(self.game, "box")
        self.container.has_lid = True
        self.container.is_open = False
        self.start_room.addThing(self.container)

    def test_climb_in_can_lie(self):
        FAILURE_MSG = (
            f"You cannot climb into {self.container.lowNameArticle(True)}, "
            "since it is closed. "
        )

        self.container.can_contain_lying_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_sit(self):
        FAILURE_MSG = (
            f"You cannot climb into {self.container.lowNameArticle(True)}, "
            "since it is closed. "
        )

        self.container.can_contain_sitting_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)

    def test_climb_in_can_stand(self):
        FAILURE_MSG = (
            f"You cannot climb into {self.container.lowNameArticle(True)}, "
            "since it is closed. "
        )

        self.container.can_contain_standing_player = True

        self.assertIs(
            self.me.location, self.start_room, "Player needs to start in start_room"
        )
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, FAILURE_MSG)


class TestPlayerGetOut(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.container = Container(self.game, "box")
        self.container.can_contain_standing_player = True
        self.start_room.addThing(self.container)
        self.game.turnMain("climb in box")
        self.assertIs(self.me.location, self.container)

    def test_climb_out_of(self):
        SUCCESS_MSG = f"You climb out of {self.container.lowNameArticle(True)}. "

        self.game.turnMain("climb out of box")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

    def test_climb_out(self):
        SUCCESS_MSG = f"You climb out of {self.container.lowNameArticle(True)}. "

        self.game.turnMain("climb out")
        self.assertIs(self.me.location, self.start_room)

        msg = self.app.print_stack.pop()
        self.assertEqual(msg, SUCCESS_MSG)

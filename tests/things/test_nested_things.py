from ..helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import Container, UnderSpace


class TestContainer(IFPTestCase):
    def test_reveal_contents(self):
        box = Container(self.app.game, "box")
        widget = Thing(self.app.game, "widget")
        widget.moveTo(box)
        sub_widget = Thing(self.app.game, "glitter")
        sub_widget.moveTo(widget)
        box.giveLid()
        box.makeClosed()
        box.moveTo(self.start_room)
        self.assertItemNotIn(
            widget, self.start_room.sub_contains, "Contents shown before reveal"
        )
        box.makeOpen()
        self.assertItemIn(
            widget, self.start_room.sub_contains, "Contents not shown after reveal"
        )
        self.assertItemIn(
            sub_widget,
            self.start_room.sub_contains,
            "Sub contents not shown after reveal",
        )


class TestUnderSpace(IFPTestCase):
    def test_reveal_contents(self):
        box = UnderSpace(self.app.game, "box")
        widget = Thing(self.app.game, "widget")
        widget.moveTo(box)
        sub_widget = Thing(self.app.game, "glitter")
        sub_widget.moveTo(widget)
        box.moveTo(self.start_room)
        box.revealed = False
        self.app.game.turnMain("l")
        self.app.game.turnMain("take widget")
        self.assertIn("don't see any widget", self.app.print_stack.pop())
        self.assertItemNotIn(
            widget, self.start_room.sub_contains, "Contents shown before reveal"
        )
        box.revealUnder()
        self.assertItemIn(
            widget, self.start_room.sub_contains, "Contents not shown after reveal"
        )
        self.assertItemIn(
            sub_widget,
            self.start_room.sub_contains,
            "Sub contents not shown after reveal",
        )

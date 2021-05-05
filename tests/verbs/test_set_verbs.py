from ..helpers import IFPTestCase

from intficpy.things import (
    Thing,
    Surface,
    Container,
    UnderSpace,
)


class TestSetVerbs(IFPTestCase):
    def test_set_in_adds_item(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        container = Container(self.game, self._get_unique_noun())
        self.start_room.addThing(container)

        self.assertNotIn(item.ix, container.contains)

        self.game.turnMain(f"set {item.verbose_name} in {container.verbose_name}")

        self.assertIn(item.ix, container.contains)
        self.assertIn(item, container.contains[item.ix])

    def test_set_on_adds_item(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        surface = Surface(self.game, self._get_unique_noun())
        self.start_room.addThing(surface)

        self.assertNotIn(item.ix, surface.contains)

        self.game.turnMain(f"set {item.verbose_name} on {surface.verbose_name}")

        self.assertIn(item.ix, surface.contains)
        self.assertIn(item, surface.contains[item.ix])

    def test_set_under_adds_item(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        underspace = UnderSpace(self.game, self._get_unique_noun())
        self.start_room.addThing(underspace)

        self.assertNotIn(item.ix, underspace.contains)

        self.game.turnMain(f"set {item.verbose_name} under {underspace.verbose_name}")

        self.assertIn(item.ix, underspace.contains)
        self.assertIn(item, underspace.contains[item.ix])

    def test_cannot_set_in_non_container(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self.game, self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        self.game.turnMain(f"set {item.verbose_name} in {invalid_iobj.verbose_name}")

        self.assertNotIn(item.ix, invalid_iobj.contains)

    def test_cannot_set_on_non_surface(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self.game, self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        self.game.turnMain(f"set {item.verbose_name} on {invalid_iobj.verbose_name}")

        self.assertNotIn(item.ix, invalid_iobj.contains)

    def test_cannot_set_under_non_underspace(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        invalid_iobj = Thing(self.game, self._get_unique_noun())
        self.start_room.addThing(invalid_iobj)

        self.assertNotIn(item.ix, invalid_iobj.contains)

        self.game.turnMain(f"set {item.verbose_name} under {invalid_iobj.verbose_name}")

        self.assertNotIn(item.ix, invalid_iobj.contains)

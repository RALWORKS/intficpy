from ..helpers import IFPTestCase

from intficpy.things import (
    Thing,
    Surface,
    Container,
    UnderSpace,
    Liquid,
)


class TestAddItemToItself(IFPTestCase):
    def test_set_surface_on_itself(self):
        item = Surface(self.game, "thing")
        item.moveTo(self.start_room)
        self.game.turnMain("set thing on thing")
        self.assertIn("You cannot", self.app.print_stack.pop())
        self.assertFalse(item.containsItem(item))

    def test_set_container_in_itself(self):
        item = Container(self.game, "thing")
        item.moveTo(self.start_room)
        self.game.turnMain("set thing in thing")
        self.assertIn("You cannot", self.app.print_stack.pop())
        self.assertFalse(item.containsItem(item))

    def test_set_underspace_under_itself(self):
        item = UnderSpace(self.game, "thing")
        item.moveTo(self.start_room)
        self.game.turnMain("set thing under thing")
        self.assertIn("You cannot", self.app.print_stack.pop())
        self.assertFalse(item.containsItem(item))


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

    def test_set_composite_child_in_gives_attached_message(self):
        parent = Thing(self.game, "thing")
        parent.moveTo(self.me)
        item = Thing(self.game, "handle")
        parent.addComposite(item)
        container = Container(self.game, "place")
        self.start_room.addThing(container)

        self.game.turnMain(f"set handle in place")

        self.assertIn("is attached to", self.app.print_stack.pop())
        self.assertIs(item.location, self.me)

    def test_set_in_gives_too_big_message_if_item_too_big(self):
        item = Thing(self.game, "giant")
        item.size = 100000
        self.me.addThing(item)
        place = Container(self.game, "place")
        self.start_room.addThing(place)

        self.game.turnMain(f"set giant in place")

        self.assertIn("too big", self.app.print_stack.pop())
        self.assertFalse(place.containsItem(item))

    def test_set_in_closed_container_implies_open_it_first(self):
        item = Thing(self.game, "item")
        self.me.addThing(item)
        place = Container(self.game, "place")
        place.giveLid()
        place.is_open = False
        self.start_room.addThing(place)

        self.game.turnMain(f"set item in place")

        self.assertIn("You set the item in the place", self.app.print_stack.pop())
        self.assertIn("You open the place", self.app.print_stack.pop())
        self.assertIn("(First trying to open", self.app.print_stack.pop())
        self.assertTrue(place.is_open)
        self.assertTrue(place.containsItem(item))

    def test_cannot_set_item_in_if_container_already_contains_liquid(self):
        item = Thing(self.game, "item")
        self.me.addThing(item)
        place = Container(self.game, "place")
        self.start_room.addThing(place)
        liquid = Liquid(self.game, "water", "water")
        liquid.moveTo(place)

        self.game.turnMain(f"set item in place")

        self.assertIn("already full of water", self.app.print_stack.pop())
        self.assertFalse(place.containsItem(item))

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

    def test_set_on_floor_add_item_to_outer_room(self):
        item = Thing(self.game, "thing")
        item.invItem = True
        item.moveTo(self.game.me)

        self.assertIsNot(item.location, self.start_room)

        self.game.turnMain(f"set thing on floor")

        self.assertIs(item.location, self.start_room)

    def test_set_composite_child_on_gives_attached_message(self):
        parent = Thing(self.game, "thing")
        parent.moveTo(self.me)
        item = Thing(self.game, "handle")
        parent.addComposite(item)
        surface = Surface(self.game, "place")
        self.start_room.addThing(surface)

        self.game.turnMain(f"set handle on place")

        self.assertIn("is attached to", self.app.print_stack.pop())
        self.assertIs(item.location, self.me)

    def test_set_composite_child_on_floor_gives_attached_message(self):
        parent = Thing(self.game, "thing")
        parent.moveTo(self.me)
        item = Thing(self.game, "handle")
        parent.addComposite(item)

        self.assertIsNot(item.location, self.start_room)

        self.game.turnMain(f"set handle on floor")

        self.assertIn("is attached to", self.app.print_stack.pop())
        self.assertIs(item.location, self.me)

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

    def test_set_under_gives_too_big_message_if_item_too_big(self):
        item = Thing(self.game, "giant")
        item.size = 100000
        self.me.addThing(item)
        place = UnderSpace(self.game, "place")
        self.start_room.addThing(place)

        self.game.turnMain(f"set giant under place")

        self.assertIn("too big", self.app.print_stack.pop())
        self.assertFalse(place.containsItem(item))

    def test_set_composite_child_under_gives_attached_message(self):
        parent = Thing(self.game, "thing")
        parent.moveTo(self.me)
        item = Thing(self.game, "handle")
        parent.addComposite(item)
        underspace = UnderSpace(self.game, "place")
        self.start_room.addThing(underspace)

        self.game.turnMain(f"set handle under place")

        self.assertIn("is attached to", self.app.print_stack.pop())
        self.assertIs(item.location, self.me)

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

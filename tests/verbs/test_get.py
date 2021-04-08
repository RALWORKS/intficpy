from ..helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import Surface, Container, Liquid, UnderSpace
from intficpy.verb import GetVerb


class TestGetVerb(IFPTestCase):
    def test_verb_func_adds_invitem_to_inv(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.start_room.addThing(item)

        success = GetVerb()._runVerbFuncAndEvents(self.game, item)
        self.assertTrue(success)

        self.assertIn(item.ix, self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

    def test_verb_func_does_not_add_to_inv_where_invitem_false(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = False
        self.start_room.addThing(item)

        self.assertFalse(item.ix in self.me.contains)

        success = GetVerb()._runVerbFuncAndEvents(self.game, item)
        self.assertFalse(success)

        self.assertNotIn(item.ix, self.me.contains)

    def test_verb_func_does_not_add_to_inv_where_already_in_inv(self):
        item = Thing(self.game, self._get_unique_noun())
        item.invItem = True
        self.me.addThing(item)
        self.assertTrue(item.ix in self.me.contains)
        self.assertEqual(len(self.me.contains[item.ix]), 1)
        self.assertIn(item, self.me.contains[item.ix])

        success = GetVerb()._runVerbFuncAndEvents(self.game, item)
        self.assertFalse(success)

        self.assertEqual(len(self.me.contains[item.ix]), 1)

    def test_get_item_when_pc_is_in_container(self):
        loc = Container(self.game, "box")
        loc.moveTo(self.start_room)
        loc.can_contain_standing_player = True

        sub_loc = Container(self.game, "vase")
        sub_loc.moveTo(loc)
        sub_loc.can_contain_standing_player = True

        self.game.me.moveTo(sub_loc)

        self.game.turnMain("take box")

        self.assertIn("You climb out of the box. ", self.app.print_stack)

    def test_get_item_when_pc_is_on_surface(self):
        loc = Surface(self.game, "desk")
        loc.moveTo(self.start_room)
        loc.can_contain_standing_player = True

        sub_loc = Surface(self.game, "box")
        sub_loc.moveTo(loc)
        sub_loc.can_contain_standing_player = True

        self.game.me.moveTo(sub_loc)

        self.game.turnMain("take desk")

        self.assertIn("You climb down from the desk. ", self.app.print_stack)

    def test_get_item_when_pc_is_in_thing_with_no_corresponding_exit_verb(self):
        loc = Thing(self.game, "brick")
        loc.moveTo(self.start_room)
        loc.can_contain_standing_player = True
        self.game.me.moveTo(loc)

        self.game.turnMain("take brick")

        self.assertIn("Could not move player out of brick", self.app.print_stack)

    def test_get_item_when_pc_sitting(self):
        item = Thing(self.game, "bob")
        item.moveTo(self.start_room)
        self.game.me.position = "sitting"

        self.game.turnMain("take bob")

        self.assertIn("You stand up. ", self.app.print_stack)
        self.assertEqual(self.game.me.position, "standing")

    def test_get_liquid_in_container_gets_container(self):
        container = Container(self.game, "cup")
        container.moveTo(self.start_room)
        item = Liquid(self.game, "broth", "broth")
        item.moveTo(container)

        self.game.turnMain("take broth")

        self.assertIn("You take the cup. ", self.app.print_stack)

    def test_get_thing_nested_in_thing_in_inventory(self):
        container = Container(self.game, "cup")
        container.moveTo(self.start_room)
        item = Thing(self.game, "bead")

        container.moveTo(self.game.me)
        item.moveTo(container)

        self.game.turnMain("look in cup")

        self.game.turnMain("take bead")

        self.assertIn("You remove the bead from the cup. ", self.app.print_stack)

    def test_get_explicitly_invitem_component_of_composite_object(self):
        parent = Thing(self.game, "cube")
        child = Thing(self.game, "knob")
        parent.addComposite(child)
        parent.moveTo(self.start_room)
        child.invItem = True

        self.game.turnMain("take knob")
        self.assertIn("The knob is attached to the cube. ", self.app.print_stack)

    def test_get_underspace_reveals_single_contained_item(self):
        parent = UnderSpace(self.game, "rug")
        child = Thing(self.game, "penny")
        parent.moveTo(self.start_room)
        child.moveTo(parent)

        self.game.turnMain("take rug")
        self.assertIn("A penny is revealed. ", self.app.print_stack)

    def test_get_underspace_reveals_multiple_contained_items(self):
        parent = UnderSpace(self.game, "rug")
        child = Thing(self.game, "penny")
        child2 = Thing(self.game, "rock")
        parent.moveTo(self.start_room)
        child.moveTo(parent)
        child2.moveTo(parent)

        self.game.turnMain("take rug")
        self.assertIn("are revealed", self.app.print_stack.pop())

    def test_get_composite_underspace_reveals_contained_item(self):
        item = Container(self.game, "box")
        parent = UnderSpace(self.game, "space")
        child = Thing(self.game, "penny")
        item.addComposite(parent)
        item.moveTo(self.start_room)
        child.moveTo(parent)

        self.game.turnMain("take box")
        self.assertIn("A penny is revealed. ", self.app.print_stack)

    def test_get_object_from_closed_container_in_inventory(self):
        box = Container(self.game, "box")
        box.giveLid()
        item = Thing(self.game, "bead")
        item.moveTo(box)
        box.makeOpen()
        box.moveTo(self.game.me)

        self.assertFalse(self.game.me.topLevelContainsItem(item))
        self.game.turnMain("look in box")
        self.assertIn("bead", self.app.print_stack.pop())
        self.game.turnMain("close box")
        self.assertFalse(box.is_open, "Failed to close box")
        self.game.turnMain("take bead")
        self.assertTrue(self.game.me.topLevelContainsItem(item))


class TestTakeAll(IFPTestCase):
    def test_take_all_takes_all_known_top_level_invitems(self):
        hat = Thing(self.game, "hat")
        hat.moveTo(self.start_room)
        cat = Thing(self.game, "cat")
        cat.moveTo(self.start_room)

        self.game.turnMain("l")
        self.game.turnMain("take all")

        self.assertTrue(self.game.me.containsItem(hat))
        self.assertTrue(self.game.me.containsItem(cat))

    def test_no_items_are_taken_unless_they_are_known(self):
        hat = Thing(self.game, "hat")
        hat.moveTo(self.start_room)
        cat = Thing(self.game, "cat")
        cat.moveTo(self.start_room)

        # self.game.turnMain("l") # we haven't looked, so we don't know
        self.game.turnMain("take all")

        self.assertFalse(self.game.me.containsItem(hat))
        self.assertFalse(self.game.me.containsItem(cat))

    def test_take_all_takes_known_objects_from_sub_locations(self):
        desk = Surface(self.game, "desk")
        desk.inv_item = False
        desk.desc_reveal = True
        desk.moveTo(self.start_room)
        hat = Thing(self.game, "hat")
        hat.moveTo(desk)

        self.game.turnMain("l")
        self.game.turnMain("take all")

        self.assertTrue(self.game.me.containsItem(hat))

    def test_take_all_does_not_take_items_that_are_not_discovered(self):
        desk = Surface(self.game, "desk")
        desk.inv_item = False
        desk.desc_reveal = False  # don't reveal the contents with "look"
        desk.moveTo(self.start_room)
        hat = Thing(self.game, "hat")
        hat.moveTo(desk)

        self.game.turnMain("l")
        self.game.turnMain("take all")

        self.assertTrue(self.game.me.containsItem(hat))

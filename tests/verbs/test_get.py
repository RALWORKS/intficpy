from ..helpers import IFPTestCase

from intficpy.thing_base import Thing
from intficpy.things import Surface, Container, Liquid, UnderSpace, Lock
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

    def test_get_item_when_pc_is_on_surface(self):
        loc = Surface(self.game, "desk")
        loc.invItem = True
        loc.moveTo(self.start_room)
        loc.can_contain_standing_player = True

        sub_loc = Container(self.game, "box")
        sub_loc.moveTo(loc)
        sub_loc.can_contain_standing_player = True

        self.game.me.moveTo(sub_loc)

        self.game.turnMain("take desk")

        self.assertIn("You take the desk", self.app.print_stack.pop())
        self.assertIn("You get off of the desk", self.app.print_stack.pop())
        self.assertIn("You get out of the box", self.app.print_stack.pop())

    def test_get_item_when_pc_sitting(self):
        item = Thing(self.game, "bob")
        item.moveTo(self.start_room)
        self.game.me.position = "sitting"

        self.game.turnMain("take bob")

        self.assertIn("You stand up. ", self.app.print_stack)
        self.assertEqual(self.game.me.position, "standing")

    def test_get_liquid_in_container_gets_container(self):
        container = Container(self.game, "cup")
        container.invItem = True
        container.moveTo(self.start_room)
        item = Liquid(self.game, "broth", "broth")
        item.moveTo(container)

        self.game.turnMain("take broth")

        self.assertIn("You take the cup. ", self.app.print_stack)

    def test_get_thing_nested_in_thing_in_inventory(self):
        container = Container(self.game, "cup")
        container.moveTo(self.start_room)
        item = Thing(self.game, "bead")
        item.invItem = True

        container.moveTo(self.game.me)
        item.moveTo(container)

        self.game.turnMain("look in cup")

        self.game.turnMain("take bead")

        self.assertEqual(
            "You remove the bead from the cup. ", self.app.print_stack.pop()
        )

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
        parent.invItem = True
        child = Thing(self.game, "penny")
        parent.moveTo(self.start_room)
        child.moveTo(parent)

        self.game.turnMain("take rug")
        self.assertIn("A penny is revealed. ", self.app.print_stack)

    def test_get_underspace_reveals_multiple_contained_items(self):
        parent = UnderSpace(self.game, "rug")
        parent.invItem = True
        child = Thing(self.game, "penny")
        child2 = Thing(self.game, "rock")
        parent.moveTo(self.start_room)
        child.moveTo(parent)
        child2.moveTo(parent)

        self.game.turnMain("take rug")
        self.assertIn("are revealed", self.app.print_stack.pop())

    def test_get_composite_underspace_reveals_contained_item(self):
        item = Container(self.game, "box")
        item.invItem = True
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
        item.invItem = True
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

    def test_get_object_from_closed_and_locked_container(self):
        box = Container(self.game, "box")
        box.giveLid()
        item = Thing(self.game, "bead")
        item.invItem = True
        item.moveTo(box)
        box.setLock(Lock(self.game, True, None))
        box.revealed = True
        box.moveTo(self.start_room)

        self.game.turnMain("get bead")
        self.assertIn("is locked", self.app.print_stack.pop())

        self.assertTrue(box.containsItem(item))
        self.assertFalse(box.is_open)


class TestTakeAll(IFPTestCase):
    def test_take_all_takes_all_known_top_level_invitems(self):
        hat = Thing(self.game, "hat")
        hat.invItem = True
        hat.moveTo(self.start_room)
        cat = Thing(self.game, "cat")
        cat.invItem = True
        cat.moveTo(self.start_room)

        self.game.turnMain("l")
        self.game.turnMain("take all")

        self.assertTrue(self.game.me.containsItem(hat))
        self.assertTrue(self.game.me.containsItem(cat))

    def test_no_items_are_taken_unless_they_are_known(self):
        hat = Thing(self.game, "hat")
        hat.invItem = True
        hat.moveTo(self.start_room)
        cat = Thing(self.game, "cat")
        cat.invItem = True
        cat.moveTo(self.start_room)

        # self.game.turnMain("l") # we haven't looked, so we don't know
        self.game.turnMain("take all")

        self.assertFalse(self.game.me.containsItem(hat))
        self.assertFalse(self.game.me.containsItem(cat))

    def test_take_all_takes_known_objects_from_sub_locations(self):
        desk = Surface(self.game, "desk")
        desk.desc_reveal = True
        desk.moveTo(self.start_room)
        hat = Thing(self.game, "hat")
        hat.invItem = True
        hat.moveTo(desk)

        self.game.turnMain("l")
        self.game.turnMain("take all")

        self.assertTrue(self.game.me.containsItem(hat))

    def test_take_all_does_not_take_items_that_are_not_discovered(self):
        desk = Surface(self.game, "desk")
        desk.invItem = False
        desk.desc_reveal = False  # don't reveal the contents with "look"
        desk.moveTo(self.start_room)
        hat = Thing(self.game, "hat")
        hat.invItem = True
        hat.moveTo(desk)

        self.game.turnMain("l")
        self.game.turnMain("take all")

        self.assertFalse(self.game.me.containsItem(hat))


class TestRemoveFrom(IFPTestCase):
    def test_remove_me(self):
        box = Container(self.game, "box")
        box.moveTo(self.start_room)
        self.game.me.moveTo(box)
        self.game.turnMain("remove me from box")
        self.assertIn("cannot take yourself", self.app.print_stack.pop())

    def test_remove_object_from_something_the_object_is_not_in(self):
        box = Container(self.game, "box")
        box.moveTo(self.start_room)
        glob = Thing(self.game, "glob")
        glob.moveTo(self.start_room)
        self.game.turnMain("remove glob from box")
        self.assertIn("The glob is not in the box. ", self.app.print_stack)

    def test_remove_object_already_in_top_level_inventory(self):
        glob = Thing(self.game, "glob")
        glob.moveTo(self.me)
        self.game.turnMain("remove glob from me")
        self.assertIn("You are currently holding the glob. ", self.app.print_stack)

    def test_remove_object_from_locked_closed_container(self):
        box = Container(self.game, "box")
        box.moveTo(self.start_room)
        box.giveLid()
        box.setLock(Lock(self.game, True, None))
        box.revealed = True
        glob = Thing(self.game, "glob")
        glob.moveTo(box)
        self.game.turnMain("remove glob from box")
        self.assertIn("The box is locked. ", self.app.print_stack)
        self.assertIs(glob.location, box)

    def test_remove_non_inv_item(self):
        box = Container(self.game, "box")
        box.moveTo(self.start_room)
        glob = Thing(self.game, "glob")
        glob.invItem = False
        glob.moveTo(box)
        self.game.turnMain("remove glob from box")
        self.assertIn(glob.cannotTakeMsg, self.app.print_stack)
        self.assertIs(glob.location, box)

    def test_remove_child_composite_object(self):
        box = Container(self.game, "box")
        box.moveTo(self.start_room)
        glob = Thing(self.game, "glob")
        glob.moveTo(box)
        drip = Thing(self.game, "drip")
        glob.addComposite(drip)
        self.game.turnMain("remove drip from box")
        self.assertIn(drip.cannotTakeMsg, self.app.print_stack)
        self.assertIs(drip.location, box)

    def test_remove_object_containing_player(self):
        pedestal = Surface(self.game, "pedestal")
        pedestal.moveTo(self.start_room)
        box = Container(self.game, "box")
        box.invItem = True
        box.moveTo(pedestal)
        self.me.moveTo(box)
        self.game.turnMain("remove box from pedestal")
        self.assertIn("You are currently in the box", self.app.print_stack.pop())
        self.assertIs(box.location, pedestal)

    def test_remove_underspace_not_containing_items(self):
        box = Container(self.game, "box")
        box.moveTo(self.start_room)
        rug = UnderSpace(self.game, "rug")
        rug.invItem = True
        rug.moveTo(box)
        self.game.turnMain("remove rug from box")
        msg = self.app.print_stack.pop()
        self.assertNotIn("revealed", msg)

    def test_remove_underspace_containing_items(self):
        box = Container(self.game, "box")
        box.moveTo(self.start_room)
        rug = UnderSpace(self.game, "rug")
        rug.invItem = True
        rug.moveTo(box)
        penny = Thing(self.game, "penny")
        bead = Thing(self.game, "bead")
        penny.moveTo(rug)
        bead.moveTo(rug)
        self.game.turnMain("remove rug from box")
        msg = self.app.print_stack.pop()
        self.assertIn("penny", msg)
        self.assertIn("bead", msg)
        self.assertIn("are revealed", msg)
        self.assertIs(penny.location, box)
        self.assertIs(bead.location, box)

    def test_remove_item_with_component_underspace_containing_items(self):
        box = Container(self.game, "box")
        box.moveTo(self.start_room)
        mishmash = Thing(self.game, "mishmash")
        mishmash.invItem = True
        rug = UnderSpace(self.game, "rug")
        mishmash.addComposite(rug)
        mishmash.moveTo(box)
        penny = Thing(self.game, "penny")
        penny.moveTo(rug)
        self.game.turnMain("remove mishmash from box")
        msg = self.app.print_stack.pop()
        self.assertIn("penny", msg)
        self.assertIn("is revealed", msg)
        self.assertIs(penny.location, box)

from ..helpers import IFPTestCase

from intficpy.things import Container, Liquid, Thing


class TestPourIntoVerb(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.old_container = Container(self.game, "bottle")
        self.old_container.invItem = True
        self.old_container.holds_liquid = True
        self.new_container = Container(self.game, "bowl")
        self.new_container.invItem = True
        self.new_container.size = 50
        self.new_container.holds_liquid = True
        self.liquid = Liquid(self.game, "wine", "wine")
        self.liquid.moveTo(self.old_container)
        self.old_container.moveTo(self.start_room)
        self.new_container.moveTo(self.start_room)

    def test_pour_out_non_liquid_non_container(self):
        item = Thing(self.game, "bead")
        item.invItem = True
        item.moveTo(self.start_room)
        self.game.turnMain("pour bead into bowl")
        self.assertIn("has nothing on", self.app.print_stack.pop())

    def test_pour_out_non_liquid_non_container_from_container(self):
        item = Thing(self.game, "bead")
        item.size = 2
        item.moveTo(self.old_container)
        self.old_container.removeThing(self.liquid)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("You dump the bottle", self.app.print_stack.pop())

    def test_pour_out_non_liquid_non_container_item_too_large(self):
        item = Thing(self.game, "bead")
        item.size = 100
        item.moveTo(self.old_container)
        self.old_container.removeThing(self.liquid)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn(
            self.new_container.does_not_fit_msg.format(
                item=item, self=self.new_container
            ),
            self.app.print_stack,
        )

    def test_pour_non_liquid_into_non_container(self):
        item = Thing(self.game, "bead")
        item.size = 2
        item.moveTo(self.old_container)
        self.old_container.removeThing(self.liquid)

        rock = Thing(self.game, "rock")
        rock.moveTo(self.start_room)

        self.game.turnMain("pour bottle into rock")
        self.assertIn("cannot put anything in the rock", self.app.print_stack.pop())

    def test_pour_liquid_into_container(self):
        self.game.turnMain("pour wine into bowl")
        self.assertIn("You dump the wine in the bowl. ", self.app.print_stack)

    def test_pour_liquid_into_container_containing_non_liquid_item(self):
        # TODO: rethink the handling of priority.
        item = Thing(self.game, "bead")
        item.moveTo(self.new_container)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("You dump the bottle in the bowl", self.app.print_stack.pop())
        self.assertIn("You dump out the bowl", self.app.print_stack.pop())
        self.assertIn("(First trying to dump out the bowl", self.app.print_stack.pop())

        self.assertIs(item.location, self.start_room)
        self.assertIs(self.liquid.location, self.new_container)

    def test_pour_liquid_into_closed_container(self):
        self.new_container.giveLid()
        self.new_container.makeClosed()

        self.game.turnMain("pour wine into bowl")
        self.assertIn("You dump", self.app.print_stack.pop())
        self.assertIn("You open", self.app.print_stack.pop())

    def test_pour_liquid_from_closed_container_referencing_liquid_directly(self):
        self.old_container.giveLid()
        self.old_container.makeClosed()
        self.old_container.revealed = True

        self.game.turnMain("pour wine into bowl")
        self.assertIn("is closed", self.app.print_stack.pop())

    def test_pour_empty_container(self):
        self.old_container.removeThing(self.liquid)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn(self.old_container.empty_msg, self.app.print_stack)

    def test_pour_liquid_from_closed_container(self):
        self.old_container.giveLid()
        self.old_container.makeClosed()

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("is closed", self.app.print_stack.pop())

    def test_pour_liquid_into_container_that_does_not_hold_liquid(self):
        self.new_container.holds_liquid = False
        self.game.turnMain("pour wine into bowl")
        self.assertIn("cannot hold a liquid", self.app.print_stack.pop())

    def test_pour_liquid_not_in_container(self):
        syrup = Liquid(self.game, "syrup", "syrup")
        syrup.moveTo(self.start_room)

        self.game.turnMain("pour syrup into bowl")
        self.assertIn("unable to collect", self.app.print_stack.pop())

    def test_pour_liquid_onto_same_liquid(self):
        wine = Liquid(self.game, "wine", "wine")
        wine.moveTo(self.new_container)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("already wine in the bowl", self.app.print_stack.pop())

    def test_pour_liquid_onto_infinite_well_of_same_liquid(self):
        wine = Liquid(self.game, "wine", "wine")
        wine.moveTo(self.new_container)
        wine.infinite_well = True

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("You dump the bottle in the bowl. ", self.app.print_stack)

    def test_pour_liquid_onto_different_liquid(self):
        syrup = Liquid(self.game, "syrup", "syrup")
        syrup.moveTo(self.new_container)

        self.game.turnMain("pour wine into bowl")
        self.assertIn("already syrup", self.app.print_stack.pop())

    def test_pour_liquid_onto_different_liquid_mixwith_implemented(self):
        syrup = Liquid(self.game, "syrup", "syrup")
        syrup.moveTo(self.new_container)

        sweetened_wine = Liquid(self.game, "wine", "sweetened wine")

        def mixWith(g, base_liquid, mix_liquid, event="turn"):
            mix = set([base_liquid.liquid_type, mix_liquid.liquid_type])
            container = base_liquid.location
            if mix == {"wine", "syrup"}:
                container.removeThing(base_liquid)
                container.addThing(sweetened_wine)
                g.addTextToEvent(event, "The syrup dissolves in the wine.")
                return True
            else:
                return False

        syrup.mix_with_liquid_type_allowed = ["wine"]
        self.liquid.mix_with_liquid_type_allowed = ["syrup"]
        syrup.mixWith = mixWith
        self.liquid.mixWith = mixWith

        self.game.turnMain("pour wine into bowl")
        self.assertIn("dissolves", self.app.print_stack.pop())
        self.assertIn("You dump", self.app.print_stack.pop())
        self.assertFalse(self.new_container.containsItem(self.liquid))
        self.assertFalse(self.new_container.containsItem(syrup))
        self.assertTrue(self.new_container.containsItem(sweetened_wine))

    def test_pour_item_implicitly_into_child_object(self):
        target = Thing(self.game, "thing")
        target.addComposite(self.new_container)
        target.moveTo(self.start_room)

        self.game.turnMain("pour wine in thing")
        self.assertIn("You dump", self.app.print_stack.pop())
        self.assertTrue(self.new_container.containsItem(self.liquid))


class TestFillFromVerb(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.old_container = Container(self.game, "bottle")
        self.old_container.invItem = True
        self.old_container.holds_liquid = True
        self.new_container = Container(self.game, "bowl")
        self.new_container.invItem = True
        self.new_container.size = 50
        self.new_container.holds_liquid = True
        self.liquid = Liquid(self.game, "wine", "wine")
        self.liquid.moveTo(self.old_container)
        self.old_container.moveTo(self.start_room)
        self.new_container.moveTo(self.start_room)

    def test_fill_container_with_liquid(self):
        self.game.turnMain("fill bowl with wine")
        self.assertIn("You fill the bowl", self.app.print_stack.pop())
        self.assertTrue(self.new_container.topLevelContainsItem(self.liquid))

    def test_fill_non_container(self):
        item = Thing(self.game, "bead")
        item.invItem = True
        item.moveTo(self.start_room)
        self.game.turnMain("fill bead from bottle")
        self.assertIn("can't fill that", self.app.print_stack.pop())

    def test_fill_container_from_container_containing_only_non_liquids(self):
        item = Thing(self.game, "bead")
        item.size = 2
        item.moveTo(self.old_container)
        self.old_container.removeThing(self.liquid)

        self.game.turnMain("fill bowl from bottle")
        self.assertIn("no liquid in", self.app.print_stack.pop())

    def test_fill_container_non_container_non_liquid(self):
        item = Thing(self.game, "rock")
        item.moveTo(self.start_room)
        self.game.turnMain("fill bowl from rock")
        self.assertIn("no liquid in the rock", self.app.print_stack.pop())

    def test_fill_container_from_me(self):
        self.game.turnMain("fill bowl from myself")
        self.assertIn("cannot fill anything from yourself", self.app.print_stack.pop())

    def test_fill_container_from_container(self):
        self.game.turnMain("fill bowl from bottle")
        self.assertIn("You fill the bowl", self.app.print_stack.pop())
        self.assertTrue(self.new_container.topLevelContainsItem(self.liquid))

    def test_fill_container_containing_non_liquid_item(self):
        item = Thing(self.game, "bead")
        item.moveTo(self.new_container)

        self.game.turnMain("fill bowl from bottle")
        self.assertIn("You fill the bowl", self.app.print_stack.pop())
        self.assertIn("You dump", self.app.print_stack.pop())

        self.assertIs(item.location, self.start_room)
        self.assertIs(self.liquid.location, self.new_container)

    def test_fill_container_from_closed_container(self):
        self.old_container.giveLid()
        self.old_container.makeClosed()

        self.game.turnMain("fill bowl from bottle")
        self.assertIn("bottle is closed", self.app.print_stack.pop())

    def test_fill_closed_container(self):
        self.new_container.giveLid()
        self.new_container.makeClosed()

        self.game.turnMain("fill bowl from bottle")
        self.assertIn("bowl is closed", self.app.print_stack.pop())

    def test_fill_from_empty_container(self):
        self.old_container.removeThing(self.liquid)

        self.game.turnMain("fill bowl from bottle")
        self.assertIn("no liquid in the bottle", self.app.print_stack.pop())

    def test_fill_container_that_does_not_hold_liquid(self):
        self.new_container.holds_liquid = False
        self.game.turnMain("fill bowl from bottle")
        self.assertIn("cannot hold a liquid", self.app.print_stack.pop())

    def test_fill_container_from_infinite_well(self):
        self.liquid.infinite_well = True
        self.game.turnMain("fill bowl from bottle")
        self.assertIn("You fill the bowl", self.app.print_stack.pop())
        self.assertNotIn("taking all of it", self.app.print_stack.pop())

    def test_fill_liquid_onto_same_liquid(self):
        wine = Liquid(self.game, "wine", "wine")
        wine.moveTo(self.new_container)

        self.game.turnMain("fill bowl from bottle")
        self.assertIn("already wine", self.app.print_stack.pop())

    def test_fill_liquid_from_cannot_fill_from_true_liquid(self):
        self.liquid.can_fill_from = False

        self.game.turnMain("fill bowl from bottle")
        self.assertIn(self.liquid.cannot_fill_from_msg, self.app.print_stack)

    def test_fill_liquid_using_liquid_name(self):
        self.game.turnMain("fill bowl from wine")
        self.assertIn("You fill the bowl with wine", self.app.print_stack.pop())
        self.assertTrue(self.new_container.topLevelContainsItem(self.liquid))

    def test_fill_container_of_liquid_with_different_liquid(self):
        syrup = Liquid(self.game, "syrup", "syrup")
        syrup.moveTo(self.new_container)

        self.game.turnMain("fill bowl from bottle")
        self.assertIn("already syrup", self.app.print_stack.pop())

    def test_fill_container_of_liquid_with_different_liquid_mixwith_implemented(self):
        syrup = Liquid(self.game, "syrup", "syrup")
        syrup.moveTo(self.new_container)

        sweetened_wine = Liquid(self.game, "wine", "sweetened wine")

        def mixWith(g, base_liquid, mix_liquid):
            mix = set([base_liquid.liquid_type, mix_liquid.liquid_type])
            container = base_liquid.location
            if mix == {"wine", "syrup"}:
                container.removeThing(base_liquid)
                container.addThing(sweetened_wine)
                g.addText("The syrup dissolves in the wine.")
                return True
            else:
                return False

        syrup.mixWith = mixWith
        self.liquid.mixWith = mixWith

        self.game.turnMain("fill bowl from bottle")
        self.assertIn("dissolves", self.app.print_stack.pop())
        self.assertFalse(self.new_container.containsItem(self.liquid))
        self.assertFalse(self.new_container.containsItem(syrup))
        self.assertTrue(self.new_container.containsItem(sweetened_wine))

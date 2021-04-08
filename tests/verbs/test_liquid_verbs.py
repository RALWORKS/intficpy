from ..helpers import IFPTestCase

from intficpy.things import Container, Liquid, Thing


class TestPourIntoVerb(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.old_container = Container(self.game, "bottle")
        self.old_container.holds_liquid = True
        self.new_container = Container(self.game, "bowl")
        self.new_container.size = 50
        self.new_container.holds_liquid = True
        self.liquid = Liquid(self.game, "wine", "wine")
        self.liquid.moveTo(self.old_container)
        self.old_container.moveTo(self.start_room)
        self.new_container.moveTo(self.start_room)

    def test_pour_out_non_liquid_non_container(self):
        item = Thing(self.game, "bead")
        item.moveTo(self.start_room)
        self.game.turnMain("pour bead into bowl")
        self.assertIn("You can't", self.app.print_stack.pop())

    def test_pour_out_non_liquid_non_container_from_container(self):
        item = Thing(self.game, "bead")
        item.size = 2
        item.moveTo(self.old_container)
        self.old_container.removeThing(self.liquid)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("You dump the contents", self.app.print_stack.pop())

    def test_pour_out_non_liquid_non_container_item_too_large(self):
        item = Thing(self.game, "bead")
        item.size = 100
        item.moveTo(self.old_container)
        self.old_container.removeThing(self.liquid)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("too large to fit inside", self.app.print_stack.pop())

    def test_pour_non_liquid_into_non_container(self):
        item = Thing(self.game, "bead")
        item.size = 2
        item.moveTo(self.old_container)
        self.old_container.removeThing(self.liquid)

        rock = Thing(self.game, "rock")
        rock.moveTo(self.start_room)

        self.game.turnMain("pour bottle into rock")
        self.assertIn("not a container", self.app.print_stack.pop())

    def test_pour_liquid_into_container(self):
        self.game.turnMain("pour wine into bowl")
        self.assertIn("You pour the wine into the bowl. ", self.app.print_stack)

    def test_pour_liquid_into_container_containing_non_liquid_item(self):
        item = Thing(self.game, "bead")
        item.moveTo(self.new_container)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("You pour", self.app.print_stack.pop())
        self.assertIn("You dump the contents of the bowl", self.app.print_stack.pop())

        self.assertIs(item.location, self.start_room)
        self.assertIs(self.liquid.location, self.new_container)

    def test_pour_liquid_into_closed_container(self):
        self.new_container.giveLid()
        self.new_container.makeClosed()

        self.game.turnMain("pour wine into bowl")
        self.assertIn("is closed", self.app.print_stack.pop())

    def test_pour_liquid_from_closed_container_referencing_liquid_directly(self):
        self.old_container.giveLid()
        self.old_container.makeClosed()

        self.game.turnMain("pour wine into bowl")
        self.assertIn("is closed", self.app.print_stack.pop())

    def test_pour_empty_container(self):
        self.old_container.removeThing(self.liquid)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("is empty", self.app.print_stack.pop())

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
        self.assertIn("isn't in a container", self.app.print_stack.pop())

    def test_pour_liquid_onto_same_liquid(self):
        wine = Liquid(self.game, "wine", "wine")
        wine.moveTo(self.new_container)

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("already has wine", self.app.print_stack.pop())

    def test_pour_liquid_onto_infinite_well_of_same_liquid(self):
        wine = Liquid(self.game, "wine", "wine")
        wine.moveTo(self.new_container)
        wine.infinite_well = True

        self.game.turnMain("pour bottle into bowl")
        self.assertIn("You pour the bottle into the bowl. ", self.app.print_stack)

    def test_pour_liquid_onto_different_liquid(self):
        syrup = Liquid(self.game, "syrup", "syrup")
        syrup.moveTo(self.new_container)

        self.game.turnMain("pour wine into bowl")
        self.assertIn("already full", self.app.print_stack.pop())

    def test_pour_liquid_onto_different_liquid_mixwith_implemented(self):
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

        self.game.turnMain("pour wine into bowl")
        self.assertIn("dissolves", self.app.print_stack.pop())
        self.assertFalse(self.new_container.containsItem(self.liquid))
        self.assertFalse(self.new_container.containsItem(syrup))
        self.assertTrue(self.new_container.containsItem(sweetened_wine))

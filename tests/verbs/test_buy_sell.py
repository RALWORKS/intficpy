from ..helpers import IFPTestCase
from intficpy.thing_base import Thing
from intficpy.actor import Actor
from intficpy.verb import BuyVerb, SellVerb, BuyFromVerb, SellToVerb
from intficpy.grammar import GrammarObject


class TestBuyFiniteStock(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "widget")
        self.actor = Actor(self.game, "Dmitri")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.currency)
        self.actor.addSelling(self.sale_item, self.currency, 1, 1)
        self.start_room.addThing(self.actor)
        self.sale_item.makeKnown(self.me)

        self.OUT_STOCK_MSG = "That item is out of stock. "

    def test_buy(self):
        self.game.turnMain(f"buy {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(msg, expected, "Unexpected msg after attempting to buy item")

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )

        self.game.turnMain(f"buy {self.sale_item.verbose_name}")
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.OUT_STOCK_MSG,
            "Tried to buy item which should be out of stock. Received unexpected msg",
        )
        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy out of stock item. Number in inventory should not have "
            "changed. ",
        )

    def test_buy_from(self):
        BuyFromVerb()._runVerbFuncAndEvents(self.game, self.sale_item, self.actor)

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(msg, expected, "Unexpected msg after attempting to buy item")

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )

        BuyFromVerb()._runVerbFuncAndEvents(self.game, self.sale_item, self.actor)
        msg = self.app.print_stack.pop()

        self.assertEqual(
            msg,
            self.OUT_STOCK_MSG,
            "Tried to buy item which should be out of stock. Received unexpected msg",
        )
        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy out of stock item. Number in inventory should not have "
            "changed. ",
        )


class TestBuyInfiniteStock(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "widget")
        self.actor = Actor(self.game, "Dmitri")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.currency)
        self.actor.addSelling(self.sale_item, self.currency, 1, True)
        self.start_room.addThing(self.actor)
        self.sale_item.makeKnown(self.me)

    def test_buy(self):
        stock_before = self.actor.for_sale[self.sale_item.ix].number

        self.game.turnMain(f"buy {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(msg, expected, "Unexpected msg after attempting to buy item")

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )

        stock_after = self.actor.for_sale[self.sale_item.ix].number

        self.assertIs(
            stock_before,
            stock_after,
            "Stock of infinite item should not have changed after buying",
        )


class TestBuyNotEnoughMoney(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "widget")
        self.actor = Actor(self.game, "Dmitri")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.currency)
        self.actor.addSelling(self.sale_item, self.currency, 2, 1)
        self.start_room.addThing(self.actor)
        self.sale_item.makeKnown(self.me)

    def test_buy(self):
        self.game.turnMain(f"buy {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        BASE_FAILURE_MSG = "You don't have enough"
        self.assertIn(
            BASE_FAILURE_MSG,
            msg,
            "Unexpected message after attempting to buy item with insufficient funds",
        )

        self.assertItemNotIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item with insufficient money.",
        )


class TestBuyNotSelling(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "widget")
        self.actor = Actor(self.game, "Dmitri")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.currency)
        self.sale_item.makeKnown(self.me)

        self.start_room.addThing(self.actor)

    def test_buy(self):
        BuyVerb()._runVerbFuncAndEvents(self.game, self.sale_item)

        msg = self.app.print_stack.pop()
        BASE_FAILURE_MSG = f"{self.actor.capNameArticle(True)} doesn't sell"
        self.assertIn(
            BASE_FAILURE_MSG,
            msg,
            "Unexpected message after attempting to buy item not for sale",
        )

        self.assertItemNotIn(
            self.sale_item, self.me.contains, "Attempted to buy item not for sale."
        )


class TestBuyWithNoActorsInRoom(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "widget")
        self.actor = Thing(self.game, "statue")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.currency)
        self.start_room.addThing(self.actor)
        self.sale_item.makeKnown(self.me)

    def test_buy_from(self):
        self.game.turnMain(
            f"buy {self.sale_item.verbose_name} from {self.actor.verbose_name}"
        )

        msg = self.app.print_stack.pop()
        BASE_FAILURE_MSG = "You cannot buy anything from"
        self.assertIn(
            BASE_FAILURE_MSG,
            msg,
            "Unexpected message after attempting to buy item from non-Actor",
        )

        self.assertItemNotIn(
            self.sale_item, self.me.contains, "Attempted to buy item from non-Actor."
        )

    def test_buy(self):
        self.game.turnMain(f"buy {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        FAILURE_MSG = "There's no one obvious here to buy from. "
        self.assertEqual(
            FAILURE_MSG,
            msg,
            "Unexpected message after attempting to buy item in a room with no Actors",
        )

        self.assertItemNotIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item in a room with no Actors.",
        )


class TestBuyPerson(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Actor(self.game, "kate")
        self.actor = Actor(self.game, "dmitri")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.currency)
        self.actor.addSelling(self.sale_item, self.currency, 2, 1)
        self.start_room.addThing(self.actor)
        self.sale_item.makeKnown(self.me)

    def test_buy(self):
        self.game.turnMain(f"buy {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        FAILURE_MSG = "You cannot buy or sell a person. "
        self.assertEqual(
            FAILURE_MSG, msg, "Unexpected message after attempting to buy an Actor"
        )

        self.assertItemNotIn(
            self.sale_item, self.me.contains, "Attempted to buy an Actor."
        )


class TestBuyInRoomWithMultipleActors(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "bulb")
        self.actor1 = Actor(self.game, "Dmitri")
        self.actor2 = Actor(self.game, "Kate")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.currency)
        self.actor1.addSelling(self.sale_item, self.currency, 1, 1)
        self.start_room.addThing(self.actor1)
        self.start_room.addThing(self.actor2)
        self.sale_item.makeKnown(self.me)

    def test_buy(self):
        self.game.turnMain(f"buy {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        BASE_DISAMBIG_MSG = "Would you like to buy from"
        self.assertIn(
            BASE_DISAMBIG_MSG,
            msg,
            "Unexpected message after attempting to buy from ambiguous Actor",
        )

        self.assertItemNotIn(
            self.sale_item, self.me.contains, "Attempted to buy from ambiguous Actor."
        )

    def test_buy_with_lastTurn_dobj_actor(self):
        self.game.parser.command.dobj = GrammarObject(target=self.actor1)

        self.game.turnMain(f"buy {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(
            msg, expected, "Unexpected msg after attempting to buy from ambigous Actor",
        )

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )

    def test_buy_with_lastTurn_iobj_actor(self):
        self.game.parser.command.iobj = GrammarObject(target=self.actor1)

        self.game.turnMain(f"buy {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        expected = f"(Received: {self.sale_item.verbose_name}) "
        self.assertEqual(
            msg, expected, "Unexpected msg after attempting to buy from ambigous Actor"
        )

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. ",
        )


class TestSell(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "widget")
        self.sale_item.makeKnown(self.me)
        self.actor = Actor(self.game, "dmitri")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.sale_item)
        self.me.addThing(self.sale_item.copyThing())
        self.actor.addWillBuy(self.sale_item, self.currency, 1, 1)
        self.start_room.addThing(self.actor)

        self.BASE_DOES_NOT_WANT_MORE_MSG = "will not buy any more"

    def test_sell(self):
        self.assertItemIn(
            self.sale_item,
            self.me.contains,
            "This test needs widgets in the inventory. ",
        )
        self.assertEqual(len(self.me.contains[self.sale_item.ix]), 2)

        self.game.turnMain(f"sell {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        expected = (
            f"(Received: {self.actor.will_buy[self.sale_item.ix].price} "
            f"{self.currency.verbose_name}) "
        )
        self.assertEqual(msg, expected, "Unexpected msg after attempting to sell item")

        self.assertItemExactlyOnceIn(
            self.currency,
            self.me.contains,
            "Attempted to sell item. Received success message. ",
        )

        SellVerb()._runVerbFuncAndEvents(self.game, self.sale_item)
        msg = self.app.print_stack.pop()

        self.assertIn(
            self.BASE_DOES_NOT_WANT_MORE_MSG,
            msg,
            "Tried to sell item to actor who should not want any more. Received "
            "unexpected msg",
        )
        self.assertItemExactlyOnceIn(
            self.currency,
            self.me.contains,
            "Attempted to buy out of stock item. Number in inventory should not have "
            "changed. ",
        )

    def test_sell_to(self):
        self.assertItemIn(
            self.sale_item,
            self.me.contains,
            "This test needs widgets in the inventory. ",
        )
        self.assertEqual(len(self.me.contains[self.sale_item.ix]), 2)

        self.game.turnMain(
            f"sell {self.sale_item.verbose_name} to {self.actor.verbose_name}"
        )

        msg = self.app.print_stack.pop()
        expected = (
            f"(Received: {self.actor.will_buy[self.sale_item.ix].price} "
            f"{self.currency.verbose_name}) "
        )
        self.assertEqual(msg, expected, "Unexpected msg after attempting to sell item")

        self.assertItemExactlyOnceIn(
            self.currency,
            self.me.contains,
            "Attempted to sell item. Received success message. ",
        )

        SellToVerb()._runVerbFuncAndEvents(self.game, self.sale_item, self.actor)
        msg = self.app.print_stack.pop()

        self.assertIn(
            self.BASE_DOES_NOT_WANT_MORE_MSG,
            msg,
            "Tried to sell item to actor who should not want any more. Received "
            "unexpected msg",
        )
        self.assertItemExactlyOnceIn(
            self.currency,
            self.me.contains,
            "Attempted to buy out of stock item. Number in inventory should not have "
            "changed. ",
        )


class TestSellDoesNotWant(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "widget")
        self.sale_item.makeKnown(self.me)
        self.actor = Actor(self.game, "Dmitri")
        self.me.addThing(self.sale_item)

        self.start_room.addThing(self.actor)

        self.BASE_DOES_NOT_WANT_MSG = "doesn't want to buy"

    def test_sell(self):
        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "This test needs a widget in the inventory. ",
        )

        SellVerb()._runVerbFuncAndEvents(self.game, self.sale_item)

        msg = self.app.print_stack.pop()
        self.assertIn(
            self.BASE_DOES_NOT_WANT_MSG,
            msg,
            "Unexpected msg after attempting to sell item",
        )

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to sell item actor does not want. Should still have exactly 1.",
        )

    def test_sell_to(self):
        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "This test needs a widget in the inventory. ",
        )

        SellToVerb()._runVerbFuncAndEvents(self.game, self.sale_item, self.actor)

        msg = self.app.print_stack.pop()
        self.assertIn(
            self.BASE_DOES_NOT_WANT_MSG,
            msg,
            "Unexpected msg after attempting to sell item",
        )

        self.assertItemExactlyOnceIn(
            self.sale_item,
            self.me.contains,
            "Attempted to sell item actor does not want. Should still have exactly 1.",
        )


class TestSellInRoomWithMultipleActors(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "bulb")
        self.actor1 = Actor(self.game, "dmitri")
        self.actor2 = Actor(self.game, "kate")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.sale_item)
        self.actor1.addWillBuy(self.sale_item, self.currency, 1, 1)
        self.start_room.addThing(self.actor1)
        self.start_room.addThing(self.actor2)

    def test_sell(self):
        self.game.turnMain(f"sell {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        BASE_DISAMBIG_MSG = "Would you like to sell it to"
        self.assertIn(
            BASE_DISAMBIG_MSG,
            msg,
            "Unexpected message after attempting to sell to ambiguous Actor",
        )

        self.assertItemIn(
            self.sale_item, self.me.contains, "Attempted to sell to ambiguous Actor."
        )

    def test_sell_with_lastTurn_dobj_actor(self):
        self.game.parser.command.dobj = GrammarObject(target=self.actor1)

        self.game.turnMain(f"sell {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        expected = (
            f"(Received: {self.actor1.will_buy[self.sale_item.ix].price} "
            f"{self.currency.verbose_name}) "
        )
        self.assertEqual(
            msg, expected, "Unexpected msg after attempting to sell from ambigous Actor"
        )

        self.assertItemExactlyOnceIn(
            self.currency,
            self.me.contains,
            "Attempted to sell item. Recieved success message. Expected 1 currency. ",
        )
        self.assertItemNotIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. Expected no sale_item "
            "in inv.",
        )

    def test_sell_with_lastTurn_iobj_actor(self):
        self.game.parser.command.iobj = GrammarObject(target=self.actor1)
        self.assertTrue(self.game.parser.command.iobj.target)

        self.game.turnMain(f"sell {self.sale_item.verbose_name}")

        msg = self.app.print_stack.pop()
        expected = (
            f"(Received: {self.actor1.will_buy[self.sale_item.ix].price} "
            f"{self.currency.verbose_name}) "
        )
        self.assertEqual(
            msg, expected, "Unexpected msg after attempting to sell from ambigous Actor"
        )

        self.assertItemExactlyOnceIn(
            self.currency,
            self.me.contains,
            "Attempted to sell item. Recieved success message. Expected 1 currency. ",
        )
        self.assertItemNotIn(
            self.sale_item,
            self.me.contains,
            "Attempted to buy item. Received success message. Expected no sale_item "
            "in inv.",
        )


class TestSellInRoomWithNoActors(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.sale_item = Thing(self.game, "bulb")
        self.currency = Thing(self.game, "penny")
        self.me.addThing(self.sale_item)

    def test_sell(self):
        SellVerb()._runVerbFuncAndEvents(self.game, self.sale_item)

        msg = self.app.print_stack.pop()
        NOONE_HERE_MSG = "There's no one obvious here to sell to. "
        self.assertIn(
            NOONE_HERE_MSG,
            msg,
            "Unexpected message after attempting to sell in room with no Actor",
        )

        self.assertItemIn(
            self.sale_item, self.me.contains, "Attempted to sell in room with no Actor."
        )

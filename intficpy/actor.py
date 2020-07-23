from .ifp_object import IFPObject
from .thing_base import Thing
from . import vocab
from .tokenizer import cleanInput, tokenize, removeArticles

##############################################################
# ACTOR.PY - the Actor class for IntFicPy
# Contains the Actor class, the Topic class the actors dictionary
##############################################################


class Actor(Thing):
    """Actor class, used for characters in the creator's game """

    POSITION_STATE_DESC_KEY = "position_state_desc"

    def __init__(self, name):
        """Intitializes the Actor instance and sets essential properties """
        super().__init__(name)

        self.can_be_led = False
        self.for_sale = {}
        self.will_buy = {}
        self.ask_topics = {}
        self.tell_topics = {}
        self.give_topics = {}
        self.show_topics = {}
        self.special_topics = {}
        self.special_topics_alternate_keys = {}
        self.sticky_topic = None
        self.hi_topic = None
        self.return_hi_topic = None
        self.said_hi = False
        self.hermit_topic = None
        self.manual_suggest = False
        # prints when player's question/statement does not match a topic
        self.default_topic = "No response."

        self.knows_about = [self.ix]
        self.position = "standing"
        self.commodity = False
        self.wearing = {}
        self.invItem = False
        self.cannotTakeMsg = "You cannot take a person. "

    @property
    def position_state_desc(self):
        if self.position == "standing":
            return ""
        return f"{self.capNameArticle()} is {self.position}. "

    def makeProper(self, proper_name):
        """Makes the name of an Actor into proper name
		Takes a string argument proper_name
		Called by the game creator """
        # NOTE: currently enters vocab words incorrectly if proper_name contains multiple words
        token_name = proper_name
        token_name = cleanInput(token_name, False)
        token_name = tokenize(token_name)
        token_name = removeArticles(token_name)
        self.name = token_name[-1]
        self.setAdjectives(self.adjectives + token_name)
        for tok in token_name:
            self.addSynonym(tok)
        self.verbose_name = proper_name
        self.hasArticle = False

    def makeStanding(self):
        self.position = "standing"

    def makeSitting(self):
        self.position = "sitting"

    def makeLying(self):
        self.position = "lying"

    def setHiTopics(self, hi_topic, return_hi_topic):
        self.said_hi = False
        if hi_topic:
            hi_topic.owner = self
        if return_hi_topic:
            return_hi_topic.owner = self
        self.hi_topic = hi_topic
        self.return_hi_topic = return_hi_topic

    def setHermitTopic(self, hermit_topic):
        self.hermit_topic = hermit_topic
        if hermit_topic:
            hermit_topic.owner = self

    def removeHermitTopic(self):
        self.hermit_topic = None

    def addTopic(self, ask_tell_give_show, topic, thing):
        """Adds a conversation topic to the Actor
		Takes argument ask_tell, a string """
        topic.owner = self
        if "ask" in ask_tell_give_show or ask_tell_give_show == "all":
            self.ask_topics[thing.ix] = topic
        if "tell" in ask_tell_give_show or ask_tell_give_show == "all":
            self.tell_topics[thing.ix] = topic
        if "give" in ask_tell_give_show or ask_tell_give_show == "all":
            self.give_topics[thing.ix] = topic
        if "show" in ask_tell_give_show or ask_tell_give_show == "all":
            self.show_topics[thing.ix] = topic

    def addSpecialTopic(self, topic):
        topic.owner = self
        self.special_topics[topic.suggestion] = topic
        for x in topic.alternate_phrasings:
            self.special_topics_alternate_keys[x] = topic

    def removeSpecialTopic(self, topic):
        if topic.suggestion in self.special_topics:
            del self.special_topics[topic.suggestion]
        for x in topic.alternate_phrasings:
            if x in self.special_topics_alternate_keys:
                del self.special_topics_alternate_keys[x]

    def removeAllSpecialTopics(self):
        topics = []
        for suggestion in self.special_topics:
            topics.append(self.special_topics[suggestion])
        for topic in topics:
            self.removeSpecialTopic(topic)

    def removeAllTopics(self):
        self.ask_topics = {}
        self.tell_topics = {}
        self.give_topics = {}
        self.show_topics = {}

    def printSuggestions(self, game):
        if self.special_topics != {}:
            for suggestion in self.special_topics:
                game.addTextToEvent("turn", "(You could " + suggestion + ")")
                game.parser.command.specialTopics[suggestion] = self.special_topics[
                    suggestion
                ]
            for phrasing in self.special_topics_alternate_keys:
                game.parser.command.specialTopics[
                    phrasing
                ] = self.special_topics_alternate_keys[phrasing]

    def defaultTopic(self, game):
        """
        The default function for an Actor's default topic
        Should be overwritten by the game creator for an instance to create special responses
        """
        game.addTextToEvent("turn", self.default_topic)
        self.printSuggestions(game)

    def addSelling(self, item, currency, price, stock):
        """
        Add an item that the Actor sells.
        Parameters:
            item     - the Thing for sale (by the unit)
            currency - Thing to offer in exchange (use currency.copyThing() for duplicates)
            price    - the number of the currency Things required,
            stock    - the number of a given Thing the Actor has to sell (set to True for infinite)
        """
        if item.ix not in self.for_sale:
            self.for_sale[item.ix] = SaleItem(item, currency, price, stock)

    def addWillBuy(self, item, currency, price, max_wanted):
        """
        Parameters:
            item       - the Thing the Actor wishes to purchase (by the unit)
            currency   - the Thing the Actor will offer in exchange
                         (use currency.copyThing() for duplicates)
            price      - the number of the currency Things the Actor will give,
            max_wanted - the number of a given Thing the Actor is willing to buy
                         (set to True for infinite)
        """
        if item.ix not in self.will_buy:
            self.will_buy[item.ix] = SaleItem(item, currency, price, max_wanted)


class Player(Actor):
    """
    Player object.

    Currently, the game only supports a single Player character.
    """

    def __init__(self, name):
        super().__init__(name)

    def setPlayer(self):
        self.addSynonym("me")
        self.addSynonym("myself")
        self.addSynonym("yourself")
        self.addSynonym("you")

    @property
    def default_desc(self):
        """
        By default, the Player is not described in the room description.
        """
        return ""

    @property
    def default_xdesc(self):
        """
        The base item description, if a description has not been specified.
        """
        return "You notice nothing remarkable about yourself. "


class Topic(IFPObject):
    """class for conversation topics"""

    def __init__(self, topic_text):
        super().__init__
        self.text = topic_text
        self.owner = None

    def func(self, game, suggest=True):
        game.addTextToEvent("turn", self.text)
        if self.owner and suggest:
            if not self.owner.manual_suggest:
                self.owner.printSuggestions(game)


class SpecialTopic(IFPObject):
    """class for conversation topics"""

    def __init__(self, suggestion, topic_text):
        super().__init__()
        self.text = topic_text
        self.suggestion = suggestion
        self.alternate_phrasings = []
        self.owner = None

    def func(self, game, suggest=True):
        game.addTextToEvent("turn", self.text)
        if suggest and self.owner:
            if not self.owner.manual_suggest:
                self.owner.printSuggestions(game)

    def addAlternatePhrasing(self, phrasing):
        self.alternate_phrasings.append(phrasing)


class SaleItem(IFPObject):
    def __init__(self, item, currency, price, number):
        super().__init__()
        self.thing = item
        self.currency = currency
        self.price = price
        self.number = number
        self.wants = number
        self.out_stock_msg = "That item is out of stock. "
        self.wants_no_more_msg = None
        self.purchase_msg = "You purchase " + item.lowNameArticle(False) + ". "
        self.sell_msg = "You sell " + item.lowNameArticle(True) + ". "

    def buyUnit(self, game):
        for i in range(0, self.price):
            if self.currency.ix in game.me.contains:
                game.me.removeThing(game.me.contains[self.currency.ix][0])
            elif self.currency.ix in game.me.sub_contains:
                game.me.removeThing(game.me.sub_contains[self.currency.ix][0])
        if self.price > 1:
            game.addTextToEvent(
                "turn",
                "(Lost: " + str(self.price) + " " + self.currency.getPlural() + ")",
            )
        else:
            game.addTextToEvent(
                "turn",
                "(Lost: " + str(self.price) + " " + self.currency.verbose_name + ")",
            )
        if self.number is True:
            obj = self.thing.copyThing()
        elif self.number > 1:
            obj = self.thing.copyThing()
        else:
            obj = self.thing
            if obj.location:
                obj.location.removeThing(obj)
        game.me.addThing(obj)
        if not self.number is True:
            self.number = self.number - 1
        game.addTextToEvent("turn", "(Received: " + obj.verbose_name + ") ")

    def afterBuy(self, game):
        pass

    def beforeBuy(self, game):
        pass

    def soldOut(self, game):
        pass

    def sellUnit(self, game):
        game.me.removeThing(self.thing)
        game.addTextToEvent("turn", "(Lost: " + self.thing.verbose_name + ")")
        for i in range(0, self.price):
            game.me.addThing(self.currency)
        if not self.number is True:
            self.number = self.number - 1
        if self.price > 1:
            game.addTextToEvent(
                "turn",
                "(Received: "
                + str(self.price)
                + " "
                + self.currency.getPlural()
                + ") ",
            )
        else:
            game.addTextToEvent(
                "turn",
                "(Received: "
                + str(self.price)
                + " "
                + self.currency.verbose_name
                + ") ",
            )

    def afterSell(self, game):
        pass

    def beforeSell(self, game):
        pass

    def boughtAll(self, game):
        pass

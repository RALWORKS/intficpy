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

    def __init__(self, name):
        """Intitializes the Actor instance and sets essential properties """
        super().__init__(name)

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
        # self.desc = proper_name + " is here."
        self.hasArticle = False

    def describeThing(self, description):
        self.base_desc = description
        self.desc = self.base_desc
        if self.position != "standing":
            self.desc = (
                self.base_desc
                + " "
                + (self.getArticle(True) + self.name).capitalize()
                + " is "
                + self.position
                + " down."
            )

    def xdescribeThing(self, description):
        self.base_xdesc = description
        self.xdesc = self.base_xdesc
        if self.position != "standing":
            self.xdesc = (
                self.base_xdesc
                + " "
                + (self.getArticle(True) + self.name).capitalize()
                + " is "
                + self.position
                + " down."
            )

    def addThing(self, item):
        """Add an item to contents, update descriptions
		Takes argument item, pointing to a Thing """
        if item.contains_in:
            if item.lock_obj:
                if item.lock_obj.ix in self.contains:
                    if not item.lock_obj in self.contains[item.lock_obj.ix]:
                        self.addThing(item.lock_obj)
                else:
                    self.addThing(item.lock_obj)
        if item.is_composite:
            for item2 in item.children:
                if item2.ix in self.contains:
                    if not item2 in self.contains[item2.ix]:
                        self.addThing(item2)
                else:
                    self.addThing(item2)
        item.location = self
        # nested items
        nested = item.getNested()
        for t in nested:
            if t.ix in self.sub_contains:
                self.sub_contains[t.ix].append(t)
            else:
                self.sub_contains[t.ix] = [t]
        # top level item
        if item.ix in self.contains:
            self.contains[item.ix].append(item)
        else:
            self.contains[item.ix] = [item]

    def makeStanding(self):
        self.position = "standing"
        self.desc = self.base_desc
        self.xdesc = self.base_xdesc

    def makeSitting(self):
        self.position = "sitting"
        self.desc = (
            self.base_desc
            + " "
            + self.getArticle().capitalize()
            + self.name
            + " is sitting down."
        )
        self.xdesc = (
            self.base_xdesc
            + " "
            + self.getArticle().capitalize()
            + self.name
            + " is sitting down."
        )

    def makeLying(self):
        self.position = "lying"
        self.desc = (
            self.base_desc
            + " "
            + self.getArticle().capitalize()
            + self.name
            + " is lying down."
        )
        self.xdesc = (
            self.base_xdesc
            + " "
            + self.getArticle().capitalize()
            + self.name
            + " is lying down."
        )

    def removeThing(self, item):
        """Remove an item from contents, update decription """
        if item.contains_in:
            if item.lock_obj:
                if item.lock_obj.ix in self.contains:
                    if item.lock_obj in self.contains[item.lock_obj.ix]:
                        self.removeThing(item.lock_obj)
                if item.lock_obj.ix in self.sub_contains:
                    if item.lock_obj in self.sub_contains[item.lock_obj.ix]:
                        self.removeThing(item.lock_obj)
        if item.is_composite:
            for item2 in item.children:
                if item2.ix in self.contains:
                    if item2 in self.contains[item2.ix]:
                        self.removeThing(item2)
                if item2.ix in self.sub_contains:
                    if item2 in self.sub_contains[item2.ix]:
                        self.removeThing(item2)
        # nested items
        nested = item.getNested()
        for t in nested:
            if t.ix in self.sub_contains:
                if t in self.sub_contains[t.ix]:
                    self.sub_contains[t.ix].remove(t)
                    if self.sub_contains[t.ix] == []:
                        del self.sub_contains[t.ix]
        # top level item
        rval = False
        if item.ix in self.contains:
            if item in self.contains[item.ix]:
                self.contains[item.ix].remove(item)
                if self.contains[item.ix] == []:
                    del self.contains[item.ix]
                rval = True
                item.location = False
        if item.ix in self.sub_contains:
            if item in self.sub_contains[item.ix]:
                self.sub_contains[item.ix].remove(item)
                if self.sub_contains[item.ix] == []:
                    del self.sub_contains[item.ix]
                rval = True
                item.location = False
        return rval

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
            game.lastTurn.convNode = True
            for suggestion in self.special_topics:
                game.addTextToEvent("turn", "(You could " + suggestion + ")")
                game.lastTurn.specialTopics[suggestion] = self.special_topics[
                    suggestion
                ]
            for phrasing in self.special_topics_alternate_keys:
                game.lastTurn.specialTopics[
                    phrasing
                ] = self.special_topics_alternate_keys[phrasing]

    def defaultTopic(self, game):
        """The default function for an Actor's default topic
		Should be overwritten by the game creator for an instance to create special responses
		Takes argument game.app, pointing to the PyQt5 GUI"""
        game.addTextToEvent("turn", self.default_topic)
        self.printSuggestions(game)

    def addSelling(self, item, currency, price, stock):
        """item is the Thing for sale (by the unit), currency is the Thing to offer in exchange 
		(use currency.copyThing() for duplicates), price is the number of the currency Things required,
		and stock is the number of a given Thing the Actor has to sell (set to True for infinite) """
        if item.ix not in self.for_sale:
            self.for_sale[item.ix] = SaleItem(item, currency, price, stock)

    def addWillBuy(self, item, currency, price, max_wanted):
        """item is the Thing the Actor wishes to purchase (by the unit), currency is the Thing the Actor will offer in exchange 
		(use currency.copyThing() for duplicates), price is the number of the currency Things the Actor will give,
		and max_wanted is the number of a given Thing the Actor is willing to buy (set to True for infinite) """
        if item.ix not in self.will_buy:
            self.will_buy[item.ix] = SaleItem(item, currency, price, max_wanted)


class Player(Actor):
    """Class for Player objects """

    def __init__(self, name):
        super().__init__(name)

        self.desc = ""
        self.base_desc = ""
        self.xdesc = "You notice nothing remarkable about yourself. "
        self.base_xdesc = "You notice nothing remarkable about yourself. "

    def setPlayer(self):
        self.addSynonym("me")
        self.addSynonym("myself")
        self.addSynonym("yourself")
        self.addSynonym("you")

    def makeStanding(self):
        self.position = "standing"
        self.desc = self.base_desc
        self.xdesc = self.base_xdesc

    def makeSitting(self):
        self.position = "sitting"
        if isinstance(self.location, Thing):
            self.desc = (
                self.base_desc
                + " You are sitting on "
                + self.location.getArticle()
                + self.location.verbose_name
                + "."
            )
            self.xdesc = (
                self.base_xdesc
                + " You are sitting on "
                + self.location.getArticle()
                + self.location.verbose_name
                + "."
            )
        else:
            self.desc = self.base_desc + " You are sitting down."
            self.xdesc = self.base_xdesc + " You are sitting down."

    def makeLying(self):
        self.position = "lying"
        if isinstance(self.location, Thing):
            self.desc = (
                self.base_desc
                + " You are lying "
                + self.location.contains_preposition
                + " "
                + self.location.getArticle()
                + self.location.verbose_name
                + "."
            )
            self.xdesc = (
                self.base_xdesc
                + " You are lying "
                + self.location.contains_preposition
                + " "
                + self.location.getArticle()
                + self.location.verbose_name
                + "."
            )
        else:
            self.desc = self.base_desc + " You are lying down."
            self.xdesc = self.base_xdesc + " You are lying down."


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

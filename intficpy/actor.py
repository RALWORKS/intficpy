from .ifp_object import IFPObject
from .thing_base import Thing
from . import vocab
from .tokenizer import cleanInput, tokenize, removeArticles

##############################################################
# ACTOR.PY - the Actor class for IntFicPy
# Contains the Actor class, the Topic class the actors dictionary
##############################################################


class Actor(Thing):
    """
    Actors are Things that are capable of conversations.

    Topics can be added using the `addTopic` method. SpecialTopics are added using the
    `addSpecialTopic` method.

    Actors track their available topics in dictionaries, depending on topic type.
    Each Actor has a dicitonary for `ask_topics`, `tell_topics`, `give_topics`, and
    `show_topics`, to which Topic objects can be added, as well as a `special_topics`
    dictionary for SpecialTopics.

    All topics that are currently in these dictionaries are considered to be active, and
    will be available in converstions.

    Actors can also buy and sell items. This can be enabled by adding an item using the
    `addSelling` or `addWillBuy` methods.

    Items the Actor is willing to sell or buy are stored in the `for_sale` and `will_buy`
    dictionaries on the Actor object. More specifically, objects of the SaleItem class
    are stored here, serving as records of what is for sale/what is wanted, and templates
    for the transactions.

    If you need to access a SaleItem created by `addSelling`/`addWillBuy`, you can look
    it up in the Actor's `for_sale` or `will_buy` dictionary. The key is the IFPObject
    index of the relevant Thing, which can be found in the Thing's `ix` attribute.
    For example, if an Actor `person` sells a Thing called `item`, we can look up the
    SaleItem with `person.for_sale[item.ix]`.

    :param game: the current game
    :type game: IFPGame
    :param name: a single noun to use as the Actor's initial name (synonyms/adjectives/
        full_name can be customized after initialization)
    :type name: str
    """

    POSITION_STATE_DESC_KEY = "position_state_desc"

    def __init__(self, game, name):
        super().__init__(game, name)

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
    def verb_to_be(self):
        """Get the simple present tense of the verb "to be" for this Actor. Returns "is"
        unless the Actor is the current player (i.e. "you"), in which case it returns
        "are".

        :rtype: str
        """
        if self.is_current_player:
            return "are"
        return "is"

    @property
    def verbose_name(self):
        """The name the game will use to describe this Actor to the player. Returns "you"
        if this Actor is currently the player character, otherwise defaults to the logic
        from the superclass.

        :rtype: str
        """
        if self.is_current_player:
            return "you"
        return super().verbose_name

    @property
    def is_current_player(self):
        """Is this Actor the current player character?

        :rtype: bool
        """
        if not self.game:
            return False
        return self.game.me.ix == self.ix

    @property
    def contains_desc(self):
        """Return an empty string. We do not want to describe an actor's inventory on
        room/examine desc.
        """
        return ""

    @property
    def position_state_desc(self):
        """A description of an Actor's position (standing, lying, etc.), to be appended to
        that Actor's description in the room. Standing is assumed to be default, and is
        not specially described.

        :rtype: str
        """
        if self.position == "standing":
            return ""
        return f"{self.capNameArticle()} is {self.position}. "

    def makeProper(self, proper_name):
        """Give this character a proper name. Updates `has_proper_name` as well as
        `name`, `full_name`, synonyms, and adjectives for this Actor based on
        the new name given. The intended use is to facilitate having the player
        character "learn" the initially unknown name of another character.

        :param proper_name: the name of this character
        :type proper_name: str
        """
        # NOTE: currently enters vocab words incorrectly if proper_name contains multiple words
        token_name = proper_name
        token_name = cleanInput(token_name, False)
        token_name = tokenize(token_name)
        token_name = removeArticles(token_name)
        self.name = token_name[-1]
        self.setAdjectives(self.adjectives + token_name)
        for tok in token_name:
            self.addSynonym(tok)
        self.full_name = proper_name
        self.has_proper_name = True

    def makeStanding(self):
        """
        Set the Actor's position to standing
        """
        self.position = "standing"

    def makeSitting(self):
        """
        Set the Actor's position to sitting
        """
        self.position = "sitting"

    def makeLying(self):
        """Set the Actor's position to lying"""
        self.position = "lying"

    def makeWearing(self, item):
        """
        Make the Actor wear an item.

        :param item: the item to wear
        :type item: Thing
        """
        if item.location:
            item.location.removeThing(item)
        if item.ix in self.wearing:
            self.wearing[item.ix].append(item)
            return
        self.wearing[item.ix] = [item]

    def removeWearing(self, item):
        """
        Make the Actor wear an item.

        :param item: the item to wear
        :type item: Thing
        """
        if not item.ix in self.wearing:
            return
        self.wearing[item.ix].remove(item)
        if not self.wearing[item.ix]:
            del self.wearing[item.ix]
        item.location = None

    def setHiTopics(self, hi_topic, return_hi_topic):
        """Set the hi topics for this Actor. Sets both the initial greeting, and the
        greeting to show at the start of subsequent interactions. To make both greetings
        the same, pass in the same Topic for both.

        :param hi_topic: the Topic to open when the player first talks to this Actor
            None skips directly to the topic at hand.
        :type hi_topic: Topic, None
        :param return_hi_topic: the Topic to open when the the player uses "hi" or
            "talk to" after having previously interacted with the Actor. None skips
            directly to the topic at hand.
        :type return_hi_topic: Topic, None
        """
        self.said_hi = False
        if hi_topic:
            hi_topic.owner = self
        if return_hi_topic:
            return_hi_topic.owner = self
        self.hi_topic = hi_topic
        self.return_hi_topic = return_hi_topic

    def setHermitTopic(self, hermit_topic):
        """
        Set a hermit topic for this Actor. While the hermit topic is set, it will be the
        only response the Actor gives to any conversation.

        :param hermit_topic: the topic to set as the Actor's hermit topic
        :type hermit_topic: Topic
        """
        self.hermit_topic = hermit_topic
        if hermit_topic:
            hermit_topic.owner = self

    def removeHermitTopic(self):
        """
        Remove the Actor's hermit topic, if there is one. Equivalent to setting
        `some_actor.hermit_topic = None`
        """
        self.hermit_topic = None

    def addTopic(self, ask_tell_give_show, topic, thing):
        """Adds a conversation topic (ask/tell/give/show) to the Actor.

        :param ask_tell_give_show: specifies one or more conversation verbs
            (ask, tell, give, and/or show) to which the actor should respond with
            the specified topic, when the direct object is the specified thing.
            For every substring "ask", "tell", "give" and "show" present in
            this string, the Topic will be registered under the corresponding
            topic category for the given Thing. For instance, passing in "ask show"
            for this parameter will cause the Topic to be saved as both an ask
            topic, ("ask selena about rice") and a show topic ("show selena rice")
            Ordering of ask/tell/give/show in the string does not matter.
        :type ask_tell_give_show: str
        :param topic: the Topic you want to add to the Actor
        :type topic: Topic
        :param thing: the Thing you want to associate the Topic to, ie. what you want to
            ask about, tell about, or give, or show to the Actor
        :type thing: Thing
        """
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
        """Add a SpecialTopic for this Actor. This will immediately add it to the
        available suggestions for the Actor.

        :param topic: the SpecialTopic to add
        :type topic: SpecialTopic
        """
        topic.owner = self
        self.special_topics[topic.suggestion] = topic
        for x in topic.alternate_phrasings:
            self.special_topics_alternate_keys[x] = topic

    def removeSpecialTopic(self, topic):
        """Remove the specified SpecialTopic from this Actor. The SpecialTopic will no
        longer appear in the Actor's conversation suggestions.

        :param topic: the SpecialTopic to remove
        :type topic: SpecialTopic
        """
        if topic.suggestion in self.special_topics:
            del self.special_topics[topic.suggestion]
        for x in topic.alternate_phrasings:
            if x in self.special_topics_alternate_keys:
                del self.special_topics_alternate_keys[x]

    def removeAllSpecialTopics(self):
        """Clear all SpecialTopics from this Actor. This removes all conversation
        suggestions. The SpecialTopic objects will remain unchanged, and can be
        added back later.
        """
        topics = []
        for suggestion in self.special_topics:
            topics.append(self.special_topics[suggestion])
        for topic in topics:
            self.removeSpecialTopic(topic)

    def removeAllTopics(self):
        """Clear all ask/tell/give/show Topics from this Actor. The Actor will no longer
        have responses to being asked or told about anything, or to being given or shown
        anything. The Topic objects will remain unchanged, and can be
        added back later.
        """
        self.ask_topics = {}
        self.tell_topics = {}
        self.give_topics = {}
        self.show_topics = {}

    def printSuggestions(self, game):
        """Print the suggestions for this all of this Actor's current SpecialTopics in the
        format, "(You could {suggestion)".

        :param game: the current game
        :type game: IFPGame
        """
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
        """Called when the Actor's default topic is triggered. Prints the `default_topic`
        text, and the current SpecialTopic suggestions.

        :param game: the current game
        :type game: IFPGame
        """
        game.addTextToEvent("turn", self.default_topic)
        self.printSuggestions(game)

    def addSelling(self, item, currency, price, stock):
        """Add an item that the Actor sells.

        :param item: the Thing for sale (by the unit)
        :type item: Thing
        :param currency: Thing to offer in exchange (use currency.copyThing() for duplicates)
        :type currency: Thing
        :param price: the number of the currency Things required
        :type price: int
        :param stock: the number of a given Thing the Actor has to sell (set to True for infinite)
        :type stock: int or True
        """
        if item.ix not in self.for_sale:
            self.for_sale[item.ix] = SaleItem(self.game, item, currency, price, stock)

    def addWillBuy(self, item, currency, price, max_wanted):
        """Add an item that the Actor is willing to buy.

        :param item: the Thing the Actor wishes to purchase (by the unit)
        :type item: Thing
        :param currency: the Thing the Actor will offer in exchange (by the unit)
        :type currency: Thing
        :param price: the number of the currency Things the Actor will give for a single unit
            of the item
        :type price: int
        :param max_wanted: the number of a given Thing the Actor is willing to buy
            (set to True for infinite)
        :type max_wanted: int or True
        """
        if item.ix not in self.will_buy:
            self.will_buy[item.ix] = SaleItem(
                self.game, item, currency, price, max_wanted
            )

    def playerTalksTo(self, event="turn", **kwargs):
        """
        The result of the player trying to talk to this character

        :param event: the key for the event to print text to
        :type event: str
        """
        if self.hermit_topic:
            self.hermit_topic.func(self.game, False)
        elif self.sticky_topic:
            self.sticky_topic.func(self.game)
        elif self.hi_topic and not self.said_hi:
            self.hi_topic.func(self.game)
            self.said_hi = True
        elif self.return_hi_topic:
            self.return_hi_topic.func(self.game)
        else:
            self.defaultTopic(self.game)
        return True

    def playerAboutToAskAbout(self, item, event="turn", **kwargs):
        """
        Evaluated when the player is about to try to ask the actor about something
        + gives hermit topic if set, and returns False (blocks interaction)

        :param item: the item the player asks about
        :type item: Thing
        :param event: the key for the event to print text to
        :type event: str
        """
        if self.hermit_topic:
            self.hermit_topic.func(self.game, False)
            return False
        return True

    def playerAsksAbout(self, item, event="turn", **kwargs):
        """
        The result of the player trying to ask this character about an item

        :param item: the item the player asks about
        :type item: Thing
        :param event: the key for the event to print text to
        :type event: str
        """
        if self.hi_topic and not self.said_hi:
            self.hi_topic.func(self.game)
            self.said_hi = True
        elif self.return_hi_topic:
            self.return_hi_topic.func(self.game)

        if item.ix in self.ask_topics:
            self.ask_topics[item.ix].func(self.game)
            ret = True
        else:
            self.defaultTopic(self.game)
            ret = False

        if self.sticky_topic:
            self.sticky_topic.func(self.game)

        return ret

    def playerAboutToTellAbout(self, item, event="turn", **kwargs):
        """
        Evaluated when the player is about to try to tell the actor about something
        + gives hermit topic if set, and returns False (blocks interaction)

        :param item: the item the player tells about
        :type item: Thing
        :param event: the key for the event to print text to
        :type event: str
        """
        if self.hermit_topic:
            self.hermit_topic.func(self.game, False)
            return False
        return True

    def playerTellsAbout(self, item, event="turn", **kwargs):
        """
        The result of the player trying to tell this character about an item

        :param item: the item the player tells about
        :type item: Thing
        :param event: the key for the event to print text to
        :type event: str
        """
        if self.hi_topic and not self.said_hi:
            self.hi_topic.func(self.game)
            self.said_hi = True
        elif self.return_hi_topic:
            self.return_hi_topic.func(self.game)

        if item.ix in self.tell_topics:
            self.tell_topics[item.ix].func(self.game)
            ret = True
        else:
            self.defaultTopic(self.game)
            ret = False

        if self.sticky_topic:
            self.sticky_topic.func(self.game)

        return ret

    def playerAboutToShow(self, item, event="turn", **kwargs):
        """
        Evaluated when the player is about to try to show the actor something
        + gives hermit topic if set, and returns False (blocks interaction)

        :param item: the item the player shows
        :type item: Thing
        :param event: the key for the event to print text to
        :type event: str
        """
        if self.hermit_topic:
            self.hermit_topic.func(self.game, False)
            return False
        return True

    def playerShows(self, item, event="turn", **kwargs):
        """
        The result of the player trying to show this character about an item

        :param item: the item the player shows
        :type item: Thing
        :param event: the key for the event to print text to
        :type event: str
        """
        if self.hi_topic and not self.said_hi:
            self.hi_topic.func(self.game)
            self.said_hi = True
        elif self.return_hi_topic:
            self.return_hi_topic.func(self.game)

        if item.ix in self.show_topics:
            self.show_topics[item.ix].func(self.game)
            ret = True
        else:
            self.defaultTopic(self.game)
            ret = False

        if self.sticky_topic:
            self.sticky_topic.func(self.game)

        return ret

    def playerAboutToGiveItem(self, item, event="turn", **kwargs):
        """
        Evaluated when the player is about to try to give the actor something
        + gives hermit topic if set, and returns False (blocks interaction)

        :param item: the item the player gives
        :type item: Thing
        :param event: the key for the event to print text to
        :type event: str
        """
        if self.hermit_topic:
            self.hermit_topic.func(self.game, False)
            return False
        return True

    def playerAboutToGiveAway(self, event="turn", **kwargs):
        """
        Evaluated when the player is about to try to give this item away.
        Gives some better dialog & logic for attempts to give away the current player

        :param event: the key for the event to print text to
        :type event: str
        """
        if self.is_current_player:
            self.game.addTextToEvent(event, "You cannot give yourself away. ")
            return False
        return True

    def playerGivesItem(self, item, event="turn", **kwargs):
        """
        The result of the player trying to give this character about an item

        :param item: the item the player gives
        :type item: Thing
        :param event: the key for the event to print text to
        :type event: str
        """
        if not item.playerAboutToGiveAway(event="turn"):
            return False

        if self.hi_topic and not self.said_hi:
            self.hi_topic.func(self.game)
            self.said_hi = True
        elif self.return_hi_topic:
            self.return_hi_topic.func(self.game)

        if item.ix in self.give_topics:
            self.give_topics[item.ix].func(self.game)
            if item.give:
                item.moveTo(self)
            ret = True
        else:
            self.defaultTopic(self.game)
            ret = False

        if self.sticky_topic:
            self.sticky_topic.func(self.game)

        return ret


class Player(Actor):
    """
    A playable Actor.

    Currently, the game only supports a single player character.

    :param game: the current game
    :type game: IFPGame

    """

    def __init__(self, game):
        super().__init__(game, "me")

    def setPlayer(self):
        """
        Add some default synomyms for this Player object that players are likely to try
        to use to refer to their character
        """
        self.addSynonym("me")
        self.addSynonym("myself")
        self.addSynonym("yourself")
        self.addSynonym("you")

    def teleport(self, location):
        """
        Move the player to a new location, then describe the room
        """
        self.moveTo(location)
        self.location.describe(self.game)

    @property
    def default_desc(self):
        """
        Describe this Player in the room.
        By default, the Player is not described in the room description.

        :rtype: str
        """
        return ""

    @property
    def default_xdesc(self):
        """
        The base description of the Player, if a description has not been specified.

        :rtype: str
        """
        return "You notice nothing remarkable about yourself. "


class Topic(IFPObject):
    """Topic represents a topic in conversation.

    Topic (base) is meant to be added to an Actor as an ask/tell/give/show topic -
    a conversation topic that is triggered when a player asks about, tells
    about, shows, or gives a Thing or Abstract.

    As well as printing text, a Topic can add and remove SpecialTopics from its Actor
    when it is triggered. Set SpecialTopics to *add* to the Actor by adding the
    SpecialTopic objects to the Topic's `new_suggestions`. Add them to `expire_suggestions`
    to remove them.

    The Topic itself contains no reference to any Thing or Abstract to which a given
    Actor will associate it. This connection is created when the Topic is added to the
    Actor with addTopic, and then, exists only on the Actor object. This means that the
    same Topic can be added as a response to multiple things.

    A single Topic should *not* be added to multiple Actors at the same time, as this
    will break suggestion functionality.

    :param game: the current game
    :type game: IFPGame
    :param topic_text: the text that should print when this Topic is opened
    :type topic_text: str
    """

    def __init__(self, game, topic_text):
        super().__init__(game)

        self.text = topic_text
        self.owner = None
        self.new_suggestions = []
        self.expire_suggestions = []

    def func(self, game, suggest=True):
        """What happens when this Topic is opened.
        Prints the topic text and suggestions to the turn.

        :param game: the current game
        :type game: IFPGame
        :param suggest: should we print the current suggested SpecialTopics?
        :type suggest: bool, optional
        """
        self.update_suggestions()

        game.addTextToEvent("turn", self.text)

        self.on_trigger(game)

        if self.owner and suggest:
            if not self.owner.manual_suggest:
                self.owner.printSuggestions(game)

    def update_suggestions(self):
        """Read this Topic's `new_suggestions` and `expire_suggestions`, and add/remove
        SpecialTopic suggestions from the Actor as needed.
        """
        if not self.owner:
            return
        for item in self.new_suggestions:
            if item.suggestion not in self.owner.special_topics:
                self.owner.addSpecialTopic(item)
        for item in self.expire_suggestions:
            if item.suggestion in self.owner.special_topics:
                self.owner.removeSpecialTopic(item)

    def on_trigger(self, game):
        """Override this to add custom behaviour when the Topic function runs

        :param game: the current game
        :type game: IFPGame
        """
        pass


class SpecialTopic(Topic):
    """A SpecialTopic is is a Topic accessed by responding to a printed suggestion during
    conversation, instead of through the use of the ask/tell/give/show verbs.

    A SpecialTopic can be added to an Actor using `Actor.addSpecialTopic`

    :param game: the current game
    :type game: IFPGame
    :param suggestion: the prompt or suggestion that will lead the player to this
        SpecialTopic
    :type suggestion: str
    :param topic_text: the text that should print when this Topic is opened
    :type topic_text: str
    """

    def __init__(self, game, suggestion, topic_text):
        super().__init__(game, topic_text)

        self.suggestion = suggestion
        self.alternate_phrasings = []

    def addAlternatePhrasing(self, phrasing):
        """
        Add a possible alternate phrasing for this suggestion.
        Alternate phrasings will not be printed to the user.

        :param phrasing: the alternate phrasing to add
        :type phrasing: str
        """
        self.alternate_phrasings.append(phrasing)


class SaleItem(IFPObject):
    """Stores information about an Actor's ability to sell a particular item to the player,
    or buy a particular item from the player.
    SaleItems are created automatically by the Actor methods `addSelling` and `addWillBuy`,
    and game creators should not generally need to create them manually.

    Once created, SaleItems can be accessed in the Actor's `for_sale` and `will_buy`
    dictionaries by looking up the `ix` of the Thing in question.

    :param game: the current game
    :type game: IFPGame
    :param item: the item the Actor sells
    :type item: Thing
    :param currency: the item the Actor expects to receive in return, as currency
    :type currency: Thing
    :param price: the number of the currency item required to purchase 1 of the item
        for sale
    :type price: int
    :param number: the number of the item the Actor has in stock (True for infinite)
    :type number: int or True
    """

    def __init__(self, game, item, currency, price, number):
        super().__init__(game)
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
        """
        Buy one unit of the item for sale.

        Removes the needed amount of currency from the player's inventory, adds the
        purchased item, and prints the interaction messages to the turn.

        :param game: the current game
        :type game: IFPGame
        """
        for i in range(0, self.price):
            if self.currency.ix in game.me.contains:
                game.me.removeThing(game.me.contains[self.currency.ix][0])
            elif self.currency.ix in game.me.sub_contains:
                game.me.removeThing(game.me.sub_contains[self.currency.ix][0])
        if self.price > 1:
            game.addTextToEvent(
                "turn", "(Lost: " + str(self.price) + " " + self.currency.plural + ")",
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
        """
        Override this to trigger behaviour after a unit of the item is bought.

        :param game: the current game
        :type game: IFPGame
        """
        pass

    def beforeBuy(self, game):
        """
        Override this to trigger behaviour before a unit of the item is bought.

        :param game: the current game
        :type game: IFPGame
        """
        pass

    def soldOut(self, game):
        """
        Override this to trigger behaviour when the item sells out.

        :param game: the current game
        :type game: IFPGame
        """
        pass

    def sellUnit(self, game):
        """
        Sell one unit of the item for sale.

        Removes the item from the player's inventory, adds the needed amount of
        currency, and prints the interaction messages to the turn.

        :param game: the current game
        :type game: IFPGame
        """
        game.me.removeThing(self.thing)
        game.addTextToEvent("turn", "(Lost: " + self.thing.verbose_name + ")")
        for i in range(0, self.price):
            game.me.addThing(self.currency)
        if not self.number is True:
            self.number = self.number - 1
        if self.price > 1:
            game.addTextToEvent(
                "turn",
                "(Received: " + str(self.price) + " " + self.currency.plural + ") ",
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
        """
        Override this to trigger behaviour after the player sells a unit of the item.

        :param game: the current game
        :type game: IFPGame
        """
        pass

    def beforeSell(self, game):
        """
        Override this to trigger behaviour before the player sells a unit of the item.

        :param game: the current game
        :type game: IFPGame
        """
        pass

    def boughtAll(self, game):
        """
        Override this to trigger behaviour when the Actor has bought all of the item
        that they are willing to buy.

        :param game: the current game
        :type game: IFPGame
        """
        pass

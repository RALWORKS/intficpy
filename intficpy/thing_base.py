import copy

from .physical_entity import PhysicalEntity

##############################################################
# THING_BASE.PY - the Thing class for IntFicPy
# Defines the Thing class
##############################################################


class Thing(PhysicalEntity):
    """Thing is the overarching class for all items that exist in the game """

    ignore_if_ambiguous = False
    cannot_interact_msg = None

    # TRAVELCONNECTOR FACE
    twin = None
    connection = None
    direction = None

    # CONTENTS
    # contain type flags
    contains_on = False
    contains_in = False
    contains_under = False

    # is valid Player location?
    can_contain_sitting_player = False
    can_contain_standing_player = False
    can_contain_lying_player = False

    # language
    # TODO: these should default to in/out (out of?) to eliminate the null check
    contains_preposition = "on"
    contains_preposition_inverse = "off"
    desc_reveal = True
    xdesc_reveal = True

    # COMPOSITE OBJECTS
    is_composite = False  # TODO: replace if x.composite with if x.children
    parent_obj = None
    lock_obj = None
    children_desc = None

    # TODO: refactor: duplicate storing of all children seems unnecessary
    child_Things = None
    child_Surfaces = None
    child_Containers = None
    child_UnderSpaces = None
    children = None

    # OPEN/CLOSE
    has_lid = False
    is_open = False

    # STATES
    state_descriptors = None

    # thing properties
    far_away = False
    size = 50

    # ARTICLES & PLURALIZATION
    is_plural = False
    special_plural = None
    has_proper_name = False
    is_definite = False
    is_numberless = False

    # LOCATION & INVITEM STATUS
    location = None
    invItem = False

    # ACTION MESSAGES
    cannotTakeMsg = "You cannot take that. "
    empty_msg = None
    default_cannot_add_item_msg = (
        "You cannot put anything {preposition} the {self.verbose_name}. "
    )
    player_exits_msg = (
        "You get {self.contains_preposition_inverse} of the {self.verbose_name}. "
    )

    # VOCABULARY
    adjectives = None
    name = None
    synonyms = None
    full_name = None

    # CAPABILITIES
    # can I do x with this?
    wearable = False
    commodity = True

    # TODO: reevalute how this works
    # should the item take objects given to it? Irrelevant if not Actor
    give = False

    # DESCRIPTION
    description = None
    x_description = None

    def __init__(self, game, name):
        super().__init__(game)

        self.name = name
        self.known_ix = self.ix

        self.child_Things = []
        self.child_Surfaces = []
        self.child_Containers = []
        self.child_UnderSpaces = []
        self.children = []

        self.state_descriptors = []

        self.adjectives = []
        self.synonyms = []

        self.empty_msg = (
            f"The {self.name} has nothing {self.contains_preposition or 'in'} " "it. "
        )

        # add name to list of nouns
        if name in self.game.nouns:
            self.game.nouns[name].append(self)
        else:
            self.game.nouns[name] = [self]

    @property
    def verb_to_be(self):
        if self.is_plural:
            return "are"
        return "is"

    @property
    def plural(self):
        if self.is_plural:
            return self.verbose_name
        if self.special_plural:
            return self.special_plural
        elif (
            self.verbose_name[-1] == "s"
            or self.verbose_name[-1] == "x"
            or self.verbose_name[-1] == "z"
            or self.verbose_name[-2:] == "sh"
            or self.verbose_name[-2:] == "ch"
        ):
            return self.verbose_name + "es"
        else:
            return self.verbose_name + "s"

    @property
    def is_current_player(self):
        return False

    @property
    def verbose_name(self):
        """
        The name that will be printed for descriptions.
        """
        if self.full_name is not None:
            return self.full_name
        return " ".join(self.adjectives + [self.name])

    @property
    def _verbose_name(self):
        """
        Alias for Thing.full_name. To be deprecated.
        """
        return self.full_name

    @_verbose_name.setter
    def _verbose_name(self, value):
        """
        Alias for Thing.full_name. To be deprecated.
        """
        self.full_name = value

    @property
    def default_desc(self):
        """
        The base item description, if a description has not been specified.
        """
        if self.has_proper_name or self.is_definite:
            return f"{self.capNameArticle()} is here. "
        return f"There {self.verb_to_be} {self.lowNameArticle()} here. "

    @property
    def default_xdesc(self):
        """
        The base item examine description, if an x_description has not been specified.
        """
        return f"You notice nothing remarkable about {self.lowNameArticle(True)}. "

    @property
    def desc(self):
        """
        The item description that will be used in room descriptions.
        """
        return (
            (self.description if self.description is not None else self.default_desc)
            + self.state_desc
            + self.composite_desc
            + (self.contains_desc if self.desc_reveal else "")
        )

    @property
    def xdesc(self):
        """
        The item description that will be used for examine.
        """
        return (
            (
                self.x_description
                if self.x_description is not None
                else self.default_xdesc
            )
            + self.state_desc
            + self.composite_desc
            + (self.contains_desc if self.xdesc_reveal else "")
        )

    @property
    def state_desc(self):
        """
        Describe an item's state, with aspects such as open/closed or on/off
        """
        return "".join([getattr(self, key) for key in self.state_descriptors])

    @property
    def component_desc(self):
        """
        How the item is described when it is a component of another item
        """
        return self.desc

    @property
    def composite_desc(self):
        """
        Describe the composite parts (children) of the item
        """
        if not self.children:
            return ""

        return (
            self.children_desc
            or "".join([child.component_desc for child in self.children]) + " "
        )

    @property
    def contains_desc(self):
        """
        Describe the contents of an item
        """
        if not self.contains:
            return ""

        desc = (
            f"{self.contains_preposition.capitalize()} {self.lowNameArticle(True)} is "
        )
        item_phrases = []
        # filter out composite child items
        contains = {
            ix: sublist
            for ix, sublist in self.contains.items()
            if not (sublist[0].parent_obj and sublist[0].parent_obj.ix in self.contains)
        }
        for key, sublist in contains.items():
            item_phrases.append(
                sublist[0].lowNameArticle()
                if len(sublist) == 1
                else (str(len(sublist)) + sublist[0].plural)
            )

        item_phrases[-1] += ". "

        if len(item_phrases) > 1:
            for i in range(0, len(item_phrases) - 2):
                item_phrases[i] += ","
            item_phrases[-2] += " and"

        return desc + " ".join(item_phrases)

    def makeKnown(self, me):
        if self.known_ix and (not self.known_ix in me.knows_about):
            me.knows_about.append(self.known_ix)

    def addSynonym(self, word):
        """Adds a synonym (noun) that can be used to refer to a Thing
        Takes argument word, a string, which should be a single noun """
        self.synonyms.append(word)
        if word in self.game.nouns:
            if self not in self.game.nouns[word]:
                self.game.nouns[word].append(self)
        else:
            self.game.nouns[word] = [self]

    def removeSynonym(self, word):
        """Adds a synonym (noun) that can be used to refer to a Thing
        Takes argument word, a string, which should be a single noun """
        if word in self.synonyms:
            self.synonyms.remove(word)
        if word in self.game.nouns:
            if self in self.game.nouns[word]:
                self.game.nouns[word].remove(self)
            if self.game.nouns[word] == []:
                del self.game.nouns[word]

    def setAdjectives(self, adj_list):
        """Sets adjectives for a Thing
        Takes arguments adj_list, a list of one word strings (adjectives), and update_desc, a Boolean defaulting to True
        Game creators should set update_desc to False if using a custom desc or xdesc for a Thing """
        self.adjectives = adj_list

    def capNameArticle(self, definite=False):
        out = self.getArticle(definite) + self.verbose_name
        first = out[0].upper()
        out = first + out[1:]
        return out

    def lowNameArticle(self, definite=False):
        return self.getArticle(definite) + self.verbose_name

    def getArticle(self, definite=False):
        """
        Gets the correct article for a Thing
        Takes argument definite (defaults to False), which specifies whether the
        article is definite
        Returns a string
        """
        if self.has_proper_name:
            return ""
        elif definite or self.is_definite:
            return "the "
        elif self.is_numberless or self.is_plural:
            return ""
        else:
            if self.verbose_name[0] in ["a", "e", "i", "o", "u"]:
                return "an "
            else:
                return "a "

    def moveTo(self, location):
        """
        Move an item to a new location
        """
        if self.location:
            self.location.removeThing(self)
        location.addThing(self)

    def makeUnique(self):
        """Make a Thing unique (use definite article)
        Creators should use a Thing's makeUnique method rather than setting its definite property directly """
        self.is_definite = True

    def copyThing(self):
        """
        Copy a Thing, keeping the index of the original.
        Safe to use for dynamic item duplication.
        """
        out = copy.copy(self)
        self.game.nouns[out.name].append(out)
        out.setAdjectives(out.adjectives)
        for synonym in out.synonyms:
            self.game.nouns[synonym].append(out)
        out.full_name = self.full_name
        out.contains = {}
        return out

    def copyThingUniqueIx(self):
        """
        Copy a Thing, creating a new index. NOT safe to use for dynamic item duplication.
        The copy object is by default treated as not distinct from the original in
        Player knowledge (me.knows_about dictionary).
        To override this behaviour, manually set the copy's known_ix to its own ix property.
        """
        out = copy.copy(self)
        self.registerNewIndex()
        self.game.nouns[out.name].append(out)
        out.setAdjectives(out.adjectives)
        for synonym in out.synonyms:
            self.game.nouns[synonym].append(out)
        out.full_name = self.full_name
        out.contains = {}
        return out

    def setFromPrototype(self, item):
        if not isinstance(item, Thing):
            print(
                "Error: "
                + self.verbose_name
                + " cannot set attributes from non Thing prototype"
            )
            return False
        else:
            if self.name in self.game.nouns:
                if self in self.game.nouns[self.name]:
                    self.game.nouns[self.name].remove(self)
                    if self.game.nouns[self.name] == []:
                        del self.game.nouns[self.name]
            for synonym in self.synonyms:
                if self in self.game.nouns[synonym]:
                    if self in self.game.nouns[synonym]:
                        self.game.nouns[synonym].remove(self)
                        if self.game.nouns[synonym] == []:
                            del self.game.nouns[synonym]
            for attr, value in item.__dict__.items():
                if attr != "ix":
                    setattr(self, attr, value)
            if self.name in self.game.nouns:
                self.game.nouns[self.name].append(self)
            else:
                self.game.nouns[self.name] = [self]
            for synonym in self.synonyms:
                if synonym in self.game.nouns:
                    self.game.nouns[synonym].append(self)
                else:
                    self.game.nouns[synonym] = [self]
            return True

    def describeThing(self, description):
        self.description = description

    def xdescribeThing(self, description):
        self.x_description = description

    def addComposite(self, item):
        self.is_composite = True
        item.parent_obj = self

        self.children.append(item)
        if item.contains_on:
            self.child_Surfaces.append(item)
        elif item.contains_in:
            self.child_Containers.append(item)
        elif item.contains_under:
            self.child_UnderSpaces.append(item)
        elif isinstance(item, Thing):
            self.child_Things.append(item)

        if self.location:
            self.location.addThing(item)
        item.invItem = False
        item.cannotTakeMsg = (
            item.capNameArticle(True)
            + " is attached to "
            + self.lowNameArticle(True)
            + ". "
        )
        self.containsListUpdate()

    def containsListUpdate(self):
        pass

    def describeChildren(self, description):
        self.children_desc = description
        self.containsListUpdate()

    def containsLiquid(self):
        """Returns the first liquid found in the `contains`, or None"""
        for key in self.contains:
            for item in self.contains[key]:
                if getattr(item, "liquid_type", None):
                    return item
        return None

    def liquidRoomLeft(self):
        """Returns the portion of the Container's size not taken up by a liquid"""
        liquid = self.containsLiquid()
        if not liquid:
            return self.size
        return self.size - liquid.size

    def playerAboutToMoveTo(self, item, event="turn", **kwargs):
        """
        The preparations we make when the player tries to move this item to another item.
        Returns True to allow the moveTo, else False.

        :param item: the item the player is trying to add this Thing into
        :type item: Thing
        :rtype: bool
        """
        if self.parent_obj:
            self.game.addTextToEvent(
                event,
                f"{self.capNameArticle(True)} is attached to "
                f"{self.parent_obj.lowNameArticle(True)}.",
            )
            return False
        return True

    def playerMovesTo(self, item, event="turn", **kwargs):
        """
        The result of a player trying to add this item to some other item's contains.
        Returns True if this can be done, otherwise, prints a rejection message for
        the player, and returns False.

        :param item: the item the player is trying to add this Thing into
        :type item: Thing
        :rtype: bool
        """
        self.moveTo(item)
        return True

    def playerLooksUnder(self, event="turn", **kwargs):
        """
        The result of the player trying to look under this item

        :param event: the key of the event to print text to
        :type event: str
        :rtype: bool
        """
        if self.invItem:
            if not self.playerAboutToTake(event=event):
                return False
            self.playerTakes(event=event)
            self.game.addTextToEvent(event, "You find nothing underneath. ")
            return True
        self.game.addTextToEvent(
            event, f"There's no reason to look under {self.lowNameArticle(True)}. ",
        )
        return False

    def implicitAddItemToChild(self, item, preposition, event="turn", **kwargs):
        """
        Try to interpret the player's instruction to add an item to this item, as an
        instruction to add an item to a *component* of this item.

        For example, we might try interpreting "put bead in night table" as an attempt
        to put the bead in the *drawer* of the night table.

        :param item: the item to attempt to add
        :type item: Thing
        :param preposition: the contains preposition (on, in, under, etc.) to search
            for in the child items
        :type preposition: str
        """
        matching_children = [
            c for c in self.children if c.contains_preposition == preposition
        ]
        if not matching_children:
            return False
        success = matching_children[0].playerAddsItem(item, preposition)
        if success:
            return True

    def playerAboutToAddItem(self, item, preposition, event="turn", **kwargs):
        """
        The prepartations we make when the player is about to try to add an item
        to this item. Performs any implicit actions needed to add the item.
        Returns True if the item addition is allowed, False otherwise.
        :param item: the item to attempt to add
        :type item: Thing
        :param preposition: the contains preposition the player wants to add the item with
            (in/on/etc.)
        :type preposition: str
        """
        matching_children = [
            c for c in self.children if c.contains_preposition == preposition
        ]
        if len(matching_children) == 1:
            if not item.playerAboutToMoveTo(matching_children[0], event=event):
                return False
            return True

        if not item.playerAboutToMoveTo(self, event=event):
            return False

        if self is self.game.me.getOutermostLocation().floor:
            return True

        self.game.addText(
            self.default_cannot_add_item_msg.format(self=self, preposition=preposition)
        )
        return False

    def playerAddsItem(
        self, item, preposition, event="turn", success_msg=None, **kwargs
    ):
        """
        The result of a player trying to add an item to this item's contents.
        For base Things, first checks if we are the floor, and if so, moves the item to
        the outer Room, otherwise tries to find an appropriate child item to add to.

        Returns True on success, else False.

        :param item: the item to attempt to add
        :type item: Thing
        :param preposition: the contains preposition the player wants to add the item with
            (in/on/etc.)
        :type preposition: str
        """
        outer_loc = self.game.me.getOutermostLocation()
        if self is outer_loc.floor:
            if success_msg:
                self.game.addTextToEvent(event, success_msg)
            item.moveTo(outer_loc)
            return True

        return self.implicitAddItemToChild(item, preposition)

    def playerDumpsItems(
        self,
        into_location=None,
        success_msg=None,
        event="turn",
        preposition="in",
        **kwargs,
    ):
        """
        The result of a player trying to dump the items.

        Returns True on success, else False.

        :param into_location: the location to dump items into
        :type into_location: Thing
        """
        if not self.topLevelContentsList:
            self.game.addText(self.empty_msg)
            return False

        can_move = False
        if into_location:
            for t in self.topLevelContentsList:
                if into_location.playerAboutToAddItem(
                    t, preposition, event=event, **kwargs
                ):
                    can_move = True
        else:
            can_move = True

        if not can_move:
            return False

        if success_msg:
            self.game.addTextToEvent(event, success_msg)

        success = False

        if into_location:
            for t in self.topLevelContentsList:
                if into_location.playerAddsItem(t, preposition, event=event, **kwargs):
                    success = True
        else:
            for t in self.topLevelContentsList:
                # TODO: implement Room/PhysicalEntity playerAddsItem instead
                t.moveTo(self.game.me.location)
                success = True

        if not success:
            return False

        return True

    def playerAboutToTake(self, event="turn", **kwargs):
        """
        Actions carried out when the player is about to try and take this item.

        :param event: the event name to print to
        :type event: str
        """
        if not self.invItem or self.parent_obj:
            self.game.addTextToEvent(event, self.cannotTakeMsg)
            return False
        if self.game.me.topLevelContainsItem(self):
            self.game.addTextToEvent(
                event, f"You already have {self.lowNameArticle(True)}. "
            )
            return False
        if self.containsItem(self.game.me):
            self.game.addTextToEvent(
                event, f"(First trying to leave {self.lowNameArticle(True)})"
            )
            if not self.playerExits(event=event):
                return False
        if not self.location.playerAboutToRemoveItem(self):
            return False
        return True

    def playerTakes(self, event="turn", **kwargs):
        """
        The result of the player taking this item.

        :param event: the event name to print to
        :type event: str
        """
        if self.game.me.containsItem(self) and not self.game.me.topLevelContainsItem(
            self
        ):
            self.game.addTextToEvent(
                event,
                f"You remove {self.lowNameArticle(True)} from "
                f"{self.location.lowNameArticle(True)}. ",
            )
        else:
            self.game.addTextToEvent(event, f"You take {self.lowNameArticle(True)}. ")
        self.moveTo(self.game.me)

        for c in self.children:
            c.playerTakesParentObject(event=event)
        return True

    def playerTakesParentObject(self, event="turn", **kwargs):
        """
        The result of the player taking the composite parent of this item.
        :param event: the event name to print to
        :type event: str
        """
        return True

    def playerAboutToGiveAway(self, event="turn", **kwargs):
        """
        Evaluated when the player is about to try to give this item away.

        :param event: the key for the event to print text to
        :type event: str
        """
        return True

    def playerExits(self, event="turn", **kwargs):
        """
        The result of the player leaving this item.
        Returns True if the player is not contained by this item at the time of completion,
        i.e, if the player has successfully left, or was not inside to begin with.

        :param event: the event name to print to
        :type event: str
        """
        if not self.containsItem(self.game.me):
            f"You are not {self.contains_preposition} {self.lowNameArticle(True)}. "
            return True

        while self.containsItem(self.game.me.location):
            if not self.game.me.location.playerExits(event=event):
                return False

        # TODO: implement Room/PhysicalEntity playerAddsItem instead?
        self.game.addTextToEvent(event, self.player_exits_msg.format(self=self))
        self.game.me.moveTo(self.location)
        return True

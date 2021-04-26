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
    invItem = True

    # ACTION MESSAGES
    cannotTakeMsg = "You cannot take that."

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

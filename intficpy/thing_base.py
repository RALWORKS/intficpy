import copy

from .physical_entity import PhysicalEntity
from .vocab import nounDict

##############################################################
# THING_BASE.PY - the Thing class for IntFicPy
# Defines the Thing class, and the thing dictionary
##############################################################


class Thing(PhysicalEntity):
    """Thing is the overarching class for all items that exist in the game """

    def __init__(self, name):
        super().__init__()

        self.known_ix = self.ix
        self.ignore_if_ambiguous = False
        self.cannot_interact_msg = None

        # TRAVELCONNECTOR FACE
        self.twin = None
        self.connection = None
        self.direction = None

        # CONTENTS
        # contain type flags
        self.contains_on = False
        self.contains_in = False
        self.contains_under = False
        # is valid Player location?
        self.canSit = False
        self.canStand = False
        self.canLie = False
        # language
        # TODO: these should default to in/out (out of?) to eliminate the null check
        self.contains_preposition = "on"
        self.contains_preposition_inverse = "off"
        self.revealed = False
        self.desc_reveal = True
        self.xdesc_reveal = True

        # COMPOSITE OBJECTS
        self.is_composite = False  # TODO: replace if x.composite with if x.children
        self.parent_obj = None
        self.lock_obj = None
        self.children_desc = None
        # TODO: refactor: duplicate storing of all children seems unnecessary
        self.child_Things = []
        self.child_Surfaces = []
        self.child_Containers = []
        self.child_UnderSpaces = []
        self.children = []

        # OPEN/CLOSE
        self.has_lid = False
        self.is_open = False

        # STATES
        self.state_descriptors = []

        # thing properties
        self.far_away = False

        self.size = 50

        # ARTICLES & PLURALIZATION
        self.isPlural = False
        self.special_plural = False
        self.hasArticle = True
        self.isDefinite = False
        self.is_numberless = False

        # LOCATION & INVITEM STATUS
        self.location = False
        self.invItem = True

        # ACTION MESSAGES
        self.cannotTakeMsg = "You cannot take that."

        # VOCABULARY
        self.adjectives = []
        self.name = name
        self.synonyms = []
        self.manual_update = False
        # verbose name will be updated when adjectives are added
        self.verbose_name = name

        # CAPABILITIES
        # can I do x with this?
        self.wearable = False
        self.commodity = True

        # TODO: reevalute how this works
        # should the item take objects given to it? Irrelevant if not Actor
        self.give = False

        # DESCRIPTION
        self.description = None
        self.x_description = None

        # add name to list of nouns
        if name in nounDict:
            nounDict[name].append(self)
        else:
            nounDict[name] = [self]

    @property
    def default_desc(self):
        """
        The base item description, if a description has not been specified.
        """
        if not self.hasArticle or self.isDefinite:
            return f"{self.capNameArticle()} is here. "
        return f"There is {self.lowNameArticle()} here. "

    @property
    def default_xdesc(self):
        """
        The base item examin description, if an x_description has not been specified.
        """
        return f"You notice nothing remarkable about {self.lowNameArticle(True)}. "

    @property
    def desc(self):
        """
        The item description that will be used in room descriptions.
        """
        return (
            (self.description or self.default_desc)
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
            (self.x_description or self.default_xdesc)
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
                else (str(len(sublist)) + sublist[0].getPlural())
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

    def containsItem(self, item):
        """Returns True if item is in the Thing's contains or sub_contains dictionary """
        if item.ix in self.contains:
            if item in self.contains[item.ix]:
                return True
        if item.ix in self.sub_contains:
            if item in self.sub_contains[item.ix]:
                return True
        return False

    def strictContainsItem(self, item):
        """Returns True only if item is in the Thing's contains dictionary (top level)"""
        if item.ix in self.contains:
            if item in self.contains[item.ix]:
                return True
        return False

    def addSynonym(self, word):
        """Adds a synonym (noun) that can be used to refer to a Thing
		Takes argument word, a string, which should be a single noun """
        self.synonyms.append(word)
        if word in nounDict:
            if self not in nounDict[word]:
                nounDict[word].append(self)
        else:
            nounDict[word] = [self]

    def removeSynonym(self, word):
        """Adds a synonym (noun) that can be used to refer to a Thing
		Takes argument word, a string, which should be a single noun """
        if word in self.synonyms:
            self.synonyms.remove(word)
        if word in nounDict:
            if self in nounDict[word]:
                nounDict[word].remove(self)
            if nounDict[word] == []:
                del nounDict[word]

    def setAdjectives(self, adj_list):
        """Sets adjectives for a Thing
		Takes arguments adj_list, a list of one word strings (adjectives), and update_desc, a Boolean defaulting to True
		Game creators should set update_desc to False if using a custom desc or xdesc for a Thing """
        self.adjectives = adj_list
        self.verbose_name = " ".join(adj_list) + " " + self.name

    def capNameArticle(self, definite=False):
        out = self.getArticle(definite) + self.verbose_name
        first = out[0].upper()
        out = first + out[1:]
        return out

    def lowNameArticle(self, definite=False):
        return self.getArticle(definite) + self.verbose_name

    def getArticle(self, definite=False):
        """Gets the correct article for a Thing
		Takes argument definite (defaults to False), which specifies whether the article is definite
		Returns a string """
        if not self.hasArticle:
            return ""
        elif definite or self.isDefinite:
            return "the "
        else:
            if self.verbose_name[0] in ["a", "e", "i", "o", "u"]:
                return "an "
            else:
                return "a "

    def getPlural(self):
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

    def makeUnique(self):
        """Make a Thing unique (use definite article)
		Creators should use a Thing's makeUnique method rather than setting its definite property directly """
        self.isDefinite = True

    def copyThing(self):
        """
        Copy a Thing, keeping the index of the original.
        Safe to use for dynamic item duplication.
        """
        out = copy.copy(self)
        nounDict[out.name].append(out)
        out.setAdjectives(out.adjectives)
        for synonym in out.synonyms:
            nounDict[synonym].append(out)
        out.verbose_name = self.verbose_name
        out.contains = {}
        out.sub_contains = {}
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
        nounDict[out.name].append(out)
        out.setAdjectives(out.adjectives)
        for synonym in out.synonyms:
            nounDict[synonym].append(out)
        out.verbose_name = self.verbose_name
        out.contains = {}
        out.sub_contains = {}
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
            if self.name in nounDict:
                if self in nounDict[self.name]:
                    nounDict[self.name].remove(self)
                    if nounDict[self.name] == []:
                        del nounDict[self.name]
            for synonym in self.synonyms:
                if self in nounDict[synonym]:
                    if self in nounDict[synonym]:
                        nounDict[synonym].remove(self)
                        if nounDict[synonym] == []:
                            del nounDict[synonym]
            for attr, value in item.__dict__.items():
                if attr != "ix":
                    setattr(self, attr, value)
            if self.name in nounDict:
                nounDict[self.name].append(self)
            else:
                nounDict[self.name] = [self]
            for synonym in self.synonyms:
                if synonym in nounDict:
                    nounDict[synonym].append(self)
                else:
                    nounDict[synonym] = [self]
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

    def getNested(self):
        """
        Find revealed nested Things
        """
        # list to populate with found Things
        nested = []
        # iterate through top level contents
        if self.has_lid and not self.is_open:
            return []
        for key in self.contains:
            for item in self.contains[key]:
                nested.append(item)
        for key in self.sub_contains:
            for item in self.sub_contains[key]:
                nested.append(item)
        return nested

from .ifp_object import IFPObject


class PhysicalEntity(IFPObject):
    def __init__(self, game):
        super().__init__(game)

        self.location = None

        # CONTENTS
        self.contains = {}
        self.revealed = True

    def containsItem(self, item):
        """Returns True if item is in the contains or sub_contains dictionary """
        return self.topLevelContainsItem(item) or self.subLevelContainsItem(item)

    def topLevelContainsItem(self, item):
        if item.ix in self.contains:
            if item in self.contains[item.ix]:
                return True
        return False

    def subLevelContainsItem(self, item):
        if item.ix in self.sub_contains:
            if item in self.sub_contains[item.ix]:
                return True
        return False

    def addThing(self, item):
        if item.lock_obj and not self.containsItem(item.lock_obj):
            self.addTopLevelContains(item.lock_obj)

        for child in item.children:
            if not self.containsItem(child):
                self.addTopLevelContains(child)

        # top level item
        self.addTopLevelContains(item)

        return True

    def addTopLevelContains(self, item):
        if item.ix in self.contains:
            self.contains[item.ix].append(item)
        else:
            self.contains[item.ix] = [item]
        item.location = self

    def removeThing(self, item):
        if not self.containsItem(item):
            return False  # might be better to raise here
        if item.lock_obj and self.containsItem(item.lock_obj):
            self.removeContains(item.lock_obj)

        for child in item.children:
            if self.containsItem(child):
                self.removeContains(child)

        self.removeContains(item)

        if not self.location:
            return True

        return True

    def removeContains(self, item):
        ret = False  # we have not removed anything yet
        loc = self

        if self.topLevelContainsItem(item):
            self.contains[item.ix].remove(item)
            if not self.contains[item.ix]:
                del self.contains[item.ix]
            item.location = None
            return True

        if self.subLevelContainsItem(item):
            return item.location.removeThing(item)

        return False

    def getOutermostLocation(self):
        if self.location is self:
            return self
        x = self.location
        if not x:
            return self.location
        while x.location:
            x = x.location
        return x

    def getNested(self):
        """
        Find revealed nested Things
        """
        # list to populate with found Things
        nested = []
        # iterate through top level contents
        if not self.revealed:
            return []
        for key in self.contains:
            for item in self.contains[key]:
                nested.append(item)
        for key in self.sub_contains:
            for item in self.sub_contains[key]:
                nested.append(item)
        return nested

    def playerAboutToRemoveItem(self, item, event="turn", **kwargs):
        """
        Actions carried out when the player is about to try and remove an item contained
        by this item.

        :param event: the event name to print to
        :type event: str
        """
        return True

    @property
    def visible_nested_contents(self):
        if not self.revealed:
            return []
        ret = self.topLevelContentsList
        for item in self.topLevelContentsList:
            ret += item.visible_nested_contents
        return ret

    @property
    def sub_contains(self):
        ret = {}
        for item in self.topLevelContentsList:
            flat = item.visible_nested_contents
            for sub in flat:
                if sub.ix in ret:
                    ret[sub.ix].append(sub)
                else:
                    ret[sub.ix] = [sub]
        return ret

    @property
    def topLevelContentsList(self):
        """
        Return the top level contents as a flattened list

        :rtype: list
        """
        return [item for ix, sublist in self.contains.items() for item in sublist]

    @property
    def subLevelContentsList(self):
        """
        Return the sub contents as a flattened list

        :rtype: list
        """
        return [item for ix, sublist in self.sub_contains.items() for item in sublist]

    @property
    def contentsList(self):
        """
        Return the contents from contains and sub_contains as a flattened list

        :rtype: list
        """
        return self.topLevelContentsList + self.subLevelContentsList

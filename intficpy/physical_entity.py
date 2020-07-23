from .ifp_object import IFPObject


class PhysicalEntity(IFPObject):
    def __init__(self):
        super().__init__()

        self.location = None

        # CONTENTS
        self.contains = {}
        self.sub_contains = {}

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

        # nested items
        item_nested = item.getNested()
        for t in item_nested:
            self.addSubLevelContains(t)
        # top level item
        item.location = self
        self.addTopLevelContains(item)

        if not self.location:
            return True

        self_nested = self.getNested()
        for t in self_nested:
            self.location.addSubLevelContains(t)

        return True

    def addTopLevelContains(self, item):
        if item.ix in self.contains:
            self.contains[item.ix].append(item)
        else:
            self.contains[item.ix] = [item]
        item.location = self

    def addSubLevelContains(self, item):
        if item.ix in self.sub_contains:
            self.sub_contains[item.ix].append(item)
        else:
            self.sub_contains[item.ix] = [item]

    def removeThing(self, item):
        if not self.containsItem(item):
            return False  # might be better to raise here
        if item.lock_obj and self.containsItem(item.lock_obj):
            self.removeContains(item.lock_obj)

        for child in item.children:
            if self.containsItem(child):
                self.removeContains(child)

        # nested items
        nested = item.getNested()
        for t in nested:
            if self.containsItem(t):
                self.removeContains(t)

        self.removeContains(item)

        if not self.location:
            return

        self_nested = self.getNested()
        for t in self_nested:
            self.location.removeContains(t)

        return True

    def removeContains(self, item):
        if self.topLevelContainsItem(item):
            self.contains[item.ix].remove(item)
            if not self.contains[item.ix]:
                del self.contains[item.ix]
            item.location = None
            return True

        if self.subLevelContainsItem(item):
            self.sub_contains[item.ix].remove(item)
            if not self.sub_contains[item.ix]:
                del self.sub_contains[item.ix]
            return True

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

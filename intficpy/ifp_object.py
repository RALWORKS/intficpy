class IFPObject:
    instances = {}
    _ix_iteration = 0

    def __init__(self):
        self.registerNewIndex()
        self.is_top_level_location = False

    def registerNewIndex(self):
        ix = f"{type(self).__name__}__{IFPObject._ix_iteration}"
        self.ix = ix
        IFPObject._ix_iteration += 1
        self.instances[ix] = self

class ObjMap:
    def __init__(self, prefix):
        self.dict = {}
        self.ix = 0
        self.prefix = prefix

    def addEntry(self, obj):
        ix = self.prefix + str(self.ix)
        obj.ix = ix
        self.ix += 1
        self.dict[ix] = obj
        obj.obj_map = self


connectors = ObjMap("connector")
rooms = ObjMap("room")
achievements = ObjMap("achievement")
hintnodes = ObjMap("hintnode")
actors = ObjMap("actor")
topics = ObjMap("topic")
things = ObjMap("thing")

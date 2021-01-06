class IFPObject:
    def __init__(self, game):
        self.game = game
        self.registerNewIndex()
        self.is_top_level_location = False

    def registerNewIndex(self):
        ix = f"{type(self).__name__}__{self.game.next_obj_ix}"
        self.ix = ix
        self.game.next_obj_ix += 1
        self.game.ifp_objects[ix] = self

class RunEvery:
    """Class of daemons, an object containing creator-defined functions to be evaluated every turn """

    def __init__(self):
        self.funcs = []

    def runAll(self, me, app):
        for func in self.funcs:
            func(me, app)

    def add(self, daemon):
        self.funcs.append(daemon)

    def remove(self, daemon):
        if daemon in self.funcs:
            self.funcs.remove(daemon)


daemons = RunEvery()

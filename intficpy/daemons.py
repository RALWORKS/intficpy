from intficpy.ifp_object import IFPObject


class DaemonManager(IFPObject):
    def __init__(self):
        super().__init__()
        self.active = []

    def runAll(self, me, app):
        for daemon in self.active:
            daemon.func(me, app)

    def add(self, daemon):
        self.active.append(daemon)
        daemon.onAdd()

    def remove(self, daemon):
        if daemon in self.active:
            self.active.remove(daemon)
            daemon.onRemove()


daemons = DaemonManager()


class Daemon(IFPObject):
    """
    While active, a Daemon's func is run every turn.
    Properties added to a Daemon object will be saved/loaded, provided they are
    serializable, and can be added so a Daemon can track its own state.
    """

    def __init__(self, func):
        super().__init__()
        self.func = func

    def onRemove(self):
        pass

    def onAdd(self):
        pass

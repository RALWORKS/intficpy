from unittest import TestCase

class TestApp:
    def __init__(self):
        pass

    def printToGUI(self, msg, *args):
        print(f"APP PRINT: {msg}")

class IFPTestCase(TestCase):
    def setUp(self):
        self.app = TestApp()
        self.me = Player("me")
        self.start_room = Room("room", "desc")
        self.start_room.addThing(self.me)
        self.me.setPlayer()

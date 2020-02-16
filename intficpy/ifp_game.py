from .parser import Parser
from .daemons import DaemonManager
from .vocab import verbDict
from .event import IFPEvent


class GameInfo:
    def __init__(self):
        self.title = "IntFicPy Game"
        self.author = "Unnamed"
        self.basic_instructions = (
            "This is a parser-based game, which means the user interacts by typing "
            "commands. <br><br>A command should be a simple sentence, starting with a "
            "verb, for instance, <br>> JUMP<br>> TAKE UMBRELLA<br>> TURN DIAL TO 7"
            "<br><br>The parser is case insensitive, and ignores punctuation and "
            "articles (a, an, the). <br><br>It can be difficult at times to figure out "
            "the correct verb to perform an action. Even once you have the correct "
            "verb, it can be hard to get the right phrasing. In these situations, you "
            "can view the full list of verbs in the game using the VERBS command. You "
            "can also view the accepted phrasings for a specific verb with the VERB "
            "HELP command (for instance, type VERB HELP WEAR).<br><br>This game does "
            "not have quit and restart commands. To quit, simply close the program. "
            "To restart, open it again.<br><br>Typing SAVE will open a dialogue to "
            "create a save file. Typing LOAD will allow you to select a save file to "
            "restore. "
        )
        self.game_instructions = None
        self.intFicPyCredit = True
        self.desc = None
        self.showVerbs = True
        self.betaTesterCredit = None
        self.customMsg = None
        self.verbs = [
            verb.list_word
            for name, verblist in verbDict.items()
            for verb in verblist
            if verb.list_by_default
        ]
        self.verbs = sorted(set(self.verbs))
        self.discovered_verbs = []
        self.help_msg = None

    def setInfo(self, title, author):
        self.title = title
        self.author = author

    def printAbout(self, app):
        if self.customMsg:
            addTextToEvent("turn", self.customMsg)
        else:
            addTextToEvent("turn", "<b>" + self.title + "</b>")
            addTextToEvent("turn", "<b>Created by " + self.author + "</b>")
            if self.intFicPyCredit:
                addTextToEvent("turn", "Built with JSMaika's IntFicPy parser")
            if self.desc:
                addTextToEvent("turn", self.desc)
            if self.betaTesterCredit:
                addTextToEvent("turn", "<b>Beta Testing Credits</b>")
                addTextToEvent("turn", self.betaTesterCredit)

    def printInstructions(self, app):
        addTextToEvent("turn", "<b>Basic Instructions</b>")
        addTextToEvent("turn", self.basic_instructions)
        if self.game_instructions:
            addTextToEvent("turn", "<b>Game Instructions</b>")
            addTextToEvent("turn", self.game_instructions)

    def printHelp(self, app):
        if self.help_msg:
            addTextToEvent("turn", self.help_msg)
        # self.printVerbs(app)
        addTextToEvent(
            "turn",
            "Type INSTRUCTIONS for game instructions, or VERBS for a full list of accepted verbs. ",
        )

    def printVerbs(self, app):
        addTextToEvent("turn", "<b>This game accepts the following basic verbs: </b>")
        verb_list = ""
        for verb in self.verbs:
            verb_list = verb_list + verb
            if verb != self.verbs[-1]:
                verb_list = verb_list + ", "
        addTextToEvent("turn", verb_list)
        if len(self.discovered_verbs) > 0:
            addTextToEvent(
                "turn", "<b>You have discovered the following additional verbs: </b>"
            )
            d_verb_list = ""
            for verb in self.discovered_verbs:
                verb_list = verb_list + verb
                if verb != self.verbs[-1]:
                    d_verb_list = d_verb_list + ", "
            addTextToEvent("turn", d_verb_list)
        addTextToEvent(
            "turn",
            'For help with phrasing, type "verb help" followed by a verb for a '
            "complete list of acceptable sentence structures for that verb. This will "
            "work for any verb, regardless of whether it has been discovered. ",
        )


class TurnInfo:
    """Class of lastTurn, used for disambiguation mode """

    def __init__(self):
        self.things = []
        self.ambiguous = False
        self.err = False
        self.verb = False
        self.dobj = False
        self.iobj = False
        self.ambig_noun = None
        self.find_by_loc = False
        self.turn_list = []
        self.back = 0
        self.gameOpening = False
        self.gameEnding = False
        self.convNode = False
        self.specialTopics = {}
        self.recfile = None
        self.turn_list = []

    def recordOn(self, f):
        try:
            self.recfile = open(f, "w+")
            return True
        except:
            return False

    def recordOff(self):
        if not self.recfile:
            return
        self.recfile.close()


class IFPGame:
    def __init__(self, me, app):
        self.app = app
        app.game = self
        self.me = me
        self.parser = Parser(self)
        self.lastTurn = TurnInfo()
        self.aboutGame = GameInfo()
        self.daemons = DaemonManager()
        self.next_events = {}

        self.turn_event_style = None
        self.command_event_style = None

    def runTurnEvents(self):
        events = sorted(
            [event for name, event in self.next_events.items()],
            key=lambda x: x.priority,
        )
        for event in events:
            self.app.printEventText(event)
        self.next_events.clear()
        self.addEvent("turn", 5, style=self.turn_event_style)

    def initGame(self):
        self.addEvent("turn", 5, style=self.turn_event_style)
        if self.lastTurn.gameOpening:
            self.lastTurn.gameOpening(self)
        self.parser.roomDescribe()
        self.daemons.runAll(self)
        self.runTurnEvents()

    def addEvent(self, name, priority, text=None, style=None):
        """
        Add an event to the current turn

        Raises ValueError if an event of the specified name is already defined
        for this turn
        """
        if name in self.next_events:
            raise ValueError(
                f"Cannot add event with name '{name}': "
                "Name is already used for current turn."
            )
        self.next_events[name] = IFPEvent(self, priority, text, style)

    def addTextToEvent(self, name, text):
        """
        Add text to an event in the current turn

        Raises KeyError if the specified event name is not defined for this
        turn
        """
        if not name in self.next_events:
            raise KeyError(
                f"Event with name '{name}' does not yet exist in current turn. "
            )
        self.next_events[name].text.append(text)

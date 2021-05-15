from .parser import Parser
from .daemons import DaemonManager
from .score import AbstractScore, HintSystem
from .event import IFPEvent
from .verb import get_base_verbset


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
        self.help_msg = None

    def setInfo(self, title, author):
        self.title = title
        self.author = author

    def printAbout(self, game):
        if self.customMsg:
            game.addTextToEvent("turn", self.customMsg)
        else:
            game.addTextToEvent("turn", "<b>" + self.title + "</b>")
            game.addTextToEvent("turn", "<b>Created by " + self.author + "</b>")
            if self.intFicPyCredit:
                game.addTextToEvent("turn", "Built with JSMaika's IntFicPy parser")
            if self.desc:
                game.addTextToEvent("turn", self.desc)
            if self.betaTesterCredit:
                game.addTextToEvent("turn", "<b>Beta Testing Credits</b>")
                game.addTextToEvent("turn", self.betaTesterCredit)

    def printInstructions(self, game):
        game.addTextToEvent("turn", "<b>Basic Instructions</b>")
        game.addTextToEvent("turn", self.basic_instructions)
        if self.game_instructions:
            game.addTextToEvent("turn", "<b>Game Instructions</b>")
            game.addTextToEvent("turn", self.game_instructions)

    def printHelp(self, game):
        if self.help_msg:
            game.addTextToEvent("turn", self.help_msg)
        # self.printVerbs(app)
        game.addTextToEvent(
            "turn",
            "Type INSTRUCTIONS for game instructions, or VERBS for a full list of accepted verbs. ",
        )

    def printVerbs(self, game):
        game.addTextToEvent(
            "turn", "<b>This game accepts the following basic verbs: </b>"
        )
        verb_list = sorted(
            set(
                [
                    verb.list_word or verb.word
                    for name, verblist in game.verbs.items()
                    for verb in verblist
                    if verb.list_by_default
                ]
            )
        )

        joined_verb_list = ", ".join(verb_list) + "."

        game.addTextToEvent("turn", joined_verb_list)

        game.addTextToEvent(
            "turn",
            'For help with phrasing, type "verb help" followed by a verb for a '
            "complete list of acceptable sentence structures for that verb. This will "
            "work for any verb, regardless of whether it has been discovered. ",
        )


class IFPGame:
    def __init__(self, app, main="__main__"):
        # Track the game objects and their vocublary
        self.ifp_objects = {}
        self.next_obj_ix = 0
        self.nouns = {}
        self.verbs = get_base_verbset()

        self.app = app
        app.game = self

        self.main = __import__(main)
        self.aboutGame = GameInfo()

        self.daemons = DaemonManager(self)
        self.parser = Parser(self)

        self.ended = False
        self.next_events = {}

        self.turn_event_style = None
        self.command_event_style = None
        self.echo_on = getattr(self.app, "echo_on", True)

        self.recfile = None
        self.turn_list = []
        self.back = 0

        self.score = AbstractScore(self)
        self.hints = HintSystem(self)

    def runTurnEvents(self):
        events = sorted(
            [
                event
                for name, event in self.next_events.items()
                if event.priority is not None
                and event._text
                and not ((not self.echo_on) and name == "command")
            ],
            key=lambda x: x.priority,
        )
        for event in events:
            self.app.printEventText(event)
        self.next_events.clear()
        self.addEvent("turn", 5, style=self.turn_event_style)

    @staticmethod
    def gameOpening(game):
        pass

    def initGame(self):
        from .things import Abstract

        # HACK: trick the parser into recognizing reflexive pronouns as valid nouns
        self.reflexive = Abstract(self, "itself")
        self.reflexive.addSynonym("himself")
        self.reflexive.addSynonym("herself")
        self.reflexive.addSynonym("themself")
        self.reflexive.addSynonym("themselves")
        self.reflexive.makeKnown(self.me)

        self.addEvent("turn", 5, style=self.turn_event_style)
        self.gameOpening(self)
        self.parser.roomDescribe()
        self.daemons.runAll(self)
        self.runTurnEvents()

    def turnMain(self, input_string):
        """
        Sends user input to the parser each turn
        Runs daemons
        Runs turn events
        Takes argument input_string, the cleaned user input string
        """
        if len(input_string) == 0:
            return 0
        # parse string
        self.parser.parseInput(input_string)
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

    def addSubEvent(self, outer_name, name, text=None):
        """
        Add a sub event to an event on the current turn

        Raises ValueError if an event of the specified name is already defined
        for this turn, and KeyError if the outer event is not defined for the
        current turn

        :param outer_name: the name of the event to add the sub event into
        :type outer_name: str
        :param name: the name of the new event (sub event) to add
        :type name: str
        """
        if not outer_name in self.next_events:
            raise KeyError(
                f"Cannot add sub event to outer event '{outer_name}': "
                "Outer event does not exist in the current turn."
            )
        if name in self.next_events:
            raise ValueError(
                f"Cannot add event with name '{name}': "
                "Name is already used for current turn."
            )
        self.next_events[name] = self.next_events[outer_name].addSubEvent(text=text)

    def addTextToEvent(self, name, text):
        """
        Add text to an event in the current turn

        Raises KeyError if the specified event name is not defined for this
        turn
        """
        text = self.parser.replace_string_vars(text)
        if not name in self.next_events:
            raise KeyError(
                f"Event with name '{name}' does not yet exist in current turn. "
            )
        self.next_events[name]._text.append(text)

    def addText(self, text):
        """
        Shortcut to add text to the turn event
        """
        self.addTextToEvent("turn", text)

    def recordOn(self, f):
        """
        Try opening the specified file for recording,
        creating it if it doesn't exist.
        """
        try:
            recfile = open(f, "w+")
            recfile.close()
            self.recfile = f
            return True
        except:
            return False

    def recordOff(self):
        self.recfile = None

    def getCommandUp(self):
        """
        Move backward by 1 through the list of previous commands
        Analogous to pressing the Up key in most terminals
        """
        if len(self.turn_list) < 1:
            return ""
        self.back -= 1
        if -self.back >= len(self.turn_list):
            self.back = 0
        return self.turn_list[self.back]

    def getCommandDown(self):
        """
        Move forward by 1 through the list of previous commands
        Analogous to pressing the Down key in most terminals
        """
        if len(self.turn_list) < 1:
            return ""
        self.back += 1
        if self.back >= len(self.turn_list):
            self.back = 0
        return self.turn_list[self.back]

    def setPlayer(self, player):
        self.me = player
        self.me.setPlayer()

    def addVerb(self, verb):
        for key in [verb.word, *verb.synonyms]:
            if key in self.verbs:
                self.verbs[key].append(verb)
            else:
                self.verbs[key] = [verb]

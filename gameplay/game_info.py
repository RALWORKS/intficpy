class gameInfo:
    def __init__(self):
        self.title = "IntFicPy Game"
        self.author = "Unnamed"
        self.basic_instructions = "This is a parser-based game, which means the user interacts by typing commands. <br><br>A command should be a simple sentence, starting with a verb, for instance, <br>> JUMP<br>> TAKE UMBRELLA<br>> TURN DIAL TO 7<br><br>The parser is case insensitive, and ignores punctuation and articles (a, an, the). <br><br>It can be difficult at times to figure out the correct verb to perform an action. Even once you have the correct verb, it can be hard to get the right phrasing. In these situations, you can view the full list of verbs in the game using the VERBS command. You can also view the accepted phrasings for a specific verb with the VERB HELP command (for instance, type VERB HELP WEAR).<br><br>This game does not have quit and restart commands. To quit, simply close the program. To restart, open it again.<br><br>Typing SAVE will open a dialogue to create a save file. Typing LOAD will allow you to select a save file to restore. "
        self.game_instructions = None
        self.intFicPyCredit = True
        self.desc = None
        self.showVerbs = True
        self.betaTesterCredit = None
        self.customMsg = None
        self.verbs = []
        self.discovered_verbs = []
        self.help_msg = None
        self.main_file = None

    def setInfo(self, title, author):
        self.title = title
        self.author = author

    def printAbout(self, app):
        if self.customMsg:
            app.printToGUI(self.customMsg)
        else:
            app.printToGUI("<b>" + self.title + "</b>")
            app.printToGUI("<b>Created by " + self.author + "</b>")
            if self.intFicPyCredit:
                app.printToGUI("Built with JSMaika's IntFicPy parser")
            if self.desc:
                app.printToGUI(self.desc)
            if self.betaTesterCredit:
                app.printToGUI("<b>Beta Testing Credits</b>")
                app.printToGUI(self.betaTesterCredit)

    def printInstructions(self, app):
        app.printToGUI("<b>Basic Instructions</b>")
        app.printToGUI(self.basic_instructions)
        if self.game_instructions:
            app.printToGUI("<b>Game Instructions</b>")
            app.printToGUI(self.game_instructions)

    def printHelp(self, app):
        if self.help_msg:
            app.printToGUI(self.help_msg)
        # self.printVerbs(app)
        app.printToGUI(
            "Type INSTRUCTIONS for game instructions, or VERBS for a full list of accepted verbs. "
        )

    def printVerbs(self, app):
        app.printToGUI("<b>This game accepts the following basic verbs: </b>")
        self.verbs = sorted(self.verbs)
        verb_list = ""
        for verb in self.verbs:
            verb_list = verb_list + verb
            if verb != self.verbs[-1]:
                verb_list = verb_list + ", "
        app.printToGUI(verb_list)
        if len(self.discovered_verbs) > 0:
            app.printToGUI("<b>You have discovered the following additional verbs: ")
            d_verb_list = ""
            for verb in self.discovered_verbs:
                verb_list = verb_list + verb
                if verb != self.verbs[-1]:
                    d_verb_list = d_verb_list + ", "
            app.printToGUI(d_verb_list)
        app.printToGUI(
            'For help with phrasing, type "verb help" followed by a verb for a complete list of acceptable sentence structures for that verb. This will work for any verb, regardless of whether it has been discovered. '
        )


aboutGame = gameInfo()


class TurnInfo:
    """Class of lastTurn, used for disambiguation mode """

    things = []
    ambiguous = False
    err = False
    verb = False
    dobj = False
    iobj = False
    ambig_noun = None
    find_by_loc = False
    turn_list = []
    back = 0
    gameOpening = False
    gameEnding = False
    convNode = False
    specialTopics = {}


lastTurn = TurnInfo

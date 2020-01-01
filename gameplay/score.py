from intficpy.gameplay.daemons import daemons
from intficpy.gameplay.object_maps import achievements, hintnodes
from intficpy.gameplay.game_info import lastTurn

##############################################################
# SCORE.PY - achievements and score for IntFicPy
# Defines the Achievement class, and the Ending class
##############################################################


class Achievement:
    """Class for achievements in the IntFicPy game"""

    def __init__(self, points, desc):
        # indexing
        achievements.addEntry(self)
        # essential properties
        self.points = points
        self.desc = desc
        score.possible = score.possible + self.points

    def award(self, app):
        # add self to fullscore
        if not self in score.achievements:
            app.printToGUI(
                "<b>ACHIEVEMENT:</b><br>"
                + str(self.points)
                + " points for "
                + self.desc
            )
            score.achievements.append(self)
            score.total = score.total + self.points


class AbstractScore:
    def __init__(self):
        self.total = 0
        self.possible = 0
        self.achievements = []

    def score(self, app):
        app.printToGUI(
            "You have scored <b>"
            + str(self.total)
            + " points</b> out of a possible "
            + str(self.possible)
            + ". "
        )

    def fullscore(self, app):
        if len(self.achievements) == 0:
            app.printToGUI("You haven't scored any points so far. ")
        else:
            app.printToGUI("You have scored: ")
            for achievement in self.achievements:
                app.printToGUI(
                    "<b>"
                    + str(achievement.points)
                    + " points</b> for "
                    + achievement.desc
                )


score = AbstractScore()


class Ending:
    def __init__(self, good, title, desc):
        achievements.addEntry(self)
        self.good = good
        self.title = title
        self.desc = desc

    def endGame(self, me, app):
        from intficpy.parser import parser

        app.printToGUI("<b>" + self.title + "</b>")
        app.printToGUI(self.desc)
        parser.lastTurn.gameEnding = True


class HintSystem:
    def __init__(self):
        self.cur_node = None
        self.stack = []
        self.pending = []
        self.pending_daemon = False

    def addPending(self, node):
        if node not in self.pending:
            self.pending.append(node)
        if self.pending and not self.pending_daemon:

            self.pending_daemon = True
            if not self.checkPending in daemons.funcs:
                daemons.add(self.checkPending)

    def checkPending(self, me, app):
        if self.pending:
            remove_nodes = []
            for node in self.pending:
                if not node.checkRequiredIncomplete():
                    remove_nodes.append(node)
                    node.complete = True  # not sure about this
                elif self.setNode(node):
                    remove_nodes.append(node)
            for node in remove_nodes:
                self.pending.remove(node)

    def setNextNodeFrom(self, node):
        x = node
        if not x:
            return False
        nodes_checked = []  # record checked nodes to prevent an infinite loop
        nodes_checked.append(x)
        while x:
            if not isinstance(x, HintNode):
                print(x)
                print("ERROR: not a HintNode - cannot use as current hint ")
                return False
            if not x.complete:
                if not x.checkRequiredIncomplete():
                    x.complete = True  # not sure
                    if x in self.stack:
                        self.stack.remove(x)
                    return False
                if not x.checkRequiredComplete():
                    self.addPending(x)
                    return False
                else:
                    if x not in self.stack:
                        self.stack.append(x)
                    self.cur_node = x
                    return True
            x = x.next_node
            if x in nodes_checked:
                break
            nodes_checked.append(x)
        return False

    def setNode(self, node):
        success = self.setNextNodeFrom(node)
        if not success:
            if self.stack:
                self.cur_node = self.stack[-1]
            else:
                self.cur_node = None
        return True

    def closeNode(self, node):
        node.complete = True
        if node in self.stack:
            self.stack.remove(node)
        return self.setNode(node)


hints = HintSystem()


class Hint:
    def __init__(self, text, achievement=None, cost=0):
        hintnodes.addEntry(self)
        self.text = text
        self.achievement = achievement
        self.cost = cost
        self.shown = False

    def giveHint(self, app):
        app.printToGUI(self.text)
        if (
            isinstance(self.achievement, Achievement)
            and self.cost > 0
            and not self.shown
        ):
            self.achievement.points -= self.cost
            if self.achievement.points < 0:
                self.achievement.points = 0
        self.shown = True


class HintNode:
    def __init__(self, hints):
        hintnodes.addEntry(self)
        self.cur_hint = 0
        self.hints = []
        self.next_node = None
        self.complete = False
        for x in hints:
            if not isinstance(x, Hint):
                print(x)
                print("ERROR: not a Hint - cannot add to HintNode ")
        self.hints = hints
        # nodes that must be complete/incomplete in order to open node
        self.open_require_nodes_complete = []
        self.open_require_nodes_incomplete = []

    def checkRequiredComplete(self):
        if self.open_require_nodes_complete:
            nodes_complete = [
                item.complete for item in self.open_require_nodes_complete
            ]
            return all(nodes_complete)
        return True

    def checkRequiredIncomplete(self):
        if self.open_require_nodes_incomplete:
            nodes_incomplete = [
                (not item.complete) for item in self.open_require_nodes_complete
            ]
            return all(nodes_incomplete)
        return True

    def setHints(self, hints):
        for x in hints:
            if not isinstance(x, Hint):
                print(x)
                print("ERROR: not a Hint - cannot add to HintNode ")
                return False
        self.hints = hints

    def nextHint(self, app):
        """Gives the next hint associated with the HintNode
		Returns True if a hint can be given, False on failure """

        if len(self.hints) == 0:
            print("ERROR: cannot use nextHint on empty HintNode ")
            return False
        if previousTurnHint():
            self.cur_hint += 1
        if self.cur_hint == len(self.hints):
            self.cur_hint -= 1
        self.hints[self.cur_hint].giveHint(app)
        t = "(Hint tier " + str(self.cur_hint + 1) + "/" + str(len(self.hints))
        if not self.cur_hint < len(self.hints) - 1:
            t += ")"
        else:
            t += " - type hint now to show next)"
        app.printToGUI(t)
        if self.cur_hint < (len(self.hints) - 1):
            if (
                not self.hints[self.cur_hint + 1].shown
                and self.hints[self.cur_hint + 1].achievement
            ):
                if self.hints[self.cur_hint + 1].cost == 1:
                    app.printToGUI("(Next tier costs 1 point)")
                else:
                    app.printToGUI(
                        "(Next tier costs "
                        + str(self.hints[self.cur_hint + 1].cost)
                        + " points)"
                    )
        return True


def previousTurnHint():

    if len(lastTurn.turn_list) < 2:
        return False
    return lastTurn.turn_list[-2] == "hint"

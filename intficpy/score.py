from .ifp_object import IFPObject
from .daemons import Daemon

##############################################################
# SCORE.PY - achievements and score for IntFicPy
# Defines the Achievement class, and the Ending class
##############################################################


class Achievement(IFPObject):
    """Class for achievements in the .game"""

    def __init__(self, game, points, desc):
        super().__init__(game)
        self.points = points
        self.desc = desc
        self.game.score.possible += self.points

    def award(self, game):
        # add self to fullscore
        if not self in self.game.score.achievements:
            game.addTextToEvent(
                "turn",
                "<b>ACHIEVEMENT:</b><br>"
                + str(self.points)
                + " points for "
                + self.desc,
            )
            self.game.score.achievements.append(self)
            self.game.score.total += self.points


class AbstractScore(IFPObject):
    def __init__(self, game):
        super().__init__(game)
        self.total = 0
        self.possible = 0
        self.achievements = []

    def score(self, game):
        game.addTextToEvent(
            "turn",
            "You have scored <b>"
            + str(self.total)
            + " points</b> out of a possible "
            + str(self.possible)
            + ". ",
        )

    def fullscore(self, game):
        if len(self.achievements) == 0:
            game.addTextToEvent("turn", "You haven't scored any points so far. ")
        else:
            game.addTextToEvent("turn", "You have scored: ")
            for achievement in self.achievements:
                game.addTextToEvent(
                    "turn",
                    "<b>"
                    + str(achievement.points)
                    + " points</b> for "
                    + achievement.desc,
                )


class Ending(IFPObject):
    def __init__(self, game, good, title, desc):
        super().__init__(game)
        self.good = good
        self.title = title
        self.desc = desc

    def endGame(self, game):
        game.addTextToEvent("turn", "<b>" + self.title + "</b>")
        game.addTextToEvent("turn", self.desc)
        game.ended = True


class HintSystem(IFPObject):
    def __init__(self, game):
        super().__init__(game)
        self.cur_node = None
        self.stack = []
        self.pending = []
        self.has_pending_daemon = False
        self.pending_daemon = Daemon(self.game, self.checkPending)

    def addPending(self, game, node):
        if node not in self.pending:
            self.pending.append(node)
        if self.pending and not self.has_pending_daemon:

            self.has_pending_daemon = True
            if not self.pending_daemon in game.daemons.active:
                game.daemons.add(self.pending_daemon)

    def checkPending(self, game):
        if self.pending:
            remove_nodes = []
            for node in self.pending:
                if not node.checkRequiredIncomplete():
                    remove_nodes.append(node)
                    node.complete = True  # not sure about this
                elif self.setNode(game, node):
                    remove_nodes.append(node)
            for node in remove_nodes:
                self.pending.remove(node)

    def setNextNodeFrom(self, game, node):
        x = node
        if not x:
            return False
        nodes_checked = []  # record checked nodes to prevent an infinite loop
        nodes_checked.append(x)
        while x:
            if not isinstance(x, HintNode):
                raise ValueError(f"{x} is not a HintNode - cannot use as current hint ")
            if not x.complete:
                if not x.checkRequiredIncomplete():
                    x.complete = True  # not sure
                    if x in self.stack:
                        self.stack.remove(x)
                    return False
                if not x.checkRequiredComplete():
                    self.addPending(game, x)
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

    def setNode(self, game, node):
        success = self.setNextNodeFrom(game, node)
        if not success:
            if self.stack:
                self.cur_node = self.stack[-1]
            else:
                self.cur_node = None
        return True

    def closeNode(self, game, node):
        node.complete = True
        if node in self.stack:
            self.stack.remove(node)
        return self.setNode(game, node)


class Hint(IFPObject):
    def __init__(self, game, text, achievement=None, cost=0):
        super().__init__(game)
        self.text = text
        self.achievement = achievement
        self.cost = cost
        self.shown = False

    def giveHint(self, game):
        game.addTextToEvent("turn", self.text)
        if (
            isinstance(self.achievement, Achievement)
            and self.cost > 0
            and not self.shown
        ):
            self.achievement.points -= self.cost
            if self.achievement.points < 0:
                self.achievement.points = 0
        self.shown = True


class HintNode(IFPObject):
    def __init__(self, game, hints):
        super().__init__(game)
        self.cur_hint = 0
        self.hints = []
        self.next_node = None
        self.complete = False
        for x in hints:
            if not isinstance(x, Hint):
                raise ValueError(f"{x} is not a HintNode - cannot add to HintNode")
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
                (not item.complete) for item in self.open_require_nodes_incomplete
            ]
            return all(nodes_incomplete)
        return True

    def setHints(self, hints):
        for x in hints:
            if not isinstance(x, Hint):
                raise ValueError(f"{x} is not a HintNode - cannot add to HintNode")
        self.hints = hints

    def nextHint(self, game):
        """Gives the next hint associated with the HintNode
		Returns True if a hint can be given, False on failure """

        if len(self.hints) == 0:
            raise ValueError(f"Cannot use nextHint on {self} - HintNode is empty")

        if self.previousTurnHint(game):
            self.cur_hint += 1
        if self.cur_hint == len(self.hints):
            self.cur_hint -= 1
        self.hints[self.cur_hint].giveHint(game)
        t = "(Hint tier " + str(self.cur_hint + 1) + "/" + str(len(self.hints))
        if not self.cur_hint < len(self.hints) - 1:
            t += ")"
        else:
            t += " - type hint now to show next)"
        game.addTextToEvent("turn", t)
        if self.cur_hint < (len(self.hints) - 1):
            if (
                not self.hints[self.cur_hint + 1].shown
                and self.hints[self.cur_hint + 1].achievement
            ):
                if self.hints[self.cur_hint + 1].cost == 1:
                    game.addTextToEvent("turn", "(Next tier costs 1 point)")
                else:
                    game.addTextToEvent(
                        "turn",
                        "(Next tier costs "
                        + str(self.hints[self.cur_hint + 1].cost)
                        + " points)",
                    )
        return True

    def previousTurnHint(self, game):

        if len(game.turn_list) < 2:
            return False
        return game.turn_list[-2] == "hint"

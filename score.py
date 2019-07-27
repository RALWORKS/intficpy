##############################################################
# SCORE.PY - achievements and score for IntFicPy
# Defines the Achievement class, and the Ending class
##############################################################
# a dictionary of the indeces of all Thing objects, including subclass instances, mapped to their object
# populated at runtime
achievements = {}
# index is an integer appended to the string "thing"- increases by 1 for each Thing defined
# index of a Thing will always be the same provided the game file is written according to the rules
achievement_ix = 0
endings = {}
ending_ix = 0

class Achievement:
	"""Class for achievements in the IntFicPy game"""
	def __init__(self, points, desc):
		# indexing
		global achievement_ix
		self.ix = "achievement" + str(achievement_ix)
		achievement_ix = achievement_ix + 1
		achievements[self.ix] = self
		# essential properties
		self.points = points
		self.desc = desc
		score.possible = score.possible + self.points
	
	def award(self, app):
		# add self to fullscore
		if not self in score.achievements:
			app.printToGUI("<b>ACHIEVEMENT:</b><br>" + str(self.points) + " points for " + self.desc)
			score.achievements.append(self)
			score.total = score.total + self.points

class AbstractScore:
	def __init__(self):
		self.total = 0
		self.possible = 0
		self.achievements = []
	
	def score(self, app):
		app.printToGUI("You have scored <b>" + str(self.total) + " points</b> out of a possible " + str(self.possible) + ". ") 
	
	def fullscore(self, app):
		if len(self.achievements)==0:
			app.printToGUI("You haven't scored any points so far. ")
		else:
			app.printToGUI("You have scored: ")
			for achievement in self.achievements:
				app.printToGUI("<b>" + str(achievement.points) + " points</b> for " + achievement.desc)

score = AbstractScore()

class Ending:
	def __init__(self, good, title, desc):
		global ending_ix
		self.ix = "ending" + str(ending_ix)
		ending_ix = ending_ix + 1
		endings[self.ix] = self
		self.good = good
		self.title = title
		self.desc = desc
	
	def endGame(self, me, app):
		from . import parser
		app.printToGUI("<b>" + self.title + "</b>")
		app.printToGUI(self.desc)
		parser.lastTurn.gameEnding = True

class HintSystem:
	def __init__(self):
		self.cur_node = None
		self.stack = []
	
	def setNode(self, node):
		from .score import HintNode
		if not node:
			self.cur_node = None
			return True
		if not isinstance(node, HintNode):
			print(node)
			print("ERROR: not a HintNode - cannot use as current hint ")
			return False
		elif not node.complete:
			self.cur_node = node
			if node not in self.stack:
				self.stack.append(node)
		return True
			
	def closeNode(self, node):
		node.complete = True
		if node in self.stack:
			self.stack.remove(node)
		if node.next_node:
			x = node.next_node
			while x:
				if not x.complete:
					self.setNode(x)
					return 0
				x = x.next_node
		if len(self.stack) > 0:
			self.setNode(self.stack[-1])
			return 0
		self.setNode(None)
		return 0

hints = HintSystem()
		
class Hint:
	def __init__(self, text, achievement=None, cost=0):
		self.text = text
		self.achievement = achievement
		self.cost = cost
		self.shown = False
	
	def giveHint(self, app):
		app.printToGUI(self.text)
		if isinstance(self.achievement, Achievement) and self.cost > 0 and not self.shown:
			self.achievement.points -= self.cost
			if self.achievement.points < 0:
				self.achievement.points = 0
		self.shown = True

class HintNode:
	def __init__(self, hints):
		self.cur_hint = 0
		self.hints = []
		self.next_node = None
		self.complete = False
		for x in hints:
			if not isinstance(x, Hint):
				print(x)
				print("ERROR: not a Hint - cannot add to HintNode ")
		self.hints = hints
	
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
		self.hints[self.cur_hint].giveHint(app)
		self.cur_hint += 1
		if self.cur_hint == len(self.hints):
			self.cur_hint -= 1
			return False
		else:
			return True

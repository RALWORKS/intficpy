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
		self.good = good
		self.title = title
		self.desc = desc
	
	def endGame(self, me, app):
		from . import parser
		app.printToGUI("<b>" + self.title + "</b>")
		app.printToGUI(self.desc)
		parser.lastTurn.gameEnding = True

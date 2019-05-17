##############################################################
# VOCAB.PY - the vocabulary dictionaries for IntFicPy
# Defines the nounDict and verbDict dictionaries
##############################################################

# dictionary linking natural language nouns to arrays of related Thing objects
nounDict = {}
# dictionary of verb names
verbDict = {}
# vocab standard to the language
class VocabObject:
	def __init__(self):
		self.prepositions = []
		self.articles = []

english = VocabObject()
english.prepositions = ["in", "out", "up", "down", "on", "under", "over", "through", "at", "across", "with", "off", "around", "to", "about"]
english.articles = ["a", "an", "the"]

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
		self.keywords = []
		self.no_space_before = []

english = VocabObject()
english.prepositions = ["in", "out", "up", "down", "on", "under", "over", "through", "at", "across", "with", "off", "around", "to", "about", "from", "into", "using"]
english.articles = ["a", "an", "the"]
english.keywords = ["all", "everything"]
english.no_space_before = [",", ".", "?", "!", ":", ";", "\'s", "'s", "\'d", "'d", "\'ll", "'ll"]

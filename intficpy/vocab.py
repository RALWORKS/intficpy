##############################################################
# VOCAB.PY - the standard vocabulary dictionaries for IntFicPy
##############################################################

# vocab standard to the language
class VocabObject:
    def __init__(self):
        self.prepositions = []
        self.articles = []
        self.keywords = []
        self.no_space_before = []


english = VocabObject()
english.prepositions = [
    "in",
    "out",
    "up",
    "down",
    "on",
    "under",
    "over",
    "through",
    "at",
    "across",
    "with",
    "off",
    "around",
    "to",
    "about",
    "from",
    "into",
    "using",
]
english.articles = ["a", "an", "the"]
english.keywords = ["all", "everything"]
english.no_space_before = [
    ",",
    ".",
    "?",
    "!",
    ":",
    ";",
    "'s",
    "'s",
    "'d",
    "'d",
    "'ll",
    "'ll",
]

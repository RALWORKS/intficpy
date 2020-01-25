import string

from .vocab import english
from .game_info import lastTurn

##############################################################
# TOKENIZER.PY - tokenizing and cleaning functions for IntFicPy
##############################################################


def cleanInput(input_string, record=True):
    """
    Used on player commands to remove punctuation and convert to lowercase
    Takes the raw user input (string)
    Returns a string
    """
    input_string = input_string.lower()
    exclude = set(string.punctuation)
    input_string = "".join(ch for ch in input_string if ch not in exclude)
    if record:
        lastTurn.turn_list.append(input_string)
        if lastTurn.recfile:
            lastTurn.recfile.write(input_string + "\n")
            lastTurn.recfile.flush()
    return input_string


def tokenize(input_string):
    """Convert input to a list of tokens
	Takes a string as an argument, and returns a list of strings """
    # tokenize input with spaces
    tokens = input_string.split()
    return tokens


def removeArticles(tokens):
    for article in english.articles:
        while article in tokens:
            tokens.remove(article)
    return tokens

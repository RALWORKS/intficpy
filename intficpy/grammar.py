from .tokenizer import cleanInput, tokenize, removeArticles


class GrammarObject(object):
    def __init__(self, tokens="", target=None):
        self.tokens = tokens
        self.adjectives = []
        self.entity_matches = []
        self.target = target

    @property
    def noun_token(self):
        return (self.tokens or [None])[-1]


class Command(object):
    def __init__(self, input_string=""):
        self.input_string = cleanInput(input_string)
        self.tokens = tokenize(self.input_string)

        self.verb_matches = []
        self.verb = None
        self.verb_form = None

        self.things = []
        self.verb = None
        self.dobj = None
        self.iobj = None

        self.ambiguous = False
        self.ambig_noun = None
        self.err = False

        self.disambig_objects = []

        self.specialTopics = {}
        self.sequence = None

    @property
    def primary_verb_token(self):
        return (self.tokens or [None])[0]

    @property
    def ambig_obj(self):
        if self.dobj and self.dobj.entity_matches and not self.dobj.target:
            return dobj
        if self.iobj and self.iobj.entity_matches and not self.iobj.target:
            return iobj
        return None

    @property
    def has_active_sequence(self):
        return self.sequence and self.sequence.active

    @property
    def has_sticky_sequence(self):
        return self.has_active_sequence and self.sequence.sticky

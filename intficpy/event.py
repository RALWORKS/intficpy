class IFPEvent:
    def __init__(self, game, priority, text, style):
        self.game = game
        self.style = style
        self.priority = priority
        self._text = []
        if text:
            self._text.append(text)

    def addSubEvent(self, text=None):
        e = IFPEvent(self.game, None, text, None)
        self._text.append(e)
        return e

    @property
    def text(self):
        text = []
        for t in self._text:
            text += getattr(t, "text", [t])
        return text

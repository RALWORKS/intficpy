class IFPEvent:
    def __init__(self, game, priority, text, style):
        self.style = style
        self.priority = priority
        self.text = []
        if text:
            self.text.append(text)

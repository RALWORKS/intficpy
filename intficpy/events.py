class IFPEvent:
    def __init__(self, game, priority, text_0):
        self.priority = priority
        self.text = []
        if text_0:
            self.text.append(text_0)

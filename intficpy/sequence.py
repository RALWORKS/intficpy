"""
Considerations:
- must be able to store exact position in sequence
- sequences are *branching* simple API

```
sequence1 = Sequence([
    "You are in a dark room. Light filters in through a cracked, dirty window.",
    "What will you do?",
    {
        "Break the window": [
            "You smash the window.",
            "Acid gas flows into the room.",
            {
                "Cover your mouth with your shirt": [
                    "It doesn't help. You die anyway.",
                    me.die(),
                ],
                "Hide": [
                    "You hide. It's pointless. You die.",
                    me.die(),
                ]
            }
        ],
        "Do nothing": [
            "You do nothing.",
            "Nothing happens for a while, but then...",
            "You don't die.",
            me.win(),
        ]
    },
    "This would happen after the choice's outcome."
])
```
If we start from this ^ API, what does that imply?

The top level of a Sequence is an Array, representing events that occur in order
I like that
But I'm a little confused about this

Let's say:
- the list items are read in order
- strings are added, in order, to the "sequence" event
- when a dict is reached, we create a MENU (in the form of conv. suggestions)
  and we PAUSE the sequence (AKA stop reading in array items)
  THEN the user SELECTS an option, and we PUSH into its array
  We read the items as we did for the top level array
  When we reach the END of an array, we POP out to the next level
  When we reach the END of the main array, we end the sequence

So, how do we remember our position?
Use nested indeces
If you just did "Break the window", your position is
[2]["Break the window"] or [2, "Break the window"] ([2, "Break the window", 2] maybe?)

Sequence commands

<up> pops the navigation stack
<prompt somevarname> save user input to the scene.data dict under key "somevarname"

Allow creators to define an "on complete" function
could be used for transfering data out of the sequence, and onto other objects


def has_done_thing(sequence):
    if sequence.this_was_done:
        return [2, 1]
    return [2, 3]

--
    Sequence.Navigator(has_done_thing)

---
    Sequence.Navigator(lambda seq: [2, 1] if seq.this_was_done else [2, 3])
---

TODO:
- Sequence SaveData Node
- Sequence Prompt Node
- Conditional logic & flow control - Idea: controller/navigator node where author defines a function (array of functions evaluated in sequence?) to determine where to read next


special items
+ Prompt
+ Navigator
"""
from inspect import signature

from .exceptions import IFPError, NoMatchingSuggestion
from .ifp_object import IFPObject
from .tokenizer import cleanInput, tokenize
from .vocab import english


class Sequence(IFPObject):
    class Event:
        pass

    class Pause(Event):
        pass

    class NodeComplete(Event):
        pass

    class ControlItem:
        def read(self):
            raise NotImplementedError(
                "Sequence control classes must define a read method"
            )

    class Prompt(ControlItem):
        def __init__(self, save_key, label, question):
            self.save_key = save_key
            self.label = label
            self.question = question
            self.answer = None
            self.sequence = None
            self._submitted = False

        def read(self, game, event="turn"):
            if self._submitted:
                return
            if self.answer:
                game.addTextToEvent(event, f"{self.label}: {self.answer}? (y/n)")
            else:
                game.addTextToEvent(event, self.question)
            return self.sequence.Pause()

        def try_again(self):
            self.answer = None
            self.sequence.play()

        def submit(self):
            self.sequence.data[self.save_key] = self.answer
            self._submitted = True
            self.sequence.play()

        def accept_input(self, tokens):
            if self.answer:
                if " ".join(tokens) in english.yes:
                    self.submit()
                elif " ".join(tokens) in english.no:
                    self.try_again()
                else:
                    raise NoMatchingSuggestion(
                        "Expected yes/no answer", english.yes + english.no, []
                    )
            else:
                self.answer = " ".join(tokens)
                self.sequence.play()

    class SaveData(ControlItem):
        def __init__(self, save_key, value):
            self.save_key = save_key
            self.value = value
            self.sequence = None

        def read(self, *args, **kwargs):
            self.sequence.data[self.save_key] = self.value

    def __init__(self, game, template, data=None):
        super().__init__(game)
        self._validate(template)
        self.template = template

        self.position = [0]
        self.options = []
        self.data = data or {}
        self.data["game"] = game

    def on_complete(self):
        pass

    def start(self):
        self.position = [0]
        self.play()

    @property
    def current_item(self):
        return self._get_section(self.position)

    @property
    def current_node(self):
        if len(self.position) < 2:
            return self.template
        return self._get_section(self.position[:-1])

    def next(self, event):
        self.game.parser.command.sequence = self

        ret = self._read_item(self.current_item, event)
        if isinstance(ret, self.Pause):
            return ret
        return self._iterate()

    def play(self, event="turn"):
        while True:
            ret = self.next(event)
            if isinstance(ret, self.Pause):
                return
            while isinstance(ret, self.NodeComplete):
                if len(self.position) == 1:
                    self.on_complete()
                    return
                self.position = self.position[
                    :-2
                ]  # pop out of the list and its parent dict
                ret = self._iterate()

    def accept_input(self, tokens):
        """
        Pass current input tokens from the parser, to the method corresponding to the
        type of input we are currently expecting
        """
        if isinstance(self.current_item, self.Prompt):
            self.current_item.accept_input(tokens)
        else:
            self.choose(tokens)  # by default, we interpret input as a menu choice

    def choose(self, tokens):
        """
        Try to use input tokens from the parser to choose an option in the current menu
        """
        ix = None
        if len(tokens) == 1:
            try:
                ix = int(tokens[0]) - 1
            except ValueError:
                pass
        if ix is not None and ix <= len(self.options):
            self.position += [self.options[ix], 0]
        else:
            answer = self._match_text_to_suggestion(tokens)
            self.position += [answer, 0]
        self.play()

    def _match_text_to_suggestion(self, query_tokens):
        """
        Try to match tokens to a single suggestion from the current options
        Raises NoMatchingSuggestion on failure
        """
        tokenized_options = [tokenize(cleanInput(option)) for option in self.options]
        match_indeces = []

        for i in range(len(self.options)):
            option = tokenized_options[i]
            if not [word for word in query_tokens if not word in option]:
                match_indeces.append(i)

        if len(match_indeces) != 1:
            raise NoMatchingSuggestion(
                query_tokens, self.options, [self.options[ix] for ix in match_indeces]
            )

        return self.options[match_indeces[0]]

    def _get_section(self, location):
        section = self.template
        for ix in location:
            section = section[ix]
        return section

    def _read_item(self, item, event):
        self.options = []
        if type(item) is str:
            self.game.addTextToEvent(event, item.format(**self.data))

        elif callable(item):
            ret = item()
            if type(ret) is str:
                self.game.addTextToEvent(event, ret)

        elif isinstance(item, self.ControlItem):
            return item.read(self.game, event)

        else:
            self.options = list(item.keys())
            options = "\n".join(
                [f"{i + 1}) {self.options[i]}" for i in range(len(self.options))]
            )
            self.game.addTextToEvent(event, options)
            return self.Pause()

    def _iterate(self):
        if self.position[-1] >= len(self.current_node) - 1:
            return self.NodeComplete()
        self.position[-1] += 1

    def _validate(self, node, stack=None):
        stack = stack or []

        if not type(node) is list:
            raise IFPError(
                "Expected Sequence node (list); found {node}" f"\nLocation: {stack}"
            )
        for i in range(0, len(node)):
            stack.append(i)
            item = node[i]

            if type(item) is str:
                stack.pop()
                continue

            if isinstance(item, self.ControlItem):
                item.sequence = self
                stack.pop()
                continue

            if callable(item):
                sig = signature(item)
                if [p for p in sig.parameters]:
                    raise IFPError(
                        f"{item} found in Sequence. "
                        "Callables with that accept parameters cannot be used "
                        "as Sequence items."
                        f"\nLocation: {stack}"
                    )
                stack.pop()
                continue
            try:
                for key, sub_node in item.items():
                    if type(key) is not str:
                        raise IFPError(
                            "Only strings can be used as option names (dict keys) in Sequences. "
                            f"Found {key} ({type(key)})\nLocation: {stack}"
                        )
                    stack.append(key)
                    self._validate(sub_node, stack=stack)
                    stack.pop()
            except AttributeError:
                raise IFPError(
                    f"Expected Sequence item (string, function, or dict); found {item}"
                    f"\nLocation: {stack}"
                )
            stack.pop()

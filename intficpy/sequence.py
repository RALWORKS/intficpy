"""

TODO:
* An "Up" ControlItem (pop)
* "Label" ControlItem? - create a more human friendly interface for jumps/procedural navigation
* Conditional logic & flow control - Idea: controller/navigator node where author defines a function (array of functions evaluated in sequence?) to determine where to read next
    ```
        # example function to pass to a Navigator
        def has_done_thing(sequence):
            if sequence.this_was_done:
                return [2, 1]
            return [2, 3]
    ```
    Use in a Sequence template:
    ```
        [
            Sequence.Navigator(has_done_thing),
            ...,
            # or with a labmbda
            Sequence.Navigator(lambda seq: [2, 1] if seq.this_was_done else [2, 3]),
        ]
    ```

"""
from inspect import signature

from .exceptions import IFPError, NoMatchingSuggestion
from .ifp_object import IFPObject
from .tokenizer import cleanInput, tokenize
from .vocab import english


class Sequence(IFPObject):
    class _Completed(Exception):
        pass

    class _Event:
        pass

    class _PauseEvent(_Event):
        def __init__(self, iterate=False):
            self.iterate = iterate

    class _NodeComplete(_Event):
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
            return self.sequence._PauseEvent()

        def try_again(self):
            self.answer = None
            self.sequence.play()

        def submit(self):
            self.sequence.data[self.save_key] = self.answer
            self._submitted = True
            self.sequence.play()
            self.answer = None
            self._submitted = False

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

    class Label(ControlItem):
        def __init__(self, name):
            self.name = name

        def read(self, game, event):
            pass  # a label does nothing when read

    class Pause(ControlItem):
        def read(self, game, event):
            return Sequence._PauseEvent(iterate=True)

    class Jump(ControlItem):
        """
        Unconditionally jump to a label or index
        """

        def __init__(self, destination):
            self.sequence = None
            self.destination = destination

        def read(self, game, event):
            self.sequence.jump_to(self.destination)

    class Navigator(ControlItem):
        def __init__(self, nav_func):
            self.nav_func = nav_func
            self.sequence = None

        def read(self, game, event):
            self.sequence.jump_to(self.nav_func(self.sequence))

    def __init__(self, game, template, data=None, sticky=False):
        super().__init__(game)
        self.labels = {}
        self._parse_template_node(template)
        self.template = template
        self.sticky = sticky

        self.position = [0]
        self.options = []
        self.data = data or {}
        self.data["game"] = game
        self.active = False

        self.next_sequence = None

    @property
    def current_item(self):
        return self._get_section_by_location(self.position)

    @property
    def current_node(self):
        if len(self.position) < 2:
            return self.template
        return self._get_section_by_location(self.position[:-1])

    def start(self):
        self.active = True
        self.position = [0]
        self.play()

    def next(self, event):
        ret = self._read_item(self.current_item, event)
        if isinstance(ret, self._PauseEvent):
            if ret.iterate:
                self._iterate()
            return ret
        return self._iterate()

    def handle_node_complete(self, event):

        if len(self.position) == 1:
            self.on_complete()
            raise self._Completed()

        self.position = self.position[:-2]  # pop out of the list and its parent dict
        # self._iterate()
        # self.next(event)

        if self.node_ended:
            # self._iterate()
            # self.next(event)
            return self.handle_node_complete(event)

        self.position[-1] += 1

        return self.play(event)

    def play(self, event="turn"):
        self.game.parser.command.sequence = self

        cur = self.next(event)

        if isinstance(cur, self._PauseEvent):
            return

        if isinstance(cur, self._NodeComplete):
            try:
                return self.handle_node_complete(event)
            except self._Completed:
                return

        return self.play(event)

    def jump_to(self, value):
        """
        Read the sequence from the specified point.
        Accepts a string that is registered as a label on the Sequence
        or an array specifying an index on the Sequence template
        """
        loc = self._normalize_location(value)
        self.position = list(loc)

    def on_complete(self):
        self.active = False
        if self.next_sequence:
            self.next_sequence.start()

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
        if ix is not None and ix < len(self.options):
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

    def _get_section_by_location(self, location):
        section = self.template
        for ix in location:
            section = section[ix]
        return section

    def _normalize_location(self, value):
        if type(value) is str:
            try:
                loc = self.labels[value]
            except KeyError as e:
                raise KeyError(
                    f'"{value}" is not a valid label for Sequence {self}.\n'
                    f"This Sequence has the following labels: {self.labels.keys()}"
                ) from e
            return loc
        else:
            return value

    def _read_item(self, item, event):
        self.options = []
        if type(item) is str:
            self.game.addTextToEvent(event, item.format(**self.data))

        elif callable(item):
            ret = item(self)
            if type(ret) is str:
                self.game.addTextToEvent(event, ret)

        elif isinstance(item, self.ControlItem):
            item.sequence = self
            return item.read(self.game, event)

        else:
            self.options = list(item.keys())
            options = "\n".join(
                [f"{i + 1}) {self.options[i]}" for i in range(len(self.options))]
            )
            self.game.addTextToEvent(event, options)
            return self._PauseEvent()

    @property
    def node_ended(self):
        return self.position[-1] >= len(self.current_node) - 1

    def _iterate(self):
        if self.node_ended:
            return self._NodeComplete()
        self.position[-1] += 1

    def _parse_template_node(self, node, stack=None):
        """
        Parse, validate, and prepare the template for reading
        """
        stack = stack or []

        if not type(node) is list:
            raise IFPError(
                "Expected Sequence node (list); found {node}" f"\nLocation: {stack}"
            )
        for i in range(0, len(node)):
            stack.append(i)
            item = node[i]

            if isinstance(item, self.Label):
                if item.name in self.labels:
                    raise IFPError(
                        "Sequence Labels must be uniquely named within the Sequence. "
                        f'Label "{item.name}" at location {stack} was previously defined '
                        "for this Sequence."
                    )
                self.labels[item.name] = list(stack)
                stack.pop()
                continue

            if type(item) is str or isinstance(item, self.ControlItem):
                stack.pop()
                continue

            if callable(item):
                sig = signature(item)
                if len([p for p in sig.parameters]) != 1:
                    raise IFPError(
                        f"{item} found in Sequence. "
                        "Callables used as Sequence items must accept the Sequence instance "
                        "as the only argument."
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
                    self._parse_template_node(sub_node, stack=stack)
                    stack.pop()
            except AttributeError:
                raise IFPError(
                    f"Expected Sequence item (string, function, dict or Sequence "
                    f"ControlItem); found {item}"
                    f"\nLocation: {stack}"
                )
            stack.pop()

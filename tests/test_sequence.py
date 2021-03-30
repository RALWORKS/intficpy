from intficpy.sequence import Sequence
from intficpy.exceptions import IFPError

from .helpers import IFPTestCase


class TestSequence(IFPTestCase):
    def test_sequence_lifecycle(self):
        class MySequence(Sequence):
            game = self.game
            template = ["This is the start", {"the only option": ["the outcome"]}]

            def __init__(self):
                super().__init__()
                self.a_wonderful_strange = None

            def on_complete(self):
                self.a_wonderful_strange = True

        self.assertIsNone(self.game.parser.previous_command.sequence)

        sequence = MySequence()

        self.assertIs(self.game.parser.command.sequence, sequence)
        self.game.runTurnEvents()
        self.assertIn(sequence.template[0], self.app.print_stack)

        self.game.turnMain("1")
        self.assertIs(self.game.parser.command.sequence, sequence)

        self.assertIn(sequence.template[1]["the only option"][0], self.app.print_stack)
        self.assertTrue(sequence.a_wonderful_strange)

        self.game.turnMain("l")
        self.assertIsNone(self.game.parser.command.sequence)

    def test_select_sequence_option_by_keywords(self):
        class MySequence(Sequence):
            game = self.game
            template = [{"here it is": ["we shall"], "not here": ["no way"]}]

        sequence = MySequence()

        self.game.runTurnEvents()

        key = sequence.options[0]

        self.game.turnMain(key)
        self.assertIn(sequence.template[0][key][0], self.app.print_stack)

    def test_no_matching_suggestion(self):
        class MySequence(Sequence):
            game = self.game
            template = [{"here it is": ["we shall"], "not here": ["no way"]}]

        sequence = MySequence()

        self.game.runTurnEvents()

        self.game.turnMain("The invisible man turns the invisible key")

        self.assertIn("not enough information", self.app.print_stack.pop())

    def test_out_of_bound_option_index(self):
        class MySequence(Sequence):
            game = self.game
            template = [{"here it is": ["we shall"], "not here": ["no way"]}]

        sequence = MySequence()

        self.game.runTurnEvents()

        ix = 333
        self.assertGreater(ix, len(sequence.options))

        self.game.turnMain(str(ix))

        self.assertIn("not enough information", self.app.print_stack.pop())

    def test_accept_selection_with_single_word_non_index(self):
        class MySequence(Sequence):
            game = self.game
            template = [{"here it is": ["we shall"], "not here": ["no way"]}]

        sequence = MySequence()

        self.game.runTurnEvents()

        self.game.turnMain("not")

        self.assertIn(sequence.template[0]["not here"][0], self.app.print_stack.pop())

    def test_callable_as_sequence_item_prints_return_value_if_string(self):
        def locusts_swarm():
            return "A swarm of locusts descends upon the land."

        class MySequence(Sequence):
            game = self.game
            template = [locusts_swarm]

        sequence = MySequence()

        self.game.runTurnEvents()

        self.assertIn(locusts_swarm(), self.app.print_stack)

    def test_callable_as_sequence_runs_and_does_not_print_if_return_value_not_string(
        self,
    ):
        self.game.locusts_evaluated = False

        def locusts_swarm():
            self.game.locusts_evaluated = True
            return 17

        class MySequence(Sequence):
            game = self.game
            template = [locusts_swarm]

        sequence = MySequence()

        self.game.runTurnEvents()

        self.assertNotIn(locusts_swarm(), self.app.print_stack)
        self.assertNotIn(str(locusts_swarm()), self.app.print_stack)
        self.assertTrue(self.game.locusts_evaluated)

    def test_sequence_data_replacements(self):
        MC_NAME = "edmund"
        self.game.an_extra_something = "swamp"

        class MySequence(Sequence):
            game = self.game
            template = [
                "{name}, here is a {game.an_extra_something}.",
            ]
            starting_data = {"name": MC_NAME}

        sequence = MySequence()

        self.game.runTurnEvents()
        self.assertIn(
            sequence.template[0].format(name=MC_NAME, game=self.game),
            self.app.print_stack,
        )


class TextSaveData(IFPTestCase):
    def test_save_data_control_item(self):
        MC_NAME = "edmund"

        class MySequence(Sequence):
            game = self.game
            template = [Sequence.SaveData("name", MC_NAME)]
            starting_data = {"name": None}

        self.assertFalse(MySequence.starting_data["name"])
        sequence = MySequence()
        self.game.runTurnEvents()
        self.assertEqual(sequence.data["name"], MC_NAME)


class TestSequencePrompt(IFPTestCase):
    def test_can_respond_to_prompt_and_retrieve_data(self):
        MC_NAME = "edmund"
        LABEL = "Your name"
        DATA_KEY = "mc_name"
        QUESTION = "What's your name?"

        class MySequence(Sequence):
            game = self.game
            template = [
                "My name's Izzy. What's yours?",
                Sequence.Prompt(DATA_KEY, LABEL, QUESTION),
                "Good to meet you.",
            ]
            starting_data = {"name": MC_NAME}

        sequence = MySequence()

        self.game.runTurnEvents()
        self.assertIn(sequence.template[0], self.app.print_stack)
        self.game.turnMain(MC_NAME)
        self.assertIn(f"{LABEL}: {MC_NAME}? (y/n)", self.app.print_stack)
        self.game.turnMain("y")
        self.assertEqual(sequence.data[DATA_KEY], MC_NAME)
        self.assertIn(sequence.template[2], self.app.print_stack)

    def test_can_make_correction_before_submitting(self):
        TYPO_NAME = "edumd"
        MC_NAME = "edmund"
        LABEL = "Your name"
        DATA_KEY = "mc_name"
        QUESTION = "What's your name?"

        class MySequence(Sequence):
            game = self.game
            template = [
                "My name's Izzy. What's yours?",
                Sequence.Prompt(DATA_KEY, LABEL, QUESTION),
                "Good to meet you.",
            ]
            starting_data = {"name": MC_NAME}

        sequence = MySequence()

        self.game.runTurnEvents()
        self.assertIn(sequence.template[0], self.app.print_stack)
        self.game.turnMain(TYPO_NAME)
        self.assertIn(f"{LABEL}: {TYPO_NAME}? (y/n)", self.app.print_stack)
        self.game.turnMain("n")
        self.assertIn(QUESTION, self.app.print_stack)
        self.game.turnMain(MC_NAME)
        self.game.turnMain("y")

        self.assertEqual(sequence.data[DATA_KEY], MC_NAME)
        self.assertIn(sequence.template[2], self.app.print_stack)


class TestValidateSequenceTemplate(IFPTestCase):
    def test_invalid_top_level_template_node(self):
        with self.assertRaises(IFPError):

            class MySequence(Sequence):
                game = self.game
                template = 8

    def test_invalid_inner_template_node(self):
        with self.assertRaises(IFPError):

            class MySequence(Sequence):
                game = self.game
                template = [{"hello": "string not list"}]

    def test_invalid_sequence_item_type(self):
        with self.assertRaises(IFPError):

            class MySequence(Sequence):
                game = self.game
                template = [8]

    def test_dict_key_for_option_name_must_be_string(self):
        with self.assertRaises(IFPError):

            class MySequence(Sequence):
                game = self.game
                template = [{6: ["item"]}]

    def test_callable_accepting_arguments_is_invalid_item(self):
        def heron_event(n_herons):
            return f"There are {n_herons} herons."

        with self.assertRaises(IFPError):

            class MySequence(Sequence):
                game = self.game
                template = [heron_event]

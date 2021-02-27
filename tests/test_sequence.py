from intficpy.sequence import Sequence
from intficpy.exceptions import IFPError

from .helpers import IFPTestCase


class TestSequence(IFPTestCase):
    def test_sequence_lifecycle(self):
        sequence = Sequence(
            self.game, ["This is the start", {"the only option": ["the outcome"]}]
        )
        sequence.a_wonderful_strange = None

        def ended():
            sequence.a_wonderful_strange = True

        sequence.on_complete = ended

        self.assertIsNone(self.game.parser.previous_command.sequence)
        sequence.start()
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
        sequence = Sequence(
            self.game, [{"here it is": ["we shall"], "not here": ["no way"]}]
        )
        sequence.start()
        self.game.runTurnEvents()

        key = sequence.options[0]

        self.game.turnMain(key)
        self.assertIn(sequence.template[0][key][0], self.app.print_stack)

    def test_no_matching_suggestion(self):
        sequence = Sequence(
            self.game, [{"here it is": ["we shall"], "not here": ["no way"]}]
        )
        sequence.start()
        self.game.runTurnEvents()

        self.game.turnMain("The invisible man turns the invisible key")

        self.assertIn("not enough information", self.app.print_stack.pop())

    def test_out_of_bound_option_index(self):
        sequence = Sequence(
            self.game, [{"here it is": ["we shall"], "not here": ["no way"]}]
        )
        sequence.start()
        self.game.runTurnEvents()

        ix = 333
        self.assertGreater(ix, len(sequence.options))

        self.game.turnMain(str(ix))

        self.assertIn("not enough information", self.app.print_stack.pop())

    def test_accept_selection_with_single_word_non_index(self):
        sequence = Sequence(
            self.game, [{"here it is": ["we shall"], "not here": ["no way"]}]
        )
        sequence.start()
        self.game.runTurnEvents()

        self.game.turnMain("not")

        self.assertIn(sequence.template[0]["not here"][0], self.app.print_stack.pop())

    def test_callable_as_sequence_item_prints_return_value_if_string(self):
        def locusts_swarm():
            return "A swarm of locusts descends upon the land."

        sequence = Sequence(self.game, [locusts_swarm])

        sequence.start()
        self.game.runTurnEvents()

        self.assertIn(locusts_swarm(), self.app.print_stack)

    def test_callable_as_sequence_runs_and_does_not_print_if_return_value_not_string(
        self,
    ):
        self.game.locusts_evaluated = False

        def locusts_swarm():
            self.game.locusts_evaluated = True
            return 17

        sequence = Sequence(self.game, [locusts_swarm])

        sequence.start()
        self.game.runTurnEvents()

        self.assertNotIn(locusts_swarm(), self.app.print_stack)
        self.assertNotIn(str(locusts_swarm()), self.app.print_stack)
        self.assertTrue(self.game.locusts_evaluated)


class TestValidateSequenceTemplate(IFPTestCase):
    def test_invalid_top_level_template_node(self):
        with self.assertRaises(IFPError):
            Sequence(self.game, 8)

    def test_invalid_inner_template_node(self):
        with self.assertRaises(IFPError):
            Sequence(self.game, [{"hello": "string not list"}])

    def test_invalid_sequence_item_type(self):
        with self.assertRaises(IFPError):
            Sequence(self.game, [8])

    def test_dict_key_for_option_name_must_be_string(self):
        with self.assertRaises(IFPError):
            Sequence(self.game, [{6: ["item"]}])

    def test_callable_accepting_arguments_is_invalid_item(self):
        def heron_event(n_herons):
            return f"There are {n_herons} herons."

        with self.assertRaises(IFPError):
            Sequence(self.game, [heron_event])

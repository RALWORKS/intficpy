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

        self.assertIn("here it is", self.app.print_stack.pop())
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

        self.assertIn("here it is", self.app.print_stack.pop())
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
        def locusts_swarm(seq):
            return "A swarm of locusts descends upon the land."

        sequence = Sequence(self.game, [locusts_swarm])

        sequence.start()
        self.game.runTurnEvents()

        self.assertIn(locusts_swarm(sequence), self.app.print_stack)

    def test_callable_as_sequence_runs_and_does_not_print_if_return_value_not_string(
        self,
    ):
        self.game.locusts_evaluated = False

        def locusts_swarm(seq):
            self.game.locusts_evaluated = True
            return 17

        sequence = Sequence(self.game, [locusts_swarm])

        sequence.start()
        self.game.runTurnEvents()

        self.assertNotIn(locusts_swarm(sequence), self.app.print_stack)
        self.assertNotIn(str(locusts_swarm(sequence)), self.app.print_stack)
        self.assertTrue(self.game.locusts_evaluated)

    def test_sequence_data_replacements(self):
        MC_NAME = "edmund"
        self.game.an_extra_something = "swamp"
        sequence = Sequence(
            self.game,
            ["{name}, here is a {game.an_extra_something}.",],
            data={"name": MC_NAME},
        )
        sequence.start()
        self.game.runTurnEvents()
        self.assertIn(
            sequence.template[0].format(name=MC_NAME, game=self.game),
            self.app.print_stack,
        )

    def test_chaining_sequences(self):
        ITEM1 = "Hello"
        ITEM2 = "Again hello"
        sequence1 = Sequence(self.game, [ITEM1],)
        sequence2 = Sequence(self.game, [ITEM2],)
        sequence1.next_sequence = sequence2
        sequence1.start()
        self.game.runTurnEvents()
        self.assertIn(ITEM1, self.app.print_stack)
        self.assertIn(ITEM2, self.app.print_stack)

    def test_manual_pause(self):
        START_ITEM = "Hello."
        SKIPPED_ITEM = "NEVER!"

        sequence = Sequence(self.game, [START_ITEM, Sequence.Pause(), SKIPPED_ITEM,])
        sequence.start()
        self.game.runTurnEvents()
        self.assertIn(START_ITEM, self.app.print_stack)
        self.assertNotIn(SKIPPED_ITEM, self.app.print_stack)


class TestSequenceJump(IFPTestCase):
    def test_can_jump_by_label(self):
        START_ITEM = "Hello."
        SKIPPED_ITEM = "NEVER!"
        END_ITEM = "Goodbye."
        L = "sidestep"

        sequence = Sequence(
            self.game,
            [START_ITEM, Sequence.Jump(L), SKIPPED_ITEM, Sequence.Label(L), END_ITEM,],
        )
        sequence.start()
        self.game.runTurnEvents()
        self.assertIn(START_ITEM, self.app.print_stack)
        self.assertIn(END_ITEM, self.app.print_stack)
        self.assertNotIn(SKIPPED_ITEM, self.app.print_stack)

    def test_can_jump_by_index(self):
        START_ITEM = "Hello."
        SKIPPED_ITEM = "NEVER!"
        END_ITEM = "Goodbye."

        sequence = Sequence(
            self.game, [START_ITEM, Sequence.Jump([2]), SKIPPED_ITEM, END_ITEM,],
        )
        sequence.start()
        self.game.runTurnEvents()
        self.assertIn(START_ITEM, self.app.print_stack)
        self.assertIn(END_ITEM, self.app.print_stack)
        self.assertNotIn(SKIPPED_ITEM, self.app.print_stack)


class TestSequenceNavigator(IFPTestCase):
    def test_can_navigate_by_label(self):
        START_ITEM = "Hello."
        SKIPPED_ITEM = "NEVER!"
        END_ITEM = "Goodbye."
        L = "sidestep"

        sequence = Sequence(
            self.game,
            [
                START_ITEM,
                Sequence.Navigator(lambda s: L),
                SKIPPED_ITEM,
                Sequence.Label(L),
                END_ITEM,
            ],
        )
        sequence.start()
        self.game.runTurnEvents()
        self.assertIn(START_ITEM, self.app.print_stack)
        self.assertIn(END_ITEM, self.app.print_stack)
        self.assertNotIn(SKIPPED_ITEM, self.app.print_stack)

    def test_can_navigate_by_index(self):
        START_ITEM = "Hello."
        SKIPPED_ITEM = "NEVER!"
        END_ITEM = "Goodbye."

        sequence = Sequence(
            self.game,
            [START_ITEM, Sequence.Navigator(lambda s: [2]), SKIPPED_ITEM, END_ITEM,],
        )
        sequence.start()
        self.game.runTurnEvents()
        self.assertIn(START_ITEM, self.app.print_stack)
        self.assertIn(END_ITEM, self.app.print_stack)
        self.assertNotIn(SKIPPED_ITEM, self.app.print_stack)


class TextSaveData(IFPTestCase):
    def test_save_data_control_item(self):
        MC_NAME = "edmund"
        self.game.an_extra_something = "swamp"
        sequence = Sequence(
            self.game, [Sequence.SaveData("name", MC_NAME)], data={"name": None}
        )
        self.assertFalse(sequence.data["name"])
        sequence.start()
        self.game.runTurnEvents()
        self.assertEqual(sequence.data["name"], MC_NAME)


class TestSequencePrompt(IFPTestCase):
    def test_can_respond_to_prompt_and_retrieve_data(self):
        MC_NAME = "edmund"
        LABEL = "Your name"
        DATA_KEY = "mc_name"
        QUESTION = "What's your name?"
        sequence = Sequence(
            self.game,
            [
                "My name's Izzy. What's yours?",
                Sequence.Prompt(DATA_KEY, LABEL, QUESTION),
                "Good to meet you.",
            ],
        )
        sequence.start()
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
        sequence = Sequence(
            self.game,
            [
                "My name's Izzy. What's yours?",
                Sequence.Prompt(DATA_KEY, LABEL, QUESTION),
                "Good to meet you.",
            ],
        )
        sequence.start()
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

    def test_callable_accepting_too_many_arguments_is_invalid_item(self):
        def heron_event(seq, n_herons):
            return f"There are {n_herons} herons."

        with self.assertRaises(IFPError):
            Sequence(self.game, [heron_event])

    def test_callable_accepting_no_arguments_is_invalid_item(self):
        def heron_event():
            return f"There are 2 herons."

        with self.assertRaises(IFPError):
            Sequence(self.game, [heron_event])

    def test_label_name_cannot_be_used_twice(self):
        L = "label"
        with self.assertRaises(IFPError):
            Sequence(self.game, [Sequence.Label(L), Sequence.Label(L)])

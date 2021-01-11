from intficpy.cutscene import Cutscene
from intficpy.exceptions import IFPError

from .helpers import IFPTestCase


class TestCutscene(IFPTestCase):
    def test_cutscene_lifecycle(self):
        cutscene = Cutscene(
            self.game, ["This is the start", {"the only option": ["the outcome"]}]
        )
        cutscene.a_wonderful_strange = None

        def ended():
            cutscene.a_wonderful_strange = True

        cutscene.on_complete = ended

        self.assertIsNone(self.game.parser.previous_command.cutscene)
        cutscene.start()
        self.assertIs(self.game.parser.command.cutscene, cutscene)
        self.game.runTurnEvents()
        self.assertIn(cutscene.template[0], self.app.print_stack)

        self.game.turnMain("1")
        self.assertIs(self.game.parser.command.cutscene, cutscene)

        self.assertIn(cutscene.template[1]["the only option"][0], self.app.print_stack)
        self.assertTrue(cutscene.a_wonderful_strange)

        self.game.turnMain("l")
        self.assertIsNone(self.game.parser.command.cutscene)

    def test_select_cutscene_option_by_keywords(self):
        cutscene = Cutscene(
            self.game, [{"here it is": ["we shall"], "not here": ["no way"]}]
        )
        cutscene.start()
        self.game.runTurnEvents()

        key = cutscene.options[0]

        self.game.turnMain(key)
        self.assertIn(cutscene.template[0][key][0], self.app.print_stack)

    def test_no_matching_suggestion(self):
        cutscene = Cutscene(
            self.game, [{"here it is": ["we shall"], "not here": ["no way"]}]
        )
        cutscene.start()
        self.game.runTurnEvents()

        self.game.turnMain("The invisible man turns the invisible key")

        self.assertIn("not enough information", self.app.print_stack.pop())

    def test_out_of_bound_option_index(self):
        cutscene = Cutscene(
            self.game, [{"here it is": ["we shall"], "not here": ["no way"]}]
        )
        cutscene.start()
        self.game.runTurnEvents()

        ix = 333
        self.assertGreater(ix, len(cutscene.options))

        self.game.turnMain(str(ix))

        self.assertIn("not enough information", self.app.print_stack.pop())

    def test_accept_selection_with_single_word_non_index(self):
        cutscene = Cutscene(
            self.game, [{"here it is": ["we shall"], "not here": ["no way"]}]
        )
        cutscene.start()
        self.game.runTurnEvents()

        self.game.turnMain("not")

        self.assertIn(cutscene.template[0]["not here"][0], self.app.print_stack.pop())

    def test_callable_as_cutscene_item_prints_return_value_if_string(self):
        def locusts_swarm():
            return "A swarm of locusts descends upon the land."

        cutscene = Cutscene(self.game, [locusts_swarm])

        cutscene.start()
        self.game.runTurnEvents()

        self.assertIn(locusts_swarm(), self.app.print_stack)

    def test_callable_as_cutscene_runs_and_does_not_print_if_return_value_not_string(
        self,
    ):
        self.game.locusts_evaluated = False

        def locusts_swarm():
            self.game.locusts_evaluated = True
            return 17

        cutscene = Cutscene(self.game, [locusts_swarm])

        cutscene.start()
        self.game.runTurnEvents()

        self.assertNotIn(locusts_swarm(), self.app.print_stack)
        self.assertNotIn(str(locusts_swarm()), self.app.print_stack)
        self.assertTrue(self.game.locusts_evaluated)


class TestValidateCutsceneTemplate(IFPTestCase):
    def test_invalid_top_level_template_node(self):
        with self.assertRaises(IFPError):
            Cutscene(self.game, 8)

    def test_invalid_inner_template_node(self):
        with self.assertRaises(IFPError):
            Cutscene(self.game, [{"hello": "string not list"}])

    def test_invalid_cutscene_item_type(self):
        with self.assertRaises(IFPError):
            Cutscene(self.game, [8])

    def test_dict_key_for_option_name_must_be_string(self):
        with self.assertRaises(IFPError):
            Cutscene(self.game, [{6: ["item"]}])

    def test_callable_accepting_arguments_is_invalid_item(self):
        def heron_event(n_herons):
            return f"There are {n_herons} herons."

        with self.assertRaises(IFPError):
            Cutscene(self.game, [heron_event])

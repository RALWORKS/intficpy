from .helpers import IFPTestCase


class TestInfoCommands(IFPTestCase):
    def setUp(self):
        super().setUp()
        self.game.aboutGame.title = self._get_unique_noun()
        self.game.aboutGame.author = self._get_unique_noun()
        self.game.aboutGame.betaTesterCredit = self._get_unique_noun()
        self.game.aboutGame.desc = self._get_unique_noun()
        self.game.aboutGame.game_instructions = self._get_unique_noun()

    def test_about_prints_about_components(self):
        self.game.turnMain("about")

        about_components = {
            "title": f"<b>{self.game.aboutGame.title}</b>",
            "author": f"<b>Created by {self.game.aboutGame.author}</b>",
            "betaTesterCredit": self.game.aboutGame.betaTesterCredit,
            "desc": self.game.aboutGame.desc,
        }
        for key in about_components:
            with self.subTest(component=key):
                self.assertIn(about_components[key], self.app.print_stack)

    def test_intructions_prints_instructions_components(self):
        self.game.turnMain("instructions")

        instructions_components = {
            "basic_instructions": self.game.aboutGame.basic_instructions,
            "game_instructions": self.game.aboutGame.game_instructions,
        }
        for key in instructions_components:
            with self.subTest(component=key):
                self.assertIn(instructions_components[key], self.app.print_stack)

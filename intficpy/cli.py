import os
import re

from .tokenizer import cleanInput


class TerminalApp:

    QUIT_COMMANDS = ["quit", "q"]

    def __init__(self, echo_on=False):
        self.game = None  # we let the game instance set both game.app and app.game
        self.command = None
        self.echo_on = echo_on

    def printEventText(self, event):
        for t in event.text:
            # interpret some basic html tags - br as newline, both b and i as bold text
            t = t.replace("<br>", "\n")
            t = re.sub(r"<[ib]>", "\033[1m", t)
            t = re.sub(r"<\/[ib]>", "\033[0m", t)

            print(t)
        print("\n")

    def saveFilePrompt(self, extension, filetype_desc, msg):
        cur_dir = os.getcwd()
        print(f"Enter a file to save to (current directory: {cur_dir})")
        file_name = input(">")

        if len(file_name) == 0:
            return None

        file_path = os.sep.join([cur_dir, file_name])

        if file_path.endswith(extension):
            return file_path

        if not file_path.endswith(extension):
            file_path += extension

        return file_path

    def openFilePrompt(self, extension, filetype_desc, msg):
        cur_dir = os.getcwd()
        print(f"Enter a save file (.sav) to open (current directory: {cur_dir})")
        file_name = input(">")

        if not file_name.endswith(".sav"):
            print("not a save file")
            return None

        file_path = os.sep.join([cur_dir, file_name])

        return file_path

    def runGame(self):
        if not self.game:
            raise ValueError(
                "Please create a game object, and pass in this app in order to run "
                "a game."
            )

        print("\n")

        self.game.initGame()

        while True:
            self.command = input(">")
            if cleanInput(self.command) in self.QUIT_COMMANDS:
                break
            self.game.turnMain(self.command)

        print("Goodbye.")

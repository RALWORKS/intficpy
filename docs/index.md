# How to run the game
## Setup:
- install git, Python 3, pip3, and Pipenv
- clone this repository
- clone the IFP repository
- install the dependencies (including intficpy using `pip install -e ../intficpy`)
Once you are set up, you can run the game.

1. First, make sure your pipenv is activated. If it isn't, you'll see a message about
missing Python, or things not being installed when you try to run the game.
Start pipenv by running `pipenv shell`

2. run `python game/main.py`. The game should start up in a new window.

Once you are set up

# IntFicPy Tutorial: Contents
+ [Rooms](rooms.md) - How to create rooms, and link them together
+ [Items](items.md) - How to create items and place them
+ [Characters](characters.md) - Mechanics of game characters and conversation construction

# Structure of this project
+ Docs - information about the project and instructions for working with it
+ Planning - planning documents: outlines, brainstorming, scripts, etc.
+ Game - the code for the game
    + rooms
      The code for the rooms and the map. Import all the rooms into `rooms/__init__.py`
      and link them together
    + characters
      Code for the characters in the game.
    + achievements.py
      Code for achievements & score
    + main.py
      The main game file.

# Git cheat sheet
## Quick Tips
+ talk to each other about what you're doing, and try not to have multiple people
  changing the same file at the same time. this can cause conflicts when merging
  changes.

## What can I put in this repo?
You can put any file in here - word/libreoffice documents, pictures, code, text files, etc.
There are some features of git that work best with plaintext (.txt, .py, .md, etc), but
you can still save and sync with other file types. If you want everyone on the team to
be able to access it, put it in the repo.
Please keep in mind that **this repo is public**. That means that anyone can look it
up and see the files. This allows us to host these docs in a nice format online, and
use some other features.
## How do I save my changes?
You can get a list of the files you've changed by typing
`git status`

You can save your changes in two steps:
1. **Adding:**
   This is how you tell git which files you want it to save.
   `git add docs/index.md` will add this file.
   You can `git add` as many files as you want, or use `git add -A` to add everything
   you've changed.
2. **Committing:**
   When you're happy with the files you've added, type `git commit`. You will be prompted
   to enter a message to summarise your changes. You should describe what you changed,
   aiming for a shortish sentence.

Once you've committed, type `git push` to send your commits to the repo.
## How do I sync my files?
First, you should commit any changes you have (see above). Then, type,
`git pull`
When this command completes, you should have any new changes on your machine. You may
need to refresh any files you have open (or close then open them) to see the changes.

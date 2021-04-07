# About IntFicPy
A python library for writing parser-based interactive fiction. Currently in early development.

[IntFicPy Docs](https://jsmaika.github.io/intficpy-docs/)

## Parser-based interactive fiction
Parser based interactive fiction, sometimes called text adventure, is a story displayed through text, that the reader/player interacts with by typing out commands. Typing "get lamp", for instance, will cause the character to take the lamp.

## Why IntFicPy?
All of the major systems for writing parser based interactive have their own languages, useful for nothing else. With IntFicPy, I wanted to make it possible for creators who already knew Python to use that knowledge for writing interactive fiction, and for creators new to Python to work in a language for which myriad tutorials, and a strong online community already exist.

# IntFicPy Engine
IntFicPy is a Python game engine for creating parser-based interactive fiction (text adventures). IntFicPy is designed to be comprehensive and extensible. It has 80 predefined verbs, including all the standards of the genre, many with syonyms (get/take) and alternate phrasings (put hat on/put on hat). Game creators can define their own verbs - which integrate seamlessly with the predefined verb set - in minutes. Built in support for complex conversations with NPCs, dark areas and moveable light sources, locks and keys, save/load, and much more.
### Parser
Parsing natural language commands can be challenging. For this project, the problem was simplified substantially by the conventions of interactive fiction (IF). Commands are always in the imperative tense (phrased like direct orders). Knowing this, we can guarantee the basic word order of commands.
The IntFicPy parser starts by looking at the first word of the command, which should contain the verb. It then uses clues from the command, like prepositions, and number of grammatical objects to determine which verb function to call.
### Verbs
At the time of writing, IntFicPy has 78 verbs built in. Users can also create their own verbs, specific to their games.
Each verb in IntFicPy is an instance of the Verb class. When a new instance is created, the verb is automatically added to the game's dictionary of verbs. When synonyms are added using the addSynonm method, they are also added to the dicitonary.
### Item Classes
IntFicPy currently has 28 classes for items, all subclasses of Thing. Each class of item behaves differently when used for verbs. For instance, you can put a Thing in a Container, read a Readable, unlock a Lock using a Key, or look through a Transparent.
Composite items can be created with the addComposite method, to create, for instance, a box with writing on it, or a dresser with three drawers.
Non Player Characters and Conversations
The class for non-player-characters in IntFicPy is Actor. The most important distinguishing feature of Actors is that the player can talk with them. Creators can either set up responses to Topics ("ask/tell/give/show X (about) Y", where X is an Actor, and Y is an item in the game or creator defined abstract concept), or use SpecialTopics. Special topics allow for a menu style conversation, where the player can select from topics that are suggested to them.

# Installation and Use
## First Release & Current Developments

The first full length IntFicPy game, *Island in the Storm* was entered into IFComp 2019. Many thanks to everyone who played and voted.

IntFicPy's first release, originally planned for fall 2019, is postponed until further notice, while I improve test coverage and refactor.

If you want to play around with the library, please do - and I'd love to hear your feedback - but be aware that IntFicPy is not currently stable.

## How to Install IntFicPy

After cloning the repo, install the dependencies, then the IntFicPy package.

```
$ cd intficpy
$ pipenv shell
$ pipenv install
$ pip install -e .
```
You should now be able to run the example game.
```
$ python examples/testgame.py
```
You can also run the tests.
```
$ python -m unittest discover
```

# License
IntFicPy is distributed with the MIT license (see LICENSE)

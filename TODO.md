# TODO
# Next Goals:
+ 100% test coverage for verbs
+ standardise creation API across Thing & subclasses


# Bugs
+ Parser.checkExtra: currently fails to detect nonsensically placed duplicates of words
  that are accounted for. Catches `>climb happy on desk` as invalid, but reads
  `>climb desk on desk` as equivalent to `>climb on desk`.

## Refactoring

### Add the ability to store state in a DB instead of in live Python objects
Currently, IFP stores state in live objects in Python while the game is running. It
serializes the objects and dumps to a text file for save/load.

We want to add the ability to optionally store state in a database instead, while
keeping the current system available, and the basic authors' API more or less
unchanged.

**Idea:** 2 different "data engines" for IFP. Author can choose which to use.
The data engine dictates the behaviour of `__getattr__` and `__setattr__` on all
IFPObjects in the game. First engine simply gets/sets and maybe tracks changes for undo.
Second engine sets/gets from the db entry for that object, leaving the object itself
unchanged.

**Idea:** The parser matches input to IFPObjects by querying the DB. When the match succeeds,
we *copy* the starting-state object, using a special method that allows us to set all
attributes from the DB. We pass a special game object in, that lives only as long as this
turn, and contains a reference to the *current user*. Our `__getattr__` override now
only has to perform this same copying process on any IFPObject that is accessed by an
attribute (copy, update from db, *pass along the game instance from the referring IFPObject*,
and return the copy). `__setattr__` needs to record any changes so we can save/batch
apply them to the db at the end of the turn.

1. **Auto-register all subclasses of IFPObject** -
    IFP will need to be able to reconstruct the object instances from the class, and the
    saved attributes. This means that the ORM layer will need to be able to identify &
    access the correct class object **even if this class is not part of standard IFP.**
    To facilitate this, IFPObject will track its own subclasses.

1. **Standardise the instantiation API for all IFPObject subclasses** -
    Instantiation kwargs = setting attributes on the instance. You can specify some params
    as required (and possibly some attributes as protected?) on the class.
    This will make it possible to for the query system to quickly generate needed objects
    from the db, as well as just being a much nicer API for humans.

1. **Standardise the structure of an IFP project, and create a tool to help authors set it up** -
    In the new paradigm, IFPObjects will be instantiated when they are needed (turn-by-turn),
    rather than being kept alive over the whole course of the playtime. The starting objects
    that the author creates will become, essentially, data migrations. We need to create
    an intuitive, standardised project structure that keeps these data migrations separate
    from the author's custom classes.

1. **Replace the save file with a database** -
    Replace the save file with a single-file/embeddable non-relational db.
    The save file may eventually become a json dump **of** the db that tracks progress
    during play, but maybe this is a useful intermediate step?

1. **Update the save system** -
    In the old paradigm, the save system is designed to associate each item of its data
    to a **live IFPObject instance**. This means that it does not currently save all the
    needed to **create** the instance when it is needed (once IFPObject instances cease
    to persist between turns.) Most importantly, the current save system lacks a record
    of which IFPObject subclass the reconstructed object should be an instance of.
    The goal here is to create a save/load system that has all the data needed for both
    old and new paradigm saving.

1. **Allow authors to explicitly set an entry's key for querying, and prevent duplicates** -
    Currently, the keys for all IFPObjects are generated automatically, completely
    behind the scenes. In order to give authors an easy way to uniquely identify the
    IFPObjects they create in their starting state/data migration code, we will allow
    authors to specify their own string key for any of their IFPObjects that they wish,
    and auto-generate the key as before otherwise.

1. **Build the query system** -
    We need to be able to 1) explicitly look up & rehydrate an object using its
    specified key, without immediately rehydrating every IFPObject attatched to it, 2)
    look up & rehydrate any associated IFPObject seamlessly & automatically when
    the attribute is accessed, and 3) keep track of changes made to all rehydrated
    objects over their lifetime, so the changes can be saved.

1. **Create a migrate tool to create the initial database** -
    Find a way to protect this db to prevent modification during play.

1. **Create a temporary db on game startup to store state during play** -
    Save/load becomes a json dump/load.

1. **Initially load the game from the starting state db, not the starting state code** -
    Use the query system to load the game from the db. Stop running the starting state
    IFPObject generation code during play.

1. **Only save changed attributes in the current state db & save files** -
    Each save file does not need to keep a copy of the entire game.


### Minor
+ pull out printed strings to instance properties

## Testing
+ make sure new version of inline functions works correctly in terminal mode
+ the MORE or m built in inline function needs more testing and possible refining
+ Abstract class - try breaking it with features that shouldn't be used
+ inline functions with multiple arguments
+ give thing with give enabled

### Things
+ remove all contents
+ test LightSource consume daemon

### Test Hints
+ test HintSystem pending_daemon

### Test Verbs
+ movement (climb, exit, enter, lead)
+ positions (stand, sit, lie down)
+ liquids (pour, fill, drink)
+ press, push,
+ light sources (light, extinguish)
+ clothing (wear, doff)
+ score & fullscore
+ help, about, verbs, herb help, hint, instructions
+ record & playback (record on, record off, playback)
+ built-in placeholders (jump, kill, kick, break)

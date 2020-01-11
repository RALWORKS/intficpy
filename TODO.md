# INTFICPY - Write Parser Based Interactive Fiction in Python
IntFicPy is a tool for building parser based interactive fiction using Python. Currently, IntFicPy is in preparation for the first Beta release. A demo game, planned to be released for IFComp 2019, is in early development.

## KNOWN BUGS
### Saving
+ default save location should be home folder
### Serializer
+ check validity of save file before trying to load
+ support more depth in lists/dicts
### Terminal Mode
+ some non graphical features may not be available in terminal mode
+ replace html tags
+ make sure new version of inline functions works correctly

## FEATURES THAT REQUIRE TESTING
+ the MORE or m built in inline function needs more testing and possible refining
+ Abstract class - try breaking it with features that shouldn't be used
+ inline functions with multiple arguments
+ give thing with give enabled
+ update examples/terminaltestgame.py

## Unit Tests
### Parser
### Verbs
### Travel
+ can travel between rooms
+ can travel travel between rooms using
    + TravelConnector
    + Door
    + Ladder/Stairs
### Things
+ add a Thing to a room
+ add a Thing to a Thing
    + Surface
    + Container
    + UnderSpace
+ create an item of each subclass
+ create an Abstract
+ remove all contents
+ add and remove a composite item
+ add and remove an item with a lock

##  PREPARATIONS FOR FIRST BETA (Upcoming Features)

### Convenience & Ease of Use
+ better ordering in room descriptions
### Essential New Features
+ add a set_hint_node property to Topic and SpecialTopic, to advance the current hint when a conversation point is reached
### Other New Features
+ display the game title in the GUI window title

## MAJOR CHANGES (Eventual Implementation)
+ Rewrite GUI with a different GUI module (currently using Qt - most likely will switch to kivy)
+ write script to ensure game creator compliance with IntFicPy rules and syntax
+ support multiple Player characters



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
+ make sure new version of inine functions works correctly

## FEATURES THAT REQUIRE TESTING
+ the MORE or m built in inline function needs more testing and possible refining
+ Abstract class - try breaking it with features that shouldn't be used
+ inline functions with multiple arguments
+ give thing with give enabled
+ update examples/terminaltestgame.py

##  PREPARATIONS FOR FIRST BETA (Upcoming Features)
### Convenience & Ease of Use
+ better ordering in room descriptions
### Essential New Features
+ add a set_hint_node property to Topic and SpecialTopic, to advance the current hint when a conversation point is reached
### Other New Features
+ strdobj/striobj, where objects are interpreted as strings rather than names of Things ("look up rodent in dictionary") Watch out for adjacent objects in verb syntax.
+ display the game title in the GUI window title
+ allow game creators to modify the look of the GUI from within the main gamefile

## MAJOR CHANGES (Eventual Implementation)
+ Rewrite GUI with a different GUI module (currently using Qt - most likely will switch to kivy)
+ write script to ensure game creator compliance with IntFicPy rules and syntax
+ support multiple Player characters

## LAST DOCUMENTATION UPDATE COMPLETED: 29/04/2019
(X) actor.py
(X) parser.py
(X) thing.py
(X) vocab.py
(X) gui.py
(X) player.py
(X) room.py
(X) travel.py
(X) serializer.py
(X) verb.py

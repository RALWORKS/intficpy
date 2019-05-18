# INTFICPY - Write Parser Based Interactive Fiction in Python
IntFicPy is a tool for building parser based interactive fiction using Python. Currently, IntFicPy is in preparation for the first Beta release. A demo game, planned to be released for IFComp 2019, is in early development.

## KNOWN BUGS (Immediate Priority)
### Saving
+ default save location should be home folder
### Serializer
+ conversation topics, creator-defined variables, and player knowledge are not currently saved
+ check validity of save file before trying to load
### Terminal Mode
+ some non graphical features may not be available in terminal mode
+ make sure new version of inine functions works correctly

## FEATURES THAT REQUIRE TESTING
+ make sure the search function finds all Things in the location/inventory
+ the [MORE] or <<m>> built in inline function needs more testing and possible refining
+ test thing.copyThing with saving and loading
+ the describeThing and xdescribeThing methods of Thing
+ Abstract class - try breaking it with features that shouldn't be used
+ inline functions with multiple arguments
+ give thing with give enabled

##  PREPARATIONS FOR FIRST BETA (Upcoming Features)
### Convenience & Ease of Use
+ work on interactivity range
+ creator functions that evaluate AFTER dynamic room text (<<e_funcname>> maybe?)
### Essential New Features
+ display the game title in the GUI window title
+ interactable walls
+ Doors and Keys
+ ActorSurface class with positional restrictions
+ Things with an "under" property
+ directions/directional statements up, down, enter, exit, in, out
+ stairs/ladder
+ climb/climb on
+ AbstractVerb class, where objects are interpreted as strings rather than names of Things ("look up rodent in dictionary")
+ open/closed & containers with lids, locks
### Other New Features
+ support multiple Player characters
+ compound Things
+ allow game creators to modify the look of the GUI from within the main gamefile

## MAJOR CHANGES (Eventual Implementation)
+ Rewrite GUI with a different GUI module (currently using Qt)
+ write script to ensure game creator compliance with IntFicPy rules and syntax

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

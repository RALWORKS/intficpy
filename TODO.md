# INTFICPY - Write Parser Based Interactive Fiction in Python
IntFicPy is a tool for building parser based interactive fiction using Python. Currently, IntFicPy is in preparation for the first Beta release. A demo game, planned to be released for IFComp 2019, is in early development.

## KNOWN BUGS (Immediate Priority)
### Serializer
+ conversation topics, creator-defined variables, and player knowledge are not currently saved
+ ".sav" is currently accepted as a filename to save under (fix in gui.py)
### Terminal Mode
+ some non graphical features are not available in terminal mode

##  PREPARATIONS FOR FIRST BETA (Upcoming Features)
### Convenience & Ease of Use
+ write script to ensure game creator compliance with IntFicPy rules and syntax
+ create a describe method in Thing/Container/Surface to eliminate the need for creators to modify both desc/xdesc AND base_desc/base_xdesc in for Surfaces and Containers
+ save the last few valid commands, and allow the player to input them with the up arrow key
+ improve disambiguation - save the list of Things, and allow selection by adjective
### Essential New Features
+ display the game title in the GUI window title
+ make the player interactable
+ give/show topics
+ interactable walls
+ cutscenes & enter to show more
+ Abstract class - Things referring to ideas and concepts
### Other New Features
+ support multiple Player characters
+ compound Things
+ allow game creators to modify the look of the GUI from within the main gamefile

## MAJOR CHANGES (Eventual Implementation)
+ Rewrite GUI with a different GUI module (currently using Qt)

## LAST DOCUMENTATION UPDATE COMPLETED: 29/04/2019
(*) actor.py
(*) parser.py
(*) thing.py
(*) vocab.py
(*) gui.py
(*) player.py
(*) room.py
(*) travel.py
(*) serializer.py
(*) verb.py

# INTFICPY - Write Parser Based Interactive Fiction in Python
IntFicPy is a tool for building parser based interactive fiction using Python. Currently, IntFicPy is in preparation for the first Beta release. A demo game, planned to be released for IFComp 2019, is in early development.

## TODO: CHANGES

### Save/Load and Serializer
+ check validity of save file before trying to load
+ reevaluate WHAT we want to save. might decide to explicitly not save anything that is
  not an IFP object.

### Terminal Mode & Alternate UI Support
+ purge all non graphical functionality from the GUI App class
+ replace the style parameter of app.printToGUI with a string? we could even pass in a
  CSS class
+ some non graphical features may not be available in terminal mode
+ replace html tags
+ make sure new version of inline functions works correctly

### Travel
+ put some more info into directionDict, so we can use it to get rid of the giant
  if/else blocks in the TravelConnector inits

### Refactoring
+ alternative to passing me & app around all the time:
  move the whole game into a Game class. User instantiates, and passes in an App, which
  they can write however they want, as long as it has an app.print method that takes
  the right parameters. App instance creates Parser instance. Now we don't have to pass
  me, because it's stored in app. Easier to update me, too. App still gets passed around,
  but much less.
+ Base class IFPObject that handles registration and keeps a list of
  all instances? Standardise, so we can simplify the serializer
+ pull out printed strings to instance properties


## TODO: TESTING
+ the MORE or m built in inline function needs more testing and possible refining
+ Abstract class - try breaking it with features that shouldn't be used
+ inline functions with multiple arguments
+ give thing with give enabled

### Test Parser

### Travel

### Things
+ remove all contents
+ test LightSource consume daemon

### Save/Load
+ from any given save file, loading, and saving again should always produce an identical
  file.
  tasks that might be challenging for the serializer:
    + composite items
    + deeply nested items
    + nested dicts and arrays in custom IFP object properties

### Test Hints
+ test HintSystem pending_daemon

### Test Verbs
#### Test Movement
+ climb
+ exit
+ enter
+ lead
#### Test Positions
+ stand
+ sit
+ lie down
#### Test Liquids
+ pour
+ fill
+ drink
#### Test Misc Verbs
+ press
+ push
+ light
+ extinguish
+ wear
+ doff
#### Test Score
+ score
+ fullscore
#### Test Help
+ help
+ about
+ verbs
+ herb help
+ hint
+ instructions
#### Test Record/Playback
+ record on
+ record off
+ playback
#### Test Placeholder Verbs
+ jump
+ kill
+ kick
+ break


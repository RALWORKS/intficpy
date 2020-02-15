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
#### Major Refactoring
+ IFP Turn Events System:
  - app.newBox is the wrong level of abstraction.
    Box implies **event** so handle events instead of boxes. Let creaters of UIs for
    IFP interpret an event the way they want.
    Examples of events:
    - the player's action on their turn
    - an NPC walks into a room (triggered by a timer)
    - the ground shakes and a monster rises up from the deep (triggered by the player's action)
    IFP and the game creator can assign ordering priorities to events from 0-9
    Player action event runs every turn with priority 5
    Add print strings to the events on the current turn, then evaluate all events in order.
    The game sends app.evaluateEvent (triggerEvent? runEvent? printEvent?)
    The UI app handles this however it wants.
+ replace <<m>> with an app.morePrompt (event? function tied into an event? property on an event?)
  Or don't, and just let the app handle it?
+ refactor Parser to use a new exception ParserError instead of passing around None all the time

#### Minor Ugliness
+ pull out printed strings to instance properties
+ clean up travel.py


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


# IFPObjects
The base class for all saveable objects in IntFicPy is `IFPObject`

The direct descendents of IFPObject (as of January 2020) are:
- AbstractScore (the score tracker for a game)
- Achievement
- Daemon (timers and scheduled/recurring events)
- DaemonManager (the system that tracks active Daemons in a game)
- Ending
- HintNode (A collection of Hints)
- HintSystem (the system that tracks hints for a game)
- PhysicalEntity (base class of Thing and Room)
- RoomGroup
- SaleItem
- Topic
- TravelConnector

The game (IFPGame instance) keeps track of every IFPObject associated with it by way of
its "ifp_objects" attribute - a dictionary of IFPObjects each with a unique* index.

All IFPObjects need to be instantiated with a game object, so that they can be registered.

The "ifp_objects" dictionary is used to gather and organize the objects for serializing/saving.

*Multiple IFPObjects can be stored under the same index, but the save/load system will treat
any such objects as identical or interchangable. This is sometimes useful for identical
items generated during play.

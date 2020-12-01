# Creating a room
Each room should have its own file.
Start by creating a new file in the `rooms` directory. Name it after the name of the room.
Use a name that's descriptive and unique.

For an example, here's `rooms/bathroom.py`
```python
from intficpy.room import Room # put this at the top of the file, along with any other imports

bathroom = Room("Bathroom", "This bathroom is small and bright. ")

```
Make sure you've imported the `Room` class. Then, define the room.
To create a Room, you need to pass in two parameters: name first, then description.
When the player enters our new room, the game will print
> **Bathroom**

  This bathroom is small and bright.

# Connecting rooms together
To connect your new room to an existing room, open `rooms/__init__.py`.
Near the top, import your new room.

Then, connect your room to existing rooms using the direction properties.

```python
from .start_room import start_room
from .bathroom import bathroom # here's our new room

start_room.north = bathroom
bathroom.south = start_room

```
Rooms can be connected to the north, northeast, east, southeast, south, southwest, west, and south,
as well as up, down, entrance, and exit.

Connections are one way, so if you want the player to be able to go back the way they
came, make sure to set the reverse direction.

## Room vs. OutdoorRoom
A `Room` has walls and a ceiling, where an `OutdoorRoom` does not.
If you want to create an OutdoorRoom, replace `Room` in the examples above with `OutdoorRoom`
# Adding items & scenery to a Room
For information about creating items, look at [items](items.md).

Once you have an item, you can add it to a room like this.
```python
toilet.moveTo(bathroom)
```
You should do this inside of your room file, after you've created the room.
# Doors, stairways, ladders, locks, etc.
IFP has the capacity to do more complicated things, like connecting rooms using a ladder,
or a door that opens, closes, and locks.

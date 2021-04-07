=====================
Introduction to Rooms
=====================

Creating a room
===============

Rooms in IntFicPy are objects inheriting from the `Room` class.

Every IntFicPy game needs at least one room, where the Player object is placed at the
start of the game.

For instance, we might have a starting room like this.

.. code-block:: python

    start_room = Room(
        game,
        "Shack interior",
        "A little room. Four walls, a floor, and a ceiling. ",
    )
    startroom.addThing(me)


We can create more rooms in the same way.

.. code-block:: python

    from intficpy.room import Room

    from .main import game


    bathroom = Room(game, "Bathroom", "This bathroom is small and bright. ")

To create a Room, you need to pass in two parameters: name first, then description.
When the player enters our new room, the game will print

**Bathroom**

This bathroom is small and bright.

Connecting rooms together
=========================

You can connect your room to existing rooms using the rooms' direction attributes.

.. code-block:: python

    from .start_room import start_room
    from .bathroom import bathroom # here's our new room


    start_room.north = bathroom
    bathroom.south = start_room

Rooms can be connected to the north, northeast, east, southeast, south, southwest, west, and south,
as well as up, down, entrance, and exit.

Connections are one way, so if you want the player to be able to go back the way they
came, make sure to set the reverse direction.

Room vs. OutdoorRoom
====================

A `Room` has walls and a ceiling, where an `OutdoorRoom` does not.
If you want to create an OutdoorRoom, replace `Room` in the examples above with `OutdoorRoom`
# Adding items & scenery to a Room
For information about creating items, look at [items](items.md).

Once you have an item, you can add it to a room like this.

.. code-block:: python

    toilet.moveTo(bathroom)

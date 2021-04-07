# Creating an item:
IFP has many types of item, like, Surface, Container, UnderSpace, LightSource, Lock,
and Key. Even Actor, the class for [characters](characters.md) is a type of item.
All types of item (with the exception of `Actor`, which is in `intficpy.actor`) can
be imported from `intficpy.things`.

Let's create a `Surface` in `rooms/bathroom.py`
```python
from intficpy.room import Room
from intficpy.things import Surface

from .main import game


bathroom = Room(game, "Bathroom", "This bathroom is small and bright. ")

high_shelf = Surface(game, "shelf")
high_shelf.setAdjectives(["high"])

high_shelf.moveTo(bathroom)

```
A couple of things happened here.

First, we created our Surface, `high_shelf`. Most types of item only need one parameter
for creation, which is the **name** of the item. The name should be one word, and it
should be the final word of the name we use to describe it.

So "car starter" gets "starter" for a name; "can of nails" gets "nails". If we also want
to be able to refer to "can of nails" as "can", then we have to do
```python
can_of_nails = Container(game, "nails")
can_of_nails.setAdjectives(["can", "of"])
can_of_nails.addSynonym("can")
```

Then, we set the adjectives, as demonstrated above. Give this function a list of adjectives that can describe the item. Order matters here, as the game will try to string them together to create the name it will use to talk about the item (its verbose name).

If we want to *give* the game a phrase to use for the verbose name, instead of generating
one automatically, we should set

```python
high_shelf = Surface(game, "shelf")

high_shelf._verbose_name = "high shelf"
```

Finally, we placed the item in the bathroom with `high_shelf.moveTo(bathroom)`

# Describing an item
We now have a high shelf in the bathroom. When we look at the room, or examine the shelf,
the game prints a generic description, like
> There is a shelf here.

We don't have to stick with this - we can modify it to say whatever we like!

```python
high_shelf = Surface(game, "shelf")

# this is the description that will print when you look around the room
high_shelf.description = "A high shelf stand in the corner of the room."

# this is the description that will print when you look at the shelf specifically
high_shelf.x_description = "The shelf is high, and bare."
```
As you describe items in the room, keep in mind the adjectives you're using, and try to
make sure that you set them as acceptable adjectives for the item (with `item.setAdjectives`)

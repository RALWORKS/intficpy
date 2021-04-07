# Creating a character
A character in IFP is an item of class `Actor`.

Everything we talked about when we were [learning about items](items.md) applies here.

The main difference between `Actor`s and other items is that `Actor`s can be engaged
in conversation.

Let's create an Actor in a new file, `characters/carpenter.py`
```python
from intficpy.actor import Actor

from .main import game


carpenter = Actor(game, "carpenter")

```
We'll place the carpenter in the starting room.

In `rooms/start_room.py`:
```python
from intficpy.room import Room

from .main import game


from characters.carpenter import carpenter # import our new character into the room file


start_room = Room(game, "Starting Room", "We begin here. ")

carpenter.moveTo(start_room)

```
Now that we have our character, let's customize him!
# Customizing a character
## Naming a character (or, why am I getting "There is a Joshua here"?)
Perhaps, instead of calling him, "a carpenter" or "the carpenter", we want to give our
character a name.

If you've tried giving a character a proper name, like "Joshua", you may have noticed
that the game defaults to treating this like any other word, and adds an article
(a, an, or the) before it. To get rid of this, we need to tell the game that we're
dealing with a *name* or *proper noun*. We can do so like this:
```python
from intficpy.actor import Actor

from .main import game


carpenter = Actor(game, "carpenter")
carpenter.makeProper("Joshua")

```
Now, instead of being described as "the carpenter" by the game, our character will be
just "Joshua". The game will also understand "carpenter" as a synonym for "Joshua".
## Describing a character
Characters can be described using the same methods we use for describing [items](items.md)

# Building conversations
There are two main tools for building conversations in IFP: SpecialTopics, and Topics.

## Default topics
Start building a conversation by setting a character's default topic. This can be made
to change based on game state.

The default topic is what will print for the `talk to` or `hi` verbs (unless we expresly
set a hello topic), and will also print if we ask/tell/give/show a character something
that they don't have a programmed response to.

Let's give the carpenter a default topic.

```python
from intficpy.actor import Actor

from .main import game


carpenter = Actor(game, "carpenter")
carpenter.makeProper("Joshua")

# here's where we set the default topic text
carpenter.default_topic = "\"What did you want to talk about?\" Joshua asks."
```
Now, when we talk to the carpenter, the default response will be
> "What did you want to talk about?" Joshua asks.

## SpecialTopics & conversation suggestions
Traditional interactive fiction usually uses the verbs ask, tell, give, and show to build
conversations.

SpecialTopics offer a more flexible, and fluid way to build conversations, by having
the game print several suggestions for the next topic, and letting the player choose
between them using keywords of phrases.

Consider a conversation with Joshua.

The game prints this:
> "What did you want to talk about?" Joshua asks.
> (You could muse about the nature of reality, or offer to help him with his work)

The two suggestions at the bottom indicate available SpecialTopics, which can be accessed
by typing keywords, like "offer to help" or "muse".

SpeicalTopics can be added and removed from the suggestions as the game progresses, allowing
for an evolving converation.

So how do we use SpecialTopics? Let's build the scenario above.

```python
from intficpy.actor import Actor, SpecialTopic # here's our new import

from .main import game


carpenter = Actor(game, "carpenter")
carpenter.makeProper("Joshua")

carpenter.default_topic = "\"What did you want to talk about?\" Joshua asks."

topic_nature_of_reality = SpecialTopic(
    game,
    "muse about the nature of reality",
    "You muse about the nature of reality for a while, but Joshua doesn't listen."
)
topic_help_with_work = SpecialTopic(
    game,
    "offer to help him with his work",
    "\"That's OK,\" says Joshua."
)
```
To create a SpecialTopic, pass in two arguments: first, the suggestion that will be used
to identify it, and second, the text that will be printed when the topic is selected.

We've created the topics, but they aren't suggested yet.

We can suggest them like so:
```python
carpenter.addSpecialTopic(topic_nature_of_reality)
```
If we want these topics to be available as soon as we meet the character, we can suggest
them in the character file, at the top level, like:
```python
from intficpy.actor import Actor, SpecialTopic

from .main import game


carpenter = Actor(game, "carpenter")
carpenter.makeProper("Joshua")

carpenter.default_topic = "\"What did you want to talk about?\" Joshua asks."

topic_nature_of_reality = SpecialTopic(
    "muse about the nature of reality",
    "You muse about the nature of reality for a while, but Joshua doesn't listen."
)
topic_help_with_work = SpecialTopic(
    "offer to help him with his work",
    "\"That's OK,\" says Joshua."
)

# we suggest the topics here
carpenter.addSpecialTopic(topic_nature_of_reality)
carpenter.addSpecialTopic(topic_help_with_work)
```
### Building an evolving conversation: adding and removing SpecialTopics
Now we've replicated the original example. When we talk to the carpenter, we're offered
the two suggestions. But what if we want to do something a little more complicated?

Let's say we want a new topic to unlock after we muse to the carpenter.

We'll create a new topic to suggest:
```python
topic_nature_of_reality_2 = SpecialTopic(
    game,
    "ask what his thoughts are on the nature of reality",
    # tip: spread long strings across multiple lines like this:
    # (make sure they are enclosed in parentheses)
    "Joshua pauses to think for a moment. \"God,\" he says finally. "
    "\"The universe. Humanity. It's all the same thing.\""
)
```
Now that we have our new topic, let's suggest it when `topic_nature_of_reality` is accessed.
We can do this by customizing the `func` attribute of the SpecialTopic, creating our
own, new Python function for it.
```python
# let's define these as before
topic_nature_of_reality = SpecialTopic(
    "muse about the nature of reality",
    "You muse about the nature of reality for a while, but Joshua doesn't listen."
)
topic_nature_of_reality_2 = SpecialTopic(
    "ask what his thoughts are on the nature of reality",
    "Joshua pauses to think for a moment. \"God,\" he says finally. "
    "\"The universe. Humanity. It's all the same thing.\""
)

# now, we'll write the custom function
# functions for Topics and SpecialTopics should always accept `game` as a parameter
def topic_nature_of_reality_func(game):
    # first, let's make sure we still print the topic text, and any suggestions
    game.addText(topic_nature_of_reality.text)
    carpenter.printSuggestions(game)

    # now, suggest our next topic
    carpenter.addSpecialTopic(topic_nature_of_reality_2)

topic_nature_of_reality.func = topic_nature_of_reality_func
```
Now, `topic_nature_of_reality_2` can be unlocked by musing at the carpenter.

Let's look at all of it together.
In `characters/carpenter.py`:
```python
from intficpy.actor import Actor, SpecialTopic

from .main import game


carpenter = Actor(game, "carpenter")
carpenter.makeProper("Joshua")

carpenter.default_topic = "\"What did you want to talk about?\" Joshua asks."

topic_nature_of_reality = SpecialTopic(
    game,
    "muse about the nature of reality",
    "You muse about the nature of reality for a while, but Joshua doesn't listen."
)
topic_nature_of_reality_2 = SpecialTopic(
    game,
    "ask what his thoughts are on the nature of reality",
    "Joshua pauses to think for a moment. \"God,\" he says finally. "
    "\"The universe. Humanity. It's all the same thing.\""
)
def topic_nature_of_reality_func(game):
    game.addText(topic_nature_of_reality.text)
    carpenter.printSuggestions(game)

    carpenter.addSpecialTopic(topic_nature_of_reality_2)

topic_nature_of_reality.func = topic_nature_of_reality_func

topic_help_with_work = SpecialTopic(
    game,
    "offer to help him with his work",
    "\"That's OK,\" says Joshua."
)
```
There we are!

If we want, we can use the custom topic `func` to do other things, too, like change
the carpenter's default topic, move items, or trigger achievements.

### Un-suggesting topics
You can remove a topic suggestion like this:
```python
carpenter.removeSpecialTopic(topic_nature_of_reality)

```

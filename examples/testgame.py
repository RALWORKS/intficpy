from intficpy.room import Room, OutdoorRoom
from intficpy.things import (
    Surface,
    Container,
    Clothing,
    Abstract,
    Key,
    Lock,
    UnderSpace,
)
from intficpy.thing_base import Thing
from intficpy.score import Achievement, Ending
from intficpy.travel import (
    TravelConnector,
    DoorConnector,
    LadderConnector,
    StaircaseConnector,
)
from intficpy.actor import Actor, Player, Topic, SpecialTopic
from intficpy.ifp_game import IFPGame
from intficpy.cli import TerminalApp

ex = TerminalApp()
game = IFPGame(ex)
me = Player(game)
game.setPlayer(me)

# Set the basic game information
game.aboutGame.title = "Demo Game"
game.aboutGame.author = "JSMaika"

# OPENING
def opening(game):
    # Text is fed to to App to be shown to the player in bundles called "events".
    # All events are printed at the end of the turn, ordered by their priority, from
    # lowest number, to highest.
    # Every turn will have 2 events by default - the "turn" event, where IFP puts the
    # player's actions and their outcomes, and the "command" event, where the player
    # command is echoed
    # To add text to the next turn, can, 1) add text to an existing event, with
    #   game.addTextToEvent("some event name", "New text to append!")
    # or, its shortcut for adding to the "turn" event
    #   game.addText("We'll tack this onto the turn.")
    # or, (2) you can add a new, named event, as shown below.
    game.addEvent(
        "opening",  # the name of your event
        1,  # the priority of the event. lower numbers will show first. the main turn event is 5
        (
            f"<b>{game.aboutGame.title}</b><br><br>"
            "You can hear the waves crashing on the shore outside. "
            "There are no car sounds, no human voices. "
            "You are far from any populated area. "
        ),
    )


game.gameOpening = opening  # this function will be called once when the game begins


# ACHIEVEMENTS
opalAchievement = Achievement(game, 2, "finding the opal")
keyAchievement = Achievement(game, 2, "receiving the key")

# ENDINGS
freeEnding = Ending(
    game,
    True,  # this is a good ending
    "**YOU ARE FREE**",
    "You arrive on the seashore, leaving Sarah to cower in her shack. You are free.",
)

# PLOT ESSENTIAL PROPS
silverkey = Key(game)
silverkey.setAdjectives(["silver"])

rustykey = Key(game)
rustykey.setAdjectives(["rusty"])

opal = Thing(game, "opal")
opal.makeUnique()
opal.size = 25

# ROOMS

# Start Room (Shack Interior)
startroom = Room(
    game,
    "Shack interior",
    "You are standing in a one room shack. Light filters in through a cracked, dirty window. ",
)

me.moveTo(startroom)

# ABSTRACT CONCEPTS
# Use "Abstract" items to create topics of discussion (for ask/tell Topics) that do not
# correlate to a physical item. Alternately, use them to track player knowledge
storm_concept = Abstract(game, "storm")
shack_concept = Abstract(game, "shack")
shack_concept.setAdjectives(["one", "room"])
shack_concept.makeKnown(me)


def takeOpalFunc(game):
    if not me.opaltaken:
        game.addText(
            "As you hold the opal in your hand, you're half-sure you can feel the air cooling around you. A shiver runs down your spine. Something is not right here.",
        )
        me.opaltaken = True
        opalAchievement.award(game)
        print(opal.ix)
        print(opal.ix in me.knows_about)


opal.getVerbDobj = takeOpalFunc

bench = Surface(game, "bench")
bench.can_contain_sitting_player = True
bench.can_contain_standing_player = True
bench.invItem = False
bench.description = "A rough wooden bench sits against the wall. "
bench.x_description = (
    "The wooden bench is splintering, and faded grey. It looks very old. "
)
bench.moveTo(startroom)

underbench = UnderSpace(game, "space")
underbench.contains_preposition = "in"
bench.addComposite(underbench)
# UnderSpaces that are components of another item are not described if their "description"
# attribute is None
# This also means that we cannot see what's underneath
# Set description to an empty string so we can show what's underneath without
# having to print an actual description of the UnderSpace
underbench.description = ""
underbench.full_name = "space under the bench"

box = Container(game, "box")
box.giveLid()
box.moveTo(underbench)

opal.moveTo(box)

boxlock = Lock(game, True, silverkey)
box.setLock(boxlock)

# Beach
beach = OutdoorRoom(
    game, "Beach, near the shack", "You find yourself on an abandoned beach. "
)


def beachArrival(game):
    freeEnding.endGame(game)


beach.arriveFunc = beachArrival

shackdoor = DoorConnector(game, startroom, "e", beach, "w")
shackdoor.entrance_a.description = "To the east, a door leads outside. "
shackdoor.entrance_b.description = "The door to the shack is directly west of you. "

cabinlock = Lock(game, True, rustykey)
shackdoor.setLock(cabinlock)

startroom.exit = shackdoor
beach.entrance = shackdoor

# Attic

attic = Room(game, "Shack, attic", "You are in a dim, cramped attic. ")
shackladder = LadderConnector(game, startroom, attic)
shackladder.entrance_a.description = (
    "Against the north wall is a ladder leading up to the attic. "
)
startroom.north = shackladder
silverkey.moveTo(attic)

# CHARACTERS
# Sarah
sarah = Actor(game, "Sarah")
sarah.makeProper("Sarah")
sarah.moveTo(startroom)


def sarahOpalFunc(game, dobj):
    """
    IntFicPy verbs can be overridden or customized for specific items.
    To do this, find the verb you want to customize in the intficpy.verb module.
    Note
        1) the class name of the verb
        2) whether its verbFunc method takes just a "dobj" (direct object) parameter,
           or an "iobj" (indirect object) as well
           For instance, GetVerb (as in, "get opal") takes only a direct object (here, "opal"),
           while GiveVerb (as in, "give opal to Sarah") takes an indirect object as well
           (here, "Sarah")
    Decide whether you want to override the verb for the direct, or indirect object.
    Create a new function in your game file. The first parameter will always be "game".
    If you are overriding for an indirect object, you will also need to accept a "dobj"
    parameter for the indirect object. Likewise, if you are overriding for the direct
    object of a verb that has an indirect object as well, you should accept an "iobj"
    parameter to receive the indirect object.

    Inside the function, you can perform whatever tasks you want to do to create your
    custom behaviour.

    Return True to skip the verb's normal behaviour after evaluating, or False to continue
    as normal.
    """
    if not sarah.threwkey and dobj == sarah:
        game.addText(
            '"Fine!" she cries. "Fine! Take the key and leave! "'
            '"Just get that thing away from me!" ',
        )
        game.addText("Sarah flings a rusty key at you. You catch it.")
        rustykey.moveTo(me)
        keyAchievement.award(game)
        sarah.threwkey = True
        return True


# Now that we've created our custom behaviour, we need to hook it up to evaluate when
# the verb is called on our direct or indirect object
# When creating the override function, we should have noted to class name of the IFP
# verb we're overriding.
# In this case, we're creating an override for GiveVerb and ShowVerb for the
# indirect object of the opal
# To do this, we will need to add an attribute to the opal for each verb we are overriding.
# The verb looks for overrides by chacking its objects for attributes with the following
# pattern:
#   [firstLetterLoweredClassNameOfVerb]Iobj
# or for direct object overrides:
#   [firstLetterLoweredClassNameOfVerb]Dobj
# so, for the indirect object for GiveVerb, we get the attribute, "giveVerbDobj"
# All we need to do now is assign our new function to the attribute name we derived
opal.giveVerbIobj = sarahOpalFunc
opal.showVerbIobj = sarahOpalFunc

howgethere = SpecialTopic(
    game,
    "ask how you got here",
    'You ask Sarah how you got here. She bites her lip. <br> "There was a storm," she says. "Your ship crashed on shore. I brought you inside."',
)


def sarahDefault(game):
    game.addText(sarah.default_topic)
    storm_concept.makeKnown(me)
    sarah.addSpecialTopic(howgethere)


sarah.defaultTopic = sarahDefault

opalTopic = Topic(
    game,
    '"I should never it from the cave," says Sarah. "I want nothing to do with it. If you\'re smart, you\'ll leave it where you found it."',
)
sarah.addTopic("asktell", opalTopic, opal)

shackTopic = Topic(
    game, '"It\'s not such a bad place, this shack," Sarah says. "It\'s warm. Safe."'
)
sarah.addTopic("asktell", shackTopic, shack_concept)

key2Topic = Topic(
    game,
    '"Leave that be," Sarah says, a hint of anxiety in her voice. "Some things are better left untouched."',
)
sarah.addTopic("asktellgiveshow", key2Topic, silverkey)

sarahTopic = Topic(
    game,
    '"You want to know about <i>me?</i>" Sarah says. "I\'m flattered. Just think of me as your protector."',
)
sarah.addTopic("asktell", sarahTopic, sarah)

meTopic = Topic(
    game,
    '"You were in a sorry state when I found you," Sarah says. "Be glad I brought you here."',
)
sarah.addTopic("asktell", meTopic, me)

sarah.default_topic = "Sarah scoffs."

stormTopic = Topic(
    game, 'Sarah narrows her eyes. "Yes, there was a storm yesterday." she says.'
)
sarah.addTopic("ask", stormTopic, storm_concept)

# PROGRESS TRACKING
# IntFicPy is not able to save global variables, or objects that do not inherit from an IFP
# base class
# However, IFP can save attributes added to IFP objects, such as items or characters
# This is one of the easiest ways to save progress or player choice
me.opaltaken = False
sarah.threwkey = False

# now that all our objects are set up, run the game
ex.runGame()

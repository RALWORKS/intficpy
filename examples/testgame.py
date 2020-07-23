# imports from other libraries
import sys
import random
from PyQt5.QtWidgets import QApplication

# imports from intficpy
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
import intficpy.gui as gui

app = QApplication(sys.argv)

me = Player("boy")
ex = gui.App()
game = IFPGame(me, ex)
game.turn_event_style = ex.box_style1
game.command_event_style = ex.box_style2


game.aboutGame.setInfo("WIND AND OCEAN", "JSMaika")
game.aboutGame.desc = "This is a test game for the IntFicPy parser. "

seenshackintro = False

opalAchievement = Achievement(2, "finding the opal")
keyAchievement = Achievement(2, "receiving the key")

freeEnding = Ending(
    True,
    "**YOU ARE FREE**",
    "You arrive on the seashore, leaving Sarah to cower in her shack. You are free.",
)


def test1(app):
    game.addTextToEvent("turn", "testing")
    print("test1")


def test2(app):
    global seenshackintro
    if seenshackintro:
        return ""
    else:
        seenshackintro = True
        return "You can hear the waves crashing on the shore outside. There are no car sounds, no human voices. You are far from any populated area.\n"


startroom = Room(
    "Shack interior",
    "You are standing in a one room shack. Light filters in through a cracked, dirty window. ",
)
shack_concept = Abstract("shack")
shack_key_concept = Abstract("key")
shack_key_concept.setAdjectives(["shack", "door"])
shore_concept = Abstract("shore")
shore_concept.addSynonym("outside")

startroom.addThing(me)
me.setPlayer()


def opening(game):
    game.addTextToEvent(
        "turn",
        "<b>WIND AND OCEAN: by JSMaika</b><br> You can hear the waves crashing on the shore outside. There are no car sounds, no human voices. You are far from any populated area.",
    )


game.gameOpening = opening


def addCave(game):
    cave_concept.makeKnown(me)


scarf = Clothing("scarf")
startroom.addThing(scarf)

box = Container("box", game)
box.can_contain_standing_player = True
box.can_contain_sitting_player = True
box.can_contain_lying_player = True
box.giveLid()
startroom.addThing(box)

opal = Thing("opal")
# startroom.addThing(opal)
opal.makeUnique()
opal.size = 25

box.addThing(opal)

me.opaltaken = False


def takeOpalFunc(game):
    print("TAKE")
    if not me.opaltaken:
        game.addTextToEvent(
            "turn",
            "As you hold the opal in your hand, you're half-sure you can feel the air cooling around you. A shiver runs down your spine. Something is not right here.",
        )
        me.opaltaken = True
        opalAchievement.award(game)


opal.getVerbDobj = takeOpalFunc

bottle = Thing("bottle")
bottle.setAdjectives(["old"])
startroom.addThing(bottle)

bottle2 = bottle.copyThing()
startroom.addThing(bottle2)

bench = Surface("bench", game)
bench.can_contain_sitting_player = True
bench.can_contain_standing_player = True
bench.invItem = False
bench.describeThing("A rough wooden bench sits against the wall.")
bench.xdescribeThing(
    "The wooden bench is splintering, and faded grey. It looks very old."
)
startroom.addThing(bench)
underbench = UnderSpace("space", game)
underbench.contains_preposition = "in"
bench.addComposite(underbench)
underbench.verbose_name = "space under the bench"

nails = Thing("nails")
nails.addSynonym("can")
nails.setAdjectives(["can", "of"])
bench.addThing(nails)

emptycan = Container("can", game)
emptycan.setAdjectives(["empty", "old"])
emptycan.size = 30
startroom.addThing(emptycan)

beach = OutdoorRoom(
    "Beach, near the shack", "You find yourself on an abandoned beach. "
)


def beachEnding(game):
    freeEnding.endGame(game)
    # print("hullloo")


beach.arriveFunc = beachEnding

shackdoor = DoorConnector(startroom, "e", beach, "w")
shackdoor.entranceA.describeThing("To the east, a door leads outside. ")
shackdoor.entranceB.describeThing("The door to the shack is directly west of you. ")

startroom.exit = shackdoor
beach.entrance = shackdoor

attic = Room("Shack, attic", "You are in a dim, cramped attic.")
shackladder = LadderConnector(startroom, attic)
shackladder.entranceA.describeThing(
    "Against the north wall is a ladder leading up to the attic. "
)
shackladder.entranceA.xdescribeThing(
    "Against the north wall is a ladder leading up to the attic. "
)
startroom.north = shackladder

rustykey = Key()
rustykey.setAdjectives(["rusty"])
# attic.addThing(rustykey)
cabinlock = Lock(True, rustykey)


def sarahOpalFunc(game, dobj):
    if not sarah.threwkey and dobj == sarah:
        game.addTextToEvent(
            "turn",
            '"Fine!" she cries. "Fine! Take the key and leave! Just get that thing away from me!" ',
        )
        game.addTextToEvent("turn", "Sarah flings a rusty key at you. You catch it.")
        me.addThing(rustykey)
        keyAchievement.award(app)
        sarah.threwkey = True


opal.giveVerbIobj = sarahOpalFunc
opal.showVerbIobj = sarahOpalFunc

shackdoor.setLock(cabinlock)
silverkey = Key()
silverkey.setAdjectives(["silver"])
boxlock = Lock(True, silverkey)
box.setLock(boxlock)
attic.addThing(silverkey)

rock = Thing("rock")
beach.addThing(rock)

sarah = Actor("Sarah")
sarah.makeProper("Sarah")
startroom.addThing(sarah)
howgethere = SpecialTopic(
    "ask how you got here",
    'You ask Sarah how you got here. She bites her lip. <br> "There was a storm," she says. "Your ship crashed on shore. I brought you inside."',
)
sarah.threwkey = False


def sarahDefault(game):
    game.addTextToEvent("turn", sarah.default_topic)
    sarah.addSpecialTopic(howgethere)


sarah.defaultTopic = sarahDefault

opalTopic = Topic(
    '"I should never it from the cave," says Sarah. "I want nothing to do with it. If you\'re smart, you\'ll leave it where you found it."'
)
sarah.addTopic("asktell", opalTopic, opal)

shackTopic = Topic(
    '"It\'s not such a bad place, this shack," Sarah says. "It\'s warm. Safe."'
)
sarah.addTopic("asktell", shackTopic, shack_concept)

outsideTopic = Topic(
    '"You wouldn\'t want to go out there," Sarah says. "You\'re inside for a reason. The rest of the world isn\'t safe for you."'
)
sarah.addTopic("asktell", outsideTopic, shore_concept)

keyTopic = Topic('"Key?" Sarah says. "What key? I haven\'t got any key."')
sarah.addTopic("asktell", keyTopic, shack_key_concept)
sarah.addTopic("asktell", keyTopic, cabinlock)
sarah.addTopic("asktell", keyTopic, shackdoor.entranceA)

key2Topic = Topic(
    '"Leave that be," Sarah says, a hint of anxiety in her voice. "Some things are better left untouched."'
)
sarah.addTopic("asktellgiveshow", key2Topic, silverkey)

sarahTopic = Topic(
    '"You want to know about <i>me?</i>" Sarah says. "I\'m flattered. Just think of me as your protector."'
)
sarah.addTopic("asktell", sarahTopic, sarah)

meTopic = Topic(
    '"You were in a sorry state when I found you," Sarah says. "Be glad I brought you here."'
)
sarah.addTopic("asktell", meTopic, me)

sarah.default_topic = "Sarah scoffs."

cave_concept = Abstract("cave")

caveTopic = Topic('Sarah narrows her eyes. "You don\'t want to know," she says.')
sarah.addTopic("ask", caveTopic, cave_concept)


game.initGame()
ex.show()
sys.exit(app.exec_())

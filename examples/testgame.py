# imports from other libraries
import sys
import random
from PyQt5.QtWidgets import QApplication

# imports from intficpy
from intficpy.room import Room, OutdoorRoom
from intficpy.thing import Thing, Surface, Container, Clothing, Abstract, Key, Lock, UnderSpace
from intficpy.score import Achievement, Ending
from intficpy.travel import TravelConnector, DoorConnector, LadderConnector, StaircaseConnector
from intficpy.actor import Actor, Player, Topic, SpecialTopic
import intficpy.parser as parser
import intficpy.gui as gui

app = QApplication(sys.argv)
gui.Prelim(__name__)

parser.aboutGame.setInfo("WIND AND OCEAN", "JSMaika")
parser.aboutGame.desc = "This is a test game for the IntFicPy parser. "

seenshackintro = False

opalAchievement = Achievement(2, "finding the opal")
keyAchievement = Achievement(2, "receiving the key")

freeEnding = Ending(True, "**YOU ARE FREE**", "You arrive on the seashore, leaving Sarah to cower in her shack. You are free.")

def test1(app):
	app.printToGUI("testing")
	print("test1")

def test2(app):
	global seenshackintro
	if seenshackintro:
		return ""
	else:
		seenshackintro = True
		return "You can hear the waves crashing on the shore outside. There are no car sounds, no human voices. You are far from any populated area.\n"

startroom = Room("Shack interior", "You are standing in a one room shack. Light filters in through a cracked, dirty window. <<shore_concept.makeKnown(me)>> <<shack_concept.makeKnown(me)>> <<shack_key_concept.makeKnown(me)>>")
shack_concept = Abstract("shack")
shack_key_concept = Abstract("key")
shack_key_concept.setAdjectives(["shack", "door"])
shore_concept = Abstract("shore")
shore_concept.addSynonym("outside")

me = Player("boy")
startroom.addThing(me)
me.setPlayer()

def opening(a):
	a.printToGUI("<b>WIND AND OCEAN: by JSMaika</b><br> <<m>> You can hear the waves crashing on the shore outside. There are no car sounds, no human voices. You are far from any populated area.")
parser.lastTurn.gameOpening = opening

def windFunc(me, a):
	p = random.randint(1,7)
	if p>6:
		a.newBox(1)
		a.printToGUI("The wind whistles against the shack.")

parser.daemons.add(windFunc)

def addCave(a):
	cave_concept.makeKnown(me)

scarf = Clothing("scarf")
startroom.addThing(scarf)

box = Container("box", me)
box.canStand = True
box.canSit = True
box.canLie = True
box.giveLid()
startroom.addThing(box)

opal = Thing("opal")
#startroom.addThing(opal)
opal.makeUnique()
opal.size = 25

box.addThing(opal)

opaltaken = False

def takeOpalFunc(me, app):
	global opaltaken
	if not opaltaken:
		app.printToGUI("As you hold the opal in your hand, you're half-sure you can feel the air cooling around you. A shiver runs down your spine. Something is not right here.")
		opaltaken = True
		opalAchievement.award(app)
opal.getVerbDobj = takeOpalFunc

bottle = Thing("bottle")
bottle.setAdjectives(["old"])
startroom.addThing(bottle)

bottle2 = bottle.copyThing()
startroom.addThing(bottle2)

bench = Surface("bench", me)
bench.canSit = True
bench.canStand = True
#bench.invItem = True
bench.describeThing("A rough wooden bench sits against the wall.")
bench.xdescribeThing("The wooden bench is splintering, and faded grey. It looks very old.")
startroom.addThing(bench)
underbench = UnderSpace("space", me)
underbench.contains_preposition = "in"
bench.addComposite(underbench)
underbench.verbose_name = "space under the bench"

nails = Thing("nails")
nails.addSynonym("can")
nails.setAdjectives(["can", "of"])
bench.addThing(nails)

emptycan = Container("can", me)
emptycan.setAdjectives(["empty", "old"])
emptycan.size = 30
startroom.addThing(emptycan)

beach = OutdoorRoom("Beach, near the shack", "You find yourself on an abandoned beach. ")

def beachEnding(me, app):
	freeEnding.endGame(me, app)
	#print("hullloo")
beach.arriveFunc = beachEnding

shackdoor = DoorConnector(startroom, "e", beach, "w")
shackdoor.entranceA.describeThing("To the east, a door leads outside. ")
shackdoor.entranceB.describeThing("The door to the shack is directly west of you. ")

startroom.exit = shackdoor
beach.entrance = shackdoor

attic = Room("Shack, attic", "You are in a dim, cramped attic.")
shackladder = LadderConnector(startroom, attic)
shackladder.entranceA.describeThing("Against the north wall is a ladder leading up to the attic. ")
shackladder.entranceA.xdescribeThing("Against the north wall is a ladder leading up to the attic. ")
startroom.north = shackladder

rustykey = Key()
rustykey.setAdjectives(["rusty"])
#attic.addThing(rustykey)
cabinlock = Lock(True, rustykey)

sarahthrewkey = False
def sarahOpalFunc(me, app, dobj):
	global sarahthrewkey
	if not sarahthrewkey and dobj==sarah:
		app.printToGUI("\"Fine!\" she cries. \"Fine! Take the key and leave! Just get that thing away from me!\" ")
		app.printToGUI("Sarah flings a rusty key at you. You catch it.")
		me.addThing(rustykey)
		keyAchievement.award(app)
		sarahthrewkey = True

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
howgethere = SpecialTopic("ask how you got here", "You ask Sarah how you got here. She bites her lip. <br> \"There was a storm,\" she says. \"Your ship crashed on shore. I brought you inside.\"") 

def sarahDefault(app):
	app.printToGUI(sarah.default_topic)
	howgethere.suggest(app)
sarah.defaultTopic = sarahDefault

opalTopic = Topic("\"I should never it from the cave,\" says Sarah. \"I want nothing to do with it. If you're smart, you'll leave it where you found it.\" <<cave_concept.makeKnown(me)>>")
sarah.addTopic("asktell", opalTopic, opal)

opalTopic = Topic("You hold out the opal for Sarah to see. <br> She staggers backward, raising her arms to block her face. \"Get that away from me!\" she cries, a hint of hysteria in her voice. \"Put it away. Put it away!\"")
sarah.addTopic("giveshow", opalTopic, opal)

shackTopic = Topic("\"It's not such a bad place, this shack,\" Sarah says. \"It's warm. Safe.\"")
sarah.addTopic("asktell", shackTopic, shack_concept)

outsideTopic = Topic("\"You wouldn't want to go out there,\" Sarah says. \"You're inside for a reason. The rest of the world isn't safe for you.\"")
sarah.addTopic("asktell", outsideTopic, shore_concept)

keyTopic = Topic("\"Key?\" Sarah says. \"What key? I haven't got any key.\"")
sarah.addTopic("asktell", keyTopic, shack_key_concept)
sarah.addTopic("asktell", keyTopic, cabinlock)
sarah.addTopic("asktell", keyTopic, shackdoor.entranceA)

key2Topic = Topic("\"Leave that be,\" Sarah says, a hint of anxiety in her voice. \"Some things are better left untouched.\"")
sarah.addTopic("asktellgiveshow", key2Topic, silverkey)

sarahTopic = Topic("\"You want to know about <i>me?</i>\" Sarah says. \"I'm flattered. Just think of me as your protector.\"")
sarah.addTopic("asktell", sarahTopic, sarah)

meTopic = Topic("\"You were in a sorry state when I found you,\" Sarah says. \"Be glad I brought you here.\"")
sarah.addTopic("asktell", meTopic, me)

sarah.default_topic = "Sarah scoffs."

cave_concept = Abstract("cave")

caveTopic = Topic("Sarah narrows her eyes. \"You don't want to know,\" she says.")
sarah.addTopic("ask", caveTopic, cave_concept)

screen = app.primaryScreen()
screen = screen.size()
ex = gui.App(me)
ex.show()
sys.exit(app.exec_())


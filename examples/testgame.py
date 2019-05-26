# imports from other libraries
import sys
import random
from PyQt5.QtWidgets import QApplication

# imports from intficpy
from intficpy.room import Room, OutdoorRoom
from intficpy.thing import Thing, Surface, Container, Clothing, Abstract, Key, Lock, UnderSpace
#from intficpy.player import Player
from intficpy.travel import TravelConnector, DoorConnector, LadderConnector, StaircaseConnector
from intficpy.actor import Actor, Player, Topic
import intficpy.parser as parser
import intficpy.gui as gui

app = QApplication(sys.argv)
gui.Prelim(__name__)

seenshackintro = False

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

startroom = Room("Shack interior", "You are standing in a one room shack. Light filters in through a cracked, dirty window. ")
me = Player("boy")
startroom.addThing(me)
me.setPlayer()

def opening(a):
	a.printToGUI("<b>WIND AND OCEAN: by JSMaika</b><br> <<m>> You can hear the waves crashing on the shore outside. There are no car sounds, no human voices. You are far from any populated area.")
parser.lastTurn.gameOpening = opening

def windFunc(a):
	p = random.randint(1,7)
	if p>6:
		a.newBox(1)
		a.printToGUI("The wind whistles against the shack.")

parser.daemons.add(windFunc)

def addCave(a):
	cave_concept.makeKnown(me)

scarf = Clothing("scarf")
startroom.addThing(scarf)

box = Container("box")
box.canStand = True
box.canSit = True
box.canLie = True
box.giveLid()
startroom.addThing(box)

opal = Thing("opal")
startroom.addThing(opal)
opal.makeUnique()
opal.size = 25

bottle = Thing("bottle")
bottle.setAdjectives(["old"])
startroom.addThing(bottle)

bottle2 = bottle.copyThing()
startroom.addThing(bottle2)

bench = Surface("bench")
bench.canSit = True
bench.canStand = True
#bench.invItem = True
bench.describeThing("A rough wooden bench sits against the wall.")
bench.xdescribeThing("The wooden bench is splintering, and faded grey. It looks very old.")
startroom.addThing(bench)
underbench = UnderSpace("space")
underbench.contains_preposition = "in"
bench.addComposite(underbench)
underbench.verbose_name = "space under the bench"

nails = Thing("nails")
nails.addSynonym("can")
nails.setAdjectives(["can", "of"])
bench.addOn(nails)

emptycan = Container("can")
emptycan.setAdjectives(["empty", "old"])
emptycan.size = 30
startroom.addThing(emptycan)

beach = OutdoorRoom("Beach, near the shack", "You find yourself on an abandoned beach. ")
#startroom.east = beach
#beach.west = startroom

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
attic.addThing(rustykey)
cabinlock = Lock(True, rustykey)
shackdoor.setLock(cabinlock)
#box.setLock(cabinlock)

rock = Thing("rock")
beach.addThing(rock)

sarah = Actor("Sarah")
sarah.makeProper("Sarah")
startroom.addThing(sarah)

john = Actor("janitor")
john.makeUnique()
startroom.addThing(john)
john.makeLying()

opalTopic = Topic("\"Why is there an opal here?\" You ask.<br><br>\"I brought it from the cave,\" says Sarah. \"Take it if you want. I want nothing to do with it.\" <<cave_concept.makeKnown(me)>>")
sarah.addTopic("asktell", opalTopic, opal)

opalTopic = Topic("You hold out the opal for Sarah to see. <br> She staggers backward, raising her arms to block her face. \"Get that away from me!\" she cries, a hint of hysteria in her voice. \"Put it away. Put it away!\"")
sarah.addTopic("giveshow", opalTopic, opal)

sarah.default_topic = "Sarah scoffs."

cave_concept = Abstract("cave")

caveTopic = Topic("Sarah narrows her eyes. \"You don't want to know,\" she says.")
sarah.addTopic("ask", caveTopic, cave_concept)

screen = app.primaryScreen()
screen = screen.size()
ex = gui.App(me)
ex.show()
sys.exit(app.exec_())


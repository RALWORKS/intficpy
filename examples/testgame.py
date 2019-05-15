# imports from other libraries
import sys
import random
from PyQt5.QtWidgets import QApplication

# imports from intficpy
from intficpy.room import Room
from intficpy.thing import Thing, Surface, Container, Clothing
from intficpy.player import Player
import intficpy.actor as actor
import intficpy.parser as parser
import intficpy.gui as gui


# comment out for TERMINAL MODE 
app = QApplication(sys.argv)

# uncomment for TERMINAL MODE
#class App:
#	def printToGUI(out_string, bold=False):
#		out_string = parser.extractInline(out_string)
#		if not bold:
#			print(out_string)
#		else:
#			print('\033[1m' + out_string + '\033[0m')
#app = App

seenshackintro = False

def test1(app):
	app.printToGUI("testing")

parser.inline.functions["test1"] = test1

def test2(app):
	global seenshackintro
	if seenshackintro:
		return ""
	else:
		seenshackintro = True
		return "<<m>> You can hear the waves crashing on the shore outside. There are no car sounds, no human voices. You are far from any populated area.\n"

parser.inline.functions["test2"] = test2

startroom = Room("Shack interior", "You are standing in a one room shack. Light filters in through a cracked, dirty window. There is a door to the east. <<test2>>")
me = Player(startroom)

def opening(a):
	a.printToGUI("WIND AND OCEAN: by JSMaika", True)
me.gameOpening = opening

def windFunc(a):
	p = random.randint(1,7)
	if p>6:
		a.newBox(1)
		a.printToGUI("The wind whistles against the shack.")

parser.daemons.add(windFunc)

scarf = Clothing("scarf")
startroom.addThing(scarf)

box = Container("box")
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
bench.describeThing("A rough wooden bench sits against the wall.")
bench.xdescribeThing("The wooden bench is splintering, and faded grey. It looks very old.")
startroom.addThing(bench)

nails = Thing("nails")
nails.addSynonym("can")
nails.setAdjectives(["can", "of"])
bench.addOn(nails)

emptycan = Container("can")
emptycan.setAdjectives(["empty", "old"])
emptycan.size = 30
startroom.addThing(emptycan)

beach = Room("Beach, near the shack", "You find yourself on an abandoned beach. The door to the shack is directly west of you.")
startroom.east = beach
beach.west = startroom

rock = Thing("rock")
beach.addThing(rock)

sarah = actor.Actor("Sarah")
sarah.makeProper("Sarah")
startroom.addThing(sarah)

john = actor.Actor("janitor")
john.makeUnique()
startroom.addThing(john)

opalTopic = actor.Topic("\"Why is there an opal here?\" You ask. \n\n\"I brought it,\" says Sarah. \"Take it if you want. I want nothing to do with it.\"")
sarah.addTopic("both", opalTopic, opal)

sarah.default_topic = "Sarah scoffs."


# uncomment for GUI MODE
screen = app.primaryScreen()
screen = screen.size()
ex = gui.App(me)
ex.show()
sys.exit(app.exec_())

# uncomment for TERMINAL MODE
#parser.mainLoop(me, app)

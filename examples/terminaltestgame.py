#import sys
import random
#from PyQt5.QtWidgets import QApplication

import intficpy
from intficpy.room import Room
from intficpy.thing import Thing, Surface, Container, Clothing
from intficpy.player import Player
import intficpy.actor as actor
import intficpy.parser as parser
import intficpy.gui as gui


# uncomment for GUI MODE 
#app = QApplication(sys.argv)

# uncomment for TERMINAL MODE
class App:
	def __init__(self):
		pass

	# prints to the terminal
	# uses the same method name as the GUI print method
	def printToGUI(self, out_string, bold=False):
		out_string = parser.extractInline(self, out_string)	
		if not bold:
			print(out_string)
		else:
			print('\033[1m' + out_string + '\033[0m')

# the App object for the game
app = App()

# optional/customizable game stuff
def test1(app):
	app.printToGUI("testing")

parser.inline.functions["test1"] = test1

def test2(app):
	return "You blink. "

parser.inline.functions["test2"] = test2

startroom = Room("Shack interior", "You are standing in a one room shack. Light filters in through a cracked, dirty window. There is a door to the east.")
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

bottle = Thing("bottle")
bottle.setAdjectives(["old"])
startroom.addThing(bottle)

bench = Surface("bench")
bench.base_desc = "A rough wooden bench sits against the wall."
bench.base_xdesc = "The wooden bench is splintering, and faded grey. It looks very old."
startroom.addThing(bench)

nails = Thing("nails")
nails.addSynonym("can")
nails.setAdjectives(["can", "of"])
bench.addOn(nails)

emptycan = Container("can")
emptycan.setAdjectives(["empty", "old"])
startroom.addThing(emptycan)

beach = Room("Beach, near the shack", "You find yourself on an abandoned beach. <<test2>> The door to the shack is directly west of you.")
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
#screen = app.primaryScreen()
#screen = screen.size()
#ex = gui.App(me)
#ex.show()
#sys.exit(app.exec_())

# uncomment for TERMINAL MODE
parser.mainLoop(me, app)

from . import thing
from . import verb
##############################################################
# ROOM.PY - travel functions for IntFicPy
# Defines travel functions and the direction vocab dictionary
##############################################################

# travel functions, called by getDirection in parser.py

def removePlayer(me, app):
	"""Remove the Player from the current room
	Called by travel functions
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	x = me.location
	if isinstance(x, thing.Thing):
		x.removeThing(me)
		x.containsListUpdate()
		if isinstance(x, thing.Surface):
			app.printToGUI("You get off of " + x.getArticle(True) + x.verbose_name + ".")
		else:
			app.printToGUI("You get out of " + x.getArticle(True) + x.verbose_name + ".")
		x = x.location
		while isinstance(x, thing.Thing):
			x.sub_contains[me.ix].remove(me)
			if x.sub_contains[me.ix]==[]:
				del x.sub_contains[me.ix]
			x = x.location
	else:
		me.location.removeThing(me)
		
def travelN(me, app):
	"""Travel north
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.north:
		app.printToGUI("You cannot go north from here.")
	else:
		removePlayer(me, app)
		me.location = loc.north
		me.location.addThing(me)
		app.printToGUI("You go north.")
		me.location.describe(me, app)

def travelNE(me, app):
	"""Travel northeast
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.northeast:
		app.printToGUI("You cannot go northeast from here.")
	else:		
		removePlayer(me, app)
		me.location = loc.northeast
		me.location.addThing(me)
		app.printToGUI("You go northeast.")
		me.location.describe(me, app)

def travelE(me, app):
	"""Travel east
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.east:
		app.printToGUI("You cannot go east from here.")
	else:
		removePlayer(me, app)
		me.location = loc.east
		me.location.addThing(me)
		app.printToGUI("You go east.")
		me.location.describe(me, app)

def travelSE(me, app):
	"""Travel southeast
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.southeast:
		app.printToGUI("You cannot go southeast from here.")
	else:
		removePlayer(me, app)
		me.location = loc.southeast
		me.location.addThing(me)
		app.printToGUI("You go southeast.")
		me.location.describe(me, app)

def travelS(me, app):
	"""Travel south
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.south:
		app.printToGUI("You cannot go south from here.")
	else:
		removePlayer(me, app)
		me.location = loc.south
		me.location.addThing(me)
		app.printToGUI("You go south.")
		me.location.describe(me, app)

def travelSW(me, app):
	"""Travel southwest
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.southwest:
		app.printToGUI("You cannot go southwest from here.")
	else:
		removePlayer(me, app)
		me.location = loc.southwest
		me.location.addThing(me)
		app.printToGUI("You go southwest.")
		me.location.describe(me, app)

def travelW(me, app):
	"""Travel west
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.west:
		app.printToGUI("You cannot go west from here.")
	else:
		removePlayer(me, app)
		me.location = loc.west
		me.location.addThing(me)
		app.printToGUI("You go west.")
		me.location.describe(me, app)

# travel northwest
def travelNW(me, app):
	"""Travel northwest
	Takes arguments me, pointing to the player, and app, pointing to the GUI app """
	loc = me.getOutermostLocation()
	if me.position != "standing":
		verb.standUpVerb.verbFunc(me, app)
	if not loc.northwest:
		app.printToGUI("You cannot go northwest from here.")
	else:
		removePlayer(me, app)
		me.location = loc.northwest
		me.location.addThing(me)
		app.printToGUI("You go northwest.")
		me.location.describe(me, app)


# maps user input to travel functions
directionDict = {"n": travelN, "north": travelN, "ne": travelNE, "northeast": travelNE, "e": travelE, "east": travelE, "se": travelSE, "southeast": travelSE, "s": travelS, "south": travelS, "sw": travelSW, "southwest": travelSW, "w": travelW, "west": travelW, "nw": travelNW, "northwest": travelNW}

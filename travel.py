##############################################################
# ROOM.PY - travel functions for IntFicPy
# Defines travel functions and the direction vocab dictionary
##############################################################

# travel functions, called by getDirection in parser.py

# travel north
def travelN(me, app):
	if not me.location.north:
		app.printToGUI("You cannot go north from here.")
	else:
		me.location = me.location.north
		app.printToGUI("You go north.")
		me.location.describe(me, app)

# travel northeast
def travelNE(me, app):
	if not me.location.northeast:
		app.printToGUI("You cannot go northeast from here.")
	else:
		me.location = me.location.northeast
		app.printToGUI("You go northeast.")
		me.location.describe(me, app)

# travel east
def travelE(me, app):
	if not me.location.east:
		app.printToGUI("You cannot go east from here.")
	else:
		me.location = me.location.east
		app.printToGUI("You go east.")
		me.location.describe(me, app)

# travel southeast
def travelSE(me, app):
	if not me.location.southeast:
		app.printToGUI("You cannot go southeast from here.")
	else:
		me.location = me.location.southeast
		app.printToGUI("You go southeast.")
		me.location.describe(me, app)

# travel south
def travelS(me, app):
	if not me.location.south:
		app.printToGUI("You cannot go south from here.")
	else:
		me.location = me.location.south
		app.printToGUI("You go south.")
		me.location.describe(me, app)

# travel southwest
def travelSW(me, app):
	if not me.location.southwest:
		app.printToGUI("You cannot go southwest from here.")
	else:
		me.location = me.location.southwest
		app.printToGUI("You go southwest.")
		me.location.describe(me, app)

# travel west
def travelW(me, app):
	if not me.location.west:
		app.printToGUI("You cannot go west from here.")
	else:
		me.location = me.location.west
		app.printToGUI("You go west.")
		me.location.describe(me, app)

# travel northwest
def travelNW(me, app):
	if not me.location.northwest:
		app.printToGUI("You cannot go northwest from here.")
	else:
		me.location = me.location.northwest
		app.printToGUI("You go northwest.")
		me.location.describe(me, app)


# maps user input to travel functions
directionDict = {"n": travelN, "north": travelN, "ne": travelNE, "northeast": travelNE, "e": travelE, "east": travelE, "se": travelSE, "southeast": travelSE, "s": travelS, "south": travelS, "sw": travelSW, "southwest": travelSW, "w": travelW, "west": travelW, "nw": travelNW, "northwest": travelNW}

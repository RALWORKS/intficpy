# travel functions, called by getDirection in parser

def travelN(me):
	if not me.location.north:
		print("You cannot go north from here.")
	else:
		me.location = me.location.north
		print("You go north.")
		me.location.describe(me)

def travelNE(me):
	if not me.location.northeast:
		print("You cannot go northeast from here.")
	else:
		me.location = me.location.northeast
		print("You go northeast.")
		me.location.describe(me)

def travelE(me):
	if not me.location.east:
		print("You cannot go east from here.")
	else:
		me.location = me.location.east
		print("You go east.")
		me.location.describe(me)

def travelSE(me):
	if not me.location.southeast:
		print("You cannot go southeast from here.")
	else:
		me.location = me.location.southeast
		print("You go southeast.")
		me.location.describe(me)

def travelS(me):
	if not me.location.south:
		print("You cannot go south from here.")
	else:
		me.location = me.location.south
		print("You go south.")
		me.location.describe(me)

def travelSW(me):
	if not me.location.southwest:
		print("You cannot go southwest from here.")
	else:
		me.location = me.location.southwest
		print("You go southwest.")
		me.location.describe(me)

def travelW(me):
	if not me.location.west:
		print("You cannot go west from here.")
	else:
		me.location = me.location.west
		print("You go west.")
		me.location.describe(me)

def travelNW(me):
	if not me.location.northwest:
		print("You cannot go northwest from here.")
	else:
		me.location = me.location.northwest
		print("You go northwest.")
		me.location.describe(me)


# maps user input to travel functions
directionDict = {"n": travelN, "north": travelN, "ne": travelNE, "northeast": travelNE, "e": travelE, "east": travelE, "se": travelSE, "southeast": travelSE, "s": travelS, "south": travelS, "sw": travelSW, "southwest": travelSW, "w": travelW, "west": travelW, "nw": travelNW, "northwest": travelNW}

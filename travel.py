from settings import main_file
game = __import__(main_file)
# travel functions, called by getDirection in parser

def travelN():
	if not game.me.location.north:
		print("You cannot go north from here.")
	else:
		game.me.location = game.me.location.north
		print("You go north.")
		game.me.location.describe()

def travelNE():
	if not game.me.location.northeast:
		print("You cannot go northeast from here.")
	else:
		game.me.location = game.me.location.northeast
		print("You go northeast.")
		game.me.location.describe()

def travelE():
	if not game.me.location.east:
		print("You cannot go east from here.")
	else:
		game.me.location = game.me.location.east
		print("You go east.")
		game.me.location.describe()

def travelSE():
	if not game.me.location.southeast:
		print("You cannot go southeast from here.")
	else:
		game.me.location = game.me.location.southeast
		print("You go southeast.")
		game.me.location.describe()

def travelS():
	if not game.me.location.south:
		print("You cannot go south from here.")
	else:
		game.me.location = game.me.location.south
		print("You go south.")
		game.me.location.describe()

def travelSW():
	if not game.me.location.southwest:
		print("You cannot go southwest from here.")
	else:
		game.me.location = game.me.location.southwest
		print("You go southwest.")
		game.me.location.describe()

def travelW():
	if not game.me.location.west:
		print("You cannot go west from here.")
	else:
		game.me.location = game.me.location.west
		print("You go west.")
		game.me.location.describe()

def travelNW():
	if not game.me.location.northwest:
		print("You cannot go northwest from here.")
	else:
		game.me.location = game.me.location.northwest
		print("You go northwest.")
		game.me.location.describe()


# maps user input to travel functions
directionDict = {"n": travelN, "north": travelN, "ne": travelNE, "northeast": travelNE, "e": travelE, "east": travelE, "se": travelSE, "southeast": travelSE, "s": travelS, "south": travelS, "sw": travelSW, "southwest": travelSW, "w": travelW, "west": travelW, "nw": travelNW, "northwest": travelNW}

##############################################################
# PLAYER.PY - Player class for IntFicPy
# Defines the Player class
##############################################################
# TODO: make the player interactable
# TODO: support multiple Player characters
# NOTE: Consider merging the Player and Actor classes 

class Player:
	# set basic properties for the Player instance
	# takes argument loc, a Room
	def __init__(self, loc):
		self.location = loc
		self.inventory = []
		self.sub_inventory = []
		self.wearing = []
		self.inv_max = 100
		self.desc=""
		self.knows_about = []
	
		self.gameOpening = False
		


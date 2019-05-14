##############################################################
# PLAYER.PY - Player class for IntFicPy
# Defines the Player class
##############################################################
# TODO: make the player interactable
# TODO: support multiple Player characters
# NOTE: Consider merging the Player and Actor classes 

class Player:
	"""Class for Player objects """
	def __init__(self, loc):
		"""Set basic properties for the Player instance
		Takes argument loc, a Room"""
		self.location = loc
		self.inventory = {}
		self.sub_inventory = {}
		self.wearing = {}
		self.inv_max = 100
		self.desc=""
		self.knows_about = []
	
		self.gameOpening = False
		


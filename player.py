class Player:
	location = False
	inventory = []
	sub_inventory = []
	wearing = []
	inv_max = 100
	desc=""
	knows_about = []
	
	gameOpening = False
	
	def __init__(self, loc):
		self.location = loc
		

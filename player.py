class Player:
	location = False
	inventory = []
	wearing = []
	inv_max = 100
	desc=""
	knows_about = []
	
	def __init__(self, loc):
		self.location = loc


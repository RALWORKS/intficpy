class Player:
	location = False
	inventory = []
	wearing = []
	inv_max = 100
	desc=""
	
	def __init__(self, loc):
		self.location = loc
		
	def listInv(self):
		self.invdesc = "You have "
		for thing in self.contains:
			self.fulldesc = self.fulldesc + " " + thing.desc

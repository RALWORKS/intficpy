import pickle
import copy
from . import thing
from . import room
from . import actor

#TODO: accomodate Containers

class SaveState:
	def __init__(self):
		self.custom_globals = []
		self.player = False
		self.rooms = {}
	
	def saveState(self, me, f):
		self.player = copy.copy(me)
		# inventory
		self.player.inventory = []
		self.player.sub_inventory = []
		self.player.wearing = []
		for item in me.inventory:
			self.player.inventory.append(item.ix)
		for item in me.wearing:
			self.player.wearing.append(item.ix)
		for item in me.sub_inventory:
			self.player.sub_inventory.append(item.ix)
		# room contents
		for key in room.rooms:
			self.rooms[key] = {"name": room.rooms[key].name, "desc": room.rooms[key].desc, "contains": []}
			for item in room.rooms[key].contains:
				self.rooms[key]["contains"].append(item.ix)
		
		self.player.location = me.location.ix
		
		# open save file
		if not "." in f:
			f = f + ".sav"
		savefile = open(f,"wb+")
		# Serialize
		pickle.dump(self, savefile, 0)
		savefile.close()
		return True
		
	def loadState(self, me, f, app):
		if f[-4:]!=".sav":
			f = f + ".sav"
		savefile = open(f, "rb")
		temp = pickle.load(savefile)
		me.inventory = []
		for key in temp.player.inventory:
			me.inventory.append(thing.things[key])
		me.wearing = []
		for key in temp.player.wearing:
			me.wearing.append(thing.things[key])
		for key in temp.rooms:
			room.rooms[key].name = temp.rooms[key]["name"]
			room.rooms[key].desc = temp.rooms[key]["desc"]
			room.rooms[key].contains = []
			for item in temp.rooms[key]["contains"]:
				if item[0]=="t":
					room.rooms[key].contains.append(thing.things[item])
				elif item[0]=="a":
					room.rooms[key].contains.append(actor.actors[item])
		me.location = room.rooms[temp.player.location]
		return True
		

curSave = SaveState()

# Unserialize

# Load

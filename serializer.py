import pickle
import copy
from . import thing
from . import player
from . import room
from . import actor


class SaveState:
	def __init__(self):
		self.custom_globals = []
		self.player = False
		self.rooms = {}
	
	def encodeNested(self, thing_list, loc_dict):
		for item in thing_list:
				loc = item.location
				if loc:
					loc = loc.ix
				loc_dict[item.ix] = {"verbose_name": item.verbose_name, "desc": item.desc, "location": loc, "contains": {}, "cleared": False}
				outer_item = loc_dict[item.ix]
				lvl = 0
				push = False
				lvl_dict = {}
				lvl_dict[0] = list(item.contains)
				lvl_parent = [item]
				while lvl_dict[0] != []:
					remove_scanned = []
					# pop to lower level if empty
					if lvl_dict[lvl]==[]:
						lvl_dict[lvl-1].remove(lvl_parent[-1])
						lvl_parent = lvl_parent[:-1]
						lvl = lvl - 1
					# scan items on current level
					for y in lvl_dict[lvl]:
						loc = y.location
						if loc:
							loc = loc.ix
						if not y.ix in outer_item["contains"]:
							outer_item["contains"][y.ix] = {"verbose_name": y.verbose_name, "desc": y.desc, "location": loc, "contains": {}, "cleared": False}
						# if y contains items, push into y.contains 
						if y.contains != []:
							lvl = lvl + 1
							lvl_dict[lvl] = list(y.contains)
							lvl_parent.append(y)
							push = True
							outer_item = outer_item["contains"][y.ix]
							break
						else:
							remove_scanned.append(y)
					# remove scanned items from lvl_dict
					for r in remove_scanned:
						if push:
							lvl_dict[lvl-1].remove(r)
						else:
							lvl_dict[lvl].remove(r)
							
					# reset push marker
					push = False
	
	def saveState(self, me, f):
		self.player = copy.copy(me)
		# inventory
		self.player.inventory = []
		self.player.sub_inventory = []
		self.player.wearing = []
		self.player.inventory = {}
		self.encodeNested(me.inventory, self.player.inventory)
		self.player.wearing = {}
		self.encodeNested(me.wearing, self.player.wearing)
		for item in me.sub_inventory:
			self.player.sub_inventory.append(item.ix)
		# room contents
		for key in room.rooms:
			self.rooms[key] = {"name": room.rooms[key].name, "desc": room.rooms[key].desc, "contains": {}}
			self.encodeNested(room.rooms[key].contains, self.rooms[key]["contains"])
		self.player.location = me.location.ix
		
		# open save file
		if not "." in f:
			f = f + ".sav"
		savefile = open(f,"wb+")
		# Serialize
		pickle.dump(self, savefile, 0)
		savefile.close()
		return True
	
	def dictLookup(self, ix):
		if not ix:
			return False
		elif ix[0]=="t":
			return thing.things[ix]
		elif ix[0]=="a":
			return actor.actors[ix]
		elif ix[0]=="r":
			return room.rooms[ix]
		else:
			print("unexpected ix format")
			return False
	
	def addSubContains(self, thing_in):
		x = thing_in.location
		while not isinstance(x, room.Room):
			x = x.location
			if isinstance(x, player.Player):
				x.sub_inventory.append(thing_in)
			else:
				x.sub_contains.append(thing_in)
			if not isinstance(x, room.Room):
				x.containsListUpdate()
	
	def decodeNested(self, dict_in, obj_out):
		for k, item in dict_in.items():
			outer_item = dict_in[k]
			x = self.dictLookup(k)
			x.verbose_name = item["verbose_name"]
			x.location = self.dictLookup(item["location"])
			obj_out.contains.append(x)
			# Inventory and sub_inventory should already be clear for the Player
			if (isinstance(x, thing.Surface) or isinstance(x, thing.Container)) and not outer_item["cleared"]:
				x.contains = []
				x.sub_contains = []
				outer_item["cleared"] = True
			lvl = 0
			push = False
			lvl_dict = {}
			lvl_dict[0] = outer_item["contains"]
			lvl_parent = [outer_item]
			parent_index = [x.ix]
			while lvl_dict[0] != {}:
				remove_scanned = []
				# pop if level is empty
				if lvl_dict[lvl] == {}:

					del lvl_dict[lvl-1][parent_index[-1]]
					lvl_parent = lvl_parent[:-1]
					parent_index = parent_index[:-1]
					lvl = lvl -1
					
				for y in lvl_dict[lvl]:
					y = self.dictLookup(y)
					z = lvl_parent[-1]["contains"][y.ix]
					y.verbose_name = z["verbose_name"]
					y.desc = z["desc"]
					y.location = self.dictLookup(z["location"])

					if (isinstance(y, thing.Surface) or isinstance(y, thing.Container)) and not z["cleared"]:
						y.contains = []
						y.sub_contains = []
						z["cleared"] = True

					if y.location and y not in y.location.contains:
						y.location.contains.append(y)
						if isinstance(y.location, thing.Container) or isinstance(y.location, thing.Surface):
							y.location.containsListUpdate()
					
					self.addSubContains(y)

					if z["contains"] == {}:
						remove_scanned.append(y)
					else:
						lvl_parent.append(z)
						parent_index.append(y.ix)
						lvl = lvl + 1
						push = True
						break
				for r in remove_scanned:
					if push:
						del lvl_dict[lvl-1][r.ix]
					else:
						del lvl_dict[lvl][r.ix]
				if push:
					lvl_dict[lvl] = z["contains"]
				
				# reset push marker
				push = False
			if isinstance(x.location, thing.Container) or isinstance(x.location, thing.Surface):
				x.location.containsListUpdate()
						
	def loadState(self, me, f, app):
		if f[-4:]!=".sav":
			f = f + ".sav"
		savefile = open(f, "rb")
		temp = pickle.load(savefile)
		me.inventory = []
		me.sub_inventory = []
		self.decodeNested(temp.player.inventory, me)
		me.wearing = []
		for key in temp.player.wearing:
			me.wearing.append(thing.things[key])
		for key in temp.rooms:
			room.rooms[key].name = temp.rooms[key]["name"]
			room.rooms[key].desc = temp.rooms[key]["desc"]
			room.rooms[key].contains = []
			room.rooms[key].sub_contains = []
			self.decodeNested(temp.rooms[key]["contains"], room.rooms[key])
		me.location = room.rooms[temp.player.location]
		return True
		

curSave = SaveState()


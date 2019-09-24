import pickle
import importlib
import types
import inspect

from . import thing
from . import room
from . import actor
from . import score
from . import travel
from . import parser
from . import tools
from .vocab import nounDict as vocab_nounDict

##############################################################
# SERIALIZER.PY - the save/load system for IntFicPy
# Defines the SaveState class, with methods for saving and loading games
##############################################################
# TODO: do not load bad save files. create a back up of game state before attempting to load, and restore in the event of an error AT ANY POINT during loading

class SaveState:
	"""The SaveState class is the outline for a save state, and the methods used in saving/loading
	Methods used in saving are saveState, and simplifyAttribute
	Methods used in loading are dictLookup, and loadState"""
	def __init__(self):
		self.recfile = None
		self.placed_things = []
		self.rooms_loaded = []
		self.found_items = []
					
	def saveState(self, me, f, main_file):
		"""Serializes game state and writes to a file
		Takes arguments me, the Player object, f, the path to write to, and main_file, the main Python file for the current game
		Returns True if successful, False if failed """
		saveDict = {}
		self.found_items = []
		main_module = importlib.import_module(main_file)
		creatorvars = dir(main_module)
		saveDict["vars"] = {}
		for var in creatorvars:
			x = getattr(main_module, var)
			if isinstance(x, list):
				tmp = []
				for item in x:
					tmp.append(self.simplifyAttr(x, main_module))
				saveDict["vars"][var] = tmp
			elif 	isinstance(x, dict):
				tmp = {}
				for k, val in x.items():
					tmp[k] = self.simplifyAttr(x, main_module)
				saveDict["vars"][var] = tmp
			elif not isinstance(x, types.ModuleType) and not inspect.isclass(x) and not hasattr(x, "__dict__") and not var.startswith('__'):
				saveDict["vars"][var] = x
		saveDict["score"] = {}
		for attr, value in score.score.__dict__.items():
			if isinstance(value, list):
				out = []
				for x in value:
					out.append(self.simplifyAttr(x, main_module))
				saveDict["score"][attr] = out
			else:
				saveDict["score"][attr] = self.simplifyAttr(value, main_module)
		saveDict["hints"] = {}
		for attr, value in score.hints.__dict__.items():
			if isinstance(value, list):
				out = []
				for x in value:
					out.append(self.simplifyAttr(x, main_module))
				saveDict["hints"][attr] = out
			else:
				saveDict["hints"][attr] = self.simplifyAttr(value, main_module)
		for key in thing.things:
			if key not in saveDict:	
				saveDict[key] = {}
				for attr, value in thing.things[key].__dict__.items():
					saveDict[key][attr] = self.simplifyAttr(value, main_module)
		for key in score.hintnodes:
			if key not in saveDict:	
				saveDict[key] = {}
				for attr, value in score.hintnodes[key].__dict__.items():
					if attr=="hints":
						continue
					saveDict[key][attr] = self.simplifyAttr(value, main_module)			
		for key in travel.connectors:
			if key not in saveDict:	
				saveDict[key] = {}
				for attr, value in travel.connectors[key].__dict__.items():
					saveDict[key][attr] = self.simplifyAttr(value, main_module)
		for key in actor.actors:
			if key not in saveDict:	
				saveDict[key] = {}
				for attr, value in actor.actors[key].__dict__.items():
					saveDict[key][attr] = self.simplifyAttr(value, main_module)
		for key in room.rooms:
			if key not in saveDict:	
				saveDict[key] = {}
				for attr, value in room.rooms[key].__dict__.items():
					if attr == "contains":
						saveDict[key][attr] = self.encodeRoomContents(room.rooms[key])
					else:
						saveDict[key][attr] = self.simplifyAttr(value, main_module)
		for key in score.endings:
			if key not in saveDict:	
				saveDict[key] = {}
				for attr, value in score.endings[key].__dict__.items():
					saveDict[key][attr] = self.simplifyAttr(value, main_module)
		for key in score.achievements:
			if key not in saveDict:	
				saveDict[key] = {}
				for attr, value in score.achievements[key].__dict__.items():
					saveDict[key][attr] = self.simplifyAttr(value, main_module)
		for key in actor.topics:
			if key not in saveDict:	
				saveDict[key] = {}
				for attr, value in actor.topics[key].__dict__.items():
					saveDict[key][attr] = self.simplifyAttr(value, main_module)
		saveDict["daemons"] = []
		for item in parser.daemons.funcs:
			saveDict["daemons"].append(self.simplifyAttr(item, main_module))
		if not "." in f:
			f = f + ".sav"
		savefile = open(f,"wb+")
		# Serialize
		pickle.dump(saveDict, savefile, 0)
		savefile.close()
		return True
	
	def encodeRoomContents(self, obj_in):
			dict_out = {}
			for key in obj_in.contains:
				dict_out[key] = []
				for item in obj_in.contains[key]:
					if not item in self.found_items:
						self.found_items.append(item)
						item_entry = self.encodeRoomContents(item)
						dict_out[key].append([item.ix, item_entry, False])
			return dict_out
	
	def simplifyAttr(self, value, main_module):
		"""Gets the unique key for objects that are instances of IntFicPy engine classes 
		(Thing, Actor, Achievement, Ending, Abstranct, Topic, TravelConnector, or Room)
		and replaces user-defined functions with function names
		Takes arguments value, (the attribute to be simplified), and main_module (the imported Python file of the current game) """
		if tools.isSerializableClassInstance(value):
			out = "<obj>" + value.ix
			return out
		elif isinstance(value, types.FunctionType):
			#func = getattr(main_module, value)
			out = "<func>" + value.__name__
			return out
		elif isinstance(value, types.MethodType):
			#func = getattr(main_module, value)
			meth_nam = value.__name__
			meth_inst = value.__self__
			out = ["<meth>", meth_nam, self.simplifyAttr(meth_inst, main_module)]
			#print(out)
			return out
		elif isinstance(value, list):
			out = []
			x = 0
			for x in range (0, len(value)):
				val = value[x]
				if isinstance(val, thing.Thing) or isinstance(val, actor.Actor) or isinstance(val, score.Achievement) or isinstance(val, score.AbstractScore) or isinstance(val, score.Ending) or isinstance(val, thing.Abstract) or isinstance(val, actor.Topic) or isinstance(val, travel.TravelConnector) or isinstance(val, room.Room) or isinstance(val, actor.SpecialTopic)  or isinstance(val, actor.SaleItem):
					out.append("<obj>" + val.ix)
				elif isinstance(val, types.FunctionType):
					#func = getattr(main_module, value[x])
					out.append("<func>" + val.__name__)
				else:
					out.append(val)
				x = x + 1
			return out
		elif isinstance(value, dict):
			out = {}
			for key in value:
				# check if value[key] is an item list
				if isinstance(value[key], list):
					out[key] = []
					x = 0
					for x in range (0, len(value[key])):
						val = value[key][x]
						if isinstance(val, thing.Thing) or isinstance(val, actor.Actor) or isinstance(val, score.Achievement) or isinstance(val, score.AbstractScore) or isinstance(val, score.Ending) or isinstance(val, thing.Abstract) or isinstance(val, actor.Topic) or isinstance(val, travel.TravelConnector) or isinstance(val, room.Room) or isinstance(val, actor.SpecialTopic) or isinstance(val, actor.SaleItem):
							out[key].append("<obj>" + val.ix)
						elif isinstance(val, types.FunctionType):
							#func = getattr(main_module, value[key][x])
							out[key].append("<func>" + value[key][x].__name__)
						else:
							out[key].append(val)
						x = x + 1
				elif isinstance(value[key], thing.Thing) or isinstance(value[key], actor.Actor) or isinstance(value[key], score.Achievement) or isinstance(value[key], score.AbstractScore) or isinstance(value[key], score.Ending) or isinstance(value[key], thing.Abstract) or isinstance(value[key], actor.Topic) or isinstance(value[key], travel.TravelConnector) or isinstance(value[key], room.Room) or isinstance(value[key], actor.SpecialTopic) or isinstance(value[key], actor.SaleItem):
					out[key] = "<obj>" + value[key].ix
				elif isinstance(value[key], types.FunctionType):
					#func = getattr(main_module, value[key])
					out[key] = "<func>" + value[key].__name__
			return out
		else:
			return value
	
	# NOTE: consider splitting this function to ensure consistent return types
	def dictLookup(self, ix):
		"""Checks the item index against the appropriate dictionary, and returns the corresponding in game object
		Takes one argument ix, the string used as item index
		Returns a Thing, an Actor, a Room, or None if failed"""
		if not ix:
			return None
		if "thing" in ix:
			return thing.things[ix]
		elif "actor" in ix:
			return actor.actors[ix]
		elif "hintnode" in ix:
			return score.hintnodes[ix]
		elif "room" in ix:
			out = room.rooms[ix]
			if ix not in self.rooms_loaded:
				self.rooms_loaded.append(ix)
			return out
		elif "topic" in ix:
			return actor.topics[ix]
		elif "connector" in ix:
			return travel.connectors[ix]
		elif "achievement" in ix:
			return score.achievements[ix]
		elif "ending" in ix:
			return score.endings[ix]
		else:
			print("unexpected ix format")
			return None
	
	def deserializeMethod(self, method_arr):
		if not isinstance(method_arr, list):
			print("ERROR: badly encoded method: " + str(method_arr))
			return None
		if not len(method_arr) == 3:
			print("ERROR: badly encoded method: " + str(method_arr))
			return None
		obj = method_arr[2][5:]
		obj = self.dictLookup(obj)
		out = getattr(obj, method_arr[1])
		return out
	
	def removeAll(self, obj):
		contains = []
		for key in obj.contains:
			for item in obj.contains[key]:
				contains.append(item)
		for item in contains:
			if obj.containsItem(item):
				self.removeAll(item)
				obj.removeThing(item)
	
	def emptyRooms(self, loadDict):
		for key in self.rooms_loaded:
			item = loadDict[key]
			obj = self.dictLookup(key)
			if not isinstance(obj, room.Room):
				continue
			#obj.contains = {}
			#obj.sub_contains = {}
			self.removeAll(obj)
	
	def populateRooms(self, loadDict):
		"""Updates the location, contains and subcontains properties of every item in every saved room """
		for key in self.rooms_loaded:
			item = loadDict[key]
			obj = self.dictLookup(key)
			if not isinstance(obj, room.Room):
				continue
			#obj.contains = {}
			#obj.sub_contains = {}
			#self.removeAll(obj)
			self.searchContains(obj, item["contains"])
			
	def addThingByIx(self, destination, ix):
		"""Adds a Thing to a location (Room/Thing) by index. Makes a copy if a Thing of the specified index has already been placed. 
		destination is a Thing/Room (or subclass)
		ix is the index generated at the Thing's creation (ix property/loadDict key)"""
		if ix in self.placed_things:
			item = self.dictLookup(ix).copyThing()
		else:
			self.placed_things.append(ix)
			item = self.dictLookup(ix)
		for word in item.synonyms:
			if not word in vocab_nounDict:
				vocab_nounDict[word] = [item]
			elif not item in vocab_nounDict[word]:
				vocab_nounDict[word].append(item)
		destination.addThing(item)
		return item
	
	def searchContains(self, root_obj, dict_in):
		"""Uses a recursive depth first search to place all items in the correct location 
		root_obj is the object to populate, dict_in is the dictionary to read from """
		for key in dict_in:
			for item in dict_in[key]:
				if not item[2]:
					found_obj = self.addThingByIx(root_obj, key)
					#found_obj.contains = {}
					#found_obj.sub_contains = {}
					self.removeAll(found_obj)
					item[2] = True
					self.searchContains(found_obj, item[1])	
	
	# NOTE: Currently breaks for invalid save files
	def loadState(self, me, f, app, main_file):
		"""Deserializes and reconstructs the saved Player object and game state
		Takes arguments me, the game's current Player object, f, the file to read, app, the PyQt5 GUI application, and main_file, the Python file of the current game
		Returns True if successful, else False """
		main_module = importlib.import_module(main_file)
		if not f:
			return False
		if f[-4:]!=".sav":
			return False
		savefile = open(f, "rb")
		loadDict = pickle.load(savefile)
		# superficial check for save file validity - a file that fails is definitely not valid
		try:
			score.score.total = loadDict["score"]["total"]
		except:
			return False
		score.score.possible = loadDict["score"]["possible"]
		score.score.achievements = []
		for ach in loadDict["score"]["achievements"]:
			score.score.achievements.append(self.dictLookup(ach[5:]))
		score.hints.stack = []
		for item in loadDict["hints"]["stack"]:
			score.hints.stack.append(self.dictLookup(item[5:]))
		score.hints.cur_node = loadDict["hints"]["cur_node"]
		if score.hints.cur_node:
			score.hints.cur_node = self.dictLookup(score.hints.cur_node[5:])
		for name in loadDict["vars"]:
			if isinstance(loadDict["vars"][name], list):
				tmp = []
				#print(name)
				#print(loadDict["vars"][name])
				for v in loadDict["vars"][name]:
					if isinstance(v, list):
						tmp2 = []
						for v2 in v:
							if "<obj>" in v2:
								tmp.append(self.dictLookup(v2[5:]))
							else:
								tmp.append(v2)
						tmp.append(tmp2)
					if "<obj>" in v:
						tmp.append(self.dictLookup(v[5:]))
					else:
						#print(v)
						tmp.append(v)
					#print(tmp)
					setattr(main_module, name, tmp)
			elif isinstance(loadDict["vars"][name], dict):
				tmp = {}
				for k, v in loadDict["vars"][name].items():
					if "<obj>" in v:
						tmp[k] = self.dictLookup(v[5:])
					else:
						tmp[k] = v
					setattr(main_module, name, tmp)
			else:
				setattr(main_module, name, loadDict["vars"][name])
		parser.daemons.funcs = []
		for value in loadDict["daemons"]:
			if value[0] == "<meth>":
				x = self.deserializeMethod(value)
			else:
				x = value[6:]
				x = getattr(main_module, x)
			parser.daemons.add(x)
			#parser.daemons.add(name)
		for key in loadDict:
			if key=="vars" or key=="score" or key=="daemons" or key=="hints":
				pass
			else:
				obj = self.dictLookup(key)
				for key2 in loadDict[key]:
					#attr = getattr(obj, key2)
					#if isinstance(attr, dict):
					try:
						attr = getattr(obj, key2)
					except:
						setattr(obj, key2, None)
						attr = getattr(obj, key2)	
					if isinstance(loadDict[key][key2], dict):
						attr = {}
						if key2 in ["contains", "sub_contains"]:
							# handle IFP item placement in populateRooms()
							#self.markContentsUndiscovered(loadDict[key][key2])
							continue
						for key3 in loadDict[key][key2]:
							if isinstance(loadDict[key][key2][key3], list):
								attr[key3] = []
								for x in loadDict[key][key2][key3]:
									if isinstance(x, str):
										if "<obj>" in x:
											x = x[5:]
											attr[key3].append(self.dictLookup(x))
										elif "<func>" in x:
											x = x[6:]
											attr[key3].append(getattr(main_module, x))
										else:
											attr[key3].append(loadDict[key][key2][key3])
							else:
								if isinstance(loadDict[key][key2][key3], str):
									if "<obj>" in loadDict[key][key2][key3]:
										x = loadDict[key][key2][key3][5:]
										x = self.dictLookup(x)
										attr[key3] = x
									elif "<func>" in loadDict[key][key2][key3]:
										x = loadDict[key][key2][key3][6:]
										x = getattr(main_module, x)
										attr[key3] = x
									else:
										attr[key3] = loadDict[key][key2][key3]
								else:
									attr[key3] = loadDict[key][key2][key3]
						setattr(obj, key2, attr)
					elif isinstance(loadDict[key][key2], list):
						#setattr(obj, key2, [])
						attr = []
						for x in loadDict[key][key2]:
							if isinstance(x, str):
								if "<obj>" in x:
									x = x[5:]
									attr.append(self.dictLookup(x))
								elif "<func>" in x:
									x = x[6:]
									attr.append(getattr(main_module, x))
								else:
									attr.append(x)
							else:
								attr.append(x)
						setattr(obj, key2, attr)
					elif isinstance(loadDict[key][key2], str):
						if "<obj>" in loadDict[key][key2]:
							x = loadDict[key][key2][5:]
							x = self.dictLookup(x)
							attr = x
							setattr(obj, key2, attr)
						elif "<func>" in loadDict[key][key2]:
							x = loadDict[key][key2][6:]
							x = getattr(main_module, x)
							attr= x
							setattr(obj, key2, attr)
						else:
							attr = loadDict[key][key2]
							setattr(obj, key2, attr)
					elif isinstance(attr, types.MethodType):
						pass
					else:
						setattr(obj, key2, loadDict[key][key2])
		self.emptyRooms(loadDict)
		self.populateRooms(loadDict)	
		return True
	
	def recordOn(self, app, f):
		app.printToGUI("**RECORDING ON**")
		if not f:
			return False
		if f[-4:]!=".txt":
			return False
		self.recfile = open(f, "w")
		if not self.recfile:
			app.printToGUI("Please select a valid file name to record moves. ")
		
	def recordOff(self, app):
		app.printToGUI("**RECORDING OFF**")
		if self.recfile:
			self.recfile.close()
			self.recfile = None
		
# the SaveState object
curSave = SaveState()


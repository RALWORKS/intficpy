import pickle
import copy
import importlib
import types
import inspect

from . import thing
from . import room
from . import actor
from . import score
from . import travel

##############################################################
# SERIALIZER.PY - the save/load system for IntFicPy
# Defines the SaveState class, with methods for saving and loading games
##############################################################
# TODO: save creator defined variables
# TODO: save me.knows_about
# TODO: implement a check for validity of save files prior to trying to load

class SaveState:
	"""The SaveState class is the outline for a save state, and the methods used in saving/loading
	Methods used in saving are encodeNested, and saveState
	Methods used in loading are dictLookup, addSubContains, decodeNested, and loadState"""
	def __init__(self):
		self.custom_globals = []
		self.player = False
		self.rooms = {}
		self.klist = []
					
	def saveState(self, me, f, main_file):
		"""Serializes game state and writes to a file
		Takes arguments me, the Player object, and f, the path to write to
		Returns True if successful, False if failed """
		saveDict = {}
		main_module = importlib.import_module(main_file)
		creatorvars = dir(main_module)
		saveDict["vars"] = {}
		for var in creatorvars:
			x = getattr(main_module, var)
			if not isinstance(x, types.ModuleType) and not inspect.isclass(x) and not hasattr(x, "__dict__") and not var.startswith('__'):
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
		for key in thing.things:
			if key not in saveDict:	
				saveDict[key] = {}
				for attr, value in thing.things[key].__dict__.items():
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
		if not "." in f:
			f = f + ".sav"
		savefile = open(f,"wb+")
		# Serialize
		pickle.dump(saveDict, savefile, 0)
		savefile.close()
		return True
	
	def simplifyAttr(self, value, main_module):
		if isinstance(value, thing.Thing) or isinstance(value, actor.Actor) or isinstance(value, score.Achievement) or isinstance(value, score.AbstractScore) or isinstance(value, score.Ending) or isinstance(value, thing.Abstract) or isinstance(value, actor.Topic) or isinstance(value, travel.TravelConnector) or isinstance(value, room.Room):
			out = "<obj>" + value.ix
			return out
		elif isinstance(value, types.FunctionType):
			#func = getattr(main_module, value)
			out = "<func>" + value.__name__
			return out
		elif isinstance(value, list):
			out = []
			x = 0
			for x in range (0, len(value)):
				val = value[x]
				if isinstance(val, thing.Thing) or isinstance(val, actor.Actor) or isinstance(val, score.Achievement) or isinstance(val, score.AbstractScore) or isinstance(val, score.Ending) or isinstance(val, thing.Abstract) or isinstance(val, actor.Topic) or isinstance(val, travel.TravelConnector) or isinstance(val, room.Room):
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
						if isinstance(val, thing.Thing) or isinstance(val, actor.Actor) or isinstance(val, score.Achievement) or isinstance(val, score.AbstractScore) or isinstance(val, score.Ending) or isinstance(val, thing.Abstract) or isinstance(val, actor.Topic) or isinstance(val, travel.TravelConnector) or isinstance(val, room.Room):
							out[key].append("<obj>" + val.ix)
						elif isinstance(val, types.FunctionType):
							#func = getattr(main_module, value[key][x])
							out[key].append("<func>" + value[key][x].__name__)
						else:
							out[key].append(val)
						x = x + 1
				elif isinstance(value[key], thing.Thing) or isinstance(value[key], actor.Actor) or isinstance(value[key], score.Achievement) or isinstance(value[key], score.AbstractScore) or isinstance(value[key], score.Ending) or isinstance(value[key], thing.Abstract) or isinstance(value[key], actor.Topic) or isinstance(value[key], travel.TravelConnector) or isinstance(value[key], room.Room):
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
		elif "room" in ix:
			return room.rooms[ix]
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

	# NOTE: Currently breaks for invalid save files
	def loadState(self, me, f, app, main_file):
		"""Deserializes and reconstructs the saved Player object and game state
		Takes arguments me, the game's current Player object (to be overwritten), f, the file to read, and app, the PyQt5 GUI application
		Returns True"""
		main_module = importlib.import_module(main_file)
		if not f:
			return False
		if f[-4:]!=".sav":
			return False
		savefile = open(f, "rb")
		loadDict = pickle.load(savefile)
		score.score.total = loadDict["score"]["total"]
		score.score.possible = loadDict["score"]["possible"]
		score.score.achievements = []
		for ach in loadDict["score"]["achievements"]:
			score.score.achievements.append(self.dictLookup(ach[5:]))
		for name in loadDict["vars"]:
			setattr(main_module, name, loadDict["vars"][name])
		for key in loadDict:
			if key=="vars" or key=="score":
				pass
			else:
				obj = self.dictLookup(key)
				for key2 in loadDict[key]:
					attr = getattr(obj, key2)
					if isinstance(attr, dict):
						setattr(obj, key2, {})
						attr = {}
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
						setattr(obj, key2, [])
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
					else:
						setattr(obj, key2, loadDict[key][key2])
		return True
# the SaveState object
curSave = SaveState()


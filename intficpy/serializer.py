import os
import pickle
import types

from .ifp_object import IFPObject
from .exceptions import DeserializationError, Unserializable

##############################################################
# SERIALIZER.PY - the save/load system for IntFicPy
# Defines the SaveState class, with methods for saving and loading games
##############################################################
# TODO: do not load bad save files. create a back up of game state before attempting to load, and restore in the event of an error AT ANY POINT during loading


class SaveGame:
    def __init__(self, game, filename):
        self.game = game
        self.filename = self.create_save_file_path(filename)
        self.data = {
            "ifp_objects": self.save_ifp_objects(),
            "locations": self.save_locations(),
            "active_sequence": self.serialize_attribute(
                game.parser.previous_command.sequence
            ),
        }
        self.file = open(self.filename, "wb+")
        pickle.dump(self.data, self.file, 0)
        self.file.close()

    def save_ifp_objects(self):
        out = {}
        for ix, obj in self.game.ifp_objects.items():
            out[ix] = self.serialize_ifp_object(obj)
        return out

    def serialize_ifp_object(self, obj):
        out = {}

        for attr, value in obj.__dict__.items():
            if attr in ["contains", "sub_contains"]:
                # contains is handled in the location section
                continue

            try:
                out[attr] = self.serialize_attribute(value)
            except Unserializable:
                pass

        return out

    def serialize_attribute(self, value):
        """
        Recursively serialize an attribute
        Raises Unserializable in the event of unserializable attribute
        """
        if isinstance(value, IFPObject):
            return f"<IFP>{value.ix}"

        if isinstance(value, str):
            return value

        try:
            out = {}
            for sub_attr, sub_value in value.items():
                out[sub_attr] = self.serialize_attribute(sub_value)
            return out

        except AttributeError:
            pass

        try:
            out = []
            for sub_value in value:
                out.append(self.serialize_attribute(sub_value))
            return out

        except TypeError:
            pass

        if (
            hasattr(value, "__dict__")
            or isinstance(value, types.FunctionType)
            or isinstance(value, types.MethodType)
        ):
            raise Unserializable("Cannot serialize attribute.")

        return value

    def save_locations(self):
        top_level_locations = [
            obj
            for key, obj in self.game.ifp_objects.items()
            if obj.is_top_level_location
        ]
        out = {}
        for obj in top_level_locations:
            out[obj.ix] = self.serialize_contains(obj)
        return out

    def serialize_contains(self, obj):
        serialized_contents = {}

        for key, sublist in obj.contains.items():
            serialized_contents[key] = []
            for item in sublist:
                serialized_contents[key].append(self.serialize_contains(item))

        return {"ix": obj.ix, "contains": serialized_contents, "placed": False}

    def create_save_file_path(self, filename):
        # check if we have a full path
        directory = os.path.join(*os.path.split(filename)[:-1])

        if not os.path.isdir(directory):
            filename = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), filename
            )

        if "." in filename and not filename[-4:] == ".sav":
            filename = filename[: filename.index(".")] + ".sav"

        elif not filename[-4:] == ".sav":
            filename += ".sav"

        return filename


class LoadGame:
    single_object_keys = ["active_sequence"]
    allowed_keys = ["ifp_objects", "locations", "active_sequence"]

    def __init__(self, game, filename):
        self.game = game
        self.filename = filename
        self.file = open(self.filename, "rb")
        self.data = pickle.load(self.file)
        self.file.close()

    def is_valid(self):
        """
        Try deserializing the data.
        On success, return True, and set load_file.validated_data
        On failure, delete the temporary objects, and return False
        """
        for key, subdict in self.data.items():
            if not key in self.allowed_keys:
                return False
            if key in self.single_object_keys:
                try:
                    self.deserialize_attribute(value)
                except DeserializationError:
                    return False
                continue

            for ix, obj in subdict.items():
                if not ix in self.game.ifp_objects:
                    return False

                for attr, value in obj.items():
                    try:
                        self.deserialize_attribute(value)
                    except DeserializationError:
                        return False

        self.validated_data = self.data
        return True

    def load(self):
        if not hasattr(self, "validated_data"):
            raise DeserializationError("Call is_valid before loading game.")
        self.load_ifp_objects()
        self.load_locations()
        self.game.parser.previous_command.sequence = self.deserialize_attribute(
            self.validated_data["active_sequence"]
        )
        return True

    def load_ifp_objects(self):
        if not hasattr(self, "validated_data"):
            raise DeserializationError("Call is_valid before loading game.")

        for ix, obj_data in self.validated_data["ifp_objects"].items():
            obj = self.game.ifp_objects[ix]

            for attr, value in obj_data.items():
                setattr(obj, attr, self.deserialize_attribute(value))

    def load_locations(self):
        self.placed_things = []

        if not hasattr(self, "validated_data"):
            raise DeserializationError("Call is_valid before loading game.")

        for ix, obj_data in self.validated_data["locations"].items():
            obj = self.game.ifp_objects[ix]
            self.empty_contains(obj)
            self.populate_contains(obj, obj_data["contains"])

        del self.placed_things

    def empty_contains(self, obj):
        contains = [item for ix, sublist in obj.contains.items() for item in sublist]
        for item in contains:
            if obj.containsItem(item):
                self.empty_contains(item)
                obj.removeThing(item)

    def add_thing_by_ix(self, destination, ix):
        """
        Adds a Thing to a location (Room/Thing) by index. Makes a copy if a Thing of
        the specified index has already been placed.
        destination is a PhysicalEntity subclass instance
        """
        if ix in self.placed_things:
            item = self.game.ifp_objects[ix].copyThing()
        else:
            self.placed_things.append(ix)
            item = self.game.ifp_objects[ix]
        for word in item.synonyms:
            if not word in self.game.nouns:
                self.game.nouns[word] = [item]
            elif not item in self.game.nouns[word]:
                self.game.nouns[word].append(item)
        destination.addThing(item)
        return item

    def populate_contains(self, root_obj, dict_in):
        """
        Uses a recursive depth first search to place all items in the correct location
        root_obj is the object to populate, dict_in is the dictionary to read from
        """
        for key in dict_in:
            for obj_data in dict_in[key]:
                if not obj_data["placed"]:
                    found_obj = self.add_thing_by_ix(root_obj, key)
                    self.empty_contains(found_obj)
                    obj_data["placed"] = True
                    self.populate_contains(found_obj, obj_data["contains"])

    def deserialize_attribute(self, value):
        """
        Recursively deserialize an attribute
        Raises DeserializationError in the event of an attribute
        that cannot be deseriliazed
        """
        if isinstance(value, str) and value[:5] == "<IFP>":
            ix = value[5:]
            if not ix in self.game.ifp_objects:
                raise DeserializationError
            return self.game.ifp_objects[ix]

        elif isinstance(value, str):
            return value

        try:
            out = {}
            for sub_attr, sub_value in value.items():
                out[sub_attr] = self.deserialize_attribute(sub_value)
            return out

        except AttributeError:
            pass

        try:
            out = []
            for sub_value in value:
                out.append(self.deserialize_attribute(sub_value))
            return out

        except TypeError:
            pass

        return value

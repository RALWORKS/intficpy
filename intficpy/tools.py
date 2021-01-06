# TOOLS.PY
# A collection of miscellaneous functions to simplify common tasks in IntFicPy

from .thing_base import Thing
from .actor import Actor
from .travel import travel, room
import intficpy.score as score


def isSerializableClassInstance(obj):
    return (
        isinstance(obj, Thing)
        or isinstance(obj, Actor)
        or isinstance(obj, score.Achievement)
        or isinstance(obj, score.Ending)
        or isinstance(obj, thing.Abstract)
        or isinstance(obj, actor.Topic)
        or isinstance(obj, travel.TravelConnector)
        or isinstance(obj, room.Room)
        or isinstance(obj, actor.SpecialTopic)
        or isinstance(obj, actor.SaleItem)
        or isinstance(obj, score.HintNode)
        or isinstance(obj, room.RoomGroup)
        or isinstance(obj, score.Hint)
    )


def isIFPClassInstance(obj):
    return (
        isinstance(obj, Thing)
        or isinstance(obj, Actor)
        or isinstance(obj, score.Achievement)
        or isinstance(obj, score.Ending)
        or isinstance(obj, thing.Abstract)
        or isinstance(obj, actor.Topic)
        or isinstance(obj, travel.TravelConnector)
        or isinstance(obj, room.Room)
        or isinstance(obj, actor.SpecialTopic)
        or isinstance(obj, actor.SaleItem)
        or isinstance(obj, score.HintNode)
        or isinstance(obj, room.RoomGroup)
        or isinstance(obj, score.Hint)
    )


def lineDefinesNewIx(line):
    """Checks if a line of code in the game file defines an IFP object with a new index """
    return (
        " Thing(" in line
        or " Surface(" in line
        or " Container(" in line
        or " Clothing(" in line
        or " Abstract(" in line
        or " Key(" in line
        or " Lock(" in line
        or " UnderSpace(" in line
        or " LightSource(" in line
        or " Transparent(" in line
        or " Readable(" in line
        or " Book(" in line
        or " Pressable(" in line
        or " Liquid(" in line
        or " Room(" in line
        or " OutdoorRoom(" in line
        or " RoomGroup(" in line
        or " Achievement(" in line
        or " Ending(" in line
        or " TravelConnector(" in line
        or " DoorConnector(" in line
        or " LadderConnector(" in line
        or " StaircaseConnector(" in line
        or " Actor(" in line
        or " Player(" in line
        or " Topic(" in line
        or " SpecialTopic(" in line
        or "=Thing(" in line
        or "=Surface(" in line
        or "=Container(" in line
        or "=Clothing(" in line
        or "=Abstract(" in line
        or "=Key(" in line
        or "=Lock(" in line
        or "=UnderSpace(" in line
        or "=LightSource(" in line
        or "=Transparent(" in line
        or "=Readable(" in line
        or "=Book(" in line
        or "=Pressable(" in line
        or "=Liquid(" in line
        or "=Room(" in line
        or "=OutdoorRoom(" in line
        or "=RoomGroup(" in line
        or "=Achievement(" in line
        or "=Ending(" in line
        or "=TravelConnector(" in line
        or "=DoorConnector(" in line
        or "=LadderConnector(" in line
        or "=StaircaseConnector(" in line
        or "=Actor(" in line
        or "=Player(" in line
        or "=Topic(" in line
        or "=SpecialTopic(" in line
        or ".copyThingUniqueIx(" in line
    )

# script to check for unsafe IFP object definitions
# because IFP saving/loading uses a dictionary of indeces generated at runtime, order must be preserved in object definitions
# this script checks for IFP objects defined, or copied with a unique index, in loops, methods, or functions

import sys

cur_indent = 0
next_indent = 0
errors = 0
warnings = 0
cur_line = 0
stack = []
file = input("enter path of file to analyze > ")
file = open(file, "r")
if not file:
    print("file not found")
    sys.exit(0)

last_line = []
print("\n")
for line in file:
    cur_line += 1
    next_indent = 0
    for char in line:
        if char.isspace():
            next_indent = +1
        else:
            break
    if next_indent < cur_indent:
        stack.pop()
    elif next_indent > cur_indent:
        if last_line[0] == "def":
            stack.append("def")
        elif last_line[0] in ["if", "elif", "else:"]:
            stack.append("con")
        elif last_line[0] in ["while", "for"]:
            stack.append("loop")
        else:
            stack.append("x")
    cur_indent = next_indent
    last_line = line.split()
    if "con" in stack or "def" in stack:
        if (
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
        ):
            print(
                "ERROR: Unique IntFicPy object (new index) created in function, method, or conditional statement. This should be done at the top level only, to preserve order for saving/loading"
            )
            print("line " + str(cur_line) + ":")
            print(line + "\n")
            errors += 1

    elif "loop" in stack:
        if (
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
        ):
            print(
                "WARNING: Unique IntFicPy object (new index) created in loop. This is safe only if the loop will always run the same number of times"
            )
            print("line " + str(cur_line) + ":")
            print(line + "\n")
            warnings += 1

print("Analysis complete.")
print(str(errors) + " errors; " + str(warnings) + " warnings")

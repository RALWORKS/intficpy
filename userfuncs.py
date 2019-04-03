import intficpy.parser as parser

def headache(app, me):
	app.printToGUI("You are struck by a sudden, intense headache.")
	print("ouch")

parser.inline.functions["headache"] = headache
print("now")
print(parser.inline.functions)

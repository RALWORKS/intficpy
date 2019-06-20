import sys
import os
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QVBoxLayout, QLabel, QFrame, QScrollArea, QAbstractSlider, QSizePolicy, QFileDialog
from PyQt5.QtGui import QIcon, QFont
import re
import time

from . import parser

##############################################################
# GUI.PY - the GUI for IntFicPy
# Defines the default GUI application for IntFicPy games
##############################################################
# TODO: modify App.__init__ to allow for insertion of a custom stylesheet directly from the main game file when the GUI is created
# TODO: display game title in the window title
# TODO: disallow ".sav" as a complete filename for saving

# defines the bold font for game output text
tBold=QFont()
tBold.setBold(True)

main_file = ""

class Prelim:
	def __init__(self, main_name):
		global main_file
		main_file = main_name

class App(QWidget):
	"""The App class, of which the GUI app will be an instance, creates the GUI's widgets and defines its methods """

	def __init__(self, me):
		"""Initialize the GUI
		Takes argument me, pointing to the Player """
		from .thing import reflexive
		super().__init__()
		reflexive.makeKnown(me)
		self.title = 'IntFicPy'
		self.left = 10
		self.top = 10
		self.width = 640
		self.height = 480
		self.initUI()
		self.showMaximized()
		self.me = me
		#self.newBox(1)
		parser.initGame(me, self, main_file)
		self.setStyleSheet('QFrame { border:none;}')
		self.new_obox = False
		# used for game-interrupting cutscenes
		# populated by enterForMore()
	
	def initUI(self):
		"""Build the basic user interface
		called by __init__ """
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
		
		self.textbox = QLineEdit(self)
		self.textbox.resize(280,30)
		
		 #   Container Widget
		self.widget = QWidget()
		#   Layout of Container Widget
		self.layout = QVBoxLayout(self)
		self.layout.setContentsMargins(15, 15, 15, 30)
		self.widget.setLayout(self.layout)
		
		#   Scroll Area Properties
		self.scroll = QScrollArea()
		self.scroll.setFrameShape(QFrame.Box)
		self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.widget)
		
		self.layout.setAlignment(QtCore.Qt.AlignTop)
		
		self.mainbox = QVBoxLayout()
		self.mainbox.addWidget(self.scroll)
		self.mainbox.addWidget(self.textbox)
		
		self.setLayout(self.mainbox)
		
		self.cutscene = []
		self.anykeyformore = False
	
	def turnMain(self, input_string):
		"""Sends user input to the parser each turn
		Takes argument input_string, the cleaned user input string """
		from intficpy.parser import parseInput
		quit = False
		if len(input_string)==0:
			return 0
		else:
			# parse string
			parseInput(self.me, self, input_string)
			parser.daemons.runAll(self.me, self)
	
	def newBox(self, box_style):
		"""Creates a new QFrame to wrap text in the game output area
		Takes argument box_style, an integer specifying textbox colour and style """
		self.new_obox = True
		self.obox = QFrame()
		self.obox.setFrameStyle(QFrame.StyledPanel)
		#self.olayout = QVBoxLayout()
		#self.obox.setLayout(self.olayout)
		#self.layout.addWidget(self.obox)
		if box_style==2:
			self.obox.setStyleSheet("background-color: #6be5cb; border: none; border-radius:20px; margin-bottom: 15px")
		else:
			self.obox.setStyleSheet("background-color: #d3e56b; border: none; border-radius:20px; margin-bottom: 15px")
	
	def on_click(self):
		"""Echos input, cleans input, and sends input to turnMain
		Called when the user presses return """
		textboxValue = self.textbox.text()
		self.textbox.setText("")
		self.newBox(2)
		t_echo = "> " + textboxValue
		self.printToGUI(t_echo)
		input_string = textboxValue.lower()
		input_string = re.sub(r'[^\w\s]','',input_string)
		if input_string != "save" and input_string != "load":
			self.newBox(1)
		self.turnMain(textboxValue)
	
	def keyPressEvent(self, event):
		"""Maps on_click to the enter key """
		if self.anykeyformore and self.cutscene != []:
			self.cutsceneNext()
		elif event.key() == QtCore.Qt.Key_Up and len(parser.lastTurn.turn_list) > 0:
			parser.lastTurn.back = parser.lastTurn.back - 1
			if -parser.lastTurn.back >= len(parser.lastTurn.turn_list):
				parser.lastTurn.back = 0
			self.textbox.setText(parser.lastTurn.turn_list[parser.lastTurn.back])
		elif event.key() == QtCore.Qt.Key_Down and len(parser.lastTurn.turn_list) > 0 and parser.lastTurn.back < 0:
			parser.lastTurn.back = parser.lastTurn.back + 1
			self.textbox.setText(parser.lastTurn.turn_list[parser.lastTurn.back])
		elif event.key() == QtCore.Qt.Key_Return and len(self.textbox.text())>0:
			parser.lastTurn.back = 0
			self.on_click()

	def printToGUI(self, out_string, bold=False):
		"""Prints game output to the GUI, and scrolls down
		Takes arguments out_string, the string to print, and bold, a Boolean which defaults to False
		Returns True on success """
		
		if len(self.cutscene) > 0 and not self.waiting:
			self.waiting = True
			self.cutscene.append(out_string)
			return True
		elif len(self.cutscene) > 0:
			self.cutscene[-1] = self.cutscene[-1] + "<br>" + out_string
			return True
		try:
			self.new_obox
		except:
			self.new_obox = False
		if self.new_obox:
			self.layout.addWidget(self.obox)
			self.olayout = QVBoxLayout()
			self.obox.setLayout(self.olayout)
			self.new_obox = False
		
		out = QLabel()
		if bold:
			out.setFont(tBold)
		# remove function calls from output
		out_string = parser.extractInline(self, out_string, main_file)
		out.setText(out_string)
		if "<<m>>" in out_string:
			self.enterForMore(out_string)
			return True
		else:
			self.olayout.addWidget(out)
			out.setWordWrap(True)
			out.setStyleSheet("margin-bottom: 5px")
			out.setMaximumSize(out.sizeHint())
			out.setMinimumSize(out.sizeHint())
			self.obox.setMaximumSize(self.obox.sizeHint())
			self.obox.setMinimumSize(self.obox.sizeHint())
			vbar = self.scroll.verticalScrollBar()
			vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.maximum()))
			return True

	def enterForMore(self, output_string):
		self.cutscene = output_string.split("<<m>> ")
		self.waiting = False
		self.cutscene[0] = self.cutscene[0] + " [MORE]"
		
		self.newBox(1)
		
		if self.new_obox:
			self.layout.addWidget(self.obox)
			self.olayout = QVBoxLayout()
			self.obox.setLayout(self.olayout)
			self.new_obox = False
		
		out = QLabel()
		self.cutscene[0] = parser.extractInline(self, self.cutscene[0], main_file)
		out.setText(self.cutscene[0])
		self.olayout.addWidget(out)
		out.setWordWrap(True)
		out.setStyleSheet("margin-bottom: 5px")
		out.setMaximumSize(out.sizeHint())
		out.setMinimumSize(out.sizeHint())
		self.obox.setMaximumSize(self.obox.sizeHint())
		self.obox.setMinimumSize(self.obox.sizeHint())
		vbar = self.scroll.verticalScrollBar()
		vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.maximum()))
		del self.cutscene[0]
		self.anykeyformore = True
	
	def cutsceneNext(self):
		self.anykeyformore = False
		self.newBox(1)
		if self.cutscene[0] != self.cutscene[-1]:
			self.cutscene[0] = self.cutscene[0] + " [MORE]"
		
		if self.new_obox:
			self.layout.addWidget(self.obox)
			self.olayout = QVBoxLayout()
			self.obox.setLayout(self.olayout)
			self.new_obox = False
		
		out = QLabel()
		self.olayout.addWidget(out)
		out.setWordWrap(True)
		out.setStyleSheet("margin-bottom: 5px")
		self.cutscene[0] = parser.extractInline(self, self.cutscene[0], main_file)
		out.setText(self.cutscene[0])
		out.setMaximumSize(out.sizeHint())
		out.setMinimumSize(out.sizeHint())
		self.obox.setMaximumSize(self.obox.sizeHint())
		self.obox.setMinimumSize(self.obox.sizeHint())
		vbar = self.scroll.verticalScrollBar()
		vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.maximum()))
		del self.cutscene[0]
		if not self.cutscene==[]:
			self.anykeyformore = True
	
	def getSaveFileGUI(self):
		"""Creates a QFileDialog when the user types save, and validates the selected file name
		Returns the file name or None"""
		cwd = os.getcwd()
		fname = QFileDialog.getSaveFileName(self, 'New save file', cwd, "Save files (*.sav)")
		fname = fname[0]
		if len(fname) == 0:
			return None
		# add .sav extension if necessary
		self.newBox(1)
		if not "." in fname:
			fname = fname + ".sav"
		elif (fname.index(".") - len(fname)) != -4:
			ex_start = fname.index(".")
			fname = fname[0:ex_start]
			fname = fname + ".sav"
		elif fname[-4:]!=".sav":
			fname = fname[0:-4]
			fname = fname + ".sav"
		return fname
	
	def getRecordFileGUI(self):
		"""Creates a QFileDialog when the user types save, and validates the selected file name
		Returns the file name or None"""
		cwd = os.getcwd()
		fname = QFileDialog.getSaveFileName(self, 'Choose where to save the record', cwd, "Text Files (*.txt)")
		fname = fname[0]
		if len(fname) == 0:
			return None
		# add .sav extension if necessary
		self.newBox(1)
		if not "." in fname:
			fname = fname + ".txt"
		elif (fname.index(".") - len(fname)) != -4:
			ex_start = fname.index(".")
			fname = fname[0:ex_start]
			fname = fname + ".txt"
		elif fname[-4:]!=".txt":
			fname = fname[0:-4]
			fname = fname + ".txt"
		return fname
	
	def getLoadFileGUI(self):
		"""Creates a QFileDialog when the user types load, and validates the selected file name
		Returns the file name if extension is sav, else return None """
		cwd = os.getcwd()
		#fname = QFileDialog.getSaveFileName(self, 'Open file', cwd,"Save files (*.sav)")
		fname = QFileDialog.getOpenFileName(self, 'Load save file', cwd, "Save files (*.sav)")
		fname = fname[0]
		# add .sav extension if necessary
		self.newBox(1)
		if len(fname) < 4:
			return None 
		elif fname[-4:]==".sav":
			return fname
		else:
			return None
	
	def getPlayBackFileGUI(self):
		"""Creates a QFileDialog when the user types load, and validates the selected file name
		Returns the file name if extension is sav, else return None """
		cwd = os.getcwd()
		#fname = QFileDialog.getSaveFileName(self, 'Open file', cwd,"Save files (*.sav)")
		fname = QFileDialog.getOpenFileName(self, 'Select file to play back', cwd, "Text files (*.txt)")
		fname = fname[0]
		# add .sav extension if necessary
		self.newBox(1)
		if len(fname) < 4:
			return None 
		elif fname[-4:]==".txt":
			return fname
		else:
			return None



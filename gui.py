import sys
import os
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QVBoxLayout, QLabel, QFrame, QScrollArea, QAbstractSlider, QSizePolicy, QFileDialog
from PyQt5.QtGui import QIcon, QFont
import re
import time

from . import parser

##############################################################
################## GUI.PY - the GUI for IntFicPy ####################
######## Defines the default GUI application for IntFicPy games #########
##############################################################
# TODO: modify App.__init__ to allow for insertion of a custom stylesheet directly from the main game file when the GUI is created
# TODO: display game title in the window title
# TODO: disallow ".sav" as a complete filename for saving

# defines the bold font for game output text
tBold=QFont()
tBold.setBold(True)

# the App class, of which the GUI app will be an instance, creates the GUI's widgets and defines its methods
class App(QWidget):
	
	# initiilaize the GUI
	# takes argument me, pointing to the Player
	def __init__(self, me):
		super().__init__()
		self.title = 'IntFicPy'
		self.left = 10
		self.top = 10
		self.width = 640
		self.height = 480
		self.initUI()
		self.showMaximized()
		self.me = me
		
		self.newBox(1)
		
		parser.initGame(me, self)
		self.setStyleSheet('QFrame { border:none;}')
	
	# build the basic user interface
	# called by __init__ 
	def initUI(self):
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
	
	# sends user input to the parser each turn
	# takes argument input_string, the cleaned user input string
	def turnMain(self, input_string):
		from intficpy.parser import parseInput
		quit = False
		if len(input_string)==0:
			return 0
		else:
			# parse string
			parseInput(self.me, self, input_string)
			parser.daemons.runAll(self)
	
	# creates a new QFrame to wrap text in the game output area
	# takes argument c, an integer specifying textbox colour and style
	def newBox(self, c):
		self.obox = QFrame()
		self.obox.setFrameStyle(QFrame.StyledPanel)
		self.olayout = QVBoxLayout()
		self.obox.setLayout(self.olayout)
		self.layout.addWidget(self.obox)
		if c==2:
			self.obox.setStyleSheet("background-color: #6be5cb; border: none; border-radius:20px; margin-bottom: 15px")
		else:
			self.obox.setStyleSheet("background-color: #d3e56b; border: none; border-radius:20px; margin-bottom: 15px")
	
	# echos input, cleans input, and sends input to turnMain
	# called when the user presses return
	def on_click(self):
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
	
	# maps on_click to the enter key
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Return and len(self.textbox.text())>0:
			self.on_click()

	# prints game output to the GUI, and scrolls down
	# takes arguments out_string, the string to print, and bold, a Boolean which defaults to False
	def printToGUI(self, out_string, bold=False):
		out = QLabel()
		if bold:
			out.setFont(tBold)
		# remove function calls from output
		out_string = parser.extractInline(self, out_string)	
		out.setText(out_string)
		#self.layout.addWidget(out)
		self.olayout.addWidget(out)
		out.setWordWrap(True)
		out.setStyleSheet("margin-bottom: 5px")
		out.setMaximumSize(out.sizeHint())
		out.setMinimumSize(out.sizeHint())
		self.obox.setMaximumSize(self.obox.sizeHint())
		self.obox.setMinimumSize(self.obox.sizeHint())
		vbar = self.scroll.verticalScrollBar()
		vbar.rangeChanged.connect(lambda: vbar.setValue(vbar.maximum()))
	
	# creates a QFileDialog when the user types save, and validates the selected file name
	# returns the file name
	def getSaveFileGUI(self):
		cwd = os.getcwd()
		#fname = QFileDialog.getSaveFileName(self, 'Open file', cwd,"Save files (*.sav)")
		fname = QFileDialog.getSaveFileName(self, 'New save file', cwd, "Save files (*.sav)")
		fname = fname[0]
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
	
	# creates a QFileDialog when the user types load, and validates the selected file name
	# returns the file name if extension is sav, else return None
	def getLoadFileGUI(self):
		cwd = os.getcwd()
		#fname = QFileDialog.getSaveFileName(self, 'Open file', cwd,"Save files (*.sav)")
		fname = QFileDialog.getOpenFileName(self, 'Load save file', cwd, "Save files (*.sav)")
		fname = fname[0]
		# add .sav extension if necessary
		self.newBox(1)
		#print(fname)
		print(fname[-4:])
		if fname[-4:]==".sav":
			return fname
		else:
			return None



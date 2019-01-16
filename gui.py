import sys
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QVBoxLayout, QLabel, QFrame, QScrollArea, QAbstractSlider, QSizePolicy
from PyQt5.QtGui import QIcon, QFont
import re
import time

from . import parser

tBold=QFont()
tBold.setBold(True)

class App(QWidget):

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
		#self.scroll.setStyleSheet("border:none")
		self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.widget)
		
		self.layout.setAlignment(QtCore.Qt.AlignTop)
		
		self.mainbox = QVBoxLayout()
		self.mainbox.addWidget(self.scroll)
		#self.mainbox.addStretch()
		self.mainbox.addWidget(self.textbox)
		
		self.setLayout(self.mainbox)
		
	def turnMain(self, input_string):
		from intficpy.parser import parseInput
		
		quit = False
		#roomDescribe(me)
		#while not quit:
		# first, print room description
		#me.location.describe()
		# clean string
		input_string = input_string.lower()
		input_string = re.sub(r'[^\w\s]','',input_string)
		# check for quit command
		#if(input_string=="q" or input_string=="quit"):
			#print("Goodbye.")
			#quit = True
		if len(input_string)==0:
			return 0
		else:
			# parse string
			parseInput(self.me, self, input_string)
	
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
	
	def on_click(self):
		textboxValue = self.textbox.text()
		#QMessageBox.question(self, 'Message - pythonspot.com', "You typed: " + textboxValue, QMessageBox.Ok, QMessageBox.Ok)
		self.textbox.setText("")
		self.newBox(2)
		t_echo = "> " + textboxValue
		self.printToGUI(t_echo)
		self.newBox(1)
		self.turnMain(textboxValue)
	
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Return:
			self.on_click()

	def printToGUI(self, out_string, bold=False):
		out = QLabel()
		if bold:
			out.setFont(tBold)
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

#if __name__ == '__main__':
#app = QApplication(sys.argv)
#screen = app.primaryScreen()
#screen = screen.size()
#ex = App()
#ex.show()
#sys.exit(app.exec_())

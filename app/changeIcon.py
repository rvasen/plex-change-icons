import getpass
import os
import platform
import sys
import sqlite3
from datetime import datetime
from PySide.QtCore import *
from PySide.QtGui import *
from shutil import copyfile

class MainPage(QWidget):
	def __init__(self, parent=None):
		#Set up window title and dimensions
		QWidget.__init__(self, parent)
		self.setWindowTitle("Change Library Icons for Plex")
		self.setFixedWidth(450)
		self.setFixedHeight(370)

		#Create and populate dropdown menu for selecting library to have icon changed
		selectLibraryLabel = QLabel("Select Library for Changing Icon:")
		selectLibraryLabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		self.selectLibraryDropdown = QComboBox()
		self.selectLibraryDropdown.addItems(self.findLibraries(True))

		#Create button for selecting icon for file; calls function to pull up a file select dialog
		selectIconButton = QPushButton("Select File for Icon")
		selectIconButton.clicked.connect(self.selectIconFile)

		#Displays directory of selected file
		selectedFileLabel = QLabel("Selected File:")
		self.selectedFile = QLabel("")
		self.selectedFile.setFrameStyle(QFrame.Panel | QFrame.Sunken)

		#Place where user enters URL for picture if retrieving from internet
		selectFileUrlLabel = QLabel("Select URL For Picture:")
		self.selectFileUrl = QLineEdit(self)
		self.selectFileUrl.setText("http://")

		#Displays note to user to give more explicit directions
		noteLabel = QLabel("Note: This GUI gives the option to use a file locally or fetch one from a URL. Fill the field depending on which method you'd like to use. If you fill both, the local file will be used. Also, if you would like to use a file locally, please make sure the file is in a shared folder and make sure your device has access to this folder over the LAN.")
		noteLabel.setWordWrap(True)

		#Create push buttons for doing different actions; will all be added to same QGroupBox with horizontal layout
		createBackupButton = QPushButton("Backup File")
		createBackupButton.clicked.connect(self.createBackup)

		retrieveBackupButton = QPushButton("Retrieve Backup File")
		#Calls a function to open a message box to make sure user does not accidentally overwrite database with backup
		retrieveBackupButton.clicked.connect(self.retrieveAlert)

		submitButton = QPushButton("Submit Icon Change")
		submitButton.clicked.connect(self.changeIcon)

		#All information given to and entered by the user is arranged in a group box with a QVBoxLayout (vertical) while action buttons are in a group box at the bottom with a QHBoxLayout (horizontal)
		fileGroup = QGroupBox("Choose New Library Icon:")
		submitGroup = QGroupBox("")

		submitGroup.setFixedHeight(50)

		fileGroupLayout = QVBoxLayout()
		submitGroupLayout = QHBoxLayout()

		fileGroupLayout.addWidget(selectLibraryLabel)
		fileGroupLayout.addWidget(self.selectLibraryDropdown)
		fileGroupLayout.addWidget(selectIconButton)
		fileGroupLayout.addWidget(selectedFileLabel)
		fileGroupLayout.addWidget(self.selectedFile)
		fileGroupLayout.addWidget(selectFileUrlLabel)
		fileGroupLayout.addWidget(self.selectFileUrl)
		fileGroupLayout.addWidget(noteLabel)

		submitGroupLayout.addWidget(createBackupButton)
		submitGroupLayout.addWidget(retrieveBackupButton)
		submitGroupLayout.addWidget(submitButton)

		fileGroup.setLayout(fileGroupLayout)
		submitGroup.setLayout(submitGroupLayout)

		#Glue two groups together in the main layout
		mainLayout = QVBoxLayout(self)
		mainLayout.addWidget(fileGroup)
		mainLayout.addWidget(submitGroup)

		self.setLayout(mainLayout)

	def findLibraries(self, firstTry):
		try:
			#firstTry is a parameter used to determine whether this function is being called from MainPage.__init__ or from selectDBFile (used when database is not found in default location)
			if(firstTry):
				#Determines OS to determine which default location to look in; only supports Windows as of now
				user = getpass.getuser()
				if(platform.system() == "Windows"):
					if(platform.release() == ("XP" or "Server 2003" or "Home Server")):
						self.dbFile = "C:\\Documents and Settings\\%s\\Local Settings\\Application Data\\Plex Media Server\\Plug-In Support\\Databases\\com.plexapp.plugins.library.db" % user
					elif(platform.release() == "7"):
						localAppData = os.environ['LOCALAPPDATA']
						self.dbFile = "%s\\Plex Media Server\\Plug-In Support\\Databases\\com.plexapp.plugins.library.db" % localAppData
			#This variable is used later by createBackup and retrieveBackup
			self.dbDir = self.dbFile.replace("\\com.plexapp.plugins.library.db", "")
			#Connects to database, looks in the table that holds information about the library sections, and returns an array of the names of the library sections
			db = sqlite3.connect(self.dbFile)
			cursor = db.cursor()
			cursor.execute('''SELECT name FROM library_sections''')
			rows = cursor.fetchall()
			sections = []
			for row in rows:
				sections.append(row[0])
			cursor.close()
			db.close()
			return sections
		#Exception for when no database is found
		except sqlite3.OperationalError:
			#This will ultimately return an array of the names of the library sections from the database the user defines; see lines 144-145
			return self.noDatabaseAlert()

	def noDatabaseAlert(self):
		msgBox = QMessageBox()
		msgBox.setText("The SQLite database necessary to change icons could not be found. Either you do not have an installation of the Plex Media Server or it is located elsewhere.")
		msgBox.setInformativeText("For help locating the database file, click Help. To download a copy of Plex Media Server, click Download. To locate the database file, click Locate.")
		msgBox.setWindowTitle("Change Icons for Plex")
		closeButton = msgBox.addButton("Close", QMessageBox.AcceptRole)
		helpButton = msgBox.addButton("Help", QMessageBox.HelpRole)
		downloadButton = msgBox.addButton("Download", QMessageBox.HelpRole)
		locateButton = msgBox.addButton("Locate", QMessageBox.YesRole)
		msgBox.exec_()
		if(msgBox.clickedButton() == closeButton):
			#I'm not sure why but the red x in the corner is greyed out; this should suffice although it returns a bunch of errors since it continues with the MainPage.__init__ call and self.selectLibraryDropdown.addItems() then takse a NoneType argument
			self.close()
		elif(msgBox.clickedButton() == helpButton):
			QDesktopServices.openUrl(QUrl("http://raspberrypihtpc.wordpress.com/how-to/how-to-plex-media-server-change-the-section-icons/"))
			self.noDatabaseAlert()
		elif(msgBox.clickedButton() == downloadButton):
			QDesktopServices.openUrl(QUrl("https://plex.tv/downloads/1/archive"))
			self.noDatabaseAlert()
		elif(msgBox.clickedButton() == locateButton):
			#Passes the returned value from selectDBFile to the findLibraries sqlite3.OperationError exception and onto self.selectLibraryDropdown.addItems() in the MainPage.__init__ function
			return self.selectDBFile()

	def selectDBFile(self):
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.AnyFile)
		dialog.setNameFilter("Databases (*.db)")
		dialog.setViewMode(QFileDialog.Detail)
		if dialog.exec_():
			self.dbFile = dialog.selectedFiles()[0]
			#Finally the list of library names
			return self.findLibraries(False)

	def selectIconFile(self):
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.AnyFile)
		dialog.setNameFilter("Images (*.png *.jpg)")
		dialog.setViewMode(QFileDialog.Detail)
		if dialog.exec_():
			#Path to file chosen is displayed in the GUI
			self.selectedFile.setText(dialog.selectedFiles()[0])
			#Icon file path is returned
			return dialog.selectedFiles()[0]

	def changeIcon(self):
		#Case where a file was chosen
		if(self.selectedFile.text() != ""):
			#Modifies the path to the icon to file:\\NAMEOFCOMPUTER\\FILEPATH so the device can access the icon as long as it is in a shared folder 
			thingToUpdateWith = 'file:\\' + self.selectedFile.text().replace("C:", platform.node())
		#Case where a URL for an icon was provided and no local file was chosen
		elif(self.selectedFile.text() == "" and len(self.selectFileUrl.text()) > 7):
			thingToUpdateWith = self.selectFileUrl.text()
		#Case where no icon was chosen
		else:
			#Alerts the user with message box
			self.alertPopUp("No icon has been chosen.")
			return
		try:
			#Aside from a URL for the icon, a field that says the library was updated need to be updated using a specific format; date and time are formatted according to that format
			formattedDateTime = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day) + ' ' + str(datetime.now().hour) + ':' + str(datetime.now().minute) + ':' + str(datetime.now().second)
			#Update values of the database to change icon
			db = sqlite3.connect(self.dbFile)
			cursor = db.cursor()
			cursor.execute("UPDATE library_sections SET user_thumb_url='%s', updated_at='%s' WHERE name = '%s'" % (thingToUpdateWith, formattedDateTime, self.selectLibraryDropdown.currentText()))
			db.commit()
			#Tell the user that things worked
			self.alertPopUp("The icon was successfully changed.")
		#In case someone is running this as a Python script and is exiting the program; don't want the database to get screwed up
		except (KeyboardInterrupt, SystemExit):
			db.rollback()
			raise
		#Something went wrong
		except:
			db.rollback()
			self.alertPopUp("An error occurred. The icon was not successfully changed.")
		finally:
			cursor.close()
			db.close()
	
	#Just an alert to make sure the user does not accidentally overwrite their database with a backup
	def retrieveAlert(self):
		msgBox = QMessageBox()
		msgBox.setText("Retrieving a backup file will result in your current file being overwritten. Are you sure you want to retrieve your backup?")
		msgBox.setWindowTitle("Change Icons for Plex")
		msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		ret = msgBox.exec_()
		if(ret == QMessageBox.Yes):
			self.retrieveBackup()
		elif(ret == QMessageBox.No):
			msgBox.close()

	def alertPopUp(self, message):
		msgBox = QMessageBox()
		msgBox.setText(message)
		msgBox.setWindowTitle("Change Icons for Plex")
		msgBox.exec_()

	def createBackup(self):
		try:
			backupDbFile = self.dbDir + "\\com.plexapp.plugins.library.db - Copy"
			copyfile(self.dbFile, backupDbFile)
			self.alertPopUp("The backup was successfully created.")
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			self.alertPopUp("An error occurred. The backup was not successfully created.")

	def retrieveBackup(self):
		try:
			backupDbFile = self.dbDir + "\\com.plexapp.plugins.library.db - Copy"
			copyfile(backupDbFile, self.dbFile)
			self.alertPopUp("The backup was successfully retrieved.")
		except (KeyboardInterrupt, SystemExit):
			raise
		except FileNotFoundError:
			self.alertPopUp("No backup file found.")
		except:
			self.alertPopUp("An error occurred. The backup was not successfully retrieved.")
			
if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainPage()
	window.show()
	sys.exit(app.exec_())
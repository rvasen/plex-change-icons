import getpass
import platform
import sys
import sqlite3
from PySide.QtCore import *
from PySide.QtGui import *
from shutil import copyfile

class MainPage(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self, parent)
		self.setWindowTitle("Change Library Icons for Plex")
		self.setFixedWidth(450)
		self.setFixedHeight(350)

		selectLibraryLabel = QLabel(self.tr("Select Library for Changing Icon:"))
		selectLibraryLabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)
		self.selectLibraryDropdown = QComboBox()
		self.selectLibraryDropdown.addItems(self.findLibraries())

		selectIconButton = QPushButton("Select File for Icon")
		selectIconButton.clicked.connect(self.selectIconFile)

		selectedFileLabel = QLabel("Selected File:")
		self.selectedFile = QLabel("")
		self.selectedFile.setFrameStyle(QFrame.Panel | QFrame.Sunken)

		selectFileUrlLabel = QLabel("Select URL For Picture:")
		self.selectFileUrl = QLineEdit(self)
		self.selectFileUrl.setText("http://")

		noteLabel = QLabel("Note: This GUI gives the option to use a file locally or fetch one from a URL. Fill the field depending on which method you'd like to use. If you fill both, the local file will be used.")
		noteLabel.setWordWrap(True)

		createBackupButton = QPushButton("Backup File")
		createBackupButton.clicked.connect(self.createBackup)

		retrieveBackupButton = QPushButton("Retrieve Backup File")
		retrieveBackupButton.clicked.connect(self.retrieveBackup)

		submitButton = QPushButton("Submit Icon Change")
		submitButton.clicked.connect(self.changeIcon)

		fileGroup = QGroupBox(self.tr("Choose New Library Icon:"))
		submitGroup = QGroupBox(self.tr(""))

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

		mainLayout = QVBoxLayout(self)
		mainLayout.addWidget(fileGroup)
		mainLayout.addWidget(submitGroup)

		self.setLayout(mainLayout)

	def findLibraries(self):
		user = getpass.getuser()
		if(platform.system() == "Windows"):
			if(platform.release() == "XP" or "Server 2003" or "Home Server"):
				self.dbFile = "C:\\Documents and Settings\\%s\\Local Settings\\Application Data\\Plex Media Server\\Plug-In Support\\Databases\\com.plexapp.plugins.library.db" % user
				self.dbDir = "C:\\Documents and Settings\\%s\\Local Settings\\Application Data\\Plex Media Server\\Plug-In Support\\Databases" % user
			elif(platform.release() == "7"):
				localAppData = os.environ['LOCALAPPDATA']
				self.dbFile = "%s\\Plex Media Server\\Plug-In Support\\Databases\\com.plexapp.plugins.library.db" % localAppData
				self.dbDir = "%s\\Plex Media Server\\Plug-In Support\\Databases" % localAppData
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

	def selectIconFile(self):
		dialog = QFileDialog(self)
		dialog.setFileMode(QFileDialog.AnyFile)
		dialog.setNameFilter("Images (*.png *.jpg)")
		dialog.setViewMode(QFileDialog.Detail)
		if dialog.exec_():
			self.selectedFile.setText(dialog.selectedFiles()[0])
			return dialog.selectedFiles()[0]

	def changeIcon(self):
		if(self.selectedFile.text() != ""):
			thingToUpdateWith = self.selectedFile.text()
		elif(self.selectedFile.text() == "" and len(self.selectFileUrl.text()) > 7):
			thingToUpdateWith = self.selectFileUrl.text()
		else:
			self.noFileAlert()
			return
		try:
			db = sqlite3.connect(self.dbFile)
			cursor = db.cursor()
			cursor.execute("UPDATE library_sections SET user_thumb_url='%s' WHERE name = '%s'" % (thingToUpdateWith, self.selectLibraryDropdown.currentText()))
			db.commit()
		except (KeyboardInterrupt, SystemExit):
			db.rollback()
			raise
		except:
			db.rollback()
			self.errorPopUp()
		finally:
			cursor.close()
			db.close()
			self.successPopUp()

	def noFileAlert(self):
		msgBox = QMessageBox()
		msgBox.setText("No icon has been chosen.")
		msgBox.setWindowTitle("Change Icons for Plex")
		msgBox.exec_()

	def errorPopUp(self):
		msgBox = QMessageBox()
		msgBox.setText("An error occurred. The icon was not successfully changed.")
		msgBox.setWindowTitle("Change Icons for Plex")
		msgBox.exec_()

	def successPopUp(self):
		msgBox = QMessageBox()
		msgBox.setText("The icon was successfully changed.")
		msgBox.setWindowTitle("Change Icons for Plex")
		msgBox.exec_()

	def createBackup(self):
		backupDbFile = self.dbDir + "\\com.plexapp.plugins.library.db - Copy"
		copyfile(self.dbFile, backupDbFile)

	def retrieveBackup(self):
		backupDbFile = self.dbDir + "\\com.plexapp.plugins.library.db - Copy"
		copyfile(backupDbFile, self.dbFile)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = MainPage()
	window.show()
	sys.exit(app.exec_())
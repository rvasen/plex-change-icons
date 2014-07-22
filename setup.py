import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

exe = Executable(script = "changeIcon.py",
				 base = base
				)

build_exe_options = {
	'includes' : ['atexit', 'PySide.QtNetwork']
}

setup(name = "PlexChangeIcons",
	  version = "0.1.0",
	  description = "GUI to interact with Plex's SQLite database to change icons the Section Icons (method based on article: http://raspberrypihtpc.wordpress.com/how-to/how-to-plex-media-server-change-the-section-icons/)",
	  executables = [exe],
	  options = {'build_exe': build_exe_options})
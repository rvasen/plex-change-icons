plex-change-icons
=================

GUI to interact with Plex's SQLite database to change icons the Section Icons (method based on article: http://raspberrypihtpc.wordpress.com/how-to/how-to-plex-media-server-change-the-section-icons/)

Icons can be changed in two ways:
1. Choose file locally but it must be in a shared folder that be accessed by your device over the LAN
2. Provide URL for image hosted online (e.g. http://upload.wikimedia.org/wikipedia/en/6/60/TV-G_white_icon.png)

App folder contains python file where the GUI was written. Setup.py is the script for freezing used by cx_Freeze. Dist folders contain installers and folders beginning in exe contain the frozen version of the GUI.

Currently only supports Windows 64 bit platforms. 32 bit support coming soon. Lack of support for other platforms is mainly due to the lack of other platforms to test on. Feel free to fork and send pull requests. Hopefully this thing I strung together will be useful to someone somewhere.
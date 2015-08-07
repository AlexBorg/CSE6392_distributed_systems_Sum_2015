Prerequisites:
This project is designed to be run with Python 3.4. It requires the tkinter and ttk modules to be installed, which should be included by most Python 3 distributions. It has been tested on the latest Ubuntu distribution and the Anaconda Python 3.4 distribution for Windows, which can be downloaded at http://continuum.io/downloads#py34 .

Running:
The program is divided into a server program that runs in the background and hosts chat rooms and a client GUI that connects and sends messages.

To launch the server, run server_app.py. It listens for connections on INADDR_ANY, so no configuration is required.

To launch a client, run client_gui.py. Multiple instances of client_gui.py should be run from different directories due to competing access to the preferences database file. Enter the address of the server (localhost if on the same machine), a username, password, and hit 'Register' to register a user and log in.

# General Information

## Future of the project
switching the main functionality from a GUI based Spotify Player to a (maybe Player independent) Music Analyzer and User specific Playlist generation using Machine Learning

## Installation

* Need to have:
  * Spotify Premium
  * usable Internet Connection (no offline functionalities (yet))
  * Python Packages:
    * should be installed: base64, io, json, os, re, subprocess, shlex, typing, time
    * install with pip: DateTime, dotenv, numpy, PIL, pylint, requests, spotipy, sqlite3, tkinter, urllib3
  * DB Browser for SQLite (optional)
1) create Spotify App ([https://developer.spotify.com/documentation/web-api/concepts/apps](https://developer.spotify.com/documentation/web-api/concepts/apps))
2) copy 'Client ID', 'Client secret' and 'Redirect URI'
3) create '.env'-file in project directory and import correctly in spotify_access.py
4) run SpotipyApp.py for GUI

## Lessons Learned

* don't overwrite attributes in the initializer with None to declare their type \
or update only half of the attributes
* Read Docs
* due to CEST and CET the datetime.datetime method can have an offset
* don't cross-reference anything (e.g. imports, classes) -> Circular Imports  \
-> big problems (max recursion depth; IDE be like: ╰（‵□′）╯)
  * instead move classes/structs to shared file as dataclasses to resolve circular import errors
* quotation marks '...' within Strings "..." are important
* if a list is required, enter a list
* though Playlist have markets don't use them
* catching exceptions can be a helpful but uncommon benefit
* superclasses can be profitable, but hurt the code readability 

## Known Error messages

* requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')) -> Just retry

## ToDo List

* [ ] do ToDo's in Code
* [ ] test Code
* [ ] comment Code

### Backend related

* [ ] fix valid_spotify_uri()
* [ ] optimize track search distribution in 'random_playlist_by_genre()' -> implement ML
* [ ] connect app with Home Assistant
* [ ] use Spotify's Audio Features & Analytics (own genres) -> implement ML
* [ ] create AI based playlists -> implement ML

### Frontend related

* [ ] fix progressbar
* [ ] add functionality to searched instance
* [ ] make possible that the Apps starts though Spotify is neither started nor playing anything \
(Classes->Player->get_instance())
* [ ] open extra Profile Window for Album, Artist, Playlist, User
* [ ] too long texts should move automatically
* [ ] QT GUI/better Frontend
* [ ] if searched track is already in queue, show/highlighted where (App Window)

## Documentations

### APIs

* [Spotify for Developers](https://developer.spotify.com/)
* [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/)

### Backend 

* [SQLite for Python](https://www.sqlitetutorial.net/sqlite-python/)

### Frontend

* [Tkinter](https://docs.python.org/3/library/tkinter.html)
* [QT for Python (PySide6)](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/index.html)

### Other

* [Markdown](https://www.markdownguide.org/basic-syntax/)

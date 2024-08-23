# General Information

## Installation

* Need to have:
  * Spotify Premium
  * usable Internet Connection (no offline functionalities (yet))
  * Python Packages:
    * should be installed: base64, io, json, os, re, subprocess, shlex, typing, time
    * install with pip: DateTime, dotenv, numpy, PIL, pylint, requests, spotipy, sqlite3, tkinter, urllib3
  * DB App for SQLite (optional)
1) create Spotify App ([https://developer.spotify.com/documentation/web-api/concepts/apps](https://developer.spotify.com/documentation/web-api/concepts/apps))
2) copy 'Client ID', 'Client secret' and 'Redirect URI'
3) create '.env'-file in project directory

## Lessons Learned

* don't overwrite attributes in the initializer with None to declare their type
* or update only half of the attributes
* Read Docs
* due to CEST and CET the datetime.datetime method can have an offset
* don't cross-reference anything (e.g. imports, classes) \
-> big problems (max recursion depth; IDE be like: ╰（‵□′）╯)
* quotation marks '...' within Strings "..." are important
* if a list is required, enter a list
* though Playlist have markets don't use them
* catching exceptions can be a helpful but uncommon benefit

## Known Error messages

* requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')) -> Just retry

## ToDo List

### Backend related

* fix check_spotify_id()
* optimize track search distribution in 'random_playlist_by_genre()'
* connect app with Home Assistant
* use Spotify's Audio Features & Analytics (own genres)
* create AI based playlists

### Frontend related

* fix progressbar
* add functionality to searched instance
* make possible that the Apps starts though Spotify is neither started nor playing anything (Classes->Player->get_instance())
* open extra Profile Window for Album, Artist, Playlist, User
* to long texts should move automatically
* QT GUI Frontend
* if searched track is already in queue, show/highlighted where (App Window)

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

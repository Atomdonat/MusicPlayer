# General Information

## Future of the project
switching the main functionality from a GUI based Spotify Player to a (maybe Player independent) Music Analyzer and User/Mood tailored Playlist generation using Machine Learning

## Installation

* Need to have:
  * Spotify Premium
  * usable Internet Connection (no offline functionalities (yet))
  * Python Packages:
    * should be installed: base64, io, json, os, re, subprocess, shlex, typing, time
    * install with pip: DateTime, dotenv, numpy, PIL, pylint, requests, spotipy, sqlite3, tkinter, urllib3, pandas
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
* added separate changes.md file to better track changes
* do not reset Database before Analyzing anything (No Data in DB -> no Data for Analysis)

## Code/Comment Highlighting in Pycharm
- TODO:
  - Usage: Used to mark tasks that need to be done.
  - Pattern: `*\btodo\b*`
  - Main Color (Light Green): `#A4C639`
  - Darker Version: `#8CAF2D`
- FIXME:
  - Usage: Used to highlight code that needs fixing.
  - Pattern: `*\bfixme\b*`
  - Main Color (Light Red or Pink): `#FF6F61`
  - Darker Version: `#E65B4F`
- BUG:
  - Usage: Used to mark known bugs in the code.
  - Pattern: `*\bbug\b*`
  - Main Color (Light Red or Pink): `#FF6F61`
  - Darker Version: `#E65B4F`
- IDEA:
  - Usage: Used to denote an idea or suggestion for the code.
  - Pattern: `*\bidea\b*`
  - Main Color (Light Yellow): `#FFD700`
  - Darker Version: `#E6BE00`
- NOTE:
  - Usage: Used to add notes or explanations about the code.
  - Pattern: `*\bnote\b*`
  - Main Color (Light Blue): `#ADD8E6`
  - Darker Version: `#93C2CF`
- WARNING:
  - Usage: Used to indicate something that might need attention or could be problematic.
  - Pattern: `*\bwarning\b*`
  - Main Color (Orange): `#FFA500`
  - Darker Version: `#E69500`
- HACK:
  - Usage: Used to mark code that is a workaround or temporary solution.
  - Pattern: `*\bhack\b*`
  - Main Color (Purple): `#9370DB`
  - Darker Version: `#7D60BF`

## Own Terminology/Abbreviations
- **IR Loop:** infinite recursion loop

## Known Error messages

* requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')) -> Just retry

## ToDo List (prioritized)

* [ ] do ToDo's in Code
* [ ] test Code
* [ ] comment Code (including Highlightings) add Docstrings

### Backend related

* [ ] finish analysis.py 
* [ ] simplify API calls (instead of 500 requests à 1 item, do (e.g.) 10 requests à 50 items (recommended by Spotify))
* [x] Rework Item Creation to avoid IR-Loop (caused by class properties) -> ItemIdQueues()
  * [x] add fetch method for tables (implement getter for items)
* [ ] check if any Spotify API request gets bottlenecked by the API limit of 100 items (split like in Playlist.track_ids())
* [x] fix valid_spotify_uri()
* [x] fix Database insertion (Playlist.track_ids(): **every** new item should be inserted).
  * tracing the Error for Playlist 5kuT9ddlqoiZjW7cgnDv2X with 1743 tracks:
    * fetching tracks_id from db returns only 100 ids (could be Spotify's API limit)
    * requesting Playlist 5kuT9ddlqoiZjW7cgnDv2X from API only returns 100 tracks 
  * => Error/Problem caused by Spotify's standard API limit
  
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

## Tags
- Dictionaries / JSON
- SQLite

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
* [Docstring Conventions](https://peps.python.org/pep-0257/)

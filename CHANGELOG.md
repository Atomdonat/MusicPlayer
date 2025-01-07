# Changelog

[//]: # (Template:)
[//]: # (## [new Version] - Date - Title)
[//]: # (#### database_access.py)
[//]: # (-)

[//]: # (#### main_app.py)
[//]: # (-)

[//]: # (#### music_classes.py)
[//]: # (-)

[//]: # (#### organize_playlist.py)
[//]: # (-)

[//]: # (#### secondary_methods.py)
[//]: # (-)

[//]: # (#### shared_config.py)
[//]: # (-)

[//]: # (#### spotify_access.py)
[//]: # (-)

[//]: # (#### spotify_requests.py)
[//]: # (-)

[//]: # (#### spotify_web_api.py)
[//]: # (-)

[//]: # (### other files)

[//]: # (#### .env.sample)
[//]: # (-)

[//]: # (#### README.md)
[//]: # (- )

[//]: # (#### requirements.txt)
[//]: # (- )

[//]: # (#### Changelog)
[//]: # (- )

## [1.14.2] - 07.01.2025 - retrofitting the changelog
[//]: # (#### database_access.py)
[//]: # (-)

[//]: # (#### main_app.py)
[//]: # (-)

[//]: # (#### music_classes.py)
[//]: # (-)

[//]: # (#### organize_playlist.py)
[//]: # (-)

[//]: # (#### secondary_methods.py)
[//]: # (-)

[//]: # (#### shared_config.py)
[//]: # (-)

[//]: # (#### spotify_access.py)
[//]: # (-)

[//]: # (#### spotify_requests.py)
[//]: # (-)

[//]: # (#### spotify_web_api.py)
[//]: # (-)

### other files

[//]: # (#### .env.sample)
[//]: # (-)

#### README.md
- regular update

#### requirements.txt
- sorted imports

#### Changelog
- moved from the "changes-per-commit" style to a complete Changelog


## [1.14.1] - 03.01.2025 - 
[//]: # (#### database_access.py)
[//]: # (-)

[//]: # (#### main_app.py)
[//]: # (-)

[//]: # (#### music_classes.py)
[//]: # (- )

[//]: # (#### organize_playlist.py)
[//]: # (-)

[//]: # (#### secondary_methods.py)
[//]: # (-)

#### shared_config.py
- updated config

[//]: # (#### spotify_access.py)
[//]: # (-)

[//]: # (#### spotify_requests.py)
[//]: # (-)

[//]: # (#### spotify_web_api.py)
[//]: # (-)

### other files
#### README.md
- regular update

#### requirements.txt
- reordered imports

## [1.14.0] - 02.01.2025 - Update in spotify_web_api.py (WIP)
### Changes in Backend Code

#### main_app.py
- minor changes 

#### music_classes.py
- added some (improvable) Docstrings

#### organize_playlist.py
- restructured to include Albums

#### secondary_methods.py
- added assisting methods for spotify_web_api.py

#### shared_config.py
- renamed and collected (global) constants
- updated imports
- added ANSI colours as strings (e.g. Error -> print(CRED+...+TEXTCOLOR))

#### spotify_web_api.py (WIP)
- some methods are finished (mps=3)
- added method to request "Extended"-Token to still use Tracks Audio Features, where "normal"-token requests are deprecated since 27 Nov. 2024, by [Spotify API Changes](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api) 
- Spotify API Access Tokens are stored/cached in .env and are valid for up to 1h since request
  - corrected implementation following API Tutorial


#### testing/*
- added as centralized testing directory

### other files
#### .env.sample
- added new Keys
- added Comments and reordered

#### README.md
- regular update

#### requirements.txt
- added project requirements (moved from README)


## [1.13.1] - 16.12.2024 - 
### Changes in Backend Code
### spotify_web_api.py
- still **WIP**; not tested yet
- implemented Progress status code: mps 0-3
- replaced check(_upper)_limit() calls with iterations of requests
- Docstrings mostly finished

## [1.13.0] - 15.12.2024 - begin to replace spotipy library (Web API part for now)
### Changes in Backend Code
#### spotify_web_api.py
- Goal: replacing spotipy calls by implementing Official Spotify Web API requests
  - Using Docstrings out of Official Documentation (f.e. spotipy errors are mis-/not leading)
  - better implementation possible/tailored to my needs
- implemented for Project relevant methods
- still **WIP**; not tested yet


## [1.12.2] - 06.12.2024 - fix .env-.gitignore problem
### Changes in Backend Code
#### other files
- created .env.sample 
- removed .env from Repo


## [1.12.1] - 22.11.2024 - updated playlist organization
### Changes in Backend Code
#### organize_playlist.py
- methods to re-/shuffle Playlist
- added (WIP) feature to remove specified tracks


## [1.12.0] - 07.11.2024 - added PRNG Playlist Shuffle
### other files
- added method/file to re-/shuffle Playlist -> no more bad Spotify shuffle with only limited number and always the same tracks


## [1.11.5] - 09.09.2024 - Outsourced Spotify API methods to spotify_access.py
### Changes in Backend Code

#### music_classes.py
- outsourced API calls to spotify_access.py

#### spotify_access.py
- added request methods
 
### other files
- minor changes/updates


## [1.11.4] - 08.09.2024 - optimizing API calls
### Changes in Backend Code
#### main_app.py
- moved Device() and Player() from music_classes.py here
   
#### music_classes.py
- reducing API calls to a minimal (reducing risc to get long timeout again)
  - removed (redundant) ID check/validation

#### share_config.py
- made path strings dependent of root dir (using os.path.dirname() and os.path.abspath())

#### other files
- minor changes/updates


## [1.11.3] - 07.09.2024 - added pandas analysis
### Changes in Backend Code
#### database_access.py
- fixed execute_script() always returns None if fetch=True (cursor.executescript() does not return anything)

#### other files
- minor changes/updates
- add .env template


## [1.11.2] - 04.09.2024 - started working on analysis.py
### Changes in Backend Code

#### main_app.py
- replaced TrackAnalysis() Database stuff with CSV for pandas  

#### database_access.py
- moved TrackAnalysis() related code to analysis.py

#### analysis.py
- created file for anything pandas (and ML) related code for data analysis

#### other files
- minor changes/updates


## [1.11.1] - 04.09.2024 - minor changes
### Changes in Backend Code
#### other files
- minor changes/updates

## [1.11.0] - 02.09.2024 - fixed instance creation IRL
- begun the fancy comments time has (using Tags)
### Changes in Backend Code
#### main_app.py
- fixed Playlist Tracks limitation of the API (100 items -> every)
- adding items to cache queue before adding to database and checking against both db and queue (avoiding IR loop, WIP)
- substituted every direct database execution with suitable method calls
- fixed IR LOOP's by adding cache queue

#### database_access.py
- added Fetch support to SQL execution methods (execute_query(), execute_script())
- updated update_item() with fetch_or_update_item() 
- added fetch_column()

#### other files
- minor changes/updates

### Changes in Frontend Code
- minor changes/updates


## [1.10.1] - 29.08.2024 - added market check in main_app.py
### Changes in Backend Code
#### main_app.py
- added market check
#### other files
- minor changes/updates

### Changes in Frontend Code
- minor changes/updates

## [1.10.0] - 29.08.2024 - 
### Changes in Backend Code
#### music_classes.py
- fixed Adding Playlist/Album ID to other Types -> Playlist() works
- Player() can be called even if Spotify is not running
  - added Dummies to Database, to resolve problem

#### database_access.py
- added Device()/devices to Database

#### other files
- minor updates/changes


## [1.9.0] - 28.08.2024 - nearly complete working classes
### Changes in Backend Code
#### music_classes.py
- replaced (new) SpotifyID/URI Types with (old) str Types -> fewer errors and conversions 
- added Popularity and Blacklisted to every class including Genre (new)
- Album, Artist, Track and User can be initialized without errors; Playlist WIP; other not tested yet

#### other files
- minor updates/changes



## [1.8.0] - 23.08.2024 - Updated Docs and Classes
### Changes in Backend Code
#### music_classes.py
- updated Devices, Device and Player
- moved constants to shared_config.py

### Other files
#### README.md
- merge multiple Docs into one
- regular update
#### class_attributes.txt
- add types to attributes


## [1.7.0] - 23.08.2024 - Re-reorganizing Project
### Changes in Backend Code
#### database_access.py 
- outsourced from former Classes.py class:MyAppDatabase
- moved imports, constants to shared_config.py

#### main_app.py
- former Classes.py
- rewrote every (not outsourced) Class


#### music_classes.py
- moved imports to shared_config.py

#### secondary_methods.py
- moved imports to shared_config.py
- added code from openImage.py methods 

#### shared_config.py
- merged most imports here
- added dataclasses for attribute types

#### spotify_access.py
- former spotifyAccessManager.py
- updated Scopes and Error Handling

### Changes in Frontend Code
#### SpotipyApp.py
- former main.py
- moved imports, constants to shared_config.py
- moved assisting methods to secondary_methods.py
- added code from icons.py

### other files
- renamed Icons/Images
- added example JSONs
#### class_attributes.txt
- add class attributes

## [1.6.5] - 31.07.2024 - Renaming/Reorienting Project
moving from private Repo to public one
### Changes in Backend Code
- merging **every** backend related line into one **(large)** file

### Changes in Frontend Code
- merging **every** frontend related line into one **(large)** file


## [1.6.4] - 16.05.2024 - Template for Analytics

- song_analytics.py
  - add placeholder

## [1.6.3] - 15.05 2024 - still not working progressbar

- main.py
  - try to fix progressbar
- Readme.md
  - add installation guide
  - regular update
- spotifyAccessManager.py
  - move redirect_uri to .env

## [1.6.2] - 08.02 2024 - Added template .env

- .env
  - add template

## [1.6.1] - 08.02.2024 - added uml class diagrams; Storing credentials in .env

- .gitignore
  - update
- add fancy diagrams
  - py_to_ucd_svg.py as converter
- spotifyAccessManager.py
  - remove Hardcoded API key
  - load API key from .env file
- rotate API key

## [1.6.0] - 26.01.2024 - adding random playlist method

- Classes.py
  - add "random" track search
  - add playlist creation

## [1.5.1] - 19.01.2021 - switching ide

- Classes.py
  - outsource Player attribute instantiation to method
- main.py
  - add progressbar to GUI (not working)

## [1.5.0] - 17.01.2024 - replaced volume entry with scale

- main.py 
  - replace volume Input Entry with Scale
- Readme.md
  - regular update

## [1.4.0] - 16.01.2024 - replaced button text with icons

- add Icons
- main.py
  - replace Button Text with Icon
- openImage.py
  - add Icon support
- secondary_methods.py
  - minor changes

## [1.3.0] - 12.01.2024 - added blacklist auto skip

- .gitignore
  - update
- Classes.py
  - add superclass to remove redundant class attributes and methods
  - rewrite classes as subclass from class:SpotifyObject
  - learn Switch Statements
- main.py
  - moved some methods
- secondary_methods.py
  - add some methods
- Readme.md
  - regular update

## [1.2.0] - 11.01.2024 - added searched object buttons app window

- Classes.py
  - fix SQLite syntax
  - add custom shuffle
  - add blacklist function
- main.py
  - update Frontend
  - add multi use buttons
    - add search buttons
  - add placeholder methods
- openImage.py
  - add Image support
- secondary_methods.py
  - add dict assisting methods
- spotifyAccessManager.py
  - update Scope

## [1.1.3] - 07.01.2024 - remodelled the app window

- main.py
  - update GUI
- Readme.md
  - regular update

## [1.1.2] - 05.01.2024 - first working search in tkinter app

- Classes.py
  - cache Instances
- TrackTank.db
  - add Database
- Readme.md
  - regular update

## [1.1.1] - 04.01.2024 - removed cross-reference of imports

- fix syntax, grammar and readability
- Classes.py
  - add ID check
  - sort classes by name

## [1.1.0] - 03.01.2024 - reorganized files due to unkown import error

- Classes.py
  - implement SQLite Databases
  - add Controller SpotifyApp
- database_related_stuff.py
  - move to Classes.py
- main.py
  - update GUI
- secondary_methods.py
  - minor changes
- spotify_related_stuff.py
  - move to Classes.py
- testing.py
  - test methods and classes

## [1.0.1] - 02.01.2024 - reorganized App into class

- Classes.py
  - minor changes
- main.py
  - organize GUI
- README.md
  - regular update
- spotify_related_stuff.py
  - optimize find_objects

## [1.0.0] - 31.12.2023 - finished tkinter improvised App 

- main.py
  - improve GUI
- secondary_methods.py
  - remove deprecated methods

## [0.3.1] - 31.12.2023 - added Player functionality

- Classes.py
  - update class:Devices
  - update class:Player
- spotify_[...].json
  - add example responses
- main.py
  - add Frontend

## [0.3.0] - 31.12.2023 - added JSON instance dumping/loading for Classes

- Classes.py
  - add JSON support
- spotify_[...].json
  - add example responses
- Readme.md
  - regular update
- secondary_methods.py
  - learn to work with JSON 
- spotifyAccessManager.py
  - add Maximal Retry Counter/Timeout

## [0.2.0] - 29.12.2023 - added new classes regarding the player

- Classes.py
  - add new classes
- spotify_raleated_stuff.py
  - add new methods

## [0.1.0] - 28.12.2023 - tracks are addable to playlists

- Readme.md
  - regular update
- debug_dicts.txt
  - add to debug API calls
- secondary_methods.py
  - add new methods
- spotifyAccessManager.py
  - update Scope
- spotify_raleated_stuff.py
  - add new methods

## [0.0.2] - 28.12.2023 - removed cache files

- remove binary files

## [0.0.1] - 28.12.2023 - updated files

- create spotifyAccessManager.py (including Hardcoded API Key (－‸ლ) oops.)
- update .gitignore

### [0.0.0] - 28.12.2023 - Initial commit

- add README 
- add .gitignore
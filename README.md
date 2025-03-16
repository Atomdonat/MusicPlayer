# General Information

## Future of the project
¯\(°_o)/¯
### Ideas
- Initial Project Idea: one unified App for Spotify, YT-Music, etc.
- tailored Playlists
  - compensate for own crappy? taste
  - Spotify's "Made for you" Playlists (by genre) are not good 

## Installation

* Need to have:
  * Spotify Premium
  * usable Internet Connection 
  * Install Requirements: `pip install -r requirements.txt`
  * Needed Host Packages: geckodriver
1) create Spotify App ([https://developer.spotify.com/documentation/web-api/concepts/apps](https://developer.spotify.com/documentation/web-api/concepts/apps))
2) copy 'Client ID', 'Client secret' and 'Redirect URI'
3) create '.env'-file from the .env.sample template

## Lessons Learned

* don't overwrite attributes in the initializer with None to declare their type \
or update only half of the attributes
* **Read Docs**
* due to CEST and CET the datetime.datetime method can have an offset
* don't cross-reference anything (e.g. imports, classes) -> Circular Imports  \
-> big problems (max recursion depth; IDE be like: ╰（‵□′）╯)
* quotation marks '...' within Strings "..." are important
* if a list is required, enter a list (typehints are useful)
  * if wrong type passed, python attribute be like: guess I'm new_type now
* using market with Playlist can lead to errors [Spotify Track Relinking](https://developer.spotify.com/documentation/web-api/concepts/track-relinking)
* catching exceptions can be a helpful but uncommon benefit (If error do B else do A)
  * Catch Exceptions early on
* superclasses can be profitable, but hurt the code readability 
* added separate CHANGELOG.md file to better track changes and shorten commit messages
* do not reset Database before Analyzing anything (No Data in DB -> no Data to analyse)
* you won't get an error (or smth. similar) if you cross the API request limit (using spotipy; for each request the delay grows exponentially)
* spotipy is a shitty library no documentation -> if it is bad do it yourself but better (=> `spotify_web_api.py`)
* where there is a problem, there is another public repo/service fixing/bypassing it
* not every error means it's not working
* Whether the requests body is send with `data` or `json` can cause an error or not (Though, the documentations cURL request always says `data`)
* testcases should include **all** cases
* RTD submodules not rendering because other project relevant modules (e.g. numpy) wouldn't be installed (requirements.txt missing in readthedocs.yaml)


## Code/Comment Highlighting (in Pycharm)
- <span style="color:#FF6F61">**BUG:**</span>
  - Usage: Used to mark known bugs in the code.
  - Pattern: `\bbug\b.*`
  - Main Color: `#FF6F61`
  - Darker Version: `#E65B4F`
- <span style="color:#FFA500">**DEBUGGING:**</span>
  - Usage: Used to mark code that is used for debugging purposes.
  - Pattern: `\bdebugging\b.*`
  - Main Color: `#FFA500`
  - Darker Version: `#E69500`
- <span style="color:#FF6F61">**FIXME:**</span>
  - Usage: Used to highlight code that needs fixing.
  - Pattern: `\bfixme\b.*`
  - Main Color: `#FF6F61`
  - Darker Version: `#E65B4F`
- <span style="color:#9370DB">**HACK:**</span>
  - Usage: Used to mark code that is a workaround or temporary solution.
  - Pattern: `\bhack\b.*`
  - Main Color: `#9370DB`
  - Darker Version: `#7D60BF`
- <span style="color:#FFD700">**IDEA:**</span>
  - Usage: Used to denote an idea or suggestion for the code.
  - Pattern: `\bidea\b.*`
  - Main Color: `#FFD700`
  - Darker Version: `#E6BE00`
- <span style="color:#C77DBB">**Method Progress Status:**</span>
  - Usage: Used to mark the development progress of methods (see below)
  - Pattern: `# \bmps\b.*`
  - Main Color: `#C77DBB`
  - Darker Version: `#C36F85`
- <span style="color:#ADD8E6">**NOTE:**</span>
  - Usage: Used to add notes or explanations about the code.
  - Pattern: `\bnote\b.*`
  - Main Color: `#ADD8E6`
  - Darker Version: `#93C2CF`
- <span style="color:#A4C639">**TODO:**</span>
  - Usage: Used to mark tasks that need to be done.
  - Pattern: `\btodo\b.*`
  - Main Color: `#A4C639`
  - Darker Version: `#8CAF2D`
- <span style="color:#FFA500">**WARNING:**</span>
  - Usage: Used to indicate something that might need attention or could be problematic.
  - Pattern: `\bwarning\b.*`
  - Main Color: `#FFA500`
  - Darker Version: `#E69500`


## Own Terminology/Abbreviations
- **IR Loop:** infinite recursion loop

### Method/Class Progress Status (mps/cps)
- 0 -- planned, not implemented
- 1 -- implemented, not tested
- 2 -- in testing/debugging
- 3 -- finished
- remove after one/two commits after mps=3, cps=3

## Known Error messages

* requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')) -> Just retry
* requests.status_code == 503 -> wait some time then retry
* HTTP error code 500 returned (after client credential login (`request_regular_token()`))
  * Solution: "Since the client credentials flow does not include authorization, only endpoints that do not access user information can be accessed. You can use another authentication flow for getting recently played tracks from a user. Let me know if you have any questions!"
  * Source: https://community.spotify.com/t5/Spotify-for-Developers/500-internal-server-error/m-p/5400938/highlight/true#M4961

## ToDo List (prioritized)

* keep Docstrings up to date
* [ ] do ToDo's in Code
* [x] test Code
* [x] add Docstrings and comment Code (including Highlightings)
  * [x] fix submodules not showing in RTD

### Backend related

* [ ] add CLI interaction for `main_app.py`
  * headless App (e.g. for servers 24/7 app access)
  * [ ] method to print docstrings as manpage
* [x] unify return types/output and print statements
* [ ] use Spotify's Audio Features & Analytics
* [ ] clean up imports
* [ ] clean up code
* [ ] optimize track search distribution in 'random_playlist_by_genre()'

### Frontend related

* [ ] migrate to new API
* [ ] overhaul GUI
  * [ ] fix progressbar
  * [ ] add functionality to searched instance
  * [ ] make possible that the Apps starts though Spotify is neither started nor playing anything
  (Classes->Player->get_instance())
  * [ ] open extra Profile Window for Album, Artist, Playlist, User
  * [ ] too long texts should move automatically
  * [ ] QT GUI/better Frontend
  * [ ] if searched track is already in queue, show/highlighted where (App Window)

## Used Conventions
- versioning: [Semantic Versioning](https://en.wikipedia.org/wiki/Software_versioning#Schemes)

### PEP
- method/function names: "[Function names should be lowercase, with words separated by underscores as necessary to improve readability. Variable names follow the same convention as function names.](https://peps.python.org/pep-0008/#function-and-variable-names)"
  - non-public: "[Use one leading underscore only for non-public methods and instance variables.](https://peps.python.org/pep-0008/#method-names-and-instance-variables)"
- constants: "[Constants are usually defined on a module level and written in all capital letters with underscores separating words. Examples include MAX_OVERFLOW and TOTAL.](https://peps.python.org/pep-0008/#constants)"
- classes: "[Class names should normally use the CapWords convention.](https://peps.python.org/pep-0008/#function-and-variable-names)"
- docstrings: "[reStructuredText Docstring Format](https://peps.python.org/pep-0287/)"

## Tags
- Dictionaries / JSON
- SQLite

## Third-Party Documentations

### APIs

* [Spotify for Developers](https://developer.spotify.com/)
* [Chosic.com](https://www.chosic.com/spotify-playlist-analyzer/) (indirectly)

### Backend 

* [SQLite for Python](https://www.sqlitetutorial.net/sqlite-python/)
* [K-NN Algorithm](https://www.geeksforgeeks.org/k-nearest-neighbours/)

### Frontend

* [Tkinter](https://docs.python.org/3/library/tkinter.html)

### Other

* [Markdown](https://www.markdownguide.org/basic-syntax/)
* [Docstring Conventions](https://peps.python.org/pep-0257/)
* [Sphinx reStructuredText](https://www.sphinx-doc.org/en/master/index.html)
* Generating Documentation
  * [Tutorial](https://www.youtube.com/watch?v=BWIrhgCAae0)
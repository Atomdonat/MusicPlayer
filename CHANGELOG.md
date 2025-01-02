# Changes for current commit


[//]: # (## [1.10.0] - 02.01.2025 - )

## Changes in Backend Code

### analysis.py

- removed due to Terms of Service violation (Spotify Developer Terms, Section IV, 2(a)(i))

[//]: # (### database_access.py)

### main_app.py

- minor changes 

### music_classes.py

- added some (improvable) Docstrings

### organize_playlist.py

- restructured to include Albums

### secondary_methods.py

- added assisting methods for spotify_web_api.py

### shared_config.py

- renamed and collected (global) constants
- updated imports
- added ANSI colours as strings (e.g. Error -> print(CRED+...+TEXTCOLOR))

[//]: # (### spotify_access.py)

[//]: # (### spotify_requests.py)


### spotify_web_api.py (WIP)
 
- added method to request "Extended"-Token to still use Tracks Audio Features, where "normal"-token requests are deprecated since 27 Nov. 2024, by [Spotify API Changes](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api) 
- Spotify API Access Tokens are stored/cached in .env and are valid for up to 60 minutes since request
  - corrected implementation following API Tutorial 


### testing/*

- added as centralized testing directory


[//]: # (## Changes in Frontend Code)
[//]: # (- minor changes/updates)

## other files
### .env.sample
- added new Keys
- added Comments and reordered

### README.md

- regular update

### requirements.txt
- added project requirements (moved from README)
# Changes for current commit

## Changes in Backend Code

### main_app.py
- moved Device() and Player() from music_classes.py here
   
### music_classes.py
- reducing API calls to a minimal (reducing risc to get long "timeout" again)
  - removed (redundant) ID check/validation
- outsourced API calls to spotify_access.py

[//]: # (### database_access.py)

### spotify_access.py
- added request methods
 
### share_config
- made path strings dependent of root dir (using os.path.dirname() and os.path.abspath())

[//]: # (### analysis.py)


[//]: # (## Changes in Frontend Code)
[//]: # (- minor changes/updates)

### other files
- minor changes/updates
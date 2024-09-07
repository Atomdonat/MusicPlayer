# Changes for current commit

## Changes in Backend Code

### main_app.py
- replaced TrackAnalysis() Database stuff with CSV for pandas  

### database_access.py
- moved TrackAnalysis() related code to analysis.py
- fixed execute_script() always returns None if fetch=True (cursor.executescript() does not return anything)

### analysis.py
- created file for anything pandas (and ML) related code for data analysis

### other files
- minor changes/updates

[//]: # (## Changes in Frontend Code)
[//]: # (- minor changes/updates)
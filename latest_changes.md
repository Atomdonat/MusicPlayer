# Changes for current commit
- begun the fancy comments time has (using Tags)
## Changes in Backend Code
### main_app.py
- added market check
- fixed Playlist Tracks limitation of the API (100 items -> every)
- adding items to cache queue before adding to database and checking against both db and queue (avoiding IR loop)
- substituted every direct database execution with suitable method calls
- fixed IR LOOP's by adding cache queue

### database_access.py
- added Fetch support to SQL execution methods (execute_query(), execute_script())
- updated update_item() with fetch_or_update_item() 
- added fetch_column()

### other files
- minor changes/updates

## Changes in Frontend Code
- minor changes/updates
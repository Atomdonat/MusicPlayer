from code_backend.shared_config import *
from code_backend.secondary_methods import (
    dict_factory, print_error, get_str_from_json_file,
    load_sql_query, absolute_path, DatabaseException
)


class MyAppDatabase:
    """
    class acting as Data Access Object for Database. Handling all access to the Database
    """
    def __init__(self, database_file: str) -> None:
        """
        initialize the database using a path
        :param database_file: (relative) path to the database file
        """
        database_file = absolute_path(database_file)
        if not os.path.isfile(database_file):
            raise DatabaseException("Database file not found")

        try:
            self.database = sqlite3.connect(database_file)
            self.cursor = self.database.cursor()
            self.sql_query_queue = []

        except sqlite3.Error as e:
            print('Db Not found', str(e))

    def execute_query(self, sql_query: str, parameters=None, fetch: bool = False) -> None | list:
        """
        Execute a SQL query with parameters
        :param sql_query: SQL query
        :param parameters: parameters to pass to the SQL query
        :param fetch: If to Fetch Data (True: Fetch/Get Data; False: Update/Give Data)
        :return: If fetch=True data gets returned, else returns None
        """
        with self.database:
            try:
                self.cursor.execute(sql_query, parameters)
                if fetch:
                    return self.cursor.fetchall()

            except Exception as e:
                # Replaces image byte strings with '...' (shortens output immensely)
                if isinstance(parameters, dict):
                    pop_type = list(parameters.keys())[0][:-3]
                    parameters[f"{pop_type}_image"] = parameters[f"{pop_type}_image"][:4] + "..."
                print_error(
                    error_message="Error occurred while executing SQL query",
                    more_infos=f"SQL query:\n{sql_query}\nWith parameters:\n{parameters}\nError: {str(e)}\n"
                )

            finally:
                self.database.commit()

    def execute_script(self, sql_script: str, fetch: bool = False):
        """
        Execute a SQL script without parameters
        :param sql_script: SQL query
        :param fetch: If to Fetch Data (True: Fetch/Get Data; False: Update/Give Data)
        :return: If fetch=True data gets returned, else returns None
        """
        with self.database:
            try:
                if fetch:
                    self.cursor.execute(sql_script, ())
                    return self.cursor.fetchall()
                else:
                    self.cursor.executescript(sql_script)

            except Exception as e:
                print_error(
                    error_message="Error occurred while executing SQL script",
                    more_infos=f"SQL script:\n{sql_script}\n\nError: {str(e)}"
                )

            finally:
                self.database.commit()

    def execute_queue_queries(self) -> None:
        """
        Execute all SQL queries queued in self.sql_query_queue
        :return:
        """
        for sql_query, sql_values in self.sql_query_queue:
            self.execute_query(sql_query, sql_values)

    def split_queries(self, sql_query, parameter: dict):
        """
        Split SQL script/query containing multiple commands with parameters into multiple queries and execute them. The placeholders in the script must match the keys in parameter.
        :param sql_query: SQL query
        :param parameter: parameters to pass to the SQL query
        :return:
        """
        queries = [f"{query};" for query in sql_query.split(';')]
        for query in queries:
            self.execute_query(sql_query=query, parameters=parameter)

    def add_dummies(self) -> None:
        """
        Add dummy data to the database to avoid Exceptions and to test methods
        :return:
        """
        params = {
            "album_json": get_str_from_json_file(absolute_path("/Databases/JSON_Files/spotify_album_dummy.json")),
            "artist_json": get_str_from_json_file(absolute_path("/Databases/JSON_Files/spotify_artist_dummy.json")),
            "device_json": get_str_from_json_file(absolute_path("/Databases/JSON_Files/spotify_device_dummy.json")),
            "playlist_json": get_str_from_json_file(absolute_path("/Databases/JSON_Files/spotify_playlist_dummy.json")),
            "track_json": get_str_from_json_file(absolute_path("/Databases/JSON_Files/spotify_track_dummy.json")),
            "user_json": get_str_from_json_file(absolute_path("/Databases/JSON_Files/spotify_user_dummy.json"))
        }
        sql_script = load_sql_query("code_backend/sql_queries/insert_dummies.sql")
        self.split_queries(sql_query=sql_script, parameter=params)

    def initialize_tables(self) -> None:
        """
        Initialize the tables in the database. Creates the tables 'albums', 'artists', 'playlists', 'tracks', 'users', 'devices' and 'genres' and add dummy data
        :return:
        """
        sqlite_command = load_sql_query("code_backend/sql_queries/create_tables.sql")

        self.execute_script(sqlite_command)
        self.add_dummies()

    def add_item_to_table(
            self,
            table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices'],
            **kwargs
    ) -> None:
        """
        Adds item to table if it does not exist, otherwise, the insert will be ignored. If not all required keys are passed, an error is raised with exit code 1.
        :param table_name: Which table to add
        :param kwargs: which arguments are passed to database
        :return:
        """
        arg_map = {
            "albums": [
                "album_id",
                "album_name",
                "album_uri",
                "album_url",
                "album_image",
                "genre_names",
                "total_duration",
                "track_count",
                "artist_ids",
                "track_ids",
                "popularity",
                "blacklisted",
                "album_json"
            ],
            "artists": [
                "artist_id",
                "artist_name",
                "artist_uri",
                "artist_url",
                "artist_image",
                "genre_names",
                "follower",
                "album_ids",
                "playlist_ids",
                "top_track_ids",
                "popularity",
                "blacklisted",
                "artist_json"
            ],
            "devices": [
                "device_id",
                "device_name",
                "device_type",
                "is_active",
                "is_private_session",
                "is_restricted",
                "supports_volume",
                "volume_percent"
            ],
            "genres": [
                "genre_name",
                "acousticness_lower_limit",
                "acousticness_upper_limit",
                "danceability_lower_limit",
                "danceability_upper_limit",
                "duration_ms",
                "energy_lower_limit",
                "energy_upper_limit",
                "instrumentalness_lower_limit",
                "instrumentalness_upper_limit",
                "key_lower_limit",
                "key_upper_limit",
                "liveness_lower_limit",
                "liveness_upper_limit",
                "loudness_lower_limit",
                "loudness_upper_limit",
                "mode_lower_limit",
                "mode_upper_limit",
                "speechiness_lower_limit",
                "speechiness_upper_limit",
                "tempo_lower_limit",
                "tempo_upper_limit",
                "valence_lower_limit",
                "valence_upper_limit",
                "popularity",
                "blacklisted"
            ],
            "playlists": [
                "playlist_id",
                "playlist_name",
                "playlist_uri",
                "playlist_url",
                "playlist_image",
                "genre_names",
                "total_duration",
                "track_count",
                "owner_id",
                "track_ids",
                "popularity",
                "blacklisted",
                "playlist_json"
            ],
            "tracks": [
                "track_id",
                "track_name",
                "track_uri",
                "track_url",
                "track_image",
                "genre_names",
                "track_duration",
                "artist_ids",
                "album_id",
                "playlist_ids",
                "popularity",
                "blacklisted",
                "track_json"
            ],
            "users": [
                "user_id",
                "user_name",
                "user_uri",
                "user_url",
                "user_image",
                "follower",
                "playlist_ids",
                "top_track_ids",
                "top_artist_ids",
                "top_genre_names",
                "popularity",
                "blacklisted",
                "user_json"
            ]
        }

        missing_keys = set(arg_map[table_name]) - set(kwargs.keys())
        if missing_keys:
            print_error(
                error_message=f"Not all required Keys are passed while adding item to table '{table_name}'",
                more_infos=f"\n  Bad item: {kwargs}\n  Missing Keys: {missing_keys}\n",
                exit_code=1
            )

        sql_query = load_sql_query(f"code_backend/sql_queries/insert_{table_name}.sql")
        sql_values = {}
        for key, value in kwargs.items():
            if type(value) in (list, tuple, dict):
                sql_values[key] = str(value)
            else:
                sql_values[key] = value


        self.execute_query(sql_query, sql_values)
        print(f"Added {kwargs[f"{table_name[:-1]}_id"]} to table '{table_name}'")


    def remove_specific_item(self, table_name: str, item_id: str):
        """
        remove item from table by ID
        :param table_name: name of the table
        :param item_id: what item to remove
        :return:
        """
        primary_key = table_name[:-1] + "_id"
        sql_delete_command = f"DELETE FROM {table_name} WHERE {primary_key} = ?"

        self.execute_query(sql_delete_command, (item_id,))

    def reset_table(self, table_name: str):
        """
        reset table to initial state
        :param table_name: name of the table
        :return:
        """
        self.execute_script(f"""DELETE FROM {table_name}""", False)
        self.add_dummies()

    def reset_database(self):
        """
        reset complete database (all tables) to initial state
        :return:
        """
        self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;""")
        table_names = self.cursor.fetchall()

        if table_names:
            for table_name in table_names:
                self.cursor.execute(f"""DROP TABLE {table_name[0]};""")

            self.database.commit()
            self.initialize_tables()

    def fetch_row(
            self,
            table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices'],
            item_id: str,
            table_column: str = '*',
    ) -> list | str | int | float | None:
        """
        fetch item from table by ID
        :param table_name: name of the table
        :param item_id: what item to fetch
        :param table_column: what column to fetch (default: '*' fetches all columns)
        :return: hopefully what you asked for (row, value of column, None, ¯\\_(ツ)_/¯)
        """

        primary_key = table_name[:-1] + "_id"

        sql_command = f"""SELECT {table_column} FROM {table_name} WHERE {primary_key} = ?;"""

        result = self.execute_query(sql_command, (item_id,), True)
        return result[0] if result else None

    def fetch_column(
            self,
            table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices'],
            table_column: str
    ) -> list | None:
        """
        fetch column from table by ID
        :param table_name: name of the table
        :param table_column: what column to fetch
        :return: wanted column
        """
        try:
            result = self.execute_query(f"""SELECT {table_column} FROM {table_name};""", (), fetch=True)
            return [row[0] for row in result] if result else None
        except Exception as exc:
            print_error(
                error_message=exc,
                more_infos=f"Error occurred while fetching column '{table_column}' from Database table '{table_name}'"
            )


    # mps: 3
    @staticmethod
    def fetch_rows(
            table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices'],
            target_column: str,
            target_value: str | int | float | None = None,
    ) -> dict | None:
        """
        Fetch one or more rows from a table, where the value of target_column is target_value.
        :param table_name: Table to fetch from
        :param target_column: Which column to match
        :param target_value: Which value to match
        :return: Dict containing the fetched rows, in the form of {primary_key: row}
        """
        try:
            con = sqlite3.connect(MAIN_DATABASE_PATH)
            con.row_factory = dict_factory
            cur = con.cursor()
            cur.execute(f"""SELECT * FROM {table_name} WHERE {target_column} = ?;""", (target_value,))
            result = {row[f"{table_name[:-1]}_id"]: row for row in cur.fetchall()}
            return result
        except Exception as exc:
            print_error(
                error_message=exc,
                more_infos=f"Error occurred while fetching rows from table {table_name}, where '{target_column}' == '{target_value}';`"
            )


    def update_item(
            self,
            table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices'],
            item_id: str,
            table_column: str,
            new_value: str | int | float | None
    ) -> None:
        """
        Updates the specified value from table by ID
        :param table_name: name of the table
        :param item_id: what item to update
        :param table_column: which column to update
        :param new_value: new value
        :return:
        """

        primary_key = table_name[:-1] + "_id"

        sql_command = f"""UPDATE {table_name} SET {table_column} = ? WHERE {primary_key} = ?;"""
        self.execute_query(sql_command, (str(new_value), item_id,), False)



APP_DATABASE = MyAppDatabase(MAIN_DATABASE_PATH)

if __name__ == '__main__':
    APP_DATABASE.reset_database()
    # APP_DATABASE.initialize_tables()


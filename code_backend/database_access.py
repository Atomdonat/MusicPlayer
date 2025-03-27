import os

from code_backend.shared_config import *
from code_backend.secondary_methods import (
    dict_factory, get_str_from_json_file,
    load_sql_query, absolute_path, check_spotify_id
)
from code_backend.exceptions import DatabaseException, InputException, SpotifyIdException


class DatabaseAccess:
    """
    class acting as Data Access Object for Database. Handling all access to the Database
    """

    def __init__(self, database_file: str) -> None:
        """
        initialize the database using a path

        :param database_file: (relative) path to the database file
        :raises DatabaseException: If Exception related to the Database occurs
        """

        database_file = absolute_path(database_file, is_file=True)
        if not os.path.isfile(database_file):
            raise DatabaseException("Database file not found")

        try:
            self.database = sqlite3.connect(database_file)
            self.cursor = self.database.cursor()
            self.sql_query_queue = []

        except sqlite3.Error as error:
            raise DatabaseException(error_message=error, more_infos=f"Exception occurred while connecting to database: '{database_file}'")

    @property
    def table_struct(self) -> dict[str, dict[str, list]]:
        """
        Get the structure of all tables in the database. This only includes the table names, primary keys and column names per table

        :return: Dict containing the database structure, in the form of {table_name: {'ids': [...], 'columns': [...]}}
        :raises DatabaseException: If Exception related to the Database occurs
        """

        table_struct = {}

        database_tables = self.execute_script("""SELECT name FROM sqlite_master WHERE type='table';""", fetch=True)
        for current_table in database_tables:
            prim_keys = []
            columns = []

            table_info = self.execute_script(f"""PRAGMA table_info('{current_table[0]}')""", fetch=True)
            for _, col_name, _, _, _, col_is_pk in table_info:
                if col_is_pk > 0: prim_keys.append(col_name)
                columns.append(col_name)

            table_struct[current_table[0]] = {"ids": prim_keys, "columns": columns}

        return table_struct

    def execute_query(self, sql_query: str, parameters=(), fetch: bool = False) -> None | list:
        """
        Execute a SQL query **with** parameters

        :param sql_query: SQL query
        :param parameters: parameters to pass to the SQL query
        :param fetch: If to Fetch Data (True: Fetch/Get Data; False: Update/Give Data)
        :return: If fetch=True data gets returned, else returns None
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(sql_query, str):
            raise InputException(item_value=sql_query, valid_values="sql query", valid_types=str)

        if not isinstance(fetch, bool):
            raise InputException(item_value=fetch, valid_values=(True, False), valid_types=bool)

        with self.database:
            try:
                self.cursor.execute(sql_query, parameters)
                if fetch:
                    return self.cursor.fetchall()

            except Exception as error:
                # Replaces image byte strings with '...' (shortens output immensely)
                if isinstance(parameters, dict):
                    pop_type = list(parameters.keys())[0][:-3]
                    parameters[f"{pop_type}_image"] = parameters[f"{pop_type}_image"][:4] + "..."
                raise DatabaseException(error_message=error, more_infos=(
                    f"Exception occurred while trying to execute query: '{sql_query}'"
                    f"{f"\nwith parameters: {json.dumps(parameters, indent=4) if isinstance(parameters, dict) else parameters}" if parameters else ""}"
                ))

            finally:
                self.database.commit()

    def execute_script(self, sql_script: str, fetch: bool = False):
        """
        Execute a SQL script **without** parameters

        :param sql_script: SQL query
        :param fetch: If to Fetch Data (True: Fetch/Get Data; False: Update/Give Data)
        :return: If fetch=True data gets returned, else returns None
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(sql_script, str):
            raise InputException(item_value=sql_script, valid_values="sql script", valid_types=str)

        if not isinstance(fetch, bool):
            raise InputException(item_value=fetch, valid_values=(True, False), valid_types=bool)

        with self.database:
            try:
                if fetch:
                    self.cursor.execute(sql_script, ())
                    return self.cursor.fetchall()
                else:
                    self.cursor.executescript(sql_script)

            except Exception as error:
                raise DatabaseException(error_message=error, more_infos=f"Exception occurred while trying to execute script: '{sql_script}'")

            finally:
                self.database.commit()

    def execute_queue_queries(self) -> None:
        """
        Execute all SQL queries queued in self.sql_query_queue

        :return:
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """
        for sql_query, sql_values in self.sql_query_queue:
            self.execute_query(sql_query, sql_values)

    def split_queries(self, sql_query: str, parameter: dict):
        """
        Split SQL script/query containing multiple commands with parameters into multiple queries and execute them. The placeholders in the script must match the keys in parameter.

        :param sql_query: SQL query
        :param parameter: parameters to pass to the SQL query
        :return:
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(sql_query, str):
            raise InputException(item_value=sql_query, valid_values="sql query", valid_types=str)

        if not isinstance(parameter, dict):
            raise InputException(item_value=parameter, valid_values="{column: value}", valid_types=dict)

        queries = [f"{query};" for query in sql_query.split(';')]

        for query in queries:
            self.execute_query(sql_query=query, parameters=parameter)

    def add_item_to_table(self, table_name: str, query_template: str, **kwargs) -> None:
        """
        Adds item to table if it does not exist, otherwise, the insert will be ignored. If not all required keys are passed, the default value 'NULL' will be used.

        :param table_name: Which table to add
        :param query_template: sql query template in the correct format
        :param kwargs: which arguments are passed to database, should be column=value assignments
        :return:
        :raises CustomException: If Exception occurs
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in self.table_struct.keys():
            raise InputException(item_value=table_name, valid_values=tuple(self.table_struct.keys()), valid_types=str)

        missing_keys = set(self.table_struct[table_name]["columns"]) - set(kwargs.keys())
        if missing_keys:
            print(InputException(
                item_value=missing_keys,
                valid_values=", ".join({f"{i}: Any" for i in self.table_struct[table_name]["columns"]}),
                valid_types=Any)
            )

        # set columns to either kwargs value or None (default)
        sql_values = {
            key: str(kwargs.get(key)) if isinstance(kwargs.get(key, None), (list, tuple, dict)) else kwargs.get(key)
            for key in self.table_struct[table_name]["columns"]
        }
        self.execute_query(query_template, sql_values)

    def remove_specific_item(self, table_name: str, item_id: str):
        """
        remove item from table by ID

        :param table_name: name of the table
        :param item_id: what item to remove
        :return:
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in self.table_struct.keys():
            raise InputException(item_value=table_name, valid_values=tuple(self.table_struct.keys()), valid_types=str)

        primary_key = self.table_struct[table_name]["ids"][0]
        sql_delete_command = f"DELETE FROM {table_name} WHERE {primary_key} = ?"

        self.execute_query(sql_delete_command, (item_id,))

    def reset_table(self, table_name: str):
        """
        reset table to initial state

        :param table_name: name of the table
        :return:
        :raises CustomException: If Exception occurs
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in self.table_struct.keys():
            raise InputException(item_value=table_name, valid_values=tuple(self.table_struct.keys()), valid_types=str)

        self.execute_script(f"""DELETE * FROM {table_name}""", False)

    def reset_database(self):
        """
        reset complete database (all tables) to initial state

        :return:
        :raises CustomException: If Exception occurs
        :raises DatabaseException: If Exception related to the Database occurs
        """

        for current_table in self.table_struct.keys():
            self.reset_table(table_name=current_table)

    def fetch_row(self, table_name: str, item_id: str, table_column: str = '*') -> list | str | int | float | None:
        """
        fetch item from table by ID

        :param table_name: name of the table
        :param item_id: what item to fetch
        :param table_column: what column to fetch (default: '*' fetches all columns)
        :return: hopefully what you asked for (row, value of column, None, ¯\\_(ツ)_/¯)
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in self.table_struct.keys():
            raise InputException(item_value=table_name, valid_values=tuple(self.table_struct.keys()), valid_types=str)

        primary_key = self.table_struct[table_name]["ids"][0]
        sql_command = f"""SELECT {table_column} FROM {table_name} WHERE {primary_key} = ?;"""

        result = self.execute_query(sql_command, (item_id,), True)
        return result[0] if result else None

    def fetch_column(self, table_name: str, table_column: str) -> list | None:
        """
        fetch column from table by ID

        :param table_name: name of the table
        :param table_column: what column to fetch
        :return: wanted column
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in self.table_struct.keys():
            raise InputException(item_value=table_name, valid_values=tuple(self.table_struct.keys()), valid_types=str)

        if not isinstance(table_column, str) or table_column not in self.table_struct[table_name]["columns"]:
            raise InputException(item_value=table_column, valid_values=tuple(self.table_struct[table_name]["columns"]), valid_types=str)

        result = self.execute_query(f"""SELECT {table_column} FROM {table_name};""", (), fetch=True)

        try:
            return [row[0] for row in result] if result else None
        except Exception as error:
            DatabaseException(
                error_message=error,
                more_infos=f"Exception occurred while fetching column '{table_column}' from Database table '{table_name}'"
            )

    def fetch_rows(
            self,
            table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices'],
            target_column: str,
            target_value: str | int | float | None = None
    ) -> dict | None:
        """
        Fetch one or more rows from a table, where the value of target_column is target_value.

        :param table_name: Table to fetch from
        :param target_column: Which column to match
        :param target_value: Which value to match
        :return: Dict containing the fetched rows, in the form of {primary_key: row}
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in self.table_struct.keys():
            raise InputException(item_value=table_name, valid_values=tuple(self.table_struct.keys()), valid_types=str)

        if not isinstance(target_column, str) or target_column not in self.table_struct[table_name]["columns"]:
            raise InputException(item_value=target_column, valid_values=tuple(self.table_struct[table_name]["columns"]), valid_types=str)

        if not isinstance(target_value, (str, int, float)) and target_value is not None:
            raise InputException(item_value=target_value, valid_values="any string, int, float or None", valid_types=(str, int, float, None))

        try:
            con = sqlite3.connect(MAIN_DATABASE_PATH)
            con.row_factory = dict_factory
            cur = con.cursor()
            cur.execute(f"""SELECT * FROM {table_name} WHERE {target_column} = ?;""", (target_value,))
            result = {row[f"{table_name[:-1]}_id"]: row for row in cur.fetchall()}
            return result
        except Exception as error:
            DatabaseException(
                error_message=error,
                more_infos=f"Exception occurred while fetching rows from table {table_name}, where '{target_column}' == '{target_value}';`"
            )

    def update_item(
            self,
            table_name: str,
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
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in self.table_struct.keys():
            raise InputException(item_value=table_name, valid_values=tuple(self.table_struct.keys()), valid_types=str)

        if not isinstance(table_column, str) or table_column not in self.table_struct[table_name]["columns"]:
            raise InputException(item_value=table_column, valid_values=tuple(self.table_struct[table_name]["columns"]), valid_types=str)

        if not isinstance(new_value, (str, int, float)) and new_value is not None:
            raise InputException(item_value=new_value, valid_values="any string, int, float or None", valid_types=(str, int, float, None))

        primary_key = self.table_struct[table_name]["ids"][0]
        sql_command = f"""UPDATE {table_name} SET {table_column} = ? WHERE {primary_key} = ?;"""

        self.execute_query(sql_command, (str(new_value), item_id,), False)


class MyAppDatabase(DatabaseAccess):
    """
    class acting as Data Access Object for Main Database
    """
    def __init__(self, database_file: str) -> None:
        super().__init__(database_file)

    def add_dummies(self) -> None:
        """
        Add dummy data to the database to avoid Exceptions and to test methods

        :return:
        :raises CustomException: If Exception occurs
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
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
        :raises CustomException: If Exception occurs
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
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
        Adds item to table if it does not exist, otherwise, the insert will be ignored. If not all required keys are passed, the default value 'NULL' will be used.

        :param table_name: Which table to add
        :param kwargs: which arguments are passed to database
        :return:
        :raises CustomException: If Exception occurs
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in ['albums', 'artists', 'tracks', 'playlists', 'users', 'devices']:
            raise InputException(item_value=table_name, valid_values=('albums', 'artists', 'tracks', 'playlists', 'users', 'devices'), valid_types=str)

        sql_query = load_sql_query(f"code_backend/sql_queries/insert_{table_name}.sql")
        return super().add_item_to_table(
            table_name=table_name,
            query_template=sql_query,
            **kwargs
        )

    def remove_specific_item(self, table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices'], item_id: str):
        """
        remove item from table by ID

        :param table_name: name of the table
        :param item_id: what item to remove
        :return:
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        :raises SpotifyIdException: if spotify id is invalid
        """

        if not isinstance(table_name, str) or table_name not in ['albums', 'artists', 'tracks', 'playlists', 'users', 'devices']:
            raise InputException(item_value=table_name, valid_values=('albums', 'artists', 'tracks', 'playlists', 'users', 'devices'), valid_types=str)

        match table_name:
            case "devices":
                if not check_spotify_id(item_id, is_device=True):
                    raise SpotifyIdException(item_id, table_name[:-1])
            case "users":
                if not check_spotify_id(item_id, is_user=True):
                    raise SpotifyIdException(item_id, table_name[:-1])
            case _:
                if not check_spotify_id(item_id):
                    raise SpotifyIdException(item_id, table_name[:-1])

        return super().remove_specific_item(table_name=table_name, item_id=item_id)

    def reset_table(self, table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices']):
        """
        reset table to initial state

        :param table_name: name of the table
        :return:
        :raises CustomException: If Exception occurs
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in ['albums', 'artists', 'tracks', 'playlists', 'users', 'devices']:
            raise InputException(item_value=table_name, valid_values=('albums', 'artists', 'tracks', 'playlists', 'users', 'devices'), valid_types=str)

        super().reset_table(table_name=table_name)
        self.add_dummies()

    def reset_database(self):
        """
        reset complete database (all tables) to initial state

        :return:
        :raises CustomException: If Exception occurs
        :raises DatabaseException: If Exception related to the Database occurs
        """

        for table_name in self.table_struct.keys():
            self.execute_script(sql_script=f"""DROP TABLE {table_name};""")

        self.initialize_tables()


    def fetch_row(
            self,
            table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices'],
            item_id: str,
            table_column: str = '*'
    ) -> list | str | int | float | None:
        """
        fetch item from table by ID

        :param table_name: name of the table
        :param item_id: what item to fetch
        :param table_column: what column to fetch (default: '*' fetches all columns)
        :return: hopefully what you asked for (row, value of column, None, ¯\\_(ツ)_/¯)
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        :raises SpotifyIdException: if spotify id is invalid
        """

        if not isinstance(table_name, str) or table_name not in ['albums', 'artists', 'tracks', 'playlists', 'users', 'devices']:
            raise InputException(item_value=table_name, valid_values=('albums', 'artists', 'tracks', 'playlists', 'users', 'devices'), valid_types=str)

        match table_name:
            case "devices":
                if not check_spotify_id(item_id, is_device=True):
                    raise SpotifyIdException(item_id, table_name[:-1])
            case "user":
                if not check_spotify_id(item_id, is_user=True):
                    raise SpotifyIdException(item_id, table_name[:-1])
            case _:
                if not check_spotify_id(item_id):
                    raise SpotifyIdException(item_id, table_name[:-1])

        return super().fetch_row(
            table_name=table_name,
            item_id=item_id,
            table_column=table_column
        )

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
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in ['albums', 'artists', 'tracks', 'playlists', 'users', 'devices']:
            raise InputException(item_value=table_name, valid_values=('albums', 'artists', 'tracks', 'playlists', 'users', 'devices'), valid_types=str)

        return super().fetch_column(table_name=table_name, table_column=table_column)

    def fetch_rows(
            self,
            table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'devices'],
            target_column: str,
            target_value: str | int | float | None = None
    ) -> dict | None:
        """
        Fetch one or more rows from a table, where the value of target_column is target_value.

        :param table_name: Table to fetch from
        :param target_column: Which column to match
        :param target_value: Which value to match
        :return: Dict containing the fetched rows, in the form of {primary_key: row}
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        """

        if not isinstance(table_name, str) or table_name not in ['albums', 'artists', 'tracks', 'playlists', 'users', 'devices']:
            raise InputException(item_value=table_name, valid_values=('albums', 'artists', 'tracks', 'playlists', 'users', 'devices'), valid_types=str)

        return super().fetch_rows(table_name=table_name, target_column=target_column, target_value=target_value)

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
        :raises DatabaseException: If Exception related to the Database occurs
        :raises InputException: if input is invalid
        :raises SpotifyIdException: if spotify id is invalid
        """

        if not isinstance(table_name, str) or table_name not in ['albums', 'artists', 'tracks', 'playlists', 'users', 'devices']:
            raise InputException(item_value=table_name, valid_values=('albums', 'artists', 'tracks', 'playlists', 'users', 'devices'), valid_types=str)

        if table_name == "devices" and not check_spotify_id(item_id, is_device=True):
            raise SpotifyIdException(item_id, table_name[:-1])

        elif table_name == "users" and not check_spotify_id(item_id, is_user=True):
            raise SpotifyIdException(item_id, table_name[:-1])

        elif table_name in ['albums', 'artists', 'tracks', 'playlists'] and not check_spotify_id(item_id):
            raise SpotifyIdException(item_id, table_name[:-1])

        return super().update_item(table_name=table_name, item_id=item_id, table_column=table_column, new_value=new_value)


APP_DATABASE = MyAppDatabase(MAIN_DATABASE_PATH)

if __name__ == '__main__':
    """"""
    APP_DATABASE.reset_database()
    APP_DATABASE.initialize_tables()

from secondary_methods import *


class MyAppDatabase:
    def __init__(self, database_file: str) -> None:
        if not os.path.isfile(database_file):
            with open(database_file, 'w') as file:
                pass

        try:
            self.database = sqlite3.connect(database_file)
        except sqlite3.Error as e:
            print('Db Not found', str(e))
        finally:
            self.cursor = self.database.cursor()

    def execute_query(self, sql_query: str, parameters = None):
        with self.database:
            try:
                self.cursor.execute(sql_query, parameters)

            except Exception as e:
                if e is not None:
                    print(e)

            finally:
                # noinspection PyStatementEffect
                self.cursor.lastrowid
                self.database.commit()

    def execute_script(self, sql_script: str):
        with self.database:
            try:
                self.cursor.executescript(sql_script)

            except Exception as e:
                if e is not None:
                    print(e)

            finally:
                # noinspection PyStatementEffect
                self.cursor.lastrowid
                self.database.commit()

    def initialize_tables(self) -> None:
        sqlite_command = """
            CREATE TABLE IF NOT EXISTS albums (
                album_id TEXT PRIMARY KEY,
                album_name TEXT,
                album_url TEXT,
                album_image TEXT,
                genre_names TEXT,
                total_duration INTEGER,
                track_count INTEGER,
                artist_ids TEXT,
                track_ids TEXT,
                popularity INTEGER,
                blacklisted INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS artists (
                artist_id TEXT PRIMARY KEY,
                artist_name TEXT,
                artist_url TEXT,
                artist_image TEXT,
                genre_names TEXT,
                follower INTEGER,
                album_ids TEXT,
                playlist_ids TEXT,
                top_tracks_ids TEXT,
                popularity INTEGER,
                blacklisted INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS  genres (
                genre_name TEXT PRIMARY KEY,
                acousticness_lower_limit REAL,
                acousticness_upper_limit REAL,
                danceability_lower_limit REAL,
                danceability_upper_limit REAL,
                duration_ms INTEGER,
                energy_lower_limit REAL,
                energy_upper_limit REAL,
                instrumentalness_lower_limit REAL,
                instrumentalness_upper_limit REAL,
                key_lower_limit INTEGER,
                key_upper_limit INTEGER,
                liveness_lower_limit REAL,
                liveness_upper_limit REAL,
                loudness_lower_limit REAL,
                loudness_upper_limit REAL,
                mode_lower_limit INTEGER,
                mode_upper_limit INTEGER,
                speechiness_lower_limit REAL, 
                speechiness_upper_limit REAL,
                tempo_lower_limit REAL,
                tempo_upper_limit REAL,
                valence_lower_limit REAL,
                valence_upper_limit REAL,
                popularity INTEGER,
                blacklisted INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS playlists(
                playlist_id TEXT PRIMARY KEY,
                playlist_name TEXT,
                playlist_url TEXT,
                playlist_image TEXT,
                genre_names TEXT,
                total_duration INTEGER,
                track_count INTEGER,
                owner_id TEXT,
                track_ids TEXT,
                popularity INTEGER,
                blacklisted INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS tracks (
                track_id TEXT PRIMARY KEY,
                track_name TEXT,
                track_url TEXT,
                track_image TEXT,
                genre_names TEXT,
                track_duration INTEGER,
                artist_ids TEXT,
                album_ids TEXT,
                playlist_ids TEXT,
                popularity INTEGER,
                blacklisted INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS track_analysis (
                track_id TEXT PRIMARY KEY,
                track_name TEXT,
                track_acousticness REAL,
                track_danceability REAL,
                track_duration_ms INTEGER,
                track_energy REAL,
                track_instrumentalness REAL,
                track_key INTEGER,
                track_liveness REAL,
                track_loudness REAL,
                track_mode INTEGER,
                track_speechiness REAL,
                track_tempo REAL,
                track_valence REAL,
                FOREIGN KEY (track_id) REFERENCES tracks(track_id)
            );
            
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                user_name TEXT,
                user_url TEXT,
                user_image TEXT,
                follower INTEGER,
                playlist_ids TEXT,
                top_tracks_ids TEXT,
                top_artists_ids TEXT,
                top_genre_names TEXT,
                popularity INTEGER,
                blacklisted INTEGER
            );
            """

        self.execute_script(sqlite_command)

    def add_album_to_albums(self, album: Album):
        sql_command = f"""INSERT INTO albums (
            album_id,
            album_name,
            album_url,
            album_image,
            genre_names,
            total_duration,
            track_count,
            artist_ids,
            track_ids,
            popularity,
            blacklisted
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?) """

        sql_values = (
            album.album_id,
            album.album_name,
            album.album_url,
            album.album_image,
            string_to_list(album.genre_names),
            album.total_duration,
            album.track_count,
            string_to_list(album.artist_ids),
            string_to_list(album.track_ids),
            album.popularity,
            album.blacklisted
        )

        self.execute_query(sql_command, sql_values)

    def add_artist_to_artists(self, artist: Artist):
        sql_command = f"""INSERT INTO artists (
            artist_id,
            artist_name,
            artist_url,
            artist_image,
            genre_names,
            follower,
            album_ids,
            playlist_ids,
            top_tracks_ids,
            popularity,
            blacklisted
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?) """

        sql_values = (
            artist.artist_id,
            artist.artist_name,
            artist.artist_url,
            artist.artist_image,
            string_to_list(artist.genre_names),
            artist.follower,
            string_to_list(artist.album_ids),
            string_to_list(artist.playlist_ids),
            string_to_list(artist.top_tracks_ids),
            artist.popularity,
            artist.blacklisted
        )

        self.execute_query(sql_command, sql_values)

    def add_playlist_to_playlists(self, playlist: Playlist):
        sql_command = f"""INSERT INTO playlists (
            playlist_id,
            playlist_name,
            playlist_url,
            playlist_image,
            genre_names,
            total_duration,
            track_count,
            owner_id,
            track_ids,
            popularity,
            blacklisted
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?) """

        sql_values = (
            playlist.playlist_id,
            playlist.playlist_name,
            playlist.playlist_url,
            playlist.playlist_image,
            string_to_list(playlist.genre_names),
            playlist.total_duration,
            playlist.track_count,
            playlist.owner_id,
            string_to_list(playlist.track_ids),
            playlist.popularity,
            playlist.blacklisted
        )

        self.execute_query(sql_command, sql_values)

    def add_track_to_tracks(self, track: Track):
        sql_command = f"""INSERT INTO tracks (
            track_id,
            track_name,
            track_url,
            track_image,
            genre_names,
            track_duration,
            artist_ids,
            album_ids,
            playlist_ids,
            popularity,
            blacklisted
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?) """

        sql_values = (
            track.track_id,
            track.track_name,
            track.track_url,
            track.track_image,
            string_to_list(track.genre_names),
            track.track_duration,
            string_to_list(track.artist_ids),
            string_to_list(track.album_ids),
            string_to_list(track.playlist_ids),
            track.popularity,
            track.blacklisted
        )

        self.execute_query(sql_command, sql_values)

    def add_user_to_users(self, user: User):
        sql_command = f"""INSERT INTO users(
            user_id,
            user_name,
            user_url,
            user_image,
            follower,
            playlist_ids,
            top_tracks_ids,
            top_artists_ids,
            top_genre_names,
            popularity,
            blacklisted
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?) """

        sql_values = (
            user.user_id,
            user.user_name,
            user.user_url,
            user.user_image,
            user.follower,
            string_to_list(user.playlist_ids),
            string_to_list(user.top_tracks_ids),
            string_to_list(user.top_artists_ids),
            string_to_list(user.top_genre_names),
            user.popularity,
            user.blacklisted
        )

        self.execute_query(sql_command, sql_values)

    def add_genre_to_genres(self, genre: Genre):
        sql_command = f"""INSERT INTO genres (
            genre_name,
            acousticness_lower_limit,
            acousticness_upper_limit,
            danceability_lower_limit,
            danceability_upper_limit,
            duration_ms,
            energy_lower_limit,
            energy_upper_limit,
            instrumentalness_lower_limit,
            instrumentalness_upper_limit,
            key_lower_limit,
            key_upper_limit,
            liveness_lower_limit,
            liveness_upper_limit,
            loudness_lower_limit,
            loudness_upper_limit,
            mode_lower_limit,
            mode_upper_limit,
            speechiness_lower_limit,
            speechiness_upper_limit,
            tempo_lower_limit,
            tempo_upper_limit,
            valence_lower_limit,
            valence_upper_limit,
            popularity,
            blacklisted
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """

        sql_values = (
            genre.genre_name,
            genre.acousticness_lower_limit,
            genre.acousticness_upper_limit,
            genre.danceability_lower_limit,
            genre.danceability_upper_limit,
            genre.duration_ms,
            genre.energy_lower_limit,
            genre.energy_upper_limit,
            genre.instrumentalness_lower_limit,
            genre.instrumentalness_upper_limit,
            genre.key_lower_limit,
            genre.key_upper_limit,
            genre.liveness_lower_limit,
            genre.liveness_upper_limit,
            genre.loudness_lower_limit,
            genre.loudness_upper_limit,
            genre.mode_lower_limit,
            genre.mode_upper_limit,
            genre.speechiness_lower_limit,
            genre.speechiness_upper_limit,
            genre.tempo_lower_limit,
            genre.tempo_upper_limit,
            genre.valence_lower_limit,
            genre.valence_upper_limit,
            genre.popularity,
            genre.blacklisted
        )

        self.execute_query(sql_command, sql_values)

    def add_track_to_track_analysis(self, track_analysis: TrackAnalysis):
        sql_command = f"""INSERT INTO track_analysis (
            track_id,
            track_name,
            track_acousticness,
            track_danceability,
            track_duration_ms,
            track_energy,
            track_instrumentalness,
            track_key,
            track_liveness,
            track_loudness,
            track_mode,
            track_speechiness,
            track_tempo,
            track_valence
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) """

        sql_values = (
            track_analysis.track_id,
            track_analysis.track_name,
            track_analysis.track_acousticness,
            track_analysis.track_danceability,
            track_analysis.track_duration_ms,
            track_analysis.track_energy,
            track_analysis.track_instrumentalness,
            track_analysis.track_key,
            track_analysis.track_liveness,
            track_analysis.track_loudness,
            track_analysis.track_mode,
            track_analysis.track_speechiness,
            track_analysis.track_tempo,
            track_analysis.track_valence,
        )

        self.execute_query(sql_command, sql_values)

    def remove_specific_entry(self, table_name: str, entry_id: str):
        if table_name == 'track_analysis':
            primary_key = 'track_id'
        else:
            primary_key = table_name[:-1] + "_id"
        sql_delete_command = f'DELETE FROM {table_name} WHERE {primary_key} = ?'

        self.execute_query(sql_delete_command, (entry_id,))

    def reset_table(self, table_name: str):
        # noinspection PyStatementEffect
        self.cursor.execute(f'DELETE FROM {table_name}')
        self.database.commit()

    def reset_database(self):
        self.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;""")
        table_names = self.cursor.fetchall()

        if table_names:
            for table_name in table_names:
                self.cursor.execute(f"""DROP TABLE {table_name[0]};""")

            self.database.commit()
            self.initialize_tables()

    def update_value(self, table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users', 'genres', 'track_analysis'], item_id: str, table_column: str, new_value):
        if table_name == 'track_analysis':
            primary_key = 'track_id'
        else:
            primary_key = table_name[:-1] + "_id"
        sql_command = f"""UPDATE {table_name} SET {table_column} = %s WHERE {primary_key} = %s;"""
        self.execute_query(sql_command, (new_value, item_id,))


if __name__ == '__main__':
    database = MyAppDatabase('../Databases/main_database.db')
    database.reset_database()

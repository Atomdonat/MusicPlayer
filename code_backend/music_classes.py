from spotipy import Spotify

from secondary_methods import *
from spotify_access import spotify_client
from database_access import MyAppDatabase


sp = spotify_client()
market = 'DE'
my_app_database: MyAppDatabase = MyAppDatabase('../Databases/main_database.db')


class Album:
    def __init__(self, spotify_album_id: str):
        spotify_uri = 'spotify:album:' + spotify_album_id
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify Album ID")

        cursor = my_app_database.database.execute('SELECT * from albums WHERE album_id = ?', (spotify_album_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            try:
                self.instance = sp.album(album_id=spotify_album_id, market=market)
            except Exception as e:
                print(f'\x1b[31mError with Spotify API request for {spotify_uri}:\n{e}')
                sys.exit(1)

            self.album_id: str = self.instance['id']
            self.album_name: str = self.instance['name']
            self.album_url: str = self.instance['external_urls']['spotify']

            if 'url' not in self.instance['images'][0]:
                self.album_image: str = file_image_bytes(no_image_path)
            else:
                self.album_image: str = spotify_image_bytes(self.instance['images'][0]['url'])

            self.track_count: int = self.instance['total_tracks']

            my_app_database.add_album_to_albums(self)

        else:
            # Unpack the database result into instance variables
            self.album_id, \
                self.album_name, \
                self.album_url, \
                self.album_image, \
                self._genre_names, \
                self._total_duration, \
                self.track_count, \
                self._artist_ids, \
                self._track_ids, \
                self._popularity, \
                self._blacklisted = result

            # convert List Strings back to list
            self._genre_names = list_from_id_string(self._genre_names)
            self._artist_ids = list_from_id_string(self._artist_ids)
            self._track_ids = list_from_id_string(self._track_ids)

            # No need to fetch from Spotify API in this case
            self.instance = None

    @property
    def genre_names(self) -> list[str]:
        if not hasattr(self, '_genre_names'):
            genres = []

            # ToDo: implement

            self._genre_names = genres
        return self._genre_names

    @property
    def artist_ids(self) -> list[str]:
        if not hasattr(self, '_artist_ids'):
            artists = []
            for artist in self.instance['artists']:
                current_artist_id = artist['id']
                artists.append(current_artist_id)
                current_artist_object = Artist(current_artist_id)

                # add album_id to artists
                my_app_database.cursor.execute('SELECT album_ids from artists WHERE artist_id = ?', (current_artist_object.artist_id,))
                used_in_playlists = my_app_database.cursor.fetchone()

                if self.album_id not in used_in_playlists:
                    my_app_database.update_value(
                        table_name='artists',
                        item_id=current_artist_object.artist_id,
                        table_column='album_ids',
                        new_value=self.album_id
                    )

            self._artist_ids = artists
        return self._artist_ids

    @property
    def track_ids(self) -> list[str]:
        if not hasattr(self, '_track_ids'):
            tracks = []
            for current_track in self.instance['tracks']['items']:
                tracks.append(current_track['id'])
            self._track_ids = tracks
        return self._track_ids

    @property
    def total_duration(self) -> int:
        if not hasattr(self, '_total_duration'):
            duration = 0
            for current_track in self.instance['tracks']['items']:
                duration += int(current_track['duration_ms'])
            self._total_duration = duration
        return self._total_duration

    @property
    def popularity(self) -> int:
        if not hasattr(self, '_popularity'):
            self._popularity = max_popularity

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        self.popularity -= skipping_step

    @property
    def blacklisted(self) -> int:
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        self._blacklisted = new_value


class Artist:
    def __init__(self, spotify_artist_id: str):
        spotify_uri = 'spotify:artist:' + spotify_artist_id
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify Artist ID")

        cursor = my_app_database.database.execute('SELECT * from artists WHERE artist_id = ?', (spotify_artist_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            try:
                self.instance = sp.artist(artist_id=spotify_artist_id)
            except Exception as e:
                print(f'\x1b[31mError with Spotify API request for {spotify_uri}:\n{e}')
                sys.exit(1)
            
            self.artist_id: str = self.instance['id']
            self.artist_name: str = self.instance['name']
            self.artist_url: str = self.instance['external_urls']['spotify']

            if 'url' not in self.instance['images'][0]:
                self.artist_image: str = file_image_bytes(no_image_path)
            else:
                self.artist_image: str = spotify_image_bytes(self.instance['images'][0]['url'])

            self.follower:int = self.instance['followers']['total']
            self.album_ids: List[str] = []
            self.playlist_ids: List[str] = []

            my_app_database.add_artist_to_artists(self)

        else:
            # Unpack the database result into instance variables
            self.artist_id, \
                self.artist_name, \
                self.artist_url, \
                self.artist_image, \
                self._genre_names, \
                self.follower, \
                self.album_ids, \
                self.playlist_ids, \
                self._top_tracks_ids, \
                self._popularity, \
                self._blacklisted = result

            # convert List Strings back to list
            self._genre_names = list_from_id_string(self._genre_names)
            self._top_tracks_ids = list_from_id_string(self._top_tracks_ids)
            self.album_ids = list_from_id_string(self.album_ids)
            self.playlist_ids = list_from_id_string(self.playlist_ids)

            # No need to fetch from Spotify API in this case
            self.instance = None

    @property
    def genre_names(self) -> list[str]:
        if not hasattr(self, '_genre_names'):
            genres = []
            for genre in self.instance['genres']:
                genres.append(genre)
            self._genre_names = genres
        return self._genre_names

    @property
    def top_tracks_ids(self) -> list[str]:
        if not hasattr(self, '_top_tracks_ids'):
            top_tracks = sp.artist_top_tracks(self.artist_id, country="DE")
            top_track_list = []
            for top_track in top_tracks['tracks']:
                top_track_list.append(top_track['id'])

            self._top_tracks_ids = top_track_list

        return self._top_tracks_ids

    @property
    def popularity(self) -> int:
        if not hasattr(self, '_popularity'):
            self._popularity = max_popularity

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        self.popularity -= skipping_step

    @property
    def blacklisted(self) -> int:
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        self._blacklisted = new_value


class Playlist:
    def __init__(self, spotify_playlist_id: str):
        spotify_uri = 'spotify:playlist:' + spotify_playlist_id
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify Playlist ID")

        cursor = my_app_database.database.execute('SELECT * from playlists WHERE playlist_id = ?', (spotify_playlist_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            try:
                self.instance = sp.playlist(playlist_id=spotify_playlist_id, market=market)
            except Exception as e:
                print(f'\x1b[31mError with Spotify API request for {spotify_uri}:\n{e}')
                sys.exit(1)

            self.playlist_id: str = self.instance['id']
            self.playlist_name: str = self.instance['name']
            self.playlist_url: str = self.instance['external_urls']['spotify']

            if 'url' not in self.instance['images'][0]:
                self.playlist_image: str = file_image_bytes(no_image_path)
            else:
                self.playlist_image: str = spotify_image_bytes(self.instance['images'][0]['url'])

            self.track_count: int = self.instance['tracks']['total']
            self.owner_id: str = self.instance['owner']['id']

            my_app_database.add_playlist_to_playlists(self)

        else:
            # Unpack the database result into instance variables
            self.playlist_id, \
                self.playlist_name, \
                self.playlist_url, \
                self.playlist_image, \
                self._genre_names, \
                self._total_duration, \
                self.track_count, \
                self.owner_id, \
                self._track_ids, \
                self._popularity, \
                self._blacklisted = result

            # convert List Strings back to list
            self._genre_names = list_from_id_string(self._genre_names)
            self._track_ids = list_from_id_string(self._track_ids)

            # No need to fetch from Spotify API in this case
            self.instance = None

    @property
    def genre_names(self) -> list[str]:
        if not hasattr(self, '_genre_names'):
            genres = []

            # ToDo: implement

            self._genre_names = genres
        return self._genre_names

    @property
    def track_ids(self) -> list[str]:
        if not hasattr(self, '_track_ids'):
            tracks = []

            for current_track in self.instance['tracks']['items']:
                current_track_id = current_track['track']['id']
                tracks.append(current_track_id)
                current_track_object = Track(current_track_id)

                # add playlist_id to tracks
                my_app_database.cursor.execute('SELECT playlist_ids from tracks WHERE track_id = ?', (current_track_object.track_id,))
                used_in_playlists = my_app_database.cursor.fetchone()

                if self.playlist_id not in used_in_playlists:
                    my_app_database.update_value(
                        table_name='tracks',
                        item_id=current_track_object.track_id,
                        table_column='playlist_ids',
                        new_value=self.playlist_id
                    )

                # add playlist_id to artists (should be different method, but performance wise better)
                # ToDo: Fix below
                for current_artist_id in current_track_object.artist_ids:
                    my_app_database.cursor.execute('SELECT playlist_ids from artists WHERE artist_id = ?', (current_artist_id,))
                    used_in_playlists = my_app_database.cursor.fetchone()

                    if current_artist_id not in used_in_playlists:
                        my_app_database.update_value(
                            table_name='artists',
                            item_id=current_artist_id,
                            table_column='playlist_ids',
                            new_value=self.playlist_id
                        )

            self._track_ids = tracks
        return self._track_ids

    @property
    def total_duration(self) -> int:
        if not hasattr(self, '_total_duration'):
            duration = 0
            for current_track in self.instance['tracks']['items']:
                duration += int(current_track['track']['duration_ms'])
            self._total_duration = duration
        return self._total_duration

    @property
    def popularity(self) -> int:
        if not hasattr(self, '_popularity'):
            self._popularity = max_popularity

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        self.popularity -= skipping_step

    @property
    def blacklisted(self) -> int:
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        self._blacklisted = new_value


class Track:
    def __init__(self, spotify_track_id: str):
        spotify_uri = 'spotify:track:' + spotify_track_id
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify Track ID")

        cursor = my_app_database.database.execute('SELECT * from tracks WHERE track_id = ?', (spotify_track_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            try:
                self.instance = sp.track(track_id=spotify_track_id, market=market)
            except Exception as e:
                print(f'\x1b[31mError with Spotify API request for {spotify_uri}:\n{e}')
                sys.exit(1)
                
            self.track_id: str = self.instance['id']
            self.track_name: str = self.instance['name']
            self.track_url: str = self.instance['external_urls']['spotify']

            if 'images' not in self.instance:
                self.track_image: str = spotify_image_bytes(self.instance['album']['images'][0]['url'])
            else:
                self.track_image: str = file_image_bytes(no_image_path)

            # Playlist ID gets added when the Playlist() is instantiated
            self.playlist_ids: list[str] = []

            self.track_duration: int = self.instance['duration_ms']

            my_app_database.add_track_to_tracks(self)

        else:
            # Unpack the database result into instance variables
            self.track_id, \
                self.track_name, \
                self.track_url, \
                self.track_image, \
                self._genre_names, \
                self.track_duration, \
                self._artist_ids, \
                self._album_ids, \
                self.playlist_ids, \
                self._popularity, \
                self._blacklisted = result

            # convert List Strings back to list
            self._genre_names = list_from_id_string(self._genre_names)
            self._artist_ids = list_from_id_string(self._artist_ids)
            self._album_ids = list_from_id_string(self._album_ids)
            self._playlist_ids = list_from_id_string(self.playlist_ids)

            # No need to fetch from Spotify API in this case
            self.instance = None

    @property
    def genre_names(self) -> list[str]:
        if not hasattr(self, '_genre_names'):
            genres = []

            # ToDo: implement

            self._genre_names = genres
        return self._genre_names

    @property
    def artist_ids(self) -> list[str]:
        if not hasattr(self, '_artist_ids'):
            artists = []
            for artist in self.instance['artists']:
                artists.append(artist['id'])
            self._artist_ids = artists
        return self._artist_ids

    @property
    def album_ids(self) -> list[str]:
        if not hasattr(self, '_album_ids'):
            self._album_ids = [self.instance['album']['id']]
        return self._album_ids

    @property
    def popularity(self) -> int:
        if not hasattr(self, '_popularity'):
            self._popularity = max_popularity

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        self.popularity -= skipping_step

    @property
    def blacklisted(self) -> int:
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        self._blacklisted = new_value


class User:
    def __init__(self, spotify_user_id: str) -> None:
        spotify_uri = 'spotify:user:' + spotify_user_id
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify  ID")

        cursor = my_app_database.database.execute('SELECT * from track_analysis WHERE track_id = ?', (spotify_user_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            try:
                self.instance = sp.user(user=spotify_user_id)

            except Exception as e:
                print(f'\x1b[31mError with Spotify API request for {spotify_uri}:\n{e}')
                sys.exit(1)

            self.user_id: str = self.instance['id']
            self.user_name: str = self.instance['display_name']
            self.user_url: str = self.instance['external_urls']['spotify']

            if 'url' not in self.instance['images'][0]:
                self.user_image: str = file_image_bytes(no_image_path)
            else:
                self.user_image: str = spotify_image_bytes(self.instance['images'][0]['url'])

            self.follower: int = self.instance['followers']

            my_app_database.add_user_to_users(self)

        else:
            # Unpack the database result into instance variables
            self.user_id, \
                self.user_name, \
                self.user_url, \
                self.user_image, \
                self.follower, \
                self._playlist_ids, \
                self._top_tracks_ids, \
                self._top_artists_ids, \
                self._top_genre_names, \
                self._popularity, \
                self._blacklisted = result

            # convert List Strings back to list
            self._playlist_ids = list_from_id_string(self._playlist_ids)
            self._top_tracks_ids = list_from_id_string(self._top_tracks_ids)
            self._top_artists_ids = list_from_id_string(self._top_artists_ids)
            self._top_genre_names = list_from_id_string(self._top_genre_names)

    @property
    def playlist_ids(self) -> list[str]:
        if not hasattr(self, '_playlist_ids'):
            playlists = []
            user_playlists = sp.current_user_playlists()
            for playlist in user_playlists['items']:
                playlists.append(playlist['id'])
            self._playlist_ids = playlists
        return self._playlist_ids

    @property
    def top_tracks_ids(self) -> list[str]:
        if not hasattr(self, '_top_tracks_ids'):
            top_tracks = []
            tracks_json = sp.current_user_top_tracks(limit=10)
            for current_track in tracks_json['items']:
                top_tracks.append(current_track['id'])
            self._top_tracks_ids = top_tracks
        return self._top_tracks_ids

    @property
    def top_artists_ids(self) -> list[str]:
        if not hasattr(self, '_top_artists_ids'):
            top_artists = []
            tracks_json = sp.current_user_top_artists(limit=10)
            for current_track in tracks_json['items']:
                top_artists.append(current_track['id'])
            self._top_artists_ids = top_artists
        return self._top_artists_ids

    @property
    def top_genre_names(self) -> list[str]:
        top_genres = []

        # ToDo: figure out what to do here

        return top_genres

    @property
    def popularity(self) -> int:
        if not hasattr(self, '_popularity'):
            self._popularity = max_popularity

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        self.popularity -= skipping_step

    @property
    def blacklisted(self) -> int:
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        self._blacklisted = new_value


class Genre:
    # ToDo: figure out what to do here
    def __init__(
            self,
            genre_name: str,
            acousticness_lower_limit: float,
            acousticness_upper_limit: float,
            danceability_lower_limit: float,
            danceability_upper_limit: float,
            duration_ms: int,
            energy_lower_limit: float,
            energy_upper_limit: float,
            instrumentalness_lower_limit: float,
            instrumentalness_upper_limit: float,
            key_lower_limit: int,
            key_upper_limit: int,
            liveness_lower_limit: float,
            liveness_upper_limit: float,
            loudness_lower_limit: float,
            loudness_upper_limit: float,
            mode_lower_limit: int,
            mode_upper_limit: int,
            speechiness_lower_limit: float,
            speechiness_upper_limit: float,
            tempo_lower_limit: float,
            tempo_upper_limit: float,
            valence_lower_limit: float,
            valence_upper_limit: float
    ) -> None:

        cursor = my_app_database.database.execute('SELECT * from genres WHERE genre_name = ?', (genre_name,))
        result = cursor.fetchone()

        # Create if not in the database
        if result is None:
            self.genre_name: str = genre_name
            self.acousticness_lower_limit: float = acousticness_lower_limit
            self.acousticness_upper_limit: float = acousticness_upper_limit
            self.danceability_lower_limit: float = danceability_lower_limit
            self.danceability_upper_limit: float = danceability_upper_limit
            self.duration_ms: int = duration_ms
            self.energy_lower_limit: float = energy_lower_limit
            self.energy_upper_limit: float = energy_upper_limit
            self.instrumentalness_lower_limit: float = instrumentalness_lower_limit
            self.instrumentalness_upper_limit: float = instrumentalness_upper_limit
            self.key_lower_limit: int = key_lower_limit
            self.key_upper_limit: int = key_upper_limit
            self.liveness_lower_limit: float = liveness_lower_limit
            self.liveness_upper_limit: float = liveness_upper_limit
            self.loudness_lower_limit: float = loudness_lower_limit
            self.loudness_upper_limit: float = loudness_upper_limit
            self.mode_lower_limit: int = mode_lower_limit
            self.mode_upper_limit: int = mode_upper_limit
            self.speechiness_lower_limit: float = speechiness_lower_limit
            self.speechiness_upper_limit: float = speechiness_upper_limit
            self.tempo_lower_limit: float = tempo_lower_limit
            self.tempo_upper_limit: float = tempo_upper_limit
            self.valence_lower_limit: float = valence_lower_limit
            self.valence_upper_limit: float = valence_upper_limit

            my_app_database.add_genre_to_genres(self)

        # Unpack the database result into instance variables
        else:
            self.genre_name, \
                self.acousticness_lower_limit, \
                self.acousticness_upper_limit, \
                self.danceability_lower_limit, \
                self.danceability_upper_limit, \
                self.duration_ms, \
                self.energy_lower_limit, \
                self.energy_upper_limit, \
                self.instrumentalness_lower_limit, \
                self.instrumentalness_upper_limit, \
                self.key_lower_limit, \
                self.key_upper_limit, \
                self.liveness_lower_limit, \
                self.liveness_upper_limit, \
                self.loudness_lower_limit, \
                self.loudness_upper_limit, \
                self.mode_lower_limit, \
                self.mode_upper_limit, \
                self.speechiness_lower_limit, \
                self.speechiness_upper_limit, \
                self.tempo_lower_limit, \
                self.tempo_upper_limit, \
                self.valence_lower_limit, \
                self.valence_upper_limit, \
                self._popularity, \
                self._blacklisted = result

    @property
    def popularity(self) -> int:
        if not hasattr(self, '_popularity'):
            self._popularity = max_popularity

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        self.popularity -= skipping_step
        my_app_database.update_value(
            table_name='genres',
            item_id=self.genre_name,
            table_column='popularity',
            new_value=self._popularity
        )

    @property
    def blacklisted(self) -> int:
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        self._blacklisted = new_value
        my_app_database.update_value(
            table_name='genres',
            item_id=self.genre_name,
            table_column='blacklisted',
            new_value=self._blacklisted
        )


class TrackAnalysis:
    def __init__(self, spotify_track_id: str):
        spotify_uri = 'spotify:track:' + spotify_track_id
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify  ID")

        cursor = my_app_database.database.execute('SELECT * from track_analysis WHERE track_id = ?', (spotify_track_id,))
        result = cursor.fetchone()

        # Fetch from Spotify API if not in the database
        if result is None:
            analyzed_track = Track(spotify_track_id)
            self.instance = sp.audio_features(tracks=[spotify_uri])

            self.track_id: str = analyzed_track.track_id
            self.track_name: str = analyzed_track.track_name
            self.track_acousticness: float = self.instance[0]["acousticness"]
            self.track_danceability: float = self.instance[0]["danceability"]
            self.track_duration_ms: int = self.instance[0]["duration_ms"]
            self.track_energy: float = self.instance[0]["energy"]
            self.track_instrumentalness: float = self.instance[0]["instrumentalness"]
            self.track_key: int = self.instance[0]["key"]
            self.track_liveness: float = self.instance[0]["liveness"]
            self.track_loudness: float = self.instance[0]["loudness"]
            self.track_mode: int = self.instance[0]["mode"]
            self.track_speechiness: float = self.instance[0]["speechiness"]
            self.track_tempo: float = self.instance[0]["tempo"]
            self.track_valence: float = self.instance[0]["valence"]

            my_app_database.add_track_to_track_analysis(self)

        # Unpack the database result into instance variables
        self.track_id, \
            self.track_name, \
            self.track_acousticness, \
            self.track_danceability, \
            self.track_duration_ms, \
            self.track_energy, \
            self.track_instrumentalness, \
            self.track_key, \
            self.track_liveness, \
            self.track_loudness, \
            self.track_mode, \
            self.track_speechiness, \
            self.track_tempo, \
            self.track_valence = result


class Devices:
    def __init__(self) -> None:
        self.instance = sp.devices()

        json_to_file(json_path, self.instance, True)

    def get_specific_device(self, device_name: str) -> ValueError | Any:
        for current_device in self.instance['devices']:

            # if re.search(current_device['name'],device_name, re.IGNORECASE) is not None:
            if current_device['name'] == device_name:
                return current_device

        valid_device_names = []
        for current_device in self.instance['devices']:
            valid_device_names.append(current_device['name'])

        return ValueError(f'The device named {device_name} was not found \n Valid Names are: {valid_device_names}')


class Device:
    def __init__(self, device_name: str, devices: Devices) -> None:
        self.instance = devices.get_specific_device(device_name)

        self.id: str = self.instance['id']
        self.is_active: bool = bool(self.instance['is_active'])
        self.is_private_session: bool = bool(self.instance['is_private_session'])
        self.is_restricted: bool = bool(self.instance['is_restricted'])
        self.name:str = self.instance['name']
        self.supports_volume: bool = bool(self.instance['supports_volume'])
        self.type:str = self.instance['type']
        self.volume_percent:int = int(self.instance['volume_percent'])


# ToDo: get to work if spotify has no instance
class Player:

    def __init__(self) -> None:
        self.instance: dict = {}
        self.current_collection: Playlist | Album
        self.current_album: Album
        self.current_artist: Artist
        self.current_track: Track
        self.device: Device
        self.is_playing: bool
        self.progress: int
        self.repeat_state: str
        self.shuffle_state: bool

        self.initialize_player()

    def get_instance(self):
        try:
            self.instance = sp.current_playback(market=market)
            return self.instance

        except SpotifyException:
            print("Spotify is currently not running")
            return None

    # JSON Files:
    def initialize_player(self):
        self.instance = self.get_instance()
        if self.instance is not None:
            if self.instance['context']['type'] == 'album':
                self.current_collection = Album(uri_to_id(self.instance['context']['uri']))
            elif self.instance['context']['type'] == 'playlist':
                self.current_collection = Playlist(uri_to_id(self.instance['context']['uri']))

            self.current_album = Album(self.instance['item']['album']['id'])
            self.current_artist = Artist(self.instance['item']['artists'][0]['id'])
            self.current_track = Track(self.instance['item']['id'])

            self.device = Device(self.instance['device']['name'], Devices())
            self.is_playing = bool(self.instance['is_playing'])
            self.progress = int(self.instance['progress_ms'])
            self.repeat_state = self.instance['repeat_state']  # no = 'off', on = 'context', once = 'track',
            self.shuffle_state = bool(self.instance['shuffle_state'])

        self.skip_blacklisted_items()

    def change_playing_state(self):
        # noinspection PyBroadException
        try:
            sp.pause_playback(self.device.id)
        except:
            # if it is not supposed to work, prohibit it xD
            sp.start_playback(self.device.id)

    def set_progress(self, time_in_ms: int):
        sp.seek_track(time_in_ms, self.device.id)

    def change_repeat_state(self, new_state: Literal['context', 'track', 'off']):
        if new_state == "context":
            sp.repeat('context', self.device.id)
        elif new_state == "track":
            sp.repeat('track', self.device.id)
        elif new_state == "off":
            sp.repeat('off', self.device.id)

    def next_track(self):
        sp.next_track(self.device.id)

    def prev_track(self):
        sp.previous_track(self.device.id)

    def change_shuffle_state(self):
        self.shuffle_state = not self.shuffle_state
        sp.shuffle(self.shuffle_state, self.device.id)

    def set_volume(self, new_volume: int):
        if not (0 <= new_volume <= 100):
            raise ValueError("Volume must be in the range from 0 to 100.")

        sp.volume(new_volume, self.device.id)

    def skip_blacklisted_items(self):
        album_cursor = my_app_database.database.execute('SELECT blacklisted from albums WHERE album_id = ?', (self.current_album.album_id,))
        artist_cursor = my_app_database.database.execute('SELECT blacklisted from artists WHERE artist_id = ?', (self.current_artist.artist_id,))
        track_cursor = my_app_database.database.execute('SELECT blacklisted from tracks WHERE track_id = ?', (self.current_track.track_id,))

        album_is_blacklisted = album_cursor.fetchone()
        artist_is_blacklisted = artist_cursor.fetchone()
        track_is_blacklisted = track_cursor.fetchone()

        if album_is_blacklisted == 1 or artist_is_blacklisted == 1 or track_is_blacklisted == 1:
            self.next_track()


if __name__ == '__main__':
    # Tests:
    # album__id = "4Gfnly5CzMJQqkUFfoHaP3"  # Meteora
    # _album = Album(album__id)
    # -> works

    # artist__id = "6XyY86QOPPrYVGvF9ch6wz"  # Linkin Park
    # _artist = Artist(artist__id)
    # -> works

    # track__id = "2nLtzopw4rPReszdYBJU6h"  # Numb
    # _track = Track(track__id)
    # -> works

    playlist__id = "6bRkO7PLCXgmV4EJH52iU4"  # my Playlist
    _playlist = Playlist(playlist__id)

    # user__id = "simonluca1"  # me
    # _user = User(user__id)
    # -> works

from secondary_methods import *
from spotify_access import spotify_client
from database_access import MyAppDatabase


sp = spotify_client()
market = 'DE'
my_app_database: MyAppDatabase = MyAppDatabase('../Databases/main_database.db')


class Album:
    def __init__(self, spotify_album_id: SpotifyID):
        spotify_uri = SpotifyURI('spotify:album:' + spotify_album_id.spotify_id)
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify Album ID")

        cursor = my_app_database.database.execute('SELECT * from albums WHERE album_id = ?', (spotify_album_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            self.instance = sp.album(album_id=spotify_album_id, market=market)

            self.album_id = self.instance['id']
            self.album_name = self.instance['name']
            self.album_url = self.instance['external_urls']['spotify']

            if 'url' not in self.instance['images'][0]:
                self.album_image = file_image_bytes(no_image_path)
            else:
                self.album_image = spotify_image_bytes(self.instance['images'][0]['url'])

            self.track_count = self.instance['total_tracks']
            self.popularity = max_popularity
            self.blacklisted = False

            my_app_database.add_album_to_albums(self)
            # ToDo: append album_id to artist.album_ids

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
                self.popularity, \
                self.blacklisted = result

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
            for genre in self.instance['genres']:
                genres.append(genre)
            self._genre_names = genres
        return self._genre_names

    @property
    def artist_ids(self) -> list[SpotifyID]:
        if not hasattr(self, '_artist_ids'):
            artists = []
            for artist in self.instance['artists']:
                artists.append(artist['id'])
            self._artist_ids = artists
        return self._artist_ids

    @property
    def track_ids(self) -> list[SpotifyID]:
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


class Artist:
    def __init__(self, spotify_artist_id: SpotifyID):
        spotify_uri = SpotifyURI('spotify:artist:' + spotify_artist_id.spotify_id)
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify Artist ID")

        cursor = my_app_database.database.execute('SELECT * from artists WHERE artist_id = ?', (spotify_artist_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            self.instance = sp.artist(artist_id=spotify_artist_id)
            self.artist_id = self.instance['id']
            self.artist_name = self.instance['name']
            self.artist_url = self.instance['external_urls']['spotify']

            if 'url' not in self.instance['images'][0]:
                self.instance_image = no_image_path
            else:
                self.album_image = self.instance['images'][0]['url']

            self.follower = self.instance['followers']['total']
            self.album_ids: List[SpotifyID] = []
            self.playlist_ids: List[SpotifyID] = []
            self.popularity = max_popularity
            self.blacklisted = False

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
                self.popularity, \
                self.blacklisted = result

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
    def top_tracks_ids(self) -> list[SpotifyID]:
        if not hasattr(self, '_top_tracks_ids'):
            top_tracks = sp.artist_top_tracks(self.artist_id, country="DE")
            top_track_list = []
            for top_track in top_tracks['tracks']:
                top_track_list.append(top_track['id'])

            self._top_tracks_ids = top_track_list

        return self._top_tracks_ids


class Playlist:
    def __init__(self, spotify_playlist_id: SpotifyID):
        spotify_uri = SpotifyURI('spotify:playlist:' + spotify_playlist_id.spotify_id)
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify Playlist ID")

        cursor = my_app_database.database.execute('SELECT * from playlists WHERE playlist_id = ?', (spotify_playlist_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            self.instance = sp.album(album_id=spotify_playlist_id, market=market)
            self.playlist_id = self.instance['id']
            self.playlist_name = self.instance['name']
            self.playlist_url = self.instance['external_urls']['spotify']

            if 'url' not in self.instance['images'][0]:
                self.instance_image = no_image_path
            else:
                self.album_image = self.instance['images'][0]['url']

            self.track_count = self.instance['tracks']['total']
            self.owner_id = self.instance['owner']['id']
            self.popularity = max_popularity
            self.blacklisted = False

            my_app_database.add_playlist_to_playlists(self)
            # ToDo: append playlist_id to artist.playlist_ids

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
                self.popularity, \
                self.blacklisted = result

            # convert List Strings back to list
            self._genre_names = list_from_id_string(self._genre_names)
            self._track_ids = list_from_id_string(self._track_ids)

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
    def track_ids(self) -> list[SpotifyID]:
        if not hasattr(self, '_track_ids'):
            tracks = []
            for current_track in self.instance['tracks']['items']:
                current_track_id = current_track['id']
                tracks.append(current_track_id)
                Track(current_track_id)

                # add playlist_id to tracks
                # ToDo: append playlist_id to track.playlist_ids
                my_app_database.cursor.execute('SELECT playlist_ids from tracks WHERE track_id = ?', (current_track_id,))
                used_in_playlists = my_app_database.cursor.fetchone()
                if self.playlist_id not in used_in_playlists:
                    my_app_database.update_value(
                        table_name='tracks',
                        item_id=current_track_id,
                        attribute='playlist_ids',
                        new_value=self.playlist_id
                    )
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


class Track:
    def __init__(self, spotify_track_id: SpotifyID):
        spotify_uri = SpotifyURI('spotify:track:' + spotify_track_id.spotify_id)
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify Track ID")

        cursor = my_app_database.database.execute('SELECT * from tracks WHERE track_id = ?', (spotify_track_id.spotify_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            self.instance = sp.track(track_id=spotify_track_id.spotify_id, market=market)
            self.track_id = self.instance['id']
            self.track_name = self.instance['name']
            self.track_url = self.instance['external_urls']['spotify']

            if 'images' not in self.instance:
                self.track_image = self.instance['album']['images'][0]['url']
            else:
                self.track_image = no_image_path

            self.track_duration = self.instance['duration_ms']
            self.popularity = max_popularity
            self.blacklisted = False

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
                self._playlist_ids, \
                self.popularity, \
                self.blacklisted = result

            # convert List Strings back to list
            self._genre_names = list_from_id_string(self._genre_names)
            self._artist_ids = list_from_id_string(self._artist_ids)
            self._album_ids = list_from_id_string(self._album_ids)
            self._playlist_ids = list_from_id_string(self._playlist_ids)

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
    def artist_ids(self) -> list[SpotifyID]:
        if not hasattr(self, '_artist_ids'):
            artists = []
            for artist in self.instance['artists']:
                artists.append(artist['id'])
            self._artist_ids = artists
        return self._artist_ids

    @property
    def album_ids(self) -> list[SpotifyID]:
        if not hasattr(self, '_album_ids'):
            albums = []

            # ToDo: implement

            self._album_ids = albums
        return self._album_ids

    @property
    def playlist_ids(self) -> list[SpotifyID]:
        if not hasattr(self, '_playlist_ids'):
            playlists = []

            # ToDo: implement

            self._playlist_ids = playlists
        return self._playlist_ids


class User:
    def __init__(self, spotify_user_id: SpotifyID) -> None:
        spotify_uri = SpotifyURI('spotify:user:' + spotify_user_id.spotify_id)
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify  ID")

        cursor = my_app_database.database.execute('SELECT * from track_analysis WHERE track_id = ?', (spotify_user_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            self.instance = sp.user(user=spotify_user_id)
            self.user_id = self.instance['id']
            self.user_name = self.instance['display_name']
            self.user_url = self.instance['external_urls']['spotify']

            if 'url' not in self.instance['images'][0]:
                self.instance_image = no_image_path
            else:
                self.album_image = self.instance['images'][0]['url']

            self.follower = self.instance['followers']
            self.popularity = max_popularity
            self.blacklisted = False

            my_app_database.add_user_to_users(self)

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
            self.popularity, \
            self.blacklisted = result

        # convert List Strings back to list
        self._playlist_ids = list_from_id_string(self._playlist_ids)
        self._top_tracks_ids = list_from_id_string(self._top_tracks_ids)
        self._top_artists_ids = list_from_id_string(self._top_artists_ids)
        self._top_genre_names = list_from_id_string(self._top_genre_names)

    @property
    def playlist_ids(self) -> list[SpotifyID]:
        if not hasattr(self, '_playlist_ids'):
            playlists = []
            for playlist in self.instance['items']:
                playlists.append(playlist['id'])
            self._playlist_ids = playlists
        return self._playlist_ids

    @property
    def top_tracks_ids(self) -> list[SpotifyID]:
        if not hasattr(self, '_top_tracks_ids'):
            top_tracks = []
            tracks_json = sp.current_user_top_tracks(limit=10)
            for current_track in tracks_json['items']:
                top_tracks.append(current_track['id'])
            self._top_tracks_ids = top_tracks
        return self._top_tracks_ids

    @property
    def top_artists_ids(self) -> list[SpotifyID]:
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

        # ToDo: implement

        return top_genres


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


class TrackAnalysis:
    def __init__(self, spotify_track_id: SpotifyID):
        spotify_uri = SpotifyURI('spotify:track:' + spotify_track_id.spotify_id)
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception("Invalid Spotify  ID")

        cursor = my_app_database.database.execute('SELECT * from track_analysis WHERE track_id = ?', (spotify_track_id,))
        result = cursor.fetchone()

        if result is None:
            # Fetch from Spotify API if not in the database
            Track(spotify_track_id)
            cursor = my_app_database.database.execute('SELECT * from track_analysis WHERE track_id = ?', (spotify_track_id,))
            result = cursor.fetchone()

            my_app_database.add_track_to_track_analysis(self)

        # Unpack the database result into instance variables
        self.track_id, self.track_name, self.track_acousticness, self.track_danceability, self.track_duration_ms, \
            self.track_energy, self.track_instrumentalness, self.track_key, self.track_liveness, self.track_loudness, \
            self.track_mode, self.track_speechiness, self.track_tempo, self.track_valence = result


# ToDo: Rewrite Devices, Device and Player to new functionalities
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

        self.id = self.instance['id']
        self.is_active = bool(self.instance['is_active'])
        self.is_private_session = bool(self.instance['is_private_session'])
        self.is_restricted = bool(self.instance['is_restricted'])
        self.name = self.instance['name']
        self.supports_volume = bool(self.instance['supports_volume'])
        self.type = self.instance['type']
        self.volume_percent = int(self.instance['volume_percent'])


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
    pass

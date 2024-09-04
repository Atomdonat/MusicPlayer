from spotipy import Spotify
from secondary_methods import *
from spotify_access import spotify_client
from database_access import MyAppDatabase


sp = spotify_client()
market = 'DE'
my_app_database = MyAppDatabase('/home/simon/git_repos/MusicPlayer/Databases/main_database.db')


class ItemIdQueues:
    def __init__(self):
        self.album_id_queue: list[str] = []
        self.artist_id_queue: list[str] = []
        self.playlist_id_queue: list[str] = []
        self.track_id_queue: list[str] = []
        self.user_id_queue: list[str] = []

    def get_queue_by_type(self, queue_type: Literal['albums', 'artists', 'tracks', 'playlists', 'users']):
        class_queues = {
            'albums': self.album_id_queue,
            'artists': self.artist_id_queue,
            'tracks': self.track_id_queue,
            'playlists': self.playlist_id_queue,
            'users': self.user_id_queue
        }
        return class_queues[queue_type]

    def add_items_to_db(self, queue_type: Literal['albums', 'artists', 'tracks', 'playlists', 'users']):
        dict_classes = {
            'albums': Album,
            'artists': Artist,
            'tracks': Track,
            'playlists': Playlist,
            'users': User
        }

        current_queue = self.get_queue_by_type(queue_type)

        while len(current_queue) > 0:
            try:
                if not my_app_database.fetch_item(queue_type, current_queue[0]):
                    dict_classes[queue_type](current_queue[0])
            except Exception as e:
                print(e)
            finally:
                print(f"added {queue_type}:{current_queue[0]} to db ({len(current_queue)} items left)")
                current_queue.pop(0)

    def add_items_to_db_and_dequeue(self):
        while any([
            len(self.album_id_queue) > 0,
            len(self.artist_id_queue) > 0,
            len(self.playlist_id_queue) > 0,
            len(self.track_id_queue) > 0,
            len(self.user_id_queue) > 0
        ]):
            i: Literal['albums', 'artists', 'tracks', 'playlists', 'users']
            for i in ['albums', 'artists', 'tracks', 'playlists', 'users']:
                if len(self.get_queue_by_type(i)) > 0:
                    self.add_items_to_db(i)


item_queues = ItemIdQueues()


class Album:
    def __init__(self, spotify_album_id: str):
        spotify_uri = 'spotify:album:' + spotify_album_id
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception(f"Invalid Spotify Album ID for: {spotify_album_id}")

        result = my_app_database.fetch_item('albums', spotify_album_id)

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

            # TODO: implement

            self._genre_names = genres
        return self._genre_names

    @property
    def artist_ids(self) -> list[str]:
        if not hasattr(self, '_artist_ids'):
            artists = []
            for artist in self.instance['artists']:
                current_artist_id = artist['id']
                artists.append(current_artist_id)

                # Check if Artist in DB or Queue, add if in neither
                my_app_database.update_item_ids_list(
                    current_id=current_artist_id,
                    match_id=self.album_id,
                    table_name='artists',
                    table_column='album_ids',
                    item_id_queue=item_queues.artist_id_queue
                )

            self._artist_ids = artists
        return self._artist_ids

    @property
    def track_ids(self) -> list[str]:
        if not hasattr(self, '_track_ids'):
            tracks = []
            for current_track in self.instance['tracks']['items']:
                current_track_id = current_track['id']

                # Check if Track in DB or Queue, add if in neither
                my_app_database.update_item_ids_list(
                    current_id=current_track_id,
                    match_id=self.album_id,
                    table_name='tracks',
                    table_column='album_ids',
                    item_id_queue=item_queues.track_id_queue
                )

                tracks.append(current_track_id)
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
        self.popularity += skipping_step

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
            raise Exception(f"Invalid Spotify Artist ID for: {spotify_artist_id}")

        result = my_app_database.fetch_item('artists', spotify_artist_id)

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

            self.follower: int = self.instance['followers']['total']
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
                current_track_id = top_track['id']

                # Check if Track in DB or Queue, add if in neither
                my_app_database.update_item_ids_list(
                    current_id=current_track_id,
                    match_id=self.artist_id,
                    table_name='tracks',
                    table_column='artist_ids',
                    item_id_queue=item_queues.track_id_queue
                )

                top_track_list.append(current_track_id)

            self._top_tracks_ids = top_track_list

        return self._top_tracks_ids

    @property
    def popularity(self) -> int:
        if not hasattr(self, '_popularity'):
            self._popularity = max_popularity

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        self.popularity += skipping_step

    @property
    def blacklisted(self) -> int:
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        self._blacklisted = new_value


class Playlist:
    # Note: Database partly insertion (--Fixed--)
    #     1. Database latency? issue, too many executions too fast (would explain why only a third was inserted) [l. 272: my_app_database.add_playlist_to_playlists(self)]
    #     2. sp.playlist() only returns limited tracks in items [l. 255: self.instance = sp.playlist(playlist_id=spotify_playlist_id, market=market)] <- API limits requests to 100 items
    #     3. checking Spotify ID ... the API limit (Should raise error -> unlikely) [ll. 313, 400: if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri)]
    # Fixme: still causes some problems with limits

    def __init__(self, spotify_playlist_id: str):
        spotify_uri = 'spotify:playlist:' + spotify_playlist_id
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception(f"Invalid Spotify Playlist ID for Playlist ID: {spotify_playlist_id}")

        result = my_app_database.fetch_item('playlists', spotify_playlist_id)

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

            # Check if User in DB or Queue, add if in neither
            if self.owner_id not in item_queues.user_id_queue:
                item_queues.user_id_queue.append(self.owner_id)

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

            # TODO: implement

            self._genre_names = genres
        return self._genre_names

    @property
    def track_ids(self) -> list[str]:
        if not hasattr(self, '_track_ids'):
            def iterate_tracks(limit: int = 100, offset: int = 0) -> None:
                playlist_items = sp.playlist_items(playlist_id=self.playlist_id, limit=limit, offset=offset, market=market)

                for current_track in playlist_items['items']:
                    current_track_id = current_track['track']['id']
                    tracks.append(current_track_id)

                    # Check if Track in DB or Queue, add if in neither
                    my_app_database.update_item_ids_list(
                        current_id=current_track_id,
                        match_id=self.playlist_id,
                        table_name='tracks',
                        table_column='playlist_ids',
                        item_id_queue=item_queues.track_id_queue
                    )

            tracks = []

            # separate request needed because Spotify API requests are limited to 100 items
            # e.g.: self.track_count = 1743
            request_iterations = self.track_count // 100  # e.g.: 17 iterations à 100 items
            last_iteration_limit = self.track_count % 100  # eg.: last 43 items

            for i in range(request_iterations):
                iterate_tracks(100, i*100)  # e.g.: tracks 1-1700

            if last_iteration_limit > 0:
                iterate_tracks(last_iteration_limit, len(tracks))  # e.g.: tracks 1701-1743

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
        self.popularity += skipping_step

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
            raise Exception(f"Invalid Spotify Track ID for: {spotify_track_id}")

        result = my_app_database.fetch_item('tracks', spotify_track_id)

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

            # TODO: implement

            self._genre_names = genres
        return self._genre_names

    @property
    def artist_ids(self) -> list[str]:
        if not hasattr(self, '_artist_ids'):
            artists = []
            for artist in self.instance['artists']:
                current_artist_id = artist['id']

                # Check if Track in DB or Queue, add if in neither
                my_app_database.update_item_ids_list(
                    current_id=current_artist_id,
                    match_id=self.track_id,
                    table_name='tracks',
                    table_column='artist_ids',
                    item_id_queue=item_queues.artist_id_queue
                )

                artists.append(current_artist_id)
            self._artist_ids = artists
        return self._artist_ids

    @property
    def album_ids(self) -> list[str]:
        if not hasattr(self, '_album_ids'):
            self._album_ids = [self.instance['album']['id']]

            # Check if Track in DB or Queue, add if in neither
            my_app_database.update_item_ids_list(
                current_id=self._album_ids[0],
                match_id=self.track_id,
                table_name='tracks',
                table_column='album_ids',
                item_id_queue=item_queues.album_id_queue
            )

        return self._album_ids

    @property
    def popularity(self) -> int:
        if not hasattr(self, '_popularity'):
            self._popularity = max_popularity

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        self.popularity += skipping_step

    @property
    def blacklisted(self) -> int:
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        self._blacklisted = new_value


# Note: (--Fixed--)
#   User creation somehow still creates IR Loop
class User:
    def __init__(self, spotify_user_id: str) -> None:
        spotify_uri = 'spotify:user:' + spotify_user_id
        if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
            raise Exception(f"Invalid Spotify User ID for: {spotify_user_id}")

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
                current_playlist_id = playlist['id']

                fetched_item_ids = my_app_database.fetch_item(
                    table_name='playlists',
                    item_id=current_playlist_id
                )

                if fetched_item_ids is None:
                    if current_playlist_id not in item_queues.playlist_id_queue:
                        item_queues.playlist_id_queue.append(current_playlist_id)
                        playlists.append(current_playlist_id)

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

        # TODO: figure out what to do here

        return top_genres

    @property
    def popularity(self) -> int:
        if not hasattr(self, '_popularity'):
            self._popularity = max_popularity

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        self.popularity += skipping_step

    @property
    def blacklisted(self) -> int:
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        self._blacklisted = new_value


class Genre:
    # TODO: figure out what to do here
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
        self.popularity += skipping_step
        my_app_database.update_item(
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
        my_app_database.update_item(
            table_name='genres',
            item_id=self.genre_name,
            table_column='blacklisted',
            new_value=self._blacklisted
        )


class TrackAnalysis:
    def __init__(self, spotify_track_id: str):
        # Note: not needed because (for now) only tracks with valid Sporify ID will be inserted to the db
        #   spotify_uri = 'spotify:track:' + spotify_track_id
        #   if not valid_spotify_uri(spotify_connection=sp, spotify_uri=spotify_uri):
        #       raise Exception(f"Invalid Spotify Track ID for: {spotify_track_id}")

        result = my_app_database.fetch_item('track_analysis', spotify_track_id)

        # Fetch from Spotify API if not in the database
        if result is None:
            analyzed_track = Track(spotify_track_id)
            self.instance = sp.audio_features(tracks=[spotify_track_id])

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


class Device:
    def __init__(self, device_id: str) -> None:
        result = my_app_database.fetch_item('devices', device_id)

        # Create if not in the database
        if result is None:
            self.instance = sp.devices()
            if not self.get_specific_device(device_id):
                raise Exception("Invalid Device ID")

            self.device_id: str = self.instance['id']
            self.device_name: str = self.instance['name']
            self.device_type: str = self.instance['type']
            self.is_active: bool = bool(self.instance['is_active'])
            self.is_private_session: bool = bool(self.instance['is_private_session'])
            self.is_restricted: bool = bool(self.instance['is_restricted'])
            self.supports_volume: bool = bool(self.instance['supports_volume'])
            self.volume_percent: int = int(self.instance['volume_percent'])

        else:
            self.device_id, \
                self.device_name, \
                self.device_type, \
                self.is_active, \
                self.is_private_session, \
                self.is_restricted, \
                self.supports_volume, \
                self.volume_percent = result

    def get_specific_device(self, device_id: str) -> ValueError | Any:
        for current_device in self.instance['devices']:

            if current_device['id'] == device_id:
                return current_device

        valid_device_ids = []
        for current_device in self.instance['devices']:
            valid_device_ids.append(current_device['id'])

        return ValueError(f'The device named {device_id} was not found \n Valid Names are: {valid_device_ids}')


class Player:

    def __init__(self) -> None:
        self.instance = sp.current_playback(market=market)
        if self.instance:
            if self.instance['context']['type'] == 'album':
                self.current_collection = Album(uri_to_id(self.instance['context']['uri']))
            elif self.instance['context']['type'] == 'playlist':
                self.current_collection = Playlist(uri_to_id(self.instance['context']['uri']))

            self.current_album = Album(self.instance['item']['album']['id'])
            self.current_artist = Artist(self.instance['item']['artists'][0]['id'])
            self.current_track = Track(self.instance['item']['id'])

            self.device = Device(self.instance['device']['name'])
            self.is_playing = bool(self.instance['is_playing'])
            self.progress = int(self.instance['progress_ms'])
            self.repeat_state = self.instance['repeat_state']  # no = 'off', on = 'context', once = 'track',
            self.shuffle_state = bool(self.instance['shuffle_state'])

        else:
            self.current_collection = Playlist("0000000000000000000000")  # Dummy
            self.current_album = Album("0000000000000000000000")  # Dummy
            self.current_artist = Artist("0000000000000000000000")  # Dummy
            self.current_track = Track("0000000000000000000000")  # Dummy
            self.device = Device("0000000000000000000000")  # Dummy
            self.is_playing = False
            self.repeat_state = "Null"
            self.shuffle_state = "Null"

        self.dummy_player = (self.device.device_id == "0000000000000000000000")

    # JSON Files:
    def initialize_player(self):
        try:
            self.instance = sp.current_playback(market=market)
        except SpotifyException as e:
            print(f'\x1b[31mNo Spotify instance found:\n{e}\n\nPlease start Spotify and retry')
            sys.exit(1)

        if self.instance:
            if self.instance['context']['type'] == 'album':
                self.current_collection = Album(uri_to_id(self.instance['context']['uri']))
            elif self.instance['context']['type'] == 'playlist':
                self.current_collection = Playlist(uri_to_id(self.instance['context']['uri']))

            self.current_album = Album(self.instance['item']['album']['id'])
            self.current_artist = Artist(self.instance['item']['artists'][0]['id'])
            self.current_track = Track(self.instance['item']['id'])

            self.device = Device(self.instance['device']['name'])
            self.is_playing = bool(self.instance['is_playing'])
            self.repeat_state = self.instance['repeat_state']  # no = 'off', on = 'context', once = 'track',
            self.shuffle_state = bool(self.instance['shuffle_state'])

        self.dummy_player = (self.device.device_id == "0000000000000000000000")
        self.skip_blacklisted_items()

    def change_playing_state(self):
        if not self.dummy_player:
            # HACK: abusing error to know if Spotify is playing
            try:
                sp.pause_playback(self.device.device_id)
            except:
                # if it is not supposed to work, why does it? xD
                sp.start_playback(self.device.device_id)

    @property
    def progress(self) -> int:
        if not self.dummy_player:
            playback_data = sp.current_user_playing_track()
            if playback_data:
                return playback_data["progress_ms"]
        else:
            return -1

    @progress.setter
    def progress(self, time_in_ms: int):
        if not self.dummy_player:
            sp.seek_track(time_in_ms, self.device.device_id)
            self.progress = time_in_ms
        else:
            self.progress = -1

    def change_repeat_state(self, new_state: Literal['context', 'track', 'off']):
        if not self.dummy_player:
            if new_state == "context":
                sp.repeat('context', self.device.device_id)
            elif new_state == "track":
                sp.repeat('track', self.device.device_id)
            elif new_state == "off":
                sp.repeat('off', self.device.device_id)

    def next_track(self):
        if not self.dummy_player:
            sp.next_track(self.device.device_id)

    def prev_track(self):
        if not self.dummy_player:
            sp.previous_track(self.device.device_id)

    def change_shuffle_state(self):
        if not self.dummy_player:
            self.shuffle_state = not self.shuffle_state
            sp.shuffle(self.shuffle_state, self.device.device_id)

    def set_volume(self, new_volume: int):
        if not (0 <= new_volume <= 100):
            raise ValueError("Volume must be in the range from 0 to 100.")
        if not self.dummy_player:
            sp.volume(new_volume, self.device.device_id)

    def skip_blacklisted_items(self):
        if self.dummy_player:
            return

        album_is_blacklisted = my_app_database.fetch_item('albums', self.current_album.album_id)
        if isinstance(self.current_collection, Album):
            collection_is_blacklisted = my_app_database.fetch_item('albums', self.current_collection.album_id)
        elif isinstance(self.current_collection, Playlist):
            collection_is_blacklisted = my_app_database.fetch_item('playlists', self.current_collection.playlist_id)
        else:
            print("How did we get here")
            return

        artist_is_blacklisted = my_app_database.fetch_item('artists', self.current_artist.artist_id)
        track_is_blacklisted = my_app_database.fetch_item('tracks', self.current_track.track_id)

        if any([album_is_blacklisted, collection_is_blacklisted, artist_is_blacklisted, track_is_blacklisted]):
            self.next_track()


class Analysis:
    def __init__(self):
        pass

    # Fixme: not working
    @staticmethod
    def analyse_tracks_in_db():
        track_ids = my_app_database.fetch_column('tracks', 'track_id')
        if track_ids:
            print(track_ids[:20])
            # for track_id in track_ids:
            #     if track_id == "0000000000000000000000":
            #         continue
            #     TrackAnalysis(track_id)


if __name__ == '__main__':
    # _player = Player()
    # my_app_database.reset_database()

    # Album("4Gfnly5CzMJQqkUFfoHaP3")
    # Artist("6XyY86QOPPrYVGvF9ch6wz")
    # Track("60a0Rd6pjrkxjPbaKzXjfq")
    # Playlist("3ng02xAP0YashD9ZFOyYk7")
    # Playlist("7bbWOJLSohSS7yOOHzXCAN")
    # User("simonluca1")
    # print(
    #     ' new Albums:   ', item_queues.album_id_queue, '\n',
    #     'new Artists:  ', item_queues.artist_id_queue, '\n',
    #     'new Tracks:   ', item_queues.track_id_queue, '\n'
    #     'new Playlists:', item_queues.playlist_id_queue, '\n',
    #     'new Users:    ', item_queues.user_id_queue
    # )
    # item_queues.add_items_to_db_and_dequeue()
    # print(
    #     '\n',
    #     'new Albums:   ', item_queues.album_id_queue, '\n',
    #     'new Artists:  ', item_queues.artist_id_queue, '\n',
    #     'new Tracks:   ', item_queues.track_id_queue, '\n'
    #     'new Playlists:', item_queues.playlist_id_queue, '\n',
    #     'new Users:    ', item_queues.user_id_queue
    # )
    analysis = Analysis()
    analysis.analyse_tracks_in_db()

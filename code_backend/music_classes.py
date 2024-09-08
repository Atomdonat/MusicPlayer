import timeit

from spotipy import Spotify
from secondary_methods import *
from spotify_access import spotify_client
from database_access import MyAppDatabase
import analysis
import numpy as np


sp = spotify_client()
my_app_database = MyAppDatabase(main_database_path)
track_analysis = analysis.TrackAnalysis(track_analysis_tsv_file_path)


# Fixme: creating new instances not working right now
#   fix (usage ItemIdQueues.process_all_queues())

# Idea: Outsource everything API Request related to independent file
#   new_file: handling the requests and returning JSON Objects / Dictionaries
#   music_classes: each class just receives the Dict with the relevant key-value entries

class ItemIdQueues:
    def __init__(self):
        self.album_id_queue: list[str] = []
        self.artist_id_queue: list[str] = []
        self.playlist_id_queue: list[str] = []
        self.track_id_queue: list[str] = []
        self.user_id_queue: list[str] = []

    def _process_queue(self, item_type: Literal['album', 'artist', 'track', 'playlist', 'user'], queue: list[str], model_class) -> None:
        def process_album_artist_or_track(current_type):
            # Split the queue into chunks
            chunked_queue = split_list_into_chunks(queue)
            id_instance_queue: list[dict] = []

            # Request data for each chunk
            for chunk in chunked_queue:
                current_chunk_instances = request_up_to_50_items(
                    sp=sp,
                    item_type=current_type,
                    items=chunk
                )
                id_instance_queue = concat_iterables(id_instance_queue, current_chunk_instances)

            # Process the retrieved items
            while id_instance_queue:
                model_class(id_instance_queue[0])
                print(f"added {id_instance_queue[0]['uri']} to DB ({len(queue)} items left)")
                queue.remove(id_instance_queue[0]['id'])
                id_instance_queue.pop(0)

        def process_playlist_or_user(current_type):
            while len(queue) > 0:
                try:
                    model_class(queue[0])
                    print(f"added spotify:{current_type}:{queue[0]} to db ({len(queue)} items left)")
                    queue.pop(0)
                except Exception as e:
                    print(e)

        if item_type in ['album', 'artist', 'track']:
            return process_album_artist_or_track(item_type)
        elif item_type in ['playlist', 'user']:
            return process_playlist_or_user(item_type)

    def process_all_queues(self):
        # Continue until all queues are empty
        while any([self.album_id_queue, self.artist_id_queue, self.playlist_id_queue, self.track_id_queue, self.user_id_queue]):
            if self.album_id_queue:
                self._process_queue('album', self.album_id_queue, Album)
            if self.artist_id_queue:
                self._process_queue('artist', self.artist_id_queue, Artist)
            if self.playlist_id_queue:
                self._process_queue('playlist', self.playlist_id_queue, Playlist)
            if self.track_id_queue:
                self._process_queue('track', self.track_id_queue, Track)
            if self.user_id_queue:
                self._process_queue('user', self.user_id_queue, User)


item_queues = ItemIdQueues()


class Album:
    def __init__(self, spotify_album: str | dict):
        result = my_app_database.fetch_item('albums', spotify_album)

        if result is None:
            if type(spotify_album) is str:
                # Fetch from Spotify API if not in the database
                try:
                    self.instance = sp.album(album_id=spotify_album, market=market)
                except Exception as e:
                    print(f'\x1b[31mError with Spotify API request for Album {spotify_album}:\n{e}')
                    sys.exit(1)
            else:
                self.instance = spotify_album

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
    def __init__(self, spotify_artist: str | dict):
        result = my_app_database.fetch_item('artists', spotify_artist)

        if result is None:
            if type(spotify_artist) is str:
                # Fetch from Spotify API if not in the database
                try:
                    self.instance = sp.artist(artist_id=spotify_artist)
                except Exception as e:
                    print(f'\x1b[31mError with Spotify API request for Artist {spotify_artist}:\n{e}')
                    sys.exit(1)
            else:
                self.instance = spotify_artist

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
    def __init__(self, spotify_playlist: str | dict):
        result = my_app_database.fetch_item('playlists', spotify_playlist)

        if result is None:
            if type(spotify_playlist) is str:
                # Fetch from Spotify API if not in the database
                try:
                    self.instance = sp.playlist(playlist_id=spotify_playlist, market=market)
                except Exception as e:
                    print(f'\x1b[31mError with Spotify API request for Playlist{spotify_playlist}:\n{e}')
                    sys.exit(1)
            else:
                self.instance = spotify_playlist

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
                iterate_tracks(last_iteration_limit, self.track_count-last_iteration_limit)  # e.g.: tracks 1701-1743

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
    def __init__(self, spotify_track: str | dict):
        result = my_app_database.fetch_item('tracks', spotify_track)

        if result is None:
            if type(spotify_track) is str:
                # Fetch from Spotify API if not in the database
                try:
                    self.instance = sp.track(track_id=spotify_track, market=market)
                except Exception as e:
                    print(f'\x1b[31mError with Spotify API request for Track {spotify_track}:\n{e}')
                    sys.exit(1)
            else:
                self.instance = spotify_track

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


class User:
    def __init__(self, spotify_user: str | dict) -> None:
        result = my_app_database.fetch_item(
            table_name='users',
            item_id=spotify_user,
            table_column='user_id',
        )

        if result is None:
            if type(spotify_user) is str:
                # Fetch from Spotify API if not in the database
                try:
                    self.instance = sp.user(user=spotify_user)

                except Exception as e:
                    print(f'\x1b[31mError with Spotify API request for User {spotify_user}:\n{e}')
                    sys.exit(1)
            else:
                self.instance = spotify_user

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


# TODO: figure out what to do here
class Genre:
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

        result = my_app_database.fetch_item(
            table_name='genres',
            item_id=genre_name,
            table_column=genre_name
        )

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
        result = track_analysis.get_track_analysis(spotify_track_id)
        self.track_id = spotify_track_id

        # Fetch from Spotify API if not in the database
        if result is None:
            analyzed_track = Track(spotify_track_id)
            self.instance = sp.audio_features(tracks=[spotify_track_id])

            self.track_id: str = analyzed_track.track_id
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

            track_analysis.append_new_track_to_data(
                track_id=self.track_id,
                track_acousticness=self.track_acousticness,
                track_danceability=self.track_danceability,
                track_duration_ms=self.track_duration_ms,
                track_energy=self.track_energy,
                track_instrumentalness=self.track_instrumentalness,
                track_key=self.track_key,
                track_liveness=self.track_liveness,
                track_loudness=self.track_loudness,
                track_mode=self.track_mode,
                track_speechiness=self.track_speechiness,
                track_tempo=self.track_tempo,
                track_valence=self.track_valence
            )

        else:
            self.track_id, \
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
                self.track_valence = track_analysis.get_track_analysis(spotify_track_id)

    def get_data_from_dataframe(self):
        self.track_id, \
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
            self.track_valence = track_analysis.get_track_analysis(self.track_id)


class Analysis:
    def __init__(self):
        self.track_analysis = analysis.TrackAnalysis(track_analysis_tsv_file_path)

    # Fixme: not working
    def analyse_tracks_in_db(self):
        track_ids = my_app_database.fetch_column('tracks', 'track_id')
        if track_ids:
            try:
                format_length = int(np.ceil(np.log10(len(track_ids))))
                for i, track_id in enumerate(track_ids):
                    if track_id == "0000000000000000000000":
                        continue
                    TrackAnalysis(track_id)
                    print("Track {}/{}: {}".format(str(i).zfill(format_length), len(track_ids), track_id))

            except Exception as e:
                print(e)
            finally:
                self.track_analysis.add_data_rows()


if __name__ == '__main__':
    # my_app_database.reset_database()

    try:
        # Album("4Gfnly5CzMJQqkUFfoHaP3")
        # Artist("6XyY86QOPPrYVGvF9ch6wz")
        Track("60a0Rd6pjrkxjPbaKzXjfq")
        # Playlist("3ng02xAP0YashD9ZFOyYk7")
        # Playlist("7bbWOJLSohSS7yOOHzXCAN")
        # User("simonluca1")

    except Exception as e:
        print(e)

    finally:
        item_queues.process_all_queues()

    # analysis = Analysis()
    # analysis.analyse_tracks_in_db()


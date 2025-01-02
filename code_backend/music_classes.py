import sys
import time
import timeit

from spotipy import Spotify
from secondary_methods import *
from spotify_access import *
from database_access import MyAppDatabase
import analysis
import numpy as np


sp = spotify_client()
my_app_database = MyAppDatabase(MAIN_DATABASE_PATH)
track_analysis = analysis.TrackAnalysis(TRACK_ANALYSIS_TSV_FILE_PATH)


class ItemIdQueues:
    """
    Todo: Docstring
    """
    def __init__(self):
        self.album_id_queue: list[str] = []
        self.artist_id_queue: list[str] = []
        self.playlist_id_queue: list[str] = []
        self.track_id_queue: list[str] = []
        self.track_analysis_id_queue: list[str] = []
        self.user_id_queue: list[str] = []

    def process_all_queues(self):
        """
        iterates through every queue and adds the items to the database if they dont exist
        """
        def _process_queue(item_type: Literal['album', 'artist', 'playlist', 'track', 'track_analysis', 'user'], queue: list[str], model_class) -> None:
            id_instance_queue = request_multiple_items_of_same_type(
                sp=sp,
                items=queue,
                item_type=item_type
            )
            queue.clear()

            while id_instance_queue:
                try:
                    model_class(id_instance_queue[0])
                    print(f"added {id_instance_queue[0]['uri']} to DB ({len(id_instance_queue)} items left)")
                    id_instance_queue.pop(0)

                except Exception as exc:
                    # with open("./errors.log", "a")as efile:
                        # efile.write(f"{exc}\nItem: {id_instance_queue[0]['id']}\nQueue: {queue}\nItemQueues:\n{self.__dict__}")
                    raise f"\n\x1b[31mError occured while adding {id_instance_queue[0]['uri']} to DB\x1b[30m\n\n{exc}"

            queue.clear()

        # Fixme:
        while any([self.album_id_queue, self.artist_id_queue, self.playlist_id_queue, self.track_id_queue, self.user_id_queue]):
            if self.album_id_queue:
                _process_queue('album', self.album_id_queue, Album)
            if self.artist_id_queue:
                _process_queue('artist', self.artist_id_queue, Artist)
            if self.track_id_queue:
                _process_queue('track', self.track_id_queue, Track)
            if self.track_analysis_id_queue:
                _process_queue('track_analysis', self.track_id_queue, Track)
            if self.playlist_id_queue:
                _process_queue('playlist', self.playlist_id_queue, Playlist)
            if self.user_id_queue:
                _process_queue('user', self.user_id_queue, User)


item_queues = ItemIdQueues()


class Album:
    """
    Todo: Docstring
    :param spotify_album: JSON response from Spotify API request (e.g. return value of sp.album)
    """
    def __init__(self, spotify_album: dict):
        result = my_app_database.fetch_item('albums', spotify_album['id'])

        if result is None:
            self.album_instance = spotify_album
            self.album_id: str = spotify_album['id']
            self.album_name: str = spotify_album['name']
            self.album_url: str = spotify_album['external_urls']['spotify']

            if 'url' not in spotify_album['images'][0]:
                self.album_image: str = file_image_bytes(NO_IMAGE_PATH)
            else:
                self.album_image: str = spotify_image_bytes(spotify_album['images'][0]['url'])

            self.track_count: int = spotify_album['total_tracks']

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

    @property
    def genre_names(self) -> list[str]:
        """
        :return: list of genre names
        """
        if not hasattr(self, '_genre_names'):
            genres = []

            # TODO: implement

            self._genre_names = genres
        return self._genre_names

    @property
    def artist_ids(self) -> list[str]:
        """
        :return: list of artist ids
        """
        if not hasattr(self, '_artist_ids'):
            artists = []
            for artist in self.album_instance['artists']:
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
        """
        :return: list of track ids
        """
        if not hasattr(self, '_track_ids'):
            tracks = []
            for current_track in self.album_instance['tracks']['items']:
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
        """
        :return: Total duration of the Album in milliseconds
        """
        if not hasattr(self, '_total_duration'):
            duration = 0
            for current_track in self.album_instance['tracks']['items']:
                duration += int(current_track['duration_ms'])
            self._total_duration = duration
        return self._total_duration

    @property
    def popularity(self) -> int:
        """
        returns the popularity value
        """
        if not hasattr(self, '_popularity'):
            self._popularity = MAX_POPULARITY

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        """
        Updates the Popularity Value
        :param skipping_step: how much to in-/decrease the Popularity Value
        :return: updates self.popularity
        """
        self.popularity += skipping_step

    @property
    def blacklisted(self) -> int:
        """
        Defines if a Album is currently blacklisted
        """
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        """
        Change the current blacklisted state of the Album
        :param new_value: 0 for not blacklisted, 1 for blacklisted
        :return: updates self.blacklisted
        """
        self._blacklisted = new_value


class Artist:
    """
    Todo: Docstring
    :param spotify_artist: JSON response from Spotify API request (e.g. return value of sp.artist)
    """
    def __init__(self, spotify_artist: dict):
        result = my_app_database.fetch_item('artists', spotify_artist['id'])

        if result is None:
            self.artist_instance = spotify_artist
            self.artist_id: str = spotify_artist['id']
            self.artist_name: str = spotify_artist['name']
            self.artist_url: str = spotify_artist['external_urls']['spotify']

            if 'url' not in spotify_artist['images'][0]:
                self.artist_image: str = file_image_bytes(NO_IMAGE_PATH)
            else:
                self.artist_image: str = spotify_image_bytes(spotify_artist['images'][0]['url'])

            self.follower: int = spotify_artist['followers']['total']
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

    @property
    def genre_names(self) -> list[str]:
        """
        :return: list of genre names
        """
        if not hasattr(self, '_genre_names'):
            genres = []
            for genre in self.artist_instance['genres']:
                genres.append(genre)
            self._genre_names = genres
        return self._genre_names

    @property
    def top_tracks_ids(self) -> list[str]:
        """
        :return: list of top track ids
        """
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
        """
        returns the popularity value
        """
        if not hasattr(self, '_popularity'):
            self._popularity = MAX_POPULARITY

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        """
        Updates the Popularity Value
        :param skipping_step: how much to in-/decrease the Popularity Value
        :return: updates self.popularity
        """
        self.popularity += skipping_step

    @property
    def blacklisted(self) -> int:
        """
        Defines if a Artist is currently blacklisted
        """
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        """
        Change the current blacklisted state of the Artist
        :param new_value: 0 for not blacklisted, 1 for blacklisted
        :return: updates self.blacklisted
        """
        self._blacklisted = new_value


# Fixme: somehow a Playlist request contains +2000 items -> 502 Error
class Playlist:
    """
    Todo: Docstring
    :param spotify_album: JSON response from Spotify API request (e.g. return value of sp.album)
    """
    def __init__(self, spotify_playlist: dict):
        result = my_app_database.fetch_item('playlists', spotify_playlist['id'])

        if result is None:
            self.playlist_instance = spotify_playlist
            self.playlist_id: str = spotify_playlist['id']
            self.playlist_name: str = spotify_playlist['name']
            self.playlist_url: str = spotify_playlist['external_urls']['spotify']

            if 'url' not in spotify_playlist['images'][0]:
                self.playlist_image: str = file_image_bytes(NO_IMAGE_PATH)
            else:
                self.playlist_image: str = spotify_image_bytes(spotify_playlist['images'][0]['url'])

            self.track_count: int = spotify_playlist['tracks']['total']
            self.owner_id: str = spotify_playlist['owner']['id']

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

    @property
    def genre_names(self) -> list[str]:
        """
        :return: list of genre names
        """
        if not hasattr(self, '_genre_names'):
            genres = []

            # TODO: implement

            self._genre_names = genres
        return self._genre_names

    @property
    def track_ids(self) -> list[str]:
        """
        Fetches the Track IDs that are currently in the Playlist
        :return: list of track ids
        """
        if not hasattr(self, '_track_ids'):
            def iterate_tracks(limit: int = 50, offset: int = 0) -> None:
                playlist_items = sp.playlist_items(playlist_id=self.playlist_id, limit=limit, offset=offset, market=MARKET)

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

            # separate request needed because Spotify API requests are limited to 50 items
            # e.g.: self.track_count = 1743
            request_iterations = self.track_count // 500  # e.g.: 34 iterations à 50 items
            last_iteration_limit = self.track_count % 50  # eg.: last 43 items

            for i in range(request_iterations):
                iterate_tracks(50, i*50)  # e.g.: tracks 1-1700

            if last_iteration_limit > 0:
                iterate_tracks(last_iteration_limit, self.track_count-last_iteration_limit)  # e.g.: tracks 1701-1743

            self._track_ids = tracks
        return self._track_ids

    @property
    def total_duration(self) -> int:
        """
        :return: Total duration of the Album in milliseconds
        """
        if not hasattr(self, '_total_duration'):
            duration = 0
            for current_track in self.playlist_instance['tracks']['items']:
                duration += int(current_track['track']['duration_ms'])
            self._total_duration = duration
        return self._total_duration

    @property
    def popularity(self) -> int:
        """
        returns the popularity value
        """
        if not hasattr(self, '_popularity'):
            self._popularity = MAX_POPULARITY

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        """
        Updates the Popularity Value
        :param skipping_step: how much to in-/decrease the Popularity Value
        :return: updates self.popularity
        """
        self.popularity += skipping_step

    @property
    def blacklisted(self) -> int:
        """
        Defines if a Playlist is currently blacklisted
        """
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        """
        Change the current blacklisted state of the Playlist
        :param new_value: 0 for not blacklisted, 1 for blacklisted
        :return: updates self.blacklisted
        """
        self._blacklisted = new_value


class Track:
    """
    Todo: Docstring
    :param spotify_album: JSON response from Spotify API request (e.g. return value of sp.album)
    """
    def __init__(self, spotify_track: dict):
        result = my_app_database.fetch_item('tracks', spotify_track['id'])

        if result is None:
            self.track_instance = spotify_track
            self.track_id: str = spotify_track['id']
            self.track_name: str = spotify_track['name']
            self.track_url: str = spotify_track['external_urls']['spotify']

            if 'images' not in spotify_track:
                self.track_image: str = spotify_image_bytes(spotify_track['album']['images'][0]['url'])
            else:
                self.track_image: str = file_image_bytes(NO_IMAGE_PATH)

            # Playlist ID gets added when the Playlist() is instantiated
            self.playlist_ids: list[str] = []

            self.track_duration: int = spotify_track['duration_ms']

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

    @property
    def genre_names(self) -> list[str]:
        """
        :return: list of genre names
        """
        if not hasattr(self, '_genre_names'):
            genres = []

            # TODO: implement

            self._genre_names = genres
        return self._genre_names

    @property
    def artist_ids(self) -> list[str]:
        """
        :return: list of artist ids
        """
        if not hasattr(self, '_artist_ids'):
            artists = []
            for artist in self.track_instance['artists']:
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
        """
        :return: list of album ids
        """
        if not hasattr(self, '_album_ids'):
            self._album_ids = [self.track_instance['album']['id']]

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
        """
        returns the popularity value
        """
        if not hasattr(self, '_popularity'):
            self._popularity = MAX_POPULARITY

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        """
        Updates the Popularity Value
        :param skipping_step: how much to in-/decrease the Popularity Value
        :return: updates self.popularity
        """
        self.popularity += skipping_step

    @property
    def blacklisted(self) -> int:
        """
        Defines if a Track is currently blacklisted
        """
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        """
        Change the current blacklisted state of the Track
        :param new_value: 0 for not blacklisted, 1 for blacklisted
        :return: updates self.blacklisted
        """

        self._blacklisted = new_value


class User:
    """
    Todo: Docstring
    :param spotify_album: JSON response from Spotify API request (e.g. return value of sp.album)
    """
    def __init__(self, spotify_user: dict) -> None:
        result = my_app_database.fetch_item(
            table_name='users',
            item_id=spotify_user['id'],
            table_column='user_id',
        )

        if result is None:
            self.user_instance = spotify_user
            self.user_id: str = spotify_user['id']
            self.user_name: str = spotify_user['display_name']
            self.user_url: str = spotify_user['external_urls']['spotify']

            if 'url' not in spotify_user['images'][0]:
                self.user_image: str = file_image_bytes(NO_IMAGE_PATH)
            else:
                self.user_image: str = spotify_image_bytes(spotify_user['images'][0]['url'])

            self.follower: int = spotify_user['followers']

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
        """
        :return: list of playlist ids
        """
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
        """
        :return: list of top track ids
        """
        if not hasattr(self, '_top_tracks_ids'):
            top_tracks = []
            tracks_json = sp.current_user_top_tracks(limit=10)
            for current_track in tracks_json['items']:
                top_tracks.append(current_track['id'])
            self._top_tracks_ids = top_tracks
        return self._top_tracks_ids

    @property
    def top_artists_ids(self) -> list[str]:
        """
        :return: list of top artist ids
        """
        if not hasattr(self, '_top_artists_ids'):
            top_artists = []
            tracks_json = sp.current_user_top_artists(limit=10)
            for current_track in tracks_json['items']:
                top_artists.append(current_track['id'])
            self._top_artists_ids = top_artists
        return self._top_artists_ids

    @property
    def top_genre_names(self) -> list[str]:
        """
        :return: list of top genre names
        """
        top_genres = []

        # TODO: figure out what to do here

        return top_genres

    @property
    def popularity(self) -> int:
        """
        returns the popularity value
        """
        if not hasattr(self, '_popularity'):
            self._popularity = MAX_POPULARITY

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        """
        Updates the Popularity Value
        :param skipping_step: how much to in-/decrease the Popularity Value
        :return: updates self.popularity
        """
        self.popularity += skipping_step

    @property
    def blacklisted(self) -> int:
        """
        Defines if a User is currently blacklisted
        """
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        """
        Change the current blacklisted state of the User
        :param new_value: 0 for not blacklisted, 1 for blacklisted
        :return: updates self.blacklisted
        """

        self._blacklisted = new_value


# TODO: figure out what to do here
class Genre:
    """
    Defines what a Genre is.
    """
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
        """
        returns the popularity value
        """
        if not hasattr(self, '_popularity'):
            self._popularity = MAX_POPULARITY

        return self._popularity

    @popularity.setter
    def popularity(self, skipping_step: int) -> None:
        """
        Updates the Popularity Value
        :param skipping_step: how much to in-/decrease the Popularity Value
        :return: updates self.popularity
        """
        self.popularity += skipping_step
        my_app_database.update_item(
            table_name='genres',
            item_id=self.genre_name,
            table_column='popularity',
            new_value=self._popularity
        )

    @property
    def blacklisted(self) -> int:
        """
        Defines if a Genre is currently blacklisted
        """
        if not hasattr(self, '_blacklisted'):
            self._blacklisted = 0

        return self._blacklisted

    @blacklisted.setter
    def blacklisted(self, new_value: 0 | 1) -> None:
        """
        Change the current blacklisted state of the Genre
        :param new_value: 0 for not blacklisted, 1 for blacklisted
        :return: updates self.blacklisted
        """
        self._blacklisted = new_value
        my_app_database.update_item(
            table_name='genres',
            item_id=self.genre_name,
            table_column='blacklisted',
            new_value=self._blacklisted
        )


class TrackAnalysis:
    """
    Todo: Docstring
    :param spotify_track_analysis:
    """
    def __init__(self, spotify_track_analysis: dict):
        self.track_id = spotify_track_analysis['id']
        result = track_analysis.get_track_analysis(self.track_id)

        if result is None:
            Track(spotify_track_analysis)

            self.track_acousticness: float = spotify_track_analysis["acousticness"]
            self.track_danceability: float = spotify_track_analysis["danceability"]
            self.track_duration_ms: int = spotify_track_analysis["duration_ms"]
            self.track_energy: float = spotify_track_analysis["energy"]
            self.track_instrumentalness: float = spotify_track_analysis["instrumentalness"]
            self.track_key: int = spotify_track_analysis["key"]
            self.track_liveness: float = spotify_track_analysis["liveness"]
            self.track_loudness: float = spotify_track_analysis["loudness"]
            self.track_mode: int = spotify_track_analysis["mode"]
            self.track_speechiness: float = spotify_track_analysis["speechiness"]
            self.track_tempo: float = spotify_track_analysis["tempo"]
            self.track_valence: float = spotify_track_analysis["valence"]

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
                self.track_valence = track_analysis.get_track_analysis(self.track_id)

    def get_data_from_dataframe(self):
        """
        Extract Data from the Dataframe and update instance attribute values
        """
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
    """
    Todo: Docstring
    """
    def __init__(self):
        self.track_analysis = analysis.TrackAnalysis(TRACK_ANALYSIS_TSV_FILE_PATH)

    # Fixme: not working
    def analyse_tracks_in_db(self):
        """
        Todo: Docstring
        """
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
    my_app_database.reset_database()

    try:
        # Track(request_one_item(
        #     sp=sp,
        #     item_type='track',
        #     spotify_id="60a0Rd6pjrkxjPbaKzXjfq"
        # ))
        # Album(request_one_item(
        #     sp=sp,
        #     item_type='album',
        #     spotify_id="4Gfnly5CzMJQqkUFfoHaP3"
        # ))
        # Artist(request_one_item(
        #     sp=sp,
        #     item_type='artist',
        #     spotify_id="6XyY86QOPPrYVGvF9ch6wz"
        # ))
        Playlist(request_one_item(
            sp=sp,
            item_type='playlist',
            spotify_id='5kuT9ddlqoiZjW7cgnDv2X'
        ))
        # User(request_one_item(
        #     sp=sp,
        #     item_type='user',
        #     spotify_id="simonluca1"
        # ))

    except Exception as e:
        print(e)

    finally:
        item_queues.process_all_queues()



    # analysis = Analysis()
    # analysis.analyse_tracks_in_db()


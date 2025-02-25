"""
File to develop and debug methods, class and more
"""
from code_backend.shared_config import *
from code_backend.secondary_methods import (
    uri_to_id, list_from_id_string, file_image_bytes,
    spotify_image_bytes, url_to_uri, exclude_from_dict, id_to_uri,
    check_token_expired, load_json, debug_json, print_debug,
    load_list_from_database, value_from_dict,
    check_spotify_uri, check_spotify_uris, check_spotify_id, check_spotify_ids,
    check_limits
)
import code_backend.spotify_web_api as spotify
from code_backend.database_access import APP_DATABASE
from code_backend.exceptions import (
    SpotifyApiException, SpotifyUriException, SpotifyIdException,
    InputException, CustomException
)


class _SpotifyObject:
    """"""

    def __init__(self):
        self.popularity: int = MAX_POPULARITY
        self.blacklisted: int = 0


    @property
    def genre_names(self) -> list[str]:
        """
        Not Implemented Yet

        :return: list of genre names
        """
        genres = []

        # TODO: implement genre_names

        return genres
    

class NewAlbum(_SpotifyObject):
    """"""

    def __init__(self, spotify_album: dict):
        """
        :param spotify_album: Dict containing Spotify Albums, in the form of {album_uri: album}
        :raises InputException: if input is invalid
        """

        if not isinstance(spotify_album, dict):
            raise InputException(item_value=spotify_album, valid_values="{album_uri: album}", valid_types=dict)

        super().__init__()

        self.album_json: dict = value_from_dict(spotify_album)
        self.album_id: str = self.album_json['id']
        self.album_name: str = self.album_json['name']
        self.album_uri: str = self.album_json['uri']
        self.album_url: str = self.album_json['external_urls']['spotify']

        if 'url' not in self.album_json['images'][0]:
            self.album_image: str = file_image_bytes(NO_IMAGE_PATH)
        else:
            self.album_image: str = spotify_image_bytes(self.album_json['images'][0]['url'])

        tracks, self.total_duration = spotify.get_album_tracks(self.album_id, get_duration=True)
        self.track_count: int = self.album_json['total_tracks']
        self.artist_ids: list[str] = [current_artist['id'] for current_artist in self.album_json['artists']]
        self.track_ids: list[str] = [uri_to_id(current_track) for current_track in tracks.keys()]

        APP_DATABASE.add_item_to_table(
            table_name='albums',
            album_id=self.album_id,
            album_name=self.album_name,
            album_uri=self.album_uri,
            album_url=self.album_url,
            album_image=self.album_image,
            genre_names=self.genre_names,
            total_duration=self.total_duration,
            track_count=self.track_count,
            artist_ids=self.artist_ids,
            track_ids=self.track_ids,
            popularity=self.popularity,
            blacklisted=self.blacklisted,
            album_json=self.album_json
        )


class NewArtist(_SpotifyObject):
    """"""

    def __init__(self, spotify_artist: dict):
        """

        :param spotify_artist: Dict containing Spotify Artists, in the form of {artist_uri: artist}
        :raises InputException: if input is invalid
        """
        if not isinstance(spotify_artist, dict):
            raise InputException(item_value=spotify_artist, valid_values='{artist_uri: artist}', valid_types=dict)

        super().__init__()

        self.artist_json: dict = value_from_dict(spotify_artist)
        self.artist_id: str = self.artist_json['id']
        self.artist_name: str = self.artist_json['name']
        self.artist_uri: str = self.artist_json['uri']
        self.artist_url: str = self.artist_json['external_urls']['spotify']

        if 'url' not in self.artist_json['images'][0]:
            self.artist_image: str = file_image_bytes(NO_IMAGE_PATH)
        else:
            self.artist_image: str = spotify_image_bytes(self.artist_json['images'][0]['url'])

        albums: dict = spotify.get_artists_albums(artist_id=self.artist_id)
        top_tracks: dict = spotify.get_artists_top_tracks(self.artist_id)

        self.follower: int = self.artist_json['followers']['total']
        self.album_ids: list[str] = [uri_to_id(current_album) for current_album in albums.keys()]
        # Todo: Playlist ID gets added when the Playlist() is instantiated
        self.playlist_ids: list[str] = []
        self.top_track_ids: list[str] = [uri_to_id(current_track) for current_track in top_tracks.keys()]

        APP_DATABASE.add_item_to_table(
            table_name='artists',
            artist_id=self.artist_id,
            artist_name=self.artist_name,
            artist_uri=self.artist_uri,
            artist_url=self.artist_url,
            artist_image=self.artist_image,
            genre_names=self.genre_names,
            follower=self.follower,
            album_ids=self.album_ids,
            playlist_ids=self.playlist_ids,
            top_track_ids=self.top_track_ids,
            popularity=self.popularity,
            blacklisted=self.blacklisted,
            artist_json=self.artist_json
        )


class NewPlaylist(_SpotifyObject):
    """"""

    def __init__(self, spotify_playlist: dict):
        """

        :param spotify_playlist: Dict containing Spotify Playlists, in the form of {playlist_uri: playlist}
        :raises InputException: if input is invalid
        """
        if not isinstance(spotify_playlist, dict):
            raise InputException(item_value=spotify_playlist, valid_values='{playlist_uri: playlist}', valid_types=dict)

        super().__init__()

        self.playlist_json: dict = value_from_dict(spotify_playlist)
        self.playlist_id: str = self.playlist_json['id']
        self.playlist_name: str = self.playlist_json['name']
        self.playlist_uri: str = self.playlist_json['uri']
        self.playlist_url: str = self.playlist_json['external_urls']['spotify']

        if 'url' not in self.playlist_json['images'][0]:
            self.playlist_image: str = file_image_bytes(NO_IMAGE_PATH)
        else:
            self.playlist_image: str = spotify_image_bytes(self.playlist_json['images'][0]['url'])

        playlist_items, self.total_duration = spotify.get_playlist_items(playlist_id=self.playlist_id, get_duration=True)
        self.track_count: int = self.playlist_json['tracks']['total']
        self.owner_id: str = self.playlist_json['owner']['id']
        self.track_ids: list[str] = [uri_to_id(current_track) for current_track in playlist_items.keys()]

        APP_DATABASE.add_item_to_table(
            table_name='playlists',
            playlist_id=self.playlist_id,
            playlist_name=self.playlist_name,
            playlist_uri=self.playlist_uri,
            playlist_url=self.playlist_url,
            playlist_image=self.playlist_image,
            genre_names=self.genre_names,
            total_duration=self.total_duration,
            track_count=self.track_count,
            owner_id=self.owner_id,
            track_ids=self.track_ids,
            popularity=self.popularity,
            blacklisted=self.blacklisted,
            playlist_json=self.playlist_json
        )


class NewTrack(_SpotifyObject):
    """"""

    def __init__(self, spotify_track: dict):
        """

        :param spotify_track: Dict containing Spotify Tracks, in the form of {track_uri: track}
        :raises InputException: if input is invalid
        """
        if not isinstance(spotify_track, dict):
            raise InputException(item_value=spotify_track, valid_values='{track_uri: track}', valid_types=dict)

        super().__init__()

        self.track_json: dict = value_from_dict(spotify_track)
        self.track_id: str = self.track_json['id']
        self.track_name: str = self.track_json['name']
        self.track_uri: str = self.track_json['uri']
        self.track_url: str = self.track_json['external_urls']['spotify']

        if 'images' not in self.track_json:
            self.track_image: str = spotify_image_bytes(self.track_json['album']['images'][0]['url'])
        else:
            self.track_image: str = file_image_bytes(NO_IMAGE_PATH)

        self.track_duration: int = self.track_json['duration_ms']
        self.album_id: str = self.track_json['album']['id']
        self.artist_ids: list[str] = [current_artist['id'] for current_artist in self.track_json['artists']]
        # Todo: Playlist ID gets added when the Playlist() is instantiated
        self.playlist_ids: list[str] = []

        APP_DATABASE.add_item_to_table(
            table_name='tracks',
            track_id=self.track_id,
            track_name=self.track_name,
            track_uri=self.track_uri,
            track_url=self.track_url,
            track_image=self.track_image,
            genre_names=self.genre_names,
            track_duration=self.track_duration,
            artist_ids=self.artist_ids,
            album_id=self.album_id,
            playlist_ids=self.playlist_ids,
            popularity=self.popularity,
            blacklisted=self.blacklisted,
            track_json=self.track_json
        )


class NewUser(_SpotifyObject):
    """"""

    def __init__(self, spotify_user: dict) -> None:
        """

        :param spotify_user: Dict containing Spotify Tracks, in the form of {user_uri: user}
        :raises InputException: if input is invalid
        """

        if not isinstance(spotify_user, dict):
            raise InputException(item_value=spotify_user, valid_values='{user_uri: user}', valid_types=dict)

        super().__init__()

        self.user_json: dict = value_from_dict(spotify_user)
        self.user_id: str = self.user_json['id']
        self.user_name: str = self.user_json['display_name']
        self.user_uri: str = self.user_json['uri']
        self.user_url: str = self.user_json['external_urls']['spotify']

        if 'url' not in self.user_json['images'][0]:
            self.user_image: str = file_image_bytes(NO_IMAGE_PATH)
        else:
            self.user_image: str = spotify_image_bytes(self.user_json['images'][0]['url'])

        top_artists: dict= spotify.get_users_top_items(item_type="artists", time_range="medium_term")
        playlists: dict = spotify.get_users_playlists(user_id=self.user_id, limit=None)
        top_tracks: dict = spotify.get_users_top_items(item_type="tracks", time_range="medium_term")

        self.follower: int = self.user_json['followers']
        self.playlist_ids: list[str] = [uri_to_id(current_playlist) for current_playlist in playlists.keys()]
        self.top_track_ids: list[str] = [uri_to_id(current_track) for current_track in top_tracks.keys()]
        self.top_artist_ids: list[str] = [uri_to_id(current_artist) for current_artist in top_artists.keys()]

        APP_DATABASE.add_item_to_table(
            table_name='users',
            user_id=self.user_id,
            user_name=self.user_name,
            user_uri=self.user_uri,
            user_url=self.user_url,
            user_image=self.user_image,
            follower=self.follower,
            playlist_ids=self.playlist_ids,
            top_track_ids=self.top_track_ids,
            top_artist_ids=self.top_artist_ids,
            top_genre_names=self.top_genre_names,
            popularity=self.popularity,
            blacklisted=self.blacklisted,
            user_json=self.user_json
        )

    @property
    def top_genre_names(self) -> list[str]:
        """
        :return: list of top genre names
        """
        top_genres = []

        # TODO: figure out what to do here

        return top_genres


class ItemQueues:
    """"""

    def __init__(self):
        self.album_queue = set()
        self.artist_queue = set()
        self.playlist_queue = set()
        self.track_queue = set()
        self.user_queue = set()


    def update_queues(self) -> None:
        """
        Call `fetch_new_ids_from_database()` for every possible case to update all queues with the new URIs

        :return: updates queues
        """

        def fetch_new_ids_from_database(
                table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users'],
                target_type: Literal['album', 'artist', 'playlist', 'track', 'user']
        ) -> set | None:
            """
            Get the Items that have no Database entry, but are mentioned in the IDs (lists) from other tables. (e.g. Get to database unknown artists mentioned in albums artist_ids)

            :param table_name: source table name (e.g. albums)
            :param target_type: what type of items to return (e.g. artists)
            :return: Set containing Spotify Items IDs
            """
            type_id_map = {
                'albums': {
                    "artist": "artist_ids",
                    "track": "track_ids"
                },
                "artists": {
                    "album": "album_ids",
                    "playlist": "playlist_ids",
                    "track": "top_track_ids"
                },
                "playlists": {
                    "track": "track_ids",
                    "user": "owner_id"
                },
                "tracks": {
                    "album": "album_id",
                    "artist": "artist_ids",
                    "playlist": "playlist_ids"
                },
                "users": {
                    "artist": "top_artist_ids",
                    "playlist": "playlist_ids",
                    "track": "top_track_ids"
                }
            }

            # get IDs from target column
            unknown_ids = APP_DATABASE.fetch_column(table_name=table_name, table_column=type_id_map[table_name][target_type])
            target_list = set()
            for row in load_list_from_database(unknown_ids):
                if row != '[]':
                    target_list.add(row)

            # fetch existing IDs from Database

            existing_items = set(APP_DATABASE.fetch_column(table_name=f"{target_type}s", table_column=f'{target_type}_id'))
            return target_list - existing_items

        # update albums
        self.album_queue.update(fetch_new_ids_from_database(table_name="artists", target_type="album"))
        self.album_queue.update(fetch_new_ids_from_database(table_name="tracks", target_type="album"))

        # update artists
        self.artist_queue.update(fetch_new_ids_from_database(table_name="albums", target_type="artist"))
        self.artist_queue.update(fetch_new_ids_from_database(table_name="tracks", target_type="artist"))
        self.artist_queue.update(fetch_new_ids_from_database(table_name="users", target_type="artist"))

        # update playlists
        self.playlist_queue.update(fetch_new_ids_from_database(table_name="artists", target_type="playlist"))
        self.playlist_queue.update(fetch_new_ids_from_database(table_name="tracks", target_type="playlist"))
        self.playlist_queue.update(fetch_new_ids_from_database(table_name="users", target_type="playlist"))

        # update tracks
        self.track_queue.update(fetch_new_ids_from_database(table_name="albums", target_type="track"))
        self.track_queue.update(fetch_new_ids_from_database(table_name="artists", target_type="track"))
        self.track_queue.update(fetch_new_ids_from_database(table_name="playlists", target_type="track"))
        self.track_queue.update(fetch_new_ids_from_database(table_name="users", target_type="track"))

        # update users
        self.user_queue.update(fetch_new_ids_from_database(table_name="playlists", target_type="user"))


    def process_all_queues(self):
        """
        iterates through every queue and adds the items to the database
        """

        if self.album_queue:
            albums = spotify.get_several_albums(album_ids=list(self.album_queue))
            for uri, current_album in albums.items():
                NewAlbum(spotify_album=current_album)
                # print(f"{CGREEN}created Album for {uri}{TEXTCOLOR}")

            self.album_queue.clear()
            return


        if self.artist_queue:
            artists = spotify.get_several_artists(artist_ids=list(self.artist_queue))
            for uri, current_artist in artists.items():
                NewArtist(spotify_artist=current_artist)
                # print(f"{CGREEN}created Artist for {uri}{TEXTCOLOR}")

            self.artist_queue.clear()

        if self.playlist_queue:
            playlists = spotify.get_several_playlists(playlist_ids=list(self.playlist_queue))
            for uri, current_playlist in playlists.items():
                NewPlaylist(spotify_playlist=current_playlist)
                # print(f"{CGREEN}created Playlist for {uri}{TEXTCOLOR}")

            self.playlist_queue.clear()

        if self.track_queue:
            tracks = spotify.get_several_tracks(track_ids=list(self.track_queue))
            for uri, current_track in tracks.items():
                NewTrack(spotify_track=current_track)
                # print(f"{CGREEN}created Track for {uri}{TEXTCOLOR}")

            self.track_queue.clear()

        if self.user_queue:
            users = spotify.get_several_users(user_ids=list(self.user_queue))
            for uri, current_user in users.items():
                NewUser(spotify_user=current_user)
                # print(f"{CGREEN}created User for {uri}{TEXTCOLOR}")

            self.user_queue.clear()


class NewDevice:
    def __init__(self, spotify_device: dict) -> None:
        """

        :param spotify_device: Dict containing Spotify Device, in the form of {device_uri: device}
        :raises InputException: if input is invalid
        """
        if not isinstance(spotify_device, dict):
            raise InputException(item_value=spotify_device, valid_values='{device_uri: device}', valid_types=dict)

        self.device_json = value_from_dict(spotify_device)
        self.device_id: str = self.device_json['id']
        self.device_name: str = self.device_json['name']
        self.device_type: str = self.device_json['type']
        self.is_active: bool = bool(self.device_json['is_active'])
        self.is_private_session: bool = bool(self.device_json['is_private_session'])
        self.is_restricted: bool = bool(self.device_json['is_restricted'])
        self.supports_volume: bool = bool(self.device_json['supports_volume'])
        self.volume_percent: int = int(self.device_json['volume_percent'])

        APP_DATABASE.add_item_to_table(
            table_name='devices',
            device_id=self.device_id,
            device_name=self.device_name,
            device_type=self.device_type,
            is_active=self.is_active,
            is_private_session=self.is_private_session,
            is_restricted=self.is_restricted,
            supports_volume=self.supports_volume,
            volume_percent=self.volume_percent,
            device_json=self.device_json
        )


class Album:
    def __init__(self, album_id: str):
        """

        :param album_id:
        :raises SpotifyIdException: if spotify id is invalid
        """
        if not check_spotify_id(album_id):
            raise SpotifyIdException(invalid_id=album_id, id_type="album")

        album_from_db = APP_DATABASE.fetch_row(table_name="albums", item_id=album_id, table_column="*")
        if album_from_db is None:
            print(f"{CCYAN}Album with id '{album_id}' does not exist in database, requesting now ...{TEXTCOLOR}")
            _album = spotify.get_album(album_id=album_id)
            NewAlbum(_album)
            album_from_db = APP_DATABASE.fetch_row(table_name="albums", item_id=album_id, table_column="*")

        self.album_id, \
            self.album_name, \
            self.album_uri, \
            self.album_url, \
            self.album_image, \
            self.genre_names, \
            self.total_duration, \
            self.track_count, \
            self.artist_ids, \
            self.track_ids, \
            self.popularity, \
            self.blacklisted, \
            self.album_json = album_from_db


class Artist:
    def __init__(self, artist_id: str):
        """

        :param artist_id:
        :raises SpotifyIdException: if spotify id is invalid
        """

        if not check_spotify_id(artist_id):
            raise SpotifyIdException(invalid_id=artist_id, id_type="artist")

        artist_from_db = APP_DATABASE.fetch_row(table_name="artists", item_id=artist_id, table_column="*")
        if artist_from_db is None:
            print(f"{CCYAN}Artist with id '{artist_id}' does not exist in database, requesting now ...{TEXTCOLOR}")
            _artist = spotify.get_artist(artist_id=artist_id)
            NewArtist(_artist)
            artist_from_db = APP_DATABASE.fetch_row(table_name="artists", item_id=artist_id, table_column="*")

        self.artist_id, \
            self.artist_name, \
            self.artist_uri, \
            self.artist_url, \
            self.artist_image, \
            self.genre_names, \
            self.follower, \
            self.album_ids, \
            self.playlist_ids, \
            self.top_track_ids, \
            self.popularity, \
            self.blacklisted, \
            self.artist_json = artist_from_db


class Device:
    def __init__(self, device_id: str) -> None:
        """

        :param device_id:
        :raises SpotifyIdException: if spotify id is invalid
        """

        if not check_spotify_id(device_id, is_device=True):
            raise SpotifyIdException(invalid_id=device_id, id_type="device")

        device_from_db = APP_DATABASE.fetch_row(table_name="devices", item_id=device_id, table_column="*")
        if device_from_db is None:
            print(f"{CCYAN}Device with id '{device_id}' does not exist in database, requesting now ...{TEXTCOLOR}")
            _device = spotify.get_device(device_id=device_id)
            NewDevice(_device)
            device_from_db = APP_DATABASE.fetch_row(table_name="devices", item_id=device_id, table_column="*")

        self.device_id, \
            self.device_name, \
            self.device_type, \
            self.is_active, \
            self.is_private_session, \
            self.is_restricted, \
            self.supports_volume, \
            self.volume_percent, \
            self.device_json = device_from_db


class Playlist:
    def __init__(self, playlist_id: str):
        """

        :param playlist_id:
        :raises SpotifyIdException: if spotify id is invalid
        """

        if not check_spotify_id(playlist_id):
            raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

        playlist_from_db = APP_DATABASE.fetch_row(table_name="playlists", item_id=playlist_id, table_column="*")
        if playlist_from_db is None:
            print(f"{CCYAN}Playlist with id '{playlist_id}' does not exist in database, requesting now ...{TEXTCOLOR}")
            _playlist = spotify.get_playlist(playlist_id=playlist_id)
            NewPlaylist(_playlist)
            playlist_from_db = APP_DATABASE.fetch_row(table_name="playlists", item_id=playlist_id, table_column="*")

        self.playlist_id, \
            self.playlist_name, \
            self.playlist_uri, \
            self.playlist_url, \
            self.playlist_image, \
            self.genre_names, \
            self.total_duration, \
            self.track_count, \
            self.owner_id, \
            self.track_ids, \
            self.popularity, \
            self.blacklisted, \
            self.playlist_json = playlist_from_db


class Track:
    def __init__(self, track_id: str):
        """

        :param track_id:
        :raises SpotifyIdException: if spotify id is invalid
        """

        if not check_spotify_id(track_id):
            raise SpotifyIdException(invalid_id=track_id, id_type="track")

        track_from_db = APP_DATABASE.fetch_row(table_name="tracks", item_id=track_id, table_column="*")
        if track_from_db is None:
            print(f"{CCYAN}Track with id '{track_id}' does not exist in database, requesting now ...{TEXTCOLOR}")
            _track = spotify.get_track(track_id=track_id)
            NewTrack(_track)
            track_from_db = APP_DATABASE.fetch_row(table_name="tracks", item_id=track_id, table_column="*")

        self.track_id, \
            self.track_name, \
            self.track_uri, \
            self.track_url, \
            self.track_image, \
            self.genre_names, \
            self.track_duration, \
            self.artist_ids, \
            self.album_id, \
            self.playlist_ids, \
            self.popularity, \
            self.blacklisted, \
            self.track_json = track_from_db


class User:
    def __init__(self, user_id: str):
        """

        :param user_id:
        :raises SpotifyIdException: if spotify id is invalid
        """

        if not check_spotify_id(user_id, is_user=True):
            raise SpotifyIdException(invalid_id=user_id, id_type="user")

        user_from_db = APP_DATABASE.fetch_row(table_name="users", item_id=user_id, table_column="*")
        if user_from_db is None:
            print(f"{CCYAN}User with id '{user_id}' does not exist in database, requesting now ...{TEXTCOLOR}")
            _user = spotify.get_users_profile(user_id=user_id)
            NewUser(_user)
            user_from_db = APP_DATABASE.fetch_row(table_name="users", item_id=user_id, table_column="*")

        self.user_id, \
            self.user_name, \
            self.user_uri, \
            self.user_url, \
            self.user_image, \
            self.follower, \
            self.playlist_ids, \
            self.top_track_ids, \
            self.top_artist_ids, \
            self.top_genre_names, \
            self.popularity, \
            self.blacklisted, \
            self.user_json = user_from_db



# Note: Code snippets for the future:
# APP_DATABASE.add_item_to_table(
# 	table_name='genres',
# 	genre_name=self.genre_name,
# 	acousticness_lower_limit=self.acousticness_lower_limit,
# 	acousticness_upper_limit=self.acousticness_upper_limit,
# 	danceability_lower_limit=self.danceability_lower_limit,
# 	danceability_upper_limit=self.danceability_upper_limit,
# 	duration_ms=self.duration_ms,
# 	energy_lower_limit=self.energy_lower_limit,
# 	energy_upper_limit=self.energy_upper_limit,
# 	instrumentalness_lower_limit=self.instrumentalness_lower_limit,
# 	instrumentalness_upper_limit=self.instrumentalness_upper_limit,
# 	key_lower_limit=self.key_lower_limit,
# 	key_upper_limit=self.key_upper_limit,
# 	liveness_lower_limit=self.liveness_lower_limit,
# 	liveness_upper_limit=self.liveness_upper_limit,
# 	loudness_lower_limit=self.loudness_lower_limit,
# 	loudness_upper_limit=self.loudness_upper_limit,
# 	mode_lower_limit=self.mode_lower_limit,
# 	mode_upper_limit=self.mode_upper_limit,
# 	speechiness_lower_limit=self.speechiness_lower_limit,
# 	speechiness_upper_limit=self.speechiness_upper_limit,
# 	tempo_lower_limit=self.tempo_lower_limit,
# 	tempo_upper_limit=self.tempo_upper_limit,
# 	valence_lower_limit=self.valence_lower_limit,
# 	valence_upper_limit=self.valence_upper_limit,
# 	popularity=self.popularity,
# 	blacklisted=self.blacklisted,
# )

if __name__ == "__main__":
    """"""
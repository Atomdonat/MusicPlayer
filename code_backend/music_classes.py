"""
File to develop and debug methods, class and more
"""
from code_backend.shared_config import *
from code_backend.secondary_methods import (
    uri_to_id, print_error, list_from_id_string, file_image_bytes,
    spotify_image_bytes, url_to_uri, exclude_from_dict, id_to_uri,
    check_token_expired, load_json, debug_json, print_debug
)
import code_backend.spotify_web_api as sp_api
from code_backend.database_access import MyAppDatabase
import traceback


# cps: 3
class SpotifyObject:
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

        # TODO: implement

        return genres

    # mps: 2
    def update_database(self):
        pass


# cps: 3
class Album(SpotifyObject):
    """"""

    def __init__(self, spotify_album: dict):
        """

        :param spotify_album: Dict containing Spotify Albums, in the form of {album_uri: album}
        """
        super().__init__()

        self.album_id: str = spotify_album['id']
        self.album_name: str = spotify_album['name']
        self.album_url: str = spotify_album['external_urls']['spotify']

        if 'url' not in spotify_album['images'][0]:
            self.album_image: str = file_image_bytes(NO_IMAGE_PATH)
        else:
            self.album_image: str = spotify_image_bytes(spotify_album['images'][0]['url'])

        tracks, self.total_duration = sp_api.get_album_tracks(self.album_id, get_duration=True)
        self.track_count: int = spotify_album['total_tracks']
        self.artist_ids: list[str] = [current_artist['id'] for current_artist in spotify_album['artists']]
        self.track_ids: list[str] = [uri_to_id(current_track) for current_track in tracks.keys()]
        self.album_json: dict = spotify_album

        APP_DATABASE.add_item_to_table(
            table_name='albums',
            album_id=self.album_id,
            album_name=self.album_name,
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


# cps: 3
class Artist(SpotifyObject):
    """"""

    def __init__(self, spotify_artist: dict):
        """

        :param spotify_artist: Dict containing Spotify Artists, in the form of {artist_uri: artist}
        """
        super().__init__()

        self.artist_id: str = spotify_artist['id']
        self.artist_name: str = spotify_artist['name']
        self.artist_url: str = spotify_artist['external_urls']['spotify']

        if 'url' not in spotify_artist['images'][0]:
            self.artist_image: str = file_image_bytes(NO_IMAGE_PATH)
        else:
            self.artist_image: str = spotify_image_bytes(spotify_artist['images'][0]['url'])

        albums: dict = sp_api.get_artists_albums(artist_id=self.artist_id)
        top_tracks: dict = sp_api.get_artists_top_tracks(self.artist_id)

        self.follower: int = spotify_artist['followers']['total']
        self.album_ids: list[str] = [uri_to_id(current_album) for current_album in albums.keys()]
        # Todo: Playlist ID gets added when the Playlist() is instantiated
        self.playlist_ids: list[str] = []
        self.top_track_ids: list[str] = [uri_to_id(current_track) for current_track in top_tracks.keys()]
        self.artist_json: dict = spotify_artist

        APP_DATABASE.add_item_to_table(
            table_name='artists',
            artist_id=self.artist_id,
            artist_name=self.artist_name,
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


# cps: 3
class Playlist(SpotifyObject):
    """"""

    def __init__(self, spotify_playlist: dict):
        """

        :param spotify_playlist: Dict containing Spotify Playlists, in the form of {playlist_id: playlist}
        """
        super().__init__()

        self.playlist_id: str = spotify_playlist['id']
        self.playlist_name: str = spotify_playlist['name']
        self.playlist_url: str = spotify_playlist['external_urls']['spotify']

        if 'url' not in spotify_playlist['images'][0]:
            self.playlist_image: str = file_image_bytes(NO_IMAGE_PATH)
        else:
            self.playlist_image: str = spotify_image_bytes(spotify_playlist['images'][0]['url'])

        playlist_items, self.total_duration = sp_api.get_playlist_items(playlist_id=self.playlist_id, get_duration=True)
        self.track_count: int = spotify_playlist['tracks']['total']
        self.owner_id: str = spotify_playlist['owner']['id']
        self.track_ids: list[str] = [uri_to_id(current_track) for current_track in playlist_items.keys()]
        self.playlist_json: dict = spotify_playlist

        APP_DATABASE.add_item_to_table(
            table_name='playlists',
            playlist_id=self.playlist_id,
            playlist_name=self.playlist_name,
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


# cps: 3
class Track(SpotifyObject):
    """"""

    def __init__(self, spotify_track: dict):
        """

        :param spotify_track: Dict containing Spotify Tracks, in the form of {track_uri: track}
        """
        super().__init__()

        self.track_id: str = spotify_track['id']
        self.track_name: str = spotify_track['name']
        self.track_url: str = spotify_track['external_urls']['spotify']

        if 'images' not in spotify_track:
            self.track_image: str = spotify_image_bytes(spotify_track['album']['images'][0]['url'])
        else:
            self.track_image: str = file_image_bytes(NO_IMAGE_PATH)

        self.track_duration: int = spotify_track['duration_ms']
        self.album_id: str = spotify_track['album']['id']
        self.artist_ids: list[str] = [current_artist['id'] for current_artist in spotify_track['artists']]
        # Todo: Playlist ID gets added when the Playlist() is instantiated
        self.playlist_ids: list[str] = []
        self.track_json: dict = spotify_track

        APP_DATABASE.add_item_to_table(
            table_name='tracks',
            track_id=self.track_id,
            track_name=self.track_name,
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


# cps: 3
class User(SpotifyObject):
    """"""

    def __init__(self, spotify_user: dict) -> None:
        """

        :param spotify_user: Dict containing Spotify Tracks, in the form of {user_uri: user}
        """
        super().__init__()

        self.user_id: str = spotify_user['id']
        self.user_name: str = spotify_user['display_name']
        self.user_url: str = spotify_user['external_urls']['spotify']

        if 'url' not in spotify_user['images'][0]:
            self.user_image: str = file_image_bytes(NO_IMAGE_PATH)
        else:
            self.user_image: str = spotify_image_bytes(spotify_user['images'][0]['url'])

        top_artists: dict= sp_api.get_users_top_items(item_type="artists", time_range="medium_term")
        playlists: dict = sp_api.get_users_playlists(user_id=self.user_id, limit=None)
        top_tracks: dict = sp_api.get_users_top_items(item_type="tracks", time_range="medium_term")

        self.follower: int = spotify_user['followers']
        self.playlist_ids: list[str] = [uri_to_id(current_playlist) for current_playlist in playlists.keys()]
        self.top_track_ids: list[str] = [uri_to_id(current_track) for current_track in top_tracks.keys()]
        self.top_artist_ids: list[str] = [uri_to_id(current_artist) for current_artist in top_artists.keys()]
        self.user_json: dict = spotify_user

        APP_DATABASE.add_item_to_table(
            table_name='users',
            user_id=self.user_id,
            user_name=self.user_name,
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



# cps: 3
class ItemQueues:
    """"""

    def __init__(self, database: MyAppDatabase):
        self.album_queue = set()
        self.artist_queue = set()
        self.playlist_queue = set()
        self.track_queue = set()
        self.user_queue = set()
        self.database = database


    # mps: 3
    def update_queues(self) -> None:
        """
        Call `fetch_new_ids_from_database()` for every possible case to update all queues with the new URIs
        :return: updates queues
        """

        # mps: 3
        def fetch_new_ids_from_database(
                database: MyAppDatabase,
                table_name: Literal['albums', 'artists', 'tracks', 'playlists', 'users'],
                target_type: Literal['album', 'artist', 'playlist', 'track', 'user']
        ) -> set | None:
            """
            Get the Items that have no Database entry, but are mentioned in the IDs (lists) from other tables. (e.g. Get to database unknown artists mentioned in albums artist_ids)
            :param database: Which database to use
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
            unknown_ids = database.fetch_column(table_name=table_name, table_column=type_id_map[table_name][target_type])
            target_list = set()
            for row in load_list_from_database(unknown_ids):
                if row != '[]':
                    target_list.add(row)

            # fetch existing IDs from Database

            existing_items = set(database.fetch_column(table_name=f"{target_type}s", table_column=f'{target_type}_id'))
            return target_list - existing_items

        # update albums
        self.album_queue.update(fetch_new_ids_from_database(database=self.database, table_name="artists", target_type="album"))
        self.album_queue.update(fetch_new_ids_from_database(database=self.database, table_name="tracks", target_type="album"))

        # update artists
        self.artist_queue.update(fetch_new_ids_from_database(database=self.database, table_name="albums", target_type="artist"))
        self.artist_queue.update(fetch_new_ids_from_database(database=self.database, table_name="tracks", target_type="artist"))
        self.artist_queue.update(fetch_new_ids_from_database(database=self.database, table_name="users", target_type="artist"))

        # update playlists
        self.playlist_queue.update(fetch_new_ids_from_database(database=self.database, table_name="artists", target_type="playlist"))
        self.playlist_queue.update(fetch_new_ids_from_database(database=self.database, table_name="tracks", target_type="playlist"))
        self.playlist_queue.update(fetch_new_ids_from_database(database=self.database, table_name="users", target_type="playlist"))

        # update tracks
        self.track_queue.update(fetch_new_ids_from_database(database=self.database, table_name="albums", target_type="track"))
        self.track_queue.update(fetch_new_ids_from_database(database=self.database, table_name="artists", target_type="track"))
        self.track_queue.update(fetch_new_ids_from_database(database=self.database, table_name="playlists", target_type="track"))
        self.track_queue.update(fetch_new_ids_from_database(database=self.database, table_name="users", target_type="track"))

        # update users
        self.user_queue.update(fetch_new_ids_from_database(database=self.database, table_name="playlists", target_type="user"))


    # mps: 3
    def process_all_queues(self):
        """
        iterates through every queue and adds the items to the database
        """

        if self.album_queue:
            albums = sp_api.get_several_albums(album_ids=list(self.album_queue))
            for uri, current_album in albums.items():
                Album(spotify_album=current_album)
                # print(f"{CGREEN}created Album for {uri}{TEXTCOLOR}")

            self.album_queue.clear()
            return


        if self.artist_queue:
            artists = sp_api.get_several_artists(artist_ids=list(self.artist_queue))
            for uri, current_artist in artists.items():
                Artist(spotify_artist=current_artist)
                # print(f"{CGREEN}created Artist for {uri}{TEXTCOLOR}")

            self.artist_queue.clear()

        if self.playlist_queue:
            playlists = sp_api.get_several_playlists(playlist_ids=list(self.playlist_queue))
            for uri, current_playlist in playlists.items():
                Playlist(spotify_playlist=current_playlist)
                # print(f"{CGREEN}created Playlist for {uri}{TEXTCOLOR}")

            self.playlist_queue.clear()

        if self.track_queue:
            tracks = sp_api.get_several_tracks(track_ids=list(self.track_queue))
            for uri, current_track in tracks.items():
                Track(spotify_track=current_track)
                # print(f"{CGREEN}created Track for {uri}{TEXTCOLOR}")

            self.track_queue.clear()

        if self.user_queue:
            users = sp_api.get_several_users(user_ids=list(self.user_queue))
            for uri, current_user in users.items():
                User(spotify_user=current_user)
                # print(f"{CGREEN}created User for {uri}{TEXTCOLOR}")

            self.user_queue.clear()


# Note: Code snippets for the future:
"""
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
)

APP_DATABASE.add_item_to_table(
	table_name='genres',
	genre_name=self.genre_name,
	acousticness_lower_limit=self.acousticness_lower_limit,
	acousticness_upper_limit=self.acousticness_upper_limit,
	danceability_lower_limit=self.danceability_lower_limit,
	danceability_upper_limit=self.danceability_upper_limit,
	duration_ms=self.duration_ms,
	energy_lower_limit=self.energy_lower_limit,
	energy_upper_limit=self.energy_upper_limit,
	instrumentalness_lower_limit=self.instrumentalness_lower_limit,
	instrumentalness_upper_limit=self.instrumentalness_upper_limit,
	key_lower_limit=self.key_lower_limit,
	key_upper_limit=self.key_upper_limit,
	liveness_lower_limit=self.liveness_lower_limit,
	liveness_upper_limit=self.liveness_upper_limit,
	loudness_lower_limit=self.loudness_lower_limit,
	loudness_upper_limit=self.loudness_upper_limit,
	mode_lower_limit=self.mode_lower_limit,
	mode_upper_limit=self.mode_upper_limit,
	speechiness_lower_limit=self.speechiness_lower_limit,
	speechiness_upper_limit=self.speechiness_upper_limit,
	tempo_lower_limit=self.tempo_lower_limit,
	tempo_upper_limit=self.tempo_upper_limit,
	valence_lower_limit=self.valence_lower_limit,
	valence_upper_limit=self.valence_upper_limit,
	popularity=self.popularity,
	blacklisted=self.blacklisted,
)
"""

if __name__ == "__main__":
    """"""
    APP_DATABASE = MyAppDatabase(MAIN_DATABASE_PATH)

    # Test Data
    test_album = load_json("Databases/JSON_Files/spotify_album_4Gfnly5CzMJQqkUFfoHaP3.json")
    test_artist = load_json("Databases/JSON_Files/spotify_artist_6XyY86QOPPrYVGvF9ch6wz.json")
    test_playlist = load_json("Databases/JSON_Files/spotify_playlist_6bRkO7PLCXgmV4EJH52iU4.json")
    test_track = load_json("Databases/JSON_Files/spotify_track_73QoCfWJJWbRYmm5nCH5Y2.json")
    test_user = load_json("Databases/JSON_Files/spotify_user_simonluca1.json")

    # Test Classes
    # Album(test_album)
    # Artist(test_artist)
    # Playlist(test_playlist)
    # Track(test_track)
    # User(test_user)

    # Test ItemQueue with one initial instance
    item_queue = ItemQueues(APP_DATABASE)
    Playlist(test_playlist)

    item_queue.update_queues()
    item_queue.process_all_queues()

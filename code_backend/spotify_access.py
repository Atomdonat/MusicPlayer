import json

import spotipy
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from typing import Literal
from secondary_methods import split_list_into_chunks, concat_iterables

# load Spotipy credentials
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Define the required scopes / currently needed scopes
# https://developer.spotify.com/documentation/web-api/concepts/scopes
SCOPES = [
    'user-read-playback-state',
    'user-read-currently-playing',
    'user-modify-playback-state',
    'user-library-read',
    'user-top-read',
    'ugc-image-upload',
    'playlist-modify-public',
    'playlist-modify-private'
]

market = 'DE'


# Create Spotify authentication token
def spotify_client() -> spotipy.Spotify:
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=' '.join(SCOPES),
                cache_path=".spotify_cache",
                show_dialog=True  # Set to True to force the user to approve the app every time
            ))
            return sp

        # except ConnectionError as e:
        #     print(f"Error encountered: {e}")
        #     print(f"Retrying... (Attempt {retry_count + 1} of {max_retries})")
        #     retry_count += 1
        #     time.sleep(5)

        except SpotifyException as e:
            spotify_exceptions(e)


def try_spotify_connection(_iter: int = 0) -> spotipy.Spotify:
    if _iter < 10:
        try:
            sp = spotify_client()
            return sp
        except SpotifyException as e:
            spotify_exceptions(e)
            return try_spotify_connection(_iter+1)


def request_multiple_items_of_same_type(sp: spotipy.Spotify, items: list[str], item_type: Literal['album', 'artist', 'playlist', 'track', 'track_analysis', 'user']) -> list[dict]:
    """
    Spotify API request limits:
        Album = 20;
        Artist = 50;
        Playlist = 1;
        Track = 50;
        Audio Features = 100;
        User = 1
    """

    # Fixme: Somehow Albums still get split into chunks larger than 20
    def request_up_to_50_items() -> list[dict]:
        items_instance_list = []
        if item_type == 'album':
            chunked_items = split_list_into_chunks(items, 20)
        else:
            chunked_items = split_list_into_chunks(items, 50)

        for current_chunk in chunked_items:
            if len(current_chunk) > 50 or (len(current_chunk) > 20 and item_type == 'album'):
                raise ValueError(f"Too many items requested: {len(current_chunk)}")

            try:
                match item_type:
                    case 'album':
                        fetched_items = sp.albums(items)['albums']
                    case 'artist':
                        fetched_items = sp.artists(items)['artists']
                    case 'track':
                        fetched_items = sp.tracks(items, market=market)['tracks']
                    case 'track_analysis':
                        fetched_items = sp.audio_features(items)
                    case _:
                        raise ValueError(f"Unknown item type: {item_type}")
            except SpotifyException as e:
                spotify_exceptions(e)
                continue

            items_instance_list = concat_iterables(items_instance_list, fetched_items)

        return items_instance_list

    def request_multiple_playlists_or_user() -> list[dict]:
        items_instance_list = []

        for current_item in items:
            match item_type:
                case 'playlist':
                    fetched_items: dict = sp.playlist(current_item, market=market)
                case 'user':
                    fetched_items: dict = sp.user(current_item)
                case _:
                    raise ValueError(f"Unknown item type: {item_type}")
            items_instance_list.append(fetched_items)

        return items_instance_list

    if item_type in ['album', 'artist', 'track', 'track_analysis']:
        return request_up_to_50_items()
    else:
        return request_multiple_playlists_or_user()


def request_one_item(sp: spotipy.Spotify, item_type: Literal['album', 'artist', 'playlist', 'track', 'track_analysis', 'user'], spotify_id: str) -> dict | None:
    if spotify_id == "0000000000000000000000":
        return None

    # Normal ID
    try:
        match item_type:
            case 'album':
                return sp.album(album_id=spotify_id, market=market)
            case 'artist':
                return sp.artist(artist_id=spotify_id)
            case 'playlist':
                return sp.playlist(playlist_id=spotify_id, market=market)
            case 'track':
                return sp.track(track_id=spotify_id, market=market)
            case 'user':
                return sp.user(user=spotify_id)
            case _:
                return None

    except SpotifyException as e:
        spotify_exceptions(e)


def spotify_exceptions(error: SpotifyException, _raise: bool = True) -> None:
    match error.http_status:
        case 400:
            if 'token revoked' in error.msg:
                print("Refresh token has been revoked. Try deleting .spotify_cache")
            elif 'Too many ids requested' in error.msg:
                print("Too many ids requested. retry with less ids")
            else:
                print(f"Error 400: {error.msg}")
        case 429:
            print("'retry-after' value:", error.headers['retry-after'])
            retry_value = error.headers['retry-after']
            if int(error.headers['retry-after']) > 60:
                print("STOP FOR TODAY, retry value too high {}".format(retry_value))
                exit()
        case _:
            print(error)


if __name__ == '__main__':
    sp = spotify_client()
    _id = "1164847650"  # "4Gfnly5CzMJQqkUFfoHaP3"
    _type = {0: 'album', 1: 'artist', 2: 'track', 3: 'playlist', 4: 'user', 5: ''}

    if sp is not None:
        data = sp.user(_id)  # sp1.some_method()
        # extra = ""  # "_some_detail"
        # with open(f"../Databases/JSON_Files/spotify_{_type[4]}{extra}_{_id}.json", 'w') as f:
        #     json.dump(data, f)
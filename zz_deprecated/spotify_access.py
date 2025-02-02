###
# Note: will be deprecated if `spotify_web_api.py` is finished
##

import json
import sys

import spotipy
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from typing import Literal
from secondary_methods import split_list_into_chunks, concat_iterables, url_to_uri

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
    'playlist-modify-private',
    'playlist-read-private'
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


def try_spotify_connection(_iter: int = 0) -> spotipy.Spotify | None:
    if _iter < 10:
        try:
            sp = spotify_client()
            return sp
        except SpotifyException as e:
            spotify_exceptions(e)
            return try_spotify_connection(_iter+1)
    else:
        spotify_exceptions()
        return


def request_multiple_items_of_same_type(sp: spotipy.Spotify, items: list[str], item_type: Literal['album', 'artist', 'playlist', 'track', 'track_analysis', 'user']) -> list[dict]:
    """
    Spotify item limit per request:
        ??Album = 20??;
        Artist = 50;
        Playlist = 1;
        Track = 50;
        Audio Features = 100;
        User = 1
    """
    # ToDo: check if every API call returns expected json
    # Fixme: Somehow Albums still get split into chunks larger than 20, or at least catch http errors for too many ids
    def request_up_to_50_items() -> list[dict] | None:
        items_instance_list = []
        if item_type == 'album':
            chunked_items = split_list_into_chunks(items, 20)
        else:
            chunked_items = split_list_into_chunks(items, 50)

        for current_chunk in chunked_items:
            if len(current_chunk) > 50 or (len(current_chunk) > 20 and item_type == 'album'):
                print(f"Too many items requested: {len(current_chunk)}")
                continue

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
                    try:
                        fetched_items: dict = sp.playlist(current_item, market=market)

                        with open("../Databases/JSON_Files/tmp_data.json", "w") as file:
                            json.dump(fetched_items, file)
                            sys.exit(0)
                    except SpotifyException as e:
                        spotify_exceptions(e)
                        exit(1)
                case 'user':
                    fetched_items: dict = sp.user(current_item)
                case _:
                    print(f"Unknown item type: {item_type}")
                    continue
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


def spotify_exceptions(error: SpotifyException = None, _raise: bool = True) -> None:
    match error.http_status:
        case 400:
            if 'token revoked' in error.msg:
                print("Refresh token has been revoked. Try deleting .spotify_cache")
            elif 'Too many ids requested' in error.msg:
                print("Too many ids requested. retry with less ids")
            else:
                print(f"Error 400: {error.msg}")
        case 414:
            print(f"Request-URI Too Long:\n{error.msg}")
        case 429:
            if "too many 502 error responses" in error.msg:
                print("Max Retries reached")
                return
        case _:
            print(error)


if __name__ == '__main__':
    sp = spotify_client()
    _id = url_to_uri("https://open.spotify.com/playlist/1TufW5MXE6oDxo7KVw4ACV?si=547ca2fa281d4557", to_id=True)  # "4Gfnly5CzMJQqkUFfoHaP3"
    # test = url_to_uri("https://open.spotify.com/playlist/6bRkO7PLCXgmV4EJH52iU4?si=fbe6a250558f45f8", to_id=True)  # track_count=5
    # _type = {0: 'album', 1: 'artist', 2: 'track', 3: 'playlist', 4: 'user', 5: ''}
    # image = image_to_b64(Image.open("/home/simon/git_repos/MusicPlayer/Icons/Spotipy_Logo.png"), 'PNG')
    # if sp is not None:
    #     sp.playlist_upload_cover_image(playlist_id="1TufW5MXE6oDxo7KVw4ACV", image_b64=)
        # data = sp.album_tracks(_id, MARKET=MARKET)  # sp1.some_method()
        # extra = ""  # "_some_detail"
        # with open(f"../Databases/JSON_Files/tmp_data.json", 'w') as f:
        #     json.dump(data, f)
    tmp = sp.artist("52qKfVcIV4GS8A8Vay2xtt")
    print(tmp["images"][0])
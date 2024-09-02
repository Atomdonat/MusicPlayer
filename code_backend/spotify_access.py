import json

import spotipy
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import time

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

        except ConnectionError as e:
            print(f"Error encountered: {e}")
            print(f"Retrying... (Attempt {retry_count + 1} of {max_retries})")
            retry_count += 1
            time.sleep(5)

        except SpotifyException as e:
            print(e)
            retry_count += 1
            time.sleep(5)

        finally:
            return sp


if __name__ == '__main__':
    sp1 = spotify_client()
    _id = "1164847650"  # "4Gfnly5CzMJQqkUFfoHaP3"
    _type = {0: 'album', 1: 'artist', 2: 'track', 3: 'playlist', 4: 'user', 5: ''}

    if sp1 is not None:
        data = sp1.user(_id)  # sp1.some_method()
        extra = ""  # "_some_detail"
        with open(f"../Databases/JSON_Files/spotify_{_type[4]}{extra}_{_id}.json", 'w') as f:
            json.dump(data, f)

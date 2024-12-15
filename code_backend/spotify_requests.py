import os
from dotenv import load_dotenv
import requests
import json


# Note: Curl -> Requests Converter:


# Note: Request Token (valid for 1 hour)
#   curl -X POST "https://accounts.spotify.com/api/token" \
#        -H "Content-Type: application/x-www-form-urlencoded" \
#        -d "grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret"

# Note: Method progress status (M.G.S.)
#  0: planned, not implemented
#  1: implemented, not tested
#  2: in testing/debugging
#  3: finished

# load Spotipy credentials
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

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


# mgs: 2
def request_token() -> None:
    """
    Curl request calling Spotify Web API to obtain token
    :return: caches token in ./.cached_token
    """
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    response = requests.post(url=url, headers=headers, data=data)
    with open('./.cached_token', 'w') as token:
        token.write(response.text)


if __name__ == "__main__":
    print(request_token())

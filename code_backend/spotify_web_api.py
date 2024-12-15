import os
import sys

from dotenv import load_dotenv
import requests
import json
from typing import Literal
from code_backend.secondary_methods import image_from_url
from PIL import Image
from urllib.parse import quote

TEXTCOLOR = "\033[38;2;172;174;180m"

# Note: Curl -> Requests Converter:
#  https://curlconverter.com/python/

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
TOKEN_FILE = "../code_backend/.spotify_cache"
MARKET = "DE"
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

# mgs: 3
def debug_json(jason: dict):
    with open("testing/debugging.json", "w") as file:
        json.dump(jason, file, indent=4)


# mgs: 3
def check_limit(limit: int, api_max_limit: int = 50) -> None:
    """
    Checks if the user limit exceeded the API limit.
    :param limit: current limit
    :param api_max_limit: maximum API limit
    :return: raise Exception if API limit exceeded
    """
    if limit > api_max_limit:
        raise Exception(f"Limit of {limit} exceeded API limit of {api_max_limit} per request")


# mgs: 3
def request_token() -> None:
    """
    Curl request calling Spotify Web API to obtain token (valid for 1 hour)
    `curl -X POST "https://accounts.spotify.com/api/token" \
       -H "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret"`

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
    with open('../code_backend/.spotify_cache', 'w') as token:
        token.write(response.text)


# load token
token_header: dict
# if not os.path.isfile(TOKEN_FILE):
request_token()

with open(".spotify_cache", "r") as file:
    data = json.load(file)
    # Todo: implement token renewal after ~1h
    token_header = {
        'Authorization': "Bearer " + data["access_token"],
}


# mgs: 3
def error_codes(code: int, message: str = None) -> None:
    """
    Web API uses the following response status codes, as defined in the RFC 2616 and RFC 6585
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/concepts/api-calls#response-status-codes
    :param code:
    :param message:
    :return:
    """
    error_data: dict
    with open("../Databases/JSON_Files/http_errors.json", "r") as e_file:
        error_data = json.load(e_file)[str(code)]

    print(f"\n\x1b[31mRequest returned Code: {error_data["code"]} - {error_data["name"]}\n{error_data["explanation"]}\n\x1b[37m{message}\n{TEXTCOLOR}")
    sys.exit(1)


# mgs: 0
def api_request_data(url: str, request_type: Literal["GET", "POST", "DELETE", "PUT"], json_data: dict | str = None, overwrite_header: dict = None) -> dict | list | None:
    """
    Transferring data from or to a server using Curl commands via [requests](https://docs.python-requests.org/en/latest/index.html). Currently supported HTTP methods are `GET`, `POST`, `PUT` and `DELETE` (This implementation is designed for Spotify API requests)
    :param url: url to curl from/to
    :param request_type: HTTP request method
    :param json_data: JSON data to send
    :return: JSON data fetched from Spotify API
    """

    # HTTP Headers needed for Spotify API requests
    if not overwrite_header:
        headers = {
            'Authorization': f'Bearer {data["access_token"]}'
        }
        if json_data:
            headers['Content-Type'] = 'application/json'
    else:
        headers = overwrite_header

    match request_type:
        case "GET":
            response = requests.get(
                url=url,
                headers=headers,
                json=json_data
            )
        case "POST":
            response = requests.post(
                url=url,
                headers=headers,
                json=json_data
            )

        case "DELETE":
            response = requests.delete(
                url=url,
                headers=headers,
                json=json_data
            )

        case "PUT":
            response = requests.put(
                url=url,
                headers=headers,
                json=json_data
            )

        case _:
            raise f"{request_type} not supported"

    if response.status_code != 200:
        return error_codes(response.status_code, json.loads(response.text)["error"]["message"])

    return response.json()


# mgs: 1
def get_followed_artists(get_type: str = "artist", last_id: str = None, limit: int = 20):
    """
    Get the current user's followed artists.
    Needed Scopes: user-follow-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-followed
    :param get_type:
    :param last_id: ID of the last requested Artist
    :param limit: how many artists to request
    :return: List of artists
    """
    check_limit(
        limit=limit,
        api_max_limit=50
    )

    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/following?type={get_type}&limit={limit}&after={last_id}",
        request_type="GET",
        json_data=None
    )
    return response["artists"]["items"]


# mgs: 1
def get_users_profile(user_id: str):
    """
    Get public profile information about a Spotify user.
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-profile
    :param user_id: User ID
    :return: User Profile
    """
    response = api_request_data(
        url=f"https://api.spotify.com/v1/users/{user_id}",
        request_type="GET",
        json_data=None
    )
    return response


# mgs: 1
def get_users_top_items(
        item_type: Literal["artist", "tracks"],
        time_range: Literal["short_term", "medium_term", "long_term"] = "medium_term",
        limit: int = 20,
        offset: int = 0,
) -> dict:
    """
    Get the current user's top artists or tracks based on calculated affinity.
    Needed Scopes: user-top-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
    :param item_type: The type of entity to return. Valid values: "artists" or "tracks"
    :param time_range: Over what time frame the affinities are computed. Valid values: "long_term" (calculated from ~1 year of data and including all new data as it becomes available), "medium_term" (approximately last 6 months), "short_term" (approximately last 4 weeks). Default: medium_term
    :param limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
    :param offset: The index of the first item to return. Default: 0 (the first item). Use with limit to get the next set of items.
    :return: Dict containing Top Items, in the form of {item_uri: item}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/top/{item_type}?time_range={time_range}&limit={limit}&offset={offset}",
        request_type="GET",
        json_data=None
    )["items"]

    item_dict = {item["uri"]:item for item in response}
    return item_dict


# mgs: 1
def get_current_users_profile():
    """
    Get detailed profile information about the current user (including the current user's username).
    Needed Scopes: user-read-private, user-read-email
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
    :return: Current Users Profile
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/me",
        request_type="GET",
        json_data=None
    )
    return response


# mgs: 1
def check_users_saved_tracks(check_ids: list[str]) -> list[bool]:
    """
    Check if one or more tracks is already saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/check-users-saved-tracks
    :param check_ids: A list of the Spotify IDs to be checked. Maximum: 50 IDs.
    :return: List containing the existence of the tracks
    """
    check_limit(
        limit=len(check_ids),
        api_max_limit=50
    )

    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/tracks/contains",
        request_type="GET",
        json_data=None
    )

    return response


# mgs: 1
def get_users_saved_tracks(limit: int = 20, offset: int = 0) -> dict:
    """
    Get a list of the songs saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks
    :param limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
    :param offset: The index of the first item to return. Default: 0 (the first item). Use with limit to get the next set of items.
    :return: Dict containing Tracks, in the form of {item_uri: item}
    """
    check_limit(
        limit=limit,
        api_max_limit=50
    )

    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/tracks?market={MARKET}&limit={limit}&offset={offset}",
        request_type="GET",
        json_data=None
    )["items"]

    return {item["uri"]: item for item in response}


# mgs: 1
def get_several_tracks(track_ids: list[str]):
    """
    Get Spotify catalog information for multiple tracks based on their Spotify IDs.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-several-tracks
    :param track_ids: A list of the Spotify IDs to be checked. Maximum: 50 IDs.
    :return: Dict of Spotify Tracks, in the form of {item_uri: item}
    """
    check_limit(
        limit=len(track_ids),
        api_max_limit=50
    )

    response = api_request_data(
        url=f"https://api.spotify.com/v1/tracks?market={MARKET}&ids={track_ids}",
        request_type="GET",
        json_data=None
    )
    return {item["uri"]: item for item in response["tracks"]}


# mgs: 1
def get_track(track_id: str) -> dict:
    """
    Get Spotify catalog information for a single track identified by its unique Spotify ID.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-track
    :param track_id: The Spotify ID for the track.
    :return: A track
    """
    response = api_request_data(
        url=f"https://api.spotify.com/v1/tracks/{track_id}?market={MARKET}",
        request_type="GET",
        json_data=None
    )
    return response


# mgs: 2
def get_playlist(playlist_id: str) -> dict | None:
    """
    Get a playlist owned by a Spotify user.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-playlist
    :param playlist_id: The Spotify ID of the playlist.
    :return: A playlist
    """
    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}?market={MARKET}",
        request_type="GET",
        json_data=None
    )
    return response


# mgs: 1
def change_playlist_details(playlist_id: str, name: str, public: bool, collaborative: bool, description: str) -> dict | None:
    """
    Change a playlist's name and public/private state. (The user must, of course, own the playlist.)
    Needed Scopes: playlist-modify-public, playlist-modify-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/change-playlist-details
    :param playlist_id: The Spotify ID of the playlist.
    :param name: The new name for the playlist, for example "My New Playlist Title"
    :param public: The playlist's public/private status (if it should be added to the user's profile or not): true the playlist will be public, false the playlist will be private, null the playlist status is not relevant. For more about public/private status, see [Working with Playlists](https://developer.spotify.com/documentation/web-api/concepts/playlists)
    :param collaborative: If `true`, the playlist will become collaborative and other users will be able to modify the playlist in their Spotify client. Note: You can only set `collaborative=true` on non-public playlists.
    :param description: Value for playlist description as displayed in Spotify Clients and in the Web API.
    """

    json_data = {
        'name': name,
        'description': description,
        'public': public,
        'collaborative': collaborative,
    }

    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}",
        request_type="PUT",
        json_data=json_data
    )

    return response


# mgs: 1
def get_playlist_items(playlist_id:str) -> dict | None:
    """
    Get full details of the items of a playlist owned by a Spotify user.
    Needed Scopes: playlist-read-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks
    :param playlist_id: The Spotify ID of the playlist.
    :return:
    """
    track_count = get_playlist(playlist_id)["tracks"]["total"]
    track_dicts = {}

    for current_offset in range(0, track_count, 50):
        items = api_request_data(
            url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50&offset={current_offset}&market={MARKET}",
            request_type="GET",
            json_data=None
        )

        if not items:
            print(f"\n\x1b[31mWhat the fuck just happened? looks like you need to debug smth... xD{TEXTCOLOR}")
            sys.exit(1)

        for current_track in items["items"]:
            track_dicts[current_track["track"]["uri"]] = current_track["track"]

    if len(track_dicts) != track_count:
        print(f"\n\x1b[31mCould not fetch all Playlist {playlist_id} items{TEXTCOLOR}\nTracks fetched: {len(track_dicts)}, Tracks in Playlist: {track_count}\n")

    return track_dicts


# mgs: 1
def update_playlist_items(playlist_id:str, uris: list[str]) -> None:
    """

    Needed Scopes: playlist-read-private, playlist-modify-public, playlist-modify-private
    :param playlist_id: The Spotify ID of the playlist.
    :param uris: A comma-separated list of Spotify URIs to add, can be track or episode URIs. For example: uris=spotify:track:4iV5W9uYEdYUVa79Axb7Rh, spotify:track:1301WleyT98MSxVHPZCA6M, spotify:episode:512ojhOuo1ktJprKbVcKyQ A maximum of 100 items can be added in one request. Note: it is likely that passing a large number of item URIs as a query parameter will exceed the maximum length of the request URI. When adding a large number of items, it is recommended to pass them in the request body, see below.
    """

    # Fetch and remove current Tracks
    items = get_playlist_items(playlist_id=playlist_id)
    remove_playlist_items(
        playlist_id=playlist_id,
        track_uris=list(items.keys())
    )
    # Add new items
    add_items_to_playlist(
        playlist_id=playlist_id,
        uris=uris
    )


# mgs: 1
def add_items_to_playlist(playlist_id: str, uris: list[str], position: int = 0) -> None:
    """
    Add one or more items to a user's playlist.
    Needed Scopes: playlist-modify-public, playlist-modify-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist
    :param playlist_id: The Spotify ID of the playlist.
    :param position: The position to insert the items, a zero-based index. For example, to insert the items in the first position: position=0; to insert the items in the third position: position=2. If omitted, the items will be appended to the playlist. Items are added in the order they are listed in the query string or request body.
    :param uris: A list of Spotify URIs to add, can be track or episode URIs. For example: uris=spotify:track:4iV5W9uYEdYUVa79Axb7Rh, spotify:track:1301WleyT98MSxVHPZCA6M, spotify:episode:512ojhOuo1ktJprKbVcKyQ A maximum of 100 items can be added in one request. Note: it is likely that passing a large number of item URIs as a query parameter will exceed the maximum length of the request URI. When adding a large number of items, it is recommended to pass them in the request body, see below.
    """

    # Todo: better conversion with urllib or request
    uri_str = "%2C".join(uris).replace(":","%3")

    json_data = {
        "position": 0
    }

    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={uri_str}",
        request_type="POST",
        json_data=json_data
    )
    return response


# mgs: 1
def remove_playlist_items(playlist_id: str, track_uris: list[str]) -> None:
    """
    Remove one or more items from a user's playlist.
    Needed Scopes: playlist-modify-public, playlist-modify-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/remove-tracks-playlist
    :param playlist_id: The Spotify ID of the playlist.
    :param track_uris: An array of objects containing Spotify URIs of the tracks or episodes to remove. A maximum of 100 objects can be sent at once.
    """

    track_dict = [{"uri": item} for item in track_uris]
    json_data = {
        'tracks': track_dict,
    }

    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
        request_type="DELETE",
        json_data=json_data
    )

    return response


# mgs: 1
def get_current_users_playlists(limit: int = 20, offset: int = 0) -> dict | None:
    """
    Get a list of the playlists owned or followed by the current Spotify user.
    Needed Scopes: playlist-read-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists
    :param limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
    :param offset: The index of the first playlist to return. Default: 0 (the first object). Maximum offset: 100.000. Use with limit to get the next set of playlists.
    :return: Dict of Spotify Playlists, in the form of {item_uri: item}
    """
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/playlists?limit={limit}&offset={offset}",
        request_type="GET",
        json_data=None
    )
    return {item["uri"]: item for item in response["items"]}


# mgs: 1
def get_users_playlists(user_id: str, limit: int = 20, offset: int = 0) -> dict | None:
    """
    Get a list of the playlists owned or followed by a Spotify user.
    Needed Scopes: playlist-read-private, playlist-read-collaborative
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists
    :param user_id: The user's Spotify user ID.
    :param limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
    :param offset: The index of the first playlist to return. Default: 0 (the first object). Maximum offset: 100.000. Use with limit to get the next set of playlists.
    :return: Dict of Spotify Playlists, in the form of {item_uri: item}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/users/{user_id}/playlists?limit={limit}&offset={offset}",
        request_type="GET",
        json_data=None
    )
    return {item["uri"]: item for item in response["items"]}


# mgs: 1
def create_playlist(user_id: str, name: str, public: bool = True, collaborative: bool = False, description: str = None) -> dict | None:
    """
    Create a playlist for a Spotify user. (The playlist will be empty until you add tracks.) Each user is generally limited to a maximum of 11000 playlists.
    Needed Scopes: playlist-modify-public, playlist-modify-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/create-playlist
    :param user_id: The user's Spotify user ID.
    :param name: The name for the new playlist, for example "Your Coolest Playlist". This name does not need to be unique; a user may have several playlists with the same name.
    :param public: Defaults to true. The playlist's public/private status (if it should be added to the user's profile or not): true the playlist will be public, false the playlist will be private. To be able to create private playlists, the user must have granted the "playlist-modify-private" scope. For more about public/private status, see Working with Playlists
    :param collaborative: Defaults to false. If true the playlist will be collaborative. Note: to create a collaborative playlist you must also set public to false. To create collaborative playlists you must have granted "playlist-modify-private" and "playlist-modify-public" scopes.
    :param description: value for playlist description as displayed in Spotify Clients and in the Web API.
    :return: A playlist, in the form of {item_uri: item}
    """

    json_data = {
        "name": name,
        "description": description,
        "public": public,
        "collaborative": collaborative,
    }
    response = api_request_data(
        url=f"https://api.spotify.com/v1/users/{user_id}/playlists",
        request_type="POST",
        json_data=json_data
    )
    return {response["uri"]: response}


# mgs: 1
def get_playlist_cover_image(playlist_id: str) -> Image:
    """
    https://developer.spotify.com/documentation/web-api/reference/get-playlist-cover
    Needed Scopes: 
    Official API Documentation: Get the current image associated with a specific playlist.
    :param playlist_id: The Spotify ID of the playlist.
    :return: Playlist Cover Image loaded as Pillow Image
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        request_type="GET",
        json_data=None
    )
    return image_from_url(response[0]["url"])


# mgs: 1
def add_custom_playlist_cover_image(playlist_id: str, image: str) -> None:
    """
    Replace the image used to represent a specific playlist.
    Needed Scopes: ugc-image-upload, playlist-modify-private, playlist-modify-public
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/upload-custom-playlist-cover
    :param playlist_id: The Spotify ID of the playlist.
    :param image: Base64 encoded JPEG image data, maximum payload size is 256 KB.
    """

    api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        request_type="PUT",
        json_data=image,
        overwrite_header={
            'Authorization': f'Bearer {data["access_token"]}',
            'Content-Type': "image/jpeg"
        }
    )


# mgs: 1
def get_artist(artist_id: str) -> dict | None:
    """
    Get Spotify catalog information for a single artist identified by their unique Spotify ID.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-artist
    :param artist_id: The Spotify ID of the artist.
    :return: Spotify Artist, in the form of {item_uri: item}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{artist_id}",
        request_type="GET",
        json_data=None
    )

    return {response["uri"]: response}


# mgs: 1
def get_several_artists(artist_ids: list[str]) -> dict | None:
    """
    Get Spotify catalog information for several artists based on their Spotify IDs.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists
    :param artist_ids: A comma-separated list of the Spotify IDs for the artists.
    :return: Spotify Artist, in the form of {item_uri: item}
    """

    artists = {}
    for current_chunk in range(0, len(artist_ids), 50):
        encoded_chunk = quote(",".join(artist_ids[current_chunk: current_chunk + 50]))
        response = api_request_data(
            url=f"https://api.spotify.com/v1/artists?ids={encoded_chunk}",
            request_type="GET",
            json_data=None
        )
        tmp = {item["uri"]: item for item in response["artists"]}
        artists.update(tmp)

    return artists


# mgs: 1
def get_artists_albums(album_id: str, limit: int = 20, offset: int = 0) -> dict | None:
    """
    Get Spotify catalog information about an artist's albums.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums
    :param album_id: The Spotify ID of the album.
    :param limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
    :param offset: The index of the first item to return. Default: 0 (the first item). Use with limit to get the next set of items.
    """

    check_limit(
        limit=limit,
        api_max_limit=50
    )

    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{album_id}/albums?market={MARKET}&limit={limit}&offset={offset}",
        request_type="GET",
        json_data=None
    )
    return response


# mgs: 1
def get_artists_top_tracks(artist_id: str) -> dict | None:
    """
    Get Spotify catalog information about an artist's top tracks by country.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks
    :param artist_id: The Spotify ID of the artist.
    :return: Spotify Artists, in the form of {item_uri: item}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market={MARKET}",
        request_type="GET",
        json_data=None
    )

    return {item["uri"]: item for item in response["tracks"]}


# mgs: 1
def check_users_saved_albums(album_ids: list[str]) -> dict | None:
    """
    Check if one or more albums is already saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/check-users-saved-albums
    :param album_ids: A comma-separated list of the Spotify IDs for the albums. Maximum: 20 IDs.
    :return: Saved Spotify Albums, in the form of {item_uri: exists?}
    """

    albums = {}
    for current_chunk in range(0, len(album_ids), 50):
        encoded_chunk = quote(",".join(album_ids[current_chunk: current_chunk + 50]))
        response = api_request_data(
            url=f"https://api.spotify.com/v1/me/albums/contains?ids={encoded_chunk}",
            request_type="GET",
            json_data=None
        )

        for uri, existence in zip(album_ids[current_chunk: current_chunk + 50], response):
            albums[uri] = existence

    return albums


# mgs: 1
def get_album_tracks(album_id: str) -> dict | None:
    """
    Get Spotify catalog information about an album’s tracks. Optional parameters can be used to limit the number of tracks returned.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks
    :param album_id: The Spotify ID of the album.
    :return: Spotify Album Tracks, in the form of {item_uri: item}
    """

    track_count = get_album(album_id=album_id)["total_tracks"]
    track_dicts = {}

    for current_offset in range(0, track_count, 50):
        items = api_request_data(
            url=f"https://api.spotify.com/v1/albums/{album_id}/tracks?market={MARKET}&limit=50&offset={current_offset}",
            request_type="GET",
            json_data=None
        )

        if not items:
            print(f"\n\x1b[31mWhat the fuck just happened? looks like you need to debug smth... xD{TEXTCOLOR}")
            sys.exit(1)

        for current_track in items["items"]:
            track_dicts[current_track["uri"]] = current_track

    if len(track_dicts) != track_count:
        print(f"\n\x1b[31mCould not fetch all Playlist {album_id} items{TEXTCOLOR}\nTracks fetched: {len(track_dicts)}, Tracks in Playlist: {track_count}\n")

    return track_dicts


# mgs: 1
def get_several_albums(album_ids: list[str]) -> dict | None:
    """
    Get Spotify catalog information for multiple albums identified by their Spotify IDs.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-multiple-albums
    :param album_ids: A comma-separated list of the Spotify IDs for the albums.
    :return: Spotify Albums, in the form of {item_uri: item}
    """

    albums = {}
    for current_chunk in range(0, len(album_ids), 50):
        encoded_chunk = quote(",".join(album_ids[current_chunk: current_chunk + 50]))
        response = api_request_data(
            url=f"https://api.spotify.com/v1/albums?ids={encoded_chunk}&market={MARKET}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["artists"]}
        albums.update(tmp)

    return albums

# mgs: 1
def get_album(album_id: str) -> dict | None:
    """
    Get Spotify catalog information for a single album.
    Needed Scopes: 
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-album
    :param album_id: The Spotify ID of the album.
    :return: Spotify Albums, in the form of {item_uri: item}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/albums/{album_id}?market={MARKET}",
        request_type="GET",
        json_data=None
    )

    return {response["uri"]: response}


# mgs: 1
def get_users_saved_albums() -> dict | None:
    """
    Get a list of the albums saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-saved-albums
    """

    albums = {}

    # Get first (up to) 50 albums
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/albums?limit=50&offset=0&market={MARKET}",
        request_type="GET",
        json_data=None
    )

    tmp = {item["album"]["uri"]: item["album"] for item in response["items"]}
    albums.update(tmp)

    # If there are more than 50 albums:
    total_albums = response["total"]
    current_offset = 50

    while current_offset < total_albums:
        response = api_request_data(
            url=f"https://api.spotify.com/v1/me/albums?limit=50&offset={current_offset}&market={MARKET}",
            request_type="GET",
            json_data=None
        )
        tmp = {item["album"]["uri"]: item["album"] for item in response["items"]}
        albums.update(tmp)

        current_offset += 50

    return albums


if __name__ == '__main__':
    print(get_playlist_items(
        playlist_id="6QjbdNFUe4SFNE82RTmcCJ"
    ))
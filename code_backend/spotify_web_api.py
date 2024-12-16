from code_backend.secondary_methods import image_from_url
from code_backend.shared_config import *

from urllib.parse import quote


TEXTCOLOR = "\033[38;2;172;174;180m"

# Note: Curl -> Requests Converter:
#  https://curlconverter.com/python/

# mps: Method progress status (M.P.S.)
#  0: planned, not implemented
#  1: implemented, not tested
#  2: in testing/debugging
#  3: finished

# load Spotipy credentials
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
TOKEN_FILE = root_dir_path + "/code_backend/.spotify_cache"
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

# mps: 3
def debug_json(jason: dict):
    with open(root_dir_path+"/code_backend/testing/debugging.json", "w") as json_file:
        json.dump(jason, json_file, indent=4)


# mps: 3
def check_upper_limit(limit: int, api_max_limit: int = 50) -> None:
    """
    Checks if the user limit exceeded the API limit.
    :param limit: current limit
    :param api_max_limit: maximum API limit
    :return: raise Exception if API limit exceeded
    """
    if limit > api_max_limit:
        raise Exception(f"Limit of {limit} exceeded API limit of {api_max_limit} per request")


# mps: 3
def check_lower_limit(limit: int, api_min_limit: int = 1) -> None:
    """
    Checks if the user limit subceeded the API limit.
    :param limit: current limit
    :param api_min_limit: minimum API limit
    :return: raise Exception if API limit subceeded
    """
    if limit < api_min_limit:
        raise Exception(f"Limit of {limit} subceeded API limit of {api_min_limit} per request")


# mps: 3
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
    body_data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }

    response = requests.post(url=url, headers=headers, data=body_data)
    with open(root_dir_path+"/code_backend/.spotify_cache", 'w') as token:
        token.write(response.text)


# load token
token_header: dict
request_token()

with open(root_dir_path+"/code_backend/.spotify_cache", "r") as file:
    data = json.load(file)
    # Todo: implement token renewal after ~1h
    token_header = {
        'Authorization': "Bearer " + data["access_token"],
}


# mps: 3
def print_http_error_codes(code: int, message: str = None) -> None:
    """
    Web API uses the following response status codes, as defined in the RFC 2616 and RFC 6585
    Official API Documentation: https://developer.spotify.com/documentation/web-api/concepts/api-calls#response-status-codes
    :param code: HTTP Code of the request response
    :param message: Message of the error
    """
    error_data: dict
    with open(root_dir_path+"/Databases/JSON_Files/http_errors.json", "r") as e_file:
        error_data = json.load(e_file)[str(code)]

    print(f"\n\x1b[31mRequest returned Code: {error_data["code"]} - {error_data["name"]}\n{error_data["explanation"]}\n\x1b[37m{message}\n{TEXTCOLOR}")
    sys.exit(1)


# mps: 0
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
        return print_http_error_codes(response.status_code, json.loads(response.text)["error"]["message"])

    return response.json()


# mps: 1
def get_followed_artists(get_type: str = "artist"):
    """
    Get the current user's followed artists.
    Needed Scopes: user-follow-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-followed
    :param get_type: The ID type: currently only artist is supported.
    :return: Dict containing Spotify Artists, in the form of {artist_uri: artist}
    """

    artists = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/following?type={get_type}&limit=50",
        request_type="GET",
        json_data=None
    )

    tmp = {item["uri"]: item for item in response["artists"]["items"]}
    artists.update(tmp)

    # If there are more than 50 albums:
    total_artists = response["artists"]["total"]

    for current_offset in range(50, total_artists, 50):
        last_id = artists[list(artists.keys())[-1]]["id"]

        response = api_request_data(
            url=f"https://api.spotify.com/v1/me/following?type={get_type}&limit=50&after={last_id}",
            request_type="GET",
            json_data=None
        )
        tmp = {item["uri"]: item for item in response["artists"]["items"]}
        artists.update(tmp)

    return artists



# mps: 1
def get_users_profile(user_id: str):
    """
    Get public profile information about a Spotify user.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-profile
    :param user_id: The user's Spotify user ID.
    :return: Dict containing Spotify Users, in the form of {user_uri: user}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/users/{user_id}",
        request_type="GET",
        json_data=None
    )
    return {response["uri"]: response}


# mps: 1
def get_users_top_items(
        item_type: Literal["artist", "tracks"],
        time_range: Literal["short_term", "medium_term", "long_term"] = "medium_term",
        limit: int = 20
) -> dict:
    """
    Get the current user's top artists or tracks based on calculated affinity.
    Needed Scopes: user-top-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
    :param item_type: The type of entity to return. Valid values: "artists" or "tracks"
    :param time_range: Over what time frame the affinities are computed. Valid values: "long_term" (calculated from ~1 year of data and including all new data as it becomes available), "medium_term" (approximately last 6 months), "short_term" (approximately last 4 weeks). Default: medium_term
    :param limit: The maximum number of items to return. If `limit=None` **all** Top Tracks get returned. Default: 20. Minimum: 1.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    """

    check_lower_limit(
        limit=limit,
        api_min_limit=1
    )

    tracks = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/top/{item_type}?time_range={time_range}&limit={min(50, limit)}&offset=0",
        request_type="GET",
        json_data=None
    )

    tmp = {item["uri"]: item for item in response["items"]}
    tracks.update(tmp)

    # If there are more than 50 albums:
    total_artists = response["total"]

    for current_offset in range(50, min(total_artists,limit), 50):
        response = api_request_data(
        url=f"https://api.spotify.com/v1/me/top/{item_type}?time_range={time_range}&limit=50&offset={current_offset}",
        request_type="GET",
        json_data=None
        )

        tmp = {item["uri"]: item for item in response["items"]}
        tracks.update(tmp)

    return tracks



# mps: 1
def get_current_users_profile():
    """
    Get detailed profile information about the current user (including the current user's username).
    Needed Scopes: user-read-private, user-read-email
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile
    :return: Dict containing Spotify Users, in the form of {user_uri: user}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/me",
        request_type="GET",
        json_data=None
    )
    return {response["uri"]: response}


# mps: 1
def check_users_saved_tracks(check_ids: list[str]) -> dict:
    """
    Check if one or more tracks is already saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/check-users-saved-tracks
    :param check_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Saved Spotify Tracks, in the form of {track_uri: bool}
    """

    tracks = {}

    for current_offset in range(0, len(check_ids), 50):
        encoded_chunk = quote(",".join(check_ids[current_offset: current_offset + 50]))

        response = api_request_data(
            url=f"https://api.spotify.com/v1/me/tracks/contains?ids={encoded_chunk}",
            request_type="GET",
            json_data=None
        )

        for _id, existence in zip(check_ids[current_offset: current_offset + 50], response):
            tracks[f"spotify:track:{_id}"] = existence

    return tracks


# mps: 1
def get_users_saved_tracks(limit: int = 20) -> dict:
    """
    Get a list of the songs saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks
    :param limit: The maximum number of items to return. If `limit=None` **all** Saved Tracks get returned. Default: 20. Minimum: 1.
    :return: Dict containing Saved Spotify Tracks, in the form of {track_uri: track}
    """

    check_lower_limit(
        limit=limit,
        api_min_limit=1
    )

    tracks = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/tracks?market={MARKET}&limit={min(50, limit)}&offset=0",
        request_type="GET",
        json_data=None
    )

    tmp = {item["uri"]: item for item in response["items"]}
    tracks.update(tmp)

    # If there are more than 50 albums:
    total_tracks = response["total"]

    for current_offset in range(50, min(total_tracks, limit), 50):
        response = api_request_data(
            url=f"https://api.spotify.com/v1/me/tracks?market={MARKET}&limit=50&offset={current_offset}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["items"]}
        tracks.update(tmp)

    return tracks


# mps: 1
def get_several_tracks(track_ids: list[str]):
    """
    Get Spotify catalog information for multiple tracks based on their Spotify IDs.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-several-tracks
    :param track_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    """

    tracks = {}

    for current_offset in range(0, len(track_ids), 50):
        encoded_chunk = quote(",".join(track_ids[current_offset: current_offset + 50]))

        response = api_request_data(
            url=f"https://api.spotify.com/v1/tracks?market={MARKET}&ids={encoded_chunk}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["tracks"]}
        tracks.update(tmp)

    return tracks


# mps: 1
def get_track(track_id: str) -> dict:
    """
    Get Spotify catalog information for a single track identified by its unique Spotify ID.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-track
    :param track_id: The Spotify ID for the track.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/tracks/{track_id}?market={MARKET}",
        request_type="GET",
        json_data=None
    )
    return {response["uri"]: response}


# mps: 2
def get_playlist(playlist_id: str) -> dict:
    """
    Get a playlist owned by a Spotify user.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-playlist
    :param playlist_id: The Spotify ID of the playlist.
    :return: Dict containing Spotify Playlists, in the form of {playlist_id: playlist}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}?market={MARKET}",
        request_type="GET",
        json_data=None
    )
    return {response["uri"]: response}


# mps: 1
def change_playlist_details(playlist_id: str, name: str, public: bool, collaborative: bool, description: str) -> None:
    """
    Change a playlist's name and public/private state. (The user must, of course, own the playlist.)
    Needed Scopes: playlist-modify-public, playlist-modify-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/change-playlist-details
    :param playlist_id: The Spotify ID of the playlist.
    :param name: The new name for the playlist, for example "My New Playlist Title"
    :param public: The playlist's public/private status (if it should be added to the user's profile or not): true the playlist will be public, false the playlist will be private, null the playlist status is not relevant. For more about public/private status, see [Working with Playlists](https://developer.spotify.com/documentation/web-api/concepts/playlists)
    :param collaborative: If `true`, the playlist will become collaborative and other users will be able to modify the playlist in their Spotify client. Note: You can only set `collaborative=true` on non-public playlists.
    :param description: Value for playlist description as displayed in Spotify Clients and in the Web API.
    :return: Updates Playlist in App
    """

    json_data = {
        'name': name,
        'description': description,
        'public': public,
        'collaborative': collaborative,
    }

    api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}",
        request_type="PUT",
        json_data=json_data
    )


# mps: 1
def get_playlist_items(playlist_id:str) -> dict:
    """
    Get full details of the items of a playlist owned by a Spotify user.
    Needed Scopes: playlist-read-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks
    :param playlist_id: The Spotify ID of the playlist.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    """
    tracks = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50&offset=0&market={MARKET}",
        request_type="GET",
        json_data=None
    )

    tmp = {item["track"]["uri"]: item["track"] for item in response["items"]}
    tracks.update(tmp)

    # If there are more than 50 albums:
    total_tracks = response["total"]

    for current_offset in range(50, total_tracks, 50):
        response = api_request_data(
            url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50&offset={current_offset}&market={MARKET}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["track"]["uri"]: item["track"] for item in response["items"]}
        tracks.update(tmp)

    if len(tracks) != total_tracks:
        print(f"\n\x1b[31mCould not fetch all Playlist {playlist_id} items{TEXTCOLOR}\nTracks fetched: {len(tracks)}, Tracks in Playlist: {total_tracks}\n")

    return tracks


# mps: 1
def update_playlist_items(playlist_id: str, uris: list[str]) -> None:
    """
    Own implementation to update a Playlist
    Needed Scopes: playlist-read-private, playlist-modify-public, playlist-modify-private
    :param playlist_id: The Spotify ID of the playlist.
    :param uris: A comma-separated list of Spotify URIs to add.
    :return: Updates Playlist in App
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


# mps: 1
def add_items_to_playlist(playlist_id: str, uris: list[str]) -> None:
    """
    Append one or more items to a user's playlist.
    Needed Scopes: playlist-modify-public, playlist-modify-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist
    :param playlist_id: The Spotify ID of the playlist.
    :param uris: A list of Spotify URIs to add, can be track or episode URIs.
    """

    check_lower_limit(
        limit=len(uris),
        api_min_limit=1
    )

    # Note: The position [...] If omitted, the items will be appended to the playlist. [...]
    #  -> no position should work. Otherwise or if position is needed uncomment and update value
    # Additionally, the URIs are in the Body instead of passing numerous item URIs as a query parameter and
    # therefore, avoiding the surpassing of the maximum length of the request URI

    json_data = {
        "uris": uris
        # "position": position
    }


    for current_offset in range(0, len(uris), 100):
        api_request_data(
            url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            request_type="POST",
            json_data=json_data
        )


# mps: 1
def remove_playlist_items(playlist_id: str, track_uris: list[str]) -> None:
    """
    Remove one or more items from a user's playlist (all appearances with these URIs/all Duplicates).
    Needed Scopes: playlist-modify-public, playlist-modify-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/remove-tracks-playlist
    :param playlist_id: The Spotify ID of the playlist.
    :param track_uris: An array of objects containing Spotify URIs of the tracks or episodes to remove.
    """

    check_lower_limit(
        limit=len(track_uris),
        api_min_limit=1
    )

    track_dict = [{"uri": item} for item in track_uris]

    for current_offset in range(0, len(track_uris), 100):
        json_data = {
            'tracks': track_dict[current_offset:current_offset + 100],
        }
        api_request_data(
            url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            request_type="DELETE",
            json_data=json_data
        )

# mps: 1
def get_current_users_playlists(limit: int = 20) -> dict | None:
    """
    Get a list of the playlists owned or followed by the current Spotify user.
    Needed Scopes: playlist-read-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists
    :param limit: The maximum number of items to return.  If `limit=None` **all** Top Playlists get returned. Default: 20. Minimum: 1.
    :return: Dict containing Spotify Playlists, in the form of {playlist_uri: playlist}
    """

    check_lower_limit(
        limit=limit,
        api_min_limit=1
    )

    playlists = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/playlists?limit={min(50, limit)}&offset=0",
        request_type="GET",
        json_data=None
    )

    tmp = {item["uri"]: item for item in response["items"]}
    playlists.update(tmp)

    # If there are more than 50 albums:
    total_playlists = response["total"]

    for current_offset in range(50, min(total_playlists, limit), 50):
        response = api_request_data(
            url=f"https://api.spotify.com/v1/me/playlists?limit=50&offset={current_offset}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["items"]}
        playlists.update(tmp)

    return playlists


# mps: 1
def get_users_playlists(user_id: str, limit: int = 20) -> dict | None:
    """
    Get a list of the playlists owned or followed by a Spotify user.
    Needed Scopes: playlist-read-private, playlist-read-collaborative
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists
    :param user_id: The user's Spotify user ID.
    :param limit: The maximum number of items to return.  If `limit=None` **all** Top Playlists get returned. Default: 20. Minimum: 1.
    :return: Dict containing Spotify Playlists, in the form of {playlist_uri: playlist}
    """

    check_lower_limit(
        limit=limit,
        api_min_limit=1
    )

    playlists = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/users/{user_id}/playlists?limit={min(50, limit)}&offset=0",
        request_type="GET",
        json_data=None
    )

    tmp = {item["uri"]: item for item in response["items"]}
    playlists.update(tmp)

    # If there are more than 50 albums:
    total_playlists = response["total"]

    for current_offset in range(50, min(total_playlists, limit), 50):
        response = api_request_data(
            url=f"https://api.spotify.com/v1/users/{user_id}/playlists?limit=50&offset={current_offset}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["items"]}
        playlists.update(tmp)

    return playlists


# mps: 1
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
    :return: Dict containing Spotify Playlists, in the form of {playlist_uri: playlist}
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


# mps: 1
def get_playlist_cover_image(playlist_id: str) -> Image:
    """
    Get the current image associated with a specific playlist.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-playlist-cover
    :param playlist_id: The Spotify ID of the playlist.
    :return: Playlist Cover Image loaded as Pillow Image
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        request_type="GET",
        json_data=None
    )
    return image_from_url(response[0]["url"])


# mps: 1
def add_custom_playlist_cover_image(playlist_id: str, b64_image: str) -> None:
    """
    Replace the image used to represent a specific playlist.
    Needed Scopes: ugc-image-upload, playlist-modify-private, playlist-modify-public
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/upload-custom-playlist-cover
    :param playlist_id: The Spotify ID of the playlist.
    :param b64_image: Base64 encoded JPEG image data, maximum payload size is 256 KB.
    :return: Updates Playlist in App
    """

    api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        request_type="PUT",
        json_data=b64_image,
        overwrite_header={
            'Authorization': f'Bearer {data["access_token"]}',
            'Content-Type': "image/jpeg"
        }
    )


# mps: 1
def get_artist(artist_id: str) -> dict | None:
    """
    Get Spotify catalog information for a single artist identified by their unique Spotify ID.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-artist
    :param artist_id: The Spotify ID of the artist.
    :return: Dict containing Spotify Artists, in the form of {artist_uri: artist}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{artist_id}",
        request_type="GET",
        json_data=None
    )

    return {response["uri"]: response}


# mps: 1
def get_several_artists(artist_ids: list[str]) -> dict | None:
    """
    Get Spotify catalog information for several artists based on their Spotify IDs.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists
    :param artist_ids: A comma-separated list of the Spotify IDs for the artists.
    :return: Dict containing Spotify Artists, in the form of {artist_uri: artist}
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


# mps: 1
def get_artists_albums(album_id: str, limit: int = 20) -> dict:
    """
    Get Spotify catalog information about an artist's albums.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums
    :param album_id: The Spotify ID of the album.
    :param limit: The maximum number of items to return.
    :return: Dict containing Spotify Albums, in the form of {album_uri: album}
    """

    check_lower_limit(
        limit=limit,
        api_min_limit=1
    )

    albums = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{album_id}/albums?market={MARKET}&limit={min(50, limit)}&offset=0",
        request_type="GET",
        json_data=None
    )

    tmp = {item["uri"]: item for item in response["items"]}
    albums.update(tmp)

    # If there are more than 50 albums:
    total_albums = response["total"]

    for current_offset in range(50, min(total_albums, limit), 50):
        response = api_request_data(
            url=f"https://api.spotify.com/v1/artists/{album_id}/albums?market={MARKET}&limit=50&offset={current_offset}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["items"]}
        albums.update(tmp)

    return albums


# mps: 1
def get_artists_top_tracks(artist_id: str) -> dict:
    """
    Get Spotify catalog information about an artist's top tracks by country.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks
    :param artist_id: The Spotify ID of the artist.
    :return: Dict containing Spotify Artists, in the form of {artist_uri: artist}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market={MARKET}",
        request_type="GET",
        json_data=None
    )

    return {item["uri"]: item for item in response["tracks"]}


# mps: 1
def check_users_saved_albums(album_ids: list[str]) -> dict:
    """
    Check if one or more albums is already saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/check-users-saved-albums
    :param album_ids: A comma-separated list of the Spotify IDs for the albums. Maximum: 20 IDs.
    :return: Dict containing Saved Spotify Albums, in the form of {album_uri: exists?}
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


# mps: 1
def get_album_tracks(album_id: str) -> dict:
    """
    Get Spotify catalog information about an album’s tracks. Optional parameters can be used to limit the number of tracks returned.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks
    :param album_id: The Spotify ID of the album.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
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


# mps: 1
def get_several_albums(album_ids: list[str]) -> dict:
    """
    Get Spotify catalog information for multiple albums identified by their Spotify IDs.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-multiple-albums
    :param album_ids: A comma-separated list of the Spotify IDs for the albums.
    :return: Dict containing Spotify Albums, in the form of {album_uri: album}
    """

    albums = {}
    for current_chunk in range(0, len(album_ids), 20):
        encoded_chunk = quote(",".join(album_ids[current_chunk: current_chunk + 20]))
        response = api_request_data(
            url=f"https://api.spotify.com/v1/albums?ids={encoded_chunk}&market={MARKET}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["artists"]}
        albums.update(tmp)

    return albums


# mps: 1
def get_album(album_id: str) -> dict:
    """
    Get Spotify catalog information for a single album.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-album
    :param album_id: The Spotify ID of the album.
    :return: Dict containing Spotify Albums, in the form of {album_uri: album}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/albums/{album_id}?market={MARKET}",
        request_type="GET",
        json_data=None
    )

    return {response["uri"]: response}


# mps: 1
def get_users_saved_albums() -> dict | None:
    """
    Get a list of the albums saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-saved-albums
    :return: Dict containing Saved Spotify Albums, in the form of {album_uri: album}
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
    test_album_id = "79fnwKynD56xIXBVWkyaE5"
    test_album_uri = "spotify:album:79fnwKynD56xIXBVWkyaE5"
    test_album_ids = ["79fnwKynD56xIXBVWkyaE5", "7CI6R1kJLUMfBl4FOKP8nc"]
    test_artist_id = "6XyY86QOPPrYVGvF9ch6wz"
    test_artist_ids = ["6XyY86QOPPrYVGvF9ch6wz", "00YTqRClk82aMchQQpYMd5"]
    test_playlist_id = "6bRkO7PLCXgmV4EJH52iU4"
    test_playlist_uri = "spotify:playlist:6bRkO7PLCXgmV4EJH52iU4"
    test_track_id = "14FP9BNWHekbC17tqcppOR"
    test_track_uri = "spotify:track:14FP9BNWHekbC17tqcppOR"
    test_track_uris = ["spotify:track:6zrR8itT7IfAdl5aS7YQyt", "spotify:track:14FP9BNWHekbC17tqcppOR"]
    test_track_ids = ["6zrR8itT7IfAdl5aS7YQyt", "14FP9BNWHekbC17tqcppOR"]
    test_user_id = "simonluca1"
    test_limit = 2
    test_offset = 0

    # if not items:
    #     print(f"\n\x1b[31mWhat the fuck just happened? looks like you need to debug smth... xD{TEXTCOLOR}")
    #     sys.exit(1)
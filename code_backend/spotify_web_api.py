"""
    Implementation of the Spotify Web API to fit project purpose
"""
import requests

from code_backend.secondary_methods import (
    check_limits, check_token_expired, image_from_url,
    print_http_error_codes, print_error, update_env_key,
    absolute_path
)
from code_backend.shared_config import *


# Note: Curl-to-... Converter:
#  https://curlconverter.com/python/

# Note: some methods can still have bugs depending on usage

# mps: 3
def request_regular_token() -> None:
    """
    Request an access token, using the Authorization Code Flow tutorial and cache it in the .env file. If Spotify credentials are found in .env file, the script runs the login automated. Else User interaction is needed.
    Official API Documentation: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
    :return: caches token in .env
    """

    app = Flask(__name__)

    def generate_random_string(length):
        """Generate a random string of fixed length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @app.route('/login')
    def login():
        state = generate_random_string(16)

        query_params = {
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'scope': SCOPES,
            'redirect_uri': REDIRECT_URI,
            'state': state
        }

        auth_url = 'https://accounts.spotify.com/authorize?' + urlencode(query_params)
        return redirect(auth_url)

    # @app.route('/')
    @app.route('/callback')
    def callback():
        # Extract the 'code' and 'state' parameters from the URL
        code = request.args.get('code')
        state = request.args.get('state')

        if state is None:
            error_query = urlencode({'error': 'state_mismatch'})
            return redirect(f'/#{error_query}')

        # Prepare the request for token exchange
        token_url = 'https://accounts.spotify.com/api/token'
        auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {auth_header}'
        }
        data = {
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }

        # Exchange the authorization code for an access token
        response = requests.post(token_url, headers=headers, data=data)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return f"Error: {response.text}", response.status_code

    def run_flask_app():
        """Run Flask app in a separate thread."""
        app.run(port=8080, debug=True, use_reloader=False)

    def automated_request_handling(use_credentials=False):
        """
        Request a new Access Token from spotify
        :param use_credentials: True: use credentials inside .env file to be logged in automatically; False: log-in manually
        :return:
        """
        wait_timeout = 120 # seconds

        driver = webdriver.Firefox()
        driver.implicitly_wait(WAIT_TIME)
        try:
            driver.get("http://localhost:8080/login")
            if use_credentials:
                driver.find_element("id", "login-username").send_keys(SPOTIFY_USERNAME)
                driver.find_element("id", "login-password").send_keys(SPOTIFY_PASSWORD)
                driver.find_element("id", "login-button").click()


            # else: login manually while script waits up to 2 min
            WebDriverWait(driver, wait_timeout).until(
                lambda d: d.current_url.startswith("http://localhost:8080/?code=")
            )

            raw_data_tab = driver.find_element(By.ID, 'rawdata-tab')
            raw_data_tab.click()

            # Allow time for content to load
            time.sleep(1)

            # Locate the content within the "Raw Data" panel
            token_data = json.loads(driver.find_element(By.TAG_NAME, 'pre').text)
            relevant_data = {
                'access_token': token_data['access_token'],
                'token_type': 'Bearer',
                'expires': int(time.time()) + token_data['expires_in']
            }
            update_env_key("REGULAR_TOKEN", json.dumps(relevant_data))
            update_env_key("REFRESH_TOKEN", json.dumps({"refresh_token": token_data['refresh_token']}))
            update_env_key("AUTHORIZED_SCOPES", json.dumps({"scope": token_data['scope']}))

        except TimeoutException:
            print_error(
                error_message="TimeoutException: The timeout occurred while trying to login.",
                more_infos="Either the credentials are incorrect or the user has not logged in. \n  - Check your credentials in .env (if stored there)\n  - if script aborted before finishing to enter credentials increment wait_timeout",
                exit_code=1
            )

        except Exception as error:
            print_error(
                error_message=error,
                more_infos=None,
                exit_code=1
            )

        finally:
            driver.close()

    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Give Flask a moment to start
    time.sleep(1)

    # Run Selenium in the main thread
    automated_request_handling(use_credentials=(len(SPOTIFY_USERNAME) > 0 and len(SPOTIFY_PASSWORD) > 0))

# mps: 3
def refresh_access_token():
    """
    A refresh token is a security credential that allows client applications to obtain new access tokens without requiring users to reauthorize the application.
    Access tokens are intentionally configured to have a limited lifespan (1 hour), at the end of which, new tokens can be obtained by providing the original refresh token acquired during the authorization token request response.
    Official Documentation: https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens
    :return: update REGULAR_TOKEN (and AUTHORIZED_SCOPES) in .env
    """

    # Check Scope equality with sets
    config_scope_set = set(SCOPES.split(" "))
    env_scope_set = set(json.loads(os.getenv('AUTHORIZED_SCOPES'))["scope"].split(" "))

    if config_scope_set != env_scope_set:
        print(CORANGE+"Scope changed since the last authorization of an access token.\nReauthorizing access token..."+TEXTCOLOR)
        return request_regular_token()

    elif os.getenv('REFRESH_TOKEN') is None:
        print(CORANGE+"Refresh token was not obtained.\nReauthorizing access token..."+TEXTCOLOR)
        return request_regular_token()

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}"
    }
    form = {
        'grant_type': 'refresh_token',
        'refresh_token': json.loads(os.getenv("REFRESH_TOKEN"))['refresh_token']
    }

    response = requests.post(
        url=url,
        headers=headers,
        data=form,
        json=True
    )

    # Error handling according to Spotify's Error Codes
    if response.status_code not in [200, 201, 202, 204]:
        try:
            return print_http_error_codes(
                code=response.status_code,
                message=json.loads(response.text),
                causing_query=requests.Request(method="POST", url=url, headers=headers, data=form)
            )
        except json.decoder.JSONDecodeError:
            print(CORANGE + "print_http_error_codes() Error:" + TEXTCOLOR)
            print(f"{CORANGE}Response Code:{TEXTCOLOR} {response.status_code}")
            print(f"{CORANGE}Response as Bytes:{TEXTCOLOR} {response.content}")
            print(f"{CORANGE}Response as String:{TEXTCOLOR} {response.text}")

    if len(response.content) == 0:
        return None
    else:
        try:
            refresh_token_data = response.json()

            # update access token
            new_regular_token = {
                "access_token": refresh_token_data.get('access_token', ""),
                "token_type": "Bearer",
                "expires": int(time.time()) + refresh_token_data.get('expires_in', 0)
            }
            update_env_key('REGULAR_TOKEN', json.dumps(new_regular_token))

            # only update if new Refresh Token is part of Response, When a refresh token is not returned, continue using the existing token
            if refresh_token_data.get('refresh_token', None):
                new_refresh_token = {"refresh_token": refresh_token_data.get('refresh_token', None)}
                update_env_key('REFRESH_TOKEN', json.dumps(new_refresh_token))

            # for debug
            # return refresh_token_data

        except Exception as error:
            print(f"{CORANGE}Response Length:{TEXTCOLOR}{len(response.text)}")
            print(f"{CORANGE}Response Content:\n{TEXTCOLOR}{response.text}")
            print(f"\n{CRED}{error}\n{TEXTCOLOR}")


# mps: 3
def request_extended_token() -> bool:
    """
    Using https://www.chosic.com/spotify-playlist-analyzer/ to request temporary extended-token, that can be used to request Web API Data. After 1 hour a new token needs to be requested.
    This implementation extracts the Spotify Web API token after one default request out of the local Storage value `plAnalyzerToken` (hopefully not violating Terms of Services).
    :return: temporary token
    """
    driver = webdriver.Firefox()
    driver.implicitly_wait(WAIT_TIME)
    try:
        driver.get("https://www.chosic.com/spotify-playlist-analyzer/")

        elem = driver.find_element(By.NAME, "q")
        elem.clear()
        elem.send_keys("https://open.spotify.com/playlist/3cEYpjA9oz9GiPac4AsH4n")
        elem.send_keys(Keys.RETURN)

        time.sleep(WAIT_TIME)

        # extracting Token from Driver Storage
        token_data = json.loads(driver.execute_script(f"return localStorage;")["plAnalyzerToken"])
        relevant_data ={
            'access_token': token_data['token'],
            'token_type': 'Bearer',
            'expires': token_data['expires']
        }
        update_env_key("EXTENDED_TOKEN", json.dumps(relevant_data))

        driver.close()
        return True

    except Exception as error:
        print_error(
            error_message=str(error),
            more_infos=None,
            exit_code=None
        )
        driver.close()
        return False


# mps: 3
def api_request_data(url: str, request_type: Literal["GET", "POST", "DELETE", "PUT"], json_data: dict | str = None, overwrite_header: dict = None) -> dict | list | None:
    """
    Transferring data from or to a server using Curl commands via [requests](https://docs.python-requests.org/en/latest/index.html). Currently supported HTTP regular_api_methods are `GET`, `POST`, `PUT` and `DELETE` (This implementation is designed for Spotify API requests)
    :param url: url to curl from/to
    :param request_type: HTTP request method
    :param json_data: JSON data to send
    :param overwrite_header: Specific headers to overwrite default headers
    :return: JSON data fetched from Spotify API
    """

    if check_token_expired(extended_token=False) == 0:
        refresh_access_token()

    # HTTP Headers needed for Spotify API requests
    if overwrite_header:
        headers = overwrite_header
    else:
        headers = {
            # If the extended Token is needed, this gets overwritten (case above)
            'Authorization': "Bearer " + json.loads(os.getenv("REGULAR_TOKEN"))["access_token"]
        }
        if json_data:
            headers['Content-Type'] = 'application/json'

    # print(headers)
    match request_type:
        case "GET":
            query = requests.Request(method="GET", url=url, headers=headers, json=json_data)
            response = requests.get(
                url=url,
                headers=headers,
                json=json_data
            )
        case "POST":
            query = requests.Request(method="POST", url=url, headers=headers, json=json_data)
            response = requests.post(
                url=url,
                headers=headers,
                json=json_data
            )

        case "DELETE":
            query = requests.Request(method="DELETE", url=url, headers=headers, json=json_data)
            response = requests.delete(
                url=url,
                headers=headers,
                json=json_data
            )

        case "PUT":
            query = requests.Request(method="PUT", url=url, headers=headers, json=json_data)
            response = requests.put(
                url=url,
                headers=headers,
                data=json_data
            )

        case _:
            raise f"{request_type} not supported"

    if response.status_code not in [200, 201, 202, 204]:
        try:
            return print_http_error_codes(
                code=response.status_code,
                message=json.loads(response.text),
                causing_query=query
            )
        except (json.decoder.JSONDecodeError):
            print(CORANGE+"print_http_error_codes() Error:"+TEXTCOLOR)
            print(f"{CORANGE}Response Code:{TEXTCOLOR} {response.status_code}")
            print(f"{CORANGE}Response as Bytes:{TEXTCOLOR} {response.content}")
            print(f"{CORANGE}Response as String:{TEXTCOLOR} {response.text}")

    if len(response.content) == 0:
        return None
    else:
        try:
            return response.json()

        except Exception as error:
            print(f"{CORANGE}Response Length:{TEXTCOLOR}{len(response.text)}")
            print(f"{CORANGE}Response Content:\n{TEXTCOLOR}{response.text}")
            print(f"\n{CRED}{error}\n{TEXTCOLOR}")


# <-- Begin Spotify Album Methods -->
# mps: 3
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


# mps: 3
def get_several_albums(album_ids: list[str]) -> dict | None:
    """
    Get Spotify catalog information for multiple albums identified by their Spotify IDs.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-multiple-albums
    :param album_ids: A comma-separated list of the Spotify IDs for the albums.
    :return: Dict containing Spotify Albums, in the form of {album_uri: album}
    """

    if check_limits(limit=len(album_ids)) == 1:
        return None

    albums = {}
    for current_chunk in range(0, len(album_ids), 20):
        encoded_chunk = quote(",".join(album_ids[current_chunk: current_chunk + 20]))
        response = api_request_data(
            url=f"https://api.spotify.com/v1/albums?ids={encoded_chunk}&market={MARKET}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["albums"]}
        albums.update(tmp)

    return albums


# mps: 3
def get_album_tracks(album_id: str, get_duration: bool = False) -> dict | tuple[dict, int]:
    """
    Get Spotify catalog information about an album’s tracks. Optional parameters can be used to limit the number of tracks returned.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks
    :param album_id: The Spotify ID of the album.
    :param get_duration: If to get the Playlist duration in seconds. Default: False.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track} (and optional the duration as second param)
    """

    track_dicts = {}

    # Get first (up to) 50 tracks
    response = api_request_data(
        url=f"https://api.spotify.com/v1/albums/{album_id}/tracks?market={MARKET}&limit=50&offset=0",
        request_type="GET",
        json_data=None
    )

    tmp = {item["uri"]: item for item in response["items"]}
    track_dicts.update(tmp)

    # If there are more than 50 albums:
    total_albums = response["total"]
    current_offset = 50

    while current_offset < total_albums:
        response = api_request_data(
            url=f"https://api.spotify.com/v1/albums/{album_id}/tracks?market={MARKET}&limit=50&offset={current_offset}",
            request_type="GET",
            json_data=None
        )
        tmp = {item["uri"]: item for item in response["items"]}
        track_dicts.update(tmp)

        current_offset += 50

    if get_duration:
        duration = sum([int(current_track["duration_ms"]) for current_track in track_dicts.values()])
        return track_dicts, duration

    return track_dicts


# mps: 3
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


# mps: 3
def check_users_saved_albums(album_ids: list[str]) -> dict | None:
    """
    Check if one or more albums is already saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/check-users-saved-albums
    :param album_ids: A comma-separated list of the Spotify IDs for the albums. Maximum: 20 IDs.
    :return: Dict containing if Spotify Albums are saved by User, in the form of {album_uri: exists?}
    """

    if check_limits(limit=len(album_ids)) == 1:
        return None

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


# <-- Begin Spotify Artist Methods -->
# mps: 3
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


# mps: 3
def get_several_artists(artist_ids: list[str]) -> dict | None:
    """
    Get Spotify catalog information for several artists based on their Spotify IDs.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists
    :param artist_ids: A comma-separated list of the Spotify IDs for the artists.
    :return: Dict containing Spotify Artists, in the form of {artist_uri: artist}
    """

    if check_limits(limit=len(artist_ids)) == 1:
        return None

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


# mps: 3
def get_artists_albums(artist_id: str, limit: int = 20) -> dict | None:
    """
    Get Spotify catalog information about an artist's albums.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums
    :param artist_id: The Spotify ID of the artist.
    :param limit: The maximum number of items to return.
    :return: Dict containing Spotify Albums, in the form of {album_uri: album}
    """

    if check_limits(limit=limit) == 1:
        return None

    albums = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{artist_id}/albums?market={MARKET}&limit={min(50, limit)}&offset=0",
        request_type="GET",
        json_data=None
    )

    tmp = {item["uri"]: item for item in response["items"]}
    albums.update(tmp)

    # If there are more than 50 albums:
    total_albums = response["total"]

    for current_offset in range(50, min(total_albums, limit), 50):
        response = api_request_data(
            url=f"https://api.spotify.com/v1/artists/{artist_id}/albums?market={MARKET}&limit=50&offset={current_offset}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["items"]}
        albums.update(tmp)

    return albums


# mps: 3
def get_artists_top_tracks(artist_id: str) -> dict | None:
    """
    Get Spotify catalog information about an artist's top tracks by country.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks
    :param artist_id: The Spotify ID of the artist.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market={MARKET}",
        request_type="GET",
        json_data=None
    )

    return {item["uri"]: item for item in response["tracks"]}


# <-- Begin Spotify Playlist Methods -->
# mps: 3
def get_playlist(playlist_id: str) -> dict | None:
    """
    Get a playlist owned by a Spotify user.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-playlist
    :param playlist_id: The Spotify ID of the playlist.
    :return: Dict containing Spotify Playlists, in the form of {playlist_id: playlist}
    """
    # Note: it could be that private playlists create errors

    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}?market={MARKET}",
        request_type="GET",
        json_data=None
    )
    return {response["uri"]: response}


# mps: 3
def get_several_playlists(playlist_ids: list) -> dict | None:
    """
    Get Spotify catalog information for multiple playlists based on their Spotify IDs.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-several-tracks
    :param playlist_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    """

    if check_limits(limit=len(playlist_ids)) == 1:
        return None

    playlists = {}
    # Warning: Does not use API optimization, because there is no Web API method for this by Spotify
    #   If HTTP Error 429 occurs multiple times set time.sleep(X) between the iterations
    for current_playlist_id in playlist_ids:
        current_playlist = get_playlist(playlist_id=current_playlist_id)
        playlists.update(current_playlist)
        # time.sleep(X)

    return playlists

# mps: 3
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


# mps: 3
def get_playlist_items(playlist_id: str, get_duration: bool = False) -> dict | tuple[dict, int] | None:
    """
    Get full details of the items of a playlist owned by a Spotify user.
    Needed Scopes: playlist-read-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks
    :param playlist_id: The Spotify ID of the playlist.
    :param get_duration: If to get the Playlist duration in seconds. Default: False.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track} (and optional the duration as second param)
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
        print_error(
            error_message=f"Could not fetch all Playlist {playlist_id} items",
            more_infos=f"Tracks fetched: {len(tracks)}, Tracks in Playlist: {total_tracks}; This can be due to duplicates in the Playlist.",
            exit_code=None
        )

    if get_duration:
        duration = sum([int(current_track["duration_ms"]) for current_track in tracks.values()])
        return tracks, duration

    return tracks


# mps: 3
def update_playlist_items(playlist_id: str, uris: list[str]) -> None:
    """
    Own implementation to update a Playlist
    Needed Scopes: playlist-read-private, playlist-modify-public, playlist-modify-private
    :param playlist_id: The Spotify ID of the playlist.
    :param uris: A comma-separated list of Spotify URIs to add.
    :return: Updates Playlist in App
    """

    if check_limits(limit=len(uris)) == 1:
        return None

    # Fetch and remove current Tracks
    items = get_playlist_items(playlist_id=playlist_id)
    if len(items) > 0:
        remove_playlist_items(
            playlist_id=playlist_id,
            track_uris=list(items.keys())
        )
    # Add new items
    add_items_to_playlist(
        playlist_id=playlist_id,
        uris=uris
    )


# mps: 3
def add_items_to_playlist(playlist_id: str, uris: list[str]) -> None:
    """
    Append one or more items to a user's playlist.
    Needed Scopes: playlist-modify-public, playlist-modify-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist
    :param playlist_id: The Spotify ID of the playlist.
    :param uris: A list of Spotify URIs to add, can be track or episode URIs.
    :return: Updates Playlist in App
    """

    if check_limits(limit=len(uris)) == 1:
        return None

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


# mps: 3
def remove_playlist_items(playlist_id: str, track_uris: list[str]) -> None:
    """
    Remove one or more items from a user's playlist (all appearances with these URIs/all Duplicates).
    Needed Scopes: playlist-modify-public, playlist-modify-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/remove-tracks-playlist
    :param playlist_id: The Spotify ID of the playlist.
    :param track_uris: An array of objects containing Spotify URIs of the tracks or episodes to remove.
    :return: Updates Playlist in App
    """

    if check_limits(limit=len(track_uris)) == 1:
        return None

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


# mps: 3
def get_current_users_playlists(limit: int = 20) -> dict | None:
    """
    Get a list of the playlists owned or followed by the current Spotify user.
    Needed Scopes: playlist-read-private
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists
    :param limit: The maximum number of items to return.  If `limit=None` **all** Top Playlists get returned. Default: 20. Minimum: 1.
    :return: Dict containing Spotify Playlists, in the form of {playlist_uri: playlist}
    """

    if check_limits(limit=limit) == 1:
        return None

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


# mps: 3
def get_users_playlists(user_id: str, limit: int | None = 20) -> dict | None:
    """
    Get a list of the playlists owned or followed by a Spotify user.
    Needed Scopes: playlist-read-private, playlist-read-collaborative
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists
    :param user_id: The user's Spotify user ID.
    :param limit: The maximum number of items to return.  If `limit=None` **all** Top Playlists get returned. Default: 20. Minimum: 1.
    :return: Dict containing Spotify Playlists, in the form of {playlist_uri: playlist}
    """

    if limit is None:
        limit = 51

    if check_limits(limit=limit) == 1:
        return None

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


# mps: 3
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


# mps: 3
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


# mps: 3
def add_custom_playlist_cover_image(playlist_id: str, b64_image: str) -> None:
    """
    Replace the image used to represent a specific playlist.
    Needed Scopes: ugc-image-upload, playlist-modify-private, playlist-modify-public
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/upload-custom-playlist-cover
    :param playlist_id: The Spotify ID of the playlist.
    :param b64_image: Base64 encoded JPEG image data, maximum payload size is 256 KB.
    :return: Updates Playlist in App
    """
    # Todo: continue here
    if check_token_expired(extended_token=False) == 0:
        request_regular_token()

    header = {
        'Authorization': "Bearer " + json.loads(os.getenv("REGULAR_TOKEN"))["access_token"],
        'Content-Type': "image/jpeg"
    }

    api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        request_type="PUT",
        json_data=b64_image,
        overwrite_header=header
    )


# <-- Begin Spotify Track Methods -->
# mps: 3
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


# mps: 3
def get_several_tracks(track_ids: list[str]) -> dict | None:
    """
    Get Spotify catalog information for multiple tracks based on their Spotify IDs.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-several-tracks
    :param track_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    """

    if check_limits(limit=len(track_ids)) == 1:
        return None

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


# mps: 3
def get_users_saved_tracks(limit: int = 20) -> dict | None:
    """
    Get a list of the songs saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks
    :param limit: The maximum number of items to return. If `limit=None` **all** Saved Tracks get returned. Default: 20. Minimum: 1.
    :return: Dict containing Saved Spotify Tracks, in the form of {track_uri: track}
    """

    if check_limits(limit=limit) == 1:
        return None

    tracks = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/tracks?market={MARKET}&limit={min(50, limit)}&offset=0",
        request_type="GET",
        json_data=None
    )

    tmp = {item["track"]["uri"]: item["track"] for item in response["items"]}
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


# mps: 3
def check_users_saved_tracks(check_ids: list[str]) -> dict | None:
    """
    Check if one or more tracks is already saved in the current Spotify user's 'Your Music' library.
    Needed Scopes: user-library-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/check-users-saved-tracks
    :param check_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Saved Spotify Tracks, in the form of {track_uri: bool}
    """

    if check_limits(limit=len(check_ids)) == 1:
        return None


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


# mps: 3
def get_tracks_audio_features(track_id: str):
    """
    Get audio feature information for a single track identified by its unique Spotify ID.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-audio-features
    :param track_id: The Spotify ID for the track.
    :return: Dict containing Audio Features, in the form of {track_uri: audio_features}
    """
    header = {'Authorization': "Bearer " + json.loads(os.getenv("EXTENDED_TOKEN"))["access_token"]}
    response = api_request_data(
        url=f"https://api.spotify.com/v1/audio-features/{track_id}",
        request_type="GET",
        overwrite_header=header
    )
    return {response["uri"]: response}


# mps: 3
def get_several_tracks_audio_features(track_ids: list[str]) -> dict | None:
    """
    Get audio features for multiple tracks based on their Spotify IDs.
    Needed Scopes: None
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features
    :param track_ids: A comma-separated list of the Spotify IDs for the tracks.
    :return: Dict containing Audio Features, in the form of {track_uri: audio_features}
    """

    if check_limits(limit=len(track_ids)) == 1:
        return None


    header = {'Authorization': "Bearer " + json.loads(os.getenv("EXTENDED_TOKEN"))["access_token"]}
    audio_features = {}

    for current_offset in range(0, len(track_ids), 100):
        encoded_chunk = quote(",".join(track_ids[current_offset: current_offset + 100]))

        response = api_request_data(
            url=f"https://api.spotify.com/v1/audio-features?ids={encoded_chunk}",
            request_type="GET",
            json_data=None,
            overwrite_header=header
        )

        tmp = {item["uri"]: item for item in response["audio_features"]}
        audio_features.update(tmp)

    return audio_features


# <-- Begin Spotify User Methods -->
# mps: 3
def get_current_users_profile() -> dict:
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


# mps: 3
def get_users_top_items(
        item_type: Literal["artists", "tracks"],
        time_range: Literal["short_term", "medium_term", "long_term"] = "medium_term",
        limit: int = 20
) -> dict | None:
    """
    Get the current user's top artists or tracks based on calculated affinity.
    Needed Scopes: user-top-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
    :param item_type: The type of entity to return. Valid values: "artists" or "tracks"
    :param time_range: Over what time frame the affinities are computed. Valid values: "long_term" (calculated from ~1 year of data and including all new data as it becomes available), "medium_term" (approximately last 6 months), "short_term" (approximately last 4 weeks). Default: medium_term
    :param limit: The maximum number of items to return. If `limit=None` **all** Top Tracks get returned. Default: 20. Minimum: 1.
    :return: Dict containing Spotify Tracks, in the form of {user_uri: user}
    """

    if check_limits(limit=limit) == 1:
        return None

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


# mps: 3
def get_users_profile(user_id: str) -> dict:
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


# mps: 3
def get_several_users(user_ids: list) -> dict | None:
    """
    Get Spotify catalog information for multiple user based on their Spotify IDs.
    Needed Scopes: None
    :param user_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Spotify User, in the form of {user_uri: user}
    """

    if check_limits(limit=len(user_ids)) == 1:
        return None

    users = {}

    # Warning: Does not use API optimization, because there is no Web API method for this by Spotify
    #   If HTTP Error 429 occurs multiple times set time.sleep(X) between the iterations
    for current_user_id in user_ids:
        current_playlist = get_users_profile(user_id=current_user_id)
        users.update(current_playlist)
        # time.sleep(X)

    return users


# mps: 3
def get_followed_artists(get_type: str = "artist") -> dict | None:
    """
    Get the current user's followed artists.
    Needed Scopes: user-follow-read
    Official API Documentation: https://developer.spotify.com/documentation/web-api/reference/get-followed
    :param get_type: The ID type: currently only artist is supported.
    :return: Dict containing Spotify Artists, in the form of {artist_uri: artist}
    """

    if get_type != "artist":
        return print_error(
            error_message="The ID type: currently only artist is supported."
        )

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


if __name__ == '__main__':
    """"""

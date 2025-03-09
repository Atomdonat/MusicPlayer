"""
    Implementation of the Spotify Web API to fit project purpose
"""
import json
from types import NoneType

from selenium.common import WebDriverException

from code_backend.shared_config import *
from code_backend.secondary_methods import (
    check_limits, check_token_expired, value_from_dict,
    update_env_key, image_from_url, print_debug,
    absolute_path, remove_key_recursively, json_to_file,
    check_spotify_id, check_spotify_ids, check_spotify_uri, check_spotify_uris,
    get_invalid_spotify_ids, get_invalid_spotify_uris, check_spotify_user_ids, uri_to_id, url_to_uri
)
from code_backend.exceptions import (
    HttpException, RequestException, CustomException, InputException,
    SpotifyIdException, SpotifyUriException, LimitException
)


# Note: Curl-to-... Converter:
#  https://curlconverter.com/python/

# Note: some methods can still have bugs depending on usage


def request_regular_token(use_credentials: bool = False, force_new_token: bool = False) -> None:
    """
    Request an access token, using the Authorization Code Flow tutorial and cache it in the .env file. If Spotify credentials are found in .env file, the script runs the login automated. Else User interaction is needed.
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/tutorials/code-flow

    **Note:** using credentials can lead to some API requests returning the http error code 500

    :param use_credentials: True: use credentials inside .env file to be logged in automatically; False: log-in manually
    :param force_new_token: Whether to force a new access token (e.g. if env key has not been set yet)
    :return: caches token in .env
    :raises CustomException: If Exception occurs
    :raises InputException: if input is invalid
    """

    if not isinstance(force_new_token, bool):
        raise InputException(item_value=force_new_token, valid_values=(True, False), valid_types=bool)

    if not force_new_token and len(os.getenv("REGULAR_TOKEN")) > 0:
        return refresh_access_token()

    if not isinstance(use_credentials, bool):
        raise InputException(item_value=use_credentials, valid_values=(True, False), valid_types=bool)

    if not use_credentials and not (len(SPOTIFY_USERNAME) > 0 and len(SPOTIFY_PASSWORD) > 0):
        raise CustomException(
            error_message="No credentials provided",
            more_infos="Check your credentials in .env (if stored there)"
        )

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

    def automated_request_handling():
        """
        Request a new Access Token from spotify

        :return:
        :raises CustomException: If Exception occurs
        """
        wait_timeout = 120  # seconds

        driver = webdriver.Firefox()
        driver.implicitly_wait(WAIT_TIME)
        try:
            driver.get("http://localhost:8080/login")
        except WebDriverException as error:
            raise CustomException(error_message=error, more_infos="Exception occurred while starting selenium on 'http://localhost:8080/login'")

        if use_credentials:
            try:
                driver.find_element("id", "login-username").send_keys(SPOTIFY_USERNAME)
                driver.find_element("id", "login-password").send_keys(SPOTIFY_PASSWORD)
                driver.find_element("id", "login-button").click()
            except NoSuchElementException as error:
                # can occur if f.e. requested too many access tokens in a short period of time => Spotify requests 2FA on login (no password element)
                raise CustomException(
                    error_message=error,
                    more_infos="Exception occurred because Selenium could not find all elements 'login-username', 'login-password', 'login-button'"
                )

        try:
            # else: login manually while script waits up to 2 min
            WebDriverWait(driver, wait_timeout).until(
                lambda d: d.current_url.startswith("http://localhost:8080/callback?code=")
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

        except TimeoutException as error:
            CustomException(
                error_message=error,
                more_infos="Either the credentials are incorrect or the user has not logged in. \n  - Check your credentials in .env (if stored there)\n  - if script aborted before finishing to enter credentials increment wait_timeout"
            )

        except Exception as error:
            CustomException(
                error_message=error
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
    automated_request_handling()


def refresh_access_token():
    """
    A refresh token is a security credential that allows client applications to obtain new access tokens without requiring users to reauthorize the application.
    Access tokens are intentionally configured to have a limited lifespan (1 hour), at the end of which, new tokens can be obtained by providing the original refresh token acquired during the authorization token request response.
    Official Documentation: https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens

    :return: update REGULAR_TOKEN (and AUTHORIZED_SCOPES) in .env
    :raises HttpException: if request response code is not good
    :raises CustomException: If Exception occurs

    """

    # Check Scope equality with sets
    config_scope_set = set(SCOPES.split(" "))
    env_scope_set = set(json.loads(os.getenv('AUTHORIZED_SCOPES'))["scope"].split(" "))

    if config_scope_set != env_scope_set:
        print(CORANGE + "Scope changed since the last authorization of an access token.\nReauthorizing access token..." + TEXTCOLOR)
        return request_regular_token()

    elif os.getenv('REFRESH_TOKEN') is None:
        print(CORANGE + "Refresh token was not obtained.\nReauthorizing access token..." + TEXTCOLOR)
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
            raise HttpException(
                error_code=response.status_code,
                request_query=requests.Request(method="POST", url=url, headers=headers, data=form),
                response_text=json.loads(response.text)
            )
        except json.decoder.JSONDecodeError as error:
            CustomException(error_message=error, more_infos=(
                f"{CORANGE}HttpException() raised JSONDecodeError: {TEXTCOLOR}"
                f"{CORANGE}Response Code:{TEXTCOLOR} {response.status_code}"
                f"{CORANGE}Response as Bytes:{TEXTCOLOR} {response.content}"
                f"{CORANGE}Response as String:{TEXTCOLOR} {response.text}"
            ))

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
            raise CustomException(error_message=error, more_infos=(
                f"Exception occurred while refreshing access token\n"
                f"{CORANGE}Response Length:{TEXTCOLOR}{len(response.text)}\n"
                f"{CORANGE}Response Content:\n{TEXTCOLOR}{response.text}\n"
                f"\n{CRED}{error}\n{TEXTCOLOR}"
            ))


def request_extended_token() -> None:
    """
    Using https://www.chosic.com/spotify-playlist-analyzer/ to request temporary extended-token, that can be used to request Web API Data. After 1 hour a new token needs to be requested.
    This implementation extracts the Spotify Web API token after one default request out of the local Storage value `plAnalyzerToken` (hopefully not violating Terms of Services).

    :raises CustomException: If Exception occurs
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
        relevant_data = {
            'access_token': token_data['token'],
            'token_type': 'Bearer',
            'expires': token_data['expires']
        }
        update_env_key("EXTENDED_TOKEN", json.dumps(relevant_data))

        driver.close()

    except Exception as error:
        driver.close()
        raise CustomException(
            error_message=error,
            more_infos=f"Exception occurred while requesting temporary extended token"
        )


def api_request_data(
        url: str,
        request_type: Literal["GET", "POST", "DELETE", "PUT"],
        json_data: dict | str | None = None,
        overwrite_header: dict | None = None,
        json_as_data: bool = False,
) -> dict | list | None:
    """
    Transferring data from or to a server using Curl commands via [requests](https://docs.python-requests.org/en/latest/index.html). Currently supported HTTP regular_api_methods are `GET`, `POST`, `PUT` and `DELETE` (This implementation is designed for Spotify API requests)

    :param url: url to curl from/to
    :param request_type: HTTP request method
    :param json_data: JSON data to send
    :param overwrite_header: Specific headers to overwrite default headers
    :param json_as_data: True: data=json_data, False: json=json_data (Whether to send json_data as data or json)
    :return: JSON data fetched from Spotify API
    :raises RequestException: if Exception occurs while using requests
    :raises HttpException: if request response code is not good
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(url, str):
        raise InputException(item_value=url, valid_values="URLs (https://example.com)", valid_types=str)

    if not isinstance(request_type, str):
        raise InputException(item_value=request_type, valid_values=["GET", "POST", "DELETE", "PUT"], valid_types=str)

    if not isinstance(json_data, (dict, str, NoneType)):
        raise InputException(item_value=json_data, valid_values="(depend on specific request)", valid_types=(dict, str, NoneType))

    if not isinstance(overwrite_header, (dict, NoneType)):
        raise InputException(item_value=overwrite_header, valid_values=(None, "(depend on specific request)"), valid_types=(dict, NoneType))

    if not isinstance(json_as_data, bool):
        raise InputException(item_value=json_as_data, valid_values=(True, False), valid_types=bool)

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
    try:
        match request_type:
            # Note: there can be errors depending on whether 'json=' or 'data=' was used, modify cases if needed
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
                if json_as_data:
                    query = requests.Request(method="PUT", url=url, headers=headers, data=json_data)
                    response = requests.put(
                        url=url,
                        headers=headers,
                        data=json_data
                    )
                else:
                    query = requests.Request(method="PUT", url=url, headers=headers, json=json_data)
                    response = requests.put(
                        url=url,
                        headers=headers,
                        json=json_data
                    )

    except Exception as error:
        raise RequestException(
            error=error,
            request_query=query
        )

    if response.status_code not in [200, 201, 202, 204]:
        try:
            raise HttpException(
                error_code=response.status_code,
                request_query=query,
                response_text=json.loads(response.text)
            )
        except json.decoder.JSONDecodeError:
            print(CORANGE + "HttpException() JSONDecodeError:" + TEXTCOLOR)
            print(f"{CORANGE}Response Code:{TEXTCOLOR} {response.status_code}")
            print(f"{CORANGE}Response as Bytes:{TEXTCOLOR} {response.content}")
            print(f"{CORANGE}Response as String:{TEXTCOLOR} {response.text}")

    # Debugging:
    # with open(absolute_path(SPOTIFY_HTTP_ERRORS_PATH), 'r') as j_file:
    #     spotify_error_codes = json.load(j_file)
    #
    # prepared_query = query.prepare()
    #
    # print_debug(
    #     f"{CORANGE}Request returned Code:{TEXTCOLOR} {response.status_code} - {spotify_error_codes[str(response.status_code)]["name"]}\n"
    #     f"{CORANGE}Response as Bytes:{TEXTCOLOR} {response.content[:1000]+b'...'}\n"
    #     f"{CORANGE}Response as String:{TEXTCOLOR} {response.text[:1000]+"..."}\n\n"
    #     f"{CORANGE}Responsible Query:\n"
    #     f"{CORANGE}-----------START-----------\n"
    #     f"{prepared_query.method} {prepared_query.url}\n"
    #     + "\n".join(f"{key}: {value}" for key, value in prepared_query.headers.items()) + "\n"
    #     "Request Body:\n"
    #     f"{prepared_query.body if prepared_query.body else '\'---\''}\n"
    #     f"------------END------------{TEXTCOLOR}"
    # )

    if len(response.content) == 0:
        return None
    else:
        try:
            return response.json()

        except requests.exceptions.JSONDecodeError:
            try:
                return response.text

            except Exception as error:
                raise CustomException(
                    error_message=error,
                    more_infos=f"{CORANGE}Response Length:{TEXTCOLOR}{len(response.text)}\n{CORANGE}Response Content:\n{TEXTCOLOR}{response.text}"
                )


# <-- Begin Spotify Album Methods -->
def get_album(album_id: str, ignore_market: bool = False) -> dict:
    """
    Get Spotify catalog information for a single album.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-an-album

    :param album_id: The Spotify ID of the album.
    :param ignore_market: Whether to ignore market.
    :return: Dict containing Spotify Albums, in the form of {album_uri: album}
    :raises SpotifyIdException: if spotify id is invalid
    :raises InputException: if input is invalid
    """

    if not check_spotify_id(spotify_id=album_id):
        raise SpotifyIdException(invalid_id=album_id, id_type="album")

    if not isinstance(ignore_market, bool):
        raise InputException(item_value=ignore_market, valid_values=(True, False), valid_types=bool)

    response = api_request_data(
        url=f"https://api.spotify.com/v1/albums/{album_id}{f"?market={MARKET}" if not ignore_market else ""}",
        request_type="GET",
        json_data=None
    )

    return {response["uri"]: response}

#mps: 2
def get_several_albums(album_ids: list[str], ignore_market: bool = False) -> dict | None:
    """
    Get Spotify catalog information for multiple albums identified by their Spotify IDs.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-multiple-albums

    :param album_ids: A comma-separated list of the Spotify IDs for the albums.
    :param ignore_market: Whether to ignore market.
    :return: Dict containing Spotify Albums, in the form of {album_uri: album}
    :raises SpotifyIdException: if spotify id is invalid
    :raises InputException: if input is invalid
    """

    if not check_spotify_ids(spotify_ids=album_ids):
        invalid_albums = ', '.join(get_invalid_spotify_ids(spotify_ids=album_ids))
        raise SpotifyIdException(invalid_id=invalid_albums, id_type="album")

    if not isinstance(ignore_market, bool):
        raise InputException(item_value=ignore_market, valid_values=(True, False), valid_types=bool)

    albums = {}
    for current_chunk in range(0, len(album_ids), 20):
        encoded_chunk = quote(",".join(album_ids[current_chunk: current_chunk + 20]))
        response = api_request_data(
            url=f"https://api.spotify.com/v1/albums?ids={encoded_chunk}{f"&market={MARKET}" if not ignore_market else ""}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["albums"]}
        albums.update(tmp)

    return albums


def get_album_tracks(album_id: str, get_duration: bool = False, ignore_market: bool = False) -> dict | tuple[dict, int]:
    """
    Get Spotify catalog information about an album’s tracks. Optional parameters can be used to limit the number of tracks returned.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks

    :param album_id: The Spotify ID of the album.
    :param get_duration: If to get the Playlist duration in seconds. Default: False.
    :param ignore_market: Whether to ignore market.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track} (and optional the duration as second param)
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=album_id):
        raise SpotifyIdException(invalid_id=album_id, id_type="album")

    if not isinstance(get_duration, bool):
        raise InputException(item_value=get_duration, valid_values=(True, False), valid_types=bool)

    if not isinstance(ignore_market, bool):
        raise InputException(item_value=ignore_market, valid_values=(True, False), valid_types=bool)

    track_dicts = {}

    # Get first (up to) 50 tracks
    response = api_request_data(
        url=f"https://api.spotify.com/v1/albums/{album_id}/tracks?{f"market={MARKET}&" if not ignore_market else ""}limit=50&offset=0",
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


def get_users_saved_albums() -> dict | None:
    """
    Get a list of the albums saved in the current Spotify user's 'Your Music' library.
    
    **Needed Scopes:** user-library-read
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-users-saved-albums

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


def check_users_saved_albums(album_ids: list[str]) -> dict | None:
    """
    Check if one or more albums is already saved in the current Spotify user's 'Your Music' library.
    
    **Needed Scopes:** user-library-read
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/check-users-saved-albums

    :param album_ids: A comma-separated list of the Spotify IDs for the albums. Maximum: 20 IDs.
    :return: Dict containing if Spotify Albums are saved by User, in the form of {album_uri: exists?}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_ids(spotify_ids=album_ids):
        invalid_albums = ', '.join(get_invalid_spotify_ids(spotify_ids=album_ids))
        raise SpotifyIdException(invalid_id=invalid_albums, id_type="album")

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
def get_artist(artist_id: str) -> dict | None:
    """
    Get Spotify catalog information for a single artist identified by their unique Spotify ID.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-an-artist

    :param artist_id: The Spotify ID of the artist.
    :return: Dict containing Spotify Artists, in the form of {artist_uri: artist}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=artist_id):
        raise SpotifyIdException(invalid_id=artist_id, id_type="artist")

    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{artist_id}",
        request_type="GET",
        json_data=None
    )

    return {response["uri"]: response}


def get_several_artists(artist_ids: list[str]) -> dict | None:
    """
    Get Spotify catalog information for several artists based on their Spotify IDs.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists

    :param artist_ids: A comma-separated list of the Spotify IDs for the artists.
    :return: Dict containing Spotify Artists, in the form of {artist_uri: artist}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_ids(spotify_ids=artist_ids):
        invalid_artists = ', '.join(get_invalid_spotify_ids(spotify_ids=artist_ids))
        raise SpotifyIdException(invalid_id=invalid_artists, id_type="artist")

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


def get_artists_albums(artist_id: str, limit: int = 20) -> dict | None:
    """
    Get Spotify catalog information about an artist's albums.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums

    :param artist_id: The Spotify ID of the artist.
    :param limit: The maximum number of items to return.
    :return: Dict containing Spotify Albums, in the form of {album_uri: album}
    :raises SpotifyIdException: if spotify id is invalid
    :raises LimitException: if limit is invalid
    """

    if not check_spotify_id(spotify_id=artist_id):
        raise SpotifyIdException(invalid_id=artist_id, id_type="artist")

    if check_limits(limit=limit) > 0:
        raise LimitException(invalid_limit=limit)

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


def get_artists_top_tracks(artist_id: str) -> dict | None:
    """
    Get Spotify catalog information about an artist's top tracks by country.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks

    :param artist_id: The Spotify ID of the artist.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=artist_id):
        raise SpotifyIdException(invalid_id=artist_id, id_type="artist")

    response = api_request_data(
        url=f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market={MARKET}",
        request_type="GET",
        json_data=None
    )

    return {item["uri"]: item for item in response["tracks"]}


# <-- Begin Spotify Market Methods -->
def get_available_markets():
    """
    Get the list of markets (ISO 3166-1 alpha-2 country codes) where Spotify is available.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-available-markets

    Country Codes: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    :return: List of available markets.
    """
    response = api_request_data(
        url=f"https://api.spotify.com/v1/markets",
        request_type="GET"
    )
    return response["markets"]


# <-- Begin Spotify Player Methods -->
def get_playback_state() -> dict:
    """
    Get information about the user’s current playback state, including track or episode, progress, and active device.
    
    **Needed Scopes:** user-read-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback

    :return: Dict containing information about playback
    """
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/player?market={MARKET}",
        request_type="GET"
    )

    return response


def transfer_playback(new_device_id: str, playback_state: bool = False) -> None:
    """
    Transfer playback to a new device and optionally begin playback. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/transfer-a-users-playback

    :param new_device_id: Spotify device ID
    :param playback_state: True: ensure playback happens on new device; False: keep the current playback state.
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=new_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=new_device_id, id_type="device")
    if not isinstance(playback_state, bool):
        raise InputException(item_value=playback_state, valid_values=(True, False), valid_types=bool)

    request_body = {
        "device_ids": [new_device_id],
        "play": playback_state
    }

    api_request_data(
        url=f"https://api.spotify.com/v1/me/player",
        request_type="PUT",
        json_data=request_body,
        json_as_data=False
    )


def get_available_devices():
    """
    Get information about a user’s available Spotify Connect devices. Some device models are not supported and will not be listed in the API response.
    
    **Needed Scopes:** user-read-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-a-users-available-devices

    :return: Dict containing information about available devices, in the form of {device_uri: device} (Device uri is NOT official)
    """
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/player/devices",
        request_type="GET"
    )

    return {f"spotify:device:{current_device['id']}": current_device for current_device in response["devices"]}


def get_device(device_id: str) -> dict | None:
    """
    Get information about a user’s Spotify Connect device. Some device models are not supported and will not be listed in the API response.
    
    **Needed Scopes:** user-read-playback-state

    :param device_id: what device to get information about
    :return: Dict containing information about the device, in the form of {device_uri: device} (Device uri is NOT official)
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=device_id, is_device=True):
        raise SpotifyIdException(invalid_id=device_id, id_type="device")

    available_devices = get_available_devices()
    target_device = available_devices.get(f"spotify:device:{device_id}", None)
    return {f"spotify:device:{device_id}": target_device} if target_device else None


def get_currently_playing_track() -> dict:
    """
    Get the object currently being played on the user's Spotify account.
    
    **Needed Scopes:** user-read-currently-playing'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-the-users-currently-playing-track

    :return: Dict containing information about currently playing track
    """
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/player/currently-playing?market={MARKET}",
        request_type="GET"
    )

    return response


def start_or_resume_playback(target_device_id: str = None) -> None:
    """
    Start a new context or resume current playback on the user's active device. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback

    :param target_device_id: Spotify Device ID (If not supplied, the user's currently active device is the target)
    :raises SpotifyIdException: if spotify id is invalid
    """

    if target_device_id is not None and not check_spotify_id(spotify_id=target_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=target_device_id, id_type="device")

    # Note: Currently switching device results in 403 error with no clue why
    #   Spotify switches device and stops/aborts playback with "Error"
    target_device_id = None

    # only working if Spotify not playing anything (if called while playing -> Error)
    if not get_playback_state()['is_playing']:
        api_request_data(
            url=f"https://api.spotify.com/v1/me/player/play{"?device_id=" + target_device_id if target_device_id else ""}",
            request_type="PUT"
        )


def pause_playback() -> None:
    """
    Pause playback on the user's account. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/pause-a-users-playback
    """
    # only working if Spotify playing anything (if called while paused -> Error)
    if get_playback_state()['is_playing']:
        api_request_data(
            url=f"https://api.spotify.com/v1/me/player/pause",
            request_type="PUT"
        )


def skip_to_next(target_device_id: str = None) -> None:
    """
    Skips to next track in the user’s queue. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/skip-users-playback-to-next-track

    :param target_device_id: Spotify Device ID (If not supplied, the user's currently active device is the target)
    :raises SpotifyIdException: if spotify id is invalid
    """

    if target_device_id is not None and not check_spotify_id(spotify_id=target_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=target_device_id, id_type="device")

    # Note: Currently switching device results in 403 error with no clue why
    #   Spotify switches device and stops/aborts playback with "Error"
    target_device_id = None

    api_request_data(
        url=f"https://api.spotify.com/v1/me/player/next{"?device_id=" + target_device_id if target_device_id else ""}",
        request_type="POST"
    )


def skip_to_previous(target_device_id: str = None) -> None:
    """
    Skips to previous track in the user’s queue. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/skip-users-playback-to-previous-track

    :param target_device_id: Spotify Device ID (If not supplied, the user's currently active device is the target)
    :raises SpotifyIdException: if spotify id is invalid
    """

    if target_device_id is not None and not check_spotify_id(spotify_id=target_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=target_device_id, id_type="device")

    # Note: Currently switching device results in 403 error with no clue why
    #   Spotify switches device and stops/aborts playback with "Error"
    target_device_id = None

    api_request_data(
        url=f"https://api.spotify.com/v1/me/player/previous{"?device_id=" + target_device_id if target_device_id else ""}",
        request_type="POST"
    )


def seek_to_position(position_ms: int, target_device_id: str = None):
    """
    Seeks to the given position in the user’s currently playing track. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/seek-to-position-in-currently-playing-track

    :param position_ms: The position in milliseconds to seek to. Must be a positive number. Passing in a position that is greater than the length of the track will cause the player to start playing the next song.
    :param target_device_id: Spotify Device ID (If not supplied, the user's currently active device is the target)
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not isinstance(position_ms, int):
        raise InputException(item_value=position_ms, valid_values="positive integer", valid_types=int)

    if target_device_id is not None and not check_spotify_id(spotify_id=target_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=target_device_id, id_type="device")

    # Note: Currently switching device results in 403 error with no clue why
    #   Spotify switches device and stops/aborts playback with "Error"
    target_device_id = None

    if not isinstance(position_ms, int) or position_ms < 0:
        raise InputException(
            item_value=position_ms,
            valid_values="positive integer",
            valid_types=(int)
        )

    api_request_data(
        url=f"https://api.spotify.com/v1/me/player/seek?position_ms={position_ms}{"&device_id=" + target_device_id if target_device_id else ""}",
        request_type="PUT"
    )


def set_repeat_mode(new_repeat_mode: Literal["track", "context", "off"], target_device_id: str = None) -> None:
    """
    Set the repeat mode for the user's playback. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/set-repeat-mode-on-users-playback

    :param new_repeat_mode: track: will repeat the current track; context: will repeat the current context; off: will turn repeat off.
    :param target_device_id: Spotify Device ID (If not supplied, the user's currently active device is the target)
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(new_repeat_mode, str) or new_repeat_mode not in ["track", "context", "off"]:
        raise InputException(item_value=new_repeat_mode, valid_values=("track", "context", "off"), valid_types=str)

    if target_device_id is not None and not check_spotify_id(spotify_id=target_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=target_device_id, id_type="device")

    # Note: Currently switching device results in 403 error with no clue why
    #   Spotify switches device and stops/aborts playback with "Error"
    target_device_id = None

    if new_repeat_mode not in ["track", "context", "off"]:
        CustomException(
            error_message="new_repeat_mode must be one of 'track', 'context', 'off'",
            more_infos=f"Entered invalid repeat mode: '{new_repeat_mode}'"
        )
        return

    api_request_data(
        url=f"https://api.spotify.com/v1/me/player/repeat?state={new_repeat_mode}{"&device_id=" + target_device_id if target_device_id else ""}",
        request_type="PUT"
    )


def set_playback_volume(new_volume: int, target_device_id: str = None) -> None:
    """
    Set the volume for the user’s current playback device. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/set-volume-for-users-playback

    :param new_volume: The volume to set. Must be a value from 0 to 100 inclusive.
    :param target_device_id: Spotify Device ID (If not supplied, the user's currently active device is the target)
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not isinstance(new_volume, int) or 0 > new_volume > 100:
        raise InputException(item_value=new_volume, valid_values="0 <= new_volume <= 100", valid_types=int)

    if target_device_id is not None and not check_spotify_id(spotify_id=target_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=target_device_id, id_type="device")

    # Note: Currently switching device results in 403 error with no clue why
    #   Spotify switches device and stops/aborts playback with "Error"
    target_device_id = None

    api_request_data(
        url=f"https://api.spotify.com/v1/me/player/volume?volume_percent={new_volume}{"&device_id=" + target_device_id if target_device_id else ""}",
        request_type="PUT"
    )


def toggle_playback_shuffle(new_state: bool, target_device_id: str = None) -> None:
    """
    Toggle shuffle on or off for user’s playback. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/toggle-shuffle-for-users-playback

    :param new_state: True: Shuffle user's playback; False: Do not shuffle user's playback.
    :param target_device_id: Spotify Device ID (If not supplied, the user's currently active device is the target)
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not isinstance(new_state, bool):
        raise InputException(item_value=new_state, valid_values=(True, False), valid_types=bool)

    if target_device_id is not None and not check_spotify_id(spotify_id=target_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=target_device_id, id_type="device")

    # Note: Currently switching device results in 403 error with no clue why
    #   Spotify switches device and stops/aborts playback with "Error"
    target_device_id = None

    api_request_data(
        url=f"https://api.spotify.com/v1/me/player/shuffle?state={new_state}{"&device_id=" + target_device_id if target_device_id else ""}",
        request_type="PUT"
    )


def get_recently_played_tracks(limit: int, after: int = None, before: int = None) -> dict:
    """
    Get tracks from the current user's recently played tracks. Note: Currently doesn't support podcast episodes.
    
    **Needed Scopes:** user-read-recently-played'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-recently-played

    :param limit: The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.
    :param after: A Unix timestamp in milliseconds. Returns all items after (but not including) this cursor position. If after is specified, before must not be specified.
    :param before: A Unix timestamp in milliseconds. Returns all items before (but not including) this cursor position. If before is specified, after must not be specified.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    :raises InputException: if input is invalid
    :raises LimitException: if limit is invalid
    :raises CustomException: If Exception occurs
    """

    if check_limits(limit=limit) > 0:
        raise LimitException(invalid_limit=limit)

    if after:
        if not isinstance(after, int):
            raise InputException(item_value=after, valid_values="valid Unix timestamp in milliseconds", valid_types=int)

        url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}&after={after}"

        if before:
            print(f"{CORANGE}ignoring parameter before", TEXTCOLOR)
    elif before:
        if not isinstance(before, int):
            raise InputException(item_value=before, valid_values="valid Unix timestamp in milliseconds", valid_types=int)

        url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}&before={before}"

    else:
        CustomException(
            error_message="Either after or before must be specified",
            more_infos=f"after={after}; before={before}"
        )
        return

    check_limits(limit=limit, max_limit=50)

    response = api_request_data(
        url=url,
        request_type="GET"
    )

    return {current_item["track"]["uri"]: current_item["track"] for current_item in response["items"]}


def get_the_users_queue() -> dict:
    """
    Get the list of objects that make up the user's queue.
    
    **Needed Scopes:** user-read-currently-playing', 'user-read-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-queue

    :return: ordered Dict containing Spotify queued Tracks, in the form of {track_uri: track}
    """
    response = api_request_data(
        url="https://api.spotify.com/v1/me/player/queue",
        request_type="GET"
    )

    queue = {response["currently_playing"]["uri"]: response["currently_playing"]}
    queue.update({current_item["uri"]: current_item for current_item in response["queue"]})

    queue = remove_key_recursively(queue, "available_markets")

    return queue


def add_item_to_playback_queue(track_uri: str, target_device_id: str = None) -> None:
    """
    Add an item to the end of the user's current playback queue. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.
    
    **Needed Scopes:** user-modify-playback-state'
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/add-to-queue

    :param track_uri: The Spotify Track URIs to be queued.
    :param target_device_id: Spotify Device ID (If not supplied, the user's currently active device is the target)
    :raises SpotifyIdException: if spotify id is invalid
    :raises SpotifyUriException: if spotify uri is invalid
    """

    if not check_spotify_uri(spotify_uri=track_uri):
        raise SpotifyUriException(invalid_uri=track_uri, uri_type="track")

    if target_device_id is not None and not check_spotify_id(spotify_id=target_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=target_device_id, id_type="device")

    # Note: Currently switching device results in 403 error with no clue why
    #   Spotify switches device and stops/aborts playback with "Error"
    target_device_id = None

    encoded_uri = quote(track_uri)
    api_request_data(
        url=f"https://api.spotify.com/v1/me/player/queue?uri={encoded_uri}{"&device_id=" + target_device_id if target_device_id else ""}",
        request_type="POST"
    )


def add_several_items_to_playback_queue(track_uris: list[str], target_device_id: str = None) -> None:
    """
    Add multiple items to the end of the user's current playback queue. This API only works for users who have Spotify Premium. The order of execution is not guaranteed when you use this API with other Player API endpoints.

    :param track_uris: A list of the Spotify Track URIs to be queued.
    :param target_device_id: Spotify Device ID (If not supplied, the user's currently active device is the target)
    :raises SpotifyIdException: if spotify id is invalid
    :raises SpotifyUriException: if spotify uri is invalid
    """

    if not check_spotify_uris(spotify_uris=track_uris):
        invalid_uris = ",".join(get_invalid_spotify_uris(spotify_uris=track_uris))
        raise SpotifyUriException(invalid_uri=invalid_uris, uri_type="track")

    if target_device_id is not None and not check_spotify_id(spotify_id=target_device_id, is_device=True):
        raise SpotifyIdException(invalid_id=target_device_id, id_type="device")

    # Note: Currently switching device results in 403 error with no clue why
    #   Spotify switches device and stops/aborts playback with "Error"
    target_device_id = None

    # Warning: Does not use API optimization, because there is no Web API method for this by Spotify
    #   If HTTP Error 429 occurs multiple times set time.sleep(X) between the iterations
    for current_uri in track_uris:
        add_item_to_playback_queue(current_uri, target_device_id=target_device_id)
        # time.sleep(X)


# <-- Begin Spotify Playlist Methods -->
def get_playlist(playlist_id: str) -> dict | None:
    """
    Get a playlist owned by a Spotify user.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-playlist

    :param playlist_id: The Spotify ID of the playlist.
    :return: Dict containing Spotify Playlists, in the form of {playlist_id: playlist}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=playlist_id):
        raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

    # Note: it could be that private playlists create errors (not tested)

    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}?market={MARKET}",
        request_type="GET",
        json_data=None
    )
    return {response["uri"]: response}


def get_several_playlists(playlist_ids: list) -> dict | None:
    """
    Get Spotify catalog information for multiple playlists based on their Spotify IDs.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-several-tracks

    :param playlist_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_ids(spotify_ids=playlist_ids):
        invalid_playlists = get_invalid_spotify_ids(spotify_ids=playlist_ids)
        raise SpotifyIdException(invalid_id=invalid_playlists, id_type="playlist")

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


def change_playlist_details(playlist_id: str, name: str, public: bool, collaborative: bool, description: str) -> None:
    """
    Change a playlist's name and public/private state. (The user must, of course, own the playlist.)
    
    **Needed Scopes:** playlist-modify-public, playlist-modify-private
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/change-playlist-details

    :param playlist_id: The Spotify ID of the playlist.
    :param name: The new name for the playlist, for example "My New Playlist Title"
    :param public: The playlist's public/private status (if it should be added to the user's profile or not): true the playlist will be public, false the playlist will be private, null the playlist status is not relevant. For more about public/private status, see [Working with Playlists](https://developer.spotify.com/documentation/web-api/concepts/playlists)
    :param collaborative: If `true`, the playlist will become collaborative and other users will be able to modify the playlist in their Spotify client. Note: You can only set `collaborative=true` on non-public playlists.
    :param description: Value for playlist description as displayed in Spotify Clients and in the Web API.
    :return: Updates Playlist in App
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=playlist_id):
        raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

    if not isinstance(name, str):
        raise InputException(item_value=name, valid_values="(suitable playlist name)", valid_types=str)

    if not isinstance(public, bool):
        raise InputException(item_value=public, valid_values=(True, False), valid_types=bool)

    if not isinstance(collaborative, bool):
        raise InputException(item_value=collaborative, valid_values=(True, False), valid_types=bool)

    if not isinstance(description, str):
        raise InputException(item_value=description, valid_values="(suitable playlist description)", valid_types=str)

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


def get_playlist_items(playlist_id: str, get_duration: bool = False, ignore_market: bool = False) -> dict | tuple[dict, int] | None:
    """
    Get full details of the items of a playlist owned by a Spotify user.
    
    **Needed Scopes:** playlist-read-private
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks

    :param playlist_id: The Spotify ID of the playlist.
    :param get_duration: If to get the Playlist duration in seconds. Default: False.
    :param ignore_market: Whether to ignore market.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track} (and optional the duration as second param)
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=playlist_id):
        raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

    if not isinstance(get_duration, bool):
        raise InputException(item_value=get_duration, valid_values=(True, False), valid_types=bool)

    if not isinstance(ignore_market, bool):
        raise InputException(item_value=ignore_market, valid_values=(True, False), valid_types=bool)

    tracks = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50&offset=0{f"&market={MARKET}" if not ignore_market else ""}",
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
        CustomException(
            error_message=f"Could not fetch all Playlist '{playlist_id}' items",
            more_infos=f"Tracks fetched: {len(tracks)}, Tracks in Playlist: {total_tracks} (This difference can be due to duplicates in the Playlist.)"
        )

    if get_duration:
        duration = sum([int(current_track["duration_ms"]) for current_track in tracks.values()])
        return tracks, duration

    return tracks


def update_playlist_items(playlist_id: str, track_uris: list[str]) -> None:
    """
    Own implementation to update a Playlist
    
    **Needed Scopes:** playlist-read-private, playlist-modify-public, playlist-modify-private

    :param playlist_id: The Spotify ID of the playlist.
    :param track_uris: A comma-separated list of Spotify URIs to add.
    :return: Updates Playlist in App
    :raises SpotifyIdException: if spotify id is invalid
    :raises SpotifyUriException: if spotify uri is invalid
    """

    if not check_spotify_id(spotify_id=playlist_id):
        raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

    if not check_spotify_uris(spotify_uris=track_uris):
        invalid_uris = ",".join(get_invalid_spotify_uris(spotify_uris=track_uris))
        raise SpotifyUriException(invalid_uri=invalid_uris, uri_type="track")

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
        track_uris=track_uris
    )


def add_items_to_playlist(playlist_id: str, track_uris: list[str]) -> None:
    """
    Append one or more items to a user's playlist.
    
    **Needed Scopes:** playlist-modify-public, playlist-modify-private
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist

    :param playlist_id: The Spotify ID of the playlist.
    :param track_uris: A list of Spotify URIs to add
    :return: Updates Playlist in App
    :raises SpotifyIdException: if spotify id is invalid
    :raises SpotifyUriException: if spotify uri is invalid
    """

    if not check_spotify_id(spotify_id=playlist_id):
        raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

    if not check_spotify_uris(spotify_uris=track_uris):
        invalid_uris = ",".join(get_invalid_spotify_uris(spotify_uris=track_uris))
        raise SpotifyUriException(invalid_uri=invalid_uris, uri_type="track")

    for current_offset in range(0, len(track_uris), 100):
        # Note: The position [...] If omitted, the items will be appended to the playlist. [...]
        #  -> no position should work. Otherwise or if position is needed uncomment and update value
        # Additionally, the URIs are in the Body instead of passing numerous item URIs as a query parameter and
        # therefore, avoiding the surpassing of the maximum length of the request URI

        json_data = {
            "uris": track_uris[current_offset:current_offset + 100]
            # "position": position
        }
        api_request_data(
            url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            request_type="POST",
            json_data=json_data
        )


def remove_playlist_items(playlist_id: str, track_uris: list[str]) -> None:
    """
    Remove one or more items from a user's playlist (all appearances with these URIs/all Duplicates).
    
    **Needed Scopes:** playlist-modify-public, playlist-modify-private
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/remove-tracks-playlist

    :param playlist_id: The Spotify ID of the playlist.
    :param track_uris: An array of objects containing Spotify URIs of the tracks or episodes to remove.
    :return: Updates Playlist in App
    :raises SpotifyIdException: if spotify id is invalid
    :raises SpotifyUriException: if spotify uri is invalid
    """

    if not check_spotify_id(spotify_id=playlist_id):
        raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

    if not check_spotify_uris(spotify_uris=track_uris):
        invalid_uris = ",".join(get_invalid_spotify_uris(spotify_uris=track_uris))
        raise SpotifyUriException(invalid_uri=invalid_uris, uri_type="track")

    track_dict = get_several_tracks(track_ids=[uri_to_id(i) for i in track_uris])
    original_tracks = get_original_tracks(track_dict)
    track_dict = [{"uri": item} for item in original_tracks]

    for current_offset in range(0, len(track_uris), 100):
        json_data = {
            'tracks': track_dict[current_offset:current_offset + 100],
        }
        api_request_data(
            url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            request_type="DELETE",
            json_data=json_data
        )


def get_current_users_playlists(limit: int = 20) -> dict | None:
    """
    Get a list of the playlists owned or followed by the current Spotify user.
    
    **Needed Scopes:** playlist-read-private
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists

    :param limit: The maximum number of items to return.  If `limit=None` **all** Top Playlists get returned. Default: 20. Minimum: 1.
    :return: Dict containing Spotify Playlists, in the form of {playlist_uri: playlist}
    :raises LimitException: if limit is invalid
    """

    if check_limits(limit=limit) > 0:
        raise LimitException(invalid_limit=limit)

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


def get_users_playlists(user_id: str, limit: int | None = 20) -> dict | None:
    """
    Get a list of the playlists owned or followed by a Spotify user.
    
    **Needed Scopes:** playlist-read-private, playlist-read-collaborative
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists

    :param user_id: The user's Spotify ID.
    :param limit: The maximum number of items to return.  If `limit=None` **all** Top Playlists get returned. Default: 20. Minimum: 1.
    :return: Dict containing Spotify Playlists, in the form of {playlist_uri: playlist}
    :raises SpotifyIdException: if spotify id is invalid
    :raises LimitException: if limit is invalid
    """

    if not check_spotify_id(spotify_id=user_id, is_user=True):
        raise SpotifyIdException(invalid_id=user_id, id_type="user")

    if check_limits(limit=limit) > 0:
        raise LimitException(invalid_limit=limit)

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


def create_playlist(user_id: str, name: str, public: bool = True, collaborative: bool = False, description: str = None) -> dict | None:
    """
    Create a playlist for a Spotify user. (The playlist will be empty until you add tracks.) Each user is generally limited to a maximum of 11000 playlists.
    
    **Needed Scopes:** playlist-modify-public, playlist-modify-private
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/create-playlist

    :param user_id: The user's Spotify ID.
    :param name: The name for the new playlist, for example "Your Coolest Playlist". This name does not need to be unique; a user may have several playlists with the same name.
    :param public: Defaults to true. The playlist's public/private status (if it should be added to the user's profile or not): true the playlist will be public, false the playlist will be private. To be able to create private playlists, the user must have granted the "playlist-modify-private" scope. For more about public/private status, see Working with Playlists
    :param collaborative: Defaults to false. If true the playlist will be collaborative. Note: to create a collaborative playlist you must also set public to false. To create collaborative playlists you must have granted "playlist-modify-private" and "playlist-modify-public" scopes.
    :param description: value for playlist description as displayed in Spotify Clients and in the Web API.
    :return: Dict containing Spotify Playlists, in the form of {playlist_uri: playlist}
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=user_id, is_user=True):
        raise SpotifyIdException(invalid_id=user_id, id_type="user")

    if not isinstance(name, str):
        raise InputException(item_value=name, valid_values="(suitable playlist name)", valid_types=str)

    if not isinstance(public, bool):
        raise InputException(item_value=public, valid_values=(True, False), valid_types=bool)

    if not isinstance(collaborative, bool):
        raise InputException(item_value=collaborative, valid_values=(True, False), valid_types=bool)

    if not isinstance(description, str):
        raise InputException(item_value=description, valid_values="(suitable playlist description)", valid_types=str)

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


def get_playlist_cover_image(playlist_id: str) -> ImageFile:
    """
    Get the current image associated with a specific playlist.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-playlist-cover

    :param playlist_id: The Spotify ID of the playlist.
    :return: Playlist Cover Image loaded as Pillow Image
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=playlist_id):
        raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

    response = api_request_data(
        url=f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        request_type="GET",
        json_data=None
    )
    return image_from_url(response[0]["url"])


def add_custom_playlist_cover_image(playlist_id: str, b64_image: str) -> None:
    """
    Replace the image used to represent a specific playlist.
    
    **Needed Scopes:** ugc-image-upload, playlist-modify-private, playlist-modify-public
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/upload-custom-playlist-cover

    :param playlist_id: The Spotify ID of the playlist.
    :param b64_image: Base64 encoded JPEG image data, maximum payload size is 256 KB.
    :return: Updates Playlist in App
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=playlist_id):
        raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

    if not isinstance(b64_image, str):
        raise InputException(item_value=b64_image, valid_values="(valid base64 image string)", valid_types=str)

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
        overwrite_header=header,
        json_as_data=True
    )


def save_playlist_state(playlist_id: str, filepath: str) -> None:
    """
    Save Collection state as a Dict in the form of {playlist_uri: playlist, track_uri: track} to file

    :param playlist_id: Spotify Playlist id
    :param filepath: where to save playlist state
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=playlist_id):
        raise SpotifyIdException(invalid_id=playlist_id, id_type="playlist")

    if not isinstance(filepath, str) or not os.path.exists(absolute_path(os.path.split(filepath)[0])):
        raise InputException(item_value=filepath, valid_values="valid filepath", valid_types=str)

    playlist = get_playlist(playlist_id=playlist_id)
    playlist.update(get_playlist_items(playlist_id=playlist_id))

    json_to_file(
        json_filepath=filepath,
        json_data=playlist,
        overwrite=True
    )


# <-- Begin Spotify Search Methods -->
def search_for_item(
        search_query: str,
        item_type: list[Literal["album", "artist", "playlist", "track"]],
        limit: int = 20,
        offset: int = 0
) -> dict | None:
    """
    Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or audiobooks that match a keyword string.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/search

    **Better Search queries:**
        (1) You can narrow down your search using field filters. The available filters are album, artist, track, year, upc, tag:hipster, tag:new, isrc, and genre. Each field filter only applies to certain result types.
        (2) The artist and year filters can be used while searching albums, artists and tracks. You can filter on a single year or a range (e.g. 1955-1960).
        (3) The album filter can be used while searching albums and tracks.
        (4) The genre filter can be used while searching artists and tracks.
        (5) The isrc and track filters can be used while searching tracks.
        (6) The upc, tag:new and tag:hipster filters can only be used while searching albums. The tag:new filter will return albums released in the past two weeks and tag:hipster can be used to return only albums with the lowest 10% popularity.

    :param search_query: Your search query.
    :param item_type: A comma-separated list of item types to search across. Search results include hits from all the specified item types. For example: 'q=abacab&type=album,track' returns both albums and tracks matching "abacab".
    :param limit: The maximum number of results to return in each item type. Default: 20. Minimum: 1. Maximum: 50.
    :param offset: The index of the first result to return. Use with limit to get the next page of search results. Default: 0. Minimum: 0. Maximum: 1000-limit.
    :return: Dict containing the Search response, in the form of {item_uri: item}
    :raises InputException: if input is invalid
    :raises LimitException: if limit is invalid
    """

    if not isinstance(search_query, str):
        raise InputException(item_value=search_query, valid_values="string", valid_types=str)

    if not isinstance(item_type, list) or len(item_type) == 0 or len(set(item_type) - {"album", "artist", "playlist", "track"}) > 0:
        raise InputException(item_value=item_type, valid_values=("album", "artist", "playlist", "track"), valid_types=list)

    if check_limits(limit=limit) > 0:
        raise LimitException(invalid_limit=limit)

    if not isinstance(offset, int) or check_limits(offset, min_limit=0, max_limit=1000 - limit):
        raise InputException(item_value=offset, valid_values=f"0 <= offset <= {1000 - limit}", valid_types=int)

    response = api_request_data(
        url=f"https://api.spotify.com/v1/search?q={search_query}{"&type=" + ','.join(item_type)}&market={MARKET}&limit={limit}&offset={offset}",
        request_type="GET"
    )

    # debug
    json_to_file("code_backend/development_and_testing/debugging.json", response, overwrite=True)

    output = {}
    for item_type in response.keys():
        output.update({current_item["uri"]: current_item for current_item in response[f"{item_type}"]["items"] if current_item})

    json_to_file("code_backend/development_and_testing/debugging_2.json", output, overwrite=True)

    return output


# <-- Begin Spotify Track Methods -->
def get_track(track_id: str, ignore_market: bool = False) -> dict:
    """
    Get Spotify catalog information for a single track identified by its unique Spotify ID.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-track

    :param track_id: The Spotify ID for the track.
    :param ignore_market: Whether to ignore market.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    :raises SpotifyIdException: if spotify id is invalid
    :raises InputException: if input is invalid
    """

    if not check_spotify_id(spotify_id=track_id):
        raise SpotifyIdException(invalid_id=track_id, id_type="track")

    if not isinstance(ignore_market, bool):
        raise InputException(item_value=ignore_market, valid_values=(True, False), valid_types=bool)

    response = api_request_data(
        url=f"https://api.spotify.com/v1/tracks/{track_id}{f"?market={MARKET}" if not ignore_market else ""}",
        request_type="GET",
        json_data=None
    )
    return {response["uri"]: response}


def get_several_tracks(track_ids: list[str], ignore_market: bool = False) -> dict | None:
    """
    Get Spotify catalog information for multiple tracks based on their Spotify IDs.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-several-tracks

    :param track_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Spotify Tracks, in the form of {track_uri: track}
    :raises SpotifyIdException: if spotify id is invalid
    :raises InputException: if input is invalid
    """

    if not check_spotify_ids(spotify_ids=track_ids):
        invalid_tracks = ', '.join(get_invalid_spotify_ids(spotify_ids=track_ids))
        raise SpotifyIdException(invalid_id=invalid_tracks, id_type="track")

    if not isinstance(ignore_market, bool):
        raise InputException(item_value=ignore_market, valid_values=(True, False), valid_types=bool)

    tracks = {}

    for current_offset in range(0, len(track_ids), 50):
        encoded_chunk = quote(",".join(track_ids[current_offset: current_offset + 50]))

        response = api_request_data(
            url=f"https://api.spotify.com/v1/tracks?{f"market={MARKET}&" if not ignore_market else ""}ids={encoded_chunk}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["tracks"]}
        tracks.update(tmp)

    return tracks


def get_users_saved_tracks(limit: int = 20, ignore_market: bool = False) -> dict | None:
    """
    Get a list of the songs saved in the current Spotify user's 'Your Music' library.
    
    **Needed Scopes:** user-library-read
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks

    :param limit: The maximum number of items to return. If `limit=None` **all** Saved Tracks get returned. Default: 20. Minimum: 1.
    :param ignore_market: Whether to ignore market.
    :return: Dict containing Saved Spotify Tracks, in the form of {track_uri: track}
    :raises LimitException: if limit is invalid
    :raises InputException: if input is invalid
    """

    if check_limits(limit=limit) > 0:
        raise LimitException(invalid_limit=limit)

    if not isinstance(ignore_market, bool):
        raise InputException(item_value=ignore_market, valid_values=(True, False), valid_types=bool)

    tracks = {}

    # Get first (up to) 50 artists
    response = api_request_data(
        url=f"https://api.spotify.com/v1/me/tracks?{f"market={MARKET}&" if not ignore_market else ""}limit={min(50, limit)}&offset=0",
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


def check_users_saved_tracks(track_ids: list[str]) -> dict | None:
    """
    Check if one or more tracks is already saved in the current Spotify user's 'Your Music' library.
    
    **Needed Scopes:** user-library-read
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/check-users-saved-tracks

    :param track_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Saved Spotify Tracks, in the form of {track_uri: bool}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_ids(spotify_ids=track_ids):
        invalid_tracks = ', '.join(get_invalid_spotify_ids(spotify_ids=track_ids))
        raise SpotifyIdException(invalid_id=invalid_tracks, id_type="track")

    tracks = {}

    for current_offset in range(0, len(track_ids), 50):
        encoded_chunk = quote(",".join(track_ids[current_offset: current_offset + 50]))

        response = api_request_data(
            url=f"https://api.spotify.com/v1/me/tracks/contains?ids={encoded_chunk}",
            request_type="GET",
            json_data=None
        )

        for _id, existence in zip(track_ids[current_offset: current_offset + 50], response):
            tracks[f"spotify:track:{_id}"] = existence

    return tracks


def get_tracks_audio_features(track_id: str):
    """
    Get audio feature information for a single track identified by its unique Spotify ID.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-audio-features

    :param track_id: The Spotify ID for the track.
    :return: Dict containing Audio Features, in the form of {track_uri: audio_features}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=track_id):
        raise SpotifyIdException(invalid_id=track_id, id_type="track")

    header = {'Authorization': "Bearer " + json.loads(os.getenv("EXTENDED_TOKEN"))["access_token"]}
    response = api_request_data(
        url=f"https://api.spotify.com/v1/audio-features/{track_id}",
        request_type="GET",
        overwrite_header=header
    )
    return {response["uri"]: response}


def get_several_tracks_audio_features(track_ids: list[str]) -> dict | None:
    """
    Get audio features for multiple tracks based on their Spotify IDs.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features

    :param track_ids: A comma-separated list of the Spotify IDs for the tracks.
    :return: Dict containing Audio Features, in the form of {track_uri: audio_features}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_ids(spotify_ids=track_ids):
        invalid_tracks = ', '.join(get_invalid_spotify_ids(spotify_ids=track_ids))
        raise SpotifyIdException(invalid_id=invalid_tracks, id_type="track")

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


def get_original_tracks(tracks: dict) -> dict | None:
    """
    If the track has been relinked, the response contains a linked_from object containing information about the original
    track. In the example above, the track that was requested had the Spotify URI spotify:track:6kLCHFM39wkFjOuyPGLGeQ.
    Since it’s been relinked, this original track URI can be found in the linked_from object. The parent track object
    now contains metadata about the relinked track with URI spotify:track:6ozxplTAjWO0BlUxN8ia0A.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/concepts/track-relinking

    :param tracks: Dict containing Spotify Tracks, in the form of {track_uri: track}
    :return: Dict containing original Spotify Tracks, in the form of {track_uri: track}
    :raises SpotifyIdException: if spotify id is invalid
    :raises InputException: if input is invalid
    """

    if not isinstance(tracks, dict):
        raise InputException(item_value=tracks, valid_values="{'spotify:track:${track_id}': {...}, ..., 'spotify:track:${track_id}': {...}}", valid_types=dict)

    original_tracks = dict()
    for current_track_uri, current_track in tracks.items():
        if not isinstance(current_track, dict):
            raise InputException(item_value=current_track, valid_values="{'spotify:track:${track_id}': {...}}", valid_types=dict)

        if current_track.get("linked_from", False):
            original_track_id = current_track.get("linked_from")["id"]
            original_track = get_track(track_id=original_track_id, ignore_market=True)

            original_tracks.update(original_track)

        else:
            original_tracks.update({current_track_uri: current_track})

    return original_tracks


# <-- Begin Spotify User Methods -->
def get_current_users_profile() -> dict:
    """
    Get detailed profile information about the current user (including the current user's username).
    
    **Needed Scopes:** user-read-private, user-read-email
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile

    :return: Dict containing Spotify Users, in the form of {user_uri: user}
    """

    response = api_request_data(
        url=f"https://api.spotify.com/v1/me",
        request_type="GET",
        json_data=None
    )
    return {response["uri"]: response}


def get_users_top_items(
        item_type: Literal["artists", "tracks"],
        time_range: Literal["short_term", "medium_term", "long_term"] = "medium_term",
        limit: int = 20
) -> dict | None:
    """
    Get the current user's top artists or tracks based on calculated affinity.
    
    **Needed Scopes:** user-top-read
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks

    :param item_type: The type of entity to return. Valid values: "artists" or "tracks"
    :param time_range: Over what time frame the affinities are computed. Valid values: "long_term" (calculated from ~1 year of data and including all new data as it becomes available), "medium_term" (approximately last 6 months), "short_term" (approximately last 4 weeks). Default: medium_term
    :param limit: The maximum number of items to return. If `limit=None` **all** Top Tracks get returned. Default: 20. Minimum: 1.
    :return: Dict containing Spotify Tracks, in the form of {user_uri: user}
    :raises InputException: if input is invalid
    :raises LimitException: if limit is invalid
    """

    if not isinstance(item_type, str) or item_type not in ("artists", "tracks"):
        raise InputException(item_value=item_type, valid_values=("artists", "tracks"), valid_types=str)

    if not isinstance(time_range, str) or time_range not in ("short_term", "medium_term", "long_term"):
        raise InputException(item_value=time_range, valid_values=("short_term", "medium_term", "long_term"), valid_types=str)

    if check_limits(limit=limit) > 0:
        raise LimitException(invalid_limit=limit)

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

    for current_offset in range(50, min(total_artists, limit), 50):
        response = api_request_data(
            url=f"https://api.spotify.com/v1/me/top/{item_type}?time_range={time_range}&limit=50&offset={current_offset}",
            request_type="GET",
            json_data=None
        )

        tmp = {item["uri"]: item for item in response["items"]}
        tracks.update(tmp)

    return tracks


def get_users_profile(user_id: str) -> dict:
    """
    Get public profile information about a Spotify user.
    
    **Needed Scopes:** None
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-users-profile

    :param user_id: The user's Spotify user ID.
    :return: Dict containing Spotify Users, in the form of {user_uri: user}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_id(spotify_id=user_id, is_user=True):
        raise SpotifyIdException(invalid_id=user_id, id_type="user")

    response = api_request_data(
        url=f"https://api.spotify.com/v1/users/{user_id}",
        request_type="GET",
        json_data=None
    )
    return {response["uri"]: response}


def get_several_users(user_ids: list) -> dict | None:
    """
    Get Spotify catalog information for multiple user based on their Spotify IDs.
    
    **Needed Scopes:** None

    :param user_ids: A list of the Spotify IDs to be checked.
    :return: Dict containing Spotify User, in the form of {user_uri: user}
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not check_spotify_user_ids(spotify_ids=user_ids):
        raise SpotifyIdException(invalid_id=user_ids, id_type="user")

    users = {}

    # Warning: Does not use API optimization, because there is no Web API method for this by Spotify
    #   If HTTP Error 429 occurs multiple times set time.sleep(X) between the iterations
    for current_user_id in user_ids:
        current_playlist = get_users_profile(user_id=current_user_id)
        users.update(current_playlist)
        # time.sleep(X)

    return users


def get_followed_artists(get_type: str = "artist") -> dict | None:
    """
    Get the current user's followed artists.
    
    **Needed Scopes:** user-follow-read
    
    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/reference/get-followed

    :param get_type: The ID type: currently only artist is supported.
    :return: Dict containing Spotify Artists, in the form of {artist_uri: artist}
    :raises InputException: if input is invalid
    """

    if not isinstance(get_type, str) or get_type != "artist":
        raise InputException(item_value=get_type, valid_values="artist", valid_types=str)

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
    # print(api_request_data(
    #     url=f"https://api.spotify.com/v1/albums/79fnwKynD56xIXBVWkyaE5?market={MARKET}",
    #     request_type="GET",
    #     json_data=None
    # ))

    # with open(absolute_path("code_backend/testing/debugging.json"), "r") as jile:
    #     relinked_track = json.load(jile)
    #
    # print(get_original_tracks(relinked_track))


    # playlist_tracks = get_playlist_items(playlist_id="6bRkO7PLCXgmV4EJH52iU4")
    #
    # json_to_file(
    #     json_filepath=absolute_path("code_backend/testing/debugging.json"),
    #     json_data=playlist_tracks,
    #     overwrite=True
    # )
    # json_to_file(
    #     json_filepath=absolute_path("code_backend/testing/debugging_2.json"),
    #     json_data=get_original_tracks(tracks=playlist_tracks),
    #     overwrite=True
    # )
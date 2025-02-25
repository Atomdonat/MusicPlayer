import pytest
from code_backend.spotify_web_api import *
from code_backend.secondary_methods import image_from_file, image_to_b64
from code_backend.exceptions import *


RUN_ALL_TESTS = True
EXCLUDE_TEST = True
EXCLUDE_TOKENS = True

# Positive Values for Testing
POS_AFTER: int = 1484811043508
POS_ALBUM_ID: str = "79fnwKynD56xIXBVWkyaE5"
POS_ALBUM_IDS: list[str] = ["79fnwKynD56xIXBVWkyaE5", "7CI6R1kJLUMfBl4FOKP8nc"]
POS_ARTIST_ID: str = "6XyY86QOPPrYVGvF9ch6wz"
POS_ARTIST_IDS: list[str] = ["6XyY86QOPPrYVGvF9ch6wz", "00YTqRClk82aMchQQpYMd5"]
POS_B64_IMAGE: str = image_to_b64(image_from_file("Icons/Spotipy_Logo.png"), image_format="PNG")
POS_BEFORE: int = 1484811043508
POS_COLLABORATIVE: bool = False
POS_DESCRIPTION: str = "pytest"
POS_DEVICE_ID: str = "a59d3a684d22772199a2fe97cdcdf563eaee9ac1"
POS_FILEPATH: str = "code_backend/testing/debugging.json"
POS_GET_DURATION: bool = True
POS_GET_TYPE: str = "artist"
POS_ITEM_TYPE: Literal['artists', 'tracks'] = "artists"
POS_JSON_AS_DATA: bool = False
# POS_JSON_DATA: dict | str = None
POS_LIMIT: int = 2
POS_NAME: str = "Pytest"
POS_NEW_DEVICE_ID: str = "a59d3a684d22772199a2fe97cdcdf563eaee9ac1"
POS_NEW_REPEAT_MODE: Literal['track', 'context', 'off'] = "track"
POS_NEW_STATE: bool = False
POS_NEW_VOLUME: int = 69
POS_OFFSET: int = 0
POS_OVERWRITE_HEADER: dict = None
POS_PLAYBACK_STATE: bool = True
POS_PLAYLIST_ID: str = "6bRkO7PLCXgmV4EJH52iU4"
POS_PLAYLIST_IDS: list = ["6bRkO7PLCXgmV4EJH52iU4", "1ODwycvRrJQZ7GbBQc1iZm"]
POS_POSITION_MS: int = 0
POS_PUBLIC: bool = False
POS_REQUEST_TYPE: Literal['GET', 'POST', 'DELETE', 'PUT'] = "GET"
POS_SEARCH_QUERY: str = "Numb"
POS_TARGET_DEVICE_ID: str = "a59d3a684d22772199a2fe97cdcdf563eaee9ac1"
POS_TIME_RANGE: Literal['short_term', 'medium_term', 'long_term'] = 'short_term'
POS_TRACK_ID: str = "14FP9BNWHekbC17tqcppOR"
POS_TRACK_IDS: list[str] = ["6zrR8itT7IfAdl5aS7YQyt", "14FP9BNWHekbC17tqcppOR"]
POS_TRACK_URI: str = "spotify:track:14FP9BNWHekbC17tqcppOR"
POS_TRACK_URIS: list[str] = ["spotify:track:6zrR8itT7IfAdl5aS7YQyt", "spotify:track:14FP9BNWHekbC17tqcppOR"]
POS_URL: str = "https://api.spotify.com/v1/albums/4aawyAB9vmqN3uQ7FjRGTy"
POS_USER_ID: str = "simonluca1"
POS_USER_IDS: list = ["simonluca1", "1164847650"]

# Negative Values for Testing
# 0: correct type and wrong value
# 1: wrong type
NEG_TEST_CASE = 1

NEG_AFTER = [0, "NEG_AFTER"]
NEG_ALBUM_ID = ["NEG_ALBUM_ID", 0]
NEG_ALBUM_IDS = [["NEG_ALBUM_IDS"], 0]
NEG_ARTIST_ID = ["NEG_ARTIST_ID", 0]
NEG_ARTIST_IDS = [["NEG_ARTIST_IDS"], 0]
NEG_B64_IMAGE = ["NEG_B64_IMAGE", 0]
NEG_BEFORE = [0, "NEG_BEFORE"]
NEG_COLLABORATIVE = ["NEG_COLLABORATIVE"]
NEG_DESCRIPTION = [0]
NEG_DEVICE_ID = ["NEG_DEVICE_ID", 0]
NEG_FILEPATH = ["NEG_FILEPATH", 0]
NEG_GET_DURATION = ["NEG_GET_DURATION"]
NEG_GET_TYPE = ["NEG_GET_TYPE", 0]
NEG_ITEM_TYPE = ["NEG_ITEM_TYPE", 0]
NEG_JSON_AS_DATA = ["NEG_JSON_AS_DATA"]
NEG_JSON_DATA = ["NEG_JSON_DATA", 0]
NEG_LIMIT = [-5, "NEG_LIMIT"]
NEG_NAME = [-5]
NEG_NEW_DEVICE_ID = ["NEG_NEW_DEVICE_ID", 0]
NEG_NEW_REPEAT_MODE = ["NEG_NEW_REPEAT_MODE", 0]
NEG_NEW_STATE = ["NEG_NEW_STATE"]
NEG_NEW_VOLUME = [-5, "NEG_NEW_VOLUME"]
NEG_OFFSET = [-5, "NEG_OFFSET"]
NEG_OVERWRITE_HEADER = ["NEG_OVERWRITE_HEADER"]
NEG_PLAYBACK_STATE = ["NEG_PLAYBACK_STATE"]
NEG_PLAYLIST_ID = ["NEG_PLAYLIST_ID", 0]
NEG_PLAYLIST_IDS = [["NEG_PLAYLIST_IDS"], 0]
NEG_POSITION_MS = [-5, "NEG_POSITION_MS"]
NEG_PUBLIC = ["NEG_PUBLIC"]
NEG_REQUEST_TYPE = ["NEG_REQUEST_TYPE", 0]
NEG_SEARCH_QUERY = ["NEG_SEARCH_QUERY", 0]
NEG_TARGET_DEVICE_ID = ["NEG_TARGET_DEVICE_ID", 0]
NEG_TIME_RANGE = ["NEG_TIME_RANGE", 0]
NEG_TRACK_ID = ["NEG_TRACK_ID", 0]
NEG_TRACK_IDS = [["NEG_TRACK_IDS"], 0]
NEG_TRACK_URI = ["NEG_TRACK_URI", 0]
NEG_TRACK_URIS = [["NEG_TRACK_URIS"], 0]
NEG_URL = ["NEG_URL", 0]
NEG_USER_ID = ["NEG_USER_ID", 0]
NEG_USER_IDS = [["NEG_USER_IDS"], 0]
NEG_USE_CREDENTIALS = ["NEG_USE_CREDENTIALS"]
CUSTOM_EXCEPTIONS = (
    DatabaseException, SpotifyApiException, HttpException, RequestException,
    CustomException, InputException, SpotifyIdException, SpotifyUriException,
    LimitException
)


# Tests with Positive Test Case:
#   passed: 46, ignored: 10, failed: 0

# Tests with Negative Test Case 0:
#   passed: 46, ignored: 10, failed: 0

# Tests with Negative Test Case 1:
#   passed: 46, ignored: 10, failed: 0


@pytest.fixture(scope="session", autouse=True)
def ensure_valid_token():
    if check_token_expired(extended_token=False) == 0:
        refresh_access_token()

    if check_token_expired(extended_token=True) == 0:
        request_extended_token()


@pytest.fixture(scope="session", autouse=True)
def restore_test_playlist():
    test_track_uris = [
        "spotify:track:6zrR8itT7IfAdl5aS7YQyt",
        "spotify:track:60a0Rd6pjrkxjPbaKzXjfq",
        "spotify:track:3gVhsZtseYtY1fMuyYq06F",
        "spotify:track:5DXGHZ3QDh0FcLXPMWTv9U",
        "spotify:track:60eOMEt3WNVX1m1jmApmnX"
    ]
    update_playlist_items(
        playlist_id="6bRkO7PLCXgmV4EJH52iU4",
        track_uris=test_track_uris
    )

@pytest.mark.skipif(not RUN_ALL_TESTS or EXCLUDE_TOKENS, reason='passed manual test')
def test_request_regular_token():
    # Positive Test Case
    request_regular_token()


@pytest.mark.skipif(not RUN_ALL_TESTS or EXCLUDE_TOKENS, reason='passed manual test')
def test_refresh_access_token():
    # Positive Test Case
    refresh_access_token()


@pytest.mark.skipif(not RUN_ALL_TESTS or EXCLUDE_TOKENS, reason='passed manual test')
def test_request_extended_token():
    # Positive Test Case
    request_extended_token()


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_api_request_data():
    # Positive Test Case
    api_request_data(
        url=f"https://api.spotify.com/v1/albums/79fnwKynD56xIXBVWkyaE5?market={MARKET}",
        request_type="GET",
        json_data=None
    )

    # Negative Test Cases
    try:
        api_request_data(
            url=f"https://api.spotify.com/v1/albums/simonluca1?market={MARKET}",
            request_type="GET",
            json_data=None
        )
    except CUSTOM_EXCEPTIONS:
        pass


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_album():
    # Positive Test Case
    positive_params = {
        "album_id": POS_ALBUM_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_album.json"), "w") as file:
        file.write(json.dumps(get_album(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "album_id": NEG_ALBUM_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_album(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_several_albums():
    # Positive Test Case
    positive_params = {
        "album_ids": POS_ALBUM_IDS,  # list[str]
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_several_albums.json"), "w") as file:
        file.write(json.dumps(get_several_albums(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "album_ids": NEG_ALBUM_IDS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_several_albums(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_album_tracks():
    # Positive Test Case
    positive_params = {
        "album_id": POS_ALBUM_ID,  # str
        "get_duration": POS_GET_DURATION,  # bool
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_album_tracks.json"), "w") as file:
        file.write(json.dumps(get_album_tracks(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "album_id": NEG_ALBUM_ID[NEG_TEST_CASE],  # str
            "get_duration": NEG_GET_DURATION[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_album_tracks(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_users_saved_albums():
    # Positive Test Case
    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_users_saved_albums.json"), "w") as file:
        file.write(json.dumps(get_users_saved_albums()))


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_check_users_saved_albums():
    # Positive Test Case
    positive_params = {
        "album_ids": POS_ALBUM_IDS,  # list[str]
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/check_users_saved_albums.json"), "w") as file:
        file.write(json.dumps(check_users_saved_albums(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "album_ids": NEG_ALBUM_IDS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            check_users_saved_albums(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_artist():
    # Positive Test Case
    positive_params = {
        "artist_id": POS_ARTIST_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_artist.json"), "w") as file:
        file.write(json.dumps(get_artist(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "artist_id": NEG_ARTIST_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_artist(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_several_artists():
    # Positive Test Case
    positive_params = {
        "artist_ids": POS_ARTIST_IDS,  # list[str]
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_several_artists.json"), "w") as file:
        file.write(json.dumps(get_several_artists(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "artist_ids": NEG_ARTIST_IDS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_several_artists(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_artists_albums():
    # Positive Test Case
    positive_params = {
        "artist_id": POS_ARTIST_ID,  # str
        "limit": POS_LIMIT,  # int
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_artists_albums.json"), "w") as file:
        file.write(json.dumps(get_artists_albums(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "artist_id": NEG_ARTIST_ID[NEG_TEST_CASE],  # str
            "limit": NEG_LIMIT[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_artists_albums(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_artists_top_tracks():
    # Positive Test Case
    positive_params = {
        "artist_id": POS_ARTIST_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_artists_top_tracks.json"), "w") as file:
        file.write(json.dumps(get_artists_top_tracks(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "artist_id": NEG_ARTIST_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_artists_top_tracks(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_available_markets():
    # Positive Test Case
    get_available_markets()


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_playback_state():
    # Positive Test Case
    get_playback_state()


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_transfer_playback():
    # Positive Test Case
    positive_params = {
        "new_device_id": POS_NEW_DEVICE_ID,  # str
        "playback_state": POS_PLAYBACK_STATE,  # bool
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/transfer_playback.json"), "w") as file:
        file.write(json.dumps(transfer_playback(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "new_device_id": NEG_NEW_DEVICE_ID[NEG_TEST_CASE],  # str
            "playback_state": NEG_PLAYBACK_STATE[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            transfer_playback(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_available_devices():
    # Positive Test Case
    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_available_devices.json"), "w") as file:
        file.write(json.dumps(get_available_devices()))


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_device():
    # Positive Test Case
    positive_params = {
        "device_id": POS_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_device.json"), "w") as file:
        file.write(json.dumps(get_device(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "device_id": NEG_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_device(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_currently_playing_track():
    # Positive Test Case
    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_currently_playing_track.json"), "w") as file:
        file.write(json.dumps(get_currently_playing_track()))


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_start_or_resume_playback():
    # Positive Test Case
    positive_params = {
        "target_device_id": POS_TARGET_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/start_or_resume_playback.json"), "w") as file:
        file.write(json.dumps(start_or_resume_playback(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "target_device_id": NEG_TARGET_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            start_or_resume_playback(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_pause_playback():
    # Positive Test Case
    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/pause_playback.json"), "w") as file:
        file.write(json.dumps(pause_playback()))


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_skip_to_next():
    # Positive Test Case
    positive_params = {
        "target_device_id": POS_TARGET_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/skip_to_next.json"), "w") as file:
        file.write(json.dumps(skip_to_next(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "target_device_id": NEG_TARGET_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            skip_to_next(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_skip_to_previous():
    # Positive Test Case
    positive_params = {
        "target_device_id": POS_TARGET_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/skip_to_previous.json"), "w") as file:
        file.write(json.dumps(skip_to_previous(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "target_device_id": NEG_TARGET_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            skip_to_previous(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_seek_to_position():
    # Positive Test Case
    positive_params = {
        "position_ms": POS_POSITION_MS,  # int
        "target_device_id": POS_TARGET_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/seek_to_position.json"), "w") as file:
        file.write(json.dumps(seek_to_position(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "position_ms": NEG_POSITION_MS[NEG_TEST_CASE],  # int
            "target_device_id": NEG_TARGET_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            seek_to_position(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_set_repeat_mode():
    # Positive Test Case
    positive_params = {
        "new_repeat_mode": POS_NEW_REPEAT_MODE,  # Literal['track', 'context', 'off']
        "target_device_id": POS_TARGET_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/set_repeat_mode.json"), "w") as file:
        file.write(json.dumps(set_repeat_mode(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "new_repeat_mode": NEG_NEW_REPEAT_MODE[NEG_TEST_CASE],  # Literal['track', 'context', 'off']
            "target_device_id": NEG_TARGET_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            set_repeat_mode(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_set_playback_volume():
    # Positive Test Case
    positive_params = {
        "new_volume": POS_NEW_VOLUME,  # int
        "target_device_id": POS_TARGET_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/set_playback_volume.json"), "w") as file:
        file.write(json.dumps(set_playback_volume(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "new_volume": NEG_NEW_VOLUME[NEG_TEST_CASE],  # int
            "target_device_id": NEG_TARGET_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            set_playback_volume(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_toggle_playback_shuffle():
    # Positive Test Case
    positive_params = {
        "new_state": POS_NEW_STATE,  # bool
        "target_device_id": POS_TARGET_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/toggle_playback_shuffle.json"), "w") as file:
        file.write(json.dumps(toggle_playback_shuffle(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "new_state": NEG_NEW_STATE[NEG_TEST_CASE],  # bool
            "target_device_id": NEG_TARGET_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            toggle_playback_shuffle(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_recently_played_tracks():
    # Positive Test Case
    positive_params = {
        "limit": POS_LIMIT,  # int
        "after": POS_AFTER,  # int
        "before": POS_BEFORE,  # int
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_recently_played_tracks.json"), "w") as file:
        file.write(json.dumps(get_recently_played_tracks(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "limit": NEG_LIMIT[NEG_TEST_CASE],  # int
            "after": NEG_AFTER[NEG_TEST_CASE],  # int
            "before": NEG_BEFORE[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_recently_played_tracks(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_the_users_queue():
    # Positive Test Case
    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_the_users_queue.json"), "w") as file:
        file.write(json.dumps(get_the_users_queue()))


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_add_item_to_playback_queue():
    # Positive Test Case
    positive_params = {
        "track_uri": POS_TRACK_URI,  # str
        "target_device_id": POS_TARGET_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/add_item_to_playback_queue.json"), "w") as file:
        file.write(json.dumps(add_item_to_playback_queue(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "track_uri": NEG_TRACK_URI[NEG_TEST_CASE],  # str
            "target_device_id": NEG_TARGET_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            add_item_to_playback_queue(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_add_several_items_to_playback_queue():
    # Positive Test Case
    positive_params = {
        "track_uris": POS_TRACK_URIS,  # list[str]
        "target_device_id": POS_TARGET_DEVICE_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/add_several_items_to_playback_queue.json"), "w") as file:
        file.write(json.dumps(add_several_items_to_playback_queue(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "track_uris": NEG_TRACK_URIS[NEG_TEST_CASE],  # list[str]
            "target_device_id": NEG_TARGET_DEVICE_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            add_several_items_to_playback_queue(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_playlist():
    # Positive Test Case
    positive_params = {
        "playlist_id": POS_PLAYLIST_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_playlist.json"), "w") as file:
        file.write(json.dumps(get_playlist(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_id": NEG_PLAYLIST_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_playlist(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_several_playlists():
    # Positive Test Case
    positive_params = {
        "playlist_ids": POS_PLAYLIST_IDS,  # list
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_several_playlists.json"), "w") as file:
        file.write(json.dumps(get_several_playlists(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_ids": NEG_PLAYLIST_IDS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_several_playlists(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_change_playlist_details():
    # Positive Test Case
    positive_params = {
        "playlist_id": POS_PLAYLIST_ID,  # str
        "name": "SpotipyTest",  # str
        "public": POS_PUBLIC,  # bool
        "collaborative": POS_COLLABORATIVE,  # bool
        "description": POS_DESCRIPTION,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/change_playlist_details.json"), "w") as file:
        file.write(json.dumps(change_playlist_details(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_id": NEG_PLAYLIST_ID[NEG_TEST_CASE],  # str
            "name": NEG_NAME[NEG_TEST_CASE],  # str
            "public": NEG_PUBLIC[NEG_TEST_CASE],  # bool
            "collaborative": NEG_COLLABORATIVE[NEG_TEST_CASE],  # bool
            "description": NEG_DESCRIPTION[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            change_playlist_details(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_playlist_items():
    # Positive Test Case
    positive_params = {
        "playlist_id": POS_PLAYLIST_ID,  # str
        "get_duration": POS_GET_DURATION,  # bool
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_playlist_items.json"), "w") as file:
        file.write(json.dumps(get_playlist_items(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_id": NEG_PLAYLIST_ID[NEG_TEST_CASE],  # str
            "get_duration": NEG_GET_DURATION[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_playlist_items(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_update_playlist_items():
    # Positive Test Case
    positive_params = {
        "playlist_id": POS_PLAYLIST_ID,  # str
        "track_uris": POS_TRACK_URIS,  # list[str]
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/update_playlist_items.json"), "w") as file:
        file.write(json.dumps(update_playlist_items(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_id": NEG_PLAYLIST_ID[NEG_TEST_CASE],  # str
            "track_uris": NEG_TRACK_URIS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            update_playlist_items(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_add_items_to_playlist():
    # Positive Test Case
    positive_params = {
        "playlist_id": "6bRkO7PLCXgmV4EJH52iU4",  # str
        "track_uris": POS_TRACK_URIS,  # list[str]
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/add_items_to_playlist.json"), "w") as file:
        file.write(json.dumps(add_items_to_playlist(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_id": NEG_PLAYLIST_ID[NEG_TEST_CASE],  # str
            "track_uris": NEG_TRACK_URIS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            add_items_to_playlist(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_remove_playlist_items():
    # Positive Test Case
    positive_params = {
        "playlist_id": "6bRkO7PLCXgmV4EJH52iU4",  # str
        "track_uris": POS_TRACK_URIS,  # list[str]
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/remove_playlist_items.json"), "w") as file:
        file.write(json.dumps(remove_playlist_items(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_id": NEG_PLAYLIST_ID[NEG_TEST_CASE],  # str
            "track_uris": NEG_TRACK_URIS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            remove_playlist_items(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_current_users_playlists():
    # Positive Test Case
    positive_params = {
        "limit": POS_LIMIT,  # int
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_current_users_playlists.json"), "w") as file:
        file.write(json.dumps(get_current_users_playlists(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "limit": NEG_LIMIT[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_current_users_playlists(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_users_playlists():
    # Positive Test Case
    positive_params = {
        "user_id": POS_USER_ID,  # str
        "limit": POS_LIMIT,  # int | None
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_users_playlists.json"), "w") as file:
        file.write(json.dumps(get_users_playlists(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "user_id": NEG_USER_ID[NEG_TEST_CASE],  # str
            "limit": NEG_LIMIT[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_users_playlists(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS or EXCLUDE_TEST, reason='passed')
def test_create_playlist():
    # Positive Test Case
    positive_params = {
        "user_id": POS_USER_ID,  # str
        "name": POS_NAME,  # str
        "public": POS_PUBLIC,  # bool
        "collaborative": POS_COLLABORATIVE,  # bool
        "description": POS_DESCRIPTION,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/create_playlist.json"), "w") as file:
        file.write(json.dumps(create_playlist(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "user_id": NEG_USER_ID[NEG_TEST_CASE],  # str
            "name": NEG_NAME[NEG_TEST_CASE],  # str
            "public": NEG_PUBLIC[NEG_TEST_CASE],  # bool
            "collaborative": NEG_COLLABORATIVE[NEG_TEST_CASE],  # bool
            "description": NEG_DESCRIPTION[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            create_playlist(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_playlist_cover_image():
    # Positive Test Case
    positive_params = {
        "playlist_id": POS_PLAYLIST_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_playlist_cover_image.b64"), "w") as file:
        file.write(image_to_b64(get_playlist_cover_image(**positive_params), "JPEG")) 

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_id": NEG_PLAYLIST_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_playlist_cover_image(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS or EXCLUDE_TEST, reason='passed')
def test_add_custom_playlist_cover_image():
    # Positive Test Case
    positive_params = {
        "playlist_id": "6bRkO7PLCXgmV4EJH52iU4",  # str
        "b64_image": POS_B64_IMAGE,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/add_custom_playlist_cover_image.json"), "w") as file:
        file.write(json.dumps(add_custom_playlist_cover_image(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_id": NEG_PLAYLIST_ID[NEG_TEST_CASE],  # str
            "b64_image": NEG_B64_IMAGE[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            add_custom_playlist_cover_image(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_save_playlist_state():
    # Positive Test Case
    positive_params = {
        "playlist_id": POS_PLAYLIST_ID,  # str
        "filepath": POS_FILEPATH,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/save_playlist_state.json"), "w") as file:
        file.write(json.dumps(save_playlist_state(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "playlist_id": NEG_PLAYLIST_ID[NEG_TEST_CASE],  # str
            "filepath": NEG_FILEPATH[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            save_playlist_state(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_search_for_item():
    # Positive Test Case
    positive_params = {
        "search_query": POS_SEARCH_QUERY,  # str
        "item_type": ['track'],  # list[Literal['album', 'artist', 'playlist', 'track']]
        "limit": POS_LIMIT,  # int
        "offset": POS_OFFSET,  # int
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/search_for_item.json"), "w") as file:
        file.write(json.dumps(search_for_item(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "search_query": NEG_SEARCH_QUERY[NEG_TEST_CASE],  # str
            "item_type": NEG_ITEM_TYPE[NEG_TEST_CASE],  # list[Literal['album', 'artist', 'playlist', 'track']]
            "limit": NEG_LIMIT[NEG_TEST_CASE],  # int
            "offset": NEG_OFFSET[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        try:
            search_for_item(**current_params)
        except CUSTOM_EXCEPTIONS:
            pass


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_track():
    # Positive Test Case
    positive_params = {
        "track_id": POS_TRACK_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_track.json"), "w") as file:
        file.write(json.dumps(get_track(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "track_id": NEG_TRACK_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_track(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_several_tracks():
    # Positive Test Case
    positive_params = {
        "track_ids": POS_TRACK_IDS,  # list[str]
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_several_tracks.json"), "w") as file:
        file.write(json.dumps(get_several_tracks(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "track_ids": NEG_TRACK_IDS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_several_tracks(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_users_saved_tracks():
    # Positive Test Case
    positive_params = {
        "limit": POS_LIMIT,  # int
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_users_saved_tracks.json"), "w") as file:
        file.write(json.dumps(get_users_saved_tracks(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "limit": NEG_LIMIT[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_users_saved_tracks(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_check_users_saved_tracks():
    # Positive Test Case
    positive_params = {
        "track_ids": POS_TRACK_IDS,  # list[str]
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/check_users_saved_tracks.json"), "w") as file:
        file.write(json.dumps(check_users_saved_tracks(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "track_ids": NEG_TRACK_IDS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            check_users_saved_tracks(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_tracks_audio_features():
    # Positive Test Case
    positive_params = {
        "track_id": POS_TRACK_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_tracks_audio_features.json"), "w") as file:
        file.write(json.dumps(get_tracks_audio_features(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "track_id": NEG_TRACK_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_tracks_audio_features(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_several_tracks_audio_features():
    # Positive Test Case
    positive_params = {
        "track_ids": POS_TRACK_IDS,  # list[str]
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_several_tracks_audio_features.json"), "w") as file:
        file.write(json.dumps(get_several_tracks_audio_features(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "track_ids": NEG_TRACK_IDS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_several_tracks_audio_features(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_current_users_profile():
    # Positive Test Case
    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_current_users_profile.json"), "w") as file:
        file.write(json.dumps(get_current_users_profile()))


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_users_top_items():
    # Positive Test Case
    positive_params = {
        "item_type": POS_ITEM_TYPE,  # Literal['artists', 'tracks']
        "time_range": POS_TIME_RANGE,  # Literal['short_term', 'medium_term', 'long_term']
        "limit": POS_LIMIT,  # int
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_users_top_items.json"), "w") as file:
        file.write(json.dumps(get_users_top_items(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "item_type": NEG_ITEM_TYPE[NEG_TEST_CASE],  # Literal['artists', 'tracks']
            "time_range": NEG_TIME_RANGE[NEG_TEST_CASE],  # Literal['short_term', 'medium_term', 'long_term']
            "limit": NEG_LIMIT[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_users_top_items(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_users_profile():
    # Positive Test Case
    positive_params = {
        "user_id": POS_USER_ID,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_users_profile.json"), "w") as file:
        file.write(json.dumps(get_users_profile(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "user_id": NEG_USER_ID[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_users_profile(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_several_users():
    # Positive Test Case
    positive_params = {
        "user_ids": POS_USER_IDS,  # list
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_several_users.json"), "w") as file:
        file.write(json.dumps(get_several_users(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "user_ids": NEG_USER_IDS[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_several_users(**current_params)


@pytest.mark.skipif(not RUN_ALL_TESTS, reason='passed')
def test_get_followed_artists():
    # Positive Test Case
    positive_params = {
        "get_type": POS_GET_TYPE,  # str
    }

    with open(absolute_path("code_backend/testing/file_test/spotify_web_api_outputs/get_followed_artists.json"), "w") as file:
        file.write(json.dumps(get_followed_artists(**positive_params)))

    # Negative Test Cases
    try:
        negative_params = {
            "get_type": NEG_GET_TYPE[NEG_TEST_CASE],
        }
    except IndexError:
        return

    # test for each negative value individually
    for neg_key, neg_value in negative_params.items():
        current_params = positive_params
        current_params.update({neg_key: neg_value})

        with pytest.raises(CUSTOM_EXCEPTIONS):
            get_followed_artists(**current_params)


if __name__ == '__main__':
    """"""
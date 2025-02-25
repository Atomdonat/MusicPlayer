from code_backend.secondary_methods import image_from_file, image_to_b64, url_to_uri, uri_to_id
from code_backend.spotify_web_api import *
from code_backend.development_and_testing.dev_bench_1 import *
import pytest


PC_DEVICE_ID = "a59d3a684d22772199a2fe97cdcdf563eaee9ac1"
HANDY_DEVICE_ID = "6f627a3903683807eb6a9edce9094c66a03d1ebc"
TEST_PLAYBACK_STATE = True
TEST_POSITION = 60000
TEST_REPEAT_MODE = "context"
TEST_VOLUME = 50
TEST_LIMIT = 2
TEST_AFTER = 1484811043508
TEST_BEFORE = 1484811043508
TEST_TRACK_URI = "spotify:track:14FP9BNWHekbC17tqcppOR"
TEST_TRACK_URIS = ["spotify:track:6zrR8itT7IfAdl5aS7YQyt", "spotify:track:14FP9BNWHekbC17tqcppOR"]


@pytest.fixture(autouse=True)
def ensure_valid_token():
    if check_token_expired(extended_token=False) == 0:
        refresh_access_token()


@pytest.mark.skip()
def test_framework(method: Callable, method_name: str, **kwargs):
    # Iterate and call
    print(f"\n{TEXTCOLOR}====================== {TEXTCOLOR}\n")

    try:
        print(f"Testing method {CCYAN}{method_name}(){TEXTCOLOR}:")
        method(**kwargs)
        print(f"Status: {CGREEN}SUCCESS{TEXTCOLOR}")
    except Exception as e:
        print(f"Status: {CRED}FAILED: {TEXTCOLOR}({CRED}{e}{TEXTCOLOR})")
    finally:
        print(f"\n{TEXTCOLOR}====================== {TEXTCOLOR}\n")


def test_get_playback_state():
    test_framework(method=get_playback_state, method_name="get_playback_state", )


def test_transfer_playback():
    test_framework(method=transfer_playback, method_name="transfer_playback", new_device_id="6f627a3903683807eb6a9edce9094c66a03d1ebc", playback_state=True)


def test_get_available_devices():
    test_framework(method=get_available_devices, method_name="get_available_devices", )


def test_get_currently_playing_track():
    test_framework(method=get_currently_playing_track, method_name="get_currently_playing_track", )


@pytest.mark.skip(reason="not working")
def test_start_or_resume_playback():
    test_framework(method=start_or_resume_playback, method_name="start_or_resume_playback", target_device_id="a59d3a684d22772199a2fe97cdcdf563eaee9ac1")


def test_pause_playback():
    test_framework(method=pause_playback, method_name="pause_playback", )


def test_skip_to_next():
    test_framework(method=skip_to_next, method_name="skip_to_next", target_device_id="a59d3a684d22772199a2fe97cdcdf563eaee9ac1")


def test_skip_to_previous():
    test_framework(method=skip_to_previous, method_name="skip_to_previous", target_device_id="a59d3a684d22772199a2fe97cdcdf563eaee9ac1")


def test_seek_to_position():
    test_framework(method=seek_to_position, method_name="seek_to_position", position_ms=60000, target_device_id="a59d3a684d22772199a2fe97cdcdf563eaee9ac1")


def test_set_repeat_mode():
    test_framework(method=set_repeat_mode, method_name="set_repeat_mode", new_repeat_mode="context", target_device_id="a59d3a684d22772199a2fe97cdcdf563eaee9ac1")


def test_set_playback_volume():
    test_framework(method=set_playback_volume, method_name="set_playback_volume", new_volume=50, target_device_id="a59d3a684d22772199a2fe97cdcdf563eaee9ac1")


def test_toggle_playback_shuffle():
    test_framework(method=toggle_playback_shuffle, method_name="toggle_playback_shuffle", new_state=False, target_device_id="a59d3a684d22772199a2fe97cdcdf563eaee9ac1")


def test_get_recently_played_tracks():
    test_framework(method=get_recently_played_tracks, method_name="get_recently_played_tracks", limit=2, after=1484811043508, before=1484811043508)


def test_get_the_users_queue():
    test_framework(method=get_the_users_queue, method_name="get_the_users_queue", )


def test_add_item_to_playback_queue():
    test_framework(method=add_item_to_playback_queue, method_name="add_item_to_playback_queue", track_uri="spotify:track:14FP9BNWHekbC17tqcppOR", target_device_id="a59d3a684d22772199a2fe97cdcdf563eaee9ac1")


def test_add_several_items_to_playback_queue():
    test_framework(method=add_several_items_to_playback_queue, method_name="add_several_items_to_playback_queue", track_uris=['spotify:track:6zrR8itT7IfAdl5aS7YQyt', 'spotify:track:14FP9BNWHekbC17tqcppOR'], target_device_id="a59d3a684d22772199a2fe97cdcdf563eaee9ac1")



if __name__ == "__main__":
    test_methods = [
        test_get_playback_state,
        test_transfer_playback,
        test_get_available_devices,
        test_get_currently_playing_track,
        test_start_or_resume_playback,
        test_pause_playback,
        test_skip_to_next,
        test_skip_to_previous,
        test_seek_to_position,
        test_set_repeat_mode,
        test_set_playback_volume,
        test_toggle_playback_shuffle,
        test_get_recently_played_tracks,
        test_get_the_users_queue,
        test_add_item_to_playback_queue,
        test_add_several_items_to_playback_queue,
    ]

    # for current_method in test_methods:
    #     current_method()
from code_backend.secondary_methods import image_from_file, image_to_b64, url_to_uri, uri_to_id
from code_backend.spotify_web_api import *
import pytest

TEST_ALBUM_ID = "79fnwKynD56xIXBVWkyaE5"
TEST_ALBUM_URI = "spotify:album:79fnwKynD56xIXBVWkyaE5"
TEST_ALBUM_IDS = ["79fnwKynD56xIXBVWkyaE5", "7CI6R1kJLUMfBl4FOKP8nc"]
test_artist_id = "6XyY86QOPPrYVGvF9ch6wz"
test_artist_ids = ["6XyY86QOPPrYVGvF9ch6wz", "00YTqRClk82aMchQQpYMd5"]
test_playlist_id = "6bRkO7PLCXgmV4EJH52iU4"
test_playlist_uri = "spotify:playlist:6bRkO7PLCXgmV4EJH52iU4"
test_track_id = "14FP9BNWHekbC17tqcppOR"
test_track_uri = "spotify:track:14FP9BNWHekbC17tqcppOR"
test_track_uris = ["spotify:track:6zrR8itT7IfAdl5aS7YQyt", "spotify:track:14FP9BNWHekbC17tqcppOR"]
test_track_ids = ["6zrR8itT7IfAdl5aS7YQyt", "14FP9BNWHekbC17tqcppOR"]
test_user_id = "simonluca1"
test_b64_image = image_to_b64(image_from_file(NO_IMAGE_PATH), image_format="PNG")
test_limit = 2
test_offset = 0
new_order = ["spotify:track:14FP9BNWHekbC17tqcppOR", "spotify:track:6zrR8itT7IfAdl5aS7YQyt"]


@pytest.fixture(scope="session", autouse=True)
def ensure_valid_token():
    if check_token_expired(extended_token=False) == 0:
        request_regular_token()

    if check_token_expired(extended_token=True) == 0:
        request_extended_token()


@pytest.mark.skip(reason="Visual Framework for tests; no test worthy content here")
def test_framework(method_dict: dict):
    # Iterate and call
    print(f"\n{TEXTCOLOR}====================== {TEXTCOLOR}\n")
    for name, method_data in method_dict.items():
        func = method_data["function"]
        args = method_data.get("args", ())
        kwargs = method_data.get("kwargs", {})
        try:
            print(f"Testing method {CCYAN}{name}(){TEXTCOLOR}:")
            func(*args, **kwargs)
            print(f"Status: {CGREEN}SUCCESS{TEXTCOLOR}")
        except Exception as e:
            print(f"Status: {CRED}FAILED: {TEXTCOLOR}({CRED}{e}{TEXTCOLOR})")
        finally:
            print(f"\n{TEXTCOLOR}====================== {TEXTCOLOR}\n")


def test_regular_methods():
    # Test methods using the regular access token
    regular_api_methods = {
        "api_request_data": {
            "function": api_request_data,
            "args": (),
            "kwargs": {
                "url": f"https://api.spotify.com/v1/albums/{TEST_ALBUM_ID}?market={MARKET}",
                "request_type": "GET",
                "overwrite_header": {}
            }
        },
        "get_album": {
            "function": get_album,
            "args": (),
            "kwargs": {
                "album_id": TEST_ALBUM_ID
            }
        },
        "get_several_albums": {
            "function": get_several_albums,
            "args": (),
            "kwargs": {
                "album_ids": TEST_ALBUM_IDS
            }
        },
        "get_album_tracks": {
            "function": get_album_tracks,
            "args": (),
            "kwargs": {
                "album_id": TEST_ALBUM_ID
            }
        },
        "check_users_saved_albums": {
            "function": check_users_saved_albums,
            "args": (),
            "kwargs": {
                "album_ids": TEST_ALBUM_IDS
            }
        },
        "get_artist": {
            "function": get_artist,
            "args": (),
            "kwargs": {
                "artist_id": test_artist_id
            }
        },
        "get_several_artists": {
            "function": get_several_artists,
            "args": (),
            "kwargs": {
                "artist_ids": test_artist_ids
            }
        },
        "get_artists_albums": {
            "function": get_artists_albums,
            "args": (),
            "kwargs": {
                "artist_id": test_artist_id,
                "limit": test_limit
            }
        },
        "get_artists_top_tracks": {
            "function": get_artists_top_tracks,
            "args": (),
            "kwargs": {
                "artist_id": test_artist_id
            }
        },
        "remove_playlist_items": {
            "function": remove_playlist_items,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id,
                "track_uris": test_track_uris
            }
        },
        "add_items_to_playlist": {
            "function": add_items_to_playlist,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id,
                "uris": test_track_uris
            }
        },
        "get_playlist_items": {
            "function": get_playlist_items,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id
            }
        },
        "get_playlist": {
            "function": get_playlist,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id
            }
        },
        "get_current_users_playlists": {
            "function": get_current_users_playlists,
            "args": (),
            "kwargs": {
                "limit": test_limit
            }
        },
        "get_users_playlists": {
            "function": get_users_playlists,
            "args": (),
            "kwargs": {
                "user_id": test_user_id,
                "limit": test_limit
            }
        },
        "get_playlist_cover_image": {
            "function": get_playlist_cover_image,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id
            }
        },
        "get_track": {
            "function": get_track,
            "args": (),
            "kwargs": {
                "track_id": test_track_id
            }
        },
        "get_several_tracks": {
            "function": get_several_tracks,
            "args": (),
            "kwargs": {
                "track_ids": test_track_ids
            }
        },
        "get_users_saved_tracks": {
            "function": get_users_saved_tracks,
            "args": (),
            "kwargs": {
                "limit": test_limit
            }
        },
        "check_users_saved_tracks": {
            "function": check_users_saved_tracks,
            "args": (),
            "kwargs": {
                "check_ids": test_track_ids
            }
        },
        "get_current_users_profile": {
            "function": get_current_users_profile,
            "args": (),
            "kwargs": {}
        },
        "get_users_top_items": {
            "function": get_users_top_items,
            "args": (),
            "kwargs": {
                "item_type": "tracks",
                "time_range": "medium_term",
                "limit": test_limit
            }
        },
        "get_users_profile": {
            "function": get_users_profile,
            "args": (),
            "kwargs": {
                "user_id": test_user_id
            }
        },
        "get_followed_artists": {
            "function": get_followed_artists,
            "args": (),
            "kwargs": {
                "get_type": "artist"
            }
        },
        "get_several_playlists":{
            "function": get_several_playlists,
            "args": (),
            "kwargs": {
                "playlist_ids": ['6nlNwRp9CYsnme17lYjGmU', '43eVLiCt71PSewI2UWHYSq']
            }
        },
        "get_several_users": {
            "function": get_several_users,
            "args": (),
            "kwargs": {
                "user_ids": ["simonluca1","w3bjopyh7hdxp7ypr7s1yp0ki"]
            }
        }
    }

    test_framework(regular_api_methods)


def test_playlist_modifier():
    test_playlist_id_2:str

    def create_new_playlist():
        print(f"\n{TEXTCOLOR}====================== {TEXTCOLOR}\n")
        try:
            print(f"Testing method {CCYAN}create_playlist(){TEXTCOLOR}:")
            playlist_id_2 = uri_to_id(list(
                create_playlist(
                    user_id=test_user_id,
                    name="test_name",
                    public=True,
                    collaborative=False,
                    description="test_description"
                ).keys()
            )[0])
            print(f"{CGREEN}SUCCESS{TEXTCOLOR}")
            return playlist_id_2
        except Exception as e:
            print(f"{CRED}FAILED: {TEXTCOLOR}({CRED}{e}{TEXTCOLOR})")
            sys.exit(1)

    new_playlist = 0
    if new_playlist == 0:
        test_playlist_id_2 = url_to_uri("https://open.spotify.com/playlist/1BBkq3U5pR34vtI6tN4DBr?si=d409f04ba5374541",
                   to_id=True)
    else:
        test_playlist_id_2 = create_new_playlist()

    pl_modifying_methods = {
        "update_playlist_items": {
            "function": update_playlist_items,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id_2,
                "uris": new_order
            }
        },
        "add_custom_playlist_cover_image": {
            "function": add_custom_playlist_cover_image,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id_2,
                "b64_image": test_b64_image
            }
        },
        "change_playlist_details": {
            "function": change_playlist_details,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id_2,
                "name": "test_name_2",
                "public": False,
                "collaborative": False,
                "description": "test_description_2"
            }
        }
    }

    test_framework(pl_modifying_methods)


def test_extended_methods():
    # Test extended token methods
    ext_methods = {
        "get_tracks_audio_features": {
            "function": get_tracks_audio_features,
            "args": (),
            "kwargs": {
                "track_id": test_track_id
            }
        },
        "get_several_tracks_audio_features": {
            "function": get_several_tracks_audio_features,
            "args": (),
            "kwargs": {
                "track_ids": test_track_ids
            }
        }
    }

    test_framework(ext_methods)


if __name__ == '__main__':
    """Test manually or automated with pytest"""
    if check_token_expired(extended_token=False) == 0:
        request_regular_token()

    if check_token_expired(extended_token=True) == 0:
        request_extended_token()


    test_regular_methods()
    test_playlist_modifier()
    test_extended_methods()
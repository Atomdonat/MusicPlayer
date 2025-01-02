from code_backend.secondary_methods import image_from_file, image_to_b64
from code_backend.spotify_web_api import *


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
    test_b64_image = image_to_b64(image_from_file(NO_IMAGE_PATH), image_format="PNG")
    test_limit = 2
    test_offset = 0
    new_playlist_id = ""
    new_order = []

    methods = {
        "api_request_data": {
            "function": api_request_data,
            "args": (),
            "kwargs": {
                "url": f"https://api.spotify.com/v1/albums/{test_album_id}?market={MARKET}",
                "request_type": "GET",
                "overwrite_header": {}
            }
        },
        "get_album": {
            "function": get_album,
            "args": (),
            "kwargs": {
                "album_id": test_album_id
            }
        },
        "get_several_albums": {
            "function": get_several_albums,
            "args": (),
            "kwargs": {
                "album_ids": test_album_ids
            }
        },
        "get_album_tracks": {
            "function": get_album_tracks,
            "args": (),
            "kwargs": {
                "album_id": test_album_id
            }
        },
        "check_users_saved_albums": {
            "function": check_users_saved_albums,
            "args": (),
            "kwargs": {
                "album_ids": test_album_ids
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
                "album_id": test_album_id,
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
        "create_playlist": {
            "function": create_playlist,
            "args": (),
            "kwargs": {
                "user_id": test_user_id,
                "name": "test_name",
                "public": True,
                "collaborative": False,
                "description": "test_description"
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
        "change_playlist_details": {
            "function": change_playlist_details,
            "args": (),
            "kwargs": {
                "playlist_id": new_playlist_id,
                "name": "test_name_2",
                "public": False,
                "collaborative": False,
                "description": "test_description_2"
            }
        },
        "get_playlist_items": {
            "function": get_playlist_items,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id
            }
        },
        "update_playlist_items": {
            "function": update_playlist_items,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id,
                "uris": new_order
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
        "add_custom_playlist_cover_image": {
            "function": add_custom_playlist_cover_image,
            "args": (),
            "kwargs": {
                "playlist_id": test_playlist_id,
                "b64_image": test_b64_image
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
        }
    }

    request_regular_token()

    # Iterate and call
    a = ""
    for name, method_data in methods.items():
        func = method_data["function"]
        args = method_data.get("args", ())
        kwargs = method_data.get("kwargs", {})
        try:
            func(*args, **kwargs)
            print(f"{CGREEN}{name.ljust(35)} OK{TEXTCOLOR}")
        except Exception as e:
            print(f"{CRED}{name.ljust(35)} failed {TEXTCOLOR}({CRED}{e}{TEXTCOLOR})")

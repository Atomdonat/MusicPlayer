import json

from code_backend.shared_config import *
from code_backend.testing.dev_bench_2 import Album, Artist, Playlist, Track, User, ItemQueues
from code_backend.secondary_methods import check_token_expired,print_error
import code_backend.spotify_web_api as sp_api
from code_backend.music_classes import APP_DATABASE
import pytest


_TEST_ALBUM_ID = "79fnwKynD56xIXBVWkyaE5"
_TEST_ARTIST_ID = "6XyY86QOPPrYVGvF9ch6wz"
_TEST_PLAYLIST_ID = "6bRkO7PLCXgmV4EJH52iU4"
_TEST_TRACK_ID = "14FP9BNWHekbC17tqcppOR"
_TEST_USER_ID = "simonluca1"

_TEST_ALBUM_DICT = {"spotify:album:0000000000000000000000": {"album_id": "0000000000000000000000", "album_name": "dummy", "album_url": "", "album_image": "", "genre_names": "[]", "total_duration": 0, "track_count": 0, "artist_ids": "[]", "track_ids": "[]", "popularity": 0, "blacklisted": 0, "album_json": "{\"album_type\": \"${album_type}\", \"artists\": [{\"external_urls\": {\"spotify\": \"${artists_1_external_urls_spotify}\"}, \"href\": \"${artists_1_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${artists_1_name}\", \"type\": \"${artists_1_type}\", \"uri\": \"${artists_1_uri}\"}], \"copyrights\": [{\"text\": \"${copyrights_1_text}\", \"type\": \"${copyrights_1_type}\"}, {\"text\": \"${copyrights_2_text}\", \"type\": \"${copyrights_2_type}\"}], \"external_ids\": {\"upc\": \"${external_ids_upc}\"}, \"external_urls\": {\"spotify\": \"${external_urls_spotify}\"}, \"genres\": [], \"href\": \"${href}\", \"id\": \"0000000000000000000000\", \"images\": [{\"height\": \"${images_1_height}\", \"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"width\": \"${images_1_width}\"}, {\"height\": \"${images_2_height}\", \"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"width\": \"${images_2_width}\"}], \"is_playable\": \"${is_playable}\", \"label\": \"${label}\", \"name\": \"${name}\", \"popularity\": \"${popularity}\", \"release_date\": \"${release_date}\", \"release_date_precision\": \"${release_date_precision}\", \"total_tracks\": \"${total_tracks}\", \"tracks\": {\"href\": \"${tracks_href}\", \"items\": [{\"artists\": [{\"external_urls\": {\"spotify\": \"${tracks_items_1_artists_1_external_urls_spotify}\"}, \"href\": \"${tracks_items_1_artists_1_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${tracks_items_1_artists_1_name}\", \"type\": \"${tracks_items_1_artists_1_type}\", \"uri\": \"${tracks_items_1_artists_1_uri}\"}], \"disc_number\": \"${tracks_items_1_disc_number}\", \"duration_ms\": \"${tracks_items_1_duration_ms}\", \"explicit\": \"${tracks_items_1_explicit}\", \"external_urls\": {\"spotify\": \"${tracks_items_1_external_urls_spotify}\"}, \"href\": \"${tracks_items_1_href}\", \"id\": \"0000000000000000000000\", \"is_local\": \"${tracks_items_1_is_local}\", \"is_playable\": \"${tracks_items_1_is_playable}\", \"name\": \"${tracks_items_1_name}\", \"preview_url\": \"${tracks_items_1_preview_url}\", \"track_number\": \"${tracks_items_1_track_number}\", \"type\": \"${tracks_items_1_type}\", \"uri\": \"${tracks_items_1_uri}\"}, {\"artists\": [{\"external_urls\": {\"spotify\": \"${tracks_items_2_artists_1_external_urls_spotify}\"}, \"href\": \"${tracks_items_2_artists_1_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${tracks_items_2_artists_1_name}\", \"type\": \"${tracks_items_2_artists_1_type}\", \"uri\": \"${tracks_items_2_artists_1_uri}\"}], \"disc_number\": \"${tracks_items_2_disc_number}\", \"duration_ms\": \"${tracks_items_2_duration_ms}\", \"explicit\": \"${tracks_items_2_explicit}\", \"external_urls\": {\"spotify\": \"${tracks_items_2_external_urls_spotify}\"}, \"href\": \"${tracks_items_2_href}\", \"id\": \"0000000000000000000000\", \"is_local\": \"${tracks_items_2_is_local}\", \"is_playable\": \"${tracks_items_2_is_playable}\", \"name\": \"${tracks_items_2_name}\", \"preview_url\": \"${tracks_items_2_preview_url}\", \"track_number\": \"${tracks_items_2_track_number}\", \"type\": \"${tracks_items_2_type}\", \"uri\": \"${tracks_items_2_uri}\"}], \"limit\": \"${tracks_limit}\", \"next\": \"${tracks_next}\", \"offset\": \"${tracks_offset}\", \"previous\": \"${tracks_previous}\", \"total\": \"${tracks_total}\"}, \"type\": \"${type}\", \"uri\": \"${uri}\"}"}}
_TEST_ARTIST_DICT = {"spotify:artist:0000000000000000000000": {"artist_id": "0000000000000000000000", "artist_name": "dummy", "artist_url": "", "artist_image": "", "genre_names": "[]", "follower": 0, "album_ids": "[]", "playlist_ids": "[]", "top_track_ids": "[]", "popularity": 0, "blacklisted": 0, "artist_json": "{\"external_urls\": {\"spotify\": \"${external_urls_spotify}\"}, \"followers\": {\"href\": \"${followers_href}\", \"total\": \"${followers_total}\"}, \"genres\": [\"${genres_1}\", \"${genres_2}\"], \"href\": \"${href}\", \"id\": \"0000000000000000000000\", \"images\": [{\"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"height\": \"${images_1_height}\", \"width\": \"${images_1_width}\"}, {\"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"height\": \"${images_2_height}\", \"width\": \"${images_2_width}\"}], \"name\": \"${name}\", \"popularity\": \"${popularity}\", \"type\": \"${type}\", \"uri\": \"${uri}\"}"}}
_TEST_PLAYLIST_DICT = {"spotify:track:0000000000000000000000": {"track_id": "0000000000000000000000", "track_name": "dummy", "track_url": "", "track_image": "", "genre_names": "[]", "track_duration": 0, "album_ids": "[]", "artist_ids": "[]", "playlist_ids": "[]", "popularity": 0, "blacklisted": 0, "track_json": "{\"album\": {\"album_type\": \"${album_album_type}\", \"artists\": [{\"external_urls\": {\"spotify\": \"${album_artists_1_external_urls_spotify}\"}, \"href\": \"${album_artists_1_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${album_artists_1_name}\", \"type\": \"${album_artists_1_type}\", \"uri\": \"${album_artists_1_uri}\"}], \"external_urls\": {\"spotify\": \"${album_external_urls_spotify}\"}, \"href\": \"${album_href}\", \"id\": \"0000000000000000000000\", \"images\": [{\"height\": \"${album_images_1_height}\", \"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"width\": \"${album_images_1_width}\"}, {\"height\": \"${album_images_2_height}\", \"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"width\": \"${album_images_2_width}\"}], \"is_playable\": \"${album_is_playable}\", \"name\": \"${album_name}\", \"release_date\": \"${album_release_date}\", \"release_date_precision\": \"${album_release_date_precision}\", \"total_tracks\": \"${album_total_tracks}\", \"type\": \"${album_type}\", \"uri\": \"${album_uri}\"}, \"artists\": [{\"external_urls\": {\"spotify\": \"${artists_1_external_urls_spotify}\"}, \"href\": \"${artists_1_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${artists_1_name}\", \"type\": \"${artists_1_type}\", \"uri\": \"${artists_1_uri}\"}], \"disc_number\": \"${disc_number}\", \"duration_ms\": \"${duration_ms}\", \"explicit\": \"${explicit}\", \"external_ids\": {\"isrc\": \"${external_ids_isrc}\"}, \"external_urls\": {\"spotify\": \"${external_urls_spotify}\"}, \"href\": \"${href}\", \"id\": \"0000000000000000000000\", \"is_local\": \"${is_local}\", \"is_playable\": \"${is_playable}\", \"name\": \"${name}\", \"popularity\": \"${popularity}\", \"preview_url\": \"${preview_url}\", \"track_number\": \"${track_number}\", \"type\": \"${type}\", \"uri\": \"${uri}\"}"}}
_TEST_TRACK_DICT = {"spotify:playlist:0000000000000000000000": {"playlist_id": "0000000000000000000000", "playlist_name": "dummy", "playlist_url": "", "playlist_image": "", "genre_names": "[]", "total_duration": 0, "track_count": 0, "owner_id": "[]", "track_ids": "[]", "popularity": 0, "blacklisted": 0, "playlist_json": "{\"collaborative\": \"${collaborative}\", \"external_urls\": {\"spotify\": \"${external_urls_spotify}\"}, \"followers\": {\"href\": \"${followers_href}\", \"total\": \"${followers_total}\"}, \"href\": \"${href}\", \"id\": \"0000000000000000000000\", \"images\": [{\"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"height\": \"${images_1_height}\", \"width\": \"${images_1_width}\"}], \"primary_color\": \"${primary_color}\", \"name\": \"${name}\", \"description\": \"${description}\", \"type\": \"${type}\", \"uri\": \"${uri}\", \"owner\": {\"href\": \"${owner_href}\", \"id\": \"0000000000000000000000\", \"type\": \"${owner_type}\", \"uri\": \"${owner_uri}\", \"display_name\": \"${owner_display_name}\", \"external_urls\": {\"spotify\": \"${owner_external_urls_spotify}\"}}, \"public\": \"${public}\", \"snapshot_id\": \"0000000000000000000000\", \"tracks\": {\"limit\": \"${tracks_limit}\", \"next\": \"${tracks_next}\", \"offset\": \"${tracks_offset}\", \"previous\": \"${tracks_previous}\", \"href\": \"${tracks_href}\", \"total\": \"${tracks_total}\", \"items\": [{\"added_at\": \"${tracks_items_1_added_at}\", \"primary_color\": \"${tracks_items_1_primary_color}\", \"video_thumbnail\": {\"url\": \"${tracks_items_1_video_thumbnail_url}\"}, \"is_local\": \"${tracks_items_1_is_local}\", \"added_by\": {\"external_urls\": {\"spotify\": \"${tracks_items_1_added_by_external_urls_spotify}\"}, \"id\": \"0000000000000000000000\", \"type\": \"${tracks_items_1_added_by_type}\", \"uri\": \"${tracks_items_1_added_by_uri}\", \"href\": \"${tracks_items_1_added_by_href}\"}, \"track\": {\"preview_url\": \"${tracks_items_1_track_preview_url}\", \"is_playable\": \"${tracks_items_1_track_is_playable}\", \"explicit\": \"${tracks_items_1_track_explicit}\", \"type\": \"${tracks_items_1_track_type}\", \"episode\": \"${tracks_items_1_track_episode}\", \"track\": \"${tracks_items_1_track_track}\", \"album\": {\"is_playable\": \"${tracks_items_1_track_album_is_playable}\", \"type\": \"${tracks_items_1_track_album_type}\", \"album_type\": \"${tracks_items_1_track_album_album_type}\", \"href\": \"${tracks_items_1_track_album_href}\", \"id\": \"0000000000000000000000\", \"images\": [{\"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"width\": \"${tracks_items_1_track_album_images_1_width}\", \"height\": \"${tracks_items_1_track_album_images_1_height}\"}, {\"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"width\": \"${tracks_items_1_track_album_images_2_width}\", \"height\": \"${tracks_items_1_track_album_images_2_height}\"}], \"name\": \"${tracks_items_1_track_album_name}\", \"release_date\": \"${tracks_items_1_track_album_release_date}\", \"release_date_precision\": \"${tracks_items_1_track_album_release_date_precision}\", \"uri\": \"${tracks_items_1_track_album_uri}\", \"artists\": [{\"external_urls\": {\"spotify\": \"${tracks_items_1_track_album_artists_1_external_urls_spotify}\"}, \"href\": \"${tracks_items_1_track_album_artists_1_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${tracks_items_1_track_album_artists_1_name}\", \"type\": \"${tracks_items_1_track_album_artists_1_type}\", \"uri\": \"${tracks_items_1_track_album_artists_1_uri}\"}], \"external_urls\": {\"spotify\": \"${tracks_items_1_track_album_external_urls_spotify}\"}, \"total_tracks\": \"${tracks_items_1_track_album_total_tracks}\"}, \"artists\": [{\"external_urls\": {\"spotify\": \"${tracks_items_1_track_artists_1_external_urls_spotify}\"}, \"href\": \"${tracks_items_1_track_artists_1_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${tracks_items_1_track_artists_1_name}\", \"type\": \"${tracks_items_1_track_artists_1_type}\", \"uri\": \"${tracks_items_1_track_artists_1_uri}\"}], \"disc_number\": \"${tracks_items_1_track_disc_number}\", \"track_number\": \"${tracks_items_1_track_track_number}\", \"duration_ms\": \"${tracks_items_1_track_duration_ms}\", \"external_ids\": {\"isrc\": \"${tracks_items_1_track_external_ids_isrc}\"}, \"external_urls\": {\"spotify\": \"${tracks_items_1_track_external_urls_spotify}\"}, \"href\": \"${tracks_items_1_track_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${tracks_items_1_track_name}\", \"popularity\": \"${tracks_items_1_track_popularity}\", \"uri\": \"${tracks_items_1_track_uri}\", \"is_local\": \"${tracks_items_1_track_is_local}\"}}, {\"added_at\": \"${tracks_items_2_added_at}\", \"primary_color\": \"${tracks_items_2_primary_color}\", \"video_thumbnail\": {\"url\": \"${tracks_items_2_video_thumbnail_url}\"}, \"is_local\": \"${tracks_items_2_is_local}\", \"added_by\": {\"external_urls\": {\"spotify\": \"${tracks_items_2_added_by_external_urls_spotify}\"}, \"id\": \"0000000000000000000000\", \"type\": \"${tracks_items_2_added_by_type}\", \"uri\": \"${tracks_items_2_added_by_uri}\", \"href\": \"${tracks_items_2_added_by_href}\"}, \"track\": {\"preview_url\": \"${tracks_items_2_track_preview_url}\", \"is_playable\": \"${tracks_items_2_track_is_playable}\", \"explicit\": \"${tracks_items_2_track_explicit}\", \"type\": \"${tracks_items_2_track_type}\", \"episode\": \"${tracks_items_2_track_episode}\", \"track\": \"${tracks_items_2_track_track}\", \"album\": {\"is_playable\": \"${tracks_items_2_track_album_is_playable}\", \"type\": \"${tracks_items_2_track_album_type}\", \"album_type\": \"${tracks_items_2_track_album_album_type}\", \"href\": \"${tracks_items_2_track_album_href}\", \"id\": \"0000000000000000000000\", \"images\": [{\"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"width\": \"${tracks_items_2_track_album_images_1_width}\", \"height\": \"${tracks_items_2_track_album_images_1_height}\"}, {\"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"width\": \"${tracks_items_2_track_album_images_2_width}\", \"height\": \"${tracks_items_2_track_album_images_2_height}\"}], \"name\": \"${tracks_items_2_track_album_name}\", \"release_date\": \"${tracks_items_2_track_album_release_date}\", \"release_date_precision\": \"${tracks_items_2_track_album_release_date_precision}\", \"uri\": \"${tracks_items_2_track_album_uri}\", \"artists\": [{\"external_urls\": {\"spotify\": \"${tracks_items_2_track_album_artists_1_external_urls_spotify}\"}, \"href\": \"${tracks_items_2_track_album_artists_1_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${tracks_items_2_track_album_artists_1_name}\", \"type\": \"${tracks_items_2_track_album_artists_1_type}\", \"uri\": \"${tracks_items_2_track_album_artists_1_uri}\"}], \"external_urls\": {\"spotify\": \"${tracks_items_2_track_album_external_urls_spotify}\"}, \"total_tracks\": \"${tracks_items_2_track_album_total_tracks}\"}, \"artists\": [{\"external_urls\": {\"spotify\": \"${tracks_items_2_track_artists_1_external_urls_spotify}\"}, \"href\": \"${tracks_items_2_track_artists_1_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${tracks_items_2_track_artists_1_name}\", \"type\": \"${tracks_items_2_track_artists_1_type}\", \"uri\": \"${tracks_items_2_track_artists_1_uri}\"}], \"disc_number\": \"${tracks_items_2_track_disc_number}\", \"track_number\": \"${tracks_items_2_track_track_number}\", \"duration_ms\": \"${tracks_items_2_track_duration_ms}\", \"external_ids\": {\"isrc\": \"${tracks_items_2_track_external_ids_isrc}\"}, \"external_urls\": {\"spotify\": \"${tracks_items_2_track_external_urls_spotify}\"}, \"href\": \"${tracks_items_2_track_href}\", \"id\": \"0000000000000000000000\", \"name\": \"${tracks_items_2_track_name}\", \"popularity\": \"${tracks_items_2_track_popularity}\", \"uri\": \"${tracks_items_2_track_uri}\", \"is_local\": \"${tracks_items_2_track_is_local}\"}}]}}"}}
_TEST_USER_DICT = {"spotify:user:0000000000000000000000": {"user_id": "0000000000000000000000", "user_name": "dummy", "user_url": "", "user_image": "", "follower": 0, "playlist_ids": "[]", "top_track_ids": "[]", "top_artist_ids": "[]", "top_genre_names": "[]", "popularity": 0, "blacklisted": 0, "user_json": "{\"display_name\": \"${display_name}\", \"external_urls\": {\"spotify\": \"${external_urls_spotify}\"}, \"href\": \"${href}\", \"id\": \"0000000000000000000000\", \"images\": [{\"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"height\": \"${images_1_height}\", \"width\": \"${images_1_width}\"}, {\"url\": \"https://i.scdn.co/image/ab67706c0000da840fe55ef44d453bf6d504264d\", \"height\": \"${images_2_height}\", \"width\": \"${images_2_width}\"}], \"type\": \"${type}\", \"uri\": \"${uri}\", \"followers\": {\"href\": \"${followers_href}\", \"total\": \"${followers_total}\"}}"}}


@pytest.fixture(scope="session", autouse=True)
def ensure_valid_token():
    if check_token_expired(extended_token=False) == 0:
        sp_api.request_regular_token()



@pytest.mark.skip(reason="Framework for tests; no test worthy content here")
def test_class_framework(class_type: str):
    class_map = {
        'album': Album,
        'artist': Artist,
        'playlist': Playlist,
        'track': Track,
        'user': User,
    }
    id_map = {
        "album": _TEST_ALBUM_ID,
        "artist": _TEST_ARTIST_ID,
        "playlist": _TEST_PLAYLIST_ID,
        "track": _TEST_TRACK_ID,
        "user": _TEST_USER_ID,
    }
    fetch_map = {
        "album": sp_api.get_album,
        "artist": sp_api.get_artist,
        "playlist": sp_api.get_playlist,
        "track": sp_api.get_track,
        "user": sp_api.get_users_profile
    }

    print(f"\n{TEXTCOLOR}====================== {TEXTCOLOR}\n")
    if APP_DATABASE.fetch_item(table_name=f"{class_type}s", item_id=id_map[class_type]):
        APP_DATABASE.remove_specific_item(table_name=f"{class_type}s", item_id=id_map[class_type])

    try:
        print(f"Testing {CCYAN}{class_map[class_type]}{TEXTCOLOR}:")
        item = fetch_map[class_type](id_map[class_type])[f"spotify:{class_type}:{id_map[class_type]}"]
        class_map[class_type](item)
        print(f"Status: {CGREEN}SUCCESS{TEXTCOLOR}")
    except Exception as e:
        print(f"Status: {CRED}FAILED {TEXTCOLOR}")
        print_error(error_message=e, more_infos=f"Error occurred while testing {class_map[class_type]}", exit_code=1)
    finally:
        print(f"\n{TEXTCOLOR}====================== {TEXTCOLOR}\n")

def test_Album():
    test_class_framework("album")

def test_Artist():
    test_class_framework("artist")

def test_Playlist():
    test_class_framework("playlist")

def test_Track():
    test_class_framework("track")

def test_User():
    test_class_framework("user")


def test_Itemqueue():
    def test_Itemqueue_fe():
        queue_map = [
            album_queue,
            artist_queue,
            playlist_queue,
            track_queue,
            user_queue
        ]

        for i in queue_map: print(i)

        item_queues = ItemQueues()
        item_queues.fetch_new_unknown_items()

        for i in queue_map: print(i)

if __name__ == '__main__':
    """"""
    test_class_framework()
import json
import sys

from spotify_access import spotify_client, request_multiple_items_of_same_type,market
from secondary_methods import image_to_b64, url_to_uri, split_list_into_chunks
import random
from PIL import Image


sp = spotify_client()


def all_shuffle(playlist_tracks: list) -> list:
    """
    Shuffles the given list using the PRNG random.randint(). Every item will occur exactly once.
    :param playlist_tracks: list to be shuffled
    :return: shuffled list
    """
    shuffled_playlist = []
    shuffle_track_ids = playlist_tracks
    while len(shuffle_track_ids) > 0:
        random_position = random.randint(0, len(shuffle_track_ids) - 1)
        current_track_id = shuffle_track_ids[random_position]
        shuffled_playlist.append(current_track_id)
        shuffle_track_ids.pop(random_position)
    return shuffled_playlist


def prepare_playlist_tracks(
        playlist: dict,
        chunk_size: int = 50,
        shuffle: bool = False
) -> list[list]:
    """
    Extracts every Track URI from a given Playlist instance and prepares them for further API calls.
    :param playlist: Playlist instance (e.g. from sp.playlist())
    :param chunk_size: API limit for items per request (https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks -> limit)
    :param shuffle: If to shuffle the Playlist Tracks
    :return: List of Track URI chunks
    """
    track_ids = []

    for current_offset in range(0, playlist["tracks"]["total"], chunk_size):
        items = sp.playlist_items(
            playlist_id=playlist["id"],
            limit=chunk_size,
            offset=current_offset,
            market=market
        )
        if items is None:
            print(f"\n\x1b[31mCould not fetch Playlist {playlist["id"]} items\x1b[30m\n")
            sys.exit(1)

        track_ids.extend([item["track"]["uri"] for item in items["items"]])

    if shuffle:
        track_ids = all_shuffle(track_ids)

    return track_ids


def reshuffle_playlist(playlist_id: str) -> None:
    """
    Reshuffles the given Playlist and either creates new Playlist or updates existing Playlist. (If successful either new Playlist appears in Spotify or the Tracks have a new order)
    :param playlist_id: Playlist to reshuffle
    :return: New/Updated Playlist in Spotify
    """
    # Fetch Playlist with API call
    playlist = sp.playlist(playlist_id=playlist_id, market=market)
    if not playlist:
        print(f"\n\x1b[31mPlaylist with the ID {playlist_id} does not exist\x1b[30m\n")
        sys.exit(1)

    # Prepare Playlist Tracks (Get Tracks and shuffle)
    playlist_tracks = prepare_playlist_tracks(playlist=playlist, shuffle=True)
    if playlist_tracks is None:
        print(f"\n\x1b[31mCould not prepare Playlist {playlist_id} Tracks\x1b[30m\n")
        sys.exit(1)

    # Create Playlist if not yours
    owner_not_me = playlist["owner"]["display_name"] != sp.current_user()["display_name"]
    if playlist and owner_not_me:
        new_playlist_json = sp.user_playlist_create(
            user=sp.current_user()['id'],
            name=f"{playlist["name"]} (Shuffled)",
            public=True,
            collaborative=False,
            description=f"reshuffled Playlist of {playlist["name"]} created by {playlist["owner"]["display_name"]}"
        )
        if new_playlist_json is None:
            print(f"\n\x1b[31mCould not create Playlist {playlist_id}\x1b[30m\n")
            sys.exit(1)

        b64_image = image_to_b64(Image.open("/home/simon/git_repos/MusicPlayer/Icons/Spotipy_if_no_image.png"), 'PNG')
        sp.playlist_upload_cover_image(playlist_id=new_playlist_json['id'], image_b64=b64_image)
        # uploading image can fail, but it's not that relevant to succeed
        playlist_id = new_playlist_json['id']

    # Remove Tracks if it is yours
    else:
        sp.playlist_remove_all_occurrences_of_items(
            playlist_id=playlist_id,
            items=playlist_tracks,
        )

    splitted_data = split_list_into_chunks(
        lst=playlist_tracks,
        # API limit for items per request is 100 (https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist -> uris)
        chunk_length=100
    )

    # add shuffled Tracks to (new) Playlist
    for chunk in splitted_data:
        sp.playlist_add_items(playlist_id=playlist_id, items=chunk)


if __name__ == '__main__':
    """
    Functionality:
        1. fetch Playlist
        2. get Tracks and shuffle them randomly (all_shuffle())
        3.1 create new Playlist if its not yours
        3.2 update existing Playlist if its yours
        4. add shuffled Tracks to Playlist
        5. no more Bad Spotify Shuffle needed (rerun to reshuffle)
    """
    playlist_uri = url_to_uri("https://open.spotify.com/playlist/1TufW5MXE6oDxo7KVw4ACV?si=47eb71b7ec9d4bd9")
    reshuffle_playlist(playlist_id=playlist_uri)

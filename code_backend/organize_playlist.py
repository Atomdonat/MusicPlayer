import json
import sys
from hashlib import sha256
import re

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
) -> (list, dict):
    """
    Extracts every Track URI from a given Playlist instance and prepares them for further API calls.
    :param playlist: Playlist instance (e.g. from sp.playlist())
    :param chunk_size: API limit for items per request (https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks -> limit)
    :param shuffle: If to shuffle the Playlist Tracks
    :return: List of Track URI chunks and Dict with all Tracks
    """
    track_ids = []
    track_dicts = []

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

        for item in items["items"]:
            track_ids.append(item["track"]["uri"])
            track_dicts.append({
                "uri": item["track"]["uri"],
                "name": item["track"]["name"],
                "artist": item["track"]["artists"][0]["name"]
            })

    if shuffle:
        track_ids = all_shuffle(track_ids)

    if len(track_ids) < 1 or len(track_dicts) < 1:
        print(f"\n\x1b[31mCould not fetch Playlist {playlist["id"]} items\x1b[30m\n")
        sys.exit(1)

    return track_ids, track_dicts


def fetch_playlist_with_tracks(playlist_id: str, shuffle: bool = False) -> (dict, (list, dict)):
    """
    Requests the Playlist Dict using the Spotify API then fetches every track from the playlist
    :param playlist_id: Spotify Playlist ID
    :param shuffle: If to shuffle the Playlist Tracks
    :return: Triple of (1) Playlist JSON, (2) list of Track URIs and (3) Dict with all Tracks JSON
    """

    playlist = sp.playlist(playlist_id=playlist_id, market=market)
    if not playlist:
        print(f"\n\x1b[31mPlaylist with the ID {playlist_id} does not exist\x1b[30m\n")
        sys.exit(1)

    playlist_tracks = prepare_playlist_tracks(playlist=playlist, shuffle=shuffle)
    if playlist_tracks is None:
        print(f"\n\x1b[31mCould not prepare Playlist {playlist_id} Tracks\x1b[30m\n")
        sys.exit(1)

    return playlist, playlist_tracks


def remove_duplicates(tracks: list[dict]) -> list:
    """
    Removes duplicate tracks (name and artist are the same) from a list of dicts
    :param tracks: list of tracks in the form of {"uri": ..., "name": ..., "artist": ...}
    :return: List of unique Tracks
    """
    uniques = {}
    for i in tracks:
        a = i["name"] + i["artist"]
        # Hash produces unique identifiers, if a collision occurs, the URI gets overwritten by the new one -> no collisions/duplicates
        uniques[sha256(a.encode("utf-8")).hexdigest()] = i["uri"]

    return list(uniques.values())

def organize_playlist(playlist_id: str, **kwargs) -> None:
    """
    Reorganizes the given Playlist and either creates new Playlist or updates existing Playlist. (If successful either new Playlist appears in Spotify or Playlist Content changed)
    :param playlist_id: Spotify Playlist ID to organize
    :return: New/Updated Playlist in Spotify
    """
    # Process Keyword Arguments
    shuffle_tracks: bool = ("shuffle" in kwargs and kwargs["shuffle"])  # shuffle exists and is True
    remove_tracks: list[str] = kwargs["remove"] if "remove" in kwargs else []

    fetched_playlist = fetch_playlist_with_tracks(playlist_id=playlist_id, shuffle=shuffle_tracks)
    playlist = fetched_playlist[0]
    playlist_tracks, track_dict = fetched_playlist[1]

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

    # empty Playlist if it is yours
    else:
        sp.playlist_remove_all_occurrences_of_items(
            playlist_id=playlist_id,
            items=playlist_tracks,
        )

    tracks_to_keep: list[str] = []
    unwanted_tracks: list[str] = []

    with open("debugging.json", "w") as f:
        f.write(json.dumps(track_dict))


    # Remove unwanted Tracks
    while len(remove_tracks) > 0:
        # Note: Can remove Tracks "unintentionally" e.g. if pattern is "Live in" (Live/Concert Version), "Live in the moment" by Portugal. The Man gets removed
        if remove_tracks[0] == "duplicate":
            # Todo: Check if playlist_tracks is the correct attribute
            print(playlist_tracks)
            unwanted_tracks.extend(remove_duplicates(track_dict))  # Todo continue here
            print(playlist_tracks)

        else:
            for track in track_dict:
                if not re.search(remove_tracks[0], track["name"], flags=re.IGNORECASE):
                    if track["uri"] not in tracks_to_keep:
                        tracks_to_keep.append(track["uri"])
                else:
                    if track["uri"] not in tracks_to_keep:
                        unwanted_tracks.append(track["uri"])

        remove_tracks.pop(0)

    if tracks_to_keep:
        playlist_tracks = tracks_to_keep

    split_data = split_list_into_chunks(
        lst=playlist_tracks,
        # API limit for items per request is 100 (https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist -> uris)
        chunk_length=100
    )

    # add shuffled Tracks to (new) Playlist
    for chunk in split_data:
        sp.playlist_add_items(playlist_id=playlist_id, items=chunk)


def fix_test():
    tst = [
        "spotify:track:6zrR8itT7IfAdl5aS7YQyt",
        "spotify:track:60a0Rd6pjrkxjPbaKzXjfq",
        "spotify:track:3gVhsZtseYtY1fMuyYq06F",
        "spotify:track:5DXGHZ3QDh0FcLXPMWTv9U",
        "spotify:track:60eOMEt3WNVX1m1jmApmnX"
    ]
    sp.playlist_remove_all_occurrences_of_items(
        playlist_id=test,
        items=tst,
    )
    sp.playlist_add_items(
        playlist_id=test,
        items=tst
    )



if __name__ == '__main__':
    test = url_to_uri("https://open.spotify.com/playlist/6bRkO7PLCXgmV4EJH52iU4?si=fbe6a250558f45f8", to_id=True)  # track_count=5
    prod = url_to_uri("https://open.spotify.com/playlist/6QjbdNFUe4SFNE82RTmcCJ?si=ca49189f2c994135", to_id=True)  # track_count=98

    fix_test()

    # Test case: shuffle
    organize_playlist(
        playlist_id=test,
        shuffle=True
    )
    # -> passed

    # Test case: remove
    organize_playlist(
        playlist_id=test,
        remove=[
            "Live in",
            "Live from",
            "Acoustic",
            "duplicate"
        ]
    )
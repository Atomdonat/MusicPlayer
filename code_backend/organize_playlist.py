from code_backend.shared_config import *
from code_backend.secondary_methods import image_to_b64, url_to_uri, split_list_into_chunks, uri_to_id, print_error, load_json, value_from_dict, key_from_dict,print_debug
import code_backend.spotify_web_api as sp_api


DEFAULT_IMAGE = image_to_b64(Image.open(NO_IMAGE_PATH), 'PNG')

# mps: 3
def all_shuffle(collection_tracks: list) -> list:
    """
    Shuffles the given list using the PRNG random.randint(). Every item will occur exactly once.
    :param collection_tracks: list to be shuffled
    :return: shuffled list
    """
    shuffled_collection = []
    shuffle_track_ids = collection_tracks
    while len(shuffle_track_ids) > 0:
        random_position = random.randint(0, len(shuffle_track_ids) - 1)
        current_track_id = shuffle_track_ids[random_position]
        shuffled_collection.append(current_track_id)
        shuffle_track_ids.pop(random_position)
    return shuffled_collection

# mps: 3
def all_shuffle_dict(collection_tracks: dict) -> dict:
    """
    Shuffles the given dict using the PRNG random.randint(). Every item will occur exactly once.
    :param collection_tracks: dict to be shuffled
    :return: shuffled dict
    """
    shuffled_collection = dict()
    shuffle_track_uris = list(collection_tracks.keys())

    while len(shuffle_track_uris) > 0:
        random_position = random.randint(0, len(shuffle_track_uris) - 1)
        current_track_uri = shuffle_track_uris[random_position]
        shuffled_collection[current_track_uri] = collection_tracks[current_track_uri]
        shuffle_track_uris.pop(random_position)
    return shuffled_collection


# mps: 3
def remove_duplicates(tracks: list[dict], get_removed: bool = False) -> set | tuple[set, set]:
    """
    Removes duplicate tracks (name and artist are the same) from a list of dicts
    :param tracks: list of tracks in the form of {"uri": ..., "name": ..., "artist": ...}
    :param get_removed: True: (no duplicates, removed duplicates); False: no duplicates
    :return: Set of unique Tracks (optional with the removed duplicates)
    """
    uniques = {}
    for i in tracks:
        a = i["name"] + i["artist"]
        # Hash produces unique identifiers, if a collision occurs, the URI gets overwritten by the new one -> no collisions/duplicates
        uniques[sha256(a.encode("utf-8")).hexdigest()] = i["uri"]

    all_tracks = set([i["uri"] for i in tracks])
    keep_tracks = set(uniques.values())
    remove_tracks = all_tracks - keep_tracks

    return (keep_tracks, remove_tracks) if get_removed else keep_tracks


# mps: 3
def organize_collection(collection_uri: str, **kwargs) -> None:
    """
    Reorganizes the given Playlist and either creates new Playlist or updates existing Playlist. (If successful either new Playlist appears in Spotify or Playlist Content changed)
    :param collection_uri: Spotify Collection URI to organize
    :return: New/Updated Playlist in Spotify
    """

    collection_id, collection_type = uri_to_id(spotify_uri=collection_uri, get_type=True)
    if not collection_type in ["album", "playlist"]:
        print_error(
            error_message="Collection {collection_type} is not valid.",
            more_infos="Valid options are: album, playlist",
            exit_code=1
        )

    # Process Keyword Arguments
    shuffle_tracks = bool("shuffle" in kwargs and kwargs["shuffle"])  # shuffle exists and is True
    remove_tracks = list(kwargs["remove"] if "remove" in kwargs else [])

    # Fetch tracks from collection
    match collection_type:
        case "album":
            collection_tracks = sp_api.get_album_tracks(album_id=collection_id)
        case "playlist":
            collection_tracks = sp_api.get_playlist_items(playlist_id=collection_id)
        case _:
            print(f"{CRED}Invalid collection type: {collection_type}{TEXTCOLOR}")
            return None

    if len(collection_tracks) < 1:
        print_error(
            error_message="Could not fetch items of '{collection_uri}'",
            exit_code=1
        )

    # get relevant Collection Data
    match collection_type:
        case "album":
            collection = sp_api.get_album(album_id=collection_id)
            collection_owner_id = [current_artist['id'] for current_artist in collection['artists']][0]
            collection_owner_name = collection["artists"][0]["name"]
            collection_owner_type = "Artist"
        case "playlist":
            collection = sp_api.get_playlist(playlist_id=collection_id)
            collection_owner_id = collection[collection_uri]['owner']['id']
            collection_owner_name = collection[collection_uri]['owner']['display_name']
            collection_owner_type = "User"
            old_description = collection[collection_uri]['description']

    # create Playlist if not yours
    current_user_id = value_from_dict(sp_api.get_current_users_profile())['id']
    if collection_owner_id != current_user_id:
        new_playlist = sp_api.create_playlist(
            user_id=current_user_id,
            name=f"{collection[collection_uri]["name"]} (Shuffled)",
            public=True,
            collaborative=False,
            description=f"reshuffled Playlist of '{collection[collection_uri]["name"]}' created by {collection_owner_type} '{collection_owner_name}'"
        )

        collection_id = uri_to_id(key_from_dict(new_playlist))
        sp_api.add_custom_playlist_cover_image(playlist_id=collection_id, b64_image=DEFAULT_IMAGE)

    # update Playlist name if it is yours (optional step)
    else:
        sp_api.change_playlist_details(
            playlist_id=collection_id,
            name=f"{collection[collection_uri]["name"]} (Shuffled)",
            public=True,
            collaborative=False,
            description=old_description
        )

    # Shuffle Tracks if wanted (get RNG on what duplicated tracks to remove)
    if shuffle_tracks:
        collection_tracks = all_shuffle_dict(collection_tracks)

    # Remove unwanted Tracks
    tracks_to_keep = set(collection_tracks.keys())
    while len(remove_tracks) > 0:
        if remove_tracks[0] == "duplicate":
            # Two Tracks are duplicates, if both track name and artist ID match
            hashable_collection_tracks = [{"uri": current_track_uri ,"name": current_track["name"], "artist": current_track["artists"][0]["id"]} for current_track_uri, current_track in collection_tracks.items()]
            tracks_to_keep = remove_duplicates(tracks=hashable_collection_tracks)

        else:
            debug_1 = remove_tracks[0]

            for current_track_uri, current_track in collection_tracks.items():
                # remove track if pattern matches
                # Note: Can remove Tracks "unintentionally" e.g. if pattern is "Live in" (Live/Concert Version), "Live in the moment" by 'Portugal. The Man' gets removed
                if re.search(pattern=remove_tracks[0], string=current_track["name"], flags=re.IGNORECASE):
                    tracks_to_keep.remove(current_track_uri)

        remove_tracks.pop(0)

    if tracks_to_keep:
        collection_tracks = list(tracks_to_keep)

    # Shuffle Tracks if wanted (Shuffle again, to avoid "bias" after removing multiple tracks)
    if shuffle_tracks:
        collection_tracks = all_shuffle(list(collection_tracks))

    sp_api.update_playlist_items(playlist_id=collection_id, uris=collection_tracks)


if __name__ == '__main__':
    """"""
    # organize_collection(
    #     collection_uri="spotify:playlist:6bRkO7PLCXgmV4EJH52iU4",
    #     shuffle=True,
    #     remove=["duplicate"]
    # )
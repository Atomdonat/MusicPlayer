from code_backend.shared_config import *
from code_backend.secondary_methods import (
    image_to_b64, url_to_uri, split_list_into_chunks, uri_to_id,
    load_json, value_from_dict, key_from_dict,print_debug, check_spotify_uris, check_spotify_uri
)
import code_backend.spotify_web_api as spotify
from code_backend.spotify_web_api import save_playlist_state
from code_backend.exceptions import InputException, CustomException, SpotifyUriException, SpotifyApiException


DEFAULT_IMAGE = image_to_b64(Image.open(NO_IMAGE_PATH), 'PNG')


def all_shuffle(collection_tracks: list) -> list:
    """
    Shuffles the given list using the PRNG random.randint(). Every item will occur exactly once.
    :param collection_tracks: list to be shuffled
    :return: shuffled list
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(collection_tracks, list):
        raise InputException(item_value=collection_tracks, valid_values="not empty list", valid_types=list)

    try:
        shuffled_collection = []
        shuffle_track_ids = collection_tracks
        while len(shuffle_track_ids) > 0:
            random_position = random.randint(0, len(shuffle_track_ids) - 1)
            current_track_id = shuffle_track_ids[random_position]
            shuffled_collection.append(current_track_id)
            shuffle_track_ids.pop(random_position)
        return shuffled_collection

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while shuffling collection: '{collection_tracks}'")


def all_shuffle_dict(collection_tracks: dict) -> dict:
    """
    Shuffles the given dict using the PRNG random.randint(). Every item will occur exactly once.
    :param collection_tracks: dict to be shuffled
    :return: shuffled dict
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(collection_tracks, dict):
        raise InputException(item_value=collection_tracks, valid_values="any dict", valid_types=dict)

    try:
        shuffle_track_uris = list(collection_tracks.keys())

        shuffled_track_uris = all_shuffle(shuffle_track_uris)
        return {current_track_uri: collection_tracks[current_track_uri] for current_track_uri in shuffled_track_uris}

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while shuffling collection:\n'{json.dumps(collection_tracks, indent=4)}'")


def remove_duplicates(tracks: list[dict], get_removed: bool = False) -> set | tuple[set, set]:
    """
    Removes duplicate tracks (name and artist are the same) from a list of dicts
    :param tracks: list of tracks in the form of {"uri": ..., "name": ..., "artist": ...}
    :param get_removed: True: (no duplicates, removed duplicates); False: no duplicates
    :return: Set of unique Tracks (optional with the removed duplicates)
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(tracks, list) or not all(isinstance(i, dict) for i in tracks):
        raise InputException(item_value=tracks, valid_values="list containing dicts", valid_types=list)

    if not isinstance(get_removed, bool):
        raise InputException(item_value=get_removed, valid_values=(True, False), valid_types=bool)

    for current_track in tracks:
        if not set(current_track.keys()) == {"uri", "name", "artist"}:
            raise InputException(item_value=current_track, valid_values="{'uri': ..., 'name': ..., 'artist': ...}", valid_types=dict)

    try:
        uniques = {}
        for current_track in tracks:
            a = current_track["name"] + current_track["artist"]
            # Hash produces unique identifiers, if a collision occurs, the URI gets overwritten by the new one -> no collisions/duplicates
            uniques[sha256(a.encode("utf-8")).hexdigest()] = current_track["uri"]

        all_tracks = set([i["uri"] for i in tracks])
        keep_tracks = set(uniques.values())
        remove_tracks = all_tracks - keep_tracks

        return (keep_tracks, remove_tracks) if get_removed else keep_tracks

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while removing duplicates: '[\n{",\n".join(str(i) for i in tracks)}\n''")


def organize_collection(collection_uri: str, **kwargs) -> None:
    """
    Reorganizes the given Playlist and either creates new Playlist or updates existing Playlist. (If successful either new Playlist appears in Spotify or Playlist Content changed)
    :param collection_uri: Spotify Collection URI to organize
    :param kwargs: valid kwargs: "shuffle=..." -> shuffle collection tracks; "remove=['duplicate']" -> remove duplicate tracks; "remove=['remove_string']" -> removes tracks containing 'remove_string' (supports regex pattern)
    :return: New/Updated Playlist in Spotify
    :raises InputException: if input is invalid
    :raises SpotifyApiException: if Exception related to Spotify API occurs
    :raises SpotifyUriException: if spotify uri is invalid
    """

    if not check_spotify_uri(collection_uri):
        raise SpotifyUriException(invalid_uri=collection_uri)

    collection_id, collection_type = uri_to_id(spotify_uri=collection_uri, get_type=True)

    # Process Keyword Arguments
    shuffle_tracks = bool("shuffle" in kwargs and kwargs["shuffle"])  # shuffle exists and is True
    remove_tracks = list(kwargs["remove"] if "remove" in kwargs else [])

    # Fetch tracks from collection
    match collection_type:
        case "album":
            collection_tracks = spotify.get_album_tracks(album_id=collection_id)
        case "playlist":
            collection_tracks = spotify.get_playlist_items(playlist_id=collection_id)
        case _:
            raise InputException(item_value=collection_uri, valid_values=("album", "playlist"), valid_types=str)

    if len(collection_tracks) < 1:
        raise SpotifyApiException(message=f"Could not fetch items of '{collection_uri}' while organizing collection")

    # get relevant Collection Data
    match collection_type:
        case "album":
            collection = spotify.get_album(album_id=collection_id)
            collection_owner_id = [current_artist['id'] for current_artist in collection['artists']][0]
            collection_owner_name = collection["artists"][0]["name"]
            collection_owner_type = "Artist"
        case "playlist":
            collection = spotify.get_playlist(playlist_id=collection_id)
            collection_owner_id = collection[collection_uri]['owner']['id']
            collection_owner_name = collection[collection_uri]['owner']['display_name']
            collection_owner_type = "User"
            old_description = collection[collection_uri]['description']

    # create Playlist if not yours
    current_user_id = value_from_dict(spotify.get_current_users_profile())['id']
    if collection_owner_id != current_user_id:
        new_playlist = spotify.create_playlist(
            user_id=current_user_id,
            name=f"{collection[collection_uri]["name"]} (Shuffled)",
            public=True,
            collaborative=False,
            description=f"reshuffled Playlist of '{collection[collection_uri]["name"]}' created by {collection_owner_type} '{collection_owner_name}'"
        )

        collection_id = uri_to_id(key_from_dict(new_playlist))
        spotify.add_custom_playlist_cover_image(playlist_id=collection_id, b64_image=DEFAULT_IMAGE)

    # update Playlist name if it is yours (optional step)
    else:
        new_name = f"{collection[collection_uri]["name"]} (Shuffled)" if not str(collection[collection_uri]["name"]).endswith("(Shuffled)") else collection[collection_uri]["name"]
        new_description = f"reshuffled Playlist" if old_description == "" else old_description

        spotify.change_playlist_details(
            playlist_id=collection_id,
            name=new_name,
            public=True,
            collaborative=False,
            description=new_description
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

    spotify.update_playlist_items(playlist_id=collection_id, track_uris=collection_tracks)


if __name__ == '__main__':
    """"""
    collection_uri = url_to_uri("https://open.spotify.com/playlist/5PPHCyClHIW1SgHWuRQLqh?si=ec3447c1b8af4d55")
    # collection_uri = url_to_uri(input("Enter Collection URL: "))
    organize_collection(collection_uri=collection_uri, shuffle=True)

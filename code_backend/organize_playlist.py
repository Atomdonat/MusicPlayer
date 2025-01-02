from spotify_access import spotify_client, request_multiple_items_of_same_type
from secondary_methods import image_to_b64, url_to_uri, split_list_into_chunks
from shared_config import *

# Warning: Not using `spotify_web_api.py` yet

sp = spotify_client()
DEFAULT_IMAGE = image_to_b64(Image.open(NO_IMAGE_PATH), 'PNG')


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


def prepare_collection_tracks(
        collection: dict,
        chunk_size: int = 50,
        shuffle: bool = False
) -> (list, dict):
    """
    Extracts every Track URI from a given Collection instance and prepares them for further API calls.
    :param collection: Collection instance (e.g. from sp.playlist(), sp.album(), etc.)
    :param chunk_size: API limit for items per request (https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks -> limit)
    :param shuffle: If to shuffle the Collection Tracks
    :return: List of Track URI chunks and Dict with all Tracks
    """
    track_ids = []
    track_dicts = []

    for current_offset in range(0, collection["tracks"]["total"], chunk_size):
        try:
            match collection["type"]:
                case "album":
                    items = sp.album_tracks(
                        album_id=collection["id"],
                        limit=chunk_size,
                        offset=current_offset,
                        market=MARKET
                    )
                case "playlist":
                    items = sp.playlist_items(
                        playlist_id=collection["id"],
                        limit=chunk_size,
                        offset=current_offset,
                        market=MARKET
                    )
                case _:
                    items = None

        except SpotifyException as e:
            print(f"\n\x1b[31mAn Error occurred while fetching the Collection {collection["id"]} items\x1b[30m\n{e}")
            sys.exit(1)

        if items is None:
            print(f"\n\x1b[31mCould not fetch Collection {collection["id"]} items\x1b[30m\n")
            sys.exit(1)

        # <--- debugging --->
        # with open("debugging.json", "w") as f:
        #     json.dump(items, f)
        # <--- end debugging --->

        match collection["type"]:
            case "album":
                for item in items["items"]:
                    if item["uri"] in track_ids:
                        continue
                    track_ids.append(item["uri"])
                    track_dicts.append({
                        "uri": item["uri"],
                        "name": item["name"],
                        "artist": item["artists"][0]["name"]
                    })
            case "playlist":
                for item in items["items"]:
                    if item["track"]["uri"] in track_ids:
                        continue
                    track_ids.append(item["track"]["uri"])
                    track_dicts.append({
                        "uri": item["track"]["uri"],
                        "name": item["track"]["name"],
                        "artist": item["track"]["artists"][0]["name"]
                    })

    if shuffle:
        track_ids = all_shuffle(track_ids)

    if len(track_ids) < 1 or len(track_dicts) < 1:
        print(f"\n\x1b[31mCould not fetch Collection {collection["id"]} items\x1b[30m\n")
        sys.exit(1)

    return track_ids, track_dicts


def fetch_collection_with_tracks(collection_id: str, collection_type: Literal["album", "playlist"], shuffle: bool = False) -> (dict, (list, dict)):
    """
    Requests the Playlist Dict using the Spotify API then fetches every track from the playlist
    :param collection_id: Spotify Collection ID
    :param collection_type: Spotify Collection Type
    :param shuffle: If to shuffle the Collection Tracks
    :return: Triple of (1) Collection JSON, (2) list of Track URIs and (3) Dict with all Tracks JSON
    """
    try:
        match collection_type:
            case "album":
                collection = sp.album(album_id=collection_id, market=MARKET)
            case "playlist":
                collection = sp.playlist(playlist_id=collection_id, market=MARKET)
            case _:
                collection = None

    except SpotifyException as e:
        print(f"\n\x1b[31mAn Error occurred while fetching the Collection {collection_id} items\x1b[30m\n{e}")
        sys.exit(1)

    if not collection:
        print(f"\n\x1b[31mCollection with the ID {collection_id} does not exist\x1b[30m\n")
        sys.exit(1)

    collection_tracks = prepare_collection_tracks(collection=collection, shuffle=shuffle)
    if collection_tracks is None:
        print(f"\n\x1b[31mCould not prepare Collection {collection_id} Tracks\x1b[30m\n")
        sys.exit(1)

    return collection, collection_tracks


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


def empty_playlist(collection_id, collection_tracks:list[str]) -> None:
    """
    Removing Tracks from Playlist while avoiding API limitations of removing more than 100 items per request
    :param collection_id: Collection ID
    :param collection_tracks: List containing Track URIs
    :return: empty Spotify Collection
    """
    limit = 100
    for current_offset in range(0, len(collection_tracks), limit):
        try:
            sp.playlist_remove_all_occurrences_of_items(
                playlist_id=collection_id,
                items=collection_tracks[current_offset:current_offset + limit],
            )
        except SpotifyException as e:
            print(f"\n\x1b[31mError occurred while removing Tracks from Playlist {collection_id}\n{e}\x1b[30m")
            sys.exit(1)


def organize_collection(collection_uri: str, **kwargs) -> None:
    """
    Reorganizes the given Playlist and either creates new Playlist or updates existing Playlist. (If successful either new Playlist appears in Spotify or Playlist Content changed)
    :param collection_uri: Spotify Collection URI to organize
    :return: New/Updated Playlist in Spotify
    """

    _, collection_type, collection_id = collection_uri.split(":")
    if not collection_type in ["album", "playlist"]:
        print(f"\n\x1b[31m Collection {collection_type} is not valid.\x1b[30m\nValid options are: album, playlist")
        sys.exit(1)

    # Process Keyword Arguments
    shuffle_tracks: bool = ("shuffle" in kwargs and kwargs["shuffle"])  # shuffle exists and is True
    remove_tracks: list[str] = kwargs["remove"] if "remove" in kwargs else []

    # Fetch Collection
    # noinspection PyTypeChecker
    fetched_collection = fetch_collection_with_tracks(
        collection_id=collection_id,
        collection_type=collection_type,
        shuffle=shuffle_tracks
    )

    collection = fetched_collection[0]
    collection_tracks, track_dict = fetched_collection[1]

    # <--- debugging --->
    # with open("debugging.json", "w") as file:
    #     json.dump(track_dict, file)
    #     sys.exit(13)
    # <--- end debugging --->

    # Create Playlist if not yours
    collection_owner = \
        collection["owner"]["display_name"] if collection_type == "playlist" \
        else collection["artists"][0]["name"]

    if collection_owner != sp.current_user()["display_name"]:
        try:
            new_playlist_json = sp.user_playlist_create(
                user=sp.current_user()['id'],
                name=f"{collection["name"]} (Shuffled)",
                public=True,
                collaborative=False,
                description=f"reshuffled Playlist of {collection["name"]} created by {collection_owner}"
            )
        except SpotifyException as e:
            print(f"\n\x1b[31mError occurred while creating the Playlist {collection_id}\x1b[30m\n",e)
            sys.exit(1)

        if new_playlist_json is None:
            print(f"\n\x1b[31mCould not create Playlist {collection_id}\x1b[30m\n")
            sys.exit(1)

        collection_id = new_playlist_json['id']

        try:
            sp.playlist_upload_cover_image(playlist_id=collection_id, image_b64=DEFAULT_IMAGE)
        except SpotifyException as e:
            print(f"\n\x1b[33mSetting Playlists {collection_id} Image did not work\n{e}\x1b[30m\n")

        try:
            sp.playlist_change_details(playlist_id=collection_id,description="Reshuffled Playlist")
        except SpotifyException as e:
            print(f"\n\x1b[33mSetting Playlists {collection_id} Description did not work\n{e}\x1b[30m\n")


    # empty Playlist if it is yours
    else:
        empty_playlist(collection_id, collection_tracks)

    tracks_to_keep: list[str] = []
    unwanted_tracks: list[str] = []

    # Remove unwanted Tracks
    while len(remove_tracks) > 0:
        # Note: Can remove Tracks "unintentionally" e.g. if pattern is "Live in" (Live/Concert Version), "Live in the moment" by Portugal. The Man gets removed
        if remove_tracks[0] == "duplicate":
            # Todo: Check if collection_tracks is the correct attribute
            print(collection_tracks)
            unwanted_tracks.extend(remove_duplicates(track_dict))  # Todo continue here
            print(collection_tracks)

        else:
            tmp = remove_tracks[0]
            for track in track_dict:
                if not re.search(remove_tracks[0], track["name"], flags=re.IGNORECASE):
                    if track["uri"] not in tracks_to_keep:
                        tracks_to_keep.append(track["uri"])
                else:
                    if track["uri"] not in tracks_to_keep:
                        unwanted_tracks.append(track["uri"])

        remove_tracks.pop(0)

    if tracks_to_keep:
        collection_tracks = tracks_to_keep

    split_data = split_list_into_chunks(
        lst=collection_tracks,
        # API limit for items per request is 100 (https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist -> uris)
        chunk_length=100
    )

    # add shuffled Tracks to (new) Playlist
    for chunk in split_data:
        sp.playlist_add_items(playlist_id=collection_id, items=chunk)


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

    # fix_test()
    #
    # # Test case: shuffle
    # organize_playlist(
    #     playlist_id=test,
    #     shuffle=True
    # )
    # # -> passed
    #
    # # Test case: remove
    # organize_playlist(
    #     playlist_id=test,
    #     remove=[
    #         "Live in",
    #         "Live from",
    #         "Acoustic",
    #         "duplicate"
    #     ]
    # )
    shuffle_lists = {
    # "linkin_park_shuffle": url_to_uri("https://open.spotify.com/playlist/1TufW5MXE6oDxo7KVw4ACV?si=b923e75e5b3c4065"),
    "current_shuffle": url_to_uri("https://open.spotify.com/playlist/6QjbdNFUe4SFNE82RTmcCJ?si=6df960bfc1f044b9"),
    # "depr_shuffle": url_to_uri("https://open.spotify.com/playlist/5kdy1Iw5b2ZfYoxJxJIGxi?si=9b16d37cb21c4bcc")
    }
    for name,uri in shuffle_lists.items():
        organize_collection(
            collection_uri=uri,
            shuffle=True,
            remove=[
                "duplicate"
            ]
        )
        print(f"organized {name}")
        sleep(2)  # <- no specific reason to be there

    # image = image_to_b64(Image.open("/home/simon/git_repos/MusicPlayer/Icons/Spotipy_Logo.png"), 'PNG')
    # if sp:
    #     sp.playlist_upload_cover_image(playlist_id="1TufW5MXE6oDxo7KVw4ACV", image_b64=image)

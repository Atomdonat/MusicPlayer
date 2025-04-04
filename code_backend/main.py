from code_backend.shared_config import *

import code_backend.organize_playlist as organize
import code_backend.spotify_web_api as spotify
from code_backend.database_access import APP_DATABASE
from code_backend.exceptions import SpotifyApiException, HttpException, InputException
from code_backend.music_classes import Album, Artist, Device, Playlist, Track, User
from code_backend.secondary_methods import (
    uri_to_id, load_json, url_to_uri, key_from_dict, check_limits
)
import code
import readline
import rlcompleter


BANNER = f"""{CSPOGREEN}
    ███    ███ ██    ██ ███████ ██  ██████    ██████  ██       █████  ██    ██ ███████ ██████  
    ████  ████ ██    ██ ██      ██ ██         ██   ██ ██      ██   ██  ██  ██  ██      ██   ██ 
    ██ ████ ██ ██    ██ ███████ ██ ██         ██████  ██      ███████   ████   █████   ██████  
    ██  ██  ██ ██    ██      ██ ██ ██         ██      ██      ██   ██    ██    ██      ██   ██ 
    ██      ██  ██████  ███████ ██  ██████    ██      ███████ ██   ██    ██    ███████ ██   ██ 
               
{TEND}"""


class Player:
    def __init__(self) -> None:
        self.player = spotify.get_playback_state()
        if self.player is not None:
            match self.player['context']['type']:
                case 'album':
                    self.current_collection = Album(uri_to_id(self.player['context']['uri']))
                case 'artist':
                    self.current_collection = Artist(uri_to_id(self.player['context']['uri']))
                case 'playlist':
                    self.current_collection = Playlist(uri_to_id(self.player['context']['uri']))
                case 'track':
                    self.current_collection = Track(uri_to_id(self.player['context']['uri']))
                case 'user':
                    self.current_collection = User(uri_to_id(self.player['context']['uri']))

            self.current_album = Album(album_id=self.player['item']['album']['id'])
            self.current_artist = Artist(artist_id=self.player['item']['artists'][0]['id'])
            self.current_track = Track(track_id=self.player['item']['id'])
            self.current_device = Device(self.player['device']['id'])
            self.dummy_player = bool(self.current_device.device_id == "0000000000000000000000000000000000000000")

            self.is_playing = bool(self.player['is_playing'])
            self.repeat_state = self.player['repeat_state']
            self.shuffle_state = bool(self.player['shuffle_state'])

        else:
            self.player = load_json("Databases/JSON_Files/spotify_player_dummy.json")
            self.current_album = Album(self.player["current_album_id"])
            self.current_artist = Artist(self.player["current_artist_id"])
            self.current_collection = Playlist(self.player["current_collection_id"])
            self.current_device = Device(self.player["current_device_id"])
            self.dummy_player = bool(self.current_device.device_id == "0000000000000000000000000000000000000000")
            self.current_track = Track(self.player["current_track_id"])
            self.is_playing = bool(self.player["is_playing"])
            self.repeat_state = self.player["repeat_state"]
            self.shuffle_state = bool(self.player["shuffle_state"])

        self.skip_blacklisted_items()

    def change_playing_state(self):
        """
        Switch the current playing state of Spotify Player

        :return:
        :raises HttpException: if request response code is not good
        """
        if not self.dummy_player:
            if self.is_playing:
                try:
                    spotify.pause_playback()
                    # returns Error 403 if playback is already paused
                    self.is_playing = False

                except HttpException:
                    spotify.start_or_resume_playback(target_device_id=self.current_device.device_id)
                    self.is_playing = True

            else:
                spotify.start_or_resume_playback(target_device_id=self.current_device.device_id)
                self.is_playing = True

    def initialize_player(self):
        """
        Get Information of the current Player state of Spotify (updates attributes)

        :raises SpotifyApiException: if Exception related to Spotify API occurs
        """
        if spotify.get_playback_state() is None:
            raise SpotifyApiException(f"No Spotify instance found\n{CCYAN}Please start Spotify and retry{TEXTCOLOR}")
        self.__init__()

    @property
    def progress(self) -> int:
        """
        Get the current progress of the playing track or episode

        :return: progress in milliseconds
        """
        if not self.dummy_player:
            playback_data = spotify.get_currently_playing_track()
            if playback_data:
                return playback_data["progress_ms"]
        else:
            return -1

    @progress.setter
    def progress(self, position_ms: int):
        """

        :param position_ms:
        :return:
        :raises InputException: if input is invalid
        """
        if not isinstance(position_ms, int):
            raise InputException(item_value=position_ms, valid_values="positive integer", valid_types=int)

        if not self.dummy_player:
            spotify.seek_to_position(position_ms=position_ms)
            self.progress = position_ms
        else:
            self.progress = -1

    def change_repeat_state(self, new_state: Literal['context', 'track', 'off']):
        """
        Change the current playing state of Spotify Player

        :param new_state: 'off': off, 'context': on, 'track': only repeat current track
        :raises InputException: if input is invalid
        """
        if not isinstance(new_state, str) or new_state not in ['context', 'track', 'off']:
            raise InputException(item_value=new_state, valid_values=('context', 'track', 'off'), valid_types=str)

        if not self.dummy_player:
            spotify.set_repeat_mode(new_repeat_mode=new_state)
            self.repeat_state = new_state

    def next_track(self):
        """
        Skips current track
        """
        if not self.dummy_player:
            spotify.skip_to_next()
            self.__init__()

    def prev_track(self):
        """
        Go to previous track (progress=0) or track start (progress>0)
        """
        if not self.dummy_player:
            spotify.skip_to_previous()
            self.__init__()

    def change_shuffle_state(self):
        if not self.dummy_player:
            self.shuffle_state = not self.shuffle_state
            spotify.toggle_playback_shuffle(new_state=self.shuffle_state)

    def set_volume(self, new_volume: int):
        """

        :param new_volume:
        :return:
        :raises InputException: if input is invalid
        """
        if not isinstance(new_volume, int) or 100 < new_volume < 0:
            raise InputException(item_value=new_volume, valid_values="0 <= new_volume <= 100", valid_types=int)

        if not self.dummy_player:
            spotify.set_playback_volume(new_volume=new_volume)

    def skip_blacklisted_items(self):
        """
        Skip Item if it is blacklisted in the Database
        """
        if self.dummy_player:
            return

        collection_id, collection_type = uri_to_id(self.player['context']['uri'], get_type=True)
        collection_is_blacklisted = APP_DATABASE.fetch_row(
            table_name=f"{collection_type}s",
            item_id=collection_id,
            table_column="blacklisted"
        )[0]
        album_is_blacklisted = APP_DATABASE.fetch_row(
            table_name='albums',
            item_id=self.current_album.album_id,
            table_column="blacklisted"
        )[0]
        artist_is_blacklisted = APP_DATABASE.fetch_row(
            table_name='artists',
            item_id=self.current_artist.artist_id,
            table_column="blacklisted"
        )[0]
        track_is_blacklisted = APP_DATABASE.fetch_row(
            table_name='tracks',
            item_id=self.current_track.track_id,
            table_column="blacklisted"
        )[0]

        if any([album_is_blacklisted, collection_is_blacklisted, artist_is_blacklisted, track_is_blacklisted]):
            self.next_track()


class SpotifyApp:
    """"""
    def __init__(self) -> None:
        """

        :raises SpotifyApiException: if Exception related to Spotify API occurs
        """
        available_markets = spotify.get_available_markets()
        if MARKET not in available_markets:
            raise SpotifyApiException(f"Market '{MARKET}' not available\n{CCYAN}Available markets: {available_markets}{TEXTCOLOR}")

        self.player = Player()

    @staticmethod
    def find_object(
        search_query: str,
        item_type: list[Literal["album", "artist", "playlist", "track"]],
        select_correct: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> dict | None:
        """
        Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or audiobooks that match a keyword string.

        **Better Search queries:**
        (1) You can narrow down your search using field filters. The available filters are album, artist, track, year, upc, tag:hipster, tag:new, isrc, and genre. Each field filter only applies to certain result types.
        (2) The artist and year filters can be used while searching albums, artists and tracks. You can filter on a single year or a range (e.g. 1955-1960).
        (3) The album filter can be used while searching albums and tracks.
        (4) The genre filter can be used while searching artists and tracks.
        (5) The isrc and track filters can be used while searching tracks.
        (6) The upc, tag:new and tag:hipster filters can only be used while searching albums. The tag:new filter will return albums released in the past two weeks and tag:hipster can be used to return only albums with the lowest 10% popularity.

        :param search_query: Your search query.
        :param item_type: A comma-separated list of item types to search across. Search results include hits from all the specified item types. For example: 'q=abacab&type=album,track' returns both albums and tracks matching "abacab".
        :param select_correct: True: Select correct item with CLI; False: return all items.
        :param limit: The maximum number of results to return in each item type. Default: 20. Minimum: 1. Maximum: 50.
        :param offset: The index of the first result to return. Use with limit to get the next page of search results. Default: 0. Minimum: 0. Maximum: 1000-limit.
        :return: Dict containing the Search response, in the form of {item_uri: item}
        :raises InputException: if input is invalid
        :raises LimitException: if limit is invalid
        """

        results = spotify.search_for_item(
            search_query=search_query,
            item_type=item_type,
            limit=limit,
            offset=offset
        )

        # Choose right one
        if select_correct:
            print(f"\n{TEXTCOLOR}These items are found by your search {search_query}:")
            item_counter = 1
            for item_uri, item in results.items():
                _, item_type = uri_to_id(spotify_uri=item_uri, get_type=True)
                match item_type:
                    case "album":
                        print(f"\t{str(item_counter).zfill(len(str(limit)))} Album: {item['name']} by {', '.join([current_artist['name'] for current_artist in item['artists']])}")
                    case "artist":
                        print(f"\t{str(item_counter).zfill(len(str(limit)))} Artist: {item['name']}")
                    case 'playlist':
                        print(f"\t{str(item_counter).zfill(len(str(limit)))} Playlist: {item['name']} by {item['owner']['display_name']}")
                    case "track":
                        print(f"\t{str(item_counter).zfill(len(str(limit)))} Track: {item['name']} ({item['album']['name']}) by {', '.join([current_artist['name'] for current_artist in item['artists']])}")

                item_counter += 1
            item_index = int(input(f"\nEnter the index of the item to return [1-{len(results.values())}]: "))
            correct_item_uri = list(results.keys())[item_index]
            return {correct_item_uri: results[correct_item_uri]}

        return results


    @staticmethod
    def random_tracks_by_genre(genre_name: str, track_count: int = 10, create_playlist: bool = False) -> dict | None:
        """
        Get random tracks by genre and either return them as a dict or create a new playlist with them.

        :param genre_name: what genre to search for
        :param track_count: how many tracks to return
        :param create_playlist: whether to create a new playlist
        :return: Dict containing Spotify Tracks, in the form of {track_uri: track} or (playlist_id, playlist_name)
        :raises InputException: if input is invalid
        :raises SpotifyApiException: if Exception related to Spotify API occurs
        """

        if not isinstance(genre_name, str):
            raise InputException(item_value=genre_name,valid_values="suitable string", valid_types=str)

        if not isinstance(track_count, int) or track_count < 0:
            raise InputException(item_value=track_count,valid_values="positive integer", valid_types=int)

        if not isinstance(create_playlist, bool):
            raise InputException(item_value=create_playlist,valid_values=(True, False), valid_types=bool)

        random_tracks = set()

        anti_loop = track_count
        tracks_per_request = min(10, track_count)
        while anti_loop > 0 and len(random_tracks) < track_count:
            random_offset = random.randint(0, 1000-tracks_per_request)
            results = spotify.search_for_item(
                search_query=f"genre:{genre_name}",
                item_type=["track"],
                limit=tracks_per_request,
                offset=random_offset
            )

            if results is None:
                raise SpotifyApiException(f"Error occurred while searching for tracks in genre: {genre_name}")

            for current_track_uri in results.keys():
                if current_track_uri not in random_tracks:
                    random_tracks.add(current_track_uri)

            anti_loop -= 1

        if len(random_tracks) > 0:
            if create_playlist:
                current_user_uri = key_from_dict(spotify.get_current_users_profile())
                current_user = User(uri_to_id(spotify_uri=current_user_uri, get_type=False))
                new_playlist = spotify.create_playlist(
                    user_id=current_user.user_id,
                    name=genre_name,
                    public=False,
                    collaborative=False,
                    description=f"{track_count} randomly selected tracks within the genre '{genre_name}'"
                )
                playlist_id = uri_to_id(key_from_dict(new_playlist))
                spotify.add_items_to_playlist(
                    playlist_id=playlist_id,
                    track_uris=list(random_tracks),
                )

                # Todo: add custom genre image

                return playlist_id, f"genre:{genre_name}"

            else:
                return random_tracks
        else:
            print("No tracks found")
            return None


def clear():
    """
    Clear the current terminal screen
    """
    os.system('cls' if sys.platform == "win32" else 'clear')
    print(BANNER)


def man(method: str = 'code_backend.main.man') -> None:
    """
    print Manpage for the entered method

    **Example:** `>>> man('code_backend.spotify_web_api.get_album')`

    :param method: wanted method, in the form of 'path.to.module.method_name'
    """
    # get docstring from method name inside class
    class_name = None
    if any(letter in method for letter in string.ascii_uppercase):
        mod_name, class_name, func_name = method.rsplit('.', 2)
        mod = importlib.import_module(mod_name)
        clas = getattr(mod, class_name)
        func = getattr(clas, func_name)
        docstring = func.__doc__

    # get docstring from method name
    else:
        mod_name, func_name = method.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        docstring = func.__doc__

    # parse docstring
    if ":param" in docstring:
        description, attributes = docstring.split(":param", 1)
        attributes = f":param {attributes}"
        attributes_exist = True

    elif ":return" in docstring:
        description, attributes = docstring.split(":return", 1)
        attributes = f":return {attributes}"
        attributes_exist = True

    elif ":raises" in docstring:
        description, attributes = docstring.split(":raises", 1)
        attributes = f":raises {attributes}"
        attributes_exist = True

    else:
        description = docstring
        attributes_exist = False

    parameters = {}
    returns = "None"
    errors = {}
    if attributes_exist:
        for line in attributes.splitlines():
            if line.startswith(":param"):
                param = line.replace(":param ", "").split(":",1)
                parameters[param[0].strip()] = param[1].strip()

            elif line.startswith(":return"):
                returns = line.replace(":return:", "").replace(":return :", "").strip()

            elif line.startswith(":raises"):
                error = line.replace(":raises ", "").split(":", 1)
                errors[error[0].strip()] = error[1].strip()

    # prepare docstring
    description = (
        description.lstrip("\n")
        .replace("\n**", f"\n{TBOLD}{CSPOGREEN}")
        .replace("**", f"{TEND}\n\t")
    )
    parameters = "\n\t".join(f"{TBOLD}{key}:{TEND} {value}" for key, value in parameters.items())
    errors = "\n\t".join(f"{TBOLD}{key}:{TEND} {value}" for key, value in errors.items())

    # format docstring
    met_name = f"\n{TBOLD}{CSPOGREEN}NAME:{TEND}\n\t{func_name}\n\n"
    met_module = f"{TBOLD}{CSPOGREEN}MODULE:{TEND}\n\t{mod_name}\n\n"
    met_class = f"{TBOLD}{CSPOGREEN}CLASS:{TEND}\n\t{func_name}\n\n" if class_name else ""
    met_description = f"{TBOLD}{CSPOGREEN}DESCRIPTION:\n\t{TEND}{description}"
    met_parameter = f"{TBOLD}{CSPOGREEN}PARAMETER:{TEND}\n\t{parameters}\n\n" if parameters != "" else ""
    met_return = f"{TBOLD}{CSPOGREEN}RETURN VALUE:{TEND}\n\t{returns}\n\n" if returns != "" else ""
    met_errors = f"{TBOLD}{CSPOGREEN}ERRORS:{TEND}\n\t{errors}\n\n" if errors != "" else ""

    print((
        met_name
        + met_module
        + met_class
        + met_description
        + met_parameter
        + met_return
        + met_errors
    ).replace('\t', ' '*4))


if __name__ == '__main__':
    # myApp = SpotifyApp()
    #
    # vars = globals()
    # vars.update(locals())
    #
    # readline.set_completer(rlcompleter.Completer(vars).complete)
    # readline.parse_and_bind("tab: complete")
    #
    # code.InteractiveConsole(locals=vars).interact(banner=BANNER)
    man()
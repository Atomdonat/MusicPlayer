from music_classes import *


class Device:
    def __init__(self, device_id: str) -> None:
        result = my_app_database.fetch_item('devices', device_id)

        # Create if not in the database
        if result is None:
            self.instance = sp.devices()
            if not self.get_specific_device(device_id):
                raise Exception("Invalid Device ID")

            self.device_id: str = self.instance['id']
            self.device_name: str = self.instance['name']
            self.device_type: str = self.instance['type']
            self.is_active: bool = bool(self.instance['is_active'])
            self.is_private_session: bool = bool(self.instance['is_private_session'])
            self.is_restricted: bool = bool(self.instance['is_restricted'])
            self.supports_volume: bool = bool(self.instance['supports_volume'])
            self.volume_percent: int = int(self.instance['volume_percent'])

        else:
            self.device_id, \
                self.device_name, \
                self.device_type, \
                self.is_active, \
                self.is_private_session, \
                self.is_restricted, \
                self.supports_volume, \
                self.volume_percent = result

    def get_specific_device(self, device_id: str) -> ValueError | Any:
        for current_device in self.instance['devices']:

            if current_device['id'] == device_id:
                return current_device

        valid_device_ids = []
        for current_device in self.instance['devices']:
            valid_device_ids.append(current_device['id'])

        return ValueError(f'The device named {device_id} was not found \n Valid Names are: {valid_device_ids}')


class Player:

    def __init__(self) -> None:
        self.instance = sp.current_playback(market=market)
        if self.instance:
            if self.instance['context']['type'] == 'album':
                self.current_collection = Album(uri_to_id(self.instance['context']['uri']))
            elif self.instance['context']['type'] == 'playlist':
                self.current_collection = Playlist(uri_to_id(self.instance['context']['uri']))

            self.current_album = Album(self.instance['item']['album']['id'])
            self.current_artist = Artist(self.instance['item']['artists'][0]['id'])
            self.current_track = Track(self.instance['item']['id'])

            self.device = Device(self.instance['device']['name'])
            self.is_playing = bool(self.instance['is_playing'])
            self.progress = int(self.instance['progress_ms'])
            self.repeat_state = self.instance['repeat_state']  # no = 'off', on = 'context', once = 'track',
            self.shuffle_state = bool(self.instance['shuffle_state'])

        else:
            self.current_collection = Playlist("0000000000000000000000")  # Dummy
            self.current_album = Album("0000000000000000000000")  # Dummy
            self.current_artist = Artist("0000000000000000000000")  # Dummy
            self.current_track = Track("0000000000000000000000")  # Dummy
            self.device = Device("0000000000000000000000")  # Dummy
            self.is_playing = False
            self.repeat_state = "Null"
            self.shuffle_state = "Null"

        self.dummy_player = (self.device.device_id == "0000000000000000000000")

    # JSON Files:
    def initialize_player(self):
        try:
            self.instance = sp.current_playback(market=market)
        except SpotifyException as e:
            print(f'\x1b[31mNo Spotify instance found:\n{e}\n\nPlease start Spotify and retry')
            sys.exit(1)

        if self.instance:
            if self.instance['context']['type'] == 'album':
                self.current_collection = Album(uri_to_id(self.instance['context']['uri']))
            elif self.instance['context']['type'] == 'playlist':
                self.current_collection = Playlist(uri_to_id(self.instance['context']['uri']))

            self.current_album = Album(self.instance['item']['album']['id'])
            self.current_artist = Artist(self.instance['item']['artists'][0]['id'])
            self.current_track = Track(self.instance['item']['id'])

            self.device = Device(self.instance['device']['name'])
            self.is_playing = bool(self.instance['is_playing'])
            self.repeat_state = self.instance['repeat_state']  # no = 'off', on = 'context', once = 'track',
            self.shuffle_state = bool(self.instance['shuffle_state'])

        self.dummy_player = (self.device.device_id == "0000000000000000000000")
        self.skip_blacklisted_items()

    def change_playing_state(self):
        if not self.dummy_player:
            # HACK: abusing error to know if Spotify is playing
            try:
                sp.pause_playback(self.device.device_id)
            except:
                # if it is not supposed to work, why does it? xD
                sp.start_playback(self.device.device_id)

    @property
    def progress(self) -> int:
        if not self.dummy_player:
            playback_data = sp.current_user_playing_track()
            if playback_data:
                return playback_data["progress_ms"]
        else:
            return -1

    @progress.setter
    def progress(self, time_in_ms: int):
        if not self.dummy_player:
            sp.seek_track(time_in_ms, self.device.device_id)
            self.progress = time_in_ms
        else:
            self.progress = -1

    def change_repeat_state(self, new_state: Literal['context', 'track', 'off']):
        if not self.dummy_player:
            if new_state == "context":
                sp.repeat('context', self.device.device_id)
            elif new_state == "track":
                sp.repeat('track', self.device.device_id)
            elif new_state == "off":
                sp.repeat('off', self.device.device_id)

    def next_track(self):
        if not self.dummy_player:
            sp.next_track(self.device.device_id)

    def prev_track(self):
        if not self.dummy_player:
            sp.previous_track(self.device.device_id)

    def change_shuffle_state(self):
        if not self.dummy_player:
            self.shuffle_state = not self.shuffle_state
            sp.shuffle(self.shuffle_state, self.device.device_id)

    def set_volume(self, new_volume: int):
        if not (0 <= new_volume <= 100):
            raise ValueError("Volume must be in the range from 0 to 100.")
        if not self.dummy_player:
            sp.volume(new_volume, self.device.device_id)

    def skip_blacklisted_items(self):
        if self.dummy_player:
            return

        album_is_blacklisted = my_app_database.fetch_item('albums', self.current_album.album_id)
        if isinstance(self.current_collection, Album):
            collection_is_blacklisted = my_app_database.fetch_item('albums', self.current_collection.album_id)
        elif isinstance(self.current_collection, Playlist):
            collection_is_blacklisted = my_app_database.fetch_item('playlists', self.current_collection.playlist_id)
        else:
            print("How did we get here")
            return

        artist_is_blacklisted = my_app_database.fetch_item('artists', self.current_artist.artist_id)
        track_is_blacklisted = my_app_database.fetch_item('tracks', self.current_track.track_id)

        if any([album_is_blacklisted, collection_is_blacklisted, artist_is_blacklisted, track_is_blacklisted]):
            self.next_track()


class SpotifyApp:
    def __init__(self) -> None:
        available_markets = sp.available_markets()
        if market not in available_markets["markets"]:
            raise Exception(f"Market not available\nAvailable markets: {available_markets["markets"]}")

        self.market = market
        self.client = spotify_client()
        self.user = self.client.current_user()

    @property
    def current_queue(self):
        return self.client.queue()

    def add_to_queue(self, track: Track):
        return self.client.add_to_queue(track.track_id)

    def find_object(self,
                    object_name: str,
                    object_type: Literal['album', 'artist', 'playlist', 'track', 'user'] | None
                    ) -> Album | Artist | Playlist | Track:

        # relevant for GUI
        if object_type is None:
            if re.search('album', object_name, re.IGNORECASE) is not None:
                search_type = 'album'
            elif re.search('artist', object_name, re.IGNORECASE) is not None:
                search_type = 'artist'
            elif re.search('playlist', object_name, re.IGNORECASE) is not None:
                search_type = 'playlist'
            elif re.search('track', object_name, re.IGNORECASE) is not None:
                search_type = 'track'
            elif re.search('user', object_name, re.IGNORECASE) is not None:
                search_type = 'user'
            else:
                search_type = ''

            object_name = re.sub(search_type, '', object_name)

            results = self.client.search(q=object_name, type=search_type, market=self.market, limit=50)

        else:
            results = self.client.search(q=object_name, type=object_type, market=self.market, limit=50)

        # Choose right one
        print(f"\n These {next(iter(results.keys()))} are found by {object_name}:\n")
        for current_object in results[next(iter(results.keys()))]['items']:
            by_artist = ''
            if re.search("artist", next(iter(results.keys())), re.IGNORECASE) is None:
                if re.search("playlist", next(iter(results.keys())), re.IGNORECASE) is not None:
                    by_artist = f'by \'{current_object['owner']['display_name']}\''
                else:
                    by_artist = f'by \'{current_object['artists'][0]['name']}\''

            current_input = input(f"\n Do you mean \'{current_object['name']}\' {by_artist} (Y/n): ")
            if current_input != 'n':
                if re.search("album", next(iter(results.keys())), re.IGNORECASE) is not None:
                    return Album(current_object['id'])

                elif re.search("artist", next(iter(results.keys())), re.IGNORECASE) is not None:
                    return Artist(current_object['id'])

                elif re.search("playlist", next(iter(results.keys())), re.IGNORECASE) is not None:
                    return Playlist(current_object['id'])

                elif re.search("track", next(iter(results.keys())), re.IGNORECASE) is not None:
                    return Track(current_object['id'])

                # elif re.search("genre", next(iter(results.keys())), re.IGNORECASE) is not None:
                #     return Genre(current_object['id'])

        raise ValueError(f"\n Cannot find {next(iter(results.keys()))}: \'{object_name}\'.\n")

    def random_tracks_by_genre(self, genre_name: str, track_count: int = 10) -> dict | None:
        random_tracks = {}

        def get_random_tracks(number_of_tracks: int):
            random_offset = random.randint(0, 990)
            results = self.client.search(q=f'genre:{genre_name}', type='track', limit=number_of_tracks, market=self.market,
                                         offset=random_offset)

            for current_track in results['tracks']['items']:
                if current_track['id'] not in random_tracks:
                    random_tracks[current_track['id']] = current_track['name']
            print(f'{round(len(random_tracks)/track_count*100, 2)}%')

        anti_loop = track_count
        while anti_loop > 0 and len(random_tracks) < track_count:
            get_random_tracks(10)
            anti_loop -= 1

        if len(random_tracks) > 0:
            return random_tracks
        else:
            print("No tracks found")
            return None

    def random_playlist_shuffle(self, playlist: Playlist, shuffle_mode: Literal['random', 'all']):
        """
        :param: playlist: Playlist object
        :param: shuffle_mode: shuffle all tracks (random: duplicates possible; all: no duplicates)
        """

        iteration = True

        def random_shuffle():
            while iteration:
                if input("\nContinue (Y/n):") != 'n':
                    random_position = random.randint(0, playlist.track_count-1)
                    current_track_id = playlist.track_ids[random_position]
                    self.client.add_to_queue(current_track_id)
                else:
                    break

        def all_shuffle() -> None:
            shuffle_track_ids = playlist.track_ids
            while iteration and len(shuffle_track_ids) > 0:
                if input("\nContinue (Y/n):") != 'n':
                    random_position = random.randint(0, len(shuffle_track_ids) - 1)
                    current_track_id = shuffle_track_ids[random_position]
                    self.client.add_to_queue(current_track_id)
                    shuffle_track_ids.pop(random_position)
                else:
                    break

        match shuffle_mode:
            case 'random':
                random_shuffle()
            case 'all':
                all_shuffle()

    def add_to_playlist(self, playlist: Playlist, track: Track):
        try:
            id_playlist = playlist.playlist_id
            uri_track = id_to_uri('track', track.track_id)
            self.client.playlist_add_items(id_playlist, [uri_track])

        except Exception as e:
            print(e)

        finally:
            return self.client.playlist_items(playlist_id=playlist.playlist_id, limit=100, market=self.market)

    def create_playlist(self, name: str, public: bool = False, collaborative: bool = False, description: str = '') -> Playlist:
        new_playlist_json = self.client.user_playlist_create(user=self.user['id'], name=name, public=public, collaborative=collaborative, description=description)
        new_playlist = Playlist(new_playlist_json['id'])

        b64_image = image_to_b64(new_playlist.playlist_image, 'PNG')
        self.client.playlist_upload_cover_image(playlist_id=new_playlist.playlist_id, image_b64=b64_image)

        return new_playlist

    def new_playlist_by_random_genre(self, genre: str, length_min: int) -> Playlist:
        track_count = int(length_min/3)

        tracks = self.random_tracks_by_genre(genre_name=genre, track_count=track_count)
        playlist = self.create_playlist(name=genre, public=False, collaborative=False, description=f'{track_count} randomly selected tracks within the genre \'{genre}\'')

        track_ids = keys_from_dict(tracks)
        for track in track_ids:
            self.add_to_playlist(playlist=playlist, track=Track(track))

        return playlist

    @property
    def player(self) -> Player:
        return Player()


if __name__ == '__main__':
    app = SpotifyApp()
    sp.mar

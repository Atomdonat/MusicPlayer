from music_classes import *


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

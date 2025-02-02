import json
import time
from datetime import timedelta
import sqlite3
from typing import Union, Literal
from PIL import Image, ImageTk
from redis.commands.json import JSON
from spotipy import SpotifyException

import os
import re
from typing import *
import requests
import numpy
import spotipy
from spotipy import SpotifyException

import base64
from PIL import Image, ImageTk
import io
from io import BytesIO
import requests
from tkinter import PhotoImage
import sys

import random
import sqlite3

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import urllib3
from dotenv import load_dotenv


# load Spotipy credentials
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Define the required scopes / currently needed scopes
# https://developer.spotify.com/documentation/web-api/concepts/scopes
SCOPES = [
    'user-read-playback-state',
    'user-read-currently-playing',
    'user-modify-playback-state',
    'user-library-read',
    'ugc-image-upload',
    'playlist-modify-public',
    'playlist-modify-private'
]

no_image_file_path = '../Icons/Spotipy_if_no_image.jpeg'
json_path = '../Databases/JSON_Files/spotify_devices.json'
frontend_window_size = [800,400]

# Create Spotify authentication token
def spotify_client() -> spotipy.Spotify:
    max_retries = 10
    retry_count = 0

    while retry_count < max_retries:
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope=' '.join(SCOPES),
                cache_path="../.spotify_cache",
                show_dialog=True  # Set to True to force the user to approve the app every time
            ))

        except ConnectionError as e:
            print(f"Error encountered: {e}")
            print(f"Retrying... (Attempt {retry_count + 1} of {max_retries})")
            retry_count += 1
            time.sleep(5)

        finally:
            return sp


sp = spotify_client()
market = 'DE'


def millis_to_minutes(millis: int, to_hours: bool = False) -> str:
    if to_hours:
        return str(timedelta(seconds=millis // 1000))
    else:
        return str(timedelta(seconds=millis // 1000)) + "." + str(millis % 1000)  # .strip(":")[2:]


def url_to_uri(spotify_url: str, to_id: bool = False) -> str:
    class_type = spotify_url.split("/")[-2]

    if class_type[-1] == "s":
        class_type = class_type[:-1]

    id_ = (spotify_url.split("/")[-1]).split("?")[0]
    if to_id:
        return id_
    else:
        return "spotify:" + class_type + ":" + id_


def id_to_uri(class_type: str, spotify_id: str) -> str:
    return "spotify:" + class_type + ":" + spotify_id


def uri_to_id(spotify_uri: str) -> str:
    return spotify_uri.split(":")[-1]


def json_to_file(json_filepath, json_data, overwrite: bool = False):
    if not overwrite:
        if not os.path.exists(json_filepath):
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
    else:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)


def average_file_size(directory_path: str) -> float:
    current_size = 0
    counted_files = 0

    for filename in os.listdir(directory_path):
        # if re.search('track',filename) != None:
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            current_size += os.path.getsize(file_path)
            counted_files += 1

    return current_size / counted_files

def values_from_dict(dictionary: dict) -> list:
    value_list = []
    for current_value in dictionary.values():
        value_list.append(current_value)
    return value_list

def keys_from_dict(dictionary: dict) -> list:
    keys_list = []
    for current_key in dictionary.keys():
        keys_list.append(current_key)
    return keys_list

def list_from_dict(dictionary: dict) -> list:
    dict_list = []
    for key, value in dictionary.items():
        dict_list.append([key, value])

    return dict_list

def format_bytes(input_bytes: int):
    factor = 1
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for unit in units:
        new_factor = factor * 1024
        if input_bytes <= new_factor:
            return f'{input_bytes/factor:.2f} {unit}'
        factor = new_factor

def value_from_dict(dictio: dict) -> str:
    return next(iter(dictio.values()))

def try_spotify_connection():
    try:
        sp = spotify_client()
        return sp
    except:
        print('Spotify went mimimi...\n will retry again')
        return try_spotify_connection()

def check_spotify_id(
        spotify_id: str,
        id_type: Literal['album', 'artist', 'playlist', 'track', 'user'],
        retries: int = 0) \
        -> bool | SpotifyException:
    return True

    # max_retries = 5
    # # noinspection PyBroadException
    # try:
    #     match id_type:
    #         case 'album':
    #             sp.album(artist_id=spotify_id, market=market)
    #         case 'artist':
    #             sp.artist(artist_id=spotify_id)
    #         case 'playlist':
    #             sp.playlist(playlist_id=spotify_id, market=market)
    #         case 'track':
    #             sp.track(track_id=spotify_id, market=market)
    #         case 'user':
    #             sp.user(user=spotify_id)
    #     return True
    #
    # except:
    #     if retries < max_retries:
    #         return check_spotify_id(spotify_id, id_type, retries + 1)
    #     if retries >= max_retries:
    #         raise ValueError(f'\n {spotify_id} is an invalid {id_type} id')


class JsonDatabase:
    def __init__(self, database_file: str) -> None:
        self.database = sqlite3.connect(database_file)
        self.cursor = self.database.cursor()
        self.initialize_tables()

    def initialize_tables(self) -> None:
        tmp = ['album', 'artist', 'playlist', 'track', 'user']
        for table_name in tmp:
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS '{table_name}' (
                    'ID' TEXT PRIMARY KEY,
                    'Name' TEXT,
                    'JSON' TEXT,
                    'Blacklisted' INTEGER
                )
            """
            self.cursor.execute(create_table_query)
            self.database.commit()

    def add_json_to_table(self, json_file_path: str | None = None, json_data: dict | None = None) -> None:
        if json_file_path is not None:
            with open(json_file_path, 'r') as file:
                json_data = json.load(file)

        sql_command = f"""
            INSERT INTO '{json_data['type']}'(
                'ID',
                'Name',
                'JSON',
                'Blacklisted'
            )
            VALUES(?,?,?,?) 
        """
        if json_data['type'] != 'user':
            sql_values = (
                json_data['id'],
                json_data['name'],
                json.dumps(json_data),
                False
            )
        else:
            sql_values = (
                json_data['id'],
                json_data['display_name'],
                json.dumps(json_data),
                False
            )

        with self.database:
            # only new instances will be added, due to the uniqueness of the IDs.
            # Otherwise, the error will be caught
            try:
                self.cursor.execute(sql_command, sql_values)
                # print(f"\n Committed \'{json_data['name']}\' to Table {json_data['type']}. \n")

            except Exception as e:
                if e is not None:
                    print(e)
                # else:
                # print(f"\n \'{json_data['name']}\' is already known. \n")

            finally:
                # noinspection PyStatementEffect
                self.cursor.lastrowid
                self.database.commit()

    def get_json_from_table(self, table_name: str, item_id: str) -> dict:
        cursor = self.database.execute(f'SELECT * from {table_name} WHERE ID = ?', (item_id,))
        json_data = cursor.fetchone()[2]
        json_data = json.loads(json_data)
        return json_data

    def set_blacklist_value(self, table_name: str, item_id: str, new_value=0 | 1) -> None:
        self.database.execute(
            f"""UPDATE '{table_name}' SET Blacklisted = {new_value} WHERE ID = '{item_id}'"""
        )
        self.database.commit()

    def is_item_blacklisted(self, table_name: str, item_id: str) -> bool:
        item = self.database.execute(
            f"""SELECT * from '{table_name}' WHERE ID = '{item_id}'"""
        )
        result = item.fetchone()
        if result:
            return result[3] == 1
        else:
            return False


class SpotifyObject:
    def __init__(self, spotify_id: str,
                 spotify_object_type: Literal['album', 'artist', 'playlist', 'track', 'user']) -> None:
        self.object_type = spotify_object_type

        check_spotify_id(spotify_id=spotify_id, id_type=spotify_object_type)

        self.json_database = JsonDatabase('../Databases/TrackTank.db')

        cursor = self.json_database.database.execute(f"""SELECT * from '{spotify_object_type}' WHERE ID = ?""",
                                                     (spotify_id,))
        if not bool(cursor.fetchone()):
            match spotify_object_type:
                case 'album':
                    self.instance = sp.album(album_id=spotify_id, market=market)
                case 'artist':
                    self.instance = sp.artist(artist_id=spotify_id)
                case 'playlist':
                    self.instance = sp.playlist(playlist_id=spotify_id, market=market)
                case 'track':
                    self.instance = sp.track(track_id=spotify_id, market=market)
                case 'user':
                    self.instance = sp.user(user=spotify_id)
            self.json_database.add_json_to_table(json_data=self.instance)
        else:
            self.instance = self.json_database.get_json_from_table(table_name=spotify_object_type, item_id=spotify_id)

        if 'name' in self.instance:
            self.name = self.instance['name']
        elif 'display_name' in self.instance:
            self.display_name = self.instance['display_name']

        self.id = self.instance['id']
        self.uri = self.instance['uri']
        self.url = self.instance['external_urls']['spotify']

        if 'images' in self.instance and self.instance['images']:
            self.image = image_from_url(self.instance['images'][0]['url'])

        elif self.object_type == 'track' and 'images' in self.instance['album'] and self.instance['album']['images']:
            self.image = image_from_url(self.instance['album']['images'][0]['url'])
        else:
            self.image = image_from_file(no_image_file_path)

    @property
    def is_blacklisted(self) -> bool:
        return self.json_database.is_item_blacklisted(table_name=self.object_type, item_id=self.id) == 1

    @is_blacklisted.setter
    def is_blacklisted(self, new_value=0 | 1) -> None:
        self.json_database.set_blacklist_value(table_name=self.object_type, item_id=self.id, new_value=new_value)


class Album(SpotifyObject):
    def __init__(self, spotify_album_id: str):
        super().__init__(spotify_id=spotify_album_id, spotify_object_type='album')

        self.genres = self.instance['genres']
        self.track_count = self.instance['total_tracks']

    @property
    def artists(self) -> dict:
        artists = {}
        for artist in self.instance['artists']:
            artists[artist['id']] = artist['name']
        return artists

    @property
    def tracks(self) -> (dict, int):
        tracks = {}
        for current_track in self.instance['tracks']['items']:
            tracks[current_track['id']] = current_track['name']
        return tracks

    @property
    def duration(self) -> int:
        duration = 0
        for current_track in self.instance['tracks']['items']:
            duration += int(current_track['duration_ms'])
        return duration

    def print_album_profile(self) -> None:
        if self.duration >= int(36e5):
            duration = millis_to_minutes(self.duration, True)
        else:
            duration = millis_to_minutes(self.duration)

        print(
            f"""
            Name:     {self.name} \n
            ID:       {self.id} \n
            URL:      {self.url} \n
            Artist:   {self.artists} \n
            Tracks:"""
        )
        for current_track in self.tracks.values():
            print(
                f"""                      {current_track}"""
            )
        print("""
            Genres:"""
              )
        if len(self.genres) == 0:
            print("""                      ¯\\(o_o)/¯""")
        else:
            for current_genre in self.genres:
                print(
                    f"""                      {current_genre}"""
                )
        print(
            f"""
            Duration: {duration}\n
            Image:    {self.image} \n
            """
        )


class Artist(SpotifyObject):
    def __init__(self, artist_spotify_id: str) -> None:
        super().__init__(spotify_id=artist_spotify_id, spotify_object_type='artist')

        self.follower = self.instance['followers']['total']
        self.genres = self.instance['genres']

    @property
    def top_tracks(self) -> dict:
        top_tracks = sp.artist_top_tracks(self.id, country="DE")
        top_track_list = {}
        for top_track in top_tracks['tracks']:
            top_track_list[top_track['id']] = top_track['name']

        return top_track_list

    def print_artist_profile(self) -> None:
        print(
            f"""
            Name:       {self.name} \n
            ID:         {self.id} \n
            URL:        {self.url} \n
            Follower:   {self.follower} \n
            Top Tracks:""")
        for current_track in self.top_tracks.values():
            print(
                f"""                        {current_track}"""
            )

        print(f"""
            Genres:     {self.genres} \n
            Image:      {self.image} \n
            """)


class Playlist(SpotifyObject):
    def __init__(self, spotify_playlist_id: str) -> None:
        super().__init__(spotify_id=spotify_playlist_id, spotify_object_type='playlist')

        self.owner = User(self.instance['owner']['id'])
        self.track_count = int(self.instance['tracks']['total'])

    @property
    def tracks(self) -> (list, int):
        tracks = {}
        for current_track in self.instance['tracks']['items']:
            tracks[current_track['track']['id']] = current_track['track']['name']
        return tracks

    @property
    def duration(self) -> (list, int):
        duration = 0
        for current_track in self.instance['tracks']['items']:
            duration += int(current_track['track']['duration_ms'])
        return duration

    def print_playlist_profile(self):
        if self.duration >= int(36e5):
            duration = millis_to_minutes(self.duration, True)
        else:
            duration = millis_to_minutes(self.duration)

        print(
            f"""
            Name:     {self.name} \n
            ID:       {self.id} \n
            URL:      {self.url} \n
            Owner:    {self.owner.name} \n
            Tracks:"""
        )
        for current_track in self.tracks.values():
            print(
                f"""                      {current_track}"""
            )
        print(
            f"""
            Duration: {duration}\n
            Image:    {self.image} \n
            """
        )


class Track(SpotifyObject):
    def __init__(self, spotify_track_id: str) -> None:
        super().__init__(spotify_id=spotify_track_id, spotify_object_type='track')

        self.duration = self.instance['duration_ms']

    @property
    def artist(self) -> dict:
        artists = {}
        for artist in self.instance['artists']:
            artists[artist['id']] = artist['name']
        return artists

    @property
    def album(self) -> dict:
        return {self.instance['album']['id']: self.instance['album']['name']}

    def print_track_profile(self) -> None:
        print(
            f"""
            Name:     {self.name} \n
            ID:       {self.id} \n
            URL:      {self.url} \n
            Artist:   {self.artist} \n
            Album:    {self.album} \n
            Duration: {millis_to_minutes(self.duration)}\n
            Image:    {self.image} \n
            """)


class User(SpotifyObject):
    def __init__(self, spotify_user_id: str) -> None:
        super().__init__(spotify_id=spotify_user_id, spotify_object_type='user')

        self.name = self.instance['display_name']
        self.follower = self.instance['followers']
        self.playlists = sp.user_playlists(self.id)

    @property
    def top_tracks(self) -> dict:
        return sp.current_user_top_tracks(limit=10)

    @top_tracks.setter
    def top_tracks(self, limit: int):
        self.top_tracks = sp.current_user_top_tracks(limit=limit)

    @property
    def saved_tracks(self):
        return sp.current_user_saved_tracks(limit=10, market=market)

    @saved_tracks.setter
    def saved_tracks(self, limit: int | None = None, track: Track | None = None):
        if limit is not None:
            self.saved_tracks = sp.current_user_saved_tracks(limit=limit, market=market)
        if track is not None:
            sp.current_user_saved_tracks_add(tracks=[track.id])

    def get_user_profile(self):
        print(
            f"""
            Name:      {self.name}
            ID:        {self.id}
            URL:       {self.url}
            Image:     {self.image}
            Follower:  {self.follower}
            Playlists: """
        )
        for current_playlist in self.playlists['items']:
            print(f'                       {current_playlist['name']}')


class MyAppDatabase:
    def __init__(self, database_file: str) -> None:
        self.database = sqlite3.connect(database_file)
        self.cursor = self.database.cursor()

    def create_table(self, table_name: str) -> None:
        if re.search('album', table_name, re.IGNORECASE) is not None:
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS '{table_name}' (
                    'ID' TEXT PRIMARY KEY,
                    'Name' TEXT,
                    'URL' TEXT,
                    'Artist ID' TEXT,
                    'Artist Name' TEXT,
                    'Track Count' INTEGER,
                    'Track ID' TEXT,
                    'Track Name' TEXT,
                    'Genres' TEXT,
                    'Total Duration' INTEGER,
                    'Image' TEXT,
                    FOREIGN KEY ('Artist ID') REFERENCES 'Spotify Artists'('ID'),
                    FOREIGN KEY ('Track ID') REFERENCES 'Spotify Tracks'('ID')
                )
            """

        elif re.search("artist", table_name, re.IGNORECASE) is not None:
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS '{table_name}' (
                    'ID' TEXT PRIMARY KEY,
                    'Name' TEXT,
                    'URL' TEXT,
                    'Follower' INTEGER,
                    'Top Tracks ID' TEXT,
                    'Top Tracks Name' TEXT,
                    'Genres' TEXT,
                    'Image' TEXT
                )
            """

        elif re.search("playlist", table_name, re.IGNORECASE) is not None:
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS '{table_name}' (
                    'ID' TEXT PRIMARY KEY,
                    'Name' TEXT,
                    'URL' TEXT,
                    'Owner ID' TEXT,
                    'Owner Name' TEXT, 
                    'Track Count' INTEGER,
                    'Track ID' TEXT,
                    'Track Name' TEXT,
                    'Total Duration' INTEGER,
                    'Image' TEXT,
                    FOREIGN KEY ('Track ID') REFERENCES 'Spotify Tracks'('ID')
                )
            """

        elif re.search("track", table_name, re.IGNORECASE) is not None:
            create_table_query = f"""
                CREATE TABLE IF NOT EXISTS '{table_name}' (
                    'ID' TEXT PRIMARY KEY,
                    'Name' TEXT,
                    'URL' TEXT,
                    'Artist ID' TEXT, 
                    'Artist Name' TEXT,
                    'Album ID' TEXT,
                    'Album Name' TEXT,
                    'Duration' INTEGER,
                    'Image' TEXT,
                    FOREIGN KEY ('Artist ID') REFERENCES 'Spotify Artists'('ID'),
                    FOREIGN KEY ('Album ID') REFERENCES 'Spotify Albums'('ID')
                )
            """

        elif re.search("user", table_name, re.IGNORECASE) is not None:
            raise NotImplementedError

        else:
            # print(
            #     """\n
            #     Unsupported Table Name Entered \n
            #     Names should include: 'album', 'artist', 'playlist' or 'track'
            #     \n
            #     """
            # )
            raise TypeError

        self.cursor.execute(create_table_query)
        self.database.commit()
        # print(f"\n Table \'{table_name}\' got created \n")

    def add_to_table(self, instance: Union[Album, Artist, Playlist, Track]):
        match instance.object_type:
            case 'album':
                table_name = 'Spotify Albums'
                sql_command = f"""INSERT INTO '{table_name}'(
                            'ID',
                            'Name',
                            'URL',
                            'Artist ID',
                            'Artist Name',
                            'Track Count',
                            'Track ID',
                            'Track Name',
                            'Genres',
                            'Total Duration',
                            'Image'
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?) """

                sql_values = (
                    instance.id,
                    instance.name,
                    instance.url,
                    json.dumps(list(instance.artists.keys())),  # Artist ID
                    json.dumps(list(instance.artists.values())),  # Artist Name
                    instance.track_count,
                    json.dumps(list(instance.tracks.keys())),
                    json.dumps(list(instance.tracks.values())),
                    json.dumps(instance.genres),
                    instance.duration,
                    str(instance.image)
                )

            case 'artist':
                table_name = 'Spotify Artists'
                sql_command = f"""
                    INSERT INTO '{table_name}'(
                        'ID',
                        'Name',
                        'URL',
                        'Follower',
                        'Top Tracks ID',
                        'Top Tracks Name',
                        'Genres',
                        'Image'
                    )
                    VALUES(?,?,?,?,?,?,?,?)
                """
                sql_values = (
                    instance.id,
                    instance.name,
                    instance.url,
                    instance.follower,
                    json.dumps(list(instance.top_tracks.keys())),
                    json.dumps(list(instance.top_tracks.values())),
                    json.dumps(instance.genres),
                    str(instance.image)
                )

            case 'playlist':
                table_name = 'Spotify Playlists'
                sql_command = f"""
                    INSERT INTO '{table_name}'(
                        'ID',
                        'Name',
                        'URL',
                        'Owner ID',
                        'Owner Name',
                        'Track Count',
                        'Track ID',
                        'Track Name',
                        'Total Duration',
                        'Image'
                    )
                    VALUES(?,?,?,?,?,?,?,?,?,?) 
                """

                sql_values = (
                    instance.id,
                    instance.name,
                    instance.url,
                    instance.owner.id,
                    instance.owner.name,
                    instance.track_count,
                    json.dumps(list(instance.tracks.keys())),
                    json.dumps(list(instance.tracks.values())),
                    instance.duration,
                    str(instance.image)
                )

            case 'track':
                table_name = 'Spotify Tracks'
                sql_command = f"""
                    INSERT INTO '{table_name}'(
                        'ID',
                        'Name',
                        'URL',
                        'Artist ID', 
                        'Artist Name',
                        'Album ID',
                        'Album Name',
                        'Duration',
                        'Image'
                    )
                    VALUES(?,?,?,?,?,?,?,?,?) 
                """

                current_artists = {}
                current_album = {}
                current_artists.update(instance.artist)
                current_album.update(instance.album)

                sql_values = (
                    instance.id,
                    instance.name,
                    instance.url,
                    json.dumps(list(current_artists.keys())),  # Artist ID
                    json.dumps(list(current_artists.values())),  # Artist Name
                    json.dumps(list(current_album.keys())),  # Album  ID
                    json.dumps(list(current_album.values())),  # Album  Name
                    instance.duration,
                    str(instance.image)
                )

            case 'user':
                raise NotImplementedError

            case _:
                # print(
                #     """\n
                #     Unsupported Instance Type Entered
                #     Valid Types are: Album, Artist, Playlist or Track
                #     \n
                #     """
                # )
                raise TypeError

        with self.database:
            cur = self.database.cursor()

            # only new instances will be added, due to the uniqueness of the IDs.
            # Otherwise, the error will be caught
            try:
                cur.execute(sql_command, sql_values)
                # print(f"\n Committed \'{instance.name}\' to Table {table_name}. \n")

            except Exception as e:
                if e is not None:
                    print(e)

                # print(f"\n \'{instance.name}\' is already known. \n")

            finally:
                # noinspection PyStatementEffect
                cur.lastrowid
                self.database.commit()

    def delete_table(self, table_name: str):
        # if input('Confirm Reset (y/N):') == 'y':
        drop_table_query = f"""
            DROP TABLE IF EXISTS '{table_name}';
        """
        self.cursor.execute(drop_table_query)
        # print(f"\n The Table \'{table_name}\' got deleted! \n")

        self.database.commit()

    def reset_table(self, table_name: str):
        self.delete_table(table_name)
        self.create_table(table_name)
        return None


class Devices:
    def __init__(self) -> None:
        self.instance = sp.devices()

        json_to_file(json_path, self.instance, True)

    def get_specific_device(self, device_name: str) -> ValueError | Any:
        for current_device in self.instance['devices']:

            # if re.search(current_device['name'],device_name, re.IGNORECASE) is not None:
            if current_device['name'] == device_name:
                return current_device

        valid_device_names = []
        for current_device in self.instance['devices']:
            valid_device_names.append(current_device['name'])

        return ValueError(f'The device named {device_name} was not found \n Valid Names are: {valid_device_names}')


class Device:
    def __init__(self, device_name: str, devices: Devices) -> None:
        self.instance = devices.get_specific_device(device_name)

        self.id = self.instance['id']
        self.is_active = bool(self.instance['is_active'])
        self.is_private_session = bool(self.instance['is_private_session'])
        self.is_restricted = bool(self.instance['is_restricted'])
        self.name = self.instance['name']
        self.supports_volume = bool(self.instance['supports_volume'])
        self.type = self.instance['type']
        self.volume_percent = int(self.instance['volume_percent'])

    def print_device_profile(self):
        print(f"""
              Name:            {self.name} \n
              ID:              {self.id} \n
              Type:            {self.type} \n
              is Active:       {self.is_active} \n
              is Private:      {self.is_private_session} \n
              supports Volume: {self.supports_volume} \n
              Volume:          {self.volume_percent}% \n

        """)


class Player:

    def __init__(self) -> None:
        # self.instance: dict = None
        # self.current_collection: Playlist | Album = None
        # self.current_album: Album = None
        # self.current_artist: Artist = None
        # self.current_track: Track = None
        # self.device: Device = None
        # self.is_playing: bool = None
        # self.progress: int = None
        # self.repeat_state: str = None
        # self.shuffle_state: bool = None

        self.initialize_player()

    def get_instance(self):
        try:
            self.instance = sp.current_playback(market=market)
            return self.instance

        except:
            print("Spotify is currently not running")
            return None

    # JSON Files:
    def initialize_player(self):
        self.instance = self.get_instance()
        if self.instance is None:
            self.instance: dict = None
            self.current_collection: Playlist | Album = None
            self.current_album: Album = None
            self.current_artist: Artist = None
            self.current_track: Track = None
            self.device: Device = None
            self.is_playing: bool = None
            self.progress: int = None
            self.repeat_state: str = None
            self.shuffle_state: bool = None

        else:
            if self.instance['context']['type'] == 'album':
                self.current_collection = Album(uri_to_id(self.instance['context']['uri']))
            elif self.instance['context']['type'] == 'playlist':
                self.current_collection = Playlist(uri_to_id(self.instance['context']['uri']))

            self.current_album = Album(self.instance['item']['album']['id'])
            self.current_artist = Artist(self.instance['item']['artists'][0]['id'])
            self.current_track = Track(self.instance['item']['id'])

            self.device = Device(self.instance['device']['name'], Devices())
            self.is_playing = bool(self.instance['is_playing'])
            self.progress = int(self.instance['progress_ms'])
            self.repeat_state = self.instance['repeat_state']  # no = 'off', on = 'context', once = 'track',
            self.shuffle_state = bool(self.instance['shuffle_state'])

        self.skip_blacklisted_items()

    def change_playing_state(self):
        # noinspection PyBroadException
        try:
            sp.pause_playback(self.device.id)
        except:
            # if it is not supposed to work, prohibit it xD
            sp.start_playback(self.device.id)

    def set_progress(self, time_in_s: int):
        sp.seek_track(time_in_s*1000, self.device.id)

    def change_repeat_state(self, new_state: Literal['context', 'track', 'off']):
        if new_state == "context":
            sp.repeat('context', self.device.id)
        elif new_state == "track":
            sp.repeat('track', self.device.id)
        elif new_state == "off":
            sp.repeat('off', self.device.id)

    def next_track(self):
        sp.next_track(self.device.id)

    def prev_track(self):
        sp.previous_track(self.device.id)

    def change_shuffle_state(self):
        self.shuffle_state = not self.shuffle_state
        sp.shuffle(self.shuffle_state, self.device.id)

    def set_volume(self, new_volume: int):
        if not (0 <= new_volume <= 100):
            raise ValueError("Volume must be in the range from 0 to 100.")

        sp.volume(new_volume, self.device.id)

    def skip_blacklisted_items(self):
        if self.current_track.is_blacklisted or self.current_track.is_blacklisted or self.current_artist.is_blacklisted:
            self.next_track()


class SpotifyApp:
    def __init__(self) -> None:
        # check if market exists
        self.market = market
        self.client = spotify_client()
        self.user = self.client.current_user()

    @property
    def current_queue(self):
        return self.client.queue()

    def add_to_queue(self, track: Track):
        return self.client.add_to_queue(track.id)

    def find_object(self,
                    object_name: str,
                    object_type: Literal['album', 'artist', 'playlist', 'track', 'user'] | None
                    ) -> Album | Artist | Playlist | Track:

        if object_type is None:
            search_type = ''
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
            results = self.client.search(q=f'genre:{genre_name}', type='track', limit=number_of_tracks,
                                         market=self.market,
                                         offset=random_offset)

            for current_track in results['tracks']['items']:
                if current_track['id'] not in random_tracks:
                    random_tracks[current_track['id']] = current_track['name']
            print(f'{round(len(random_tracks) / track_count * 100, 2)}%')

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
        iteration = True
        playlist_track_id_list = keys_from_dict(playlist.tracks)

        def random_shuffle():
            while iteration:
                tmp_input = input("\nContinue (Y/n):")
                if tmp_input != 'n':
                    random_position = random.randint(0, playlist.track_count - 1)
                    current_track_id = playlist_track_id_list[random_position]
                    self.client.add_to_queue(current_track_id)
                else:
                    break

        def all_shuffle():
            while iteration and len(playlist_track_id_list) > 0:
                tmp_input = input("\nContinue (Y/n):")
                if tmp_input != 'n':
                    random_position = random.randint(0, playlist.track_count - 1)
                    current_track_id = playlist_track_id_list[random_position]
                    self.client.add_to_queue(current_track_id)
                    playlist_track_id_list.pop(random_position)
                else:
                    break

        match shuffle_mode:
            case 'random':
                random_shuffle()
            case 'all':
                all_shuffle()

    def add_to_playlist(self, playlist: Playlist, track: Track):
        try:
            id_playlist = playlist.id
            uri_track = id_to_uri('track', track.id)
            self.client.playlist_add_items(id_playlist, [uri_track])

        except Exception as e:
            print(e)

        finally:
            return self.client.playlist_items(playlist_id=playlist.id, limit=100, market=self.market)

    def create_playlist(self, name: str, public: bool = False, collaborative: bool = False,
                        description: str = '') -> Playlist:
        new_playlist_json = self.client.user_playlist_create(user=self.user['id'], name=name, public=public,
                                                             collaborative=collaborative, description=description)
        new_playlist = Playlist(new_playlist_json['id'])

        b64_image = image_to_b64(new_playlist.image)
        self.client.playlist_upload_cover_image(playlist_id=new_playlist.id, image_b64=b64_image)

        return new_playlist

    def new_playlist_by_random_genre(self, genre: str, length_min: int) -> Playlist:
        track_count = int(length_min / 3)

        tracks = self.random_tracks_by_genre(genre_name=genre, track_count=track_count)
        playlist = self.create_playlist(name=genre, public=False, collaborative=False,
                                        description=f'{track_count} randomly selected tracks within the genre \'{genre}\'')

        track_ids = keys_from_dict(tracks)
        for track in track_ids:
            self.add_to_playlist(playlist=playlist, track=Track(track))

        return playlist

    @property
    def player(self) -> Player:
        return Player()


# Spotify independent instances:
# init_player = {
#
# }
# test_player = Player(standard_player=init_player)


def image_from_url(image_url: str) -> Image:
    # Example: Load an image from an URL
    response = requests.get(image_url)
    return Image.open(io.BytesIO(response.content))


def image_from_file(file_path: str) -> Image:
    return Image.open(file_path)


def tk_image_from_file(file_path: str) -> Image:
    new_image_width = int(0.05*frontend_window_size[0])
    new_image_height = int(0.07*frontend_window_size[1])
    image = Image.open(file_path)
    image = image.resize((new_image_width, new_image_height), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(image)
    return image


def show_image(image: Image) -> None:
    image.show()


def resize_image(image: Image, width=100, height=100) -> bytes:
    # Perform image operations (example: resize)

    new_size = (width, height)
    resized_image = image.resize(new_size)

    return resized_image


def bytes_to_image(image_bytes: bytes) -> Image:
    image = Image.open(BytesIO(image_bytes)).convert("RGBA")
    return image


def get_tk_image(image: Image, image_size: [int, int]) -> ImageTk:
    # response = requests.get(image)
    # image_data = BytesIO(response.content)
    # original_image = Image.open(image_data)
    # resized_image = original_image.resize((image_size[0], image_size[1]), Image.Resampling.LANCZOS)
    resized_image = image.resize((image_size[0], image_size[1]), Image.Resampling.LANCZOS)
    instance_image = ImageTk.PhotoImage(resized_image)
    return instance_image


def image_to_b64(image: Image) -> str:
    output = BytesIO()
    image.save(output, format='JPEG')
    im_data = output.getvalue()

    image_data = base64.b64encode(im_data)
    if not isinstance(image_data, str):
        # Python 3, decode from bytes to string
        image_data = image_data.decode()

    return image_data


def get_instruments(track: Track) -> JSON:
    instruments:JSON = None

    # ToDo: analyze track

    return instruments


if __name__ == '__main__':
    # test_track = Track(spotify_track_id='60a0Rd6pjrkxjPbaKzXjfq')
    # test_album = Album(spotify_album_id='0DoVnWjNFYoUfq7qe36jxh')
    # test_artist = Artist(artist_spotify_id='6MwPCCR936cYfM1dLsGVnl')
    # test_playlist = Playlist(spotify_playlist_id='6bRkO7PLCXgmV4EJH52iU4')
    # test_user = User(spotify_user_id='simonluca1')
    # test_user.get_user_profile()
    # test_devices = Devices()
    # test_device = Device('FLEX5I', devices=test_devices)
    # test_player = Player()
    # print(test_player.is_playing)
    # test_myDatabase = MyAppDatabase('Databases/myApp.db')
    # test_myApp = SpotifyApp()
    # text_converter = JsonDatabase('Databases/TrackTank.db')

    # new_user = User('ji36vamlv0b5rkri5si22h4tm')
    # json_to_file('Databases/JSON_Files/new_user.json', sp.user('ji36vamlv0b5rkri5si22h4tm'))
    # json_to_file('Databases/JSON_Files/saved_tracks.json',sp.current_user_saved_tracks(limit=2, market=market))
    # current_user = User(sp.current_user()['id'])
    # my_App = SpotifyApp()
    # play_list_id = url_to_uri('https://open.spotify.com/playlist/6bRkO7PLCXgmV4EJH52iU4?si=a2b9f98b8a544b2e', True)
    # test_playlist = Playlist(play_list_id)
    # print(test_playlist.tracks)
    # my_App.random_playlist_shuffle(test_playlist, 'random')
    # print(my_App.is_item_blacklisted())

    # Test Blacklist
    # json_dat = JsonDatabase(database_file='Databases/JSON_Files/blacklist.json')
    # black_track = Track(spotify_track_id='2FRnf9qhLbvw8fu4IBXx78')
    # black_track.is_blacklisted = 1
    # print(black_track.is_blacklisted)

    myApp = SpotifyApp()
    track_ = Track(
        spotify_track_id=url_to_uri('https://open.spotify.com/track/3l0y7QwjtDPtKEw4ucTg0i?si=aq0iRB2MQwyKonwikS1J6g',
                                    to_id=True))
    track_.print_track_profile()
    # random__tracks = myApp.random_tracks_by_genre(genre_name='pop', track_count=12)
    # print(len(keys_from_dict(random__tracks)))
    # test_image = image_from_file('nonPythonRelevant/Python-logo-notext.svg.png')
    # myApp.create_playlist(name='Test', public=False, collaborative=False, description='first playlist creation via python')
    # test_pl = myApp.new_playlist_by_random_genre(genre='gymcore', length_min=180)

    # image_path = 'nonPythonRelevant/Spotipy_if_no_image.png'
    # show_image(image_from_file(image_path))
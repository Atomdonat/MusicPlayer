import os
import re
from typing import *
import requests
import numpy
import spotipy
from spotipy import SpotifyException, SpotifyOAuth
import base62


import random
import time
import sqlite3
import json

import base64
from PIL import Image, ImageTk
import io
from io import BytesIO
from tkinter import PhotoImage
import sys
from datetime import timedelta
from PIL import Image, ImageTk
from dotenv import load_dotenv
from dataclasses import dataclass


frontend_window_size: list = [800, 400]
json_path: str = 'Databases/JSON_Files/spotify_devices.json'
no_image_path: str = 'Icons/Spotify_if_no_image.png'
max_popularity = 20
skipping_steps: dict = {
    "20sec": -2,
    "0.5_of_duration": -1,
    "0.75_of_duration": -0.5,
    "last_quarter": 0,
    "not_skipped": 1
}


@dataclass
class SpotifyID:
    spotify_id: base62


@dataclass
class SpotifyURI:
    spotify_uri: str

    def __post_init__(self):
        valid_uri_starts = [
            'spotify:album:',
            'spotify:artist:',
            'spotify:playlist:',
            'spotify:track:',
            'spotify:user:',
        ]
        if not self.spotify_uri.startswith(tuple(valid_uri_starts)):
            raise ValueError('Spotify URI is invalid')

    def split(self, sep: str) -> List[str]:
        return self.spotify_uri.split(sep)


# noinspection DuplicatedCode
@dataclass
class Album:
    album_id: str
    album_name: str
    album_url: str
    album_image: str
    genre_names: list
    total_duration: int
    track_count: int
    artist_ids: list
    track_ids: list
    popularity: int
    blacklisted: int


# noinspection DuplicatedCode
@dataclass
class Artist:
    artist_id: str
    artist_name: str
    artist_url: str
    artist_image: str
    genre_names: list
    follower: int
    album_ids: list
    playlist_ids: list
    top_tracks_ids: list
    popularity: int
    blacklisted: int


# noinspection DuplicatedCode
@dataclass
class Genre:
    genre_name: str
    acousticness_lower_limit: float
    acousticness_upper_limit: float
    danceability_lower_limit: float
    danceability_upper_limit: float
    duration_ms: int
    energy_lower_limit: float
    energy_upper_limit: float
    instrumentalness_lower_limit: float
    instrumentalness_upper_limit: float
    key_lower_limit: int
    key_upper_limit: int
    liveness_lower_limit: float
    liveness_upper_limit: float
    loudness_lower_limit: float
    loudness_upper_limit: float
    mode_lower_limit: int
    mode_upper_limit: int
    speechiness_lower_limit: float
    speechiness_upper_limit: float
    tempo_lower_limit: float
    tempo_upper_limit: float
    valence_lower_limit: float
    valence_upper_limit: float


# noinspection DuplicatedCode
@dataclass
class Playlist:
    playlist_id: str
    playlist_name: str
    playlist_url: str
    playlist_image: str
    genre_names: list
    total_duration: int
    track_count: int
    owner_id: str
    track_ids: list
    popularity: int
    blacklisted: int


# noinspection DuplicatedCode
@dataclass
class Track:
    track_id: str
    track_name: str
    track_url: str
    track_image: str
    genre_names: list
    track_duration: int
    artist_ids: list
    album_ids: list
    playlist_ids: list
    popularity: int
    blacklisted: int


# noinspection DuplicatedCode
@dataclass
class TrackAnalysis:
    track_id: str
    track_name: str
    track_acousticness: float
    track_danceability: float
    track_duration_ms: int
    track_energy: float
    track_instrumentalness: float
    track_key: int
    track_liveness: float
    track_loudness: float
    track_mode: int
    track_speechiness: float
    track_tempo: float
    track_valence: float


# noinspection DuplicatedCode
@dataclass
class User:
    user_id: str
    user_name: str
    user_url: str
    user_image: str
    follower: int
    playlist_ids: list
    top_tracks_ids: list
    top_artists_ids: list
    top_genre_names: list
    popularity: int
    blacklisted: int
    
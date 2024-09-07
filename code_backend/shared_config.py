import os
import re
from typing import *
import requests
import numpy
import spotipy
from spotipy import SpotifyException, SpotifyOAuth


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


# local paths for files
json_path: str = '/home/simon/git_repos/MusicPlayer/Databases/JSON_Files/spotify_devices.json'
no_image_path: str = '/home/simon/git_repos/MusicPlayer/Icons/Spotify_if_no_image.png'
main_database_path = '/home/simon/git_repos/MusicPlayer/Databases/main_database.db'
track_analysis_tsv_file_path = "/home/simon/git_repos/MusicPlayer/Databases/CSV_Files/track_analysis.tsv"

max_popularity = 20
skipping_steps: dict = {
    "20sec": -2,
    "0.5_of_duration": -1,
    "0.75_of_duration": -0.5,
    "last_quarter": 0,
    "not_skipped": 1
}
market = 'DE'
frontend_window_size: list = [800, 400]


# noinspection DuplicatedCode
@dataclass
class Album:
    album_id: str
    album_name: str
    album_url: str
    album_image: str
    genre_names: list[str]
    total_duration: int
    track_count: int
    artist_ids: list[str]
    track_ids: list[str]
    popularity: int
    blacklisted: int


# noinspection DuplicatedCode
@dataclass
class Artist:
    artist_id: str
    artist_name: str
    artist_url: str
    artist_image: str
    genre_names: list[str]
    follower: int
    album_ids: list[str]
    playlist_ids: list[str]
    top_tracks_ids: list[str]
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
    popularity: int
    blacklisted: int


# noinspection DuplicatedCode
@dataclass
class Playlist:
    playlist_id: str
    playlist_name: str
    playlist_url: str
    playlist_image: str
    genre_names: list[str]
    total_duration: int
    track_count: int
    owner_id: str
    track_ids: list[str]
    popularity: int
    blacklisted: int


# noinspection DuplicatedCode
@dataclass
class Track:
    track_id: str
    track_name: str
    track_url: str
    track_image: str
    genre_names: list[str]
    track_duration: int
    artist_ids: list[str]
    album_ids: list[str]
    playlist_ids: list[str]
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
    playlist_ids: list[str]
    top_tracks_ids: list[str]
    top_artists_ids: list[str]
    top_genre_names: list[str]
    popularity: int
    blacklisted: int


@dataclass
class Device:
    device_id: str
    device_name: str
    device_type:str
    is_active: int
    is_private_session: int
    is_restricted: int
    supports_volume: int
    volume_percent:int

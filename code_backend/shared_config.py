# Standard library imports
import base64
from hashlib import sha256
import io
import json
import os
import random
import re
import sqlite3
import string
import sys
import threading
import time
from time import sleep
import timeit
from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO
from tkinter import PhotoImage
from typing import *
from urllib.parse import quote, urlencode

# Third-party library imports
import numpy
import requests
import spotipy
from dotenv import find_dotenv, load_dotenv, set_key
from PIL import Image, ImageTk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from spotipy import SpotifyException, SpotifyOAuth
from flask import Flask, jsonify, redirect, request


# local paths for files
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR_PATH = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
NO_IMAGE_PATH = os.path.join(ROOT_DIR_PATH, 'Icons', 'Spotipy_if_no_image.png')
MAIN_DATABASE_PATH = os.path.join(ROOT_DIR_PATH, 'Databases', 'main_database.db')
JSON_PATH = os.path.join(ROOT_DIR_PATH, 'Databases', 'JSON_Files', 'spotify_devices.json')

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SPOTIFY_USERNAME = os.getenv("SPOTIFY_USERNAME")
SPOTIFY_PASSWORD = os.getenv("SPOTIFY_PASSWORD")
MARKET = 'DE'
SCOPES = " ".join([
    'user-read-playback-state',
    'user-read-currently-playing',
    'user-modify-playback-state',
    'user-library-read',
    'user-top-read',
    'ugc-image-upload',
    'playlist-modify-public',
    'playlist-modify-private',
    'playlist-read-private',
    'user-read-email'
])

MAX_POPULARITY = 20
SKIPPING_STEPS: dict = {
    "20sec": -2,
    "0.5_of_duration": -1,
    "0.75_of_duration": -0.5,
    "last_quarter": 0,
    "not_skipped": 1
}
GUI_SIZE = [800, 400]

TEXTCOLOR = "\033[38;2;172;174;180m"
CBLACK="\x1b[30m"
CRED="\x1b[31m"
CGREEN="\x1b[32m"
CYELLOW="\x1b[33m"
CBLUE="\x1b[34m"
CMAGENTA="\x1b[35m"
CCYAN="\x1b[36m"
CWHITE="\x1b[37m"
CORANGE="\x1b[38;5;215m"

WAIT_TIME = 5

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


if __name__ == '__main__':
    """"""
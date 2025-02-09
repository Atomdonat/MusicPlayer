"""
    File containing every imported package for project and global constants
"""

# Standard library imports
import ast
import base64
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
import timeit
import traceback
from dataclasses import dataclass
from datetime import timedelta
from hashlib import sha256
from io import BytesIO
from time import sleep
from tkinter import PhotoImage
from typing import *
from urllib.parse import quote, urlencode

# Third-party library imports
import numpy
import requests
from dotenv import find_dotenv, load_dotenv, set_key
from PIL import Image, ImageTk
from requests import PreparedRequest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from flask import Flask, jsonify, redirect, request


# local paths for files
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR_PATH = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
NO_IMAGE_PATH = os.path.join(ROOT_DIR_PATH, 'Icons', 'Spotipy_if_no_image.png')
MAIN_DATABASE_PATH = os.path.join(ROOT_DIR_PATH, 'Databases', 'main_database.db')
JSON_PATH = os.path.join(ROOT_DIR_PATH, 'Databases', 'JSON_Files', 'spotify_devices.json')
ENV_PATH = os.path.join(ROOT_DIR_PATH,'code_backend', '.env')

load_dotenv(ENV_PATH)
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
    'user-read-email',
    'user-follow-read'
])

MAX_REQUESTS_PER_CALL = 500
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


if __name__ == '__main__':
    """"""
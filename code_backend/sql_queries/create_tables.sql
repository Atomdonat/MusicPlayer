CREATE TABLE IF NOT EXISTS albums (
    album_id TEXT PRIMARY KEY,
    album_name TEXT,
    album_url TEXT,
    album_image TEXT,
    genre_names TEXT,
    total_duration INTEGER,
    track_count INTEGER,
    artist_ids TEXT,
    track_ids TEXT,
    popularity INTEGER,
    blacklisted INTEGER,
    album_json TEXT
);

CREATE TABLE IF NOT EXISTS artists (
    artist_id TEXT PRIMARY KEY,
    artist_name TEXT,
    artist_url TEXT,
    artist_image TEXT,
    genre_names TEXT,
    follower INTEGER,
    album_ids TEXT,
    playlist_ids TEXT,
    top_track_ids TEXT,
    popularity INTEGER,
    blacklisted INTEGER,
    artist_json TEXT
);

CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    device_name TEXT,
    device_type TEXT,
    is_active INTEGER,
    is_private_session INTEGER,
    is_restricted INTEGER,
    supports_volume INTEGER,
    volume_percent INTEGER,
    device_json TEXT
);

CREATE TABLE IF NOT EXISTS  genres (
    genre_name TEXT PRIMARY KEY,
    acousticness_lower_limit REAL,
    acousticness_upper_limit REAL,
    danceability_lower_limit REAL,
    danceability_upper_limit REAL,
    duration_ms INTEGER,
    energy_lower_limit REAL,
    energy_upper_limit REAL,
    instrumentalness_lower_limit REAL,
    instrumentalness_upper_limit REAL,
    key_lower_limit INTEGER,
    key_upper_limit INTEGER,
    liveness_lower_limit REAL,
    liveness_upper_limit REAL,
    loudness_lower_limit REAL,
    loudness_upper_limit REAL,
    mode_lower_limit INTEGER,
    mode_upper_limit INTEGER,
    speechiness_lower_limit REAL,
    speechiness_upper_limit REAL,
    tempo_lower_limit REAL,
    tempo_upper_limit REAL,
    valence_lower_limit REAL,
    valence_upper_limit REAL,
    popularity INTEGER,
    blacklisted INTEGER,
    genre_json TEXT
);

CREATE TABLE IF NOT EXISTS playlists(
    playlist_id TEXT PRIMARY KEY,
    playlist_name TEXT,
    playlist_url TEXT,
    playlist_image TEXT,
    genre_names TEXT,
    total_duration INTEGER,
    track_count INTEGER,
    owner_id TEXT,
    track_ids TEXT,
    popularity INTEGER,
    blacklisted INTEGER,
    playlist_json TEXT
);

CREATE TABLE IF NOT EXISTS tracks (
    track_id TEXT PRIMARY KEY,
    track_name TEXT,
    track_url TEXT,
    track_image TEXT,
    genre_names TEXT,
    track_duration INTEGER,
    album_id TEXT,
    artist_ids TEXT,
    playlist_ids TEXT,
    popularity INTEGER,
    blacklisted INTEGER,
    track_json TEXT
);

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    user_name TEXT,
    user_url TEXT,
    user_image TEXT,
    top_genre_names TEXT,
    follower INTEGER,
    playlist_ids TEXT,
    top_track_ids TEXT,
    top_artist_ids TEXT,
    popularity INTEGER,
    blacklisted INTEGER,
    user_json TEXT
);

INSERT OR IGNORE INTO albums (album_id, album_name, album_uri, album_url, album_image, genre_names, total_duration, track_count, artist_ids, track_ids, popularity, blacklisted, album_json)
VALUES ('0000000000000000000000', 'dummy', 'spotify:album:0000000000000000000000', '', '', '[]', 0, 0, '[]', '[]', 0, 0, :album_json);
INSERT OR IGNORE INTO artists (artist_id, artist_name, artist_uri, artist_url, artist_image, genre_names, follower, album_ids, playlist_ids, top_track_ids, popularity, blacklisted, artist_json)
VALUES ('0000000000000000000000', 'dummy', 'spotify:artist:0000000000000000000000', '', '', '[]', 0, '[]', '[]', '[]', 0, 0, :artist_json);
INSERT OR IGNORE INTO devices (device_id, device_name, device_type, is_active, is_private_session, is_restricted, supports_volume, volume_percent, device_json)
VALUES ('0000000000000000000000000000000000000000', 'dummy', '', 0, 0, 0, 0, 0, :device_json);
INSERT OR IGNORE INTO playlists (playlist_id, playlist_name, playlist_uri, playlist_url, playlist_image, genre_names, total_duration, track_count, owner_id, track_ids, popularity, blacklisted, playlist_json)
VALUES ('0000000000000000000000', 'dummy', 'spotify:playlist:0000000000000000000000', '', '', '[]', 0, 0, '[]', '[]', 0, 0, :playlist_json);
INSERT OR IGNORE INTO tracks (track_id, track_name, track_uri, track_url, track_image, genre_names, track_duration, artist_ids, album_id, playlist_ids, popularity, blacklisted, track_json)
VALUES ('0000000000000000000000', 'dummy', 'spotify:track:0000000000000000000000', '', '', '[]', 0, '[]', '[]', '[]', 0, 0, :track_json);
INSERT OR IGNORE INTO users (user_id, user_name, user_uri, user_url, user_image, follower, playlist_ids, top_track_ids, top_artist_ids, top_genre_names, popularity, blacklisted, user_json)
VALUES ('0000000000000000000000', 'dummy', 'spotify:user:0000000000000000000000','', '', 0, '[]', '[]', '[]', '[]', 0, 0, :user_json);

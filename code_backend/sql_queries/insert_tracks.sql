INSERT OR IGNORE INTO tracks (track_id, track_name, track_uri, track_url, track_image, genre_names, track_duration, artist_ids, album_id, playlist_ids, popularity, blacklisted, track_json)
VALUES (:track_id, :track_name, :track_uri, :track_url, :track_image, :genre_names, :track_duration, :artist_ids, :album_id, :playlist_ids, :popularity, :blacklisted, :track_json);
INSERT OR IGNORE INTO users (user_id, user_name, user_uri, user_url, user_image, follower, playlist_ids, top_track_ids, top_artist_ids, top_genre_names, popularity, blacklisted, user_json)
VALUES (:user_id, :user_name, :user_uri, :user_url, :user_image, :follower, :playlist_ids, :top_track_ids, :top_artist_ids, :top_genre_names, :popularity, :blacklisted, :user_json);
methods = [
    {
        "name": "Get Several Tracks",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-several-tracks",
        "desc": "Get Spotify catalog information for multiple tracks based on their Spotify IDs.",
        "scopes": []
    },
    {
        "name": "Get Track",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-track",
        "desc": "Get Spotify catalog information for a single track identified by its unique Spotify ID.",
        "scopes": []
    },
    {
        "name": "Get Playlist",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-playlist",
        "desc": "Get a playlist owned by a Spotify user.",
        "scopes": []
    },
    {
        "name": "Change Playlist Details",
        "url": "https://developer.spotify.com/documentation/web-api/reference/change-playlist-details",
        "desc": "Change a playlist's name and public/private state. (The user must, of course, own the playlist.)",
        "scopes": []
    },
    {
        "name": "Get Playlist Items",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks",
        "desc": "Get full details of the items of a playlist owned by a Spotify user.",
        "scopes": []
    },
    {
        "name": "Update Playlist Items",
        "url": "https://developer.spotify.com/documentation/web-api/reference/reorder-or-replace-playlists-tracks",
        "desc": "Either reorder or replace items in a playlist depending on the request's parameters. To reorder items, include range_start, insert_before, range_length and snapshot_id in the request's body. To replace items, include uris as either a query parameter or in the request's body. Replacing items in a playlist will overwrite its existing items. This operation can be used for replacing or clearing items in a playlist. Note: Replace and reorder are mutually exclusive operations which share the same endpoint, but have different parameters. These operations can't be applied together in a single request.",
        "scopes": []
    },
    {
        "name": "Add Items to Playlist",
        "url": "https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist",
        "desc": "Add one or more items to a user's playlist.",
        "scopes": []
    },
    {
        "name": "Remove Playlist Items",
        "url": "https://developer.spotify.com/documentation/web-api/reference/remove-tracks-playlist",
        "desc": "Remove one or more items from a user's playlist.",
        "scopes": []
    },
    {
        "name": "Get Current User's Playlists",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists",
        "desc": "Get a list of the playlists owned or followed by the current Spotify user.",
        "scopes": []
    },
    {
        "name": "Get User's Playlists",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists",
        "desc": "Get a list of the playlists owned or followed by a Spotify user.",
        "scopes": []
    },
    {
        "name": "Create Playlist",
        "url": "https://developer.spotify.com/documentation/web-api/reference/create-playlist",
        "desc": "Create a playlist for a Spotify user. (The playlist will be empty until you add tracks.) Each user is generally limited to a maximum of 11000 playlists.",
        "scopes": []
    },
    {
        "name": "Get Playlist Cover Image",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-playlist-cover",
        "desc": "Get the current image associated with a specific playlist.",
        "scopes": []
    },
    {
        "name": "Add Custom Playlist Cover Image",
        "url": "https://developer.spotify.com/documentation/web-api/reference/upload-custom-playlist-cover",
        "desc": "Replace the image used to represent a specific playlist.",
        "scopes": []
    },
    {
        "name": "Get Artist",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-an-artist",
        "desc": "Get Spotify catalog information for a single artist identified by their unique Spotify ID.",
        "scopes": []
    },
    {
        "name": "Get Several Artists",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists",
        "desc": "Get Spotify catalog information for several artists based on their Spotify IDs.",
        "scopes": []
    },
    {
        "name": "Get Artist's Albums ",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums",
        "desc": "Get Spotify catalog information about an artist's albums.",
        "scopes": []
    },
    {
        "name": "Get Artist's Top Tracks ",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks",
        "desc": "Get Spotify catalog information about an artist's top tracks by country.",
        "scopes": []
    },
    {
        "name": "Check User's Saved Albums ",
        "url": "https://developer.spotify.com/documentation/web-api/reference/check-users-saved-albums",
        "desc": "Check if one or more albums is already saved in the current Spotify user's 'Your Music' library.",
        "scopes": []
    },
    {
        "name": "Get Album Tracks",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks",
        "desc": "Get Spotify catalog information about an album’s tracks. Optional parameters can be used to limit the number of tracks returned.",
        "scopes": []
    },
    {
        "name": "Get Several Albums ",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-multiple-albums",
        "desc": "Get Spotify catalog information for multiple albums identified by their Spotify IDs.",
        "scopes": []
    },
    {
        "name": "Get Album ",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-an-album",
        "desc": "Get Spotify catalog information for a single album.",
        "scopes": []
    },
    {
        "name": "Get User's Saved Albums",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-users-saved-albums",
        "desc": "Get a list of the albums saved in the current Spotify user's 'Your Music' library.",
        "scopes": []
    },
    {
        "name": "Get Track's Audio Features",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-audio-features",
        "desc": "Get audio feature information for a single track identified by its unique Spotify ID.",
        "scopes": []
    }, {
        "name": "Get Several Tracks' Audio Features",
        "url": "https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features",
        "desc": "Get audio features for multiple tracks based on their Spotify IDs.",
        "scopes": []
    }
]

# with open("spotify_web_api.py", "w") as file:

for current_method in methods:
    current_name = current_method["name"].lower().replace(" ", "_").replace("'", "")
    method = f"""\
# mps: 0
def {current_name}():
    \"\"\"
    {current_method["desc"]}
    Needed Scopes: {current_method["scopes"]}
    Official API Documentation: {current_method["url"]}
    \"\"\"
    raise NotImplementedError


"""
    print(method)

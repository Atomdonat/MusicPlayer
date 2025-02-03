methods = [
    # {
    #     "name": "",
    #     "url": "",
    #     "desc": "",
    #     "scopes": [""],
    #     "request_type": ""
    # }
    {
        "name": "Search for Item",
        "url": "https://developer.spotify.com/documentation/web-api/reference/search",
        "desc": "Get Spotify catalog information about albums, artists, playlists, tracks, shows, episodes or audiobooks that match a keyword string. Audiobooks are only available within the US, UK, Canada, Ireland, New Zealand and Australia markets.",
        "scopes": [""],
        "request_type": "GET"
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
    Needed Scopes: {current_method["scopes"] if len(current_method["scopes"]) > 0 else "None"}
    Official API Documentation: {current_method["url"]}
    \"\"\"
    response = api_request_data(
        url=f"",
        request_type=\"{current_method["request_type"]}\",
        json_data="",
        overwrite_header=False,
    )

"""
    print(method)

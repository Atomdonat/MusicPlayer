from code_backend.organize_playlist import *
import pytest

TEST_PLAYLIST_URI = url_to_uri("https://open.spotify.com/playlist/6bRkO7PLCXgmV4EJH52iU4?si=fbe6a250558f45f8")  # track_count=5
PROD_PLAYLIST_URI = url_to_uri("https://open.spotify.com/playlist/6QjbdNFUe4SFNE82RTmcCJ?si=ca49189f2c994135")  # track_count=98


@pytest.fixture(autouse=True)
def revert_tests():
    test_track_uris = [
        "spotify:track:6zrR8itT7IfAdl5aS7YQyt",
        "spotify:track:60a0Rd6pjrkxjPbaKzXjfq",
        "spotify:track:3gVhsZtseYtY1fMuyYq06F",
        "spotify:track:5DXGHZ3QDh0FcLXPMWTv9U",
        "spotify:track:60eOMEt3WNVX1m1jmApmnX"
    ]
    prod_track_uris = [
        'spotify:track:2ww2xnkptug8KwF6XzEwMq', 'spotify:track:5oalZAqETYfixh9TIbWeIQ', 'spotify:track:5a3qqnzBzpY9at2h7kpGW5', 'spotify:track:3aYBjxTMvrEOP0A0UXg9ER', 'spotify:track:1KvyBpAxgllKW7bQb0GYCR', 'spotify:track:737yse38y2hsWQeNRrLaMY', 'spotify:track:4BRvD5QdauTo8EuUvYchu3',
        'spotify:track:3S8MFB68isPbRVgaU0MaIW', 'spotify:track:0OYcEfskah1egYHjYRvbg1', 'spotify:track:3dJj6o9o1fRgrojWjailuz', 'spotify:track:35jdp4bY3CABKBroODRq7Y', 'spotify:track:0J1IJsMbKWb5g2sJArTkGF', 'spotify:track:16AFbRYIdpesOleGTKClHs', 'spotify:track:7nAfXgeHfDO50upcOjJOaq',
        'spotify:track:5ZIcLKQxzyI3nPnivwuylV', 'spotify:track:4qVR3CF8FuFvHN4L6vXlB1', 'spotify:track:0fxGA5lxrdYNYoE7yJxTNZ', 'spotify:track:32fEW4jygJjjnZh2iBa5IR', 'spotify:track:4JqgUZ4yZqjeEmgJNsuUjX', 'spotify:track:5mFZipkX1HZ4Idz5LOWpzq', 'spotify:track:1NxBqfjNr4bFHQbZ65foDt',
        'spotify:track:2n1jBz26dVBtSbMvJNjGsu', 'spotify:track:3fjmSxt0PskST13CSdBUFx', 'spotify:track:1fLlRApgzxWweF1JTf8yM5', 'spotify:track:3PvwlVjMxuAqN8rJc84zPg', 'spotify:track:3zZ009FB8sc8JghwVrbLFq', 'spotify:track:6lXhmc2P7lGOBZDasmS9Uv', 'spotify:track:6xtQ23d8GEXgcxyUKPtwc5',
        'spotify:track:2ipYQ6pcabz1NovVrr9LKH', 'spotify:track:0TTN18FVx6Ibfqzotyneok', 'spotify:track:3dxiWIBVJRlqh9xk144rf4', 'spotify:track:00KfIFi2TpAaQGPbRbFbKJ', 'spotify:track:1EDPVGbyPKJPeGqATwXZvN', 'spotify:track:1obWEuIAC3pzFUgljW5nAa', 'spotify:track:7M8eZBRTD9QNasEVReEM0H',
        'spotify:track:6R1yUVtY4dPrGFOD7Eghrl', 'spotify:track:5JHNg1hxZFT7TDEphhM4wj', 'spotify:track:69ZEgPX0hxWXJIqkTlYz41', 'spotify:track:26mWgYHPpUhDWaYS9xxkXG', 'spotify:track:4Yf5bqU3NK4kNOypcrLYwU', 'spotify:track:1KEQ9UIwVhQ3dCzKJ3ORFr', 'spotify:track:5egqKwgK5r5rvGD1LrtR7J',
        'spotify:track:6L5QMBrydoaapTDMQ0Anui', 'spotify:track:3cQGb2POE359G9WH81bF60', 'spotify:track:6OocN63GLU7NF0wHdewhID', 'spotify:track:62pPrpXsLR3Hbdw6kkA99L', 'spotify:track:6c0I7CfL9ziGZN8yYkLppP', 'spotify:track:45Wip7bDtu3hnyGvKyVw2N', 'spotify:track:0sp00HSXkQyqTa6QqM0O8V',
        'spotify:track:1Zeo9glWlcZrqdmTPXoK9o', 'spotify:track:3aZQQWGNShP6IzzaprPlFX', 'spotify:track:5rAxhWcgFng3s570sGO2F8', 'spotify:track:7hPBYRCHcBUMT7I5V9Go2s', 'spotify:track:5Rcs3fREgibWujLUlUb8KA', 'spotify:track:2HBBM75Xv3o2Mqdyh1NcM0', 'spotify:track:0UFDKFqW2oGspYeYqo9wjA',
        'spotify:track:3k4gjmYNJugQRlh2aounZ9', 'spotify:track:373gDROnujxNTFa1FojYIl', 'spotify:track:5DyMj79ijY8WptFX8YJxDS', 'spotify:track:7BkzAHnNW7WfrT4NcLaUDx', 'spotify:track:3xXBsjrbG1xQIm1xv1cKOt', 'spotify:track:5bvgRxco3jgSZ3SP8rueDA', 'spotify:track:60a0Rd6pjrkxjPbaKzXjfq',
        'spotify:track:7diOv6wm3ngF7Vt6ubK0Sf', 'spotify:track:5Z6g6zZwPX6sLw9wU3nJaM', 'spotify:track:6Wx88Mv6b9ofjKMKkdwOJd', 'spotify:track:6i5qhmmF9UNUBRyrPSGn4m', 'spotify:track:4zNk347FJz4yDDcjUhJJMI', 'spotify:track:3K4HG9evC7dg3N0R9cYqk4', 'spotify:track:57BrRMwf9LrcmuOsyGilwr',
        'spotify:track:2oNYsdCasRRlz1shXFAz7D', 'spotify:track:50jyxHSIHAz7N5jIzODvs4', 'spotify:track:16XJqMv1M2D1seDcPEznfY', 'spotify:track:7kxM3UJwN6rHAW5kwdlAHK', 'spotify:track:34isqXjbTstbYwl2MfdzDq', 'spotify:track:1dYw8HTRJnFpeEeMtXj99a', 'spotify:track:3NvAcUYxfyZhW2ALOGknXB',
        'spotify:track:56k09emMLjXvPwuVyjR4tn', 'spotify:track:1r1fPuhj9H4VdXr7OK6FL5', 'spotify:track:7oVEtyuv9NBmnytsCIsY5I', 'spotify:track:5uuXtfqM7Wp3idCxyHeOll', 'spotify:track:3h5gMWp1KJQkLBgCtG5EgH', 'spotify:track:1EU3VuKGZOvd1HTkxLPUXK', 'spotify:track:7GVqIMb6OdMY5mG7fUrtOq',
        'spotify:track:1Vej0qeQ3ioKwpI6FUbRv1', 'spotify:track:5njHkFji5oL7cYrbuHZyaC', 'spotify:track:4dbveKUpOx62SiwXQCALQH', 'spotify:track:3FQCJI2t5LTbsRPfYVBSVB', 'spotify:track:1gAaRSN57UYVRI4eWRyAvP', 'spotify:track:2cZXlLwkRmDww37tbEygXl', 'spotify:track:1YxwrB0UypHNMghmFM9ZQR',
        'spotify:track:650OeHTLxZAQmb4aEbGmaA', 'spotify:track:697M5JB8FDIyRXEXgl1pBZ', 'spotify:track:104buTcnP2AsxqB7U1FIZ4', 'spotify:track:6015DaBwB49tXWlmNPo64w', 'spotify:track:6aCBjSb87RizdH8lVBIRW7']

    # Revert 'SpotipyTest':
    spotify.update_playlist_items(playlist_id="6bRkO7PLCXgmV4EJH52iU4", track_uris=test_track_uris)
    # Revert 'Linkin Park Only (Shuffled)':
    spotify.update_playlist_items(playlist_id="1TufW5MXE6oDxo7KVw4ACV", track_uris=prod_track_uris)


def test_shuffle():
    organize_collection(
        collection_uri=TEST_PLAYLIST_URI,
        shuffle=True
    )

def test_remove_duplicates():
    organize_collection(
        collection_uri=TEST_PLAYLIST_URI,
        remove=[
            "duplicate"
        ]
    )

def test_remove():
    organize_collection(
        collection_uri=TEST_PLAYLIST_URI,
        remove=[
            "Live in",
            "Live from",
            "Acoustic",
            "duplicate"
        ]
    )
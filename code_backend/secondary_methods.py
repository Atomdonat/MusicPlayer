from shared_config import *
from spotify_access import *


frontend_window_size = [800, 400]
market = 'DE'


def millis_to_minutes(millis: int, to_hours: bool = False) -> str:
    if to_hours:
        return str(timedelta(seconds=millis // 1000))
    else:
        return str(timedelta(seconds=millis // 1000)) + "." + str(millis % 1000)  # .strip(":")[2:]


def url_to_uri(spotify_url: str, to_id: bool = False) -> str:
    class_type = spotify_url.split("/")[-2]

    if class_type[-1] == "s":
        class_type = class_type[:-1]

    id_ = (spotify_url.split("/")[-1]).split("?")[0]
    if to_id:
        return id_
    else:
        return "spotify:" + class_type + ":" + id_


def id_to_uri(class_type: str, spotify_id: str) -> str:
    return "spotify:" + class_type + ":" + spotify_id


def uri_to_id(spotify_uri: str) -> str:
    return spotify_uri.split(":")[-1]


def json_to_file(json_filepath, json_data, overwrite: bool = False):
    if not overwrite:
        if not os.path.exists(json_filepath):
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
    else:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)


def average_file_size(directory_path: str) -> float:
    current_size = 0
    counted_files = 0

    for filename in os.listdir(directory_path):
        # if re.search('track',filename) != None:
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            current_size += os.path.getsize(file_path)
            counted_files += 1

    return current_size / counted_files


def values_from_dict(dictionary: dict) -> list:
    value_list = []
    for current_value in dictionary.values():
        value_list.append(current_value)
    return value_list


def keys_from_dict(dictionary: dict) -> list:
    keys_list = []
    for current_key in dictionary.keys():
        keys_list.append(current_key)
    return keys_list


def list_from_dict(dictionary: dict) -> list:
    dict_list = []
    for key, value in dictionary.items():
        dict_list.append([key, value])

    return dict_list


def format_bytes(input_bytes: int):
    factor = 1
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for unit in units:
        new_factor = factor * 1024
        if input_bytes <= new_factor:
            return f'{input_bytes/factor:.2f} {unit}'
        factor = new_factor


def value_from_dict(dictio: dict) -> str:
    return next(iter(dictio.values()))


def try_spotify_connection():
    try:
        sp = spotify_client()
        return sp
    except SpotifyException:
        print('Spotify went mimimi...\n will retry again')
        return try_spotify_connection()


def valid_spotify_uri(spotify_connection: spotipy.Spotify, spotify_uri: str) -> bool:
    uri_parts = spotify_uri.split(':')
    uri_type, spotify_id = uri_parts[1:]

    # Dummy
    if spotify_id == "0000000000000000000000":
        return True

    # Normal ID
    try:
        match uri_type:
            case 'album':
                spotify_connection.album(album_id=spotify_id, market=market)
            case 'artist':
                spotify_connection.artist(artist_id=spotify_id)
            case 'playlist':
                spotify_connection.playlist(playlist_id=spotify_id, market=market)
            case 'track':
                spotify_connection.track(track_id=spotify_id, market=market)
            case 'user':
                spotify_connection.user(user=spotify_id)

        return True

    except SpotifyException:
        return False


def list_from_id_string(id_string: str) -> list[str]:
    list_elements = id_string[1:-1].replace("'", "").split(', ')
    id_list = []
    for element in list_elements:
        id_list.append(element)

    return id_list


def string_from_list(id_list: list) -> str:
    return str(id_list)


def image_from_url(image_url: str) -> Image:
    # Example: Load an image from an URL
    response = requests.get(image_url)
    return Image.open(io.BytesIO(response.content))


def image_from_file(file_path: str) -> Image:
    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)

    return Image.open(file_path)


def show_image(image: Image) -> None:
    image.show()


def resize_image(image: Image, width=100, height=100) -> bytes:
    # Perform image operations (example: resize)

    new_size = (width, height)
    resized_image = image.resize(new_size)

    return resized_image


def bytes_to_image(image_bytes: bytes) -> Image:
    image = Image.open(BytesIO(image_bytes)).convert("RGBA")
    return image


def get_tk_image(image: Image, image_size: [int, int]) -> ImageTk:
    # response = requests.get(image)
    # image_data = BytesIO(response.content)
    # original_image = Image.open(image_data)
    # resized_image = original_image.resize((image_size[0], image_size[1]), Image.Resampling.LANCZOS)
    resized_image = image.resize((image_size[0], image_size[1]), Image.Resampling.LANCZOS)
    instance_image = ImageTk.PhotoImage(resized_image)
    return instance_image


def tk_image_from_file(file_path: str) -> Image:
    new_image_width = int(0.05*frontend_window_size[0])
    new_image_height = int(0.07*frontend_window_size[1])
    image = Image.open(file_path)
    image = image.resize((new_image_width, new_image_height), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(image)
    return image


def image_to_b64(image: Image, image_format: Literal['PNG', 'JPEG'] | str) -> str:
    output = BytesIO()
    try:
        image.save(output, format=image_format)
        im_data = output.getvalue()

        image_data = base64.b64encode(im_data)
        if not isinstance(image_data, str):
            # Python 3, decode from bytes to string
            image_data = image_data.decode()

        return image_data

    except Exception as e:
        print(f"\x1b[31m{e}: Image format error!\nMake sure the Image format matches (https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html)\x1b[30m")


def spotify_image_bytes(image_url: str) -> str:
    image = image_from_url(image_url)
    return image_to_b64(image=image, image_format='JPEG')


def file_image_bytes(image_path: str) -> str:
    image = image_from_file(image_path)
    return image_to_b64(image=image, image_format='JPEG')


if __name__ == '__main__':
    image_pth = '../Icons/Spotipy_if_no_image.png'


"""
File containing (helper) methods outsourced from other files
"""

from code_backend.shared_config import *


def millis_to_minutes(millis: int, to_hours: bool = False) -> str:
    """
    Convert milliseconds to minutes or hours
    :param millis: value in milliseconds
    :param to_hours: if to convert to hours
    :return: converted milliseconds
    """
    if to_hours:
        return str(timedelta(seconds=millis // 1000))
    else:
        return str(timedelta(seconds=millis // 1000)) + "." + str(millis % 1000)  # .strip(":")[2:]


def url_to_uri(spotify_url: str, to_id: bool = False) -> str:
    """
    Convert spotify url to uri
    :param spotify_url: url to spotify item
    :param to_id: if to get only the id
    :return: Spotify uri or id
    """
    class_type = spotify_url.split("/")[-2]

    if class_type[-1] == "s":
        class_type = class_type[:-1]

    id_ = (spotify_url.split("/")[-1]).split("?")[0]
    if to_id:
        return id_
    else:
        return "spotify:" + class_type + ":" + id_


def id_to_uri(class_type: Literal['album', 'artist', 'track', 'playlist', 'user'], spotify_id: str) -> str:
    """
    Convert spotify id to uri
    :param class_type: what item type to use
    :param spotify_id: spotify id
    :return: spotify uri
    """
    return "spotify:" + class_type + ":" + spotify_id


def uri_to_id(spotify_uri: str, get_type: bool = False) -> tuple[str,str] | str:
    """
    Extract the Spotify ID (and Type) from the Spotify URI in the form of "spotify:${type}:${id}"
    :param spotify_uri: The Spotify URI for the item.
    :param get_type: if to get the Spotify type (e.g. album)
    :return: item_id | (item_id, item_type)
    """
    if not spotify_uri.startswith("spotify:"):
        raise ValueError("Invalid Spotify URI, must be in the form of \"spotify:${type}:${id}\"")

    uri_parts = spotify_uri.split(":")

    return [uri_parts[2],uri_parts[1]] if get_type else uri_parts[2]


def json_to_file(json_filepath, json_data, overwrite: bool = False):
    """
    Dump a dict into a json file
    :param json_filepath: where to save the json file
    :param json_data: json data
    :param overwrite: if to overwrite the json file if it exists
    """
    json_filepath = absolute_path(json_filepath)

    if not overwrite:
        if not os.path.exists(json_filepath):
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
    else:
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)


def average_file_size(directory_path: str) -> float:
    """
    Calculate the average file size of a directory
    :param directory_path: path to directory
    :return: size in bytes
    """
    current_size = 0
    counted_files = 0

    directory_path = absolute_path(directory_path)
    for filename in os.listdir(directory_path):
        # if re.search('track',filename) != None:
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            current_size += os.path.getsize(file_path)
            counted_files += 1

    return current_size / counted_files


def format_bytes(input_bytes: int):
    """
    Convert bytes to human-readable string
    :param input_bytes: bytes
    :return: human-readable string
    """
    factor = 1
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for unit in units:
        new_factor = factor * 1024
        if input_bytes <= new_factor:
            return f'{input_bytes/factor:.2f} {unit}'
        factor = new_factor


def value_from_dict(dictio: dict) -> str:
    return next(iter(dictio.values()))


def key_from_dict(dictio: dict) -> str:
    return next(iter(dictio.keys()))


def list_from_id_string(id_string: str) -> list[str]:
    """
    Convert an id string into a list of strings (`load_list_from_database()` should do this better?)
    :param id_string: input id string
    :return: list of id strings
    """
    list_elements = id_string[1:-1].replace("'", "").split(', ')

    return [element for element in list_elements]


def image_from_url(image_url: str) -> Image:
    """
    Load an image from a URL
    :param image_url: image url
    :return: Pillow Image
    """
    response = requests.get(image_url)
    return Image.open(io.BytesIO(response.content))


def image_from_file(file_path: str) -> Image:
    """
    Load an image from a file
    :param file_path: path to file
    :return: Pillow Image
    """
    file_path = absolute_path(file_path)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)

    return Image.open(file_path)


def resize_image(image: Image, width=100, height=100) -> bytes:
    """
    Resize an image to a given width and height
    :param image: what image to resize
    :param width: target width
    :param height: target height
    :return: bytes of resized image
    """
    new_size = (width, height)
    resized_image = image.resize(new_size)

    return resized_image


def bytes_to_image(image_bytes: bytes) -> Image:
    """
    Convert bytes to an image using the RGBA matrix
    :param image_bytes: image bytes
    :return: Pillow Image
    """
    image = Image.open(BytesIO(image_bytes)).convert("RGBA")
    return image


def get_tk_image(image: Image, image_size: [int, int]) -> ImageTk:
    """
    Convert Pillow Image to Tk Image
    :param image: Pillow Image
    :param image_size: target image size [width, height]
    :return: Tk Image
    """
    # response = requests.get(image)
    # image_data = BytesIO(response.content)
    # original_image = Image.open(image_data)
    # resized_image = original_image.resize((image_size[0], image_size[1]), Image.Resampling.LANCZOS)
    resized_image = image.resize((image_size[0], image_size[1]), Image.Resampling.LANCZOS)
    instance_image = ImageTk.PhotoImage(resized_image)
    return instance_image


def tk_image_from_file(file_path: str) -> Image:
    """
    Load an Tk image from a file
    :param file_path: path to file
    :return: Tk Photo Image
    """
    new_image_width = int(0.05 * GUI_SIZE[0])
    new_image_height = int(0.07 * GUI_SIZE[1])
    image = Image.open(absolute_path(file_path))
    image = image.resize((new_image_width, new_image_height), Image.Resampling.LANCZOS)
    image = ImageTk.PhotoImage(image)
    return image


def image_to_b64(image: Image, image_format: Literal['PNG', 'JPEG'] | str) -> str:
    """
    Convert an image to base64
    :param image: Pillow Image
    :param image_format: source format
    :return: base64 encoded image
    """
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
        print(f"{CRED}{e}: Image format error!\nMake sure the Image format matches (https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html){TEXTCOLOR}")


def spotify_image_bytes(image_url: str) -> str:
    """
    Load an image from a URL to a Spotify usable image
    :param image_url: url to image
    :return: bytes for spotify
    """
    image = image_from_url(image_url)
    return image_to_b64(image=image, image_format='JPEG')


def file_image_bytes(image_path: str) -> str:
    """
    Load an image from path to a Spotify usable image
    :param image_path: path to image
    :return: bytes for spotify
    """
    image = image_from_file(absolute_path(image_path))
    return image_to_b64(image=image, image_format='JPEG')


def split_list_into_chunks(lst: list, chunk_length: int = 50) -> list:
    """
    Split a list into chunks of size chunk_length
    :param lst: what list to split
    :param chunk_length: size of each chunk
    :return: chunked list
    """
    return [lst[x:x+chunk_length] for x in range(0, len(lst), chunk_length)]


T = TypeVar('T')
def concat_iterables(iter1: Iterable[T], iter2: Iterable[T]) -> List[T]:
    """
    Concat two iterables into one iterable.
    :param iter1: iterable 1
    :param iter2: iterable 2
    :return: concatenated iterable
    """
    return [*iter1, *iter2]


def debug_json(jason: dict):
    """
    Dump a dict into a .json file.
    :param jason: what dict to dump
    """
    with open(absolute_path("/code_backend/testing/debugging.json"), "w") as json_file:
        json.dump(jason, json_file, indent=4)


def check_upper_limit(limit: int, api_max_limit: int = 50) -> int:
    """
    Checks if the user limit exceeded the API limit.
    :param limit: current limit
    :param api_max_limit: maximum API limit
    :return: 0: limit okay; 1: API limit subceeded, print error message
    """
    if limit > api_max_limit:
        print_error(
            error_message=f"Limit of {limit} exceeded API limit of {api_max_limit} per request",
            exit_code=None
        )
        return 1

    return 0


def check_lower_limit(limit: int, api_min_limit: int = 1) -> int:
    """
    Checks if the user limit subceeded the API limit.
    :param limit: current limit
    :param api_min_limit: minimum API limit
    :return: 0: limit okay; 1: API limit subceeded, print error message
    """
    if limit < api_min_limit:
        print_error(
            error_message=f"Limit of {limit} subceeded API limit of {api_min_limit} per request",
            exit_code=None
        )
        return 1

    return 0


def check_limits(limit: int) -> int:
    """
    Checks if the limit is in range of the API.
    :param limit: current limit (1 <= limit <= MAX_REQUESTS_PER_CALL)
    :return: 0: limit okay; 1: limit out of API range, print error message; 2: API limit both subceeded and exceeded, print error message
    """
    return check_lower_limit(limit, 1) + check_upper_limit(limit, MAX_REQUESTS_PER_CALL)


def update_env_key(env_key: str, new_value) -> tuple[str, str]:
    """
    Update the env key with the new value.
    :param env_key: what key to update
    :param new_value: what new value to set
    :return: old value and current value
    """
    env_file = find_dotenv()
    if not env_file:
        print(f"\n\x1b[31mCould not find .env file\n{TEXTCOLOR}")
    load_dotenv(env_file)

    old_value = os.getenv(env_key)

    os.environ[env_key] = new_value
    set_key(env_file, env_key, os.environ[env_key])
    return old_value, os.environ[env_key]


def check_token_expired(extended_token: bool = False) -> int:
    """
    Checks when the Token expires
    :param extended_token: Whether to check the regular Token (=False) or the extended one (=True)
    :return: Time till Token expires (if 0 is returned, the token did expire)
    """
    env_file = find_dotenv()
    if not env_file:
        print(f"\n\x1b[31mCould not find .env file\n{TEXTCOLOR}")
    load_dotenv(env_file)

    token_name = "EXTENDED_TOKEN" if extended_token else "REGULAR_TOKEN"
    token_data = json.loads(os.getenv(token_name))

    expiration_date = token_data["expires"]

    # Print time remaining
    # t = expiration_date - int(time.time())
    # print(f"Token expires in: {t//60} min {t%60} sec")

    return 0 if expiration_date - int(time.time()) < 1 else expiration_date - int(time.time())

def print_debug(content: str) -> None:
    """
    Print debug content
    :param content: what to display inside the debug block
    """
    print(f"{CORANGE}\n<----- Begin Debugging ----->\n\n{content}\n\n<------ End Debugging ------>\n{TEXTCOLOR}")


def print_error(error_message: str | Exception, more_infos: str = None, exit_code: int = None) -> None:
    """
    Give more information on error
    :param error_message: either an Exception or a custom error message
    :param more_infos: more infos e.g. what could have lead to the error
    :param exit_code: if to exit the program with code X (None: minor error, program can continue)
    :return: print detailed error message
    """
    print(f"\n{CORANGE}<===== Begin Error =====>{CRED}\n")
    print("Error message:", str(error_message))
    if more_infos:
        print("More infos:",more_infos)
    if isinstance(error_message, Exception):
        print("Error type:", error_message.__class__.__name__)
        print("Arguments:", error_message.args)
        print("Traceback:")
        print(traceback.format_exc())
    print(f"{CORANGE}<===== End Error =====>{TEXTCOLOR}\n")
    if exit_code:
        sys.exit(exit_code)


def print_http_error_codes(code: int, message: str = None, causing_query: str | requests.Request = None) -> None:
    """
    Web API uses the following response status codes, as defined in the RFC 2616 and RFC 6585
    Official API Documentation: https://developer.spotify.com/documentation/web-api/concepts/api-calls#response-status-codes
    :param code: HTTP Code of the request response
    :param message: Message of the error
    :param causing_query: Query parameter that caused the error
    """
    def pretty_print_POST(req: requests.Request):
        """
        by: AntonioHerraizS (https://stackoverflow.com/a/23816211)
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in
        this function because it is programmed to be pretty
        printed and may differ from the actual request.
        """
        req = req.prepare()
        return "{}\n{}\n{}\n\n{}\n{}".format(
            f'{CORANGE}-----------START-----------',
            req.method + ' ' + req.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body if req.body else '',
            f'------------END------------{TEXTCOLOR}\n'
        )

    error_data: dict
    with open(absolute_path("Databases/JSON_Files/http_errors.json"), "r") as e_file:
        error_data = json.load(e_file)[str(code)]
    # print(error_data["code"],"-",error_data["name"])
    print_error(
        error_message=f"Request returned Code: {error_data["code"]} - {error_data["name"]}\n{error_data["explanation"]}\n{TEXTCOLOR}Responsible Query:\n{pretty_print_POST(causing_query) if causing_query else "---"}",
        more_infos=message,
        exit_code=1
    )


def exclude_from_dict(target_dict: dict, exclude_keys: list) -> dict:
    """
    Safely exclude keys from a dictionary
    :param target_dict: what dictionary to exclude from
    :param exclude_keys: what keys to pop
    """
    for key in exclude_keys:
        target_dict.pop(key, None)

    return target_dict


def dict_factory(cursor, row) -> dict:
    """
    by Alex Martelli on Stackoverflow (https://stackoverflow.com/a/3300514)
    :param cursor: Database cursor
    :param row: Database table row
    :return: Dict containing the column names and values {column_name: value}
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_str_from_json_file(json_path: str) -> str:
    """
    Load a JSON file into a string
    :param json_path: path to JSON file
    :return: JSON file converted to string
    """
    with open(absolute_path(json_path), "r") as json_file:
        return json.dumps(json.load(json_file))


def load_sql_query(file_path: str) -> str:
    """
    Load a SQL query from a file Using the path from the Repository Root
    :param file_path: relative path to query file
    :return: loaded query
    """
    with open(absolute_path(file_path), "r") as query_file:
        return query_file.read()


def absolute_path(path: str) -> str:
    """
    Converts the given path to an absolute path. If the path is absolute nothing happens. If in doubt just call it
    :param path: (relative) path to convert
    :return: absolute path
    """

    if path.startswith(ROOT_DIR_PATH):
        return path
    else:
        # remove leading '/' or './'
        path = path[1:] if path.startswith("/") else path[2:] if path.startswith("./") else path

        return str(os.path.join(ROOT_DIR_PATH, path))


def load_json(path: str) -> dict:
    """
    Load JSON from .json file
    :param path: path to file
    :return: JSON object
    """
    path = absolute_path(path)
    with open(path, 'r') as j_file:
        return json.load(j_file)


def load_list_from_database(fetched_list: list) -> list:
    """
    Convert a list string into a list (e.g. ["['6O7MpKrY91vlCd4Osi6XKs']", "['2iLpvtffIrQ4bMYrFPRN4x']"] -> [['6O7MpKrY91vlCd4Osi6XKs'], ['2iLpvtffIrQ4bMYrFPRN4x']])
    :param fetched_list: list of list-strings
    :return: list containing flattened data
    """
    try:
        loaded_list = [ast.literal_eval(row) for row in fetched_list]
        return flatten(loaded_list)

    except Exception as exc:
        print(f"{CORANGE}The list '{fetched_list}' cannot be converted{TEXTCOLOR}")
        # print_error(
        #     error_message=exc,
        #     exit_code=None
        # )
        return fetched_list


def flatten(lst: list) -> list:
    """
    Recursively flatten a list
    :param lst: multidimensional list
    :return: one-dimensional list
    """
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

if __name__ == '__main__':
    """"""
    check_token_expired()
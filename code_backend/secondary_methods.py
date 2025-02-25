"""
File containing (helper) methods outsourced from other files
"""
from code_backend.shared_config import *
from code_backend.exceptions import InputException, CustomException, SpotifyIdException, SpotifyUriException, RequestException


def millis_to_minutes(millis: int, to_hours: bool = False) -> str:
    """
    Convert milliseconds to minutes or hours
    :param millis: value in milliseconds
    :param to_hours: if to convert to hours
    :return: converted milliseconds
    :raises InputException: if input is invalid
    """
    if not isinstance(millis, int):
        raise InputException(item_value=millis, valid_values="milliseconds", valid_types=int)

    if not isinstance(to_hours, bool):
        raise InputException(item_value=to_hours, valid_values=(True, False), valid_types=bool)

    if to_hours:
        return str(timedelta(seconds=millis // 1000))
    else:
        return str(timedelta(seconds=millis // 1000)) + "." + str(millis % 1000)  # .strip(":")[2:]



def url_to_uri(spotify_url: str, to_id: bool = False) -> str:
    """
    Convert spotify url to uri or id
    :param spotify_url: url to spotify item
    :param to_id: if to get only the id
    :return: Spotify uri or id
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(spotify_url, str):
        raise InputException(item_value=spotify_url, valid_values="spotify url", valid_types=str)

    if not isinstance(to_id, bool):
        raise InputException(item_value=to_id, valid_values=(True, False), valid_types=bool)

    try:
        class_type = spotify_url.split("/")[-2]
        id_ = (spotify_url.split("/")[-1]).split("?")[0]

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while converting spotify url to uri: '{spotify_url}'")


    class_type = class_type[:-1] if class_type[-1] == "s" else class_type

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
    :raises InputException: if input is invalid
    :raises SpotifyIdException: if spotify id is invalid
    """

    if not isinstance(class_type, str) or class_type not in ['album', 'artist', 'track', 'playlist', 'user']:
        raise InputException(item_value=class_type, valid_values=('album', 'artist', 'track', 'playlist', 'user'), valid_types=str)

    if not check_spotify_id(spotify_id=spotify_id, is_user=(class_type == 'user')):
        raise SpotifyIdException(invalid_id=spotify_id, id_type=class_type)

    return "spotify:" + class_type + ":" + spotify_id


def uri_to_id(spotify_uri: str, get_type: bool = False) -> tuple[str,str] | str:
    """
    Extract the Spotify ID (and Type) from the Spotify URI in the form of "spotify:${type}:${id}"
    :param spotify_uri: The Spotify URI for the item.
    :param get_type: if to get the Spotify type (e.g. album)
    :return: item_id | (item_id, item_type)
    :raises InputException: if input is invalid
    :raises SpotifyUriException: if spotify uri is invalid
    """
    if not check_spotify_uri(spotify_uri):
        raise SpotifyUriException(invalid_uri=spotify_uri)

    if not isinstance(get_type, bool):
        raise InputException(item_value=get_type, valid_values=(True, False), valid_types=bool)

    uri_parts = spotify_uri.split(":")

    return [uri_parts[2],uri_parts[1]] if get_type else uri_parts[2]


def json_to_file(json_filepath: str, json_data: dict, overwrite: bool = False):
    """
    Dump a dict into a json file
    :param json_filepath: where to save the json file
    :param json_data: json data
    :param overwrite: if to overwrite the json file if it exists
    :raises InputException: if input is invalid
    """

    json_filepath = absolute_path(json_filepath)

    if not isinstance(json_data, dict):
        raise InputException(item_value=json_data, valid_values="valid json data", valid_types=dict)

    if not isinstance(overwrite, bool):
        raise InputException(item_value=overwrite, valid_values=(True, False), valid_types=bool)


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
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    directory_path = absolute_path(directory_path)

    current_size = 0
    counted_files = 0

    try:
        for filename in os.listdir(directory_path):
            # if re.search('track',filename) != None:
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                current_size += os.path.getsize(file_path)
                counted_files += 1

        return current_size / counted_files
    
    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while calculating average file size of '{directory_path}'")


def format_bytes(input_bytes: int):
    """
    Convert bytes to human-readable string
    :param input_bytes: bytes
    :return: human-readable string
    :raises InputException: if input is invalid
    """

    if not isinstance(input_bytes, int) or input_bytes < 0:
        raise InputException(item_value=input_bytes, valid_values="positive integers", valid_types=int)

    factor = 1
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for unit in units:
        new_factor = factor * 1024
        if input_bytes <= new_factor:
            return f'{input_bytes/factor:.2f} {unit}'
        factor = new_factor


def value_from_dict(dictio: dict) -> Any:
    """

    :param dictio:
    :return: Value from dict
    :raises InputException: if input is invalid
    """
    if not isinstance(dictio, dict):
        raise InputException(item_value=dictio, valid_values="valid dict", valid_types=dict)

    return next(iter(dictio.values()))


def key_from_dict(dictio: dict) -> str:
    """

    :param dictio:
    :return:
    :raises InputException: if input is invalid
    """
    if not isinstance(dictio, dict):
        raise InputException(item_value=dictio, valid_values="valid dict", valid_types=dict)

    return next(iter(dictio.keys()))


def list_from_id_string(id_string: str) -> list[str]:
    """
    Convert an id string into a list of strings (`load_list_from_database()` should do this better?)
    :param id_string: input id string
    :return: list of id strings
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(id_string, str):
        raise InputException(item_value=id_string, valid_values="string containing list of ids", valid_types=str)

    try:
        list_elements = id_string[1:-1].replace("'", "").split(', ')
    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while parsing id string: '{id_string}'")

    return [element for element in list_elements]


def image_from_url(image_url: str) -> ImageFile:
    """
    Load an image from a URL
    :param image_url: image url
    :return: Pillow Image
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(image_url, str):
        raise InputException(item_value=image_url, valid_values="valid url", valid_types=str)

    try:
        query = requests.Request('GET', image_url)
        response = requests.get(image_url)

    except requests.exceptions.RequestException as error:
        raise RequestException(error=error, request_query=query)

    try:
        return Image.open(io.BytesIO(response.content))

    except (FileNotFoundError, UnidentifiedImageError, ValueError, TypeError) as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while trying to load image from url: '{image_url}'")


def image_from_file(file_path: str) -> Image:
    """
    Load an image from a file
    :param file_path: path to file
    :return: Pillow Image
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    file_path = absolute_path(file_path, is_file=True)

    try:
        return Image.open(file_path)

    except (FileNotFoundError, UnidentifiedImageError, ValueError, TypeError) as e:
        raise CustomException(error_message=e, more_infos=f"Exception occurred while trying to load image from file: '{file_path}'")


def resize_image(image: Image, width=100, height=100) -> bytes:
    """
    Resize an image to a given width and height
    :param image: what image to resize
    :param width: target width
    :param height: target height
    :return: bytes of resized image
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    if not isinstance(image, Image.Image):
        raise InputException(item_value=image, valid_values="valid image", valid_types=Image.Image)
    
    if not isinstance(width, int) or width <= 0:
        raise InputException(item_value=width, valid_values="positive integers", valid_types=int)
    
    if not isinstance(height, int) or height <= 0:
        raise InputException(item_value=height, valid_values="positive integers", valid_types=int)

    try:
        new_size = (width, height)
        resized_image = image.resize(new_size)
    
        return resized_image
    
    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while resizing image: \n'{image}',\nwidth: '{width}',\nheight: '{height}'")


def bytes_to_image(image_bytes: bytes) -> Image:
    """
    Convert bytes to an image using the RGBA matrix
    :param image_bytes: image bytes
    :return: Pillow Image
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    if not isinstance(image_bytes, bytes):
        raise InputException(item_value=image_bytes, valid_values="valid bytes", valid_types=bytes)
    
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGBA")
        return image
    except (FileNotFoundError, UnidentifiedImageError, ValueError, TypeError) as e:
        raise CustomException(error_message=e, more_infos=f"Exception occurred while converting bytes to image: '{image_bytes}'")
        


def get_tk_image(image: Image, image_size: [int, int]) -> ImageTk:
    """
    Convert Pillow Image to Tk Image
    :param image: Pillow Image
    :param image_size: target image size [width, height]
    :return: Tk Image
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    if not isinstance(image, Image.Image):
        raise InputException(item_value=image, valid_values="valid image", valid_types=Image.Image)
    
    if not isinstance(image_size, list) or len(image_size) != 2 or image_size[0] < 0 or image_size[1] < 0:
        raise InputException(item_value=image_size, valid_values="[positive integer, positive integers]", valid_types=list[int])
    
    try:
        resized_image = image.resize((image_size[0], image_size[1]), Image.Resampling.LANCZOS)
        instance_image = ImageTk.PhotoImage(resized_image)
        return instance_image
    
    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while converting Image to Tk Image: '{image}',\nwidth: '{image_size[0]}',\nheight: '{image_size[1]}'")    


def tk_image_from_file(file_path: str) -> Image:
    """
    Load an Tk image from a file
    :param file_path: path to file
    :return: Tk Photo Image
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    file_path = absolute_path(file_path, is_file=True)

    new_image_width = int(0.05 * GUI_SIZE[0])
    new_image_height = int(0.07 * GUI_SIZE[1])

    try:
        image = Image.open(file_path)
        image = image.resize((new_image_width, new_image_height), Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image)
        return image
    
    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while trying to load Tk image from file: '{file_path}'")


def image_to_b64(image: Image, image_format: Literal['PNG', 'JPEG'] | str) -> str:
    """
    Convert an image to base64
    :param image: Pillow Image
    :param image_format: source format
    :return: base64 encoded image
    :raises InputException: if input is invalid
    """
    
    if not isinstance(image, Image.Image):
        raise InputException(item_value=image, valid_values="valid image", valid_types=Image.Image)
    
    if not isinstance(image_format, str):
        raise InputException(item_value=image_format, valid_values="Image formats from (https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html)", valid_types=str)
    
    output = BytesIO()
    try:
        image.save(output, format=image_format)
        im_data = output.getvalue()

        image_data = base64.b64encode(im_data)
        if not isinstance(image_data, str):
            # Python 3, decode from bytes to string
            image_data = image_data.decode()

        return image_data

    except Exception as error:
        print(f"{CRED}{error}: Image format error!\nMake sure the Image format matches (https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html){TEXTCOLOR}")


def spotify_image_bytes(image_url: str) -> str:
    """
    Load an image from a URL to a Spotify usable image
    :param image_url: url to image
    :return: bytes for spotify
    :raises InputException: if input is invalid
    """
    
    if not isinstance(image_url, str):
        raise InputException(item_value=image_url, valid_values="valid url", valid_types=str)
    
    image = image_from_url(image_url)
    return image_to_b64(image=image, image_format='JPEG')


def file_image_bytes(image_path: str) -> str:
    """
    Load an image from path to a Spotify usable image
    :param image_path: path to image
    :return: bytes for spotify
    :raises InputException: if input is invalid
    """
    
    image_path = absolute_path(image_path, is_file=True)
    
    image = image_from_file(image_path)
    return image_to_b64(image=image, image_format='JPEG')


def split_list_into_chunks(lst: list, chunk_length: int = 50) -> list:
    """
    Split a list into chunks of size chunk_length
    :param lst: what list to split
    :param chunk_length: size of each chunk
    :return: chunked list
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    if not isinstance(lst, list):
        raise InputException(item_value=lst, valid_values="valid list", valid_types=list)
    
    if not isinstance(chunk_length, int) or chunk_length <= 0:
        raise InputException(item_value=chunk_length, valid_values="positive integers", valid_types=int)
    
    try:
        return [lst[x:x+chunk_length] for x in range(0, len(lst), chunk_length)]
    
    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while splitting list: '{lst}' into chunks of size '{chunk_length}'")


T = TypeVar('T')
def concat_iterables(iter1: Iterable[T], iter2: Iterable[T]) -> List[T]:
    """
    Concat two iterables into one iterable.
    :param iter1: iterable 1
    :param iter2: iterable 2
    :return: concatenated iterable
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    if not isinstance(iter1, Iterable):
        raise InputException(item_value=iter1, valid_values="valid iterable", valid_types=Iterable)
    
    if not isinstance(iter2, Iterable):
        raise InputException(item_value=iter2, valid_values="valid iterable", valid_types=Iterable)
    
    try:
        return [*iter1, *iter2]
    
    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while concatenating iterables: '{iter1}' and '{iter2}'")


def debug_json(jason: dict):
    """
    Dump a dict into 'code_backend/testing/debugging.json'.
    :param jason: what dict to dump
    :raises InputException: if input is invalid
    """
    json_to_file(
        json_filepath="code_backend/testing/debugging.json",
        json_data=jason,
        overwrite=True
    )


def check_upper_limit(limit: int, api_max_limit: int = 50) -> int:
    """
    Checks if the user limit exceeded the API limit.
    :param limit: current limit
    :param api_max_limit: maximum API limit
    :return: 0: limit okay; 1: API limit subceeded, print error message
    :raises InputException: if input is invalid
    """
    
    if not isinstance(limit, int) or limit < 0:
        raise InputException(item_value=limit, valid_values="positive integers", valid_types=int)
    
    if not isinstance(api_max_limit, int) or MAX_REQUESTS_PER_CALL < api_max_limit < 0:
        raise InputException(item_value=api_max_limit, valid_values="0 < api_max_limit < MAX_REQUESTS_PER_CALL", valid_types=int)
    
    if limit > api_max_limit:
        print(f"{CRED}Limit of {limit} exceeded API limit of {api_max_limit} per request{TEXTCOLOR}")
        return 1

    return 0


def check_lower_limit(limit: int, api_min_limit: int = 1) -> int:
    """
    Checks if the user limit subceeded the API limit.
    :param limit: current limit
    :param api_min_limit: minimum API limit
    :return: 0: limit okay; 1: API limit subceeded, print error message
    :raises InputException: if input is invalid
    """
    if not isinstance(limit, int) or limit < 0:
        raise InputException(item_value=limit, valid_values="positive integers", valid_types=int)

    if not isinstance(api_min_limit, int) or api_min_limit < 0:
        raise InputException(item_value=api_min_limit, valid_values="positive integers", valid_types=int)

    if limit < api_min_limit:
        print(f"{CRED}Limit of {limit} subceeded API limit of {api_min_limit} per request{TEXTCOLOR}")
        return 1

    return 0


def check_limits(limit: int, min_limit: int = 1, max_limit: int = MAX_REQUESTS_PER_CALL) -> int:
    """
    Checks if the limit is in range of the API.
    :param limit: current limit (1 <= limit <= MAX_REQUESTS_PER_CALL)
    :param min_limit: minimum API limit
    :param max_limit: maximum API limit
    :return: 0: limit okay; 1: limit out of API range, print error message; 2: API limit both subceeded and exceeded, print error message
    :raises InputException: if input is invalid
    """

    if not isinstance(limit, int) or limit < 0:
        raise InputException(item_value=limit, valid_values="positive integers", valid_types=int)

    if not isinstance(min_limit, int) or min_limit < 0:
        raise InputException(item_value=min_limit, valid_values="positive integers", valid_types=int)

    if not isinstance(max_limit, int) or MAX_REQUESTS_PER_CALL < max_limit < 0:
        raise InputException(item_value=max_limit, valid_values="0 < max_limit < MAX_REQUESTS_PER_CALL", valid_types=int)

    return check_lower_limit(limit, min_limit) + check_upper_limit(limit, max_limit)


def update_env_key(env_key: str, new_value) -> tuple[str, str]:
    """
    Update the env key with the new value.
    :param env_key: what key to update
    :param new_value: what new value to set
    :return: old value and current value
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    if not isinstance(env_key, str):
        raise InputException(item_value=env_key, valid_values="any string", valid_types=str)
    
    env_file = find_dotenv()
    if not env_file:
        print(f"{CRED}Could not find .env file\n{TEXTCOLOR}")
    load_dotenv(env_file)

    try:
        old_value = os.getenv(env_key)

        os.environ[env_key] = new_value
        set_key(env_file, env_key, os.environ[env_key])
        return old_value, os.environ[env_key]
    
    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while updating .env key '{env_key}' to '{error}'")


def check_token_expired(extended_token: bool = False, print_remaining_time: bool = False) -> int:
    """
    Checks when the Token expires
    :param extended_token: Whether to check the regular Token (=False) or the extended one (=True)
    :param print_remaining_time: Whether to print the time the token remains valid
    :return: Time till Token expires (if 0 is returned, the token did expire)
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    if not isinstance(extended_token, bool):
        raise InputException(item_value=extended_token, valid_values=(True, False), valid_types=bool)
    
    env_file = find_dotenv()
    if env_file == "":
        raise FileNotFoundError(f"Could not find .env file")

    load_dotenv(env_file)
    token_name = "EXTENDED_TOKEN" if extended_token else "REGULAR_TOKEN"

    try:
        token_data = json.loads(os.getenv(token_name))
        expiration_date = token_data["expires"]

        if print_remaining_time:
            t = expiration_date - int(time.time())
            print(f"Token expires in: {t//60} min {t%60} sec")

        return 0 if expiration_date - int(time.time()) < 1 else expiration_date - int(time.time())

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while checking expiration of token '{token_name}'.")


def print_debug(content) -> None:
    """
    Print debug content
    :param content: what to display inside the debug block
    :raises InputException: if input is invalid
    """

    if content is None:
        raise InputException(item_value=content, valid_values="anything, but None", valid_types=str)

    if not isinstance(content, str):
        content = str(content)

    print(f"{CORANGE}\n<----- Begin Debugging ----->\n\n{content}\n\n{CORANGE}<------ End Debugging ------>\n{TEXTCOLOR}")


def exclude_from_dict(target_dict: dict, exclude_keys: list) -> dict:
    """
    Safely exclude keys from a dictionary
    :param target_dict: what dictionary to exclude from
    :param exclude_keys: what keys to pop
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(target_dict, dict):
        raise InputException(item_value=target_dict, valid_values="valid dict", valid_types=dict)

    if not isinstance(exclude_keys, list):
        raise InputException(item_value=exclude_keys, valid_values="valid list", valid_types=list)

    try:
        for key in exclude_keys:
            target_dict.pop(key, None)

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while excluding keys '{exclude_keys}' from dictionary '{target_dict}'.")

    return target_dict


def dict_factory(cursor, row) -> dict:
    """
    by Alex Martelli on Stackoverflow (https://stackoverflow.com/a/3300514)
    :param cursor: Database cursor
    :param row: Database table row
    :return: Dict containing the column names and values {column_name: value}
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    # Todo: Input check
    #   if not isinstance(cursor, ??):
    #       raise InputException(item_value=cursor, valid_values="valid cursor", valid_types=??)
    #   if not isinstance(row, ??):
    #       raise InputException(item_value=row, valid_values=??, valid_types=??)

    d = {}

    try:
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while using dict_factory on cursor '{cursor}' and row '{row}'.")

    return d


def get_str_from_json_file(json_path: str) -> str:
    """
    Load a JSON file and then dump it in a string
    :param json_path: path to JSON file
    :return: JSON file converted to string
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    json_path = absolute_path(json_path, is_file=True)

    try:
        return json.dumps(load_json(json_path))

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while loading JSON file '{json_path}'.")


def load_sql_query(file_path: str) -> str:
    """
    Load a SQL query from a file Using the path from the Repository Root
    :param file_path: relative path to query file
    :return: loaded query
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    file_path = absolute_path(file_path, is_file=True)

    try:
        with open(file_path, "r") as query_file:
            return query_file.read()

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while loading SQL query from file '{file_path}'.")


def absolute_path(path: str, is_file: bool = False) -> str:
    """
    Converts the given path to an absolute path. If the path is absolute nothing happens. If in doubt just call it
    :param path: (relative) path to convert
    :param is_file: (optional) whether the path is a file
    :return: absolute path
    :raises InputException: if input is invalid
    """

    if not isinstance(path, str):
        raise InputException(item_value=path, valid_values="string", valid_types=str)

    if not path.startswith(ROOT_DIR_PATH):
        # remove leading '/' or './'
        path = path[1:] if path.startswith("/") else path[2:] if path.startswith("./") else path
        path = str(os.path.join(ROOT_DIR_PATH, path))

    if not os.path.exists(os.path.split(path)[0]):
        raise InputException(item_value=path, valid_values="valid filepath", valid_types=str)

    if is_file and not os.path.isfile(path):
        raise InputException(item_value=path, valid_values="path to existing file", valid_types=str)
    
    return path


def load_json(path: str) -> dict:
    """
    Load JSON from .json file
    :param path: path to file
    :return: JSON object
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """
    
    path = absolute_path(path, is_file=True)

    try:
        with open(path, 'r') as j_file:
            return json.load(j_file)

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while loading JSON file '{path}'.")


def json_pointer_to_path(json_pointer: str) -> None:
    """"""

    if not isinstance(json_pointer, str):
        raise InputException(item_value=json_pointer, valid_values="any JSON pointer", valid_types=str)

    print(f"[{"][".join(json_pointer.split("/")[1:])}]")


def resolve_json_pointer(json_data: dict, json_pointer: str) -> Any:
    """

    :param json_data:
    :param json_pointer:
    :return:
    """
    if not isinstance(json_data, dict):
        raise InputException(item_value=json_pointer, valid_values="any dict", valid_types=dict)

    if not isinstance(json_pointer, str):
        raise InputException(item_value=json_pointer, valid_values="any JSON pointer", valid_types=str)

    keys = json_pointer.split("/")[1:]
    relevant_data = json_data
    for key in keys:
        relevant_data = relevant_data.get(key)

    return relevant_data


def load_list_from_database(fetched_list: list) -> list:
    """
    Convert a list string into a list (e.g. ["['6O7MpKrY91vlCd4Osi6XKs']", "['2iLpvtffIrQ4bMYrFPRN4x']"] -> [['6O7MpKrY91vlCd4Osi6XKs'], ['2iLpvtffIrQ4bMYrFPRN4x']])
    :param fetched_list: list of list-strings
    :return: list containing flattened data
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(fetched_list, list):
        raise InputException(item_value=fetched_list, valid_values="any list", valid_types=list)

    try:
        loaded_list = [ast.literal_eval(row) for row in fetched_list]
        return flatten(loaded_list)

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while converting the list string '{fetched_list}' into a list.")


def flatten(lst: list) -> list:
    """
    Recursively flatten a list
    :param lst: multidimensional list
    :return: one-dimensional list
    :raises InputException: if input is invalid
    :raises CustomException: If Exception occurs
    """

    if not isinstance(lst, list):
        raise InputException(item_value=lst, valid_values="valid list", valid_types=list)

    result = []

    try:
        for item in lst:
            if isinstance(item, list):
                result.extend(flatten(item))
            else:
                result.append(item)
        return result

    except Exception as error:
        raise CustomException(error_message=error, more_infos=f"Exception occurred while flattening list '{lst}'.")


def remove_key_recursively(d, key_to_remove: str):
    """

    :param d:
    :param key_to_remove:
    :return:
    :raises InputException: if input is invalid
    """
    if not isinstance(key_to_remove, str):
        raise InputException(item_value=key_to_remove, valid_values="valid dict key", valid_types=str)

    if isinstance(d, dict):  # If it's a dictionary, iterate through its keys
        return {
            k: remove_key_recursively(v, key_to_remove)
            for k, v in d.items() if k != key_to_remove
        }
    elif isinstance(d, list):  # If it's a list, iterate through its elements
        return [remove_key_recursively(item, key_to_remove) for item in d]
    else:  # Base case: return value as is
        return d


def check_base62(check_str: str) -> bool:
    """
    Check if a string is a base62 encoded string
    :param check_str: string to be checked
    :return: True: string is base62 encoded; False: otherwise
    :raises InputException: if input is invalid
    """

    if not isinstance(check_str, str):
        raise InputException(item_value=check_str, valid_values="string", valid_types=str)

    base62_alph = string.digits + string.ascii_letters
    return set(check_str).issubset(base62_alph)


def check_spotify_id(spotify_id: str, is_device: bool = False, is_user: bool = False) -> bool:
    """
    Check if a spotify ID is valid
    Official Documentation: https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids
    :param spotify_id: spotify ID to be checked
    :param is_device: if the spotify ID is from a device
    :param is_user: if the spotify ID is from a user
    :return: True: id format is valid; False: otherwise
    :raises InputException: if input is invalid
    """

    if not isinstance(spotify_id, str):
        raise InputException(item_value=spotify_id, valid_values="string", valid_types=str)

    if not isinstance(is_device, bool):
        raise InputException(item_value=is_device, valid_values=(True, False), valid_types=bool)

    if not isinstance(is_user, bool):
        raise InputException(item_value=is_user, valid_values=(True, False), valid_types=bool)


    correct_encode = check_base62(spotify_id)

    if is_device:
        correct_length = (len(spotify_id) == 40)
    elif is_user:
        return True
    else:
        correct_length = (len(spotify_id) == 22)

    return correct_encode and correct_length


def check_spotify_uri(spotify_uri: str) -> bool:
    """
    Check if a spotify URI is valid
    Official Documentation: https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids
    :param spotify_uri: spotify URI to be checked
    :return: True: uri format is valid; False: otherwise
    :raises InputException: if the spotify URI is invalid
    :raises InputException: if input is invalid
    """

    if not isinstance(spotify_uri, str) or len(spotify_uri.split(":")) != 3:
        raise InputException(item_value=spotify_uri, valid_values="strings in the from of \'spotify:${type}:${id}\'", valid_types=str)

    spotify_, spotify_type, spotify_id = spotify_uri.split(":")
    correct_format = (spotify_ == "spotify") and (spotify_type in ("album", "artist", "playlist", "track", "user"))

    if spotify_type == "user":
        correct_id = check_spotify_id(spotify_id, is_user=True)
    else:
        correct_id = check_spotify_id(spotify_id)

    return correct_format and correct_id


def check_spotify_ids(spotify_ids: list) -> bool:
    """
    Check if a list contains valid spotify IDs (not working for user)
    :param spotify_ids: list containing spotify IDs to be checked
    :return: True: spotify ID formats are valid; False: otherwise
    :raises InputException: if the spotify IDs are invalid
    :raises InputException: if input is invalid
    """

    if not isinstance(spotify_ids, list) or len(spotify_ids) < 1:
        raise InputException(item_value=spotify_ids, valid_values="list containing strings", valid_types=list)

    return all(check_spotify_id(i) for i in spotify_ids)


def check_spotify_user_ids(spotify_ids: list) -> bool:
    """
    Check if a list contains valid spotify user IDs
    :param spotify_ids: list containing spotify user IDs to be checked
    :return: True: spotify user ID formats are valid; False: otherwise
    """

    if not isinstance(spotify_ids, list) or len(spotify_ids) < 1:
        raise InputException(item_value=spotify_ids, valid_values="list containing strings", valid_types=list)

    # Note: always returns True
    return all(check_spotify_id(i, is_user=True) for i in spotify_ids)


def check_spotify_device_ids(spotify_ids: list) -> bool:
    """
    Check if a list contains valid spotify device IDs
    :param spotify_ids: list containing spotify device IDs to be checked
    :return: True: spotify device ID formats are valid; False: otherwise
    :raises InputException: if input is invalid
    """

    if not isinstance(spotify_ids, list) or len(spotify_ids) < 1:
        raise InputException(item_value=spotify_ids, valid_values="list containing strings", valid_types=list)

    return all(check_spotify_id(i, is_device=True) for i in spotify_ids)


def check_spotify_uris(spotify_uris: list) -> bool:
    """
    Check if a list contains valid spotify URIs
    :param spotify_uris: list containing spotify URIs to be checked
    :return: True: spotify URI formats are valid; False: otherwise
    :raises InputException: if input is invalid
    """

    if not isinstance(spotify_uris, list) or len(spotify_uris) < 1:
        raise InputException(item_value=spotify_uris, valid_values="list containing strings", valid_types=list)

    return all(check_spotify_uri(i) for i in spotify_uris)


def get_invalid_spotify_ids(spotify_ids: list) -> list:
    """
    Get invalid spotify IDs (not working for user)
    :param spotify_ids: list containing spotify IDs to be checked
    :return: invalid spotify IDs
    :raises InputException: if input is invalid
    """
    if not isinstance(spotify_ids, list) or len(spotify_ids) < 1:
        raise InputException(item_value=spotify_ids, valid_values="list containing strings", valid_types=list)

    return [i for i in spotify_ids if not check_spotify_id(i)]


def get_invalid_spotify_uris(spotify_uris: list) -> list:
    """
    Get invalid spotify URIs
    :param spotify_uris: list containing spotify URIs to be checked
    :return: invalid spotify URIs
    :raises InputException: if input is invalid
    """

    if not isinstance(spotify_uris, list) or len(spotify_uris) < 1:
        raise InputException(item_value=spotify_uris, valid_values="list containing strings", valid_types=list)

    return [i for i in spotify_uris if not check_spotify_uri(i)]


if __name__ == '__main__':
    """"""
from code_backend.shared_config import *


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
    list(dictionary.values())


def keys_from_dict(dictionary: dict) -> list:
    list(dictionary.keys())


def list_from_dict(dictionary: dict) -> list:
    list(dictionary.items())


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
    new_image_width = int(0.05 * GUI_SIZE[0])
    new_image_height = int(0.07 * GUI_SIZE[1])
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


def split_list_into_chunks(lst: list, chunk_length: int = 50) -> list:
    return [lst[x:x+chunk_length] for x in range(0, len(lst), chunk_length)]


T = TypeVar('T')
def concat_iterables(iter1: Iterable[T], iter2: Iterable[T]) -> List[T]:
    return [*iter1, *iter2]


def debug_json(jason: dict):
    with open(ROOT_DIR_PATH + "/code_backend/testing/debugging.json", "w") as json_file:
        json.dump(jason, json_file, indent=4)


def check_upper_limit(limit: int, api_max_limit: int = 50) -> None:
    """
    Checks if the user limit exceeded the API limit.
    :param limit: current limit
    :param api_max_limit: maximum API limit
    :return: raise Exception if API limit exceeded
    """
    if limit > api_max_limit:
        raise Exception(f"Limit of {limit} exceeded API limit of {api_max_limit} per request")


def check_lower_limit(limit: int, api_min_limit: int = 1) -> None:
    """
    Checks if the user limit subceeded the API limit.
    :param limit: current limit
    :param api_min_limit: minimum API limit
    :return: raise Exception if API limit subceeded
    """
    if limit < api_min_limit:
        raise Exception(f"Limit of {limit} subceeded API limit of {api_min_limit} per request")


def update_env_key(env_key: str, new_value) -> tuple[str, str]:
    env_file = find_dotenv()
    if not env_file:
        print(
            f"\n\x1b[31mCould not find .env file\n{TEXTCOLOR}")
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
        print(
            f"\n\x1b[31mCould not find .env file\n{TEXTCOLOR}")
    load_dotenv(env_file)

    token_name = "EXTENDED_TOKEN" if extended_token else "REGULAR_TOKEN"
    token_data = json.loads(os.getenv(token_name))

    expiration_date = token_data["expires"]
    return 0 if expiration_date - int(time.time()) < 1 else expiration_date - int(time.time())


def print_error(error_message: str | Exception, more_infos: str = None, exit_code: int = None) -> None:
    print(f"\n\x1b[31m{error_message}\n{TEXTCOLOR}{more_infos}\n")
    if exit_code:
        sys.exit(exit_code)


def print_http_error_codes(code: int, message: str = None) -> None:
    """
    Web API uses the following response status codes, as defined in the RFC 2616 and RFC 6585
    Official API Documentation: https://developer.spotify.com/documentation/web-api/concepts/api-calls#response-status-codes
    :param code: HTTP Code of the request response
    :param message: Message of the error
    """
    error_data: dict
    with open(ROOT_DIR_PATH + "/Databases/JSON_Files/http_errors.json", "r") as e_file:
        error_data = json.load(e_file)[str(code)]
    # print(error_data["code"],"-",error_data["name"])
    print_error(
        error_message=f"Request returned Code: {error_data["code"]} - {error_data["name"]}\n{error_data["explanation"]}",
        more_infos=message,
        exit_code=1
    )


if __name__ == '__main__':
    """"""
"""
Project specific exceptions

Exception Definition for Docstrings:
:raises CustomException: If Exception occurs
:raises DatabaseException: If Exception related to the Database occurs
:raises HttpException: if request response code is not good
:raises InputException: if input is invalid
:raises LimitException: if limit is invalid
:raises RequestException: if Exception occurs while using requests
:raises SpotifyApiException: if Exception related to Spotify API occurs
:raises SpotifyIdException: if spotify id is invalid
:raises SpotifyUriException: if spotify uri is invalid

"""

from code_backend.shared_config import *

# avoid circular import error with secondary_methods.py
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


# avoid circular import error with secondary_methods.py
def load_json(path: str) -> dict:
    """
    Load JSON from .json file

    :param path: path to file
    :return: JSON object
    """
    path = absolute_path(path)
    with open(path, 'r') as j_file:
        return json.load(j_file)


class SpotifyApiException(Exception):
    """Base exception for errors related to Spotify API requests."""
    def __init__(self, message: str) -> None:
        super().__init__(message)


class HttpException(SpotifyApiException):
    """
    Exception raised for HTTP errors when interacting with the Spotify Web API.

    Web API uses the following response status codes, as defined in the RFC 2616 and RFC 6585

    **Official API Documentation:** https://developer.spotify.com/documentation/web-api/concepts/api-calls#response-status-codes
    """
    def __init__(self, error_code, request_query: requests.Request, response_text: str):
        """
        :param error_code: The HTTP status code returned by the server.
        :param request_query: The original HTTP request that triggered the error.
        :param response_text: The response body received from the server.
        """
        with open(absolute_path(SPOTIFY_HTTP_ERRORS_PATH), 'r') as j_file:
            spotify_http_errors = json.load(j_file)

        assert str(error_code) in spotify_http_errors.keys(), f"Invalid HTTP error code encountered '{error_code}'"

        http_error_details = spotify_http_errors[str(error_code)]

        self.error_code = error_code
        self.error_name = http_error_details["name"]
        self.error_description = http_error_details["explanation"]
        self.request_query = request_query.prepare()
        self.response_text = response_text

        super().__init__(self.__str__())

    def __str__(self):
        return (
            "\n<===== Begin Error =====>\n\n"
            f"Request returned Code: {self.error_code} - {self.error_name}\n"
            f"{self.error_description}\n"
            "Responsible Query:\n"
            f"{CORANGE}-----------START-----------\n"
            f"{self.request_query.method} {self.request_query.url}\n"
            + "\n".join(f"{key}: {value}" for key, value in self.request_query.headers.items()) + "\n"
            "Request Body:\n"
            f"{self.request_query.body if self.request_query.body else '\'---\''}\n"
            f"------------END------------{TEXTCOLOR}\n"
            f"More infos: {self.response_text}\n"
            f"\n{CORANGE}<===== End Error =====>{TEXTCOLOR}\n"
        )


class RequestException(Exception):
    """
    Exception raised while using requests
    """

    def __init__(self, error: Exception, request_query: requests.Request) -> None:
        self.error = error
        self.request_query = request_query.prepare()
        super().__init__(self.__str__())
        print(f"\n{CORANGE}<===== End Error =====>{TEXTCOLOR}\n")

    def __str__(self):
        return (
            "\n<===== Begin Error =====>\n\n"
            f"{CCYAN}Request returned:{CORANGE} {self.error.args}\n"
            f"{CCYAN}Responsible Query:\n"
            f"{CORANGE}-----------START-----------\n"
            f"{self.request_query.method} {self.request_query.url}\n"
            + "\n".join(f"{key}: {value}" for key, value in self.request_query.headers.items()) + "\n"
            f"Request Body:\n"
            f"{self.request_query.body if self.request_query.body else '---'}\n"
            f"------------END------------{TEXTCOLOR}\n\n"
            f"{CCYAN}Traceback: {CRED}\n{traceback.format_exc()}{TEXTCOLOR}"
        )


class CustomException(Exception):
    """Wrapper for exceptions"""
    def __init__(self, error_message: str | Exception, more_infos: str = None) -> None:
        """
        :param error_message: either an Exception or a custom error message
        :param more_infos: more infos e.g. what could have lead to the error
        :return: print detailed error message
        """
        self.error_message = error_message
        self.more_infos = more_infos
        super().__init__(self.__str__())
        print(f"\n{CORANGE}<===== End Error =====>{TEXTCOLOR}\n")

    def __str__(self) -> str:
        print(f"\n{CORANGE}<===== Begin Error =====>{CRED}\n")
        print("Error message:", str(self.error_message))
        if self.more_infos:
            print("More infos:", self.more_infos)
        if isinstance(self.error_message, Exception):
            print("Error type:", self.error_message.__class__.__name__)
            print("Arguments:", self.error_message.args)


class DatabaseException(CustomException):
    """Base exception for errors related to the Database."""
    def __init__(self, error_message: str | Exception, more_infos: str = None) -> None:
        super().__init__(error_message, more_infos)


class InputException(Exception):
    """
    Exception raised when the input is invalid
    """
    def __init__(self, item_value: Any, valid_values: tuple | str, valid_types: Any | tuple):
        self.item_value = item_value
        self.valid_values = f"'{'\', \''.join([str(i) for i in valid_values])}'" if isinstance(valid_values, tuple) else f"'{valid_values}'"
        self.item_type = type(item_value).__name__
        if isinstance(valid_types, tuple):
            self.valid_types = f"'{'\', \''.join([i.__name__ if i is not None else "None" for i in valid_types])}'"
        else:
            self.valid_types = f"'{valid_types.__name__}'"

        super().__init__(self.__str__())

    def __str__(self):
        return (
            f"Invalid Input detected{TEXTCOLOR}\n"
            f"\n{CORANGE}<===== Begin Error Description =====>{TEXTCOLOR}\n\n"
            f"{CORANGE}Received Value:{TEXTCOLOR} {self.item_value}\n"
            f"{CORANGE}Valid Values:{TEXTCOLOR} {self.valid_values}\n\n"
            f"{CORANGE}Received Type:{TEXTCOLOR} {self.item_type}\n"
            f"{CORANGE}Valid Types:{TEXTCOLOR} {self.valid_types}\n"
            f"\n{CORANGE}<===== End Error Description =====>{TEXTCOLOR}\n"
        )


class SpotifyIdException(Exception):
    """
    Exception raised when invalid Spotify ID passed
    """
    def __init__(self, invalid_id: str, id_type: Literal["album", "artist", "device", "playlist", "track", "user"]) -> None:
        """
        :param invalid_id: invalid Spotify ID
        :param id_type: type of Spotify ID
        """
        self.invalid_id = invalid_id
        self.id_type = id_type
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return (
            f"Invalid Spotify ID detected{TEXTCOLOR}\n"
            f"\n{CORANGE}<===== Begin Error Description =====>{TEXTCOLOR}\n\n"
            f"{CORANGE}Invalid ID:{TEXTCOLOR} '{self.invalid_id}'\n"
            f"{CORANGE}ID type:{TEXTCOLOR} {self.id_type}\n"
            f"\n{CORANGE}<====== End Error Description ======>{TEXTCOLOR}\n"
        )


class SpotifyUriException(Exception):
    """
    Exception raised when invalid Spotify URI passed
    """
    def __init__(self, invalid_uri: str, uri_type: Literal["album", "artist", "playlist", "track", "user"] = None) -> None:
        """
        :param invalid_uri: invalid Spotify URI
        :param uri_type: type of Spotify URI
        """
        self.invalid_uri = invalid_uri
        self.uri_type = uri_type if uri_type else "unknown"
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return (
            f"Invalid Spotify URI detected{TEXTCOLOR}\n"
            f"\n{CORANGE}<===== Begin Error Description =====>{TEXTCOLOR}\n\n"
            f"{CORANGE}Invalid URI:{TEXTCOLOR} '{self.invalid_uri}'\n"
            f"{CORANGE}URI type:{TEXTCOLOR} {self.uri_type}\n"
            f"\n{CORANGE}<====== End Error Description ======>{TEXTCOLOR}\n"
        )


class LimitException(Exception):
    """
    Exception raised when invalid limit passed
    """

    def __init__(self, invalid_limit: int, valid_range: tuple = (1, MAX_REQUESTS_PER_CALL)) -> None:
        """
        :param invalid_limit: invalid limit
        :param valid_range: valid range
        """
        self.invalid_limit = invalid_limit
        self.valid_range = valid_range
        super().__init__(self.__str__())

    def __str__(self) -> str:
        return (
            f"Invalid Limit detected{TEXTCOLOR}\n"
            f"\n{CORANGE}<===== Begin Error Description =====>{TEXTCOLOR}\n\n"
            f"{CORANGE}Invalid limit:{TEXTCOLOR} '{self.invalid_limit}'\n"
            f"{CORANGE}valid range:{TEXTCOLOR} {self.valid_range}\n"
            f"\n{CORANGE}<====== End Error Description ======>{TEXTCOLOR}\n"
        )

class EnvFileException(Exception):
    def __init__(self, file_path: str, key_name: str, expected_value: Any = None, passed_value: Any = None) -> None:
        self.file_path: str = file_path
        self.key_name: str = key_name

        self.expected_value: Any = expected_value
        self.passed_value: Any = passed_value

        self.expected_type: Any = type(expected_value).__name__
        self.passed_type: Any = type(passed_value).__name__

        super().__init__(self.__str__())

    def __str__(self):
        return (
            f"Invalid ENV value detected{TEXTCOLOR}\n"
            f"\n{CORANGE}<===== Begin Error Description =====>{TEXTCOLOR}\n\n"
            
            f"{CORANGE}Responsible ENV file:{TEXTCOLOR} {self.file_path}\n"
            f"{CORANGE}Responsible Key:{TEXTCOLOR} {self.key_name}\n\n"
            
            f"{CORANGE}Received Values:{TEXTCOLOR} {self.passed_value}\n"
            f"{CORANGE}Expected Values:{TEXTCOLOR} {self.expected_value}\n\n"
            
            f"{CORANGE}Received Type:{TEXTCOLOR} {self.passed_type}\n"
            f"{CORANGE}Expected Type:{TEXTCOLOR} {self.expected_type}\n"
            
            f"\n{CORANGE}<===== End Error Description =====>{TEXTCOLOR}\n"
        )

if __name__ == "__main__":
    """"""
    # import code_backend.spotify_web_api as spotify
    # try:
    #     spotify.pause_playback()
    # except Exception as e:
    #     raise CustomException(e,"test")
    raise EnvFileException(
        file_path="./env",
        key_name="test",
        expected_value="{}",
        passed_value=None,
    )
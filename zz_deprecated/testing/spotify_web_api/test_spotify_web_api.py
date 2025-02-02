import json

from code_backend.spotify_web_api import *
import ast
from code_backend.shared_config import root_dir_path

def create_testing_values(test_file_path, output_file_path):
    with open(test_file_path, "r") as file:
        tree = ast.parse(file.read())

    methods = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            method_name = node.name
            args = [arg.arg for arg in node.args.args]
            methods[method_name] = args

    with open(output_file_path, "w") as file:
        output = {}
        for method_name, args in methods.items():
            output[method_name] = {"input": {arg: "" for arg in args}, "expected_output": {}, "actual_output": {}}

        json.dump(output, file, indent=4)

    return methods


def set_testing_values(test_file_path: str, values: dict) -> None:
    with open(test_file_path, "r") as json_file:
        file_data = json.load(json_file)

    for method_name, primary_value in file_data.items():
        primary_value["input"].update({k: v for k, v in values.items() if k in primary_value["input"]})

    with open(test_file_path, "w") as json_file:
        json.dump(file_data, json_file, indent=4)


def create_unit_tests(reference_file: str, testing_file: str):
    with open(reference_file, "r") as file:
        reference = json.load(file)

    with open(testing_file, "w") as file:
        file.write("import unittest\n")
        file.write("from code_backend.spotify_web_api import *\n\n\n")
        file.write("class TestMethods(unittest.TestCase):\n\n")

        for method_name, method_data in reference.items():
            input_data = method_data.get("input", {})
            expected_output = method_data.get("expected_output", {})

            file.write(f"\tdef test_{method_name}(self):\n")
            file.write(f"\t\t\"\"\"\n\tTest case for {method_name}\n\t\"\"\"\n\n")
            file.write(f"\t\texpected_output = {expected_output}\n")
            file.write(f"\t\tactual_output = {method_name}(\n")
            for arg, val in method_data["input"].items():
                file.write(f"\t\t\t{arg}={json.dumps(val).replace('null', 'None').replace("false", "False").replace("true","True")},\n")
            file.write(f"\t\t)\n\n")
            file.write("\t\tself.assertEqual(expected_output, actual_output)\n\n")

    print(f"Unittest file '{testing_file}' generated successfully.")


if __name__ == "__main__":
    file_path = root_dir_path + "/code_backend/spotify_web_api.py"
    out_file_path = root_dir_path + "/code_backend/testing/spotify_web_api/test_spotify_web_api.json"
    testing_file_path = root_dir_path + "/code_backend/testing/testing.py"

    # regular_api_methods = create_testing_values(file_path, out_file_path)
    #
    # set_testing_values(
    #     test_file_path=out_file_path,
    #     values={
    #         "artist_id": "79fnwKynD56xIXBVWkyaE5",
    #         "album_uri": "spotify:album:79fnwKynD56xIXBVWkyaE5",
    #         "album_ids": ["79fnwKynD56xIXBVWkyaE5", "7CI6R1kJLUMfBl4FOKP8nc"],
    #         "artist_id": "6XyY86QOPPrYVGvF9ch6wz",
    #         "artist_ids": ["6XyY86QOPPrYVGvF9ch6wz", "00YTqRClk82aMchQQpYMd5"],
    #         "playlist_id": "6bRkO7PLCXgmV4EJH52iU4",
    #         "playlist_uri": "spotify:playlist:6bRkO7PLCXgmV4EJH52iU4",
    #         "track_id": "14FP9BNWHekbC17tqcppOR",
    #         "track_uri": "spotify:track:14FP9BNWHekbC17tqcppOR",
    #         "track_uris": ["spotify:track:6zrR8itT7IfAdl5aS7YQyt", "spotify:track:14FP9BNWHekbC17tqcppOR"],
    #         "track_ids": ["6zrR8itT7IfAdl5aS7YQyt", "14FP9BNWHekbC17tqcppOR"],
    #         "user_id": "simonluca1",
    #         "limit": 2,
    #         "offset": 0
    #     }
    # )

    create_unit_tests(
        reference_file=out_file_path,
        testing_file=testing_file_path
    )
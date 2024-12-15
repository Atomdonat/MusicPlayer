from code_backend.spotify_web_api import *
import ast
from code_backend.secondary_methods import url_to_uri

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
#
# with open("../../spotify_web_api.py", "r") as file:
#     for line in file:
#         if line[:3] == "def":
#             method_name = line.split(" ")[1].split("(")[0]
#             method_args = methods[method_name]["args"]
#             remove_return = line[4:].split(" ->")[0] + " -> bool:"
#             if len(method_args) > 0:
#                 print(f"def test_{remove_return}\n\t\"\"\"\"\"\"\n\toutput = {method_name}(")
#                 for i in method_args:
#                     print(f"\t\t{i}=,")
#                 print("\t)\n\n")
#             else:
#                 print(f"def test_{remove_return}\n\t\"\"\"\"\"\"\n\toutput = {method_name}()\n\n")
#             print("\nreturn output")


if __name__ == "__main__":
    file_path = "/home/simon/git_repos/MusicPlayer/code_backend/spotify_web_api.py"
    out_file_path = "/home/simon/git_repos/MusicPlayer/code_backend/testing/spotify_web_api/test_spotify_web_api.json"
    create_testing_values(file_path, out_file_path)

    playlist_id =  url_to_uri(spotify_url="https://open.spotify.com/playlist/6bRkO7PLCXgmV4EJH52iU4?si=4eb79d4616ef4215", to_id=True)
    playlist_uri = url_to_uri(spotify_url="https://open.spotify.com/playlist/6bRkO7PLCXgmV4EJH52iU4?si=4eb79d4616ef4215")

    album_id =  url_to_uri(spotify_url="", to_id=True)
    album_uri = url_to_uri(spotify_url="")

    track_id =  url_to_uri(spotify_url="", to_id=True)
    track_uri = url_to_uri(spotify_url="")

    user_id =  url_to_uri(spotify_url="https://open.spotify.com/user/simonluca1?si=a4972ce147f244fc", to_id=True)
    user_uri = url_to_uri(spotify_url="https://open.spotify.com/user/simonluca1?si=a4972ce147f244fc")
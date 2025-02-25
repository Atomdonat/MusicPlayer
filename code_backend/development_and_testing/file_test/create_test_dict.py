from code_backend.shared_config import *

PC_DEVICE_ID = "a59d3a684d22772199a2fe97cdcdf563eaee9ac1"
HANDY_DEVICE_ID = "6f627a3903683807eb6a9edce9094c66a03d1ebc"
TEST_PLAYBACK_STATE = True
TEST_POSITION = 60000
TEST_REPEAT_MODE = "context"
TEST_VOLUME = 50
TEST_LIMIT = 2
TEST_AFTER = 1484811043508
TEST_BEFORE = 1484811043508
TEST_TRACK_URI = "spotify:track:14FP9BNWHekbC17tqcppOR"
TEST_TRACK_URIS = ["spotify:track:6zrR8itT7IfAdl5aS7YQyt", "spotify:track:14FP9BNWHekbC17tqcppOR"]


def extract_methods(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read())

    methods_dict = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):  # Check for function definitions
            method_name = node.name
            kwargs = {}

            for arg in node.args.args:  # Positional arguments
                kwargs[arg.arg] = ""

            for arg in node.args.kwonlyargs:  # Keyword-only arguments
                kwargs[arg.arg] = ""

            methods_dict[method_name] = {"kwargs": kwargs}

    return methods_dict

def generate_tests(regular_api_methods):
    for method, args in regular_api_methods.items():
        arg_string = ', '.join([f"{key}=\"{value}\"" if type(value) is str else f"{key}={value}" for key, value in args["kwargs"].items()])
        print(f"""
def test_{method}():
    test_framework(method={method}, method_name="{method}", {arg_string})
""")

def generate_test_calls(regular_api_methods):
    print("\ttest_methods = [")
    for method in regular_api_methods.keys():
        print(f"\t\ttest_{method},")
    print("\t]")
    print("""
    for current_method in test_methods:
    \tcurrent_method()
    """)

if __name__ == "__main__":
    from code_backend.secondary_methods import absolute_path, json_to_file
    file_path = absolute_path("code_backend/spotify_web_api.py")
    functions_dict = extract_methods(file_path)
    json_to_file(functions_dict, "code_backend/testing/debugging.json")
    print(f"functions_dict = {json.dumps(functions_dict, indent=4)}")
    # generate_tests(regular_api_methods)


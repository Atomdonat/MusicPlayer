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

regular_api_methods = {
    "get_playback_state": {
        "kwargs": {}
    },
    "transfer_playback": {
        "kwargs": {
            "new_device_id": HANDY_DEVICE_ID,
            "playback_state": TEST_PLAYBACK_STATE
        }
    },
    "get_available_devices": {
        "kwargs": {}
    },
    "get_currently_playing_track": {
        "kwargs": {}
    },
    "start_or_resume_playback": {
        "kwargs": {
            "target_device_id": PC_DEVICE_ID
        }
    },
    "pause_playback": {
        "kwargs": {}
    },
    "skip_to_next": {
        "kwargs": {
            "target_device_id": PC_DEVICE_ID
        }
    },
    "skip_to_previous": {
        "kwargs": {
            "target_device_id": PC_DEVICE_ID
        }
    },
    "seek_to_position": {
        "kwargs": {
            "position_ms": TEST_POSITION,
            "target_device_id": PC_DEVICE_ID
        }
    },
    "set_repeat_mode": {
        "kwargs": {
            "new_repeat_mode": TEST_REPEAT_MODE,
            "target_device_id": PC_DEVICE_ID
        }
    },
    "set_playback_volume": {
        "kwargs": {
            "new_volume": TEST_VOLUME,
            "target_device_id": PC_DEVICE_ID
        }
    },
    "toggle_playback_shuffle": {
        "kwargs": {
            "new_state": False,
            "target_device_id": PC_DEVICE_ID
        }
    },
    "get_recently_played_tracks": {
        "kwargs": {
            "limit": TEST_LIMIT,
            "after": TEST_AFTER,
            "before": TEST_BEFORE
        }
    },
    "get_the_users_queue": {
        "kwargs": {}
    },
    "add_item_to_playback_queue": {
        "kwargs": {
            "track_uri": TEST_TRACK_URI,
            "target_device_id": PC_DEVICE_ID
        }
    },
    "add_several_items_to_playback_queue": {
        "kwargs": {
            "track_uris": TEST_TRACK_URIS,
            "target_device_id": PC_DEVICE_ID
        }
    }
}

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
    file_path = r"E:\Programmieren\Github_Repositories\MusicPlayer\code_backend\testing\dev_bench_1.py"  # Change this to the target Python file
    # functions_dict = extract_methods(file_path)
    # generate_tests(regular_api_methods)
    generate_test_calls(regular_api_methods)
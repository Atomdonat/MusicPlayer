from xml.etree.ElementTree import indent

from code_backend.shared_config import *
from code_backend.secondary_methods import absolute_path, json_to_file, load_json
import ast
from typing import Dict, Any
import inspect


def parse_python_file(file_path: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Extract methods and attributes from a python file to generate a test file.
    :param file_path: python file path
    :return:
    """

    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    functions_data = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            attr_type = {}
            attr_value = {}

            for arg in node.args.args:
                arg_name = arg.arg
                if arg.annotation:
                    attr_type[arg_name] = ast.unparse(arg.annotation)
                else:
                    attr_type[arg_name] = None
                    attr_value[arg_name] = arg_name.upper()

            for default, arg in zip(node.args.defaults, node.args.args[-len(node.args.defaults):]):
                attr_value[arg.arg] = arg.arg.upper()

            functions_data[func_name] = {
                "attr_type": attr_type,
                "attr_value": attr_value
            }

    for attributes in functions_data.values():
        for current_attribute in attributes["attr_type"]:
            attributes["attr_value"][current_attribute] = current_attribute.upper()

    return functions_data


def generate_test_file(methods: dict, file_path: str):
    file_path = absolute_path(file_path)
    attributes = {}
    with open(file_path, "w") as file:
        sys.stdout = file
        print("""\
import pytest
from code_backend.spotify_web_api import *


@pytest.fixture(scope="session", autouse=True)
def ensure_valid_token():
\tif check_token_expired(extended_token=False) == 0:
\t\trequest_regular_token()

\tif check_token_expired(extended_token=True) == 0:
\t\trequest_extended_token()\n
""")
        for func_name, func in methods.items():
            print("# @pytest.mark.skip(reason='passed')")
            print(f"def test_{func_name}():\n\t# Positive Test Case")
            if not func.get("attr_value") == {}:
                print("\tpositive_params = {")
                for key, value in func["attr_type"].items():
                    attributes.update({f"POS_{func["attr_value"][key]}": value})
                    print(f"\t\t\"{key}\": POS_{func["attr_value"][key]},  # {value}")
                print(f"\t}}\n\n\t{func_name}(**positive_params)")

                print(f"\n\t# Negative Test Cases\n\tnegative_params = {{")
                for key, value in func["attr_type"].items():
                    attributes.update({f"NEG_{func["attr_value"][key]}": value})
                    print(f"\t\t\"{key}\": NEG_{func["attr_value"][key]},  # {value}")
                print("\t}")
                print("\n\t# test for each negative value individually\n\tfor neg_key, neg_value in negative_params.items():")
                print("\t\tcurrent_params = positive_params")
                print("\t\tcurrent_params.update({neg_key: neg_value})")
                print("\n\t\twith pytest.raises(_Exception):")
                print(f"\t\t\t{func_name}(**current_params)")
            else:
                print(f"\t{func_name}()")

            print("\n")

        print("# Values for Testing")
        sorted_attributes = dict(sorted(attributes.items()))
        for key, value in sorted_attributes.items():
            print(f"{key}: {value} = ")


if __name__ == "__main__":
    file_path = absolute_path("code_backend/spotify_web_api.py")
    parsed_data = parse_python_file(file_path)
    print(json.dumps(parsed_data, indent=4))
    # json_to_file(json_filepath="code_backend/testing/debugging.json", json_data=parsed_data, overwrite=True)
    # generate_test_file(load_json("code_backend/testing/debugging.json"), "code_backend/testing/file_test/test_spotify_web_api.py")
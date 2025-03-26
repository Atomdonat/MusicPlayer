import git
import re
import sys
import subprocess
import os
from datetime import datetime


def replace_in_file(file_path: str, pattern: str, replacement: str) -> None:
    """
    replace string in file

    :param file_path: file path
    :param pattern: pattern to replace
    :param replacement: replacement string
    :raises FileNotFoundError: if file doesn't exist
    :raises PermissionError: if file is not readable or writable
    :raises IsADirectoryError: if file path leads to a directory
    :raises OSError: if file cannot be written to
    """

    with open(file_path, "r") as f:
        old_file = f.read()

    new_file = re.sub(pattern, replacement, old_file)
    with open(file_path, "w") as f:
        f.write(new_file)


def new_version(is_major: bool = False, is_minor: bool = False, is_patch: bool = True) -> str:
    """
    Get the new version number

    :param is_major: commit is major update (+1.0.0)
    :param is_minor: commit is minor update (+0.1.0)
    :param is_patch: commit is a patch (+0.0.1)
    :return: new version number as string
    """

    with open("CHANGELOG.md", "r") as f:
        data = f.read()
        data = re.search(r"\[(\d+\.\d+\.\d+)]", data).group(1)

    major, minor, patch = tuple(int(i) for i in data.split("."))

    if is_major:
        return f"{major+1}.0.0"
    elif is_minor:
        return f"{major}.{minor+1}.0"
    else:
        return f"{major}.{minor}.{patch+1}"


def update_files():
    """update required files"""

    back_changes="\n### Changes in Backend Code\n\n"
    front_changes="### Changes in Frontend Code\n\n"
    other_changes="### Changes in Other files\n\n"

    repo = git.Repo('.', search_parent_directories=True)
    diffs = repo.index.diff(None)
    for current_file in diffs:
        current_file_path = current_file.a_path
        if any(ignore_dir in current_file_path for ignore_dir in ["docs/", "zz_deprecated/"]):
            continue

        if "code_backend/" in current_file_path:
            back_changes += f"#### {current_file_path.split("/")[-1]}\n- \n\n"
        elif "code_frontend/" in current_file_path:
            front_changes += f"#### {current_file_path.split("/")[-1]}\n- \n\n"
        else:
            other_changes += f"#### {current_file_path.split("/")[-1]}\n- \n\n"

    now = datetime.now()
    date_time_str = now.strftime("%d.%m.%Y")
    changes = f"# Changelog\n\n## [{new_version}] - {date_time_str} - Title\n{back_changes}{front_changes}{other_changes}"
    replace_in_file(file_path="CHANGELOG.md", pattern="# Changelog\n", replacement=changes)

    replace_in_file(file_path="setup.py", pattern=r" *version='\d+\.\d+\.\d+'", replacement=f"    version='{new_version}'")
    replace_in_file(file_path="docs/conf.py", pattern=r"release = '\d+\.\d+\.\d+'", replacement=f"release = '{new_version}'")


def recompile_documentation():
    """
    recompile documentation with needed steps

    :raises FileNotFoundError: if file doesn't exist
    :raises PermissionError: if file is not readable or writable
    :raises IsADirectoryError: if file path leads to a directory
    :raises OSError: if file cannot be written to
    """

    try:
        os.remove(os.path.abspath("docs/README.rst"))
    except OSError:
        pass

    # update .rst files
    subprocess.run(["sphinx-apidoc", "--force", "-o", "docs", "."], check=True)

    # remove Unwanted files
    try:
        os.remove(os.path.abspath("docs/prepare_commit.rst"))
        os.remove(os.path.abspath("docs/setup.rst"))
    except OSError:
        pass

    with open("docs/modules.rst", "r") as file:
        data = file.read()
        updated_data = data.replace("   prepare_commit\n", "")
        updated_data = updated_data.replace("   setup\n", "")

    with open("docs/modules.rst", "w") as file:
        file.write(updated_data)

    # update README.rst
    subprocess.run(["pandoc", "-s", "README.md", "-o", "docs/README.rst"])

    # regenerate .html files
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')

    if sys.platform == "linux" or sys.platform == "linux2":
        subprocess.run(["make", "clean"], cwd=docs_dir, check=True)
        subprocess.run(["make", "html"], cwd=docs_dir, check=True)

    elif sys.platform == "win32":
        subprocess.run(["./make.bat", "html"], cwd=docs_dir, check=True)


if __name__ == "__main__":
    """"""
    new_version = new_version(is_major=False, is_minor=True, is_patch=False)
    update_files()
    print("Updated files")
    recompile_documentation()
    print("recompiled Documentation")
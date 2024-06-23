"""
Utility functions used in various places
"""

import os
import subprocess
import sys
from collections import deque
from typing import Dict, List

import sublime

from .jomini import GameObjectBase


def open_path(path: str):
    system = sys.platform
    if system == "Darwin":  # macOS
        subprocess.Popen(("open", path))
    elif system == "Windows" or system == "win32" or system == "win":  # Windows
        os.startfile(path)
    else:  # Linux and other Unix-like systems
        subprocess.Popen(("xdg-open", path))


def is_file_in_directory(file_path: str, directory_path: str) -> bool:
    if not os.path.exists(file_path):
        return False

    if not os.path.exists(directory_path):
        return False

    absolute_file_path = os.path.abspath(file_path)
    absolute_directory_path = os.path.abspath(directory_path)

    common_path = os.path.commonpath([absolute_file_path, absolute_directory_path])

    return common_path == absolute_directory_path


class IterViews:
    def __init__(self, windows: List[sublime.Window]):
        self.windows = windows

    def __iter__(self):
        for win in self.windows:
            for view in win.views():
                yield view


def get_syntax_name(view: sublime.View) -> str:
    syntax = view.syntax()
    if syntax is None:
        return ""

    name = view.syntax().name  # type: ignore
    return name


def get_file_name(view: sublime.View) -> str:
    filename = view.file_name()
    if filename is None:
        return ""

    return filename


# Get the index of a closing bracket in a string given the starting brackets index
def get_index(string: str, index: int):
    if string[index] != "{":
        return -1
    d = deque()
    for k in range(index, len(string)):
        if string[k] == "}":
            d.popleft()
        elif string[k] == "{":
            d.append(string[index])
        if not d:
            return k + 1
    return -1


def print_load_balanced_game_object_creation(
    game_objects: Dict[str, GameObjectBase], object_names: Dict[str, type]
):
    """
    Algorithm to balance the load between between the functions that load game objects
    Distributes game objects to the functions as evenly as possible based on the total number of objects within them.
    """
    object_values = dict()

    for i in object_names.keys():
        object_values[i] = int(game_objects[i].length())

    sorted_values = sorted(object_values.items(), key=lambda x: x[1], reverse=True)
    groups = [[] for _ in range(5)]

    for i in sorted_values:
        key = i[0]
        value = i[1]
        min_group = min(groups, key=lambda group: sum(int(item[1]) for item in group))
        min_group.append((key, value))

    suffixes = {
        1: "first",
        2: "second",
        3: "third",
        4: "fourth",
        5: "fifth",
    }

    expected_values_dict = dict()
    for i, group in enumerate(groups, 1):
        for key, value in group:
            expected_values_dict[key] = value

        print(f"def load_{suffixes[i]}():")
        for key, value in group:
            object_class = object_names[key].__name__
            print(f'    self.game_objects["{key}"] = {object_class}()')

    print(
        dict(
            sorted(expected_values_dict.items(), key=lambda item: item[1], reverse=True)
        )
    )

"""
Code related to loading, saving, and caching imperator game objects
"""

import ast
import hashlib
import json
import os
from typing import Any, Dict, List, Set

import sublime
from .jomini import dict_to_game_object


class JominiGameObject:
    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name

    def get_mod_cache_path(self) -> str:
        return os.path.join(sublime.cache_path(), self.plugin_name, "mod_cache.json")

    def get_object_cache_path(self) -> str:
        return os.path.join(sublime.cache_path(), self.plugin_name, "object_cache.json")

    def check_mod_for_changes(
        self,
        mod_files: List[Any],
        dir_to_game_object_dict: Dict[str, str],
        game_object_dirs: Dict[str, str],
        write_syntax=False,
    ) -> Set[str]:
        """
        Check if any changes have been made to mod files
        if changes have been made this returns a set of game objects that need to be recreated and cached
        """
        if not os.path.exists(self.get_object_cache_path()):
            with open(self.get_object_cache_path(), "w", encoding="utf-8") as file:
                file.write("{ }")
        if os.stat(self.get_object_cache_path()).st_size < 200:
            # If there are no objects in the cache, they all need to be created
            return set(dir_to_game_object_dict.values())

        mod_cache_path = self.get_mod_cache_path()
        with open(mod_cache_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Add the names and output of os.stat.st_mtime together for all the files in the current mods into stats_string
        for path in mod_files:
            mod_name = path.replace("\\", "/").rstrip("/").rpartition("/")[2]
            for dirpath, dirnames, filenames in os.walk(path):
                relative_path = dirpath.replace(path, "")[1:]
                if relative_path not in game_object_dirs:
                    continue

                mod_files = [
                    x for x in filenames if x.endswith(".txt") or x.endswith(".gui")
                ]

                if not mod_files:
                    continue

                stats_string = str()
                for i in mod_files:
                    full_path = dirpath + "/" + i
                    value = os.stat(full_path).st_mtime
                    stats_string += f"{mod_name}{value}"

                # Encode stats_string for each game object directory
                game_object_dirs[relative_path] = hashlib.sha256(
                    stats_string.encode()
                ).hexdigest()

        with open(mod_cache_path, "w") as f:
            if write_syntax:
                json_to_write = [game_object_dirs, "write_syntax"]
            else:
                json_to_write = [game_object_dirs]

            f.write(json.dumps(json_to_write))

        changed_objects = set()
        for i in self.compare_dicts(game_object_dirs, data[0]):
            if i in dir_to_game_object_dict:
                changed_objects.add(dir_to_game_object_dict[i])

        return changed_objects

    def compare_dicts(self, dict1: Dict, dict2: Dict):
        # Compare two dictionaries and return a set of all the keys with values that are not the same in both
        common_keys = set(dict1.keys()) & set(dict2.keys())
        unequal_keys = set()

        for key in common_keys:
            if dict1[key] != dict2[key]:
                unequal_keys.add(key)

        return unequal_keys

    def check_for_syntax_changes(self) -> bool:
        if not os.path.exists(self.get_mod_cache_path()):
            with open(self.get_mod_cache_path(), "w", encoding="utf-8") as file:
                file.write("[{ }]")
        with open(self.get_mod_cache_path(), "r", encoding="utf-8") as file:
            data = json.load(file)
        if len(data) > 1:
            return True
        return False

    def load_game_objects_json(self):
        with open(self.get_object_cache_path(), "r") as f:
            data = json.load(f)
        return data

    def get_objects_from_cache(self, default_game_objects):
        with open(self.get_object_cache_path(), "r") as f:
            data = json.load(f)
        for i in default_game_objects:
            if i in data:
                default_game_objects[i] = dict_to_game_object(ast.literal_eval(data[i]))

        return default_game_objects

    def cache_all_objects(self, game_objects):
        # Write all generated objects to cache
        objects = dict()
        for i in game_objects:
            objects[i] = game_objects[i].to_json()
        with open(self.get_object_cache_path(), "w") as f:
            f.write(json.dumps(objects))

    def add_color_scheme_scopes(self):
        # Add scopes for yml text formatting to color scheme
        DEFAULT_CS = "Packages/Color Scheme - Default/Monokai.sublime-color-scheme"
        prefs = sublime.load_settings("Preferences.sublime-settings")
        cs = prefs.get("color_scheme", DEFAULT_CS)
        scheme_cache_path = os.path.join(
            sublime.packages_path(),
            "User",
            "PdxTools",
            cs,  # type: ignore
        ).replace("tmTheme", "sublime-color-scheme")
        if not os.path.exists(scheme_cache_path):
            os.makedirs(os.path.dirname(scheme_cache_path), exist_ok=True)
            rules = """{"variables": {}, "globals": {},"rules": [{"scope": "text.format.white.yml","foreground": "rgb(250, 250, 250)",},{"scope": "text.format.grey.yml","foreground": "rgb(173, 165, 160)",},{"scope": "text.format.red.yml","foreground": "rgb(210, 40, 40)",},{"scope": "text.format.green.yml","foreground": "rgb(40, 210, 40)",},{"scope": "text.format.yellow.yml","foreground": "rgb(255, 255, 0)",},{"scope": "text.format.blue.yml","foreground": "rgb(51, 214, 255)",},{"scope": "text.format.gold.yml","foreground": "#ffb027",},{"scope": "text.format.bold.yml","font_style": "bold"},{"scope": "text.format.italic.yml","font_style": "italic"}]}"""
            with open(scheme_cache_path, "w") as f:
                f.write(rules)


def write_syntax(li: List[str], header: str, scope: str):
    string = ""
    count = 0
    string += f"\n    # Generated {header}\n    - match: \\b("
    for i in li:
        count += 1
        # Count is needed to split because columns are waaay too long for syntax regex
        if count == 0:
            string = f")\\b\n      scope: {scope}\n"
            string += f"    # Generated {header}\n    - match: \\b({i}|"
        elif count == 75:
            string += f")\\b\n      scope: {scope}\n"
            string += f"    # Generated {header}\n    - match: \\b({i}|"
            count = 1
        else:
            string += f"{i}|"
    string += f")\\b\n      scope: {scope}"
    return string

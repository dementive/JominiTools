"""
Special game objects that are common to all jomini games can be implemented here, currently these include:

NamedColor
"""

import os
import re
from colorsys import hsv_to_rgb
from typing import Union

from .jomini import PdxScriptObject, PdxScriptObjectType, GameObjectBase


# Gui Class implementations
class GuiType(GameObjectBase):
    def __init__(self, mod_files, game_files):
        super().__init__(mod_files, game_files)
        self.get_data("gui")

    def get_pdx_object_list(self, path: str) -> PdxScriptObjectType:
        obj_list = list()
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in [f for f in filenames if f.endswith(".gui")]:
                if filename in self.ignored_files:
                    continue
                file_path = os.path.join(dirpath, filename)
                if self.included_files:
                    if filename not in self.included_files:
                        continue
                with open(file_path, "r", encoding="utf-8-sig") as file:
                    for i, line in enumerate(file):
                        if self.should_read(line):
                            found_item = re.search(
                                r"type\s([A-Za-z_][A-Za-z_0-9]*)\s?=", line
                            )
                            if found_item and found_item.groups()[0]:
                                found_item = found_item.groups()[0]
                                obj_list.append(
                                    PdxScriptObject(found_item, file_path, i + 1)
                                )
        return PdxScriptObjectType(obj_list)

    def should_read(self, x: str) -> bool:
        # Check if a line should be read
        out = re.search(r"type\s[A-Za-z_][A-Za-z_0-9]*\s?=", x)
        return True if out else False


class GuiTemplate(GameObjectBase):
    def __init__(self, mod_files, game_files):
        super().__init__(mod_files, game_files)
        self.get_data("gui")

    def get_pdx_object_list(self, path: str) -> PdxScriptObjectType:
        obj_list = list()
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in [f for f in filenames if f.endswith(".gui")]:
                if filename in self.ignored_files:
                    continue
                file_path = os.path.join(dirpath, filename)
                if self.included_files:
                    if filename not in self.included_files:
                        continue
                with open(file_path, "r", encoding="utf-8-sig") as file:
                    for i, line in enumerate(file):
                        if self.should_read(line):
                            found_item = re.search(
                                r"template\s([A-Za-z_][A-Za-z_0-9]*)", line
                            )
                            if found_item and found_item.groups()[0]:
                                found_item = found_item.groups()[0]
                                obj_list.append(
                                    PdxScriptObject(found_item, file_path, i + 1)
                                )
        return PdxScriptObjectType(obj_list)

    def should_read(self, x: str) -> bool:
        # Check if a line should be read
        out = re.search(r"template\s[A-Za-z_][A-Za-z_0-9]*", x)
        return True if out else False

class ScriptValue(GameObjectBase):
    def __init__(self, mod_files, game_files):
        super().__init__(mod_files, game_files)
        self.get_data(f"common{os.sep}script_values")


class ScriptedEffect(GameObjectBase):
    def __init__(self, mod_files, game_files):
        super().__init__(mod_files, game_files)
        self.get_data(f"common{os.sep}scripted_effects")


class ScriptedModifier(GameObjectBase):
    def __init__(self, mod_files, game_files):
        super().__init__(mod_files, game_files)
        self.get_data(f"common{os.sep}scripted_modifiers")


class ScriptedTrigger(GameObjectBase):
    def __init__(self, mod_files, game_files):
        super().__init__(mod_files, game_files)
        self.get_data(f"common{os.sep}scripted_triggers")


class ScriptedList(GameObjectBase):
    def __init__(self, mod_files, game_files):
        super().__init__(mod_files, game_files)
        self.get_data(f"common{os.sep}scripted_lists")


class ScriptedGui(GameObjectBase):
    def __init__(self, mod_files, game_files):
        super().__init__(mod_files, game_files)
        self.get_data(f"common{os.sep}scripted_guis")


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in hsv_to_rgb(h, s, v))


class PdxColorObject(PdxScriptObject):
    def __init__(self, key, path, line, color):
        super().__init__(key, path, line)
        self.color = color
        self.rgb_color = self.get_rgb_color()

    def get_rgb_color(self):
        """
        Color Formats:
                color1 = hsv { 1.0 1.0 1.0 }
                color2 = hsv360 { 360 100 100 }
                color3 = { 255 255 255 }
                color4 = rgb { 255 255 255 }
                color5 = hex { aabbccdd }
        This function merges all of these formats into one and returns (r, g, b) tuple
        """
        object_color = self.color
        r = 255
        g = 255
        b = 0
        try:
            if object_color.startswith("rgb") or object_color.startswith("{"):
                split_color = object_color.split("{")[1].replace(" }", "")
                split_color = split_color.split(" ")
                r = float(split_color[1].replace("o", ""))
                g = float(split_color[2].replace("o", ""))
                b = float(split_color[3].replace("o", ""))
            if re.search(r"\bhsv\b", object_color):
                split_color = object_color.split("{")[1].replace(" }", "")
                split_color = object_color.split(" ")
                h = float(split_color[2].replace("o", ""))
                s = float(split_color[3].replace("o", ""))
                v = float(split_color[4].replace("o", ""))
                rgb = hsv2rgb(h, s, v)
                r = rgb[0]
                g = rgb[1]
                b = rgb[2]
            if re.search(r"\bhsv360\b", object_color):
                split_color = object_color.split("{")[1].replace(" }", "")
                split_color = object_color.split(" ")
                h = float(split_color[2].replace("o", "")) / 360
                s = float(split_color[3].replace("o", "")) / 100
                v = float(split_color[4].replace("o", "")) / 100
                rgb = hsv2rgb(h, s, v)
                r = rgb[0]
                g = rgb[1]
                b = rgb[2]
                if (
                    split_color[2] == "187"
                    and split_color[3] == "83"
                    and split_color[4] == "146"
                ):
                    r = 230
                    g = 0
                    b = 230
            if re.search(r"\bhex\b", object_color):
                split_color = object_color.split("{")[1].replace(" }", "")
                split_color = split_color.split("#").replace(" ", "")
                return tuple(int(split_color[i : i + 2], 16) for i in (0, 2, 4))
        except IndexError:
            pass
        return (r, g, b)

    def __eq__(self, other):
        if isinstance(other, PdxColorObject):
            return self.key == other.key
        elif isinstance(other, str):
            return self.key == other
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, PdxColorObject):
            return self.key < other.key
        elif isinstance(other, str):
            return self.key < other
        else:
            return False

    def __gt__(self, other):
        if isinstance(other, PdxColorObject):
            return self.key > other.key
        elif isinstance(other, str):
            return self.key > other
        else:
            return False


def make_named_color_object(objects: dict) -> GameObjectBase:
    obj_list = list()
    for i in objects:
        obj_list.append(PdxColorObject(i, objects[i][0], objects[i][1], objects[i][2]))
    game_object = GameObjectBase()
    game_object.main = PdxScriptObjectType(obj_list)
    return game_object


class NamedColor(GameObjectBase):
    def __init__(self, mod_files, game_files):
        super().__init__(mod_files, game_files, level=1)
        self.get_data(f"common{os.sep}named_colors")

    def to_dict(self) -> dict:
        d = dict()
        for i in self.main.objects:
            d[i.key] = [i.path, i.line, i.color]  # type: ignore
        return d

    def get_pdx_object_list(self, path: str) -> PdxScriptObjectType:
        obj_list = list()
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in [f for f in filenames if f.endswith(".txt")]:
                if filename in self.ignored_files:
                    continue
                file_path = os.path.join(dirpath, filename)
                if self.included_files:
                    if filename not in self.included_files:
                        continue
                with open(file_path, "r", encoding="utf-8-sig") as file:
                    for i, line in enumerate(file):
                        if self.should_read(line):
                            found_item = re.search(
                                r"([A-Za-z_][A-Za-z_0-9]*)\s*=(.*)", line
                            )
                            if found_item and found_item.groups()[0]:
                                item_color = found_item.groups()[1]
                                found_item = found_item.groups()[0]
                                item_color = item_color.strip().split("#")[0]
                                item_color = item_color.rpartition("}")[0]
                                if not item_color:
                                    continue
                                else:
                                    item_color = item_color.replace("\t", " ") + " }"
                                    item_color = re.sub(r"\s+", " ", item_color)
                                    obj_list.append(
                                        PdxColorObject(
                                            found_item, file_path, i + 1, item_color
                                        )
                                    )
        return PdxScriptObjectType(obj_list)

    def should_read(self, x: str) -> bool:
        # Check if a line should be read
        if re.search(r"([A-Za-z_][A-Za-z_0-9]*)\s*=", x):
            return True
        return False


JominiObject = Union[
    ScriptValue,
    ScriptedEffect,
    ScriptedModifier,
    ScriptedTrigger,
    ScriptedList,
    ScriptedGui,
    NamedColor,
    GuiType,
    GuiTemplate,
]

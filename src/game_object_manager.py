import os
from typing import Set, Dict

from .jomini import GameObjectBase


class GameObjectData:
    def __init__(self, name: str, obj: type, path: str):
        self.name = name
        self.obj = obj
        self.path = path


class JominiGameObjectManager:
    def __init__(self):
        self.example = GameObjectData("ambition", str, f"common{os.sep}ambitions")

    def __iter__(self):
        for attr in self.__dict__:
            yield getattr(self, attr)

    def get_objects(self) -> Set[GameObjectData]:
        objects = set()
        for i in self:
            objects.add(i)
        return objects

    def get_default_game_objects(self):
        base_object = GameObjectBase()
        objects = self.get_objects()
        game_objects = dict()
        for i in objects:
            game_objects[i.name] = base_object

        return game_objects

    def get_game_object_dirs(self) -> Dict[str, str]:
        objects = self.get_objects()
        game_objects = dict()
        for i in objects:
            if i.path not in game_objects:
                game_objects[i.path] = ""

        return game_objects

    def get_dir_to_game_object_dict(self) -> Dict[str, str]:
        objects = self.get_objects()
        game_objects = dict()
        for i in objects:
            game_objects[i.path] = i.name

        return game_objects

    def get_game_object_to_class_dict(self) -> Dict[str, type]:
        objects = self.get_objects()
        game_objects = dict()
        for i in objects:
            game_objects[i.name] = i.obj

        return game_objects

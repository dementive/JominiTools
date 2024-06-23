"""
The main event listener for the plugin, this is where most of the plugin features actually happen.
The init function of the event listener is treated as the main entry point for the plugin.
"""

import re
import inspect
from abc import ABC, abstractmethod
from typing import Set, Union, List, Tuple

import sublime

from .game_data import JominiGameData
from .game_objects import JominiGameObject
from .game_object_manager import JominiGameObjectManager
from .utils import get_file_name, get_syntax_name
from .plugin import JominiPlugin
from .jomini import PdxScriptObject


class JominiEventListener(ABC):
    @abstractmethod
    def init_hover(
        self,
        script_syntax_name: str,
        localization_syntax_name: str,
    ):
        pass

    @abstractmethod
    def init_autocomplete(
        self, auto_complete_fields, auto_complete_selector_flag_pairs
    ):
        pass

    @abstractmethod
    def init_game_object_manager(self):
        self.manager = JominiGameObjectManager()

    @abstractmethod
    def init_game_data(self):
        self.game_data = JominiGameData

    @abstractmethod
    def write_data_to_syntax(self, game_objects):
        pass

    @abstractmethod
    def show_popup_default(
        self,
        view: sublime.View,
        point: int,
        PdxObject: PdxScriptObject,
        header: str,
    ):
        pass

    @abstractmethod
    def handle_scripted_args(
        self, view: sublime.View, point: int, region=False
    ) -> Union[sublime.Region, str]:
        pass

    @abstractmethod
    def create_all_game_objects(self):
        pass

    @abstractmethod
    def on_deactivated_async(self, view: sublime.View):
        """
        Remove field states when view loses focus
        if cursor was in a field in the old view but not the new view the completions will still be accurate
        save the id of the view so it can be readded when it regains focus
        """
        vid = view.id()
        for field, views in self.auto_complete_fields.items():
            if getattr(self, field):
                setattr(self, field, False)
                views.append(vid)

    @abstractmethod
    def on_activated_async(self, view: sublime.View):
        vid = view.id()
        for field, views in self.auto_complete_fields.items():
            if vid in views:
                setattr(self, field, True)
                views.remove(vid)

    @abstractmethod
    def on_query_completions(
        self, view: sublime.View, prefix: str, locations: List[int]
    ) -> Union[
        None,
        List[Union[str, Tuple[str, str], sublime.CompletionItem]],
        Tuple[
            List[Union[str, Tuple[str, str], sublime.CompletionItem]],
            sublime.AutoCompleteFlags,
        ],
        sublime.CompletionList,
    ]:
        if not view:
            return None

        syntax_name = get_syntax_name(view)

        if (
            syntax_name != self.plugin.script_syntax_name
            and syntax_name != self.plugin.localization_syntax_name
            and syntax_name != self.plugin.gui_syntax_name
        ):
            return None

    def init(self, plugin: JominiPlugin):
        self.auto_complete_fields = dict()  # must be before init_autocomplete
        self.init_hover(plugin.script_syntax_name, plugin.localization_syntax_name)
        self.init_game_object_manager()
        self.init_game_data()
        self.init_autocomplete(
            self.game_data.auto_complete_fields,
            self.game_data.auto_complete_selector_flag_pairs,
        )
        self.game_objects = self.manager.get_default_game_objects()
        self.plugin = plugin
        self.settings = plugin.settings
        self.game_files_path = self.settings.get("GameFilesPath")
        self.mod_files: List = self.settings.get("PathsToModFiles")  # type: ignore
        self.jomini_game_object = JominiGameObject(plugin.name)

        syntax_changes = self.jomini_game_object.check_for_syntax_changes()
        changed_objects_set = self.jomini_game_object.check_mod_for_changes(
            self.mod_files,
            self.manager.get_dir_to_game_object_dict(),
            self.manager.get_game_object_dirs(),
        )
        if len(self.jomini_game_object.load_game_objects_json()) != len(
            self.game_objects
        ):
            # Create all objects for the first time
            sublime.set_timeout_async(lambda: self.create_all_game_objects(), 0)
            sublime.set_timeout_async(lambda: self.post_game_object_creation(), 0)
            sublime.active_window().run_command("run_tiger")
        elif changed_objects_set:
            self.load_changed_objects(changed_objects_set)
            sublime.active_window().run_command("run_tiger")
        else:
            # Load cached objects
            self.game_objects = self.jomini_game_object.get_objects_from_cache(
                self.manager.get_default_game_objects()
            )
            if syntax_changes:
                sublime.set_timeout_async(
                    lambda: self.write_data_to_syntax(self.game_objects), 0
                )

        # Uncomment this and use the output to balance the load between the threads in create_all_game_objects
        # from .utils import print_load_balanced_game_object_creation
        # sublime.set_timeout_async(
        #     lambda: print_load_balanced_game_object_creation(self.game_objects), 0
        # )

        self.jomini_game_object.add_color_scheme_scopes()

    def load_changed_objects(self, changed_objects_set: Set[str], write_syntax=True):
        # Load objects that have changed since they were last cached
        self.game_objects = self.jomini_game_object.get_objects_from_cache(
            self.manager.get_default_game_objects()
        )

        sublime.set_timeout_async(
            lambda: self.create_game_objects(changed_objects_set), 0
        )
        if write_syntax:
            sublime.set_timeout_async(
                lambda: self.write_data_to_syntax(self.game_objects), 0
            )

        # Cache created objects
        sublime.set_timeout_async(
            lambda: self.jomini_game_object.cache_all_objects(self.game_objects), 0
        )

    def create_game_objects(
        self,
        changed_objects_set: Set[str],
    ):
        game_object_to_class_dict = self.manager.get_game_object_to_class_dict()
        for i in changed_objects_set:
            # TODO - threading and load balancing here if the expected number of objects to be created is > 250
            class_ref = game_object_to_class_dict[i]

            # Jomini objects have to be called with the mod and game files paths since they are not known at the time of class creation.
            is_jomini_object = (
                True
                if len(inspect.signature(class_ref.__init__).parameters.values()) == 3
                else False
            )
            if is_jomini_object:
                self.game_objects[i] = class_ref(self.mod_files, self.game_files_path)
            else:
                self.game_objects[i] = class_ref()

    def post_game_object_creation(self):
        # Write syntax data after creating objects so they actually exist when writing
        sublime.set_timeout_async(
            lambda: self.write_data_to_syntax(self.game_objects), 0
        )
        # Cache created objects
        sublime.set_timeout_async(
            lambda: self.jomini_game_object.cache_all_objects(self.game_objects), 0
        )
        # Update hashes for each game object directory
        sublime.set_timeout_async(
            lambda: self.jomini_game_object.check_mod_for_changes(
                self.mod_files,
                self.manager.get_dir_to_game_object_dict(),
                self.manager.get_game_object_dirs(),
            ),
            0,
        )

    def create_completion_list(self, flag_name: str, completion_kind: str):
        if not getattr(self, flag_name, False):
            return None

        completions = self.game_objects[flag_name].keys()
        completions = sorted(completions)
        return sublime.CompletionList(
            [
                sublime.CompletionItem(
                    trigger=key,
                    completion_format=sublime.COMPLETION_FORMAT_TEXT,
                    kind=completion_kind,
                    details=" ",
                )
                # Calling sorted() twice makes it so completions are ordered by
                # 1. the number of times they appear in the current buffer
                # 2. if they dont appear they show up alphabetically
                for key in sorted(completions)
            ],
            flags=sublime.INHIBIT_EXPLICIT_COMPLETIONS
            | sublime.INHIBIT_WORD_COMPLETIONS,
        )

    def do_hover_async(self, view: sublime.View, point: int, hover_objects):
        word_region = view.word(point)
        word = view.substr(word_region)
        fname = get_file_name(view)
        current_line_num = view.rowcol(point)[0] + 1

        if view.match_selector(point, "comment.line"):
            return

        if (
            view.match_selector(point, "variable.parameter.scope.usage")
            or view.match_selector(point, "variable.parameter.remove.var")
            or view.match_selector(point, "variable.parameter.trigger.usage")
            or view.match_selector(point, "variable.parameter.var.usage")
        ):
            if fname and (
                "scripted_triggers" in fname
                or "scripted_effects" in fname
                or "scripted_modifiers" in fname
            ):
                word = self.handle_scripted_args(view, point)

            if view.match_selector(point, "variable.parameter.scope.usage"):
                self.show_popup_default(
                    view,
                    point,
                    PdxScriptObject(word, fname, current_line_num),  # type: ignore
                    "Saved Scope",
                )
            else:
                self.show_popup_default(
                    view,
                    point,
                    PdxScriptObject(word, fname, current_line_num),  # type: ignore
                    "Saved Variable",
                )
            return

        if view.match_selector(point, "entity.name.function.var.declaration"):
            if fname and (
                "scripted_triggers" in fname
                or "scripted_effects" in fname
                or "scripted_modifiers" in fname
            ):
                word = self.handle_scripted_args(view, point)
            self.show_popup_default(
                view,
                point,
                PdxScriptObject(word, fname, current_line_num),  # type: ignore
                "Saved Variable",
            )
            return
        if view.match_selector(point, "entity.name.function.scope.declaration"):
            if fname and (
                "scripted_triggers" in fname
                or "scripted_effects" in fname
                or "scripted_modifiers" in fname
            ):
                word = self.handle_scripted_args(view, point)
            self.show_popup_default(
                view,
                point,
                PdxScriptObject(word, fname, current_line_num),  # type: ignore
                "Saved Scope",
            )
            return

        if view.match_selector(
            point, "entity.name.scripted.arg"
        ) or view.match_selector(point, "variable.language.scripted.arg"):
            self.show_popup_default(
                view,
                point,
                PdxScriptObject(word, fname, current_line_num),
                "Scripted Argument",
            )
            return

        # Iterate over the list and call show_popup_default for each game object
        for hover_object, name in hover_objects:
            game_object = self.game_objects[hover_object].access(word)
            if game_object:
                self.show_popup_default(
                    view,
                    point,
                    game_object,
                    name,
                )
                break

    def check_for_patterns_and_set_flag(
        self,
        patterns_list: List[str],
        flag_name: str,
        view: sublime.View,
        line: str,
        point: int,
    ):
        for pattern in patterns_list:
            r = re.search(rf'\b{pattern}\s?=\s?(")?', line)
            if not r:
                continue
            y = 0
            idx = line.index(pattern) + view.line(point).a + len(pattern) + 2
            if r.groups()[0] == '"':
                y = 2
            if idx == point or idx + y == point or idx + 1 == point:
                setattr(self, flag_name, True)
                view.run_command("auto_complete")
                return True
        return False

    def check_pattern_and_set_flag(
        self, pattern: str, flag_name: str, view: sublime.View, line: str, point: int
    ):
        if pattern in line:
            idx = line.index(pattern) + view.line(point).a + len(pattern)
            if idx == point:
                setattr(self, flag_name, True)
                view.run_command("auto_complete")

    def check_for_simple_completions(self, view: sublime.View, point: int):
        """
        Check if the current cursor position should trigger a autocompletion item
        this is for simple declarations like: remove_building = CursorHere
        """
        for i in self.auto_complete_fields.keys():
            setattr(self, i, False)

        if view.substr(point) == "=":
            return

        line = view.substr(view.line(point))

        for patterns, flag in self.game_data.simple_completion_pattern_flag_pairs: # type: ignore
            if self.check_for_patterns_and_set_flag(patterns, flag, view, line, point):
                return

        for pattern, flag in self.game_data.simple_completion_scope_pattern_flag_pairs: # type: ignore
            self.check_pattern_and_set_flag(pattern, flag, view, line, point)

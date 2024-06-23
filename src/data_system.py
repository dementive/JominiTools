"""
Plugin features related to the game's data system functions.
Data system features that are not coupled to game objects should go here.
"""

from typing import List
from abc import ABC, abstractmethod

import sublime

from .plugin import JominiPlugin
from .utils import IterViews, get_syntax_name


class JominiDataSystemEventListener(ABC):
    def __init__(self, plugin: JominiPlugin):
        self.plugin = plugin

    @abstractmethod
    def on_selection_modified_async(self, view):
        if not view:
            return

        syntax_name = get_syntax_name(view)

        if (
            syntax_name != self.plugin.localization_syntax_name
            and syntax_name != self.plugin.gui_syntax_name
        ):
            return

        if len(view.sel()) == 1:
            point = view.sel()[0].a
            if view.match_selector(point, "empty.scope.prompt") or view.match_selector(
                point, "empty.scope.variable"
            ):
                view.run_command("auto_complete")

    @abstractmethod
    def on_query_completions(
        self, view: sublime.View, prefix: str, locations: List[int]
    ):
        if not view:
            return None

        syntax_name = get_syntax_name(view)

        if (
            syntax_name != self.plugin.localization_syntax_name
            and syntax_name != self.plugin.gui_syntax_name
        ):
            return

        fname = view.file_name()
        if not fname:
            return

        if len(view.sel()) == 1:
            point = view.sel()[0].a
            if view.match_selector(point, "empty.scope.prompt"):
                return self.get_prompt_completions(
                    "Scope", "entity.name.function.scope.declaration"
                )
            if view.match_selector(point, "empty.scope.variable"):
                return self.get_prompt_completions(
                    "Variable", "entity.name.function.var.declaration"
                )

    def get_prompt_completions(self, kind: str, selector: str):
        found_words = set()

        for view in IterViews(sublime.windows()):
            if get_syntax_name(view) != self.plugin.script_syntax_name:
                continue

            scope_regions = view.find_by_selector(selector)
            for region in scope_regions:
                found_words.add(view.substr(region))

        if not found_words:
            return None

        return sublime.CompletionList(
            [
                sublime.CompletionItem(
                    trigger=key,
                    completion=key,
                    completion_format=sublime.COMPLETION_FORMAT_SNIPPET,
                    kind=(sublime.KIND_ID_NAMESPACE, kind[0], kind),
                )
                for key in sorted(found_words)
            ],
            flags=sublime.INHIBIT_EXPLICIT_COMPLETIONS
            | sublime.INHIBIT_WORD_COMPLETIONS,
        )

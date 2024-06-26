"""
Code for autocomplete features of a plugin
"""

from abc import ABC, abstractmethod

import sublime
from .utils import get_index

auto_complete_fields_example = {
    "example": [],
}
selector_flag_pairs_example = [
    ("meta.op.mod.bracket", "opinion", "modifier = "),
    ("meta.trait.bracket", "trait"),
]


class JominiAutoComplete(ABC):
    def __init__(
        self,
        auto_complete_fields=auto_complete_fields_example,
        selector_flag_pairs=auto_complete_fields_example,
    ):
        self.trigger_field = False
        self.effect_field = False
        self.modifier_field = False
        self.mtth_field = False
        self.auto_complete_fields = auto_complete_fields
        self.selector_flag_pairs = selector_flag_pairs
        for field in self.auto_complete_fields.keys():
            setattr(self, field, False)

    @abstractmethod
    def init_autocomplete(
        self, auto_complete_fields, auto_complete_selector_flag_pairs
    ):
        # Must be overriden to init autocomplete.
        # this can't be done in the normal __init__ of the subclass due to how it is inherited into the main event listener.
        pass

    def check_region_and_set_flag(
        self,
        selector: str,
        flag_name: str,
        view: sublime.View,
        view_str: str,
        point: int,
        string_check_and_move=None,
    ):
        for br in view.find_by_selector(selector):
            i = sublime.Region(br.a, get_index(view_str, br.a))
            s = view.substr(i)
            if string_check_and_move and string_check_and_move in s:
                fpoint = (
                    s.index(string_check_and_move) + len(string_check_and_move)
                ) + i.a
                if fpoint == point:
                    setattr(self, flag_name, True)
                    view.run_command("auto_complete")
            elif i.contains(point) and not string_check_and_move:
                setattr(self, flag_name, True)
                view.run_command("auto_complete")

    def check_for_complex_completions(self, view: sublime.View, point: int):
        view_str = view.substr(sublime.Region(0, view.size()))

        for pair in self.selector_flag_pairs:
            if len(pair) == 3:
                selector, flag, string_check_and_move = pair
                self.check_region_and_set_flag(
                    selector, flag, view, view_str, point, string_check_and_move
                )
            else:
                selector, flag = pair
                self.check_region_and_set_flag(selector, flag, view, view_str, point)

from abc import ABC, abstractmethod
from typing_extensions import LiteralString

import sublime


class JominiPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> LiteralString:
        pass

    @property
    @abstractmethod
    def settings(self) -> sublime.Settings:
        pass

    @property
    @abstractmethod
    def script_syntax_name(self) -> LiteralString:
        pass

    @property
    @abstractmethod
    def localization_syntax_name(self) -> LiteralString:
        pass

    @property
    def gui_syntax_name(self) -> LiteralString:
        return "Jomini Gui"

    def valid_syntax(self, syntax_name: str) -> bool:
        """
        Check if a syntax is a syntax defined in this plugin
        """
        return (
            True
            if syntax_name
            in (
                self.script_syntax_name,
                self.localization_syntax_name,
                self.gui_syntax_name,
            )
            else False
        )

    def is_data_system_syntax(self, syntax_name: str) -> bool:
        """
        Check if a syntax is a data system syntax (localization or gui)
        """
        return (
            True
            if syntax_name in (self.localization_syntax_name, self.gui_syntax_name)
            else False
        )

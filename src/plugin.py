from abc import ABC, abstractmethod

import sublime


class JominiPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def settings(self) -> sublime.Settings:
        pass

    @property
    @abstractmethod
    def script_syntax_name(self) -> str:
        pass

    @property
    @abstractmethod
    def localization_syntax_name(self) -> str:
        pass

    @property
    def gui_syntax_name(self) -> str:
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

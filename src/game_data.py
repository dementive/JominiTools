from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any

import sublime


class JominiGameData(ABC):
    @property
    @abstractmethod
    def game_effects(self) -> Dict[str, str]:
        """
        A dictionary of a game's effects generated from the logs

        The key is the effect name and the value is the effect description in minihtml format
        """
        pass

    @property
    @abstractmethod
    def game_triggers(self) -> Dict[str, str]:
        """
        A dictionary of a game's triggers generated from the logs

        The key is the trigger name and the value is the trigger description in minihtml format
        """
        pass

    @property
    @abstractmethod
    def game_scopes(self) -> Dict[str, str]:
        """
        A dictionary of a game's scopes generated from the logs

        The key is the scopes name and the value is the scope description in minihtml format
        """
        pass

    @property
    @abstractmethod
    def game_modifiers(self) -> Dict[str, str]:
        """
        A dictionary of a game's modifiers generated from the logs.

        The key is the modifier name and the value is the modifier description in minihtml format.
        """
        pass

    @property
    @abstractmethod
    def simple_completion_pattern_flag_pairs(self) -> List[Tuple[List[str], str]]:
        """
        Data structure to hold all the effects, triggers, and other keywords that should trigger autocomplete

        The ingame syntax of these kinds of autocomplete triggers should always be:

        <keyword> = <game object>
        """
        pass

    @property
    @abstractmethod
    def simple_completion_scope_pattern_flag_pairs(self) -> List[Tuple[str, str]]:
        """
        Data structure to hold all the scope -> game object autocomplete triggers

        These would be things like:

        The ingame syntax of these kinds of autocomplete triggers should always be:

        <scope>:<game object>
        """
        pass

    @property
    @abstractmethod
    def completion_flag_pairs(
        self,
    ) -> List[Tuple[str, Tuple[sublime.KindId, str, str]]]:
        """
        Data structure to hold the game objects associated with certain autocomplete triggers that automatically show up depending on cursor position.

        All game objects that have any kind of autocomplete features will need an entry in this data structure.
        """
        pass

    @property
    @abstractmethod
    def data_system_completion_flag_pairs(
        self,
    ) -> List[Tuple[str, Tuple[sublime.KindId, str, str]]]:
        """
        The same as completion_flag_pairs but this is only for game objects that have autocomplete features in data system functions
        """
        pass

    @property
    @abstractmethod
    def data_system_completion_functions(self) -> List[Tuple[str, str]]:
        """
        Data structure to map game object keys to data system functions for autocomplete features.
        """
        pass

    @property
    @abstractmethod
    def auto_complete_selector_flag_pairs(self) -> List[Tuple[str, str, str]]:
        """
        Syntax selector to game object mapping for autocomplete in more complicated situations

        This solution is awful and parsing should be done in the lib NOT in the via syntax scopes so this will be removed in the future.
        """
        pass

    @property
    @abstractmethod
    def auto_complete_fields(self) -> Dict[str, List[Any]]:
        """
        Data structure to map game objects to all the views they are currently have autocomplete open in.

        This is used both to trigger autocomplete and keep it open when changing between views.

        Every game object with autocomplete features will need an entry.
        """
        pass

    @property
    @abstractmethod
    def script_hover_objects(self) -> List[Tuple[str, str]]:
        pass

    @property
    @abstractmethod
    def data_system_hover_objects(self) -> List[Tuple[str, str]]:
        pass

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

    @property
    def gui_content(self) -> Dict[str, Tuple[str, str, str]]:
        return {
            # Default types
            "button": ("green", "Used for player interaction with the game.", ""),
            "icon": ("green", "Used to display textures.", ""),
            "widget": ("green", "Main component of the interface.", ""),
            "container": ("green", "A basic container used to contain other elements.", ""),
            "flowcontainer": (
                "green",
                "Container that automatically spaces it’s children.",
                "",
            ),
            "vbox": ("green", "Vertical layout box.", ""),
            "hbox": ("green", "Horizontal layout box.", ""),
            "background": (
                "green",
                "Set a texture or a color as the background of a widget.",
                "",
            ),
            "textbox": ("green", "Box used to show text.", ""),
            "editbox": (
                "green",
                "Box used to take user input as text. These are mostly hardcoded.",
                "",
            ),
            "modify_texture": (
                "green",
                "Modify a texture with another texture. Implementation can be found in pdxgui_sprite_base.fxh.",
                "",
            ),
            "template": (
                "purple",
                "Define a reusable template of code.",
                "using = example_name",
            ),
            "datacontext": ("yellow", "Set the data context for the current element", ""),
            # Scrollbar Properties
            "min": ("orange", "Minimum fixed point value for a scrollbar.", "min = 0"),
            "max": ("orange", "Maximum fixed point value for a scrollbar.", "min = 100"),
            # General Properties
            "using": ("green", "Template usage.", "using = example_name"),
            "name": (
                "purple",
                "Name of an element. Does nothing in game but is useful when organizing code. Some element names are tied to C++ code so be careful when removing existing names as there may be game code that relies on that name.",
                'name = "x"',
            ),
            "size": ("blue", "Set element X and Y size.", "size = { 20 20 }"),
            "minimumsize": (
                "blue",
                "Set element X and Y minimum size.",
                "minimumsize = { 20 20 }",
            ),
            "maximumsize": (
                "blue",
                "Set element X and Y maximum size.",
                "maximumsize = { 20 20 }",
            ),
            "resizeparent": (
                "blue",
                "Automatically resize the parent of an element. Be careful not to have 2 elements resizing the same parent, this will cause recursion and crash the game.",
                "resizeparent = yes",
            ),
            "position": ("blue", "Set element X and Y position.", "position = { 20 20 }"),
            "parentanchor": (
                "blue",
                "Set position of element based on a point in it’s parent.",
                "parentanchor = left/right/center/top/bottom/vcenter/hcenter\nOR\nparentanchor = top|right",
            ),
            "widgetanchor": (
                "blue",
                "Set position of element based on a point.",
                "widgetanchor = left/right/center/top/bottom/vcenter/hcenter\nOR\nwidgetanchor = top|right",
            ),
            "visible": ("yellow", "Set element visibility.", "visible = &#60;triggers&#62;"),
            "enabled": (
                "yellow",
                "Determine if a button is clickable.",
                "enabled = &#60;triggers&#62;",
            ),
            "checked": (
                "yellow",
                "Determine if a checkbutton is checked.",
                'checked = "&#60;triggers&#62;"',
            ),
            "movable": (
                "blue",
                "Determine if an element can be moved around the UI. Typically only used with top level windows/widgets.",
                "movable = yes",
            ),
            "alpha": ("blue", "Set alpha of an element", "alpha = 0.5"),
            "alwaystransparent": (
                "blue",
                "Allow an element to be clicked through.",
                "alwaystransparent = yes",
            ),
            "allow_outside": (
                "blue",
                "Allow children of this element to be clickable if they end up outside of its bounds.",
                "allow_outside = yes",
            ),
            "scissor": (
                "blue",
                "Crops the children of an element if they end up outside of its bounds.",
                "scissor = yes",
            ),
            "margin": ("blue", "Set the margins of a element.", "margin = { 10 10 }"),
            "margin_top": ("blue", "Set the top margin of an element.", "margin_top = 4"),
            "margin_bottom": (
                "blue",
                "Set the bottom margin of an element.",
                "margin_bottom = 4",
            ),
            "margin_left": ("blue", "Set the left margin of an element.", "margin_left = 4"),
            "margin_right": (
                "blue",
                "Set the right margin of an element.",
                "margin_right = 4",
            ),
            "spritetype": (
                "blue",
                "The sprite type of an element.",
                "spritetype = CorneredTiled/CorneredStretched/Stretched",
            ),
            "spriteType": (
                "blue",
                "The sprite type of an element.",
                "spriteType = CorneredTiled/CorneredStretched/Stretched",
            ),
            "spriteborder": (
                "blue",
                "The sprite border of an element.",
                "spriteborder = { 110 5 }",
            ),
            "priority": (
                "blue",
                "Set the priority of a layer. Layers with a higher priority will be shown on top of layers with lower priority.",
                "priority = 10",
            ),
            "layer": (
                "blue",
                "The layer the element is placed on. Layers with a higher priority will be shown on top of layers with lower priority.",
                "layer = top",
            ),
            "color": (
                "blue",
                "Set the color of an element, only works with elements that have a texture of some kind.",
                "color = { 0.8 0.2 0.2 1 }",
            ),
            "block": (
                "red",
                "Define a block of code within a type or template that can be overriden when it is used with a blockoverride.",
                "",
            ),
            "blockoverride": (
                "red",
                "Override a named block of code in a type or template.",
                "",
            ),
            "types": (
                "purple",
                "Definition of a new type that is derived from another type.",
                "",
            ),
            "type": (
                "purple",
                "Definition of a new type that is derived from another type.",
                "",
            ),
            "pop_out": (
                "blue",
                "Pop out the portrait from a portrait button.",
                "pop_out = no",
            ),
            "glow": (
                "red",
                "Set a glow around an element. Glow can have a set radius and color.",
                "",
            ),
            "glow_radius": (
                "blue",
                "Set the radius of the glow around an element.",
                "glow_radius = 4",
            ),
            "fonttintcolor": (
                "blue",
                "The font tint color, used only in tooltips. Takes a function that returns a CVector4f",
                'fonttintcolor = "[TooltipInfo.GetTintColor]"',
            ),
            # Container Properties
            "ignoreinvisible": (
                "blue",
                "Ignore invisible elements of a container.",
                "ignoreinvisible = yes",
            ),
            "direction": (
                "blue",
                "The direction of a layout.",
                "direction = vertical/horizontal",
            ),
            "flipdirection": (
                "blue",
                "Flip the direction of the layout.",
                "flipdirection = yes",
            ),
            "spacing": (
                "blue",
                "Set the spacing between child elements of a container.",
                "spacing = 10",
            ),
            "layoutpolicy_vertical": (
                "blue",
                "Set the vertical layout behavior of a container.",
                "layoutpolicy_vertical = expanding/fixed/preferred/growing",
            ),
            "layoutpolicy_horizontal": (
                "blue",
                "Set the horizontal layout behavior of a container.",
                "layoutpolicy_horizontal = expanding/fixed/preferred/growing",
            ),
            # Effect Properties
            "onclick": (
                "red",
                "Effect to run when a button is clicked.",
                'onclick = "&#60;effects&#62;"',
            ),
            "onrightclick": (
                "red",
                "Effect to run when a button is right clicked.",
                'onrightclick = "&#60;effects&#62;"',
            ),
            "onmousehierarchyenter": (
                "red",
                "Effect to run when the element is hovered with a mouse. Only works for some elements, if it doesn't work use the '_mouse_enter' state instead.",
                'onmousehierarchyenter = "&#60;effects&#62;"',
            ),
            "onmousehierarchyleave": (
                "red",
                "Effect to run when the element is hovered with a mouse. Only works for some elements, if it doesn't work use the '_mouse_leave' state instead.",
                'onmousehierarchyleave = "&#60;effects&#62;"',
            ),
            "shortcut": (
                "blue",
                "Keyboard shortcut that will run the onclick of a button when pressed.",
                'shortcut = "close_window"',
            ),
            # Text Properties
            "text": ("purple", "Text to display in an element.", 'text = "words"'),
            "tooltip": (
                "purple",
                "Show text in a tooltip when an element is hovered over.",
                'tooltip = "words"',
            ),
            "tooltip_enabled": (
                "yellow",
                "Determine whether to show the tooltip.",
                "tooltip_enabled = no",
            ),
            "max_width": ("blue", "Set max width of text.", "max_width = 100"),
            "elide": (
                "blue",
                "Adds 3 dots to the end or start of text if it exceeds max_width.",
                "elide = left/right",
            ),
            "font": ("blue", "Set the font to use to render text.", 'font = "OpenSans"'),
            "fontsize": ("blue", "Set the font size of text.", "fontsize = 18"),
            "fontcolor": (
                "blue",
                "Set the fontcolor of a text. Don't ever hardcode these values into individual textboxes. Always use common font color templates.",
                "fontcolor = { 1 0 0 1 }",
            ),
            "autoresize": (
                "blue",
                "Automatically resize text to fit the container it is in.",
                "autoresize = yes",
            ),
            "align": (
                "blue",
                "Align text within it’s textbox.",
                "align = left/right/center/top/bottom/vcenter/hcenter\nOR\nalign = top|right",
            ),
            "fontsize_min": (
                "blue",
                "Set the minimum possible font size for text.",
                "fontsize_min = 14",
            ),
            "multiline": (
                "blue",
                "Set if text will automatically show up on multiple lines.",
                "multiline = yes",
            ),
            # Animation Properties
            "animation": (
                "red",
                "Animate an elements properties. Used inside of a state = {} block.",
                "",
            ),
            "state": ("blue", "Animation state of an element.", ""),
            "duration": (
                "purple",
                "Time an animation state will take to execute.",
                "duration = 0.5",
            ),
            "delay": (
                "purple",
                "Add a delay before an animation state is executed.",
                "delay = 0.3",
            ),
            "trigger_when": (
                "yellow",
                "Trigger state when condition is True.",
                'trigger_when = "&#60;triggers&#62;"',
            ),
            "trigger_on_create ": (
                "yellow",
                "Trigger state when the element becomes visible.",
                "trigger_on_create = yes",
            ),
            "on_start": (
                "red",
                "Run effect when state starts.",
                'on_start = "&#60;effects&#62;"',
            ),
            "on_finish": (
                "red",
                "Run effect when state ends.",
                'on_finish = "&#60;effects&#62;"',
            ),
            "next": (
                "red",
                "Executes another named state in the same element after this one is finished.",
                'next = "state_name"',
            ),
            "start_sound": (
                "red",
                "Sound to play when animation starts.",
                'start_sound  = {\n\tsoundeffect = "x"\n}',
            ),
            "_show": (
                "blue",
                "A state with this name will run its effect when the element becomes visible.",
                "",
            ),
            "_hide": (
                "blue",
                "A state with this name will run its effect when the element is hidden.",
                "",
            ),
            "_mouse_enter": (
                "blue",
                "A state with this name will run its effect when the mouse is hovered over the element.",
                "",
            ),
            "_mouse_leave": (
                "blue",
                "A state with this name will run its effect when the mouse leaves the element.",
                "",
            ),
            # Texture Properties
            "texture": (
                "purple",
                "Path to a texture or a function that returns a texture.",
                'texture = "x"',
            ),
            "frame": ("blue", "Points to the given frame (0-indexed).", "frame = 5"),
            "framesize": (
                "blue",
                "Subdivides the texture into frames, based on the given dimensions (a 250 by 50 texture will by made into 5 frames left-to-right).",
                "framesize = { 50 50 }",
            ),
            "upframe": (
                "blue",
                "Frame to use when a button is clicked and released.",
                "upframe = 1",
            ),
            "overframe": (
                "blue",
                "Frame to use when a button is hovered over.",
                "overframe = 2",
            ),
            "downframe": (
                "blue",
                "Frame to use when a button is pressed down.",
                "downframe = 3",
            ),
            "disableframe": (
                "blue",
                "Frame to use when a button is disabled.",
                "disableframe = 4",
            ),
            "blend_mode": (
                "blue",
                "Modify texture blend mode.",
                "blend_mode = multiply/add/overlay/colordodge/lighten/darken/alphamultiply/mask",
            ),
            "shaderfile": (
                "purple",
                "Shader file that is used to render the element.",
                'shaderfile = "x"',
            ),
            "effectname": (
                "blue",
                "The effect in the shader file that is used to render the element.",
                'effectname = "x"',
            ),
            "gfxtype": (
                "purple",
                "The gfx type to use for the element. All gfxtype's are hard-coded, but you should always try to use the correct one for the element that is being used so it will render correctly.",
                'gfxtype = "x"',
            ),
            "portrait_texture": (
                "purple",
                "Texture to use for a portrait, usually takes the GetPortrait function.",
                "portrait_texture = \"[Character.GetPortrait('default', 'looking_right')]\"",
            ),
            "progresstexture": (
                "purple",
                "Texture to use for a progress bar.",
                'progresstexture = "x"',
            ),
            # Sound Properties
            "clicksound": (
                "orange",
                "Sound played when a button is clicked.",
                'clicksound = "x"',
            ),
            "oversound": (
                "orange",
                "Sound played when an element is hovered over, only works with some elements.",
                'oversound = "x"',
            ),
            "soundeffect": (
                "orange",
                "Sound to play inside of a start_sound block of an animation.",
                'soundeffect = "x"',
            ),
        }

import os
import struct
from typing import Set
from abc import ABC, abstractmethod

import sublime

from .utils import get_syntax_name, IterViews


def get_views_with_shown_textures() -> Set[sublime.View]:
    views_with_shown_textures = set()
    for view in IterViews(sublime.windows()):
        if hasattr(view, "textures"):
            views_with_shown_textures.add(view)
    return views_with_shown_textures


class JominiShowTextureBase:
    conversion_iterations = 0
    total_conversion_attempts = 2 if sublime.platform() == "linux" else 6

    def show_texture(self, path: str, point: int):
        window = sublime.active_window()
        simple_path = (
            path.replace("\\", "/")
            .rstrip("/")
            .rpartition("/")[2]
            .replace(".dds", ".png")
        )
        output_file = os.path.join(sublime.cache_path(), simple_path)
        if not os.path.exists(output_file):
            cmd = ["magick", path, output_file]
            window.run_command("quiet_execute", {"cmd": cmd})
            window.destroy_output_panel("exec")
            # Wait 750ms for conversion to finish
            timeout = 500
            sublime.set_timeout_async(
                lambda: self.toggle_async(
                    output_file, simple_path, point, window, path
                ),
                timeout,
            )
        else:
            self.toggle_async(output_file, simple_path, point, window, path)

    def toggle_async(
        self,
        output_file: str,
        simple_path: str,
        point: int,
        window: sublime.Window,
        original_path: str,
    ):
        # Try to convert for 750ms
        if (
            not os.path.exists(output_file)
            and self.conversion_iterations < self.total_conversion_attempts
        ):
            self.conversion_iterations += 1
            self.show_texture(original_path, point)
        elif os.path.exists(output_file):
            self.conversion_iterations = 0
            image = f"file://{output_file}"
            dimensions = self.get_png_dimensions(output_file)
            width = dimensions[0]
            height = dimensions[1]
            html = f'<img src="{image}" width="{width}" height="{height}">'
            view = window.active_view()
            if view is None:
                return

            if os.path.exists(output_file):
                self.toggle(simple_path, view, html, point)

    def toggle(self, key: str, view: sublime.View, html: str, point: int):
        pid = key + "|" + str(view.rowcol(point)[0] + 1)
        if hasattr(view, "textures"):
            view.textures.add(view.id())  # type: ignore
        else:
            setattr(view, "textures", [view.id()])
        views_with_shown_textures = get_views_with_shown_textures()
        x = [v for v in views_with_shown_textures if v.id() == view.id()]
        current_view = ""
        if x:
            current_view = x[0]
        current_view = view  # TODO - important this is bugged and this is a very dumb workaround, need to fix so inline images actually get removed when toggled.
        if not current_view or not hasattr(current_view, "textures"):
            return
        if pid in current_view.textures:  # type: ignore
            current_view.textures.remove(pid)  # type: ignore
            view.erase_phantoms(key)
        else:
            current_view.textures.append(pid)  # type: ignore
            line_region = view.line(point)
            # Find region of texture path declaration
            # Ex: [start]texture = "gfx/interface/icons/goods_icons/meat.dds"[end]
            start = view.find(
                r'[A-Za-z_][A-Za-z_0-9]*\s?=\s?"?/?(gfx)?', line_region.a
            ).a
            end = view.find('"|\n', start).a
            phantom_region = sublime.Region(start, end)
            view.add_phantom(key, phantom_region, html, sublime.LAYOUT_BELOW)

    def get_png_dimensions(self, path: str):
        height = 150
        width = 150
        file = open(path, "rb")
        try:
            head = file.read(31)
            size = len(head)
            if (
                size >= 24
                and head.startswith(b"\211PNG\r\n\032\n")
                and head[12:16] == b"IHDR"
            ):
                try:
                    width, height = struct.unpack(">LL", head[16:24])
                except struct.error:
                    pass
            elif size >= 16 and head.startswith(b"\211PNG\r\n\032\n"):
                try:
                    width, height = struct.unpack(">LL", head[8:16])
                except struct.error:
                    pass
        finally:
            file.close()

        # Scale down so image doens't take up entire viewport
        if width > 150 and height > 150:
            width /= 1.75
            height /= 1.75
        return int(width), int(height)


class JominiShowAllTexturesCommand(JominiShowTextureBase):
    def _run(self, window: sublime.Window, settings: sublime.Settings):
        view = window.active_view()
        if view is None:
            return

        texture_list = [
            x
            for x in view.lines(sublime.Region(0, view.size()))
            if ".dds" in view.substr(x)
        ]
        game_files_path = settings.get("GameFilesPath")

        for line, i in zip(texture_list, range(settings.get("MaxToggleTextures"))):  # type: ignore
            texture_raw_start = view.find("gfx", line.a)
            texture_raw_end = view.find(".dds", line.a)
            texture_raw_region = sublime.Region(texture_raw_start.a, texture_raw_end.b)
            texture_raw_path = view.substr(texture_raw_region)
            full_texture_path = game_files_path + "/" + texture_raw_path  # type: ignore
            full_texture_path = full_texture_path.replace("\\", "/")
            self.show_texture(full_texture_path, texture_raw_start.a)


class JominiToggleAllTexturesCommand:
    def __init__(self):
        self.shown = False

    def _run(
        self,
        syntax_name="Imperator Script",
        show_all_command_name="imperator_show_all_textures",
    ):
        window = sublime.active_window()
        view = window.active_view()
        if not view:
            return None

        if get_syntax_name(view) != syntax_name:
            return None

        if self.shown or len(get_views_with_shown_textures()) > 0:
            self.shown = False
            window.run_command("jomini_clear_all_textures")
        else:
            self.shown = True
            window.run_command(show_all_command_name)


class JominiTextureEventListener(ABC):
    def init(
        self,
        settings: sublime.Settings,
        syntax_name="Imperator Script",
        show_all_command_name="imperator_show_all_textures",
    ):
        self.syntax_name = syntax_name
        self.settings = settings
        self.show_all_command_name = show_all_command_name

    @abstractmethod
    def on_post_text_command(self, view: sublime.View, command_name: str, args):
        if command_name in ("left_delete", "insert"):
            if view.file_name() and get_syntax_name(view) == self.syntax_name:
                views_with_shown_textures = get_views_with_shown_textures()
                x = [v for v in views_with_shown_textures if v.id() == view.id()]
                if x:
                    update_line_count(x[0], view.rowcol(view.size())[0] + 1)

    @abstractmethod
    def on_load_async(self, view: sublime.View):
        if not view:
            return

        if get_syntax_name(view) != self.syntax_name:
            return

        if self.settings.get("ShowInlineTexturesOnLoad"):
            sublime.active_window().run_command(self.show_all_command_name)


def update_line_count(view, new_count):
    diff = new_count - view.line_count
    view.line_count += diff
    to_update = []
    for i, tex in enumerate(view.textures):
        tex = tex.split("|")
        key = tex[0]
        line = int(tex[1])
        point = view.text_point(line, 1)
        if view.find(key, point):
            # Texture is still on the same line, dont need to update
            return
        else:
            current_selection_line = view.rowcol(view.sel()[0].a)[0] + 1
            if current_selection_line < line:
                line += diff
                out = key + "|" + str(line)
                to_update.append((i, out))
    for i in to_update:
        index = i[0]
        replacement = i[1]
        view.textures[index] = replacement

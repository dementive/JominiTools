"""
Various ST interfacing commands used for plugins
"""

import os

import Default.exec
import sublime
import sublime_plugin

from JominiTools.src import (
    JominiShowTextureBase,
    open_path,
    get_views_with_shown_textures,
)


class GotoScriptObjectDefinitionCommand(sublime_plugin.WindowCommand):
    def run(self, path: str, line: str):  # type: ignore
        if os.path.exists(path):
            file_path = "{}:{}:{}".format(path, line, 0)
            self.open_location(self.window, file_path)

    def open_location(self, window, line):
        flags = sublime.ENCODED_POSITION | sublime.FORCE_GROUP
        window.open_file(line, flags)


class GotoScriptObjectDefinitionRightCommand(sublime_plugin.WindowCommand):
    def run(self, path: str, line: str):  # type: ignore
        if os.path.exists(path):
            file_path = "{}:{}:{}".format(path, line, 0)
            self.open_location(
                self.window, file_path, side_by_side=True, clear_to_right=True
            )

    def open_location(
        self, window, location, side_by_side=False, replace=False, clear_to_right=False
    ):
        flags = sublime.ENCODED_POSITION | sublime.FORCE_GROUP

        if side_by_side:
            flags |= sublime.ADD_TO_SELECTION | sublime.SEMI_TRANSIENT
            if clear_to_right:
                flags |= sublime.CLEAR_TO_RIGHT

        elif replace:
            flags |= sublime.REPLACE_MRU | sublime.SEMI_TRANSIENT

        window.open_file(location, flags)


class QuietExecuteCommand(sublime_plugin.WindowCommand):
    """
    Simple version of Default.exec.py that only runs the process and shows no panel or messages
    """

    def __init__(self, window):
        super().__init__(window)
        self.proc = None

    def run(
        self,
        cmd=None,
        shell_cmd=None,
        working_dir="",
        encoding="utf-8",
        env={},
        **kwargs,
    ):
        self.encoding = encoding
        merged_env = env.copy()
        view = self.window.active_view()
        if view:
            user_env = view.settings().get("build_env")
            if user_env:
                merged_env.update(user_env)

        if working_dir != "":
            os.chdir(working_dir)

        try:
            # Run process
            self.proc = Default.exec.AsyncProcess(
                cmd, shell_cmd, merged_env, self, **kwargs
            )
            self.proc.start()
        except Exception:
            sublime.status_message("Build error")

    def on_data(self, proc, data):
        return

    def on_finished(self, proc):
        return


class JominiClearAllTexturesCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        keys = []
        views_with_shown_textures = get_views_with_shown_textures()
        for view in views_with_shown_textures:
            for i in view.textures:  # type: ignore
                tex = i.split("|")
                key = tex[0]
                keys.append(key)
        for view in sublime.active_window().views():
            for i in keys:
                view.erase_phantoms(i)
        views_with_shown_textures.clear()


class OpenJominiTextureCommand(sublime_plugin.WindowCommand):
    def run(self, path: str, folder=False, mode="default_program", point=0):  # type: ignore
        if folder:
            end = path.rfind("/")
            path = path[0:end:]
            open_path(path)
        else:
            if mode == "default_program":
                open_path(path)
            elif mode == "inline":
                cmd = JominiShowTextureCommand()
                cmd.show(path, point)
            elif mode == "in_sublime":
                simple_path = (
                    path.replace("\\", "/")
                    .rstrip("/")
                    .rpartition("/")[2]
                    .replace(".dds", ".png")
                )
                output_file = os.path.join(sublime.cache_path(), simple_path)

                if not os.path.exists(output_file):
                    # Run dds to png converter
                    cmd = ["magick", "convert", path, output_file]
                    self.window.run_command("quiet_execute", {"cmd": cmd})
                    self.window.destroy_output_panel("exec")
                    sublime.active_window().open_file(output_file)
                else:
                    # File is already in cache, don't need to convert
                    sublime.active_window().open_file(output_file)


class JominiShowTextureCommand(JominiShowTextureBase):
    def show(self, path: str, point: int):
        self.show_texture(path, point)

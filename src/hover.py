"""
Various features for showing information to the user when hovering over specific tokens.
Shows documentation for effects/triggers/scopes from the game logs in pop ups.
Also shows goto definition popups for all game objects as well as saved scopes and variables.
"""

import re
from typing import Any, Dict, Union

import sublime

from .css import CSS
from .jomini_objects import PdxColorObject
from .jomini import PdxScriptObject
from .utils import IterViews, get_file_name, get_syntax_name
from .game_data import JominiGameData


class Hover:
    def init_hover(
        self,
        script_syntax_name: str,
        localization_syntax_name: str,
    ):
        self.script_syntax_name = script_syntax_name
        self.localization_syntax_name = localization_syntax_name

    def show_hover_docs(
        self,
        view: sublime.View,
        point: int,
        scope: str,
        collection: Dict[Any, Any],
        settings: sublime.Settings,
    ):
        style = settings.get("DocsPopupStyle")
        if style == "dark":
            style = """
                        body {
                            font-family: system;
                            margin: 0;
                            padding: 0.35rem;
                            border: 0.2rem solid rgb(46, 46, 46);
                            background-color: rgb(5, 5, 5);
                        }
                        p {
                            font-size: 1.0rem;
                            margin: 0;
                        }
                    """
        elif style == "none":
            style = """
                        body {
                            font-family: system;
                        }
                        p {
                            font-size: 1.0rem;
                            margin: 0;
                        }
                    """
        elif style == "dynamic":
            if scope == "keyword.effect":
                style = """
                            body {
                                font-family: system;
                                margin: 0;
                                padding: 0.35rem;
                                border: 0.15rem solid rgb(128, 26, 0);
                                background-color: rgb(10, 10, 10);
                            }
                            p {
                                font-size: 1.0rem;
                                margin: 0;
                            }
                        """
            elif scope == "string.trigger" or scope == "string.modifier.type":
                style = """
                            body {
                                font-family: system;
                                margin: 0;
                                padding: 0.35rem;
                                border: 0.15rem solid rgb(123, 123, 0);
                                background-color: rgb(10, 10, 10);
                            }
                            p {
                                font-size: 1.0rem;
                                margin: 0;
                            }
                        """
            elif scope == "storage.type.scope":
                style = """
                            body {
                                font-family: system;
                                margin: 0;
                                padding: 0.35rem;
                                border: 0.15rem solid rgb(0, 122, 153);
                                background-color: rgb(10, 10, 10);
                            }
                            p {
                                font-size: 1.0rem;
                                margin: 0;
                            }
                        """
        item = view.substr(view.word(point))
        if item in collection:
            desc = collection[item]
            hover_body = """
                <body id="jomini-body">
                    <style>%s</style>
                    <p>%s</p>
                </body>
            """ % (
                style,
                desc,
            )

            view.show_popup(
                hover_body,
                flags=(
                    sublime.HIDE_ON_MOUSE_MOVE_AWAY
                    | sublime.COOPERATE_WITH_AUTO_COMPLETE
                    | sublime.HIDE_ON_CHARACTER_EVENT
                ),
                location=point,
                max_width=1024,
            )
            return

    def show_gui_docs_popup(
        self, view: sublime.View, point: int, item: str, GameData: JominiGameData
    ):
        data = GameData.gui_content[item]
        color = data[0]
        desc = data[1]
        example = data[2]
        if example:
            example = f'<div class="box-for-codebox"><div class="codebox"><code>{example}</code></div></div>'
        if item in example:
            if color == "green":
                example = example.replace(
                    item, f'<code class="green-text">{item}</code>'
                )
            if color == "red":
                example = example.replace(item, f'<code class="red-text">{item}</code>')
            if color == "yellow":
                example = example.replace(
                    item, f'<code class="yellow-text">{item}</code>'
                )
            if color == "blue":
                example = example.replace(
                    item, f'<code class="blue-text">{item}</code>'
                )
            if color == "purple":
                example = example.replace(
                    item, f'<code class="purple-text">{item}</code>'
                )
            if color == "orange":
                example = example.replace(
                    item, f'<code class="orange-text">{item}</code>'
                )

        if item == "template" or item == "using":
            template_example = '<div class="box-for-codebox"><div class="codebox code">template example_name {<br>&nbsp;&nbsp;&nbsp;&nbsp;size = { 50 50 }<br>}<br></div></div>'
            template_example = template_example.replace(
                "template", '<code class="purple-text">template</code>'
            )
            template_example_text = (
                '<p class="code-header">Example template definition:</p>'
            )
            template_example_text2 = (
                '<br><br><br><p class="code-header">Example template usage:</p>'
            )
            example = example.replace("using", '<code class="green-text">using</code>')
            example = (
                template_example_text
                + template_example
                + template_example_text2
                + example
            )

        if item == "block" or item == "blockoverride":
            block_example = '<div class="box-for-codebox"><div class="codebox code">block "example_name" {<br>&nbsp;&nbsp;&nbsp;&nbsp;visible = no<br>}<br></div></div>'
            block_example = block_example.replace(
                "block", '<code class="red-text">block</code>'
            )
            block_example_text = '<p class="code-header">Example block definition:</p>'
            block_example_text2 = (
                '<br><br><br><p class="code-header">Example blockoverride:</p>'
            )
            example = '<div class="box-for-codebox"><div class="codebox code">blockoverride "example_name" {<br>&nbsp;&nbsp;&nbsp;&nbsp;visible = yes<br>}<br></div></div>'
            example = example.replace(
                "blockoverride", '<code class="red-text">blockoverride</code>'
            )
            example = block_example_text + block_example + block_example_text2 + example

        if item == "type" or item == "types":
            example = '<div class="box-for-codebox"><div class="codebox code">types My_Types<br>{<br>&nbsp;&nbsp;&nbsp;&nbsp;type widget_with_size = widget {<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;size = { 50 50 }<br>&nbsp;&nbsp;&nbsp;&nbsp;}<br>}<br></div></div>'
            example = example.replace("types", '<code class="purple-text">types</code>')
            example = example.replace("type", '<code class="purple-text">type</code>')
            type_example_text = '<p class="code-header">Example type definition:</p>'
            example = type_example_text + example

        hoverBody = """
            <body id="vic-body">
                <style>%s</style>
                <p class=\"codedesc\">%s</p>
                %s
            </body>
        """ % (
            CSS().default,
            desc,
            example,
        )

        view.show_popup(
            hoverBody,
            flags=(
                sublime.HIDE_ON_MOUSE_MOVE_AWAY
                | sublime.COOPERATE_WITH_AUTO_COMPLETE
                | sublime.HIDE_ON_CHARACTER_EVENT
            ),
            location=point,
            max_width=1024,
        )

    def show_gui_popup(
        self, view: sublime.View, point: int, PdxObject: PdxScriptObject, header: str
    ):
        word_line_num = view.rowcol(point)[0] + 1
        word_file = (
            get_file_name(view).replace("\\", "/").rstrip("/").rpartition("/")[2]
        )
        definition = ""

        if word_line_num != PdxObject.line:
            definition = f'<p><b>Definition of&nbsp;&nbsp;</b><tt class="variable">{PdxObject.key}</tt></p>'
            goto_args = {"path": PdxObject.path, "line": PdxObject.line}
            goto_url = sublime.command_url("goto_script_object_definition", goto_args)
            definition += (
                """<a href="%s" title="Open %s and goto line %d">%s:%d</a>&nbsp;"""
                % (
                    goto_url,
                    PdxObject.path.replace("\\", "/").rstrip("/").rpartition("/")[2],
                    PdxObject.line,
                    PdxObject.path.replace("\\", "/").rstrip("/").rpartition("/")[2],
                    PdxObject.line,
                )
            )
            goto_right_args = {"path": PdxObject.path, "line": PdxObject.line}
            goto_right_url = sublime.command_url(
                "goto_script_object_definition_right", goto_right_args
            )
            definition += (
                """<a class="icon" href="%s"title="Open Tab to Right of Current Selection">◨</a>&nbsp;<br>"""
                % (goto_right_url)
            )

        references = []
        ref = ""
        for i in IterViews(sublime.windows()):
            if not get_file_name(i).endswith(".gui"):
                continue

            view_region = sublime.Region(0, i.size())
            view_str = i.substr(view_region)
            for j, line in enumerate(view_str.splitlines()):
                definition_found = False
                if PdxObject.key in line:
                    filename = (
                        get_file_name(view)
                        .replace("\\", "/")
                        .rstrip("/")
                        .rpartition("/")[2]
                    )
                    line_num = j + 1
                    if word_line_num == line_num and word_file == filename:
                        # Don't do current word
                        continue
                    elif line_num == PdxObject.line and i.file_name() == PdxObject.path:
                        # Don't do definition
                        continue
                    if not definition_found:
                        references.append(f"{i.file_name()}|{line_num}")

        if references:
            ref = f'<p><b>References to&nbsp;&nbsp;</b><tt class="variable">{PdxObject.key}</tt></p>'
            for j, i in enumerate(references):
                if j > 10:
                    break
                fname = i.split("|")[0]
                shortname = fname.replace("\\", "/").rstrip("/").rpartition("/")[2]
                line = i.split("|")[1]
                goto_args = {"path": fname, "line": line}
                goto_url = sublime.command_url(
                    "goto_script_object_definition", goto_args
                )
                ref += (
                    """<a href="%s" title="Open %s and goto line %s">%s:%s</a>&nbsp;"""
                    % (
                        goto_url,
                        shortname,
                        line,
                        shortname,
                        line,
                    )
                )
                goto_right_args = {"path": fname, "line": line}
                goto_right_url = sublime.command_url(
                    "goto_script_object_definition_right", goto_right_args
                )
                ref += (
                    """<a class="icon" href="%s"title="Open Tab to Right of Current Selection">◨</a>&nbsp;<br>"""
                    % (goto_right_url)
                )

        link = definition + ref
        if link:
            hoverBody = """
                <body id="vic-body">
                    <style>%s</style>
                    <h1>%s</h1>
                    %s
                </body>
            """ % (
                CSS().default,
                header,
                link,
            )

            view.show_popup(
                hoverBody,
                flags=(
                    sublime.HIDE_ON_MOUSE_MOVE_AWAY
                    | sublime.COOPERATE_WITH_AUTO_COMPLETE
                    | sublime.HIDE_ON_CHARACTER_EVENT
                ),
                location=point,
                max_width=1024,
            )

    def show_popup_default(
        self,
        view: sublime.View,
        point: int,
        PdxObject: PdxScriptObject,
        header: str,
    ):
        if view.file_name() is None:
            return

        link = self.get_definitions_for_popup(
            view, point, PdxObject, header
        ) + self.get_references_for_popup(view, point, PdxObject)
        if link:
            hover_body = """
                <body id="jomini-body">
                    <style>%s</style>
                    <h1>%s</h1>
                    %s
                </body>
            """ % (
                CSS().default,
                header,
                link,
            )

            view.show_popup(
                hover_body,
                flags=(
                    sublime.HIDE_ON_MOUSE_MOVE_AWAY
                    | sublime.COOPERATE_WITH_AUTO_COMPLETE
                    | sublime.HIDE_ON_CHARACTER_EVENT
                ),
                location=point,
                max_width=1024,
            )

    def handle_scripted_args(
        self, view: sublime.View, point: int, region=False
    ) -> Union[sublime.Region, str]:
        argument_found = True
        word = view.word(point)
        while argument_found is True:
            one_ahead = word.b
            one_behind = word.a - 1
            one_ahead_word = view.substr(one_ahead)
            one_behind_word = view.substr(one_behind)
            if one_ahead_word == "$":
                new_word = view.word(one_ahead + 1)
                word = sublime.Region(word.a, new_word.b)
            if one_behind_word == "$":
                new_word = view.word(one_behind)
                word = sublime.Region(new_word.a, word.b)
            if one_behind_word != "$" and one_ahead_word != "$":
                argument_found = False
        if region:
            return word

        return view.substr(word).strip()

    def get_definitions_for_popup(
        self,
        view: sublime.View,
        point: int,
        PdxObject: PdxScriptObject,
        header: str,
        def_value="",
    ):
        word_line_num = view.rowcol(point)[0] + 1
        definition = ""
        definitions = []
        if header == "Saved Scope" or header == "Saved Variable":
            for i in IterViews(sublime.windows()):
                if get_syntax_name(i) != self.script_syntax_name:
                    continue

                variables = [
                    self.handle_scripted_args(i, x.a, True)
                    for x in i.find_by_selector("entity.name.function.var.declaration")
                    if self.handle_scripted_args(i, x.a) == PdxObject.key
                ]
                variables.extend(
                    [
                        self.handle_scripted_args(i, x.a, True)
                        for x in i.find_by_selector(
                            "entity.name.function.scope.declaration"
                        )
                        if self.handle_scripted_args(i, x.a) == PdxObject.key
                    ]
                )
                for r in variables:
                    line = i.rowcol(r.a)[0] + 1  # type: ignore
                    path = get_file_name(i)
                    if line == word_line_num and path == PdxObject.path:
                        continue
                    else:
                        definitions.append(PdxScriptObject(PdxObject.key, path, line))

            if len(definitions) == 1:
                if def_value:
                    definition = f"<br>{def_value}<br><br>"
                    definition += f'<p><b>Definition of&nbsp;&nbsp;</b><tt class="variable">{PdxObject.key}</tt></p>'
                else:
                    definition = f'<p><b>Definition of&nbsp;&nbsp;</b><tt class="variable">{PdxObject.key}</tt></p>'
            elif len(definitions) > 1:
                if def_value:
                    definition = f"<br>{def_value}<br><br>"
                    definition += f'<p><b>Definitions of&nbsp;&nbsp;</b><tt class="variable">{PdxObject.key}</tt></p>'
                else:
                    definition = f'<p><b>Definitions of&nbsp;&nbsp;</b><tt class="variable">{PdxObject.key}</tt></p>'
            for obj in definitions:
                goto_args = {"path": obj.path, "line": obj.line}
                goto_url = sublime.command_url(
                    "goto_script_object_definition", goto_args
                )
                definition += (
                    """<a href="%s" title="Open %s and goto line %d">%s:%d</a>&nbsp;"""
                    % (
                        goto_url,
                        obj.path.replace("\\", "/").rstrip("/").rpartition("/")[2],
                        obj.line,
                        obj.path.replace("\\", "/").rstrip("/").rpartition("/")[2],
                        obj.line,
                    )
                )
                goto_right_args = {"path": obj.path, "line": obj.line}
                goto_right_url = sublime.command_url(
                    "goto_script_object_definition_right", goto_right_args
                )
                definition += (
                    """<a class="icon" href="%s"title="Open Tab to Right of Current Selection">◨</a>&nbsp;<br>"""
                    % (goto_right_url)
                )
                return definition

        if word_line_num != PdxObject.line:
            if def_value:
                definition = f"<br>{def_value}<br><br>"
                definition += f'<p><b>Definition of&nbsp;&nbsp;</b><tt class="variable">{PdxObject.key}</tt></p>'
            else:
                definition = f'<p><b>Definition of&nbsp;&nbsp;</b><tt class="variable">{PdxObject.key}</tt></p>'
            goto_args = {"path": PdxObject.path, "line": PdxObject.line}
            goto_url = sublime.command_url("goto_script_object_definition", goto_args)
            definition += (
                """<a href="%s" title="Open %s and goto line %d">%s:%d</a>&nbsp;"""
                % (
                    goto_url,
                    PdxObject.path.replace("\\", "/").rstrip("/").rpartition("/")[2],
                    PdxObject.line,
                    PdxObject.path.replace("\\", "/").rstrip("/").rpartition("/")[2],
                    PdxObject.line,
                )
            )
            goto_right_args = {"path": PdxObject.path, "line": PdxObject.line}
            goto_right_url = sublime.command_url(
                "goto_script_object_definition_right", goto_right_args
            )
            definition += (
                """<a class="icon" href="%s"title="Open Tab to Right of Current Selection">◨</a>&nbsp;<br>"""
                % (goto_right_url)
            )

        return definition

    def get_references_for_popup(
        self, view: sublime.View, point: int, PdxObject: PdxScriptObject
    ):
        word_line_num = view.rowcol(point)[0] + 1
        filename = view.file_name()
        if filename is None:
            return ""
        word_file = filename.replace("\\", "/").rstrip("/").rpartition("/")[2]
        references = []
        ref = ""
        for i in IterViews(sublime.windows()):
            syntax_name = get_syntax_name(i)
            if (
                syntax_name != self.script_syntax_name
                and syntax_name != self.localization_syntax_name
            ):
                continue
            view_region = sublime.Region(0, i.size())
            view_str = i.substr(view_region)
            for j, line in enumerate(view_str.splitlines()):
                if re.search(r"\b" + re.escape(PdxObject.key) + r"\b", line):
                    filename = i.file_name()
                    if filename is None:
                        continue
                    filename = (
                        filename.replace("\\", "/").rstrip("/").rpartition("/")[2]
                    )
                    line_num = j + 1
                    if word_line_num == line_num and word_file == filename:
                        # Don't do current word
                        continue
                    elif line_num == PdxObject.line and i.file_name() == PdxObject.path:
                        # Don't do definition
                        continue
                    else:
                        references.append(f"{i.file_name()}|{line_num}")
        if references:
            ref = f'<p><b>References to&nbsp;&nbsp;</b><tt class="variable">{PdxObject.key}</tt></p>'
            for i in references:
                fname = i.split("|")[0]
                shortname = fname.replace("\\", "/").rstrip("/").rpartition("/")[2]
                line = i.split("|")[1]
                goto_args = {"path": fname, "line": line}
                goto_url = sublime.command_url(
                    "goto_script_object_definition", goto_args
                )
                ref += (
                    """<a href="%s" title="Open %s and goto line %s">%s:%s</a>&nbsp;"""
                    % (
                        goto_url,
                        shortname,
                        line,
                        shortname,
                        line,
                    )
                )
                goto_right_args = {"path": fname, "line": line}
                goto_right_url = sublime.command_url(
                    "goto_script_object_definition_right", goto_right_args
                )
                ref += (
                    """<a class="icon" href="%s"title="Open Tab to Right of Current Selection">◨</a>&nbsp;<br>"""
                    % (goto_right_url)
                )

        return ref

    def show_texture_hover_popup(
        self, view: sublime.View, point: int, texture_name: str, full_texture_path: str
    ):
        args = {"path": full_texture_path}
        open_texture_url = sublime.command_url("open_jomini_texture ", args)  # type: ignore
        folder_args = {"path": full_texture_path, "folder": True}
        open_folder_url = sublime.command_url("open_jomini_texture ", folder_args)
        in_sublime_args = {"path": full_texture_path, "mode": "in_sublime"}
        inline_args = {"path": full_texture_path, "mode": "inline", "point": point}
        open_in_sublime_url = sublime.command_url(
            "open_jomini_texture",
            in_sublime_args,  # type: ignore
        )
        open_inline_url = sublime.command_url("open_jomini_texture ", inline_args)
        hover_body = """
            <body id=\"jomini-body\">
                <style>%s</style>
                <h1>Open Texture</h1>
                <div></div>
                <a href="%s" title="Open folder containing the texture.">Open Folder</a>
                <br>
                <a href="%s" title="Open %s in the default program">Open in default program</a>
                <br>
                <a href="%s" title="Open %s in sublime">Open in sublime</a>
                <br>
                <a href="%s" title="Show %s at current selection">Show Inline</a>
            </body>
        """ % (
            CSS().default,
            open_folder_url,
            open_texture_url,
            texture_name,
            open_in_sublime_url,
            texture_name,
            open_inline_url,
            texture_name,
        )

        view.show_popup(
            hover_body,
            flags=(
                sublime.HIDE_ON_MOUSE_MOVE_AWAY
                | sublime.COOPERATE_WITH_AUTO_COMPLETE
                | sublime.HIDE_ON_CHARACTER_EVENT
            ),
            location=point,
            max_width=802,
        )

    def show_popup_named_color(
        self,
        view: sublime.View,
        point: int,
        word: str,
        PdxObject: PdxColorObject,
        header: str,
    ):
        if view.file_name() is None:
            return

        object_color = PdxObject.color
        css_color = PdxObject.rgb_color

        r = css_color[0]
        g = css_color[1]
        b = css_color[2]
        icon_color = f"rgb({r},{g},{b})"
        color = f'<a class="icon"style="color:{icon_color}">■</a>\t\t\t<code>{object_color}</code>'

        link = self.get_definitions_for_popup(view, point, PdxObject, header, color)
        if link:
            hover_body = """
                <body id="jomini-body">
                    <style>%s</style>
                    <h1>%s</h1>
                    %s
                </body>
            """ % (
                CSS().default,
                header,
                link,
            )

            view.show_popup(
                hover_body,
                flags=(
                    sublime.HIDE_ON_MOUSE_MOVE_AWAY
                    | sublime.COOPERATE_WITH_AUTO_COMPLETE
                    | sublime.HIDE_ON_CHARACTER_EVENT
                ),
                location=point,
                max_width=1024,
            )

import re
import sublime, sublime_plugin
import subprocess

from .edit import Edit
from . import common
from . import shell

def fix_scroll(view, sel, line):
    view.show(sel, False)

def stish_exec(view, cont=False):
    sel = view.sel()
    cur = sel[0].b
    if 'meta.stish.prompt' in view.scope_name(cur):
        # TODO: line continuations?
        # pressing \ at the end of a line could automatically dump you on the next line indented
        line = view.line(cur)
        match = re.match(r'\$\s*(.*)$', view.substr(line))
        cmd = None
        if match:
            cmd = match.group(1)

        if cmd is None or not cmd.strip():
            with Edit(view) as edit:
                edit.insert(line.b, '\n')
            sel.clear()
            sel.add(line.b + 1)
            fix_scroll(view, sel, line)
        else:
            text = shell.run(cmd)
            if text.strip():
                text = '\n' + text
            # TODO: generic "add text and fix cursor"?
            # or just do this all independently of cursor and catch up later
            with Edit(view) as edit:
                edit.insert(line.b, text)
            sel.clear()
            sel.add(line.b + len(text))
            fix_scroll(view, sel, line)

        # if not cont, need to wait until command is done printing
        # this depends on async output really
        if cont or True:
            common.new_prompt(view)

class StishPromptListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'stish-prompt' and common.is_stish_view(view):
            sel = view.sel()
            if len(sel) == 1:
                if 'meta.stish.prompt' in view.scope_name(sel[0].b):
                    return True
            return False

class StishExec(sublime_plugin.TextCommand):
    def run(self, edit):
        stish_exec(self.view, cont=False)

class StishExecContinue(sublime_plugin.TextCommand):
    def run(self, edit):
        stish_exec(self.view, cont=True)

class StishPromptSkip(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sel = view.sel()
        line = view.line(sel[0].b)
        sel.clear()
        with Edit(view) as edit:
            edit.insert(line.b, '\n')
        sel.add(line.b + 1)
        common.new_prompt(view)

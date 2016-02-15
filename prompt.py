import re
import sublime, sublime_plugin
import subprocess
from .edit import Edit
from . import common

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

        if cmd is None:
            with Edit(view) as edit:
                edit.insert(line.b, '\n')
            sel.clear()
            sel.add(cur + 1)
        else:
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out, err = p.communicate('')
            text = '\n' + ((out.decode('utf8', 'replace') or '') + (err.decode('utf8', 'replace') or '')).strip() + '\n'
            # TODO: generic "add text and fix cursor"?
            # or just do this all independently of cursor and catch up later
            with Edit(view) as edit:
                edit.insert(line.b, text)
            sel.clear()
            sel.add(cur + len(text))

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

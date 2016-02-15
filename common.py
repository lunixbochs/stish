import sublime, sublime_plugin
import re
from .edit import Edit

def is_stish_view(view):
    if view is None or not view.settings().has('syntax'):
        return False
    return view.settings().get('syntax').endswith('/stish.tmLanguage')

def new_prompt(view):
    view.run_command('single_selection')
    sel = view.sel()
    pos = sel[0].a
    with Edit(view) as edit: 
        edit.insert(pos, '$ ') 
    sel.clear()
    sel.add(pos + 2)

class StishPromptListener(sublime_plugin.EventListener):
    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'stish-prompt' and is_stish_view(view):
            sel = view.sel()
            if len(sel) == 1:
                if 'meta.stish.prompt' in view.scope_name(sel[0].b):
                    return True
            return False

class StishExec(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sel = view.sel()
        cur = sel[0].b
        if 'meta.stish.prompt' in view.scope_name(cur):
            # TODO: line continuations?
            # pressing \ at the end of a line could automatically dump you on the next line indented
            line = view.line(cur)
            match = re.match(r'\$\s*(.*)$', view.substr(line))
            if match:
                cmd = match.group(1)
                text = '\n' + cmd + '\n'
            else:
                text = '\n'

            with Edit(view) as edit:
                edit.insert(line.b, text)
            sel.clear()
            sel.add(cur + len(text))
            new_prompt(view)

class StishPromptSkip(sublime_plugin.TextCommand):
    def run(self, edit):
        print('prompt skip')
        view = self.view
        sel = view.sel()
        sel.clear()
        line = view.line(view.sel()[0].b)
        sel.add(line.b)
        new_prompt(view)

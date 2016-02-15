import sublime, sublime_plugin

from .edit import Edit
from . import common

def apply_stish_settings(view):
    settings = view.settings()
    settings.set('tab_size', 2)
    settings.set('translate_tabs_to_spaces', True)
    settings.set('syntax', 'Packages/stish/stish.tmLanguage')

def setup_stish_view(view):
    apply_stish_settings(view)
    common.new_prompt(view)
    '''
    view.add_regions(
        'stish-<pid>',
        view.lines(sublime.Region(0, view.size())),
        'stish-interact', 'Packages/stish/vt-inactive.png',
        sublime.HIDDEN,
    )
    '''

class NewStish(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.new_file()
        setup_stish_view(view)

class StishKeypress(sublime_plugin.TextCommand):
    def run(self, edit, key):
        print('captured key', key)

class StishListener(sublime_plugin.EventListener):
    def on_load(self, view):
        if is_stish_view(view):
            apply_stish_settings(view)

    def on_query_context(self, view, key, operator, operand, match_all):
        if key == 'stish-interact' and is_stish_view(view):
            # TODO: see if we're in a stish interactive output region?
            return False

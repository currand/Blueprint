import os
import re
from jinja2 import Environment

class RelEnvironment(Environment):
    """Override join_path() to enable relative template paths."""
    def join_path(self, template, parent):
        return os.path.join(os.path.dirname(parent), template)

def junos_indent(template):
    '''
    A function to strip whitespace and indent templates
    in a JUNOS style
    '''
    indent = -1
    indent_re = re.compile('^\s?.*(?<!\{)\{(?!\{)\s?$')
    outdent_re = re.compile('(?<!\})\}(?!\})\s?')

    lines = template.split('\n')
    lines = [x for x in lines if x.strip() != '']
    for i in range(0, len(lines)):
        lines[i] = lines[i].lstrip()
        if indent_re.match(lines[i]):
            indent = indent + 1
            lines[i] = "    " * indent + lines[i]
        elif outdent_re.match(lines[i]):
            lines[i] = "    " * indent + lines[i]
            indent = indent - 1
        else:
            lines[i] = "    " * indent + "    " + lines[i]

    return '\n'.join(lines)
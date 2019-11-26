import os
import re
import csv
import sys
import yaml
import json
from jinja2 import Environment

class RelEnvironment(Environment): #pragma no coverage
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

def yaml_join(loader, node):
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])

def csv_load(template_dir, values):
    config = {}

    if os.path.exists(values) is False:
        values = os.path.join(template_dir, values)
        if os.path.exists(values) is False:
            sys.exit(f'File {values} does not exist')

    with open(values, newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        config['data'] = [dict(d) for d in csv_reader]

    return config

def yaml_load(template_dir, values):

    if os.path.exists(values) is False:
        values = os.path.join(template_dir, values)
        if os.path.exists(values) is False:
            sys.exit(f'File {values} does not exist')
    
    
    with open(values, 'r') as fh:
        lines = ''.join(fh.readlines())            

        

    yaml.add_constructor('!join', yaml_join)
    config = yaml.load(lines, Loader=yaml.Loader)
    return config
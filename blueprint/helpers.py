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
    """A function to strip whitespace and indent JUNOS stype
    
    Arguments:
        template {str} -- The input template (rendered or not) as a string
    
    Returns:
        str -- The indented template
    """
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
    """Load a YAML config file. Adds a construct_squence that will
    join values from a previous node. This enables reuse of a previously
    set variable. For example:

    REGION: &REGION 2
    HOSTNAME_FULL: &HOSTNAME_FULL arr01.fake.wv
    DESCRIPTION: !join ['_LB_, ', *HOSTNAME_FULL,' ', *REGION]

    will render:

    '_LB_,  arr01.fake.wv, 2'
    """
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
    """Load config values from a YAML file
    
    Arguments:
        template_dir {str} -- The base template dir
        values {str} -- The config file name
    
    Returns:
        dict -- A dict of values
    """

    if os.path.exists(values) is False:
        values = os.path.join(template_dir, values)
        if os.path.exists(values) is False:
            sys.exit(f'File {values} does not exist')
    
    
    with open(values, 'r') as fh:
        lines = ''.join(fh.readlines())            

    yaml.add_constructor('!join', yaml_join)
    config = yaml.load(lines, Loader=yaml.Loader)
    return config
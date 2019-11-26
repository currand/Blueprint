import argparse
import json
from blueprint import Blueprint, junos_indent
    

parser = argparse.ArgumentParser()
exclusive1 = parser.add_argument_group('output types')
group1 = exclusive1.add_mutually_exclusive_group()

parser.add_argument('-t', '--template-dir', help='Location of Blueprints', required=True)
parser.add_argument('-b', '--base-template', help='The base template', required=False,
                    default='base.j2')
parser.add_argument('-e', '--template-ext', help='Template extension. Default = ".j2"',
                    default='.j2')

parser.add_argument('-s', '--stream-only', action='store_true',
                    help='Produce an unrendered single Jinja template')
group1.add_argument('--comments', action='store_true',
                    help='Include comments when using --stream-only', default=False)
group1.add_argument('-v', '--get-vars', help='Return variables for a rendered template',
                    action='store_true')
group1.add_argument('-j', '--json-schema', help='Return schema of variables for a rendered template',
                    action='store_true')
parser.add_argument('-c', '--config-vars',
                    help='A CSV or YAML file containing config variables. Must end in either .csv or .yaml',
                    default='base.yaml', nargs='?')

args = parser.parse_args()

bp = Blueprint(template_dir=args.template_dir, base_template=args.base_template, values=args.config_vars)

if args.comments is True and args.stream_only is False:
    parser.error('--comments requires -s/--stream-only')

try:
    if args.stream_only is True:
        print(junos_indent(bp.get_stream(comments=args.comments)))
    elif args.get_vars is True:
        print(bp.get_variables())
    elif args.json_schema is True:
        schema = bp.get_json_schema()
        print(json.dumps(schema, sort_keys=True ,indent=2))
    else:
        if args.config_vars:
            rendered = bp.render_template()
            print(junos_indent(rendered))
        else:
            rendered = bp.render_template()
            print(junos_indent(rendered))
            
except FileNotFoundError as error:
    print(error)
import argparse
import re
import os
import json
from jinja2schema import infer_from_ast, to_json_schema, parse
from jinja2 import FileSystemLoader, FunctionLoader, meta
from helpers import RelEnvironment, junos_indent

class Blueprint():

    def __init__(self, template_dir='./templates', template_suffix='.j2',
                base_template='base.j2'):
        
        self.template_dir = template_dir
        self.template_suffix = template_suffix
        self.base_template = base_template

        self.env = RelEnvironment(
            loader=FileSystemLoader(self.template_dir)
        )

        self.templates = self.env.list_templates(
                filter_func=self._check_template_suffix
            )
        self._stream_out = None

    def _check_template_suffix(self, name):
        # Filter function for template loader
        if self.template_suffix in name:
            return True


    def _build_stream(self, base_template):
        """
        Recursive method to build an unrendered single template from all
        sub templates included.
        """

        parent = False

        if self._stream_out is None:
            self._stream_out = []
            parent = True

        include_re = re.compile('^.*\{\%\-?\s+include\s+[\'\"]/(.*)[\"\'].*$', re.IGNORECASE)

        with open(os.path.join(self.template_dir,base_template), 
                                'r') as base_fh:
            base_template = base_fh.readlines()

        for b_line in base_template:
            b_line.rstrip()
            matches = include_re.match(b_line)
            if matches is not None:
                self._build_stream(matches.group(1))
            else:
                self._stream_out.append(b_line)

        if parent is True:
            output =  '\n'.join(self._stream_out)
            self._stream_out = None
            return output

    def get_stream(self, base_template=None):
        # External callable to build an unrendered scomplete
        # template
        if base_template is None:
            base_template = self.base_template

        return self._build_stream(base_template)

    def render_template(self, **kwargs):
        template = self.env.get_template(self.base_template)
        return template.render(kwargs)

    def get_variables(self, ignore_constants=True):
        template = self._build_stream(self.base_template)
        output = infer_from_ast(parse(template), ignore_constants=ignore_constants)
        return output

    def get_json_schema(self, ignore_constants=True):
        template = self._build_stream(self.base_template)
        out = to_json_schema(infer_from_ast(parse(template),
                             ignore_constants=ignore_constants)
        )
        return out['properties']

if __name__ == '__main__': #pragma no coverage

    parser = argparse.ArgumentParser()
    exclusive = parser.add_argument_group('output types')
    group1 = exclusive.add_mutually_exclusive_group()
    parser.add_argument('-t', '--template-dir', help='Location of Blueprints', required=True)
    parser.add_argument('-b', '--base-template', help='The base template', required=True)
    group1.add_argument('-s', '--stream-only', action='store_true',
                        help='Produce an unrendered single Jinja template'
    )
    parser.add_argument('-e', '--template-ext', help='Template extension. Default = ".j2"',
                        default='.j2'
    )
    group1.add_argument('-v', '--get-vars', help='Return variables for a rendered template',
                        action='store_true'
    )
    group1.add_argument('-j', '--json-schema', help='Return schema of variables for a rendered template',
                        action='store_true'
    )

    args = parser.parse_args()

    bp = Blueprint(template_dir=args.template_dir, base_template=args.base_template)

    try:
        if args.stream_only is True:
            print(junos_indent(bp.get_stream()))
        elif args.get_vars is True:
            print(bp.get_variables())
        elif args.json_schema is True:
            print(json.dumps(bp.get_json_schema(), sort_keys=True ,indent=2))
        else:
            rendered = bp.render_template()
            print(junos_indent(rendered))
    except FileNotFoundError:
        print(f'{args.template_dir}/{args.base_template} not found')
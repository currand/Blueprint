import re
import os
import json
import argparse
from jinja2schema import Config, infer_from_ast, to_json_schema, parse
from jinja2 import FileSystemLoader, FunctionLoader, meta, select_autoescape
from .helpers import RelEnvironment, junos_indent, yaml_load, csv_load

class Blueprint():

    def __init__(self, template_dir='./templates', template_suffix='.j2',
                base_template='base.j2', values='base.yaml'):
        
        self.template_dir = template_dir
        self.template_suffix = template_suffix
        self.base_template = base_template
        self.values = values

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


    def _build_stream(self, base_template, comments=False):
        """
        Recursive method to build an unrendered single template from all
        sub templates included.
        """

        parent = False

        if self._stream_out is None:
            self._stream_out = []
            parent = True

        include_re = re.compile('^.*\{\%\-?\s+include\s+[\'\"]/(.*)[\"\'].*$', re.IGNORECASE)
        comment_re = re.compile('\{#[\s\w]+#\}')

        with open(os.path.join(self.template_dir,base_template), 
                                'r') as base_fh:
            base_template = base_fh.read()

        if comments is False:
            base_template = re.sub(comment_re, '', base_template)            
        
        base_template = base_template.split('\n')

        for b_line in base_template:
            # b_line.rstrip()
            matches = include_re.match(b_line)
            if matches is not None:
                self._build_stream(matches.group(1))
            else:
                self._stream_out.append(b_line)

        if parent is True:
            output =  '\n'.join(self._stream_out)
            self._stream_out = None
            return output

    def get_stream(self, base_template=None, comments=False):
        # External callable to build an unrendered scomplete
        # template
        if base_template is None:
            base_template = self.base_template

        return self._build_stream(base_template, comments)

    def render_template(self):
        filetype = self.values.split('.')

        if filetype[-1] == 'yaml':
            args = yaml_load(self.template_dir, self.values)
        elif filetype[1] == 'csv':
            args = csv_load(self.template_dir, self.values)
    
        template = self.env.get_template(self.base_template)
        return template.render(args)

    def get_variables(self, ignore_constants=True):
        j2s_config = Config(BOOLEAN_CONDITIONS=True)
        template = self._build_stream(self.base_template)
        output = infer_from_ast(parse(template),
            ignore_constants=ignore_constants,
            config=j2s_config)
        return output

    def get_json_schema(self, ignore_constants=True):
        j2s_config = Config(BOOLEAN_CONDITIONS=True)
        template = self._build_stream(self.base_template)
        out = to_json_schema(infer_from_ast(parse(template),
                             ignore_constants=ignore_constants,
                             config=j2s_config)
        )
        return out['properties']

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
        """A Blueprint class to render templates based on Jinja
        
        Keyword Arguments:
            template_dir {str} -- The base template directory (default: {'./templates'})
            template_suffix {str} -- The template suffix (default: {'.j2'})
            base_template {str} -- The base Jinja template (default: {'base.j2'})
            values {str} -- A confg file to render a Blueprint template (default: {'base.yaml'})
        """
        
        self.template_dir = template_dir
        self.template_suffix = template_suffix
        self.base_template = base_template
        self.values = values

        self.env = RelEnvironment(
            loader=FileSystemLoader(self.template_dir),
            extensions=['jinja2_time.TimeExtension']
        )

        self.templates = self.env.list_templates(
                filter_func=self._check_template_suffix
            )
        self._stream_out = None

    def _check_template_suffix(self, name):
        """A filter function for Jinja template loader. When used
        Jinja will only return templates with the suffix provided,
        ignoring any other files (like YAML or other artifacts)
        
        Arguments:
            name {str} -- Template suffix
        
        Returns:
            bool -- Returns true if the suffix is in the template name
        """
        if self.template_suffix in name:
            return True


    def _build_stream(self, base_template, comments=False):
        """Recursive method to build an unrendered single template from all
        sub templates included. Recursivley combines templates from sub-dirs
        and removes comments from headers and in line where applicable
        
        Arguments:
            base_template {str} -- The base template
        
        Keyword Arguments:
            comments {bool} -- Whether to render comments or not (default: {False})
        
        Returns:
            {str} -- Return the rendered single template 
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
        """Output only the stream and do not render variables. This
        can also render a single template or templates starting farther
        down in the tree than the base template
        
        Keyword Arguments:
            base_template {str} -- The base template if different from the default (default: {None})
            comments {bool} -- Renders comments if True (default: {False})
        
        Returns:
            {str} -- Returns a "stream" or unrendered template
        """
        if base_template is None:
            base_template = self.base_template

        return self._build_stream(base_template, comments)

    def render_template(self, args=None):
        """Renders a template with supplied arguments. The arguments can
        either come from a supplied file or via a dict
        
        Keyword Arguments:
            args {dict} -- An arguments dict (default: {None})
        
        Returns:
            str -- A rendered template
        """

        if args is None:
            filetype = self.values.split('.')
            if filetype[-1] == 'yaml':
                args = yaml_load(self.template_dir, self.values)
            elif filetype[1] == 'csv':
                args = csv_load(self.template_dir, self.values)
    
        template = self.env.get_template(self.base_template)
        return template.render(args)

    def get_variables(self, ignore_constants=True):
        """Uses the json2schema library to find all variables in a
        template and attempt to infer a type.
        
        Keyword Arguments:
            ignore_constants {bool} -- Ignoring constants prevents printing of loop controls, etc. (default: {True})
        
        Returns:
            {str} -- A list of Variables found in the template. Useful for building config files
        """
        j2s_config = Config(BOOLEAN_CONDITIONS=True)
        template = self._build_stream(self.base_template)
        output = infer_from_ast(parse(template),
            ignore_constants=ignore_constants,
            config=j2s_config)
        return output

    def get_json_schema(self, ignore_constants=True):
        """Build a JSON schema from a template
        
        Keyword Arguments:
            ignore_constants {bool} -- Ignoring constants prevents printing of loop controls, etc.  (default: {True})
        
        Returns:
            [type] -- [description]
        """
        j2s_config = Config(BOOLEAN_CONDITIONS=True)
        template = self._build_stream(self.base_template)
        out = to_json_schema(infer_from_ast(parse(template),
                             ignore_constants=ignore_constants,
                             config=j2s_config)
        )
        return out['properties']

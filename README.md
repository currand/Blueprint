## Overview
Blueprint is a configuration management system for CLI and other typed of text based configurations. It is meant to ease the inclusion of text-based configurations in documentation and downstream automation systems.

## Requirements
- Python 3
- Jinja2
- PyYAML
```bash
pip install -r requirements.txt
```
## Testing
### Requirements
- PyTest
- Pytest-Coverage
```bash
$ pytest
============================================================================= test session starts ==============================================================================
platform darwin -- Python 3.7.4, pytest-5.2.2, py-1.8.0, pluggy-0.13.0
rootdir: ~/Blueprint
plugins: cov-2.8.1
collected 11 items

tests/test_helpers.py .                                                                                                                                                  [  9%]
tests/test_internals.py ...                                                                                                                                              [ 36%]
tests/test_outputs.py .......                                                                                                                                            [100%]

============================================================================== 11 passed in 0.08s ==============================================================================
```
## Usage

### Basic
```bash
$ python blueprint.py -h
usage: blueprint.py [-h] -t TEMPLATE_DIR -b BASE_TEMPLATE [-s]
                    [-e TEMPLATE_EXT] [-v] [-j] [-c CONFIG_VARS]

optional arguments:
  -h, --help            show this help message and exit
  -t TEMPLATE_DIR, --template-dir TEMPLATE_DIR
                        Location of Blueprints
  -b BASE_TEMPLATE, --base-template BASE_TEMPLATE
                        The base template
  -e TEMPLATE_EXT, --template-ext TEMPLATE_EXT
                        Template extension. Default = ".j2"

output types:
  -s, --stream-only     Produce an unrendered single Jinja template
  -v, --get-vars        Return variables for a rendered template
  -j, --json-schema     Return schema of variables for a rendered template
  -c CONFIG_VARS, --config-vars CONFIG_VARS
                        A file containing config variables
 ```
###  Generate a config
```parent.j2```:
```jinja2
some text
{% for x in y -%}
 {{ x }}
{% endfor -%}
{%- include '/child/child.j2' -%}
```
```child/child.j2```:
```jinja2
{% if things is not defined -%}
{% set things = [0,1,2] -%}
{% endif -%}
{% for thing in things -%}
 item {{ thing }}
{% endfor -%}
```
```vars.yaml```:
```yaml
things:
- foo
- bar
- baz
```

####  Generate a config with variables
```bash
python blueprint.py -t tests/templates -b parent.j2 -c tests/vars.yaml
    some text
    item foo
    item bar
    item baz
    ```
    #### Generate an unrendered config template in Jinja2
    ```bash
    $ python blueprint.py -t tests/templates -b parent.j2 -s
    some text
    {% for x in y -%}
    {{ x }}
    {% endfor -%}
    {% if things is not defined -%}
    {% set things = [0,1,2] -%}
    {% endif -%}
    {% for thing in things -%}
    item {{ thing }}
    {% endfor -%}
```
#### Generate a list of variables
```bash
 $ python blueprint.py -t tests/templates -b parent.j2 -v
{'things': [<number>], 'y': [<scalar>]}
```
#### Generate a JSON schema for a template
```bash
$ python blueprint.py -t tests/templates -b parent.j2 -j
{
  "things": {
    "items": {
      "title": "thing",
      "type": "number"
    },
    "title": "things",
    "type": "array"
  },
  "y": {
    "items": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "null"
        },
        {
          "type": "number"
        },
        {
          "type": "string"
        }
      ],
      "title": "x"
    },
    "title": "y",
    "type": "array"
  }
}
```

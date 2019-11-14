from blueprint import load_vars

def test_basic_render(blueprint):
    output = 'some text\nitem 0\nitem 1\nitem 2\n'
    
    assert blueprint.render_template() == output

def test_render_values(blueprint):
    output = 'some text\nitem foo\nitem bar\nitem baz\n'
    kwargs = {'things': [
        'foo',
        'bar',
        'baz'
        ]
    }
    assert blueprint.render_template(**kwargs) == output

def test_read_config_file(blueprint):
  output = {'things': [
        'foo',
        'bar',
        'baz'
        ]
  }
  filename = 'tests/vars.yaml'

  assert load_vars(filename) == output
  
def test_render_with_config(blueprint):
  output = 'some text\nitem foo\nitem bar\nitem baz\n'
  filename = 'tests/vars.yaml'
  kwargs = load_vars(filename)

  assert blueprint.render_template(**kwargs) == output

def test_get_stream(blueprint):
    assert blueprint.get_stream() == 'some text\n{% for x in y -%}\n {{ x }}\n{% endfor -%}\n{% if things is not defined -%}\n{% set things = [0,1,2] -%}\n{% endif -%}\n{% for thing in things -%}\n item {{ thing }}\n{% endfor -%}'
    out = blueprint.get_stream('child/child.j2')
    assert blueprint.get_stream('child/child.j2') == '{% if things is not defined -%}\n{% set things = [0,1,2] -%}\n{% endif -%}\n{% for thing in things -%}\n item {{ thing }}\n{% endfor -%}'

def test_get_variables(blueprint):
    out = "{'things': [<number>], 'y': [<scalar>]}"
    assert str(blueprint.get_variables()) == out

def test_get_json_schema(blueprint):
    out = {
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
    assert blueprint.get_json_schema() == out
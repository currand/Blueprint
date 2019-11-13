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

def test_get_stream(blueprint):
    assert blueprint.get_stream() == 'some text\n\n{% for x in y -%}\n\n {{ x }}\n\n{% endfor -%}\n\n{% if things is not defined -%}\n\n{% set things = [0,1,2] -%}\n\n{% endif -%}\n\n{% for thing in things -%}\n\n item {{ thing }}\n\n{% endfor -%}'
    assert blueprint.get_stream('child/child.j2') == '{% if things is not defined -%}\n\n{% set things = [0,1,2] -%}\n\n{% endif -%}\n\n{% for thing in things -%}\n\n item {{ thing }}\n\n{% endfor -%}'

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
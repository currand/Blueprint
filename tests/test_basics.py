import pytest
from blueprint import Blueprint

@pytest.fixture
def blueprint():
    return Blueprint(template_dir='tests/templates',
        base_template='parent.j2',
        template_suffix='.j2'
    )

def test_basic_render(blueprint):
    output = 'some text\nitem 0\nitem 1\nitem 2\n'
    
    assert blueprint.render_template() == output

def test_template_list(blueprint):
    templates = [
        'parent.j2',
        'child/child.j2'
    ]

    assert blueprint.templates.sort() == templates.sort()

def test_build_stream(blueprint):
    output = "some text\n\n{% for x in y -%}\n\n {{ x }}\n\n{% endfor -%}\n\n{%- include '/child/child.j2' -%}"
    
    stream = blueprint._build_stream('parent.j2')
    assert stream == output
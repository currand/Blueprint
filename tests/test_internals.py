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
    output = "some text\n\n{% for x in y -%}\n\n {{ x }}\n\n{% endfor -%}\n\n{% set things = [0,1,2] -%}\n\n{% for thing in things -%}\n\n item {{ thing }}\n\n{% endfor -%}"
    
    stream = blueprint._build_stream('parent.j2')
    assert stream == output

def test_check_template_suffix(blueprint):
    assert blueprint._check_template_suffix('test.j2') is True
    assert blueprint._check_template_suffix('test.r2') is None


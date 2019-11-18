from helpers import junos_indent, yaml_join

def test_helper_junos_indent():
    in_temp = "{\n{\n{\ntest indent;\n}\n}\n}"
    out_temp = '{\n    {\n        {\n            test indent;\n        }\n    }\n}'

    assert junos_indent(in_temp) == out_temp

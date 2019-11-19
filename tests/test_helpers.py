import yaml
import pytest
from helpers import junos_indent, yaml_join, csv_load, yaml_load

def test_helper_junos_indent():
    in_temp = "{\n{\n{\ntest indent;\n}\n}\n}"
    out_temp = '{\n    {\n        {\n            test indent;\n        }\n    }\n}'

    assert junos_indent(in_temp) == out_temp

def test_yaml_join():
    strings = ['a', 'b']
    class loader():
        def construct_sequence(self, seq):
            return seq
    
    loader_inst = loader()
    assert yaml_join(loader_inst,
                    strings) == ''.join(strings)

def test_bad_csv_file(blueprint):
    with pytest.raises(SystemExit) as e_info:
        assert csv_load(blueprint.template_dir, 'fake.yaml')

def test_load_csv_file(blueprint):

    out_with_blank = { 
            'data' : [
                        {
                            'Hostname': 'car01.bvtn.or',
                            'local_address': '50.46.181.0',
                            'local_address_v6': '',
                            'router_type': 'car'
                        }
                    ]
            }

    out_no_blank = { 
            'data' : [
                        {
                            'Hostname': 'car01.bvtn.or',
                            'local_address': '50.46.181.0',
                            'local_address_v6': '2001:1960::1/128',
                            'router_type': 'car'
                        }
                    ]
            }

    assert csv_load(blueprint.template_dir, 'tests/templates/out_with_blank.csv') == out_with_blank
    assert csv_load(blueprint.template_dir, 'tests/templates/out_no_blank.csv') == out_no_blank

@pytest.mark.parametrize('files', ['tests/templates/values.yaml', 'values.yaml'])
def test_read_yaml_file(blueprint, files):

    values = 'tests/templates/values.yaml'
    with open(values, 'r') as fh:
        lines = ''.join(fh.readlines())
    config = yaml.load(lines, Loader=yaml.Loader)

    assert config == yaml_load(blueprint.template_dir, files)

@pytest.mark.parametrize('files', ['fake.yaml'])
def test_bad_yaml_file(blueprint, files):

    values = 'tests/templates/values.yaml'
    with open(values, 'r') as fh:
        lines = ''.join(fh.readlines())
    config = yaml.load(lines, Loader=yaml.Loader)

    with pytest.raises(SystemExit) as e_info:
        assert config == yaml_load(blueprint.template_dir, files)

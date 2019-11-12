import pytest
from blueprint import Blueprint

@pytest.fixture
def blueprint():
    return Blueprint(template_dir='tests/templates',
        base_template='parent.j2',
        template_suffix='.j2'
    )

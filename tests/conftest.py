import pytest
import sys
sys.path.append('..')  # TODO: more elegant pkg solution
from run import create_app


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()

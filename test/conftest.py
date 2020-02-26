import os, sys
import tempfile
import pytest

sys.path.append('..')
from app import create_app
from app.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


# generate the app with temp db for testing
@pytest.fixture
def app_test():
    db_fd, db_path = tempfile.mkstemp()

    app_test = create_app({
        'TESTING': True,
        'DEBUG': True,
        'DATABASE': db_path,
    })

    with app_test.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app_test

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app_test):
    return app_test.test_client()

@pytest.fixture
def runner(app_test):
    return app_test.test_cli_runner()
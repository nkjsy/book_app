import sqlite3
import pytest
from app.db import get_db


def test_get_close_db(app_test):
    # get the same database connection
    with app_test.app_context():
        db = get_db()
        assert db is get_db()

    # close the connection after leaving the context
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    assert 'closed' in str(e.value)

# test the init-db command
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('app.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called
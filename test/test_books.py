import pytest
from app.db import get_db


# test the main page
def test_display(client):
    response = client.get('/books/')
    assert b'ADD' in response.data
    assert b'DELETE' in response.data
    assert b'Lewis Carroll' in response.data
    assert b'Title' in response.data
    assert b'Author' in response.data

# test adding
def test_add(client, app_test):
    response = client.post('/books/add', data={'title': 'Pride and Prejudice', 'author': 'Jane Austen'})
    assert response.status_code == 302
    with app_test.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(title) FROM book').fetchone()[0]
        assert count == 2
        book = db.execute('SELECT * FROM book WHERE title = "Pride and Prejudice"').fetchone()
        assert book['author'] == 'Jane Austen'

# test adding validation
def test_add_validate(client):
    response = client.post('/books/add', data={'title': '', 'author': ''})
    assert b'Title is required.' in response.data
    assert b'Author is required.' in response.data

# test deleting
def test_delete(client, app_test):
    client.post('/books/delete', data={'title': 'Pride and Prejudice', 'author': 'Jane Austen'})
    with app_test.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM book WHERE title = "Pride and Prejudice"').fetchone()
        assert post is None
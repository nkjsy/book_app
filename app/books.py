from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from app.db import get_db

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/')
def display():
    db = get_db()
    books = db.execute(
        'SELECT title, author FROM book'
    ).fetchall()
    return render_template('books/display.html', books=books)

@bp.route('/add', methods=('POST',))
def add():
    title = request.form['title']
    author = request.form['author']
    error = None

    if not title:
        error = 'Title is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO book (title, author)'
            ' VALUES (?, ?)',
            (title, author)
        )
        db.commit()
        return redirect(url_for('books.display'))

@bp.route('/delete', methods=('POST',))
def delete():
    db = get_db()
    db.execute('DELETE FROM book WHERE title = ? AND author = ?', (request.form['title'], request.form['author']))
    db.commit()
    return redirect(url_for('books.display'))
from flask import Blueprint, flash, g, redirect, render_template, request, url_for, Response, stream_with_context
from app.db import get_db
import joblib
from app.grouping import book_grouping

bp = Blueprint('books', __name__, url_prefix='/books')
# load the tfidf vectorizer
vectorizer = joblib.load('/root/book_app/model/vectorizer.pkl')
# load the LDA topic model
lda = joblib.load('/root/book_app/model/lda.pkl')
# load the Gaussian mixture model for clustering
gmm = joblib.load('/root/book_app/model/gmm.pkl')

# main page
@bp.route('/')
def display():
    db = get_db()
    books = db.execute(
        'SELECT title, author FROM book'
    ).fetchall()
    return render_template('books/display.html', books=books)

# add the title and author information of a book, along with the group info invisible to users
@bp.route('/add', methods=('POST',))
def add():
    title = request.form['title']
    author = request.form['author']
    error = ''
    error_title = 'Title is required. ' if not title else ''
    error_author = 'Author is required. ' if not author else ''
    error = error + error_title + error_author

    if error != '':
        flash(error)
        return redirect(url_for('books.display'))
    else:
        groups = book_grouping(title, author, vectorizer, lda, gmm)
        db = get_db()
        db.execute(
            'INSERT INTO book (title, author, groups, maxgroup)'
            ' VALUES (?, ?, ?, ?)',
            (title, author, groups, int(groups.split(',')[0]))
        )
        db.commit()
        return redirect(url_for('books.display'))

# delete a book from the database
@bp.route('/delete', methods=('POST',))
def delete():
    db = get_db()
    db.execute('DELETE FROM book WHERE title = ? AND author = ?', (request.form['title'], request.form['author']))
    db.commit()
    return redirect(url_for('books.display'))

# generator for csv format data
# col: all, title, author
# books: list of book info
def csv_gen(col, books):
    if col == 'all':
        yield ','.join(['title', 'author']) + '\n'
    else:
        yield col + '\n'
    for book in books:
        if col == 'all':
            yield ','.join([book['title'], book['author']]) + '\n'
        else:
            yield book[col] + '\n'

# generator for xml format data
# col: all, title, author
# books: list of book info
def xml_gen(col, books):
    yield '<books>'
    for book in books:
        yield '<book>'
        if col == 'all':
            yield '<title>' + book['title'] + '</title>' + '<author>' + book['author'] + '</author>'
        else:
            yield '<' + col + '>' + book[col] + '</' + col + '>'
        yield '</book>'
    yield '</books>'

# export file in csv or xml
@bp.route('/export/<filename>')
def export(filename):
    db = get_db()
    books = db.execute(
        'SELECT title, author FROM book'
    ).fetchall()
    col, format = filename.split('.')
    if format == 'csv':
        return Response(stream_with_context(csv_gen(col, books)), mimetype='text/csv')
    elif format == 'xml':
        return Response(stream_with_context(xml_gen(col, books)), mimetype='text/xml')
        
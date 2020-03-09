from flask import Blueprint, flash, redirect, render_template, request, url_for, Response, stream_with_context
from app.db import get_db
import joblib
import os
import pandas as pd
from app.grouping import get_stopwords, book_grouping
from app.recommend import recommend_group, recommend_knn


bp = Blueprint('books', __name__, url_prefix='/books')
# set the paths
project_root = os.path.dirname(bp.root_path)
model_path = os.path.join(project_root, 'model')
data_path = os.path.join(project_root, 'data')
# load the stopwords
stopwords = get_stopwords(data_path + '/stopwords.txt')
# load the tfidf vectorizer
vectorizer = joblib.load(model_path + '/vectorizer.pkl')
# load the LDA topic model
lda = joblib.load(model_path + '/lda.pkl')
# load the Gaussian mixture model for clustering
gmm = joblib.load(model_path + '/gmm.pkl')
# load the k nearest neighbors model for recommendation
knn = joblib.load(model_path + '/knn.pkl')
# load the original data for recommendation
archive = pd.read_csv(data_path + '/archive.csv', header=0, encoding='utf-8')

# main page
@bp.route('/')
def display():
    db = get_db()
    books = db.execute(
        'SELECT title, author, maxgroup FROM book'
    ).fetchall()
    # recommends = recommend_group(books, archive)
    recommends = recommend_knn(books, archive, vectorizer, lda, knn, stopwords)
    return render_template('books/display.html', books=books, recommends=recommends)

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
        groups = book_grouping(title, author, vectorizer, lda, gmm, stopwords)
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
        
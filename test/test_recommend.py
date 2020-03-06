import pytest
import numpy as np
import pandas as pd
from app.recommend import recommend_group, recommend_knn
from app.db import get_db
import joblib

vectorizer = joblib.load('/root/book_app/model/vectorizer.pkl')
lda = joblib.load('/root/book_app/model/lda.pkl')
knn = joblib.load('/root/book_app/model/knn.pkl')
archive = pd.read_csv('/root/book_app/data/archive.csv', header=0, encoding='utf-8')


# test recommendation by group
def test_recommend_group(app_test):
    with app_test.app_context():
        db = get_db()
        books = db.execute(
            'SELECT title, author, maxgroup FROM book'
        ).fetchall()
        recommends = recommend_group(books, archive)
        assert len(recommends) == 5
        title, author = recommends[0]
        assert title in archive['title'].values
        assert author in archive['author'].values

# test recommendation by knn
def test_recommend_knn(app_test):
    with app_test.app_context():
        db = get_db()
        books = db.execute(
            'SELECT title, author, maxgroup FROM book'
        ).fetchall()
        recommends = recommend_knn(books, archive, vectorizer, lda, knn)
        assert len(recommends) == 5
        title, author = recommends[0]
        assert title in archive['title'].values
        assert author in archive['author'].values
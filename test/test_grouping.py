import pytest
import numpy as np
from app.grouping import get_stopwords, clean_title, clean_author, into_groups
import joblib

vectorizer = joblib.load('/root/book_app/model/vectorizer.pkl')
lda = joblib.load('/root/book_app/model/lda.pkl')
gmm = joblib.load('/root/book_app/model/gmm.pkl')
stopwords = get_stopwords('/root/book_app/data/stopwords.txt')

# test cleaning title
def test_clean_title():
    clean = clean_title("Alice's adventure in wonderland", stopwords)
    assert clean == "alices adventure wonderland"

# test cleaning author
def test_clean_author():
    clean = clean_author("Lewis Carroll")
    assert clean == "lewis carroll"

# test grouping books
def test_into_groups():
    case1 = np.array([1/8] * 8)
    assert into_groups(case1) == '8'
    case2 = np.array([0.01] * 7 + [0.93])
    assert into_groups(case2) == '7'
    case3 = np.array([0.01, 0.5, 0.12, 0.01, 0.01, 0.3, 0.01, 0.04])
    assert into_groups(case3) == '1,5,2'
    
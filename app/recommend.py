import collections
import numpy as np
from app.grouping import clean_title, clean_author

# find the most prefered group and recommend random books in the same group from archive
def recommend_group(books, archive):
    max_groups = []
    for book in books:
        max_groups.append(book['maxgroup'])
    if max_groups == []:
        # no book in the list
        recommends = []
    else:
        most_group = collections.Counter(max_groups).most_common(1)[0][0]
        recommend_df = archive[archive['maxgroup']==most_group].sample(5)
        recommends = []
        for title, author in zip(recommend_df['title'], recommend_df['author']):
            recommends.append((title, author))
    return recommends

# average the book vectors in the current list and recommend the k nearest neighbors in the vector space
def recommend_knn(books, archive, vectorizer, topic_model, knn_model):
    books_info = []
    for book in books:
        both = clean_title(book['title']) + ' ' + clean_author(book['author'])
        books_info.append(both)
    if books_info == []:
        # no book in the list
        recommends = []
    else:
        vector = vectorizer.transform(books_info)
        vector_topic = topic_model.transform(vector)
        average_vec = np.mean(vector_topic, axis=0, keepdims=True)
        nbrs = knn_model.kneighbors(average_vec, n_neighbors=5, return_distance=False)
        # retrieve the books by index in the archive
        recommends = []
        for nbr in nbrs[0]:
            row = archive.iloc[nbr]
            recommends.append((row['title'], row['author']))
    return recommends
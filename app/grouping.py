import re
import numpy as np

# load the stopwords
def get_stopwords(file):
    with open(file, 'r') as fr:
        stopwords = set(map(lambda x: x.strip(), fr.readlines()))
    return stopwords

# funtion to clean the title
def clean_title(line):
    result = []
    stopwords = get_stopwords('/root/book_app/data/stopwords.txt')
    # remove the punctuation
    punc = '[~`\!\#\$\%^\&\*\'\(\)_\+\-\=\|\[\]\\/\:;\.,\?\>\<\@\"\{\}]'
    line = re.sub(re.compile(punc), '', line)
    words = line.strip().split()
    for word in words:
        word = word.lower()
        # exclude the stopwords or pure numbers
        if word in stopwords or word.isdigit():
            continue
        result.append(word)
    return ' '.join(result)

# funtion to clean the author
def clean_author(line):
    result = []
    words = line.strip().split()
    for word in words:
        word = word.lower()
        result.append(word)
    return ' '.join(result)

# how to decide groups according to probability distribution?
def into_groups(distribution):
    max_p = np.max(distribution)
    groups = []
    if max_p > 0.9:
        # if max proba > 0.9, return the max group
        groups = [np.argmax(distribution)]
    elif max_p < 0.4:
        # if max proba < 0.4, not belong to any group, return a new group
        groups = [len(distribution)]
    else:
        # if max proba is not dominant, return all the groups with proba > 0.1
        ind = np.argsort(-distribution)
        n_groups = len(distribution[distribution > 0.1])
        groups = ind[:n_groups].tolist()
    return ','.join(map(str, groups))

# book grouping function
def book_grouping(title, author, vectorizer, topic_model, cluster_model):
    both = clean_title(title) + ' ' + clean_author(author)
    vector = vectorizer.transform([both])
    vector_topic = topic_model.transform(vector)
    distribution = cluster_model.predict_proba(vector_topic)[0,:]
    groups = into_groups(distribution)
    return groups
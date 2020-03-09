# book_app

## Introduction

This is a web application to list the title and author of your faverite books and use them to group the books into different clusters and do recommendation.

The basic functions including:

1. Add a book to the list with its title and author.
2. Delete a book from the list.
3. Export the book list in CSV and XML.
4. Cluster the books into different groups based on titles and authors. 
5. Recommend 5 books according to the current book list.

The clustering algorithm is straightforward. First the titles and authors are vectorized by TF-IDF, then the topic features are extracted by LDA, based on that a gaussian mixture model is applied to do a soft clustering. Group index are assigned to books by certain thresholds.

Since the group index are just arbitrary numbers, (In pretrained models the number of book groups is 8.) the clustering results are not shown to users, although stored in the database. However, the grouping result gives rise to a intuitive way to do recommendation by recommending the books in the same group. This way requires no additional models so is quite convenient, but not necessarily recommends the most similar books.

In the current version, the recommendation is based on k nearest neighbors algorithm rather than the one based on grouping results. This will recommend the 5 most similar books in the vector space.

A demo application is hosted [here](http://47.105.193.221:5000/books) in the Alibaba cloud server. 

## Dependency

This demo application runs in Python3 with the following packages:

* flask
* joblib
* numpy
* pandas
* pytest
* scikit-learn

If you want to view the model training process in train.ipynb, you also have to install jupyter notebook. 

A convenient way to manage your python environment and packages is to install Anaconda, which already has most of the packages installed.

## Deployment

Once the python environment is ready, you can run train.ipynb and try to change the model and data if you want to explore more. Or you can just deploy the project using the pretrained model by running the following commands under the project root path:

    export FLASK_APP app
    flask init-db
    flask run --host=0.0.0.0

The application is hosted using flask as the web framework, and SQLite as the database.

## Data

The raw training dataset in data/book_list.csv includes more than 25K books with titles and authors. The preprocessing before training can be found in the train.ipynb, which is essentially the same logic as in the inference stage.

## Model

There are four model checkpoints preloaded when running the application:

1. vectorizer.pkl is the TF-IDF model to turn the books into vectors.
2. lda.pkl is the LDA topic model to extract the topic features of the books.
3. gmm.pkl is the Gaussian mixture model to do the clustering task.
4. knn.pkl is the k nearest neighbors model to find the most similar books to the current books in the list.
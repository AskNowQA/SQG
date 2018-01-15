from classifier import Classifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB


class NaiveBayesClassifier(Classifier):
    def __init__(self):
        super(NaiveBayesClassifier, self).__init__()
        self.pipeline = Pipeline(
            [('vect', CountVectorizer()), ('tf-idf', TfidfTransformer()), ('naive-bayes', MultinomialNB())])
        self.parameters = {'vect__ngram_range': [(1, 1), (1, 2)], 'tf-idf__use_idf': (True, False),
                           'naive-bayes__alpha': (1e-2, 1e-3)}

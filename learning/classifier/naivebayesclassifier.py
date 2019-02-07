from learning.classifier.classifier import Classifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB


class NaiveBayesClassifier(Classifier):
    def __init__(self, model_file_path=None):
        super(NaiveBayesClassifier, self).__init__(model_file_path)
        self.pipeline = Pipeline(
            [('vect', CountVectorizer()), ('tf-idf', TfidfTransformer()), ('naive-bayes', MultinomialNB())])
        self.parameters = {'vect__ngram_range': [(1, 1), (2, 2), (3, 3), (1, 3)], 'tf-idf__use_idf': (True, False),
                           'naive-bayes__alpha': (1e-2, 1e-3)}

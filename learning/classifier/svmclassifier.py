from classifier import Classifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier


class SVMClassifier(Classifier):
    def __init__(self, model_file_path=None):
        super(SVMClassifier, self).__init__(model_file_path)
        self.pipeline = Pipeline([('vect', CountVectorizer()), ('tf-idf', TfidfTransformer()),
                                  ('svm',
                                   SGDClassifier(loss='log', penalty='l2', alpha=1e-3, n_iter=5, random_state=42))])
        self.parameters = {'vect__ngram_range': [(1, 1), (1, 2)], 'tf-idf__use_idf': (True, False),
                           'svm__alpha': (1e-2, 1e-3)}

from classifier import Classifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression


class LogisticRegressionClassifier(Classifier):
    def __init__(self, model_file_path=None):
        super(LogisticRegressionClassifier, self).__init__(model_file_path)
        self.pipeline = Pipeline([('vect', CountVectorizer()), ('tf-idf', TfidfTransformer()),
                                  ('maxe',
                                   LogisticRegression(C=1.0, class_weight=None, dual=False, fit_intercept=True,
                                                      intercept_scaling=1, max_iter=100, multi_class='ovr',
                                                      penalty='l2', random_state=42, solver='liblinear', tol=0.0001,
                                                      verbose=0, warm_start=False))])

        self.parameters = {'vect__ngram_range': [(1, 1), (2, 2), (3, 3), (1, 3)], 'tf-idf__use_idf': (True, False),
                           'maxe__solver': ['sag','newton-cg', 'lbfgs']}




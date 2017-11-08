from classifier import Classifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import GridSearchCV


class NaiveBayesClassifier(Classifier):
    def train(self, X_train, y_train):
        classifier = Pipeline(
            [('vect', CountVectorizer()), ('tf-idf', TfidfTransformer()), ('naive-bayes', MultinomialNB())])
        parameters = {'vect__ngram_range': [(1, 1), (1, 2)], 'tf-idf__use_idf': (True, False),
                      'naive-bayes__alpha': (1e-2, 1e-3)}
        optimized_classifier = GridSearchCV(classifier, parameters, n_jobs=-1)
        self.model = optimized_classifier.fit(X_train, y_train)

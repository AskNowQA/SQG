from sklearn.externals import joblib
from sklearn.model_selection import GridSearchCV
import os

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB


class NaiveBayesClassifier(MultinomialNB):

    def __init__(self):
        super(NaiveBayesClassifier, self).__init__()
        self.pipeline = Pipeline([('naive-bayes', MultinomialNB())])
        self.parameters = {}

    def train(self, X_train, y_train):
        optimized_classifier = GridSearchCV(self.pipeline, self.parameters, n_jobs=-1, cv=10)
        optimized_classifier.fit(X_train, y_train)

        return self.model.best_score_



if __name__ == '__main__':
    nb = NaiveBayesClassifier()





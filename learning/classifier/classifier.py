from sklearn.externals import joblib
from sklearn.model_selection import GridSearchCV


class Classifier(object):
    def __init__(self):
        self.model = None
        pass

    @property
    def is_trained(self):
        return self.model is not None

    def save(self, file_path):
        joblib.dump(self.model, file_path)

    def load(self, file_path):
        self.model = joblib.load(file_path)

    def train(self, X_train, y_train):
        optimized_classifier = GridSearchCV(self.pipeline, self.parameters, n_jobs=-1, cv=10)
        self.model = optimized_classifier.fit(X_train, y_train)
        return self.model.best_score_

    def predict(self, X_test):
        if self.is_trained:
            return self.model.predict(X_test)
        else:
            return None

from sklearn.externals import joblib
from sklearn.model_selection import GridSearchCV
import os


class Classifier(object):
    def __init__(self, model_file_path):
        self.model_file_path = model_file_path
        if self.model_file_path is not None and os.path.exists(self.model_file_path):
            self.load(model_file_path)
        else:
            self.model = None

    # def __pipeline(self):
    #     pass

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
        if self.model_file_path is not None:
            self.save(self.model_file_path)
        return self.model.best_score_

    def predict(self, X_test):
        if self.is_trained:
            return self.model.predict(X_test)
        else:
            return None

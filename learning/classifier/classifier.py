from sklearn.externals import joblib


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
        pass

    def predict(self, X_test):
        if self.is_trained:
            return self.model.predict(X_test)
        else:
            return None

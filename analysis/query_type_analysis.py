from learning.classifier.svmclassifier import SVMClassifier
from learning.classifier.naivebayesclassifier import NaiveBayesClassifier
from orchestrator import Orchestrator
from parser.lc_quad import LC_QaudParser
from sklearn.metrics import classification_report


def run(classifier):
    parser = LC_QaudParser()
    query_builder = Orchestrator(classifier, parser, auto_train=False)
    scores = query_builder.train_question_classifier(file_path="../data/LC-QUAD/data_v8.json", test_size=0.5)
    print scores
    y_pred = query_builder.question_classifier.predict(query_builder.X_test)
    print(classification_report(query_builder.y_test, y_pred))


if __name__ == "__main__":
    run(SVMClassifier())
    run(NaiveBayesClassifier())

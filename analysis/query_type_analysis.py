from learning.classifier.svmclassifier import SVMClassifier
from learning.classifier.naivebayesclassifier import NaiveBayesClassifier
from orchestrator import Orchestrator
from parser.lc_quad import LC_QaudParser
from sklearn.metrics import classification_report


def run(classifier1, classifier2):
    parser = LC_QaudParser()
    query_builder = Orchestrator(classifier1, classifier2, parser, auto_train=False)

    print "train_question_classifier"
    scores = query_builder.train_question_classifier(file_path="../data/LC-QUAD/data_v8.json", test_size=0.5)
    print scores
    y_pred = query_builder.question_classifier.predict(query_builder.X_test)
    print(classification_report(query_builder.y_test, y_pred))

    print "double_relation_classifer"
    scores = query_builder.train_double_relation_classifier(file_path="../data/LC-QUAD/data_v8.json", test_size=0.5)
    print scores
    y_pred = query_builder.double_relation_classifer.predict(query_builder.X_test)
    print(classification_report(query_builder.y_test, y_pred))


if __name__ == "__main__":
    run(SVMClassifier(), SVMClassifier())
    run(NaiveBayesClassifier(), NaiveBayesClassifier())

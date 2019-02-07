from helper import *
from learning.classifier.naivebayesclassifier import NaiveBayesClassifier as NB
from learning.classifier.svmclassifier import SVMClassifier as SVM
from learning.classifier.logisticregression import LogisticRegressionClassifier as MAXE
from sklearn.metrics import accuracy_score
from feature_extraction_filter.resource_tree import parse_sparql


train_path = "data/train.json"
test_path = "data/test.json"

def type_check(question, sparql):
    model_result = type_check_model(question)
    query_result = type_check_query(sparql)


def type_check_model(question):
    model = MAXE("models/LogR")
    return model.predict([question])


def type_check_query(query_):
    return parse_sparql(query_)


# Prepares Model Train Test Sets
def prep_model_train_test():
    train = load_json(train_path)
    test = load_json(test_path)

    print train_path, test_path

    train_x, train_y = zip(*train)
    test_x, test_y = zip(*test)
    return train_x, train_y, test_x, test_y


def train_model(model):
    print "Preparing Train/Test data"
    x_train, y_train, x_test, y_test = prep_model_train_test()

    print "Training Model"
    print model.train(x_train, y_train)
    print "Training Done"


def test_model(model, out=False):
    x_train, y_train, x_test, y_test = prep_model_train_test()
    y_hyp = model.predict(x_test)

    print "Model Accuracy on Testset:", accuracy_score(y_test, y_hyp)

    if out:
        for x, y, z in zip(x_test, y_test, y_hyp):
            print x, y, z


def experiment_1():
    model = NB("models/NB")
    print model.__class__.__name__
    train_model(model)
    test_model(model)


# Compares SVM Accuracy on Testset vs WE
def experiment_2():
    model = SVM("models/SVM")
    print model.__class__.__name__
    train_model(model)
    test_model(model)


# Compares LogR Accuracy on Testset vs WE
def experiment_3():
    model = MAXE("models/LogR")
    print model.__class__.__name__
    train_model(model)
    test_model(model)


def main():
    print "MAIN"
    # experiment_1()
    # experiment_2()
    # experiment_3()
    model = NB("models/NB")
    # print model.predict(["which arts administrator won an oscar",
    #                      "was the nine years war earlier than the one thousand nine hundred and five russian revolution",
    #                      "give me all books by maria edgeworth with more than three hundred pages"])
    print type_check_model("is david dacaulay still alive")
    # query_ = """ask where{<http://dbpedia.org/resource/List_of_Power_Rangers_Turbo_episodes> <http://dbpedia.org/ontology/numberOfEpisodes> ?a . <http://dbpedia.org/resource/Absolutely_Fabulous> <http://dbpedia.org/ontology/numberOfEpisodes> ?b . filter (?a > ?b)  }"""
    # print type_check_query(query_)



if __name__ == '__main__':
    main()

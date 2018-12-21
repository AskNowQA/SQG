import json, sys, os
from learning.classifier.naivebayesclassifier import NaiveBayesClassifier as NB
from learning.classifier.svmclassifier import SVMClassifier as SVM
from learning.classifier.logisticregression import LogisticRegressionClassifier as MAXE
from sklearn.metrics import accuracy_score

PATH = "../data/clean_datasets/train_test_clean/"

# Loads a JSON file
def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


def stats(data):
    # data = load_json(path)
    questions, type_ = zip(*data)

    type_ = list(type_)

    # print type_
    list_ = type_.count(0)
    ask = type_.count(1)
    count = type_.count(2)

    print "-- No. List Questions: %d" % list_
    print "-- No. Ask Questions: %d" % ask
    print "-- No. Count Questions: %d" % count
    # print "No. Order Questions: %d" % len(order)
    # print "No. Filter Questions: %d" % len(filter_)
    # print "No. Agg Questions: %d" % len(agg)
    print ""


# Datasets: lcquad, qald, dbnqa 1%
def run_experiment(model, mode_name, dataset_name):
    train = load_json(PATH + "%s/train.json" % dataset_name)
    test = load_json(PATH + "%s/test.json" % dataset_name)

    print " Dataset %s \n" % dataset_name
    print "Training Set Stats :"
    stats(train)

    print "Testing Set Stats :"
    stats(test)

    x_train, y_train = zip(*train)
    x_test, y_test = zip(*test)

    # print "Take first 5 words"
    # x_train = first_n_words(x_train, 5)
    # x_test = first_n_words(x_test, 5)

    # print "Normalized x train"
    # x_train = normalize_numbers(x_train)
    # print x_train
    # sys.exit(0)

    # print "Take first last 3 words"
    # x_train = first_last_n_words(x_train, 3)
    # x_test = first_last_n_words(x_test, 3)

    print "Training Model Score: "
    print model.train(x_train, y_train)


    # x_test = normalize_numbers(x_test)
    y_hyp = model.predict(x_test)

    print "Testing set Accuracy: %s \n" % accuracy_score(y_test, y_hyp)

    data = load_json("../data/clean_datasets/train_test_clean/test/test.json")
    x_test, y_test = zip(*data)

    # x_test = first_n_words(x_test, 5)
    # x_test = normalize_numbers(x_test)
    # x_test = first_last_n_words(x_test, 3)

    y_hyp = model.predict(x_test)
    print "General Testing set Accuracy: %s \n" % accuracy_score(y_test, y_hyp)

    model.save("models/%s" % mode_name)

    print "Best Parameters:"
    for param in model.parameters.keys():
        print "--", param, model.model.best_params_[param]

    print ""

    means = model.model.cv_results_['mean_test_score']
    stds = model.model.cv_results_['std_test_score']

    print "Parameters Grid Stats: "

    for mean, std, params in zip(means, stds, model.model.cv_results_['params']):
        print("-- %0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))


# def run_experiment_secondary():
#     train = load_json("../data/clean_datasets/train_test_clean/order/train.json")
#     test = load_json("../data/clean_datasets/train_test_clean/order/test.json")
#
#     x_train, y_train = zip(*train)
#     x_test, y_test = zip(*test)
#
#     nb = NB()
#     print nb.train(x_train, y_train)
#
#     y_hyp = nb.predict(x_test)
#
#     print accuracy_score(y_test, y_hyp)


def deep_test(model, x_test, y_test):
    y_hyp = model.predict(x_test)

    for i, j, k in zip(x_test, y_test, y_hyp):
        print i, " True : %s" % j, " Predicted: %s" % k


# Takes the first N words in the string
def first_n_words(x_train, n):
    result = []
    for x in x_train:
        tmp = x.split(" ")
        tmp = tmp[:n]
        res = ' '.join(tmp)
        result.append(res)
    return result


# Removes Numbers and replaces them with a word. This is to overcome lack of numbers in the training data
def normalize_numbers(x_train):
    ordinals = [x.replace("-", " ") for x in load_json("../data/ComplexQuestionsOrder/ordinals.json")]
    result = []
    for row in x_train:
        for word in ordinals:
            if word in row:
                row = row.replace(word, "abdo")
        result.append(row)
    return result


def first_last_n_words(x_train, n):
    result = []
    for x in x_train:
        tmp = x.split(" ")
        tmp = tmp[:n] + tmp[-1*n:]
        res = " ".join(tmp)
        result.append(res)
    return result


def main():
    print "### MAIN ###"
    # svm = SVM()
    # nb = NB()
    # maxe = MAXE()
    # run_experiment(maxe, "MAXE_filter", "filter")


if __name__ == '__main__':
    main()
    # data = load_json("../data/clean_datasets/train_test_clean/filter/train.json")
    # stats(data)

    # nb = NB()
    # nb.load("models/NB_Filter")

    # me = MAXE()
    # me.load("models/MAXE_filter")

    # s = ["who developed oil filter"]

    # print me.predict(s)


    # print nb.model.best_score_
    # nb_norm = NB()
    # nb_norm.load("models/NB_Order_Normalized_5_grams")


    # svm = SVM()
    # svm.load("models/SVM_Order_Normalized_5_grams")
    # print svm.model.best_params_
    # print svm.predict_proba(["is mohamed emad still dead"])

    # data = load_json("../data/clean_datasets/train_test_clean/filter/test.json")
    # x_test, y_test = zip(*data)
    # deep_test(nb, x_test, y_test)

    # x = ["what is back street boys first album", "who is the second president of usa"]
    # x_norm = normalize_numbers(x)

    # print svm.predict_proba(x_norm)
    # print nb_norm.predict_proba(x_norm)







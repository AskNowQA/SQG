import json, os, pickle
from random import shuffle
from sklearn.model_selection import train_test_split
from learning.classifier.svmclassifier import SVMClassifier
from learning.classifier.naivebayesclassifier import NaiveBayesClassifier


# Loads a JSON file
def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


def save_json(data, name):
    with open(name, "w") as data_file:
        json.dump(data, data_file, sort_keys=True, indent=4, separators=(',', ': '))


# Saves a pickle object
def save_pickle(data, name):
    with open(name, "w") as data_file:
        pickle.dump(data, data_file)


def load_training_data(path="./data/clean_datasets/combined_datasets/"):
    files = []
    for file in os.listdir(path):
        if "dbpedia" in file:
            files.append(file)

    list_, ask, count, order, filter_, agg = [], [], [], [], [], []

    for f in files:
        if "list" in f:
            data = load_json(path+f)
            x_tmp = [row["question"] for row in data]
            y_tmp = [0]*len(data)
            list_ = zip(x_tmp, y_tmp)
        if "ask" in f:
            data = load_json(path+f)
            x_tmp = [row["question"] for row in data]
            y_tmp = [1]*len(data)
            ask = zip(x_tmp, y_tmp)
        if "count" in f:
            data = load_json(path + f)
            x_tmp = [row["question"] for row in data]
            y_tmp = [2]*len(data)
            count = zip(x_tmp, y_tmp)
        if "order" in f:
            data = load_json(path+f)
            x_tmp = [row["question"] for row in data]
            y_tmp = [3]*len(data)
            order = zip(x_tmp, y_tmp)
        if "filter" in f:
            data = load_json(path+f)
            x_tmp = [row["question"] for row in data]
            y_tmp = [4]*len(data)
            filter_ = zip(x_tmp, y_tmp)
        if "aggregate" in f:
            data = load_json(path+f)
            x_tmp = [row["question"] for row in data]
            y_tmp = [5]*len(data)
            agg = zip(x_tmp, y_tmp)

    data = {"list": list_, "ask": ask, "count": count, "order": order, "filter": filter_, "agg": agg}

    return data


# splits data into training test and validation
def split_training_data(data, agg=False, range_=-1, desc=""):

    assert isinstance(data, dict), "Data is not of type Dict"
    keys = dict(data).keys()

    if not agg:
        keys.remove("agg")

    results = []

    for k in keys:
        results += data[k][:range_]

    shuffle(results)
    x, y = zip(*results)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3)

    # save_pickle([x_train, y_train, x_test, y_test], "./data/classifiers/data/data_{}.pickle".format(desc))

    save_path = "./data/classifiers/data/data_{}.json".format(desc)

    save_json({"x_train": x_train, "y_train": y_train, "x_test": x_test, "y_test": y_test},
              save_path)

    return save_path


def prepare_training_data(path="./data/clean_datasets/combined_datasets/", split_range=1500, desc=""):

    data = load_training_data(path)
    save_path = split_training_data(data, agg=False, range_=split_range, desc=str(split_range)+desc)

    split_data = load_json(save_path)
    x_train = split_data["x_train"]
    y_train = split_data["y_train"]
    x_test = split_data["x_test"]
    y_test = split_data["y_test"]

    return x_train, y_train, x_test, y_test


def run_classifier(x_train, y_train, type_="NB", desc=""):

    if type_ == "NB":
        return train_classifier_NB(x_train, y_train, desc)
    elif type_ == "SVM":
        return train_classifier_SVM(x_train, y_train, desc)


def train_classifier_NB(x, y, desc=""):
    classifier = NaiveBayesClassifier()
    classifier.train(x, y)
    with open("data/classifiers/NB{}.pickle".format("_%s" % desc), "w") as data_file:
        pickle.dump(classifier, data_file)
    return classifier


def train_classifier_SVM(x, y, desc=""):
    classifier = SVMClassifier()
    classifier.train(x, y)
    with open("data/classifiers/SVM{}.pickle".format("_%s" % desc), "w") as data_file:
        pickle.dump(classifier, data_file)
    return classifier


def test_classifier(classifier, x_test, y_test):
    y_hyp = classifier.predict(x_test)
    tp = 0
    for hyp, ref, question in zip(y_hyp, y_test, x_test):
        if hyp == ref:
            tp += 1
        else:
            print question + " ",
            print hyp
            print ref

    score = tp*100.0/len(y_test)
    print score
    print len(y_test)

    return score, len(y_test)


def run_experiment(split_range=1500):

    x_train, y_train, x_test, y_test = prepare_training_data(split_range=split_range)

    classifier = run_classifier(x_train, y_train, desc=str(split_range))
    nb_score = test_classifier(classifier, x_test, y_test)

    classifier = run_classifier(x_train, y_train, type_="SVM", desc=str(split_range))
    svm_score = test_classifier(classifier, x_test, y_test)

    print "NB Accuracy: {}".format(nb_score)
    print "SVM Accuracy: {}".format(svm_score)

    # run_classifier(x_train, y_train, type_="NB", desc=str(split_range))

if __name__ == '__main__':
    print "SQG QA Classifier !!!"

    run_experiment(split_range=-1)


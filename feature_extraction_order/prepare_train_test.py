from helper import *
from order_property import get_order_property
from random import shuffle
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.data.path.append("/Users/just3obad/Desktop/Thesis/Libraries/nltk_data")
stop_words = set(stopwords.words('english'))


# Takes clean one hop data, preps a hash with questions for each property for train/test split later.
def prep_train_test_hash(path):
    data = load_json(path)
    print "Total no. of questions:", len(data)

    properties_hash = {}
    for row in data:
        property_ = get_order_property(row["query"])
        row["property"] = property_
        row["one_hop_ontologies"] = [o.replace("http://dbpedia.org/ontology/", "") for o in row["one_hop_ontologies"]]

        if property_ in properties_hash:

            properties_hash[property_]["sum"] += 1
            properties_hash[property_]["prop_list"].append(row)

        else:
            properties_hash[property_] = {"sum": 1, "prop_list": [row]}

    save_json(properties_hash, "out/train_test_TEST.json")

    # Checksum
    count = 0
    for key, value in properties_hash.iteritems():
        sum_ = value["sum"]
        count += sum_
    print len(data), count
    if count == len(data):
        print "Checksum OK"
    else:
        print "Checksum ERROR"

    return properties_hash


def prep_train_test(data, split=0.35):
    train, test = [], []

    for key, value in data.iteritems():
        train_split, test_split = split_array(value["prop_list"], split)
        train += train_split
        test += test_split

    shuffle(train)
    shuffle(test)

    save_json(train, "data/train.json")
    save_json(test, "data/test.json")


# Takes an array, shuffles it and splits it into two parts.
# Takes Test data percentage in decimals 0.2, 0.3, etc.
def split_array(arr, split):
    shuffle(arr)
    limit = int(len(arr) * (1-split))
    # print limit
    return arr[:limit], arr[limit:]


# Prints Stats for Train/Test data
def stats(train_path, test_path):
    train = load_json(train_path)
    test = load_json(test_path)

    train_hash = {}
    test_hash = {}

    for row in train:
        prop = get_order_property(row["query"])
        if prop in train_hash:
            train_hash[prop] += 1
        else:
            train_hash[prop] = 1

    for row in test:
        prop = get_order_property(row["query"])
        if prop in test_hash:
            test_hash[prop] += 1
        else:
            test_hash[prop] = 1

    print "Train data size:", len(train), "questions"
    print "Test data size:", len(test), "questions"

    for x, y in zip(train_hash.iteritems(), test_hash.iteritems()):
        print x[0], ":", x[1], y[1]


# Takes a question and returns a clean one without stopwords/
def clean_question(question):
    tokens = word_tokenize(question)
    new_tokens = []
    for t in tokens:
        try:
            t.encode("ascii")
            new_tokens.append(t)
        except:
            continue

    additions = ["most", "least", "new", "last", "latest", "top", "t"]
    question = " ".join([t for t in new_tokens if t in additions or t not in stop_words])
    return question


def prepare_train_test_2(data, ontologies):
    train, test = [], []

    for key, value in data.iteritems():
        if key in ontologies:
            test += value["prop_list"]
        else:
            train += value["prop_list"]

    shuffle(train)
    shuffle(test)

    save_json(train, "data/train_1.json")
    save_json(test, "data/test_1.json")


def main():
    print "MAIN"
    data = prep_train_test_hash("data/one_hop_ontologies_clean.json")
    # prep_train_test(data)
    prepare_train_test_2(data, ["numberOfPages", "populationTotal", "races"])
    # stats("data/train.json", "data/test.json")

    # print stop_words


if __name__ == '__main__':
    main()

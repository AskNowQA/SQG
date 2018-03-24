import fnmatch
import os
import sys
import json
import re
import pickle
from random import shuffle
from learning.classifier.svmclassifier import SVMClassifier
from learning.classifier.naivebayesclassifier import NaiveBayesClassifier
from sklearn.model_selection import train_test_split


def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


def load_txt(path):
    with open(path) as data_file:
        return data_file.read().split("\n")


# Get Sort Questions from qald xml
def get_sort_questions_qald():
    # with open("output/qald/")
    matches = []
    questions = []
    for root, dir_names, file_names in os.walk('output/qald'):
        for filename in fnmatch.filter(file_names, '*.json'):
            matches.append(os.path.join(root, filename))
    # print matches
    for m in matches:
        data = load_json(m)
        for row in data:
            if "ORDER" in row["query"]:
                questions.append(row["question"])
    return questions


def get_sort_questions_brmson():
    questions = []
    data = load_txt("data/brmson/train_5500.label.txt")
    for row in data:
        if "est" in row or "most" in row or "least" in row:
            row = re.sub(r"[a-zA-z]+:[a-zA-z]+", "", row)
            questions.append(row)

    superlatives = load_json("data/ComplexQuestionsOrder/superlatives.json")
    ordinals = load_json("data/ComplexQuestionsOrder/ordinals.json")
    questions_true = []
    questions_false = []
    for q in questions:
        flag = False
        for s in superlatives:
            if s in q.decode('ascii', 'ignore'):
                flag = True
                break
        for o in ordinals:
            if o in q.decode('ascii', 'ignore'):
                flag = True
                break
        if flag:
            questions_true.append(q)
        else:
            questions_false.append(q)
    return questions_true, questions_false


def merge_sort_questions():
    qald = get_sort_questions_qald()
    brmson_1, brmson_2 = get_sort_questions_brmson()
    result = []
    for q in brmson_1:
        result.append(clean_question(q.decode('ascii', 'ignore')))
    for q in qald:
        result.append(clean_question(q))

    with open("data/ComplexQuestionsOrder/data_v1.json", "w") as data_file:
        json.dump(result, data_file, sort_keys=True, indent=4, separators=(',', ': '))

    with open("data/ComplexQuestionsOrder/data_v1_false.json", "w") as data_file:
        json.dump(brmson_2, data_file, sort_keys=True, indent=4, separators=(',', ': '))


# Transforms superlatives
def prep_superlatives():
    superlatives = []
    data = load_txt("data/ComplexQuestionsOrder/superlatives.txt")
    for row in data:
        if row != "":
            superlatives.append(row)
    with open("data/ComplexQuestionsOrder/superlatives.json", "w") as data_file:
        json.dump(superlatives, data_file, sort_keys=True, indent=4,separators=(',', ': '))


def prep_numbers_ordinals():
    ordinals = []
    data = load_txt("data/ComplexQuestionsOrder/numbers.txt")
    for row in data:
        col = row.split("\t")
        for c in col:
            if re.match(r"[a-zA-Z]{3,}", c):
                ordinals.append(c)
    with open("data/ComplexQuestionsOrder/ordinals.json", "w") as data_file:
        json.dump(ordinals, data_file, sort_keys=True, indent=4, separators=(',', ': '))


def get_lcquad_questions():
    questions = []
    data = load_json("data/LC-QUAD/linked_answer6.json")
    for row in data:
        questions.append(clean_question(row["question"]))

    with open("data/ComplexQuestionsOrder/lcquad_all.json", "w") as data_file:
        json.dump(questions, data_file, sort_keys=True, indent=4, separators=(',', ': '))

    return questions


def construct_training_data_binary():
    data_1 = load_json("data/ComplexQuestionsOrder/data_v1.json")
    data_2 = load_json("data/ComplexQuestionsOrder/lcquad_all.json")[:1500]
    data_1_labels = [1]*len(data_1)
    data_2_labels = [0]*len(data_2)
    data_labels_final = data_1_labels + data_2_labels
    data_final = data_1+data_2
    labeled_data = zip(data_final, data_labels_final)
    shuffle(labeled_data)
    x, y = zip(*labeled_data)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)

    with open("data/ComplexQuestionsOrder/train_test.pickle", "w") as data_file:
        pickle.dump([x_train, x_test, y_train, y_test], data_file)

    return x_train, x_test, y_train, y_test


def train_classifier(x_train, y_train):
    # classifier = SVMClassifier()
    classifier = NaiveBayesClassifier()
    classifier.train(x_train, y_train)
    with open("data/ComplexQuestionsOrder/naive_bayes.pickle", "w") as data_file:
        pickle.dump(classifier, data_file)
    return classifier


def test_classifier(classifier, x_test, y_test):
    y_hyp = classifier.predict(x_test)
    tp = 0
    for hyp, ref, question in zip(y_hyp, y_test, x_test):
        if hyp == ref:
            tp += 1
            print question + " ",
            print hyp

    print tp*100.0/len(y_test)
    print len(y_test)


def clean_question(q):
    q = q.lower()
    q = q.replace(" 's", " is")
    q = re.sub(r"\?|'|,|\.|`|\\|\"", "", q)
    q = re.sub(r" {2,}|-", " ", q)
    q = re.sub(r"\t", " ", q)
    q = q.strip()
    return q


if __name__ == "__main__":
    print "HELLO THERE, BITCHESSS !!!"
    # prep_superlatives()
    # ques_1 = get_sort_questions_qald()
    # ques_1, ques_2 = get_sort_questions_brmson()
    # ques_1 = get_lcquad_questions()
    # print len(ques_1)
    # print len(quRes_2)
    # for q in ques_1:
    #     print q
    # merge_sort_questions()
    # x_train, x_test, y_train, y_test = construct_training_data_binary()

    # with open("data/ComplexQuestionsOrder/train_test.pickle") as data_file:
    #     x_train, x_test, y_train, y_test = pickle.load(data_file)

    # classifier = train_classifier(x_train, y_train)

    # with open("data/ComplexQuestionsOrder/naive_bayes.pickle") as data_file:
    #     classifier = pickle.load(data_file)

    # test_classifier(classifier, x_test, y_test)


    data, x = get_sort_questions_brmson()

    print len(data)

    # 229 QALD annotated
    # 381 brmson manually annotated





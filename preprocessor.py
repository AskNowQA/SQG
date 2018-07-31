# -*- coding: utf-8 -*-
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


def save_json(path, results):
    with open(path, "w") as data_file:
        json.dump(results, data_file, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)


# Get Sort Questions from qald xml from Output/qald
def get_order_questions_qald():
    path = "output/qald"
    # path = "./data/clean_datasets/qald/"
    matches = []
    questions = set()
    for root, dir_names, file_names in os.walk(path):
        for filename in fnmatch.filter(file_names, '*.json'):
            matches.append(os.path.join(root, filename))
    # print matches
    for m in matches:
        data = load_json(m)
        for row in data:
            if "ORDER" in row["query"]:
                questions.add(row["question"].encode("utf-8"))
    return list(questions)


# Gets Order questions from qald clean dataset data/clean_datasets/qlad
def get_order_questions_qlad_clean():
    path = "./data/clean_datasets/qald/"
    result = []
    for f in os.listdir(path):
        data = load_json(path+f)
        for row in data:
            if "order" in row[1].lower():
                result.append(row[0].encode("utf-8"))
    return result


def get_sort_questions_brmson():
    questions = set()
    data = load_txt("data/questions_only/brmson/train_5500.label.txt")
    for row in data:
        if "est" in row or "most" in row or "least" in row:
            row = re.sub(r"[a-zA-z]+:[a-zA-z]+", "", row)
            questions.add(row)

    superlatives = load_json("data/ComplexQuestionsOrder/superlatives.json")
    ordinals = load_json("data/ComplexQuestionsOrder/ordinals.json")
    questions_true = set()
    questions_false = set()
    for q in questions:
        flag = False
        for s in superlatives:
            if s.encode("utf-8") in q:
                flag = True
                break
        for o in ordinals:
            if o.encode("utf-8") in q:
                flag = True
                break
        if flag:
            questions_true.add(q)
        else:
            questions_false.add(q)
    return list(questions_true), list(questions_false)


def get_order_questions_dbnqa():
    path = "./data/clean_datasets/dbnqa/dbnqa_clean.json"
    data = load_json(path)
    result = []
    for row in data:
        if "filter" in row[1].lower():
            # result.append(row[0].encode("utf-8"))
            result.append([row[0].encode("utf-8"), row[1].encode("utf-8")])
    return result


def merge_sort_questions():
    qald = get_order_questions_qald()
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
    print "Here We Go !!!"
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
        # x_train, x_test, y_train, y_test = pickle.load(data_file)

    # classifier = train_classifier(x_train, y_train)

    # with open("data/ComplexQuestionsOrder/naive_bayes.pickle") as data_file:
    #     classifier = pickle.load(data_file)

    # test_classifier(classifier, x_test, y_test)


    # data, x = get_sort_questions_brmson()

    # print len(data)

    # 64 QALD annotated
    # 381 brmson manually annotated
    # 3900 dbnqa


    #2700 filter dbnqa


    # data = get_order_questions_dbnqa()
    # print len(data)
    # save_json("output/dbnqa_order_filter_questions.json", data)

    get_order_questions_qald()

    

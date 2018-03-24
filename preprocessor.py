import fnmatch
import os
import sys
import json
import re


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
        result.append(q.decode('ascii', 'ignore'))
    for q in qald:
        result.append(q)


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





if __name__ == "__main__":
    print "HELLO THERE, BITCHESSS !!!"
    # prep_superlatives()
    # ques_1 = get_sort_questions_qald()
    # ques_1, ques_2 = get_sort_questions_brmson()
    # print len(ques_1)
    # print len(ques_2)
    # for q in ques_1:
    #     print q
    # merge_sort_questions()






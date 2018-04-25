import json
import argparse
import os
# from query_gen import get_question_index
from parser.lc_quad_linked import LC_Qaud_Linked
import re
from parser.qald import Qald
from json import dumps
import glob
import fnmatch
import sys


def load_file(name):
    with open("output/{}".format(name)) as data_file:
        return json.load(data_file)


# takes the query_gen output file format not the analysis_deep format
def basic_stats(data):
    correct = incorrect = no_path = no_answer =  0
    for i in data:
        if i['answer'] == "correct":
            correct +=1
        elif i['answer'] == "-incorrect":
            incorrect +=1
        elif i['answer'] == "-without_path":
            no_path +=1
        elif i['answer'] == "-no_answer":
            no_answer +=1

    print "AA-- Basic Stats --"
    print "AA-  Total Questions: %d" % (correct+incorrect+no_path+no_answer)
    print "AA-  Correct: %d" % correct
    print "AA-  Incorrect: %d" % incorrect
    print "AA-  No-Path: %d" % no_path
    print "AA-  No-Answer: %d" % no_answer

    if correct+incorrect != 0:
        precision = (correct*100)/float(correct+incorrect)
    else:
        precision = 0

    recall = (correct*100)/float(correct+no_path+no_answer)
    if recall+precision != 0:
        f1 = (2*precision*recall)/float(precision+recall)
    else:
        f1 = 0

    print "AA-  Precision: %.2f" % precision
    print "AA-  Recall: %.2f" % recall
    print "AA-  F1: %.2f" % f1
    return correct, incorrect, no_path, no_answer


# Get incorrect data and saves them in a json file externally with categoreis
def deep_analysis(path):
    result = {}
    other = []
    sort = []
    boolean = []
    union = []
    filter = []
    text = []
    having = []
    group = []
    filter_union = []
    sum = []
    num = path[-1]

    for file in os.listdir(path):
        if file.endswith(".json"):
            data = load_file("qald/%s/" % num + file)
            for d in data:
                pair = {"SPARQL": "", "Question": ""}
                if d["answer"] == "-without_path":
                    pair["SPARQL"] = d["query"]
                    pair["Question"] = d["question"]
                    if "order" in d["query"].lower():
                        sort.append(pair)
                    elif "ask " in d["query"].lower():
                        boolean.append(pair)
                    elif "sum" in d["query"].lower():
                        sum.append(pair)
                    elif "filter" in d["query"].lower() and "union" in d["query"].lower():
                        filter_union.append(pair)
                    elif "filter" in d["query"].lower():
                        filter.append(pair)
                    elif "union" in d["query"].lower():
                        union.append(pair)
                    elif "text" in d["query"].lower():
                        text.append(pair)
                    elif "having" in d["query"].lower():
                        having.append(pair)
                    elif "group" in d["query"].lower():
                        group.append(pair)
                    else:
                        other.append(pair)
    result["Other"] = {"Length": len(other), "Value": other}
    result["Sort"] = {"Length": len(sort), "Value": sort}
    result["Boolean"] = {"Length": len(boolean), "Value": boolean}
    result["Union"] = {"Length": len(union), "Value": union}
    result["Filter"] = {"Length": len(filter), "Value": filter}
    result["Text"] = {"Length": len(text), "Value": text}
    result["Having"] = {"Length": len(having), "Value": having}
    result["Group"] = {"Length": len(group), "Value": group}
    result["Filter_Union"] = {"Length": len(filter_union), "Value": filter_union}
    result["Sum"] = {"Length": len(sum), "Value": sum}
    with open("output/deep_analysis_qald/qald_%s.json" % num, "w") as data_file:
        json.dump(result, data_file, sort_keys=True, indent=4, separators=(',', ': '))


# Input Question output index in the dataset
def get_question_index(question):
    ds = LC_Qaud_Linked("./data/LC-QUAD/linked_answer6.json")
    ds.load()
    ds.parse()
    for i in range(0, len(ds.qapairs)):
        if question == ds.qapairs[i].question.text:
            print "Question id:" ,i
            return i


# Input question list, out put query gen
def get_question_query(questions):
    s = ""
    for q in questions:
        id = get_question_index(q)
        s+=(" %s" % id)
    os.system("python query_gen.py --in %s" % s)


# Compares two queries
def compare_query(q1, q2):
    # Find a list of the variables in the queries
    vars1 = re.findall(r"\?\w+",q1)
    vars2 = re.findall(r"\?\w+",q2)

    vars1s = []
    vars2s = []
    
    for i, j in zip(vars1,vars2):
        if i not in vars1s:
            vars1s.append(i)
        if j not in vars2s:
            vars2s.append(j)

    # If no. of variables are not the same return false
    if len(vars1s) != len(vars2s):
        print "Step 1"
        return False

    q1n = q1
    q2n = q2
    idx = 0
    while idx < len(vars1) and idx < len(vars2):
        q1n = q1n.replace(vars1[idx],"?VAR_{}".format(idx))
        q2n = q2n.replace(vars2[idx],"?VAR_{}".format(idx))
        idx+=1

    q1n_no_space = q1n.replace(" ","").replace(".}","}")
    q2n_no_space = q2n.replace(" ","").replace(".}","}")

    # if initial queries are the same true. spaces and . at the end are removes
    if q1n_no_space == q2n_no_space:
        print "Step 2"
        return True

    q1_predicates = re.search(r'{.*}', q1n_no_space).group(0)
    q2_predicates = re.search(r'{.*}', q2n_no_space).group(0)

    q1_predicates = re.sub(r"(http://www.w3.org/)|(http://dbpedia.org/)|{|}","",q1_predicates).split('.')
    q2_predicates = re.sub(r"(http://www.w3.org/)|(http://dbpedia.org/)|{|}", "", q2_predicates).split('.')

    # if queries are the same but predicates are in the wrong order, return true.
    # q2 has to be the gold query
    print q1_predicates
    print q2_predicates

    for i in q2_predicates:
        if i not in q1_predicates:
            print "lalal"
            return False
    return True


# Runs the Query Gen on a Qald Folder
def analysis_qald(num):
    matches = []
    for root, dir_names, file_names in os.walk('data/QALD'):
        for filename in fnmatch.filter(file_names, '*.json'):
            if "questions" not in filename and num in root and "raw" not in filename:
                matches.append(os.path.join(root, filename))

    for m in matches:
        print "AA ds", m
        name = re.search(r"(\w+-)*\w+\.\w+", m).group(0)
        try:
            os.system("python query_gen.py --path {} --file qald/{}/{} > output/qald/{}/{}.log".format(m, num, name, num, name))
        except:
            sys.exit("EXITED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate SPARQL query')
    parser.add_argument("--file", help="file name to save the results", default="tmp", dest="file_name")
    args = parser.parse_args()
    file = args.file_name

    # data = load_file("tmp")

    # qald_list = [1, 2, 3, 4, 5, 7]
    # for i in qald_list:
    #     analysis_qald(str(i))


    # os.system("python query_gen.py --path %s" % "/Users/just3obad/Desktop/Thesis/AskNow/SQG/data/QALD/7/data/qald-7-train-largescale.xml")
    # basic_stats(load_file("tmp"))
    # analysis_x()
    # analysis_qald("6")
    deep_analysis("output/qald/7")

    





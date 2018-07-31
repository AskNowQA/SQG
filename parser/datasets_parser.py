# -*- coding: utf-8 -*-
# Parser for Datasets included in /data/.
import json, os, sys, fnmatch, re


def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


def load_txt(path):
    with open(path) as data_file:
        return data_file.read().split("\n")


def save_json(path, results):
    with open(path, "w") as data_file:
        json.dump(results, data_file, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)


def parse_squad():
    path = load_json("../data/questions_only/Squad/dev-v2.0.json")
    data = open(path)
    print len(data)


def parse_QAD():
    path = "../data/questions_only/Question_Answer_Dataset_v1.2/"
    files = [f for f in os.listdir(path) if f.endswith("txt")]
    questions = set()
    for f in files:
        data = load_txt(path+f)
        del data[0]
        for line in data:
            if len(line) != 0:
                line_splits = line.split("\t")
                question = line_splits[1]
                if question != "NULL" and len(question) != 0:
                    questions.add(question)

    print len(questions)
    save_json("../data/clean_datasets/QAD_questions.json", list(questions))


def parse_wiki_qa():
    path = "../data/questions_only/WikiQACorpus/"
    files = ["WikiQA-train.txt", "WikiQA-test.txt"]

    questions = set()

    for f in files:
        data = load_txt(path+f)
        for line in data:
            line_split = line.split("\t")
            question = line_split[0]
            if len(question) != 0:
                questions.add(question)
    print len(questions)
    save_json("../data/clean_datasets/WikiQA_questions.json", list(questions))


def parse_complex_web_questions():
    path = "../data/Not DBpedia Labelled/ComplexWebQuestions/"
    files = [f for f in os.listdir(path) if f.endswith("json")]

    result = []
    for f in files:
        data = load_json(path + f)
        for row in data:
            tmp = {"query": row["sparql"], "question": row["question"]}
            result.append(tmp)

    print len(result)
    save_json("../data/clean_datasets/" + "ComplexWeQquestions_dataset.json", result)


def parse_freebase():
    path = "../data/Not DBpedia Labelled/freebase/"
    files = [f for f in os.listdir(path) if f.endswith("json")]

    result = []
    for f in files:
        data = load_json(path + f)
        for row in data:
            tmp = {"query": row["targetFormula"], "question": row["utterance"]}
            result.append(tmp)

    print len(result)
    save_json("../data/clean_datasets/" + "freebase_dataset.json", result)


def parse_graph_questions():
    path = "../data/Not DBpedia Labelled/GraphQuestions-master/freebase13/"
    files = [f for f in os.listdir(path) if f.endswith("json")]

    result = []
    for f in files:
        data = load_json(path + f)
        for row in data:
            tmp = {"query": row["sparql_query"], "question": row["question"]}
            result.append(tmp)

    print len(result)
    save_json("../data/clean_datasets/" + "graph_dataset.json", result)


def parse_simple_questions():
    path_1 = "../data/Not DBpedia Labelled/SimpleQuestions_v2/annotated_fb_data_train.txt"
    path_2 = "../data/Not DBpedia Labelled/SimpleQuestions_v2/annotated_fb_data_test.txt"
    files = [path_1, path_2]

    questions = []
    for f in files:
        data = load_txt(f)
        for row in data:
            line_split = row.split("\t")
            question = line_split[-1]
            questions.append(question)
    save_json("../data/clean_datasets/simple_questions_questions.json", questions)


def parse_webqsp_questions():
    path = "../data/Not DBpedia Labelled/WebQSP/data/"
    files = [f for f in os.listdir(path) if f.endswith("json") and "partial" not in f]

    result = []
    for f in files:
        data = load_json(path + f)
        for row in data["Questions"]:
            tmp = {"query": row["Parses"][0]["Sparql"], "question": row["RawQuestion"]}
            result.append(tmp)

    print len(result)
    save_json("../data/clean_datasets/" + "webqsp_dataset.json", result)


def parse_wiki_data_simple_questions():
    path = "../data/Not DBpedia Labelled/wikidata-simplequestions-master/qald-format/"
    files = [f for f in os.listdir(path) if f.endswith("json") and "full" in f]

    result = []
    for f in files:
        data = load_json(path + f)
        for row in data["questions"]:
            tmp = {"query": row["query"]["sparql"].encode("utf-8"), "question": row["question"][0]["string"].encode("utf-8")}
            result.append(tmp)

    print len(result)
    save_json("../data/clean_datasets/" + "wiki_data_simple_questions_dataset.json", result)


def parse_qald():
    path = "../output/qald"

    matches = []
    result = list()
    for root, dir_names, file_names in os.walk(path):
        for filename in fnmatch.filter(file_names, '*.json'):
            matches.append(os.path.join(root, filename))

    for m in matches:
        data = load_json(m)
        for row in data:
            tmp = {"question": row["question"], "query": row["query"]}
            result.append(tmp)

    print len(result)
    save_json("../data/clean_datasets/qald_dataset.json", result)
    # return list(questions)


def parse_brmson():
    data = load_txt("../data/questions_only/brmson/train_5500.label.txt")
    questions = set()
    for line in data:
        question = re.sub(r"\w*:\S+", "", line)
        questions.add(question)
    print len(questions)
    save_json("../data/clean_datasets/brmson.json", list(questions))




def main():
    parse_QAD()
    # parse_wiki_qa()
    # parse_complex_web_questions()
    # parse_freebase()
    # parse_graph_questions()
    # parse_simple_questions()
    # parse_webqsp_questions()
    # parse_wiki_data_simple_questions()
    # parse_qald()
    # parse_brmson()

if __name__ == "__main__":
    print "Here We Go !!!"
    main()
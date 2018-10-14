# -*- coding: utf-8 -*-
import inflect
import json
import os
import re
import inspect
import copy

from nltk.tokenize import RegexpTokenizer
from tqdm import tqdm


def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


def save_json(path, results):
    with open(path, "w") as data_file:
        json.dump(results, data_file, sort_keys=True, indent=4, separators=(',', ': '))


def save_questions(name, list_, ask, count, order, filter_, agg):
    caller = inspect.stack()[1][3]

    if caller == "prepare_datasets":
        save_json("../data/clean_datasets/dbpedia/list_{}.json".format(name), list_)
        save_json("../data/clean_datasets/dbpedia/ask_{}.json".format(name), ask)
        save_json("../data/clean_datasets/dbpedia/count_{}.json".format(name), count)
        save_json("../data/clean_datasets/dbpedia/order_{}.json".format(name), order)
        save_json("../data/clean_datasets/dbpedia/filter_{}.json".format(name), filter_)
        save_json("../data/clean_datasets/dbpedia/agg_{}.json".format(name), agg)

    if caller == "combine_datasets":
        save_json("../data/clean_datasets/combined_datasets/list_{}.json".format(name), list_)
        save_json("../data/clean_datasets/combined_datasets/ask_{}.json".format(name), ask)
        save_json("../data/clean_datasets/combined_datasets/count_{}.json".format(name), count)
        save_json("../data/clean_datasets/combined_datasets/order_{}.json".format(name), order)
        save_json("../data/clean_datasets/combined_datasets/filter_{}.json".format(name), filter_)
        save_json("../data/clean_datasets/combined_datasets/agg_{}.json".format(name), agg)


def get_questions(name, data_set):
    list_, ask, count, order, filter_, agg = [], [], [], [], [], []
    for row in tqdm(data_set, desc="Processing Dataset: "):
        question = clean_question(row["question"])
        query = clean_query(row["query"])

        if not query or not question:
            continue

        query_head = re.findall(r"^.*where", query)
        if query_head:
            query_head = query_head[0]

        line = {"query": query, "question": question, "dataset": name, "type": ""}

        if "select" in query_head and "count" not in query_head:
            tmp = copy.deepcopy(line)
            tmp["type"] = "list"
            list_.append(tmp)
        if "ask where" in query:
            tmp = copy.deepcopy(line)
            tmp["type"] = "ask"
            ask.append(tmp)
        if "select" in query_head and "count" in query_head:
            tmp = copy.deepcopy(line)
            tmp["type"] = "count"
            count.append(tmp)
        if "order by" in query:
            tmp = copy.deepcopy(line)
            tmp["type"] = "order"
            order.append(tmp)
        if "filter " in query:
            query = query.replace("filter (lang", "")
            tmp = copy.deepcopy(line)
            tmp["type"] = "filter"
            filter_.append(tmp)
        if "select sum" in query or "select avg" in query or "select max" in query or "select min" in query:
            tmp = copy.deepcopy(line)
            tmp["type"] = "agg"
            agg.append(tmp)

    list_ = {v['question']: v for v in list_}.values()
    ask = {v['question']: v for v in ask}.values()
    count = {v['question']: v for v in count}.values()
    order = {v['question']: v for v in order}.values()
    filter_ = {v['question']: v for v in filter_}.values()
    agg = {v['question']: v for v in agg}.values()

    return list_, ask, count, order, filter_, agg


def clean_question(q):
    q = q.strip()
    q = q.lower()
    q = q.replace("&", "and")
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(q)

    for i, tk in enumerate(tokens):
        if tk.isdigit():
            p = inflect.engine()
            num = ' '.join(tokenizer.tokenize(p.number_to_words(int(tk))))
            tokens[i] = num

    return ' '.join(tokens)


def clean_query(q):
    q = q.strip()
    q = q.lower()
    q = q.replace("\n", " ")
    return q


# Parse dbpedia dataset into multiple files based on the question type
def prepare_datasets():
    data_sets = ['../data/clean_datasets/raw/qald_dataset.json', '../data/clean_datasets/raw/lcquad_dataset.json',
                 '../data/clean_datasets/raw/dbnqa_dataset.json']

    for d in data_sets:
        print "Dataset: ", d
        data_set = load_json(d)
        name = re.findall(r"\w+.json", d)[0].replace("_dataset.json", "")
        list_, ask, count, order, filter_, agg = get_questions(name, data_set)
        save_questions(name, list_, ask, count, order, filter_, agg)


def combine_datasets(path="../data/clean_datasets/dbpedia/", remove_=""):

    if remove_ == "lcquad":
        files = [f for f in os.listdir(path) if f.endswith(".json") and "lcquad" not in f]
    elif remove_ == "qald":
        files = [f for f in os.listdir(path) if f.endswith(".json") and "qald" not in f]
    elif remove_ == "dbnqa":
        files = [f for f in os.listdir(path) if f.endswith(".json") and "dbnqa" not in f]
    else:
        files = [f for f in os.listdir(path) if f.endswith(".json")]

    list_, ask, count, order, filter_, agg = [], [], [], [], [], []

    for f in tqdm(files, desc="Combining Datasets"):
        data = load_json(path + f)

        if "list" in f:
            list_ += data
        if "ask" in f:
            ask += data
        if "count" in f:
            count += data
        if "order" in f:
            order += data
        if "filter" in f:
            filter_ += data
        if "agg" in f:
            agg += data

    list_ = {v['question']: v for v in list_}.values()
    ask = {v['question']: v for v in ask}.values()
    count = {v['question']: v for v in count}.values()
    order = {v['question']: v for v in order}.values()
    filter_ = {v['question']: v for v in filter_}.values()
    agg = {v['question']: v for v in agg}.values()

    print "No. List Questions: %d" % len(list_)
    print "No. Ask Questions: %d" % len(ask)
    print "No. Count Questions: %d" % len(count)
    print "No. Order Questions: %d" % len(order)
    print "No. Filter Questions: %d" % len(filter_)
    print "No. Agg Questions: %d" % len(agg)

    if remove_ == "lcquad" or remove_ == "qald" or remove_ == "dbnqa":
        tmp = ["lcquad", "qald", "dbnqa"]
        tmp.remove(remove_)
        save_questions('_'.join(tmp), list_, ask, count, order, filter_, agg)
    else:
        save_questions("all", list_, ask, count, order, filter_, agg)


def main():
    print "### Main ###"
    prepare_datasets()
    combine_datasets()


if __name__ == '__main__':
    print "Here We Go !!!"
    main()

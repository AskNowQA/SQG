# -*- coding: utf-8 -*-

from generator_utils import decode
from tqdm import tqdm
import json

path = "../data/DBpedia/dbnqa/"


def load_file(path):
    with open(path) as data_file:
        data = data_file.readlines()
    return data


def load_json(path):
    with open(path, "r") as data_file:
        data = json.load(data_file)
    return data


def load_questions():
    questions = "{}data.en".format(path)
    return load_file(questions)


def load_sparqls():
    sparqls = "{}data.sparql".format(path)
    return load_file(sparqls)


def save_json(path, results):
    with open(path, "w") as data_file:
        json.dump(results, data_file, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)


def parse():
    questions = load_questions()
    raw_queries = load_sparqls()
    result = []
    for row, q in tqdm(zip(raw_queries, questions), desc="Parsing DBNQA Dataset"):

        tmp = {"query": decode(row.strip()), "question": q.strip()}
        result.append(tmp)
    save_json("../data/clean_datasets/dbnqa_dataset.json", result)
    return result


def basic_stats():
    path = "../data/clean_datasets/dbnqa_clean.json"
    data = load_json(path)
    print "Total No. of Questions: %s" % len(data)


if __name__ == "__main__":
    print "Here We Go !!!"

    # print len(load_questions())

    parse()
    # basic_stats()

    # print data[:10]

# -*- coding: utf-8 -*-
import json, os, re


def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


def load_txt(path):
    with open(path) as data_file:
        return data_file.read().split("\n")


def save_json(path, results):
    with open(path, "w") as data_file:
        json.dump(results, data_file, sort_keys=True, indent=4, separators=(',', ': '))


def get_complex_questions(path="./data/clean_datasets/"):

    datasets = []
    questions_only = []
    for f in os.listdir(path):
        if f.endswith("json"):
            if "dataset" in f:
                datasets.append(path+f)
            else:
                questions_only.append(path+f)

    order_questions_labelled = []
    filter_questions_labelled = []
    aggregate_questions_labelled = []

    for file_path in datasets:
        o, f, a = get_labelled_complex_questions(file_path)
        order_questions_labelled += o
        filter_questions_labelled += f
        aggregate_questions_labelled += a

    save_complex_questions(order_questions_labelled, filter_questions_labelled, aggregate_questions_labelled,
                           labelled=True)

    order_questions_manual = []
    filter_questions_manual = []
    aggregate_questions_manual = []

    for file_path in questions_only:
        o, f, a = get_manually_labelled_complex_questions(file_path)
        order_questions_manual += o
        filter_questions_manual += f
        aggregate_questions_manual += a

    save_complex_questions(order_questions_manual, filter_questions_manual, aggregate_questions_manual, False)


def get_labelled_complex_questions(path):
    filter_questions = []
    order_questions = []
    agg_questions = []

    dbpedia = ["qald_dataset", "lcquad_dataset", "dbnqa_dataset"]
    freebase = True
    for x in dbpedia:
        if x in path:
            freebase = False

    data = load_json(path)
    print path + " " + str(len(data))
    for row in data:
        question = row["question"].lower()
        query = row["query"].lower()

        if "order by" in query:
            order_questions.append({"question": question, "query": query, "dataset": path})

        if freebase:
            if query.count("filter") > 2:
                filter_questions.append({"question": question, "query": query, "dataset": path})
        else:
            cond_1 = "Filter (lang(?string) = 'en')".lower() not in query
            cond_2 = "FILTER regex".lower() not in query
            if "filter" in query and cond_1 and cond_2:

                filter_questions.append({"question": question, "query": query, "dataset": path})

        if "select sum" in query or "select avg" in query or "select max" in query or "select min" in query:
            agg_questions.append({"question": question, "query": query, "dataset": path})

    print "Dataset {} Total No. Questions {} Order Questions {} Filter Questions {} Aggregation Questions {}" \
        .format(path, len(data), len(order_questions), len(filter_questions), len(agg_questions))
    return order_questions, filter_questions, agg_questions


def get_manually_labelled_complex_questions(path):
    filter_questions = []
    order_questions = []
    aggregate_questions = []

    data = load_json(path)
    print path + " " + str(len(data))

    for row in data:
        row = row.lower()

        tmp_order_questions = []

        if "est" in row or "most" in row or "least" in row:
            row = re.sub(r"[a-zA-z]+:[a-zA-z]+", "", row)
            tmp_order_questions.append(row)
            superlatives = load_json("data/ComplexQuestionsOrder/superlatives.json")
            ordinals = load_json("data/ComplexQuestionsOrder/ordinals.json")

            for q in tmp_order_questions:
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
                    order_questions.append(q)

        if "more than" in row or "less than" in row:
            filter_questions.append(row)

        if "how much" in row:
            aggregate_questions.append(row)

    print "Dataset {} Total No. Questions {} Order Questions {} Filter Questions {} Aggregation Questions {}"\
        .format(path, len(data), len(order_questions), len(filter_questions), len(aggregate_questions))

    return order_questions, filter_questions, aggregate_questions


def save_complex_questions(order_q, filter_q, agg_q, labelled=False):
    if labelled:
        path = "_labelled"
    else:
        path = ""
    save_json("./data/clean_datasets/complex_questions/order_questions{}.json".format(path), order_q)
    save_json("./data/clean_datasets/complex_questions/filter_questions{}.json".format(path), filter_q)
    save_json("./data/clean_datasets/complex_questions/aggregate_questions{}.json".format(path), agg_q)


def basic_stats(path="data/clean_datasets/complex_questions/"):
    for f in os.listdir(path):
        data = load_json(path+f)
        print "Dataset: {} Total No. Questions: {}".format(f, len(data))


if __name__ == '__main__':
    print "Here We Go !!!"
    # get_complex_questions()

    # basic_stats()

    # a, b, c = get_labelled_complex_questions("data/clean_datasets/ComplexWeQquestions_dataset.json")
    # save_complex_questions(a, b, c, True)
    # print a

    # get_manually_labelled_complex_questions("data/clean_datasets/QAD_questions.json")









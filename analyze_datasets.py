# -*- coding: utf-8 -*-
import json, os, re, sys
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm
from classification.prepare_datasets import get_questions


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

    # datasets = []
    # questions_only = []
    # for f in os.listdir(path):
    #     if f.endswith("json"):
    #         if "dataset" in f:
    #             datasets.append(path+f)
    #         else:
    #             questions_only.append(path+f)

    datasets = ['data/clean_datasets/qald_dataset.json', 'data/clean_datasets/lcquad_dataset.json',
             'data/clean_datasets/dbnqa_dataset.json']

    order_questions_labelled = []
    filter_questions_labelled = []
    aggregate_questions_labelled = []

    for file_path in datasets:
        o, f, a = get_labelled_complex_questions(file_path)
        order_questions_labelled = o
        filter_questions_labelled = f
        aggregate_questions_labelled = a

        name = re.findall(r"\w*_dataset", file_path)[-1].replace("_dataset", "")
        # name = ""

    # print len(order_questions_labelled), len(filter_questions_labelled), len(aggregate_questions_labelled)
        save_complex_questions(order_questions_labelled, filter_questions_labelled, aggregate_questions_labelled,
                           labelled="", dataset=name)

    # order_questions_manual = []
    # filter_questions_manual = []
    # aggregate_questions_manual = []
    #
    # for file_path in questions_only:
    #     o, f, a = get_manually_labelled_complex_questions(file_path)
    #     order_questions_manual += o
    #     filter_questions_manual += f
    #     aggregate_questions_manual += a
    #
    # save_complex_questions(order_questions_manual, filter_questions_manual, aggregate_questions_manual, False)


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


def save_complex_questions(order_q, filter_q, agg_q, labelled="dbpedia", dataset=""):
    if labelled == "labelled":
        path = "_labelled"
    elif labelled == "dbpedia":
        path = "_dbpedia"
    else:
        path = ""

    if dataset != "":
        dataset = "_{}".format(dataset)

    save_json("./data/clean_datasets/dbpedia/order_questions{}{}.json".format(path, dataset), order_q)
    save_json("./data/clean_datasets/dbpedia/filter_questions{}{}.json".format(path, dataset), filter_q)
    save_json("./data/clean_datasets/dbpedia/aggregate_questions{}{}.json".format(path, dataset), agg_q)


# Prints some basic stats for json files in a given path
def basic_stats(path="data/clean_datasets/combined_datasets/"):
    print "Generating Stats"
    for f in os.listdir(path):
        data = load_json(path+f)
        print "File: {} Total No. Questions: {:,}".format(f, len(data))
        list_, ask, count, order, filter_, agg = get_questions("", data)
        print "-- No. List Questions: {:,}".format(len(list_))
        print "-- No. Ask Questions: {:,}".format(len(ask))
        print "-- No. Count Questions: {:,}".format(len(count))
        print "-- No. Order Questions: {:,}".format(len(order))
        print "-- No. Filter Questions: {:,}".format(len(filter_))
        print "-- No. Agg Questions: {:,}".format(len(agg))


def deep_stat(path="data/clean_datasets/"):
    files = []
    for f in os.listdir(path):
        if ".json" in f:
            files.append(path+f)

    # files = ['data/clean_datasets/qald_dataset.json', 'data/clean_datasets/lcquad_dataset.json',
    #          'data/clean_datasets/dbnqa_dataset.json']

    # files = ['data/clean_datasets/ComplexWeQquestions_dataset.json', 'data/clean_datasets/freebase_dataset.json',
    #          'data/clean_datasets/webqsp_dataset.json', 'data/clean_datasets/graph_dataset.json',
    #          'data/clean_datasets/wiki_data_simple_questions_dataset.json']

    for f in files:
        # get_complexity(f)
        # get_questions_stats(f)
        get_linked_items(f)


def get_complexity(path):
    if "dbpedia" not in path:
        return

    result = {1: 0, 2: 0, 3: 0}
    data = load_json(path)

    for row in data:

        query = re.findall(r"{.*}", row["query"])

        if query:
            query = query[0]
            count = max(query.count("dbo"), query.count("ontology"))

            if count == 0 or count == 1:
                result[1] += 1
            elif count == 2:
                result[2] += 1
            else:
                result[3] += 1

    print "Dataset: {} Complexity {}".format(path, result)


def get_questions_stats(path):
    if "dbpedia" not in path:
        return
    print path
    data = load_json(path)
    no_questions = len(data)
    words = set()
    words_total = 0
    max_question = 0
    words_lemmated = set()

    stopWords = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    for row in data:
        question = word_tokenize(clean_question(row["question"]))
        words_total += len(question)
        max_question = max(max_question, len(question))

        for word in question:
            if word not in stopWords:
                words.add(word)
                if lemmatizer.lemmatize(word) not in words_lemmated:
                    words_lemmated.add(word)

    words_length = len(words)
    words = list(words)
    if no_questions > 0:
        average_question = float(words_total) / float(no_questions)
    else:
        average_question = 0

    print "Dataset: {}, Average #q: {}, Max #q: {}, Vocabulary: {}, lemmatized Vocab: {}".format(path, average_question,
            max_question, words_length, len(list(words_lemmated)))


def get_linked_items(path):
    if "dbpedia" not in path:
        return

    print path

    data = load_json(path)
    result = {}

    for row in data:
        query = re.findall(r"{.*}", row["query"])

        if query:
            query = query[0]
            pattern = re.findall(r"dbpedia.org|\w+:", query)

            count = len(pattern)

            # print pattern

            # if count == 0:
            #     print query
            #     print count

            if count > 4:
                count = 5

            if count in result:
                result[count] += 1
            else:
                result[count] = 1
    print result
    return result


def clean_question(q):
    q = q.lower()
    q = q.replace(" 's", " is")
    q = re.sub(r"\?|'|,|\.|`|\\|\"", "", q)
    q = re.sub(r" {2,}|-", " ", q)
    q = re.sub(r"\t", " ", q)
    q = q.strip()
    return q


# Gets ask,list,count questions from lcquad into separate files
# def get_lcquad_questions():
#     path = "./data/clean_datasets/lcquad_dataset.json"
#     data = load_json(path)
#     print path
#     print len(data)
#
#     list_questions = []
#     ask_questions = []
#     count_questions = []
#
#     for row in tqdm(data):
#         if "ASK WHERE" in row["query"]:
#             ask_questions.append(row)
#         if "SELECT COUNT" in row["query"]:
#             count_questions.append(row)
#         if "SELECT DISTINCT" in row["query"]:
#             list_questions.append(row)
#     print len(ask_questions), len(list_questions), len(count_questions)
#
#     save_json("./data/clean_datasets/dbpedia/list_questions_lcquad.json", list_questions)
#     save_json("./data/clean_datasets/dbpedia/ask_questions_lcquad.json", ask_questions)
#     save_json("./data/clean_datasets/dbpedia/count_questions_lcquad.json", count_questions)


# Gets ask,list,count questions from qald into separate files
# def get_qald_questions():
#     path = "./data/clean_datasets/qald_dataset.json"
#     data = load_json(path)
#     print path
#     print len(data)
#
#     list_questions = []
#     ask_questions = []
#     count_questions = []
#
#     for row in tqdm(data):
#         if "ask where" in row["query"].lower():
#             ask_questions.append(row)
#         if "select count" in row["query"].lower():
#             count_questions.append(row)
#         if "select distinct" in row["query"].lower():
#             list_questions.append(row)
#     print len(ask_questions), len(list_questions), len(count_questions)
#
#     save_json("./data/clean_datasets/dbpedia/list_questions_qald.json", list_questions)
#     save_json("./data/clean_datasets/dbpedia/ask_questions_qald.json", ask_questions)
#     save_json("./data/clean_datasets/dbpedia/count_questions_qald.json", count_questions)


# combines the list,ask, count questions into single file per category


# def combine_basic_questions_types():
#     path = "./data/clean_datasets/dbpedia/"
#     ask_questions = []
#     list_questions = []
#     count_questions = []
#
#     for f in os.listdir(path):
#         if "ask" in f:
#             ask_questions += load_json(path+f)
#         if "list" in f:
#             list_questions += load_json(path+f)
#         if "count" in f:
#             count_questions += load_json(path+f)
#
#     print len(ask_questions)
#     print len(count_questions)
#     print len(list_questions)
#
#     save_json("./data/clean_datasets/combined_datasets/ask_questions_dbpedia.json", ask_questions)
#     save_json("./data/clean_datasets/combined_datasets/count_questions_dbpedia.json", count_questions)
#     save_json("./data/clean_datasets/combined_datasets/list_questions_dbpedia.json", list_questions)




    # data = load_json(path)
    # for row in data


if __name__ == '__main__':
    print "Here We Go !!!"
    # path = "data/clean_datasets/dbpedia/"

    basic_stats()


    # deep_stat("data/clean_datasets/combined_datasets/")



    # a, b, c = get_labelled_complex_questions("data/clean_datasets/ComplexWeQquestions_dataset.json")
    # save_complex_questions(a, b, c, True)
    # print a

    # get_manually_labelled_complex_questions("data/clean_datasets/QAD_questions.json")

    # basic_stats("data/clean_datasets/combined_datasets/")

import json, re, sys, os
from get_kb_properties import *
from tqdm import tqdm
from order_property import get_order_property
from helper import *

from stanfordcorenlp import StanfordCoreNLP



def get_order_properties_count(path="../data/clean_datasets/combined_datasets/order_all.json"):
    data = load_json(path)
    properties = {}
    errors = []

    for c, row in enumerate(data):
        query = row["query"]
        property_ = get_order_property(query)

        if property_:
            if property_ in properties:
                properties[property_] += 1
            else:
                properties[property_] = 1
        else:
            errors.append(row)

    return properties, errors


def get_order_properties_stats():
    props, errors = get_order_properties_count()

    props = sorted(props.items(), key=lambda x: x[1], reverse=True)

    # for row in props:
        # print row[0]
        # print row[1]

    print "No. of Unique Order Properties: %d" % len(props)
    print "No. of incorrect queries: %d" % len(errors)

    save_json(props, "properties.json")
    save_json(errors, "errors.json")





def features_properties_list():
    data = load_json("../data/clean_datasets/combined_datasets/order_all.json")
    superlatives = load_json("../data/ComplexQuestionsOrder/superlatives.json")
    ordinals = load_json("../data/ComplexQuestionsOrder/ordinals.json")

    additions = ["most", "least", "new", "last", "latest", "top"]

    result = {}

    for row in tqdm(data):
        ques = row["question"]
        property_ = get_order_property(row["query"])

        tmp = {"property": [property_], "type": ""}

        ques = row["question"].split(" ")

        for s in superlatives:
            if s in ques:
                tmp["type"] = 1
                if s not in result:
                    result[s] = tmp
                else:
                    if property_ not in result[s]["property"]:
                        result[s]["property"].append(property_)

        for o in ordinals:
            if o in ques:
                tmp["type"] = 2
                if o not in result:
                    result[o] = tmp
                else:
                    if property_ not in result[o]["property"]:
                        result[o]["property"].append(property_)

        for a in additions:
            if a in ques:
                tmp["type"] = 3
                if a not in result:
                    result[a] = tmp
                else:
                    if property_ not in result[a]["property"]:
                        result[a]["property"].append(property_)

        # result.append(tmp)

    save_json(result, "features_properties.json")


def get_ontologies_types():
    ontologies = load_txt("../data/properties.txt")

    result = []
    for o in tqdm(ontologies):
        sparql = """SELECT ?a WHERE {{ <{}> rdfs:range ?a }}""".format(o)
        type_ = get_query_answers(sparql)
        if type_:
            type_ = type_[0].replace("http://www.w3.org/2001/XMLSchema#", "")
            result.append([o, type_])
        else:
            continue

    save_json(result, "ontologies_types.json")


def clean_ontologies():
    ontos_types = load_json("ontologies_types.json")
    ontos = load_txt("../data/properties.txt")

    literal_types = ["double", "float", "gYearMonth", "positiveInteger", "nonNegativeInteger", "gYear",
                     "date", "integer"]
    clean_ontos = []

    for row in ontos_types:
        if row[1] in literal_types and row[0] in ontos:
            clean_ontos.append(row[0])

    save_json(clean_ontos, "clean_ontologies.json")


def main():
    print "MAIN"
    # get_order_properties_count()
    # get_order_properties_stats()
    # prep_multi_class_train_test()
    # features_properties_list()

    # get_ontologies_types()
    # clean_ontologies()

    # svm = SVM()
    # svm.load("svm")

    # maxe = MAXE()
    # maxe.load("maxe")

    # s = ["what is the shortest mountain in europe", "who is the shortest player in the nba",
    #      "who is the second president of the usa"]

    # print svm.predict(s)
    # print maxe.predict(s)

    # nlp = StanfordCoreNLP(r'/Users/just3obad/Desktop/Thesis/Libraries/stanford-corenlp-full-2018-10-05')

    # sentence = 'Guangdong University of Foreign Studies is located in Guangzhou.'
    # print 'Tokenize:', nlp.word_tokenize(sentence)
    # print 'Dependency Parsing:', nlp.dependency_parse(sentence)

    # nlp.close()


if __name__ == '__main__':
    print "Here We Go !!!"
    main()

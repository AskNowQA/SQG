from helper import *
from resource_tree import parse
from nltk.tokenize import word_tokenize


def detect_offset(question, sparql):
    parsed_question = parse(question, sparql)
    parsed_question = word_tokenize(parsed_question)
    ordinals = load_json("../data/ComplexQuestionsOrder/ordinals.json")

    for word in parsed_question:
        if word in ordinals:
            print question
            print word


def detect_direction(question):
    pass


def prepare_direction_list():
    pass


def offsets_experiments():
    data = load_json("data/one_hop_ontologies_clean.json")

    for row in data:
        # print row["question"]
        # print row["earl_query"]
        # print row["query"]
        detect_offset(row["question"], row["earl_query"])
        # break


def main():
    print "MAIN"
    offsets_experiments()
    # detect_offset("lalal", "{}")


if __name__ == '__main__':
    main()
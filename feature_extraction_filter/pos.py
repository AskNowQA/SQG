#-*- coding: utf-8 -*-
# POS Tagger
from helper import *
from filter_helper import *
from tqdm import tqdm
from resource_tree import parse
from prepare_train_test_classifier import filter_query_type
from word2number import w2n
from filter_property import *

__QUESTIONS_POS_TAGS = load_json("data/questions_pos_tags.json")


# Should return a list of questions and their corresponding feature
def get_questions_features():
    pass


def get_feature_precompiled(question):
    pass


# Get filter features from the question
def get_features_nlp(question, sparql):
    type_ = filter_query_type(sparql)
    question_clean = parse(question, sparql)

    # print "CLEAN QUESTION", question_clean

    result = []
    if type_ == 0:
        # return get_type_0_features(question_clean)
        result.append(question_clean)

    if type_ == 1 or type_ == 2:
        feature, question_clean = get_question_features(question_clean)
        result.append(question_clean)
        result.append(feature)
        if type_ == 1:
            numeric_value = get_question_numeric_features(question_clean)
            result.append(numeric_value)

    return result


# def get_type_0_features(question):
    # We need to test performance of single keyword vs multiple keywords
    # In case of single keywords, we use.
        #[1]
        #Verb, adv, adj,noun = verb
        #adj,adv = adj
    # return question


def get_question_features(question):
    # print "Clean Question:", question
    doc = nlp(unicode(question))
    for i, token in enumerate(doc):
        if token.tag_ in compare_tags or token.text in additions:
            if doc[i-1].pos_ == "VERB":
                tmp_doc = doc[i-1:]
                tmp_doc = [tk.text for tk in tmp_doc]
                return doc[i-1].text, " ".join(tmp_doc)
            else:
                tmp_doc = doc[i:]
                tmp_doc = [tk.text for tk in tmp_doc]
                return doc[-1].text, " ".join(tmp_doc)
    return question, question


def get_question_numeric_features(question):
    if " and " in question and "between" in question:
        tokens_list = question.split(" and ")
        tokens_list = [word_tokenize(token) for token in tokens_list]
    else:
        tokens_list = [word_tokenize(question)]

    result = []
    for tokens in tokens_list:
        nums = []
        for token in tokens:
            try:
                w2n.word_to_num(str(token))
                nums.append(str(token))
            except:
                continue
        if nums:
            nums = " ".join(nums)
            result.append(nums)

    if result:
        return [w2n.word_to_num(num) for num in result]
    else:
        return None


def prepare_comparator_hash():
    data = load_json(filter_path)
    result = {}
    for row in tqdm(data):
        question = row["question"]
        sparql = row["query"]

        # print question
        # print sparql

        doc = nlp(unicode(question))
        for i, token in enumerate(doc):
            if token.tag_ in compare_tags or token.text in additions:
                question_comparator = token.text

        sparql_comparator = get_filter_properties(sparql)

        if sparql_comparator and sparql_comparator["comparator"] != "bound":
                sparql_comparator = sparql_comparator["comparator"][0]
                if question_comparator in result:
                    if sparql_comparator not in result[question_comparator]:
                        result[question_comparator].append(sparql_comparator)
                else:
                    result[question_comparator] = [sparql_comparator]

        # break

    save_json(result, "data/comparators_hash.json")


# Prepares a Dictionary of questions and their pos
def prepare_pos_tagger_hash():
    data = load_json("../data/clean_datasets/combined_datasets/filter_all.json")
    result = {}

    for row in tqdm(data):
        question = row["question"]
        question_clean = ascii_only_tokens(question)

        doc = nlp(question_clean)

        result[question] = {token.text: token.tag_ for token in doc}

    save_json(result, "data/questions_pos_tags.json")


def main():
    print "MAIN"
    # sentence = u'was the siege of lille more than the one thousand nine hundred and five russian revolution'
    sentence = u"for which label did anthony callea record his second singles"
    # prepare_pos_tagger_hash()
    doc = nlp(sentence)
    for token in doc:
        # print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
        #       token.shape_, token.is_alpha, token.is_stop)
        print token.text, token.tag_
    #
    # data = load_json(filter_qald_path)
    # # data = load_json(filter_path)
    # for row in data:
    #     question = row["question"]
    #     sparql = row["query"]
    #     print question
    #     print sparql
    #     print get_features_nlp(question, sparql)
    #     print "\n ## \n"

    # prepare_comparator_hash()

        # break

    # print w2n.word_to_num("thousand")


if __name__ == '__main__':
    main()

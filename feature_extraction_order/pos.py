# POS Tagger
from tqdm import tqdm
import json
import nltk
from stanfordcorenlp import StanfordCoreNLP
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from resource_tree import parse
nltk.data.path.append("/Users/just3obad/Desktop/Thesis/Libraries/nltk_data")
# nlp = StanfordCoreNLP(r'/Users/just3obad/Desktop/Thesis/Libraries/stanford-corenlp-full-2018-10-05')
stop_words = set(stopwords.words('english'))


def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


def save_json(data, name):
    with open(name, "w") as data_file:
        json.dump(data, data_file, sort_keys=True, indent=4, separators=(',', ': '))


def pos_text(text):
    tokens = nltk.word_tokenize(text)
    print "Tokens ", tokens
    print "Parts of Speech Tags: ", nltk.pos_tag(tokens)


# Takes a question and returns a clean one without stopwords/
def clean_question(question):
    tokens = word_tokenize(question)

    new_tokens = []
    for t in tokens:
        try:
            t.encode("ascii")
            new_tokens.append(t)
        except:
            continue

    additions = ["most", "least", "new", "last", "latest", "top", "t"]
    question = " ".join([t for t in new_tokens if t in additions or t not in stop_words])
    return question


# Using Precompiled Lists
def get_questions_features():
    data = load_json("../data/clean_datasets/combined_datasets/order_all.json")

    result = []

    for row in tqdm(data):
        ques = row["question"]
        tmp = get_feature_precompiled(ques)
        result.append(tmp)

    save_json(result, "data/questions_features_list.json")


def get_feature_precompiled(question):
    superlatives = load_json("../data/ComplexQuestionsOrder/superlatives.json")
    ordinals = load_json("../data/ComplexQuestionsOrder/ordinals.json")
    additions = ["most", "least", "new", "last", "latest", "top"]

    tmp = {"question": question, "features": [], "keywords": [], "match": ""}
    ques = question.split(" ")
    superlative_flag = False
    superlative_feature = ""
    ordinal_flag = False
    addition_flag = False

    for s in superlatives:
        if s in ques:
            tmp["features"].append(s)
            i = ques.index(s)
            if i + 1 < len(ques):
                tmp["keywords"].append(s + " " + ques[i + 1])
                superlative_flag = True
                superlative_feature = s
            else:
                tmp["keywords"].append(s)

    for o in ordinals:
        if o in ques:
            tmp["features"].append(o)
            # tmp["features"].append("first")
            i = ques.index(o)
            if i + 1 < len(ques):
                tmp["keywords"].append(o + " " + ques[i + 1])
                # tmp["keywords"].append("first" + " " + ques[i + 1])
                ordinal_flag = True
            else:
                tmp["keywords"].append(o)
                # tmp["keywords"].append("first")

    for a in additions:
        if a in ques:
            tmp["features"].append(a)
            i = ques.index(a)
            if i + 1 < len(ques):
                tmp["keywords"].append(a + " " + ques[i + 1])
                addition_flag = True
            else:
                tmp["keywords"].append(a)

    if superlative_flag:
        tmp["match"] = [superlative_feature]

    if ordinal_flag or addition_flag:
        tmp["match"] = tmp["keywords"][0].split(" ")

    tmp["keywords"] = tmp["keywords"][0].split(" ")

    return tmp


# Prepares a Dictionary of questions and their pos
def prepare_pos_tagger_hash():
    data = load_json("../data/clean_datasets/combined_datasets/order_all.json")
    result = {}

    for row in tqdm(data):
        question = clean_question(row["question"])
        tags = nlp.pos_tag(question)
        result[question] = tags

    save_json(result, "data/questions_pos_tags.json")


def get_features_nlp(question, sparql):
    clean_features = word_tokenize(parse(question, sparql))
    feature = clean_features[0]
    # if feature == "new":
    #     return [["new"]]
    clean_features = clean_features[1:]
    result = []
    for word in clean_features:
        result.append([feature, word])
    return result


def main():
    # pos_text("Who is the shortest nba player")
    # sentence = 'who is the tallest nba player'
    # print 'Tokenize:', nlp.word_tokenize(sentence)
    # print 'Part of Speech:', nlp.pos_tag(sentence)
    # get_questions_features()

    for i, row in enumerate(load_json("data/one_hop_ontologies_clean.json")):
        get_features_nlp(row["question"], row["earl_query"])
        # if i == 30:
        #     break


if __name__ == '__main__':
    print "MAIN"
    main()

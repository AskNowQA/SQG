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
# from prepare_train_test import clean_filter_questions
import spacy

nlp = spacy.load("en")


def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


def save_json(data, name):
    with open(name, "w") as data_file:
        json.dump(data, data_file, sort_keys=True, indent=4, separators=(',', ': '))


# Should return a list of questions and their corresponding feature
def get_questions_features():
    pass


def get_feature_precompiled(question):
    pass


def get_features_nlp(question, sparql):
    pass


# Prepares a Dictionary of questions and their pos
def prepare_pos_tagger_hash():
    data = load_json("../data/clean_datasets/combined_datasets/filter_all.json")
    result = {}

    for row in tqdm(data):
        tokens = word_tokenize(row["question"])
        question = ascii_only(tokens)

        tags = nlp.pos_tag(question)
        result[question] = tags

    save_json(result, "data/questions_pos_tags.json")


# Takes a list of strings, returns a string with ascii words only.
def ascii_only(tokens):
    res = []
    for t in tokens:
        try:
            t.encode("ascii")
            res.append(t)
        except:
            res.append("#")
            continue
    return " ".join(res)


def main():
    print "MAIN"
    # pos_text("Who is the shortest nba player")
    sentence = u'was the siege of lille more than the one thousand nine hundred and five russian revolution'
    # print 'Tokenize:', nlp.word_tokenize(sentence)
    # print 'Part of Speech:', nlp.pos_tag(sentence)
    # get_questions_features()
    # print stop_words
    # prepare_pos_tagger_hash()

    doc = nlp(sentence)

    for token in doc:
        print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
              token.shape_, token.is_alpha, token.is_stop)


if __name__ == '__main__':
    main()

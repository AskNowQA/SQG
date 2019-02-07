import re
import spacy
import inflect
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer


# NLTK SETTINGS
nltk.data.path.append("/Users/just3obad/Desktop/Thesis/Libraries/nltk_data")
stop_words = set(stopwords.words('english'))

# PATHS DEFINITION
filter_path = "../data/clean_datasets/combined_datasets/filter_all.json"
filter_classifier_train_test_path = "data/filter_questions_clean.json"
filter_qald_path = "../data/clean_datasets/dbpedia/filter_qald.json"

# SPACEY
nlp = spacy.load("en")

# Filter keywords
additions = ["more", "before", "same", "since", "after", "as", "between", "also", "already", "present", "still"]
black_list_keywords = ["give", "show", ]
compare_tags = ["JJR", "RBR"]


# Clean Filter Questions

def clean_filter_questions(sparql):
    return False if "regex" in sparql.lower() else True


def clean_question(question):
    # print "AA", question
    tokens = word_tokenize(question)
    new_tokens = []
    for t in tokens:
        try:
            t.encode("ascii")
            new_tokens.append(t)
        except:
            continue

    if "between" in question:
        additions.append("and")

    # Need to check filter addition keywords
    question = " ".join([t for t in new_tokens if t in additions or (t not in stop_words and t not in black_list_keywords)])
    # question = " ".join(new_tokens)
    print "AA", question
    return question


"""
    Takes a list of tokens and returns tokens with numbers tokens transformed to text
"""


def tokens_to_digit(tokens):
    tokenizer = RegexpTokenizer(r'\w+')
    tmp = []
    for token in tokens:
        if token.isdigit():
            p = inflect.engine()
            num = ' '.join(tokenizer.tokenize(p.number_to_words(int(token))))
            tmp.append(num)
            continue
        tmp.append(token)
    return tmp


""" 
    Non ascii characters handling
"""


def ascii_only(text):
    return " ".join(re.findall(r"[a-zA-Z0-9]+", text)).lower()


def ascii_only_hash(text):
    return re.sub(r"[^a-zA-Z0-9 ]+", "#", text)


def ascii_only_tokens(text):
    tokens = word_tokenize(text)
    res = []
    for t in tokens:
        try:
            t.encode("ascii")
            res.append(t)
        except:
            # res.append("#")
            continue
    return " ".join(res)


def is_ascii(string):
    try:
        string.encode("ascii")
        return True
    except:
        return False
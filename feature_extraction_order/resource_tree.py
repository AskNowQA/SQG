from helper import *
from prepare_train_test import clean_question
import re
import inflect
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize


__QUESTIONS_POS_TAGS = load_json("data/questions_pos_tags.json")


# Takes a question. Removes resources mentions in the question
def parse(question, sparql):
    question_clean = clean_question(question)
    pos_tags = {tag[0]: tag[1] for tag in __QUESTIONS_POS_TAGS[question_clean]}
    dbr_list = parse_sparql(sparql)

    question_clean_parsed = question_clean
    for dbr in dbr_list:
        dbr = clean_question(dbr)
        question_clean_parsed = question_clean_parsed.replace(dbr, "")
        question_clean_parsed = " ".join(re.findall(r"\S+", question_clean_parsed))

    super_tags = ["JJS", "RBS"]
    additions = ["most", "least", "new", "last", "latest", "top"]
    ordinals = load_json("../data/ComplexQuestionsOrder/ordinals.json")

    question_clean_parsed = word_tokenize(question_clean_parsed)

    for i, word in enumerate(question_clean_parsed):
        if pos_tags[word] in super_tags or word in additions or word in ordinals:
            question_clean_parsed = question_clean_parsed[i:]

    question_clean_parsed = " ".join(question_clean_parsed)

    return question_clean_parsed


# Takes a SPARQL and returns a list of the resources (dbr) in that sparql
def parse_sparql(sparql):
    triples = re.findall(r"{.*}", sparql)[0].replace("{", "").replace("}", "")
    triples = re.findall(r"\S+", triples)
    resources = [triple.replace("dbr:", "") for triple in triples if "dbr:" in triple]
    resources = [r.lower().replace("-", "_").replace("_", " ") for r in resources]
    tokenizer = RegexpTokenizer(r'\w+')

    result = []
    for r in resources:
        tokens = r.split(" ")
        tmp = []
        for t in tokens:
            try:
                t.encode("ascii")
                if t.isdigit():
                    p = inflect.engine()
                    num = ' '.join(tokenizer.tokenize(p.number_to_words(int(t))))
                    tmp.append(num)
                    continue
                tmp.append(t)
            except:
                continue
        if tmp:
            result.append(tmp)
    result = [" ".join(r) for r in result if r]
    return result


def main():
    data = load_json("data/one_hop_ontologies_clean.json")
    for i, r in enumerate(data):
        print parse(r["question"], r["earl_query"])


if __name__ == '__main__':
    main()

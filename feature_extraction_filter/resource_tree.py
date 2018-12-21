from helper import *
from prepare_train_test import clean_question
import re
import inflect
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize
from prepare_train_test import filter_clean_path, filter_path
from parser.generator_utils import *


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

    super_tags = ["JJR", "RBR"]
    additions = ["more", "than"]

    question_clean_parsed = word_tokenize(question_clean_parsed)

    for i, word in enumerate(question_clean_parsed):
        if pos_tags[word] in super_tags or word in additions:
            question_clean_parsed = question_clean_parsed[i:]

    question_clean_parsed = " ".join(question_clean_parsed)

    return question_clean_parsed


# Takes a SPARQL and returns a list of the resources (dbr) in that sparql
def parse_sparql(sparql):
    triples = re.findall(r"{.*}", sparql)[0].replace("{", "").replace("}", "")
    triples = re.findall(r"\S+", triples)

    resources = [triple.replace("dbr:", "") for triple in triples if "dbr:" in triple]
    resources = ["".join(re.findall(r"\w+", r)) for r in resources]
    resources = [r.lower().replace("-", "_").replace("_", " ") for r in resources]
    # resources = [r.lower().replace("(", "").replace(")", "").replace(".", "") for r in resources]
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



def token_permutations(tokens):
    result = []
    for i in range(len(tokens)-1):
        for j in range(i+1, len(tokens)):
            # print i, j
            print tokens[i:j]
            result.append(tokens[i:j])
    print len(result)
    return result


def main():
    data = load_json(filter_path)
    for row in data:

        # question = row
        print row
        # print extract_entities(row["query"])
        # print extract_predicates(row["query"])
        print extractTriples(row["query"])
        # print ex
        # print p(question)
        print "##\n"

        # tokens = word_tokenize(question)
         # print question

        # q = row["query"]
        # print q

        # token_permutations(tokens)

        # break
    # for i, r in enumerate(data):
    #     print parse(r["question"], r["earl_query"])


if __name__ == '__main__':
    main()







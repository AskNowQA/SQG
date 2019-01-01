#-*- coding: utf-8 -*-
from helper import *
from filter_helper import *


__QUESTIONS_POS_TAGS = load_json("data/questions_pos_tags.json")


# Takes a question. Removes resources mentions in the question
def parse(question, sparql):
    uris = parse_sparql(sparql)
    question = " ".join(tokens_to_digit(word_tokenize(ascii_only(question))))
    uris_list = [token_permutations(uri) for uri in uris]
    question_clean = clean_question(remove_uris_question(question, uris_list))
    return question_clean


# Takes a SPARQL and returns a list of the resources (dbr, /resource) in that sparql
def parse_sparql(sparql):
    resources = re.findall(r"<\S+xmlns\S+name>\s*'.*'", sparql, flags=re.IGNORECASE)
    if len(resources) != 0:
        resources = re.findall(r"'.*'", resources[0], flags=re.IGNORECASE)[0]
        resources = [resources.replace("'", "")]
    else:
        resources = re.findall(r"<\S+resource\S+>", sparql)
        resources = [re.sub(r"http\S+\/|<|>", "", uri) for uri in resources]
        resources = [" ".join(re.findall(r"[a-zA-Z0-9]+", res)).lower() for res in resources]

    result = []
    for r in resources:
        tokens = word_tokenize(r)
        result.append(tokens_to_digit(tokens))
    result = [" ".join(r) for r in result if r]
    return result


# Returns a list of possible substrings from the end of the string till the beginning
def token_permutations(tokens):
    tokens = word_tokenize(tokens)
    results = []
    counter = len(tokens)
    while counter != 0:
        results.append(" ".join(tokens[:counter]))
        counter -= 1
    return results


def remove_uris_question(question, uris_list):
    for uris in uris_list:
        for uri in uris:
            if uri.lower() in question.lower():
                # question = question.replace(uri, "")
                question = re.sub(r"\b%s\b" % uri, "", question, flags=re.IGNORECASE)
                break
    return question


def main():
    # data = load_json(filter_path)
    data = load_json(filter_qald_path)
    print len(data)
    for row in data:

        question = row["question"]
        sparql_query = row["query"]
        print question
        print sparql_query
        print parse(question, sparql_query)
        print "##\n"
        # break


if __name__ == '__main__':
    main()







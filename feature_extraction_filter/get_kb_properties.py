from helper import *
from filter_helper import *
from joblib import Parallel, delayed
from helper import *
from filter_property import *
import sys
from feature_extraction_order.get_kb_properties import prepare_sparql_query as prep_order_query

from prepare_train_test_classifier import filter_query_type


# Takes order query and transforms it to a query similar to ones we get from earl
def prepare_sparql_query(sparql):
    # sparql = sparql.encode("utf-8")

    type_ = filter_query_type(sparql)

    if type_ == 0 or type_ == 2:
        resources = prepare_sparql_query_helper(sparql)

        if not resources:
            if "order by" in sparql.lower():
                sparql = re.sub(r"order by.*", "", sparql, flags=re.IGNORECASE)

            filter_condition = re.findall(r"filter.*\(.*\)", sparql, flags=re.IGNORECASE)

            if not filter_condition:
                return sparql

            earl_query = sparql.replace(filter_condition[0], "")

            if ";" in sparql:
                earl_query = re.sub(r"<\S+>\s*\?\S+", "", earl_query)
                earl_query = re.sub(r";\s+;", "", earl_query)
                return earl_query
            else:
                filter_condition = re.findall(r"filter.*\(.*\)", sparql, flags=re.IGNORECASE)
                earl_query = sparql.replace(filter_condition[0], "")
                return earl_query
        else:
            triples = []
            for i, res in enumerate(resources):
                triple = """ %s ?o ?uri_%d """ % (res, i)
                triples.append(triple)

            line = " . ".join(triples)
            earl_query = """SELECT DISTINCT(?o) WHERE {{ {} FILTER ( regex(?o, "ontology")) }}""".format(line)

            return earl_query

    elif type_ == 1:
        if "order by" in sparql.lower():
            sparql = re.sub(r"order by.*", "", sparql, flags=re.IGNORECASE)

        filter_condition = re.findall(r"filter.*\(.*\)", sparql, flags=re.IGNORECASE)
        if not filter_condition:
            return sparql

        earl_query = sparql.replace(filter_condition[0], "")

        head = """SELECT * WHERE"""

        earl_query = re.sub(r"^^.*where", head, earl_query, flags=re.IGNORECASE)

        earl_query = re.sub(r"\.\s+\.", " . ", earl_query, flags=re.IGNORECASE)

        return earl_query

    else:
        return None


def prepare_sparql_query_helper(sparql):
    sparql = sparql.encode("utf-8")

    resources = re.findall(r"<\S+xmlns\S+name>\s*'.*'", sparql, flags=re.IGNORECASE)
    if len(resources) == 0:
        resources = re.findall(r"<\S+resource\S+>", sparql)
    return resources


# Gets all the possible answer for a given query. Assuming this query is formed by resources
# returned by earl
def get_query_answers(q, limit=False, bonn=False):
    a, b = query(q, bonn)
    if a == 400 or not b:
        return "Error in the SPARQL query"

    results = b["results"]
    if results:
        results = results["bindings"]

    values = []

    for i in results:
        values += i.values()

    values = [v["value"] for v in values]
    values = list(set(values))

    if limit:
        return values[:50]
    return values


def get_one_hop_ontologies(resources):
    results = []
    for o in resources:
        # sparql = """SELECT ?o WHERE {{ <{}> ?o ?e FILTER ( regex(?o, "ontology") || regex(?o, "property") ) }}"""\
        #     .format(o.encode("utf-8"))
        sparql = """SELECT DISTINCT (?o) WHERE {{ <{}> ?o ?e FILTER ( regex(?o, "ontology")) }}""".format(o.encode("utf-8"))
        results += get_query_answers(sparql)

    results = list(set(results))

    return results


def get_query_answers_parallel(row):
    q = row["earl_query"]
    answers = get_query_answers(q, limit=True)
    row["answers"] = answers
    return row


def get_one_hop_ontologies_parallel(row):
    ontologies = row["answers"]
    row["one_hop_ontologies"] = get_one_hop_ontologies(ontologies)
    return row


def cache_one_hope_ontologies():
    dbpedia = []
    data = load_json(filter_path)

    for row in data:
        tmp = {"question": "", "earl_query": "", "query": "", "answers": [], "one_hop_ontologies": []}
        query_ = row["query"]
        tmp["query"] = query_
        tmp["earl_query"] = prepare_sparql_query(query_)
        tmp["question"] = row["question"]
        tmp["dataset"] = row["dataset"]

        dbpedia.append(tmp)

    save_json(dbpedia, "data/one_hop_ontologies.json")

    # sys.exit()

    print "Cashing Answers"

    dbpedia = Parallel(n_jobs=4, verbose=1, backend="threading")(map(delayed(get_query_answers_parallel), dbpedia))

    save_json(dbpedia, "data/one_hop_ontologies.json")

    counter = 0
    for row in dbpedia:
        counter += len(row["answers"])

    print "Total no. of answers:", counter

    print "Cashing One Hop Ontologies"

    dbpedia = Parallel(n_jobs=4, verbose=1, backend="threading")(map(delayed(get_one_hop_ontologies_parallel), dbpedia))

    save_json(dbpedia, "data/one_hop_ontologies.json")

    for i, row in enumerate(dbpedia):
        if isinstance(row["answers"], list) and not row["one_hop_ontologies"]:
            row["one_hop_ontologies"] = row["answers"]

        if "xmlns.com" in row["query"]:
            del dbpedia[i]

    save_json(dbpedia, "data/one_hop_ontologies.json")


def clean_cached_ontologies():
    data = load_json("data/one_hop_ontologies.json")
    properties = load_json("data/clean_ontologies.json")
    for row in data:
        ontos = row["one_hop_ontologies"]
        ontos_new = []
        for onto in ontos:
            if onto in properties:
                ontos_new.append(onto)
        row["one_hop_ontologies"] = ontos_new

    data = [row for row in data if row["one_hop_ontologies"]]

    clean_data = []

    for row in data:
        query_ = row["query"]
        filter_properties = get_filter_properties(query_)["properties"]

        if filter_properties:
            filter_properties = [prop.values()[0].replace("<http://dbpedia.org/ontology/", "").replace(">", "").replace("<http://dbpedia.org/property/", "") for prop in filter_properties]
            filter_properties = list(set(filter_properties))

        one_hop_ = [hop.replace("http://dbpedia.org/ontology/", "") for hop in row["one_hop_ontologies"]]

        del row["answers"]

        flag = True

        for prop in filter_properties:
            if prop not in one_hop_:
                print row
                print "\n ## \n"
                flag = False

        if not flag:
            continue

        clean_data.append(row)

    print "No. of clean questions:", len(clean_data)

    save_json(clean_data, "data/one_hop_ontologies_clean.json")


def question_one_hop_hash():
    one_hop_hash = load_json("data/one_hop_ontologies_clean.json")
    result = {}
    for row in one_hop_hash:
        one_hope_list = [o.replace("http://dbpedia.org/ontology/", "") for o in row["one_hop_ontologies"]]
        result[row["question"]] = one_hope_list
    save_json(result, "data/question_one_hop.json")


def one_hop(question):
    data = load_json("data/question_one_hop.json")
    return data[question]


def main():
    print "MAIN"
    # data = load_json(filter_qald_path)
    # data = load_json(filter_path)
    # for row in data:
    #     question = row["question"]
    #     sparql = row["query"]
    #
    #     type_ = filter_query_type(sparql)
    #
    #     if type_ == 2:
    #     print question
    #     print sparql
    #     earl_query = prepare_sparql_query(sparql)
    #     print earl_query
    #     prepare_sparql_query_helper(sparql)
    #     print get_query_answers(earl_query, limit=True)
    #
    #     break
    #
    #     print "\n  ##  \n"
    #
    # cache_one_hope_ontologies()

    clean_cached_ontologies()

    # question_one_hop_hash()




if __name__ == '__main__':
    main()
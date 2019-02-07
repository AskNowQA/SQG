from tqdm import tqdm
from analyze_features import *
from joblib import Parallel, delayed
from helper import *
# from filter_helper import *
from order_property import get_order_property


# Takes order query and transforms it to a query similar to ones we get from earl
def prepare_sparql_query(query_):

    query_ = query_.encode("utf-8")

    order_property = get_order_property(query_)
    query_ = re.findall(r".*}", query_)[0]
    # head = re.findall(r".*{", query_)[0].replace("{", "")
    head = """select * where"""

    triples_ = re.findall(r"{.*}", query_)[0].replace("{", "").replace("}", "")
    triples_ = triples_.split(".")

    try:
        for triple in triples_:
            if order_property in triple:
                triples_.remove(triple)
    except:
        return None

    tail = " . ".join(triples_)

    query_ = "{} {{ {} }}".format(head, tail)

    return query_


# Gets all the possible answer for a given query. Assuming this query is formed by resources
# returned by earl
def get_query_answers(q, limit=False, bonn=False):
    a, b = query(q, bonn)
    if a == 400:
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
        # sparql = """SELECT ?o WHERE {{ <{}> ?o ?e FILTER ( regex(?o, "ontology") || regex(?o, "property") ) }}""".format(o)
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
    data = load_json("../data/clean_datasets/combined_datasets/order_all.json")

    for row in data:
        tmp = {"question": "", "earl_query": "", "query": "", "answers": [], "one_hop_ontologies": []}
        query_ = row["query"]
        tmp["query"] = query_
        tmp["earl_query"] = prepare_sparql_query(query_)
        tmp["question"] = row["question"]

        dbpedia.append(tmp)

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


# Cleans one hop cached data.
# Removes not literal ontologies/properties
# Removes empty one hops
# Removes rows where one hops does not have the required property
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
        order_property = get_order_property(query_)

        one_hop_ = [hop.replace("http://dbpedia.org/ontology/", "") for hop in row["one_hop_ontologies"]]

        if order_property not in one_hop_:
            continue

        del row["answers"]

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


if __name__ == '__main__':
    main()
    # data = load_file("../data/clean_datasets/combined_datasets/order_all.json")
    #
    # for row in tqdm(data):
    # row = data[3]
    # q = prepare_sparql_query(row["query"])
    # resources = get_query_answers("""select * where { ?uri rdf:type dbo:ArchitecturalStructure .  ?uri dbo:location dbr:Brisbane  .   }""")
    # print resources
    # resources = ["http://dbpedia.org/resource/Anne_Graham_Lotz", "http://dbpedia.org/resource/Franklin_Graham"]
    # r = get_one_hop_ontologies(resources)
    #
    # for i in r:
    #     print i

    # cache_one_hope_ontologies()

    # clean_cached_ontologies()

    # question_one_hop_hash()







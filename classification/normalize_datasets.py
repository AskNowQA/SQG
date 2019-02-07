from helper import *
import re
from tqdm import tqdm

REPLACE = {
    "dbr:": "<http://dbpedia.org/resource/",
    "dbo:": "<http://dbpedia.org/ontology/",
    "dbp:": "<http://dbpedia.org/property/"
}


def normalize_uri(uri):
    head = re.findall(r"\w+:", uri)[0]
    return uri.replace(head, REPLACE[head]) + ">"


# Change dbo: --> www.ontology...
def normalize_sparql(sparql):
    patterns = [i for i in re.findall(r"db\w:[^<>{} ?]+", sparql) if re.findall(r"db\w:", i)[0] in REPLACE]
    # patterns = [i for i in re.findall(r"db\w:\S+", sparql) if re.findall(r"db\w:", i)[0] in REPLACE]
    # print patterns
    patterns_hash = {key_: normalize_uri(key_) for key_ in patterns}
    for key, value in patterns_hash.iteritems():
        sparql = sparql.replace(key, value)
    return sparql


def normalize_dataset(data):
    for row in data:
        # print row["query"]
        row["query"] = normalize_sparql(row["query"])
        # print "#####"
    return data


def normalize_datasets():
    datasets = ['../data/clean_datasets/raw/qald_dataset.json', '../data/clean_datasets/raw/lcquad_dataset.json',
                '../data/clean_datasets/raw/dbnqa_dataset.json']
    # datasets = ['../data/clean_datasets/raw/dbnqa_dataset.json', '../data/clean_datasets/raw/qald_dataset.json']
    for dataset in tqdm(datasets):
        print "Normalizing Datasets: %s" % dataset
        data = load_json(dataset)
        result = normalize_dataset(data)
        name = re.findall(r"\w+.json", dataset)[0]
        save_json(result, "../data/clean_datasets/raw_normalized/%s" % name)


def main():
    # input = """ask where{dbr:List_of_Power_Rangers_Turbo_episodes dbo:numberOfEpisodes ?a . dbr:Absolutely_Fabulous dbo:numberOfEpisodes ?b . filter (?a > ?b)  dbc:www }"""
    #     input = "s"
    #     print normalize_sparql(input)
    normalize_datasets()


if __name__ == '__main__':
    main()

from helper import *
from tqdm import tqdm
from joblib import Parallel, delayed
import re


def validate_sparql_func(row):
    sparql = row["query"]
    a, b = query(sparql)
    print a, b
    if a == 400 or b is None:
        row["valid"] = False
    else:
        row["valid"] = True

    return row


def validate_dataset_parallel(data):
    pass
    # results = Parallel(n_jobs=1, verbose=1, backend="threading")(map(delayed(validate_sparql_func), data))
    # valid = [row for row in results if row["valid"]]
    # not_valid = [row for row in results if not row["valid"]]
    # return valid, not_valid


def clean_datasets():
    # datasets = ['../data/clean_datasets/raw_normalized/qald_dataset.json', '../data/clean_datasets/raw_normalized/lcquad_dataset.json',
    #             '../data/clean_datasets/raw_normalized/dbnqa_dataset.json']
    datasets = ['../data/clean_datasets/raw_normalized/qald_clean_dataset.json']
    for dataset in tqdm(datasets):
        print "Cleaning Datasets: %s" % dataset
        data = load_json(dataset)
        valid, not_valid = validate_dataset_parallel(data)
        print "Valid ", len(valid)
        print "Invalid ", len(not_valid)
        name = re.findall(r"\w+.json", dataset)[0]
        save_path = "../data/clean_datasets/raw_cleaned/%s" % name
        save_json(valid, save_path)
        save_path = "../data/clean_datasets/raw_cleaned/not_valid_%s" % name
        save_json(not_valid, save_path)


def remove_duplicates(path):
    pass
    # data = load_json(path)
    # results = {row["question"]: row for row in data}.values()
    # save_json(data.values(), "../data/clean_datasets/raw_cleaned/qald_dataset.json")


def main():
    print "MAIN"
    # clean_datasets()
    # remove_duplicates("../data/clean_datasets/raw_cleaned/qald_dataset.json")
    # path = "../data/clean_datasets/raw_normalized/qald_dataset.json"
    # data = load_json(path)[0]
    # row = {
    #     "query": " SELECT DISTINCT ?uri WHERE { ?uri a <http://dbpedia.org/ontology/BasketballPlayer> ; <http://dbpedia.org/ontology/birthDate> ?date ; <http://dbpedia.org/property/highlights> ?h FILTER regex(?h, \"MVP\") } ORDER BY DESC(?date) OFFSET 0 LIMIT 4",
    #     "question": "When was the Battle of Gettysburg?" }
    # print validate_sparql_func(row)




if __name__ == '__main__':
    main()
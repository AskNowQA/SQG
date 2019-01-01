from helper import *
from filter_helper import *
from tqdm import tqdm
import re
from random import shuffle
from sklearn.model_selection import train_test_split


# Checks the type of a filter query
# 0 filter value
# 1 bound
# 2 two uris
def filter_query_type(sparql):
    sparql = sparql.lower()

    if "bound" in sparql:
        return 0
    else:
        try:
            regex = re.findall(r"filter.*\(.*\).*}", sparql)[0]

            count = regex.count("?")
            if count == 1:
                return 1
            else:
                return 2
        except:
            return -1


# Prepares the filter hash for train test sets.
def prep_train_test_hash(path):
    data = load_json(path)
    counter = 0
    filter_hash = []
    filter_hash_counter = [0,0,0]
    for i, row in enumerate(tqdm(data)):
        question = row["question"]
        sparql = row["query"]

        if clean_filter_questions(sparql):
            type_, _ = filter_query_type(sparql)
            filter_hash.append([question, type_])
            counter += 1
            filter_hash_counter[type_] += 1

    print "Total Filter Questions No.:", len(data)
    print "Correct Filter Questions No.:", counter
    print "Filter Types Count:", filter_hash_counter
    shuffle(filter_hash)

    save_json(filter_hash, "data/filter_questions_clean.json")
    return filter_hash


def prep_train_test(data, split=0.35):
    x, y = zip(*data)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=split)

    train = zip(x_train, y_train)
    test = zip(x_test, y_test)

    shuffle(train)
    shuffle(test)

    print "Trainset Lenght:", len(train)
    print "Testset Lenght:", len(test)

    save_json(train, "data/train.json")
    save_json(test, "data/test.json")


def main():
    print "MAIN"
    data = prep_train_test_hash(filter_path)
    # prep_train_test(data)


if __name__ == '__main__':
    main()

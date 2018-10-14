import json, sys, os, random
from prepare_datasets import get_questions


PATH = "../data/clean_datasets/dbpedia/"

PATH_SECONDARY = "../data/clean_datasets/combined_datasets/"


# Loads a JSON file
def load_json(path):
    with open(path) as data_file:
        return json.load(data_file)


# Saves data to a JSON file
def save_json(data, name):
    with open(name, "w") as data_file:
        json.dump(data, data_file, sort_keys=True, indent=4, separators=(',', ': '))


# Gets Primary Classes Questions: List, Ask, Count and prepares them into train test
def prepare_primary_classes_train_test_1(key_):
    if key_ == 1:
        list_train, ask_train, count_train, = [], [], []
        list_test, ask_test, count_test, = [], [], []
        files = [f for f in os.listdir(PATH) if ("list" in f or "count" in f or "ask" in f)
                 and not ("dbnqa" in f or "qald" in f)]

        for f in files:
            data = load_json(PATH + f)

            if "list" in f:
                tmp_a, tmp_b = dataset_split_percent(data, 0.8)
                list_train += tmp_a
                list_test += tmp_b
            if "ask" in f:
                tmp_a, tmp_b = dataset_split_percent(data, 0.8)
                ask_train += tmp_a
                ask_test += tmp_b
            if "count" in f:
                tmp_a, tmp_b = dataset_split_percent(data, 0.8)
                count_train += tmp_a
                count_test += tmp_b

        save_json(list_train, "../data/clean_datasets/train_test/lcquad/list_train.json")
        save_json(list_test, "../data/clean_datasets/train_test/lcquad/list_test.json")
        save_json(ask_train, "../data/clean_datasets/train_test/lcquad/ask_train.json")
        save_json(ask_test, "../data/clean_datasets/train_test/lcquad/ask_test.json")
        save_json(count_train, "../data/clean_datasets/train_test/lcquad/count_train.json")
        save_json(count_test, "../data/clean_datasets/train_test/lcquad/count_test.json")

        print len(list_train), len(list_test)
        print len(ask_train), len(ask_test)
        print len(count_train), len(count_test)
    elif key_ == 2:
        list_train, ask_train, count_train, = [], [], []
        list_test, ask_test, count_test, = [], [], []
        files = [f for f in os.listdir(PATH) if ("list" in f or "count" in f or "ask" in f)
                 and "dbnqa" not in f]

        for f in files:
            data = load_json(PATH + f)

            if "list" in f:
                tmp_a, tmp_b = dataset_split_percent(data, 0.8)
                list_train += tmp_a
                list_test += tmp_b
            if "ask" in f:
                tmp_a, tmp_b = dataset_split_percent(data, 0.8)
                ask_train += tmp_a
                ask_test += tmp_b
            if "count" in f:
                tmp_a, tmp_b = dataset_split_percent(data, 0.8)
                count_train += tmp_a
                count_test += tmp_b

        save_json(list_train, "../data/clean_datasets/train_test/lcquad_qald/list_train.json")
        save_json(list_test, "../data/clean_datasets/train_test/lcquad_qald/list_test.json")
        save_json(ask_train, "../data/clean_datasets/train_test/lcquad_qald/ask_train.json")
        save_json(ask_test, "../data/clean_datasets/train_test/lcquad_qald/ask_test.json")
        save_json(count_train, "../data/clean_datasets/train_test/lcquad_qald/count_train.json")
        save_json(count_test, "../data/clean_datasets/train_test/lcquad_qald/count_test.json")

        print len(list_train), len(list_test)
        print len(ask_train), len(ask_test)
        print len(count_train), len(count_test)
    elif key_ == 3:
        list_train, ask_train, count_train,  = [], [], []
        list_test, ask_test, count_test, = [], [], []
        files = [f for f in os.listdir(PATH) if "list" in f or "count" in f or "ask" in f]

        for f in files:
            data = load_json(PATH + f)

            if "dbnqa" in f:
                random.shuffle(data)
                data = data[:int(len(data)*0.01)]
                if "list" in f:
                    data = data[:int(len(data) * 0.01)]

            if "list" in f:
                tmp_a, tmp_b = dataset_split_percent(data, 0.8)
                list_train += tmp_a
                list_test += tmp_b
            if "ask" in f:
                tmp_a, tmp_b = dataset_split_percent(data, 0.8)
                ask_train += tmp_a
                ask_test += tmp_b
            if "count" in f:
                tmp_a, tmp_b = dataset_split_percent(data, 0.8)
                count_train += tmp_a
                count_test += tmp_b

        # save_json(list_train, "../data/clean_datasets/train_test/1/list_train.json")
        # save_json(list_test, "../data/clean_datasets/train_test/1/list_test.json")
        # save_json(ask_train, "../data/clean_datasets/train_test/1/ask_train.json")
        # save_json(ask_test, "../data/clean_datasets/train_test/1/ask_test.json")
        # save_json(count_train, "../data/clean_datasets/train_test/1/count_train.json")
        # save_json(count_test, "../data/clean_datasets/train_test/1/count_test.json")

        print len(list_train), len(list_test)
        print len(ask_train), len(ask_test)
        print len(count_train), len(count_test)

    else:
        sys.exit("Wrong Key !!!")


# Splits a list into two by a percentage. 0.1, 0.2, 0.8
def dataset_split_percent(original, value):
    list_a = original[:int(len(original)*value)]
    list_b = original[int(len(original)*value):]
    return list_a, list_b


# Prepares questions and target. Make it ready for classifier use
def prepare_primary_classes_train_test_2(path):
    files = [f for f in os.listdir(path)]

    train, test = [], []
    for f in files:
        data = load_json(path+f)
        if "train" in f:
            tmp = [row["question"] for row in data]
            if "list" in f:
                target = [0]*len(tmp)
            if "ask" in f:
                target = [1]*len(tmp)
            if "count" in f:
                target = [2]*len(tmp)

            train += zip(tmp, target)

        if "test" in f:
            tmp = [row["question"] for row in data]
            if "list" in f:
                target = [0]*len(tmp)
            if "ask" in f:
                target = [1]*len(tmp)
            if "count" in f:
                target = [2]*len(tmp)

            test += zip(tmp, target)

    random.shuffle(train)
    random.shuffle(test)

    # save_json(train, "../data/clean_datasets/train_test_clean/lcquad_qald/train.json")
    # save_json(test, "../data/clean_datasets/train_test_clean/lcquad_qald/test.json")


def prepare_secondary_classes_train_test_1():

    order = load_json(PATH_SECONDARY + "order_all.json")
    filter_ = load_json(PATH_SECONDARY + "filter_all.json")

    list_ = load_json(PATH_SECONDARY + "list_all.json")
    random.shuffle(list_)
    list_ = list_[:60000]

    ask = load_json(PATH_SECONDARY + "ask_all.json")
    random.shuffle(ask)
    ask = ask[:25000]

    count_ = load_json(PATH_SECONDARY + "count_all.json")
    random.shuffle(count_)
    count_ = count_[:25000]

    list_questions = [q["question"] for q in list_]
    ask_questions = [q["question"] for q in ask]
    count_questions = [q["question"] for q in count_]
    order_questions = [q["question"] for q in order]
    filter_questions = [q["question"] for q in filter_]

    # ORDER

    # Order Questions Loop
    list_questions_no_order = [i for c, i in enumerate(list_questions) if i not in order_questions and c < 6000]
    ask_questions_no_order = [i for c, i in enumerate(ask_questions) if i not in order_questions and c < 4000]
    count_questions_no_order = [i for c, i in enumerate(count_questions) if i not in order_questions and c < 4000]

    order_questions = zip(order_questions, [1]*len(order_questions))
    no_order = list_questions_no_order + ask_questions_no_order + count_questions_no_order
    no_order = zip(no_order, [0]*len(no_order))

    save_json(order_questions, "../data/clean_datasets/train_test/order/order.json")
    save_json(no_order, "../data/clean_datasets/train_test/order/no_order.json")
    # save_json(list_questions_no_order, "../data/clean_datasets/train_test/order/list_no_order.json")
    # save_json(ask_questions_no_order, "../data/clean_datasets/train_test/order/ask_no_order.json")
    # save_json(count_questions_no_order, "../data/clean_datasets/train_test/order/count_no_order.json")


    # FILTER

    # Filter Questions Loop
    list_questions_no_filter = [i for c, i in enumerate(list_questions) if i not in filter_questions and c < 3000]
    ask_questions_no_filter = [i for c, i in enumerate(ask_questions) if i[0] not in filter_questions and c < 3000]
    count_questions_no_filter = [i for c, i in enumerate(count_questions) if i[0] not in filter_questions and c < 3000]

    filter_questions = zip(filter_questions, [1]*len(filter_questions))
    no_filter = list_questions_no_filter + ask_questions_no_filter + count_questions_no_filter
    no_filter = zip(no_filter, [0]*len(no_filter))

    save_json(filter_questions, "../data/clean_datasets/train_test/filter/filter.json")
    save_json(no_filter, "../data/clean_datasets/train_test/filter/no_filter.json")
    # save_json(list_questions_no_filter, "../data/clean_datasets/train_test/filter/list_no_filter.json")
    # save_json(ask_questions_no_filter, "../data/clean_datasets/train_test/filter/ask_no_filter.json")
    # save_json(count_questions_no_filter, "../data/clean_datasets/train_test/filter/count_no_filter.json")


def prepare_secondary_classes_train_test_2():
    order = load_json("../data/clean_datasets/train_test/order/order.json")
    no_order = load_json("../data/clean_datasets/train_test/order/no_order.json")

    all = order + no_order
    random.shuffle(all)

    train, test = dataset_split_percent(all, 0.8)

    random.shuffle(train)
    random.shuffle(test)
    save_json(train, "../data/clean_datasets/train_test_clean/order/train.json")
    save_json(test, "../data/clean_datasets/train_test_clean/order/test.json")


    filter_ = load_json("../data/clean_datasets/train_test/filter/filter.json")
    no_filter = load_json("../data/clean_datasets/train_test/filter/no_filter.json")

    all = filter_ + no_filter
    random.shuffle(all)

    train, test = dataset_split_percent(all, 0.8)
    random.shuffle(train)
    random.shuffle(test)

    save_json(train, "../data/clean_datasets/train_test_clean/filter/train.json")
    save_json(test, "../data/clean_datasets/train_test_clean/filter/test.json")


def main():
    print "### MAIN ###"
    # prepare_primary_classes_train_test_1(4)
    # prepare_primary_classes_train_test_2("../data/clean_datasets/train_test/lcquad_qald/")
    # prepare_secondary_classes_train_test_1()
    prepare_secondary_classes_train_test_2()


if __name__ == '__main__':
    print "Preparing Training and Test Data from Combined Datasets !!!"
    main()

    # files_1 = [f for f in os.listdir("../data/clean_datasets/combined_datasets/")]
    # for f in files_1:
    #     print f, len(load_json("../data/clean_datasets/combined_datasets/"+f))
    #
    # files_2 = [f for f in os.listdir("../data/clean_datasets/train_test/")]
    # for f in files_2:
    #     print f, len(load_json("../data/clean_datasets/train_test/" + f))
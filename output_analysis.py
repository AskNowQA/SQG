import json
from common.stats import Stats


def load_ds(name):
    with open("output/{}.json".format(name)) as data_file:
        return json.load(data_file)


def filter(ds, filter_func):
    result = []
    for i in range(len(ds)):
        if filter_func(ds[i]):
            result.append(i)
    return result


def diff(ds_1, ds_2, f1=None, f2=None):
    result = []
    for i in range(len(ds_1)):
        if i < len(ds_2):
            # if ds_1[i] != ds_2[i]:
            if (f1 is None or ds_1[i]["correct_answer"] == f1) and (f2 is None or ds_2[i]["correct_answer"] == f2):
                result.append(i)
                print i
                print ds_1[i]
                print ds_2[i]
                print
    return result


def default(ds, n=-1):
    stat = Stats()
    for data in ds:
        stat.inc("total")
        if "answer" in data:
            stat.inc(data["answer"])
        if stat["total"] == n:
            break

    return stat


if __name__ == "__main__":
    print "LC_Quad"
    ds = load_ds("15")

    print default(ds, 100)
    print "answer_incorrect", filter(ds, lambda x:
        x["answer"] == "answer_incorrect" if "answer" in x else False)

    print "answer_no_path", filter(ds, lambda x:
        x["answer"] == "answer_no_path" if "answer" in x else False)

    print "No result", filter(ds, lambda x:
        x["answer"] == "" if "answer" in x else False)


    # print "\nWebQuestion"
    # default(load_ds("wq_5"))  # Fix various bugs
    # diff(load_ds("wq_3"), load_ds("wq_5"), True, False)

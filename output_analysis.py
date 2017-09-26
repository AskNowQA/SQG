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
    ds_1 = load_ds("15")
    print default(ds_1, 4000)

    ds_2 = load_ds("16")
    print default(ds_2, 4000)

    # print "answer_incorrect", filter(ds_1, lambda x:
    #     x["answer"] == "answer_incorrect" if "answer" in x else False)
    #
    # print "answer_no_path", filter(ds_1, lambda x:
    #     x["answer"] == "answer_no_path" if "answer" in x else False)
    #
    # print "No result", filter(ds_1, lambda x:
    #     x["answer"] == "" if "answer" in x else False)


    print "\nWebQuestion"
    wq_1 = load_ds("wq_7")
    print default(wq_1, 4000)

    wq_2 = load_ds("wg_9")
    print default(wq_1, 4000)

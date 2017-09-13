import json


def load_ds(name):
    with open("output/{}.json".format(name)) as data_file:
        return json.load(data_file)


def diff(ds_1, ds_2, f1=None, f2=None):
    for i in range(len(ds_1)):

        if i < len(ds_2):
            if ds_1[i] != ds_2[i]:
                if (f1 is None or ds_1[i]["correct_answer"] == f1) and (f2 is None or ds_2[i]["correct_answer"] == f2):
                    print ds_1[i]
                    print ds_2[i]
                    print

def default(ds, n=-1):
    total = 0
    answered = 0
    for data in ds:
        total += 1
        if data["correct_answer"]:
            answered += 1
        if total == n:
            break

    print answered, total
    pass

if __name__ == "__main__":
    default(load_ds("1"))
    default(load_ds("2"))
    default(load_ds("3"))
    default(load_ds("4"))
    default(load_ds("5"))
    diff(load_ds("4"), load_ds("5"), True, False)

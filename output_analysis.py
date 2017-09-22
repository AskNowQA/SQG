import json


def load_ds(name):
    with open("output/{}.json".format(name)) as data_file:
        return json.load(data_file)


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
    print "LC_Quad"
    default(load_ds("1"))
    default(load_ds("2"))
    default(load_ds("3"))
    default(load_ds("4"))
    default(load_ds("5"))  # TYPE
    default(load_ds("6"))  # BOOL
    default(load_ds("7"))  # Bug fix
    default(load_ds("8"))  # Two var-Fixed position
    default(load_ds("9"))  # Fix dataset
    default(load_ds("10"))  # Extend edge
    default(load_ds("11"))  # Fix various bugs
    default(load_ds("12"))  # Fix various bugs
    result = diff(load_ds("11"), load_ds("12"), None, False)
    print result

    print "\nWebQuestion"
    default(load_ds("wq_1"))
    default(load_ds("wq_2"))  # BOOL
    default(load_ds("wq_3"))  # Two var-Fixed position
    default(load_ds("wq_5"))  # Fix various bugs
    # diff(load_ds("wq_3"), load_ds("wq_5"), True, False)

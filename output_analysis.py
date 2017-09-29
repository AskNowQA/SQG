import json
from common.stats import Stats
import matplotlib.pyplot as plt


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


def bar_chart_per_feature(input_json):
    stats_overall = Stats()
    stats_with_answer = dict()
    stats_without_answer = dict()
    for item in input_json:
        for f in item["features"]:
            stats_overall.inc(f)
            if item["answer"].startswith("-"):
                if item["answer"] not in stats_without_answer:
                    stats_without_answer[item["answer"]] = Stats()
                stats_without_answer[item["answer"]].inc(f)
            else:
                if item["answer"] not in stats_with_answer:
                    stats_with_answer[item["answer"]] = Stats()
                stats_with_answer[item["answer"]].inc(f)

    print stats_overall
    print "-" * 10, "covered"
    stats_with_answer_keys = stats_with_answer.keys()
    stats_with_answer_keys.sort()
    for item in stats_with_answer_keys:
        print item, stats_with_answer[item]
    print "-" * 10, "not covered"
    for item in stats_without_answer:
        print item, stats_without_answer[item]
    print "-" * 100

    keys = stats_overall.dict.keys()
    ind = range(len(stats_overall.dict))
    last = Stats()
    plt_idx = []
    colors = ["green", "yellowgreen", "lightgreen", "lime", "olive"]

    fig = plt.figure()
    ax = plt.subplot(111)

    overall = [stats_overall[key] for key in keys]
    p0 = ax.bar(ind, overall, 0.35, color='red')

    color_id = 0
    for item in stats_with_answer_keys:
        answered = [stats_with_answer[item][key] for key in keys]
        tmp = [last[key] for key in keys]
        plt_idx.append(ax.bar(ind, answered, 0.2, color=colors[color_id], bottom=tmp))
        last.dict = dict([(key, stats_with_answer[item][key] + last[key]) for key in keys])
        color_id += 1

    plt.xticks(ind, keys, rotation='vertical')
    plt.subplots_adjust(bottom=0.2, left=0.1, right=0.7)
    ax.legend([p0] + [item[0] for item in plt_idx], ["All"] + [item for item in stats_with_answer_keys],
              loc='center left',
              bbox_to_anchor=(1, 0.5))
    plt.show()


if __name__ == "__main__":
    # ds_1 = load_ds("17")
    # bar_chart_per_feature(ds_1)

    ds_1 = load_ds("wq_13")
    bar_chart_per_feature(ds_1)

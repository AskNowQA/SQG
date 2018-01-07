import json
from common.utility.stats import Stats
import matplotlib.pyplot as plt
import argparse


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
        if "generated_queries" in data:
            number_of_quries = len(data["generated_queries"])
            if number_of_quries > 0:
                stat.inc("has_queries")
                stat.inc("generated_queries", number_of_quries)

    return stat


def bar_chart_per_feature(input_json):
    stats_overall = Stats()
    stats_features = Stats()
    stats_with_answer = dict()
    stats_without_answer = dict()
    for item in input_json:
        stats_overall.inc("total")
        if "answer" in item:
            stats_overall.inc(item["answer"])
        for f in item["features"]:
            stats_features.inc(f)
            if item["answer"].startswith("-"):
                if item["answer"] not in stats_without_answer:
                    stats_without_answer[item["answer"]] = Stats()
                stats_without_answer[item["answer"]].inc(f)
            else:
                if item["answer"] not in stats_with_answer:
                    stats_with_answer[item["answer"]] = Stats()
                stats_with_answer[item["answer"]].inc(f)

    print stats_features
    print "-" * 10, "covered"
    stats_with_answer_keys = stats_with_answer.keys()
    stats_with_answer_keys.sort()
    for item in stats_with_answer_keys:
        print "{}: {} -- ".format(item, stats_overall[item]), stats_with_answer[item]
    print "-" * 10, "not covered"
    stats_without_answer_keys = stats_without_answer.keys()
    stats_without_answer_keys.sort()
    for item in stats_without_answer_keys:
        print "{}: {} -- ".format(item, stats_overall[item]), stats_without_answer[item]
    print "-" * 100

    keys = stats_features.dict.keys()
    ind = range(len(stats_features.dict))
    last = Stats()
    plt_idx = []
    colors = ["green", "yellowgreen", "lightgreen", "lime", "olive"]

    fig = plt.figure()
    ax = plt.subplot(111)

    overall = [stats_features[key] for key in keys]
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
    parser = argparse.ArgumentParser(description='Analyse the output of query generator')
    parser.add_argument("--file", help="file name to save the results", default="tmp", dest="file_name")
    args = parser.parse_args()

    ds_1 = load_ds(args.file_name)
    print default(ds_1)

    # ds_1 = load_ds("wq_14")
    # print default(ds_1)
    # bar_chart_per_feature(ds_1)

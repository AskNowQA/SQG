import re
from itertools import takewhile
import os.path
from parser.lc_quad import LC_Qaud


def get_entries(name, path):
    with open(path) as file:
        for line in file:
            if "http://www.wdaqua.eu/qa#" + name in line:
                buf = [line]
                buf.extend(takewhile(str.strip, file))  # read until blank line
                yield re.findall(r'<(http://dbpedia[^>]+)>', ''.join(buf))


if __name__ == "__main__":
    base_dir = "../data/"
    rel_dir_name = os.path.join(base_dir, "relnliodLogs")
    ned_dir_name = os.path.join(base_dir, "tagmeNEDlogs")

    ds = LC_Qaud("../data/LC-QUAD/linked_3200.json")
    ds.load()
    ds.parse()

    i = 0
    input_files = os.listdir(rel_dir_name)
    input_files.sort()
    for name in input_files:
        print ds.qapairs[i].question
        for item in get_entries("AnnotationOfRelation", os.path.join(rel_dir_name, name)):
            print item,
        print
        for item in get_entries("AnnotationOfInstance", os.path.join(ned_dir_name, name)):
            print item,
        print "\n"
        i += 1

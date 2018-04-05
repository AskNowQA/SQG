import re
from itertools import takewhile
import os.path
from parser.lc_quad import LC_Qaud
import json
from tqdm import tqdm


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
    dataset = []
    q = 0
    for name in tqdm(input_files):
        # print i
        relations = list(get_entries("AnnotationOfRelation", os.path.join(rel_dir_name, name)))
        if len(relations) > 0:
            relations = [{"surface": [0, 0], "uris": [{"uri": item[0], "confidence": 1}]} for item in
                         relations if len(item) > 0]
        else:
            q += 1
        entities = list(get_entries("AnnotationOfInstance", os.path.join(ned_dir_name, name)))
        if len(entities) > 0:
            entities = [{"surface": [0, 0], "uris": [{"uri": item[0], "confidence": 1}]} for item in
                        entities]
        dataset.append({"question": ds.qapairs[i].question.text, "entities": entities, "relations": relations})
        i += 1
    print q
    with open("../data/LC-QUAD/TagMeRelnliod/output_2300.json", "w") as output_file:
        json.dump(dataset, output_file)
        # TagMeRelnliod

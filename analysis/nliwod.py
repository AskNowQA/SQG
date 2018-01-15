from parser.lc_quad_linked import LC_Qaud_Linked
import json
from kb.dbpedia import DBpedia
from parser.answerparser import AnswerParser
from common.utility.stats import Stats
from common.container.answerset import AnswerSet
from tqdm import tqdm

stats = Stats()

with open("../output/nliwod_origin.json") as data_file:
    nliwod = json.load(data_file)

ds = LC_Qaud_Linked(path="../data/LC-QUAD/linked_answer6.json")
ds.load()
ds.parse()

kb = DBpedia()
parser = AnswerParser(kb)
i = 0
for qapair in tqdm(ds.qapairs):
    nliwod_row = nliwod[i]
    if qapair.id == nliwod_row["q_id"]:
        query = nliwod_row["candidate"]
        raw_result = kb.query(query)
        result = AnswerSet(raw_result[1], parser.parse_queryresult)
        nliwod_row["answer"] = raw_result[1]
        if qapair.answerset == result:
            stats.inc("correct")
            nliwod_row["correct"] = True
        else:
            stats.inc("-incorrect")
            nliwod_row["correct"] = False
    else:
        stats.inc("-missmatch id")
        print "not id"
    i += 1
    stats.inc("total")
    # if i == 10:
    #     break
with open("../output/nliwod_origin_with_ans.json", "w") as data_file:
    json.dump(nliwod, data_file)
""
print stats

# -incorrect:4382 correct:618 total:5000

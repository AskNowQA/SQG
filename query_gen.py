from parser.lc_quad_linked import LC_Qaud_Linked
from parser.webqsp import WebQSP
from parser.qald import Qald
from common.container.answerset import AnswerSet
from common.graph.graph import Graph
from common.utility.stats import Stats
from linker.jerrl import Jerrl
from linker.earl import Earl
from common.query.querybuilder import QueryBuilder
import json
import argparse
import logging
import common.utility.utility


def qg(linker, kb, parser, qapair):
    print qapair.sparql
    print qapair.question

    ask_query = "ASK " in qapair.sparql.query
    count_query = "COUNT(" in qapair.sparql.query
    sort_query = "order by" in qapair.sparql.raw_query.lower()
    entities, ontologies = linker.do(qapair, force_gold=True)

    graph = Graph(kb)
    queryBuilder = QueryBuilder()

    logger.info("start finding the minimal subgraph")
    graph.find_minimal_subgraph(entities, ontologies, ask_query, sort_query)
    print graph
    print "-----"
    wheres = queryBuilder.to_where_statement(graph, parser.parse_queryresult, ask_query, count_query, sort_query)

    output_where = [{"query": " .".join(item["where"]), "correct": False, "target_var": "?u_0"} for item in wheres]
    if len(wheres) == 0:
        return "-without_path", output_where
    correct = False

    for idx in range(len(wheres)):
        where = wheres[idx]
        if "answer" in where:
            answerset = where["answer"]
            target_var = where["target_var"]
        else:
            target_var = "?u_" + str(item["suggested_id"])
            raw_answer = kb.query_where(item["where"], target_var, count_query, ask_query)
            answerset = AnswerSet(raw_answer, parser.parse_queryresult)

        output_where[idx]["target_var"] = target_var
        if answerset == qapair.answerset:
            correct = True
            output_where[idx]["correct"] = True
            output_where[idx]["target_var"] = target_var
        else:
            if target_var == "?u_0":
                target_var = "?u_1"
            else:
                target_var = "?u_0"
            raw_answer = kb.query_where(item["where"], target_var, count_query, ask_query)
            answerset = AnswerSet(raw_answer, parser.parse_queryresult)
            if answerset == qapair.answerset:
                correct = True
                output_where[idx]["correct"] = True
                output_where[idx]["target_var"] = target_var

    return "correct" if correct else "-incorrect", output_where


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    common.utility.utility.setup_logging()

    parser = argparse.ArgumentParser(description='Generate SPARQL query')
    parser.add_argument("--ds", help="0: LC-Quad, 1: WebQuestions", type=int, default=0, dest="dataset")
    parser.add_argument("--file", help="file name to save the results", default="tmp", dest="file_name")
    parser.add_argument("--in", help="only works on this list", type=int, nargs='+', default=[], dest="list_id")
    parser.add_argument("--max", help="max threshold", type=int, default=-1, dest="max")
    parser.add_argument("--linker", help="0: gold linker, 1: EARL", type=int, default=-1, dest="linker")
    args = parser.parse_args()

    stats = Stats()
    t = args.dataset
    output_file = args.file_name
    if args.linker == 0:
        linker = Jerrl()
    else:
        linker = Earl()

    if t == 0:
        ds = LC_Qaud_Linked(path="./data/LC-QUAD/linked_answer6.json")
        ds.load()
        ds.parse()
    elif t == 1:
        ds = WebQSP()
        ds.load()
        ds.parse()
        ds.extend("./data/WebQuestionsSP/WebQSP.test.json")
    elif t == 5:
        ds = Qald(Qald.qald_5)
        ds.load()
        ds.parse()
    elif t == 6:
        ds = Qald(Qald.qald_6)
        ds.load()
        ds.parse()
    elif t == 7:
        ds = Qald(Qald.qald_7_largescale)
        ds.load()
        ds.parse()
    elif t == 8:
        ds = Qald(Qald.qald_7_multilingual)
        ds.load()
        ds.parse()

    tmp = []
    output = []
    for qapair in ds.qapairs:
        stats.inc("total")
        if len(args.list_id) > 0 and stats["total"] - 1 not in args.list_id:
            continue
        output_row = {"question": qapair.question.text,
                      "id": qapair.id,
                      "query": qapair.sparql.query,
                      "answer": "",
                      "features": list(qapair.sparql.query_features()),
                      "generated_queries": []}

        if qapair.answerset is None or len(qapair.answerset) == 0:
            stats.inc("query_no_answer")
            output_row["answer"] = "-no_answer"
        else:
            result, where = qg(linker, ds.parser.kb, ds.parser, qapair)
            stats.inc(result)
            output_row["answer"] = result
            output_row["generated_queries"] = where
            print result

        if args.max != -1 and stats["total"] > args.max:
            break
        print "-" * 10
        print stats
        print "-" * 10
        output.append(output_row)

        if stats["total"] % 100 == 0:
            with open("output/{}.json".format(output_file), "w") as data_file:
                json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

    with open("output/{}.json".format(output_file), "w") as data_file:
        json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

from parser.lc_quad import LC_Qaud
from parser.lc_quad_linked import LC_Qaud_Linked
from parser.webqsp import WebQSP
from parser.qald import Qald
from kb.dbpedia import DBpedia
from kb.freebase import Freebase
from common.container.answerset import AnswerSet
from common.graph.graph import Graph
from common.utility.stats import Stats
from jerrl.jerrl import Jerrl
import json
import argparse


def qg(kb, parser, qapair):
    print qapair.sparql
    print qapair.question

    ask_query = "ASK " in qapair.sparql.query
    count_query = "COUNT(" in qapair.sparql.query
    sort_query = "order by" in qapair.sparql.raw_query.lower()
    jerrl = Jerrl()
    entities, ontologies = jerrl.do(qapair)

    graph = Graph(kb)
    graph.find_minimal_subgraph(entities, ontologies, ask_query, sort_query)
    print graph
    print "-----"
    where = graph.to_where_statement(parser.parse_queryresult, ask_query, count_query, sort_query)
    output_where = [" .".join(item["where"]) for item in where]
    if len(where) == 0:
        return "-without_path", output_where
    elif len(where) == 1:
        item = where[0]
        print item
        if "answer" in item:
            answerset = item["answer"]
        else:
            raw_answer = kb.query_where(item["where"], return_vars="?u_" + str(item["suggested_id"]), count=count_query,
                                        ask=ask_query)
            answerset = AnswerSet(raw_answer, parser.parse_queryresult)
        if answerset == qapair.answerset:
            return "correct", output_where
        else:
            var = ""
            if item["suggested_id"] == 1:
                var = "?u_0"
            elif item["suggested_id"] == 0:
                var = "?u_1"
            raw_answer = kb.query_where(item["where"], return_vars=var, count=count_query, ask=ask_query)
            answerset = AnswerSet(raw_answer, parser.parse_queryresult)
            if answerset == qapair.answerset:
                return "multiple_var_with_correct_answer", output_where
            return "-incorrect", output_where
    else:
        for item in where:
            print item
            if "answer" in item:
                answerset = item["answer"]
            else:
                raw_answer = kb.query_where(item["where"], return_vars="?u_" + str(item["suggested_id"]), count=count_query,
                                            ask=ask_query)
                answerset = AnswerSet(raw_answer, parser.parse_queryresult)
            if answerset == qapair.answerset:
                return "multiple_path_with_correct_answer", output_where
            else:
                var = ""
                if item["suggested_id"] == 1:
                    var = "?u_0"
                elif item["suggested_id"] == 0:
                    var = "?u_1"
                raw_answer = kb.query_where(item["where"], return_vars=var, count=count_query, ask=ask_query)
                answerset = AnswerSet(raw_answer, parser.parse_queryresult)
                if answerset == qapair.answerset:
                    return "multiple_path_and_var_with_correct_answer", output_where
        return "-multiple_path_without_correct_answer", output_where


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate SPARQL query')
    parser.add_argument("--ds", help="0: LC-Quad, 1: WebQuestions", type=int, default=0, dest="dataset")
    parser.add_argument("--file", help="file name to save the results", default="tmp", dest="file_name")
    parser.add_argument("--in", help="only works on this list", type=int, nargs='+', default=[], dest="list_id")
    parser.add_argument("--max", help="max threshold", type=int, default=-1, dest="max")
    args = parser.parse_args()

    stats = Stats()
    t = args.dataset
    output_file = args.file_name

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
            result, where = qg(ds.parser.kb, ds.parser, qapair)
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

from parser.lc_quad import LC_Qaud
from parser.lc_quad_linked import LC_Qaud_Linked
from parser.webqsp import WebQSP
from parser.qald import Qald
from kb.dbpedia import DBpedia
from kb.freebase import Freebase
from common.answerset import AnswerSet
from common.graph.graph import Graph
from common.stats import Stats
from jerrl.jerrl import Jerrl
import json


def qg(kb, parser, qapair):
	print qapair.sparql
	print qapair.question

	ask_query = "ASK " in qapair.sparql.query

	jerrl = Jerrl()
	entities, ontologies = jerrl.do(qapair)

	graph = Graph(kb)
	graph.find_minimal_subgraph(entities, ontologies, ask_query)
	print graph
	print "-----"
	where = graph.to_where_statement()
	if len(where) == 0:
		return "answer_no_path"
	elif len(where) == 1:
		item = where[0]
		print graph
		print item[1]
		raw_answer = kb.query_where(item[1], return_vars="?u_" + str(item[0]), ask=ask_query)
		answerset = AnswerSet(raw_answer, parser.parse_queryresult)
		if answerset == qapair.answerset:
			return "answer_correct"
		else:
			var = ""
			if item[0] == 1:
				var = "?u_0"
			elif item[0] == 0:
				var = "?u_1"
			raw_answer = kb.query_where(item[1], return_vars=var, ask=ask_query)
			answerset = AnswerSet(raw_answer, parser.parse_queryresult)
			if answerset == qapair.answerset:
				return "answer_multiple_var_with_correct_answer"
			return "answer_incorrect"
	else:
		for item in where:
			print item[1]
			raw_answer = kb.query_where(item[1], return_vars="?u_" + str(item[0]), ask=ask_query)
			answerset = AnswerSet(raw_answer, parser.parse_queryresult)
			if answerset == qapair.answerset:
				return "answer_multiple_path_with_correct_answer"
		return "answer_multiple_path_without_correct_answer"


if __name__ == "__main__":
	stats = Stats()
	t = 0

	if t == 0:
		ds = LC_Qaud_Linked(path="./data/LC-QUAD/linked_answer5.json")
		kb = DBpedia()
		ds.load()
		ds.parse()
	elif t == 1:
		ds = WebQSP()
		kb = Freebase()
		ds.load()
		ds.parse()
		ds.extend("./data/WebQuestionsSP/WebQSP.test.json")
	elif t == 2:
		ds = Qald(Qald.qald_6)
		kb = DBpedia()
		ds.load()
		ds.parse()


	tmp = []
	output = []
	for qapair in ds.qapairs:
		stats.inc("total")
		# if stats["total"] - 1 not in []:
		# 	continue
		# if stats["total"] <= 4984:
		# 	continue
		output_row = {}

		output_row["question"] = qapair.question.text
		output_row["id"] = qapair.id
		output_row["no_answer"] = False
		output_row["query"] = qapair.sparql.query
		output_row["correct_answer"] = False
		if qapair.answerset is None or len(qapair.answerset) == 0:
			stats.inc("query_no_answer")
			output_row["no_answer"] = True
		elif "COUNT(" in qapair.sparql.query:
			stats.inc("query_count")
		elif qapair.answerset.number_of_answer() != 1:
			stats.inc("query_multiple_answer")
		else:
			result = qg(ds.parser.kb, ds.parser, qapair)
			stats.inc(result)
			output_row["answer"] = result
			print result

		# if stats["total"] > 100:
		# 	break
		print "-" * 10
		print stats
		print "-" * 10
		output.append(output_row)

		if stats["total"] % 100 == 0:
			with open("output/tmp.json", "w") as data_file:
				json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

	with open("output/tmp.json", "w") as data_file:
		json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

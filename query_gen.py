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
		# if stats["total"] - 1 not in [13, 17, 45, 133, 135, 282, 319, 331, 332, 359, 365, 390, 399, 432, 438, 569, 588, 597, 610, 672, 675, 725, 775, 834, 863, 875, 890, 957, 968, 1007, 1041, 1058, 1062, 1063, 1064, 1215, 1217, 1233, 1252, 1258, 1274, 1307, 1323, 1355, 1410, 1434, 1437, 1461, 1539, 1544, 1548, 1599, 1663, 1711, 1733, 1752, 1755, 1899, 1902, 1909, 1919, 1928, 1930, 1931, 1938, 2007, 2032, 2058, 2066, 2068, 2083, 2098, 2116, 2145, 2191, 2215, 2233, 2236, 2264, 2270, 2286, 2331, 2362, 2391, 2409, 2430, 2448, 2505, 2538, 2578, 2645, 2673, 2692, 2713, 2734, 2748, 2762, 2844, 2861, 2941, 3006, 3010, 3051, 3058, 3116, 3125, 3176, 3178, 3194, 3207, 3215, 3221, 3246, 3278, 3402, 3471, 3491, 3579, 3610, 3624, 3689, 3695, 3803, 3808, 3829, 3868, 3950, 3995, 4001, 4027, 4034, 4036, 4054, 4064, 4066, 4085, 4133, 4183, 4222, 4228, 4253, 4289, 4308, 4324, 4344, 4345, 4383, 4389, 4411, 4419, 4430, 4491, 4522, 4544, 4545, 4571, 4587, 4643, 4736, 4744, 4788, 4793, 4819, 4877, 4971, 4984]:
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
			if result == "answer_correct":
				output_row["correct_answer"] = True

			print result

		# if stats["total"] > 100:
		# 	break
		print "-" * 10
		print stats
		print "-" * 10
		output.append(output_row)

		if stats["total"] % 100 == 0:
			with open("output/12.json", "w") as data_file:
				json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

	with open("output/12.json", "w") as data_file:
		json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

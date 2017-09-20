from parser.lc_quad_linked import LC_Qaud_Linked
from parser.webqsp import WebQSP
from parser.qald import Qald
from kb.dbpedia import DBpedia
from kb.freebase import Freebase
from common.answerset import AnswerSet
from common.graph.graph import Graph
from common.stats import Stats
import json


def qg(kb, parser, qapair):
	print qapair.sparql
	print qapair.question

	ask_query = "ASK " in qapair.sparql.query
	all_uri = []
	entities = set([u for u in qapair.sparql.uris if u.is_entity()])
	ontologies = set([u for u in qapair.sparql.uris if u.is_ontology()])

	answer_uris = []
	for answer_row in qapair.answerset.answer_rows:
		for answer in answer_row.answers:
			if answer.answer_type == "uri":
				answer_uris.append(answer.answer)

	all_uri.extend(entities)
	all_uri.extend(ontologies)
	all_uri.extend(answer_uris)

	graph = Graph(kb)
	graph.find_minimal_subgraph(entities, ontologies, answer_uris, ask_query)
	print graph
	print "-----"
	where = graph.to_where_statement()
	if len(where) == 0:
		return 0
	elif len(where) == 1:
		where = where[0]
		print graph
		print where[1]
		raw_answer = kb.query_where(where[1], return_vars="?u_" + str(where[0]), ask=ask_query)
		answerset = AnswerSet(raw_answer, parser.parse_queryresult)
		if answerset == qapair.answerset:
			return 1
		else:
			return -1
	else:
		return len(where)

if __name__ == "__main__":
	stats = Stats()
	t = 2

	if t == 0:
		ds = LC_Qaud_Linked(path="./data/LC-QUAD/linked_answer4.json")
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
		# if total <= 7:
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
			results = qg(kb, ds.parser, qapair)
			if results == -1:
				stats.inc("answer_incorrect")
			elif results == 1:
				stats.inc("answer_correct")
				output_row["correct_answer"] = True
			elif results == 0:
				stats.inc("answer_no_path")
			else:
				stats.inc("answer_multiple_path")
			print "--"

		# if total > 100:
		# 	break
		print stats
		output.append(output_row)

		if stats["total"] % 100 == 0:
			with open("output/tmp2.json", "w") as data_file:
				json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

	with open("output/tmp2.json", "w") as data_file:
		json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

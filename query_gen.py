from parser.lc_quad_linked import LC_Qaud_Linked
from parser.webqsp import WebQSP
from kb.dbpedia import DBpedia
from kb.freebase import Freebase
from common.answerset import AnswerSet
from common.graph.graph import Graph
import json


def prepare_dataset(ds):
	ds.load()
	ds.parse()
	return ds

def qg(kb, parser, qapair):
	if qapair.answerset.number_of_answer() != 1:
		return False


	ask_query = "ASK " in qapair.sparql.query

	print qapair.sparql
	print qapair.question
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
		return False
	where = where[0]
	print graph
	print where
	raw_answer = kb.query_where(where, ask=ask_query)
	answerset = AnswerSet(raw_answer, parser.parse_queryresult)
	if answerset == qapair.answerset:
		return True

	return False

if __name__ == "__main__":
	bool_q = 0
	count_q = 0
	total = 0
	no_answer = 0
	type_q = 0
	correct_answer = 0

	ds = LC_Qaud_Linked(path="./data/LC-QUAD/linked_answer4.json")
	kb = DBpedia()
	# ds = WebQSP("./data/WebQuestionsSP/WebQSP.test.json")
	# kb = Freebase()

	tmp = []
	output = []
	for qapair in prepare_dataset(ds).qapairs:
		total += 1
		print total
		# if total <= 740:
		# 	continue
		output_row = {}

		output_row["question"] = qapair.question.text
		output_row["id"] = qapair.id
		output_row["no_answer"] = False
		output_row["query"] = ""
		output_row["correct_answer"] = False
		if qapair.answerset is None or len(qapair.answerset) == 0:
			no_answer += 1
			output_row["no_answer"] = True
		elif "COUNT(" in qapair.sparql.query:
				count_q += 1
				output_row["query"] = "COUNT"
		# elif "ASK " in qapair.sparql.query:
		# 		bool_q += 1
		# 		output_row["query"] = "ASK"
		else:
			if qg(kb, ds.parser, qapair):
				print "True"
				correct_answer += 1
				output_row["correct_answer"] = True
			else:
				print "False"
			print "--"

		# if total > 1:
		# 	break
		print no_answer, bool_q, count_q, type_q, correct_answer,  total
		output.append(output_row)

		if total % 100 == 0:
			with open("output/6.json", "w") as data_file:
				json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

	with open("output/tmp.6", "w") as data_file:
		json.dump(output, data_file, sort_keys=True, indent=4, separators=(',', ': '))

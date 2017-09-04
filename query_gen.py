from parser.lc_quad_linked import LC_Qaud_Linked
from jerrl.jerrl import Jerrl
from dbpedia.dbpedia import DBpedia
from common.graph.paths import Paths
from common.answerset import AnswerSet
from parser.lc_quad_linked import LC_Qaud_LinkedParser


def prepare_dataset(ds):
	ds.load()
	ds.parse()
	return ds


def qg(qapair):
	if "22-rdf-syntax-ns#type" in qapair.sparql.raw_query:
		print "No support for type"
		return False
	if "ASK WHERE" in qapair.sparql.raw_query:
		print "No boolean question"
		return False
	print qapair.sparql
	print qapair.question
	entities = [u for u in qapair.sparql.uris if u.is_entity()]
	ontologies = [u for u in qapair.sparql.uris if u.is_ontology()]

	answer_uris = []
	for answer_row in qapair.answerset.answer_rows:
		for answer in answer_row.answers:
			if answer.answer_type == "uri":
				answer_uris.append(answer.answer)
				entities.append(answer.answer)

	dbp = DBpedia()
	path_set = Paths()
	if len(entities) > 100:
		# print "len(entities)", len(entities)
		return False
	for ent1 in entities:
		print ent1
		for ent2 in entities:
			if ent1 == ent2 or (ent1 in answer_uris and ent2 in answer_uris):
				continue
			paths = dbp.find_minimal_subgraph(ent1, ent2, lambda uri: uri in answer_uris, max_hop=2)
			if paths is not None and len(paths) > 0:
				for path in paths:
					path_set.add_path(path)

	print "paths", len(path_set.paths)
	for path in path_set.paths:
		print path

	path_set.merge_paths()
	print "Merged paths:", len(path_set.paths)
	for path in path_set.paths:
		print path

	path_set.expand_paths()
	print "expand paths", len(path_set.paths)
	for path in path_set.paths:
		print path

	path_set.merge_paths()
	print "Merged paths:", len(path_set.paths)
	for path in path_set.paths:
		print path

	path_set.prune_paths(qapair.answerset)
	print "pruned paths", len(path_set.paths)
	for path in path_set.paths:
		print path

	path_set.replace_answers(qapair.answerset)
	print "replace answers", len(path_set.paths)
	for path in path_set.paths:
		print path

	for path in path_set.paths:
		q = path.generate_sparql()
		if q is not None:
			print q
			raw_answerset = dbp.query(q)
			if raw_answerset[0] == 200:
				answerset = AnswerSet(raw_answerset[1], LC_Qaud_LinkedParser().parse_answerset)
				if answerset == qapair.answerset:
					return True
	return False

if __name__ == "__main__":
	jerrl = Jerrl()
	i = 0
	no_answer = 0
	correct_answer = 0
	ds = LC_Qaud_Linked(path="./data/LC-QUAD/linked_answer3.json")
	tmp = []
	for qapair in prepare_dataset(ds).qapairs:
		i += 1
		print i
		if i <= 7:
			continue
		results = jerrl.do(qapair)
		# if len(results) != 2:
		# 	continue
		if qapair.answerset is None or len(qapair.answerset) == 0:
			no_answer += 1
		else:
			if qg(qapair):
				print "True"
				correct_answer += 1
			else:
				print "False"
			# print qapair.answerset
			print "--"

		if i > 500:
			break
		print no_answer, correct_answer,  i

from parser.lc_quad_linked import LC_Qaud_Linked
from jerrl.jerrl import Jerrl
from dbpedia.dbpedia import DBpedia
from common.graph.paths import Paths


def prepare_dataset(ds):
	ds.load()
	ds.parse()
	return ds


def qg(qapair):
	print qapair.sparql
	entities = [u for u in qapair.sparql.uris if u.is_entity()]
	ontologies = [u for u in qapair.sparql.uris if u.is_ontology()]

	answer_uri = []
	for answer_set in qapair.answers.answers:
		for answer in answer_set:
			if answer.answer_type == "uri":
				answer_uri.append(answer.answer)
				entities.append(answer.answer)

	dbp = DBpedia()

	path_set = Paths()
	if len(entities) > 100:
		# print "len(entities)", len(entities)
		return False
	for ent1 in entities:
		for ent2 in entities:
			if ent1 == ent2 or (ent1 in answer_uri and ent2 in answer_uri):
				continue
			paths = dbp.find_minimal_subgraph(ent1, ent2, max_hop=2)
			if paths is not None and len(paths) > 0:
				for path in paths:
					path_set.add_path(path)

	# for path in path_set.paths:
	# 	print path
	# print "-----"

	path_set.prune_paths(qapair.answers)
	path_set.replace_answers(qapair.answers)
	path_set.merge_paths()

	if len(path_set.paths) == 1:
		q = path_set.paths[0].generate_sparql()
		print q
		print dbp.query(q)
	# for path in path_set.paths:
	# 	print path
	# 	print path.generate_sparql()

	# print len(entities), len(ontologies)

if __name__ == "__main__":
	jerrl = Jerrl()
	i = 0
	no_answer = 0
	ds = LC_Qaud_Linked(path="./data/LC-QUAD/linked_answer3.json")
	tmp = []
	for qapair in prepare_dataset(ds).qapairs:
		i += 1
		print i
		# if i <= 40:
		# 	continue
		results = jerrl.do(qapair)
		# if len(results) != 2:
		# 	continue
		if qapair.answers is None or len(qapair.answers) == 0:
			no_answer += 1
		else:
			qg(qapair)
			# print qapair.answers
			print "--"

		if i > 15:
			break
	print no_answer, i
from parser.lc_quad_linked import LC_Qaud_Linked
from jerrl.jerrl import Jerrl
from dbpedia.dbpedia import DBpedia


def prepare_dataset(ds):
	ds.load()
	ds.parse()
	return ds


def qg(qapair):
	print qapair.sparql
	entities = [u for u in qapair.sparql.uris if u.is_entity()]
	ontologies = [u for u in qapair.sparql.uris if u.is_ontology()]

	answer_uri = []
	for answer in qapair.answers.answers:
		if answer.type == "uri":
			answer_uri.append(answer.answer)
			entities.append(answer.answer)

	results = []
	dbp = DBpedia()

	for ent1 in entities:
		for ent2 in entities:
			if ent1 == ent2 or (ent1 in answer_uri and ent2 in answer_uri):
				continue
			paths = dbp.find_minimal_subgraph(ent1, ent2, max_hop=2)
			if paths is not None and len(paths) > 0:
				for path in paths:
					print path

	for r in results:
		print r
	print len(entities), len(ontologies)

if __name__ == "__main__":
	jerrl = Jerrl()
	i = 0
	no_answer = 0
	ds = LC_Qaud_Linked(path="./data/LC-QUAD/linked_answer3.json")
	tmp = []
	for qapair in prepare_dataset(ds).qapairs:
		i += 1
		if i == 1:
			continue
		results = jerrl.do(qapair)
		# if len(results) != 2:
		# 	continue
		if qapair.answers is None or len(qapair.answers) == 0:
			no_answer += 1
		else:
			qg(qapair)
			# print qapair.answers
			print "--"

		# print "--"
		

		if i > 10:
			break
	print no_answer, i
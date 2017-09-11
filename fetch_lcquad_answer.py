import requests, json, re, operator
from parser.lc_quad_linked import LC_Qaud_Linked


def prepare_dataset(ds):
	ds.load()
	ds.parse()
	return ds

def ask_query(uri):
	if uri == "<https://www.w3.org/1999/02/22-rdf-syntax-ns#type>":
		return 200, json.loads("{\"boolean\": \"True\"}")
	uri = uri.replace("https://","http://")
	return query(u'ASK WHERE {{ {} ?u ?x }}'.format(uri))

def query(q):
	q = q.replace("https://","http://")
	payload = (
		# ('default-graph-uri', 'http://kb.org'),
		('query', q),
		('format', 'application/json'))

	print q
	r = requests.get('http://drogon:7890/sparql', params=payload)
	return r.status_code, r.json()


def has_answer(t):
	if "results" in t and len(t["results"]["bindings"]) > 0:
		return True
	if "boolean" in t:
		return True
	return False


if __name__ == "__main__":
	# print query("SELECT DISTINCT ?uri WHERE {?uri <http://dbpedia.org/ontology/developer> <http://dbpedia.org/resource/J._Michael_Straczynski> . ?uri <http://dbpedia.org/property/network> <http://dbpedia.org/resource/TNT_(TV_channel)>  . ?uri <https://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://dbpedia.org/ontology/TelevisionShow>}".replace("/property", "/ontology"))
	i=0
	ds = LC_Qaud_Linked(path="./data/LC-QUAD/linked.json")
	tmp = []
	no_answer = 0
	no_entity = 0
	for qapair in prepare_dataset(ds).qapairs:
		try:
			r = query(qapair.sparql.query)
			qapair.raw_row["answers"] = r[1]
		except Exception as e:
			qapair.raw_row["answers"] = []
			print e
			print
		if not has_answer(qapair.raw_row["answers"]):
		# 	print qapair.question
		# 	print qapair.raw_row["answers"]
		# 	print qapair.sparql.query
		# 	print
			i+=1
			# try:
			# 	r = query(qapair.sparql.query.replace("/property", "/ontology"))
			# 	qapair.raw_row["answers"] = r[1]
			# 	if has_answer(r[1]):
			# 		print r[1]
			# 		print qapair.raw_row["answers"]
			# 		print qapair.sparql.query
			# 		print 
			# except Exception as e:
			# 	qapair.raw_row["answers"] = []
			# 	print e
			# 	print

		
		# for uri in qapair.sparql.uris:
		# 	if not ask_query(uri.uri)[1]["boolean"]:
		# 		no_entity += 1
		
		
		# if i > 10:
		# 	break
		print i
		tmp.append(qapair.raw_row)
	print i

	with open('data/LC-QUAD/linked_answer4.json', 'w') as jsonFile:
		json.dump(tmp, jsonFile)

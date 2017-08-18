import json, re, operator
from parser.lc_quad import LC_Qaud
from parser.qald import Qald
from parser.webqsp import WebQSP


def prepare_dataset(ds):
	ds.load()
	ds.parse()
	return ds


def findnth(haystack, needle, n):
    parts= haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)

def split_triples(triples):
	template = triples
	idx = findnth(template, " ", 2)
	if idx == -1:
		yield triples
	else:
		while idx >= 0:
			yield template[0:idx]
			template = template[idx + 1:]
			idx = findnth(template, " ", 2)
		yield template


# def get_type(uri):
# 	if uri.find("ns:m.") >= 0:
# 		return "?s"
# 	elif uri.find("ns:") >= 0:
# 		return "?p"
# 	# elif uri.find("rdf-syntax-ns#type") >= 0:
# 	# 	return "?t"
# 	else:
# 		# print uri
# 		return "?u"


if __name__ == "__main__":	
	WHERE = "WHERE"
	total = 0
	templates = {}
	# Qald(Qald.qald_6) LC_Qaud WebQSP
	for item in prepare_dataset(Qald(Qald.qald_6)).qapairs:
		if not item.sparql.supported:
			continue

		sparql_query = item.sparql.query
		for uri in item.sparql.uris:
			sparql_query = sparql_query.replace(uri.uri, uri.type)


		# if "?uri" in sparql_query:
		# 	print item.sparql.raw_query
		# 	print item.sparql.query
		# 	print [(u.uri, u.type) for u in item.sparql.uris]


		idx = sparql_query.find(WHERE)

		where_clause = ' '.join(sparql_query[idx +len(WHERE) + 1:].strip("{}. ").replace(".", " ").split())
		templates[where_clause] = 1 + (templates[where_clause] if where_clause in templates else 0)

		total += 1
		# if total > 100:
		# 	break

	# List templates based on number of times they have been used
	sorted_templates = sorted(templates.items(), key=operator.itemgetter(1), reverse=True)
	for template in sorted_templates:
		print "{}: \t{}".format(template[1], template[0])


	triples = {}
	for template in templates:
		for triple in split_triples(template):
			triples[triple] = 1 + (triples[triple] if triple in triples else 0)

	# for triple in triples:
	# 	print triple



# ?x ?p ?s
# ?x ?p ?uri
# ?uri ?p ?s
# ?s ?p ?s
# ?uri ?t ?p
# ?s ?p ?x
# ?uri ?p ?x
# ?s ?p ?uri
# ?x ?t ?p
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


if __name__ == "__main__":	
	WHERE = "WHERE"
	total = 0
	templates = {}
	# Qald(Qald.qald_6) LC_Qaud WebQSP
	for item in prepare_dataset(LC_Qaud()).qapairs:
		if not item.sparql.supported:
			continue

		where_clause = item.sparql.where_clause
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

	for triple in triples:
		print triple



# ?x ?p ?s
# ?x ?p ?uri
# ?uri ?p ?s
# ?s ?p ?s
# ?uri ?t ?p
# ?s ?p ?x
# ?uri ?p ?x
# ?s ?p ?uri
# ?x ?t ?p
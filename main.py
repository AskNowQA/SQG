from parser.qald import Qald
from parser.lc_quad import LC_Qaud
from parser.webqsp import WebQSP



ds = WebQSP()
ds.load()
ds.parse()
# ds.print_pairs()

### Get entity label in freebase
# PREFIX ns: <http://rdf.freebase.com/ns/>
# prefix : <http://rdf.basekb.com/ns/> 

# SELECT DISTINCT  ?label 
# WHERE {
# filter(lang(?label) = 'en').
# ns:m.03rjj rdfs:label ?label
# }


# ds = Qald(Qald.qald_6)
# ds.load()
# ds.parse()
# ds.print_pairs()


# ds = LC_Qaud()
# ds.load()
# ds.parse()
# ds.print_pairs()


for x in ds.qapairs[:10]:
	print x.sparql
	for y in x.sparql.uris:
		print y.type,
	print ""
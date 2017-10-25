from sklearn.model_selection import train_test_split
from parser.webqsp import WebQSP
from parser.lc_quad import LC_Qaud
from lsa.dssm import DSSM
from common.preprocessing.preprocessor import Preprocessor
from common.graph.graph import Graph
from jerrl.jerrl import Jerrl


def qapairs_to_triple(qapairs):
    return [{"id": item.id, "question": item.question.text, "query": item.sparql.raw_query, "uris": item.sparql.uris}
            for item in qapairs]


jerrl = Jerrl()
ds = LC_Qaud()
kb = ds.parser.kb
ds.load()
ds.parse()

# ds_train, ds_test, _, _ = train_test_split(ds.qapairs, [1] * len(ds.qapairs), test_size=0.2)

ds_train = ds.qapairs[:4000]
ds_test = ds.qapairs[4000:]

ds_train = qapairs_to_triple(ds_train)
ds_test = qapairs_to_triple(ds_test)

model = DSSM(max_steps=10)
# questions, queries, ids = Preprocessor.qapair_to_hash(ds_train)
# model.train([questions, queries])

# questions, queries, ids = Preprocessor.qapair_to_hash(ds_test)
# model.test([questions, queries])

new_ds_test = []
for item in ds_test:
    ask_query = "ASK " in item["query"]
    count_query = "COUNT(" in item["query"]
    sort_query = "order by" in item["query"].lower()

    entities, ontologies = [u for u in item["uris"] if u.is_entity()], \
                           [u for u in item["uris"] if u.is_ontology()]

    graph = Graph(kb)
    graph.find_minimal_subgraph(entities, ontologies, ask_query, sort_query)
    where = graph.to_where_statement()
    if len(where) > 1:
        for w in where:
            new_ds_test.append({"id": item["id"], "question": item["question"], "query": " ".join(w[1]),
                                "uris": item["uris"]})

questions, sparqls = Preprocessor.qapair_to_hash(new_ds_test)
model.similarity(questions, sparqls)

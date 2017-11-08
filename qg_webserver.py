#!flask/bin/python
import flask
from kb.dbpedia import DBpedia
from kb.freebase import Freebase
from common.graph.graph import Graph
from common.query.querybuilder import QueryBuilder
from common.container.uri import Uri
from common.container.linkeditem import LinkedItem
from parser.lc_quad import LC_QaudParser
from parser.webqsp import WebQSPParser

app = flask.Flask(__name__)


@app.route('/qg/api/v1.0/query', methods=['POST'])
def generate_query():
    if not flask.request.json:
        flask.abort(400)

    question = flask.request.json['question']
    raw_entities = flask.request.json['entities']
    raw_relations = flask.request.json['relations']
    kb = flask.request.json.get('kb', "dbpedia").lower()

    if kb == "dbpedia":
        kb = DBpedia()
        parser = LC_QaudParser()
    elif kb == "freebase":
        kb = Freebase()
        parser = WebQSPParser()
    else:
        flask.abort(400)

    entities = []
    for item in raw_entities:
        uris = [Uri(uri["uri"], kb.parse_uri, uri["confidence"]) for uri in item["uris"]]
        entities.append(LinkedItem(item["surface"], uris))

    relations = []
    for item in raw_relations:
        uris = [Uri(uri["uri"], kb.parse_uri, uri["confidence"]) for uri in item["uris"]]
        relations.append(LinkedItem(item["surface"], uris))

    ask_query = False
    sort_query = False
    count_query = False

    graph = Graph(kb)
    querybuilder = QueryBuilder()
    graph.find_minimal_subgraph(entities, relations, ask_query, sort_query)
    where = querybuilder.to_where_statement(graph, parser.parse_queryresult, ask_query, count_query, sort_query)

    return flask.jsonify(
        {'queries': [kb.sparql_query(item["where"], "?u_" + str(item["suggested_id"])) for item in where]}), 201


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)

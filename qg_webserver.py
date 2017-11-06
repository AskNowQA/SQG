#!flask/bin/python
import flask
from common.graph.graph import Graph
from kb.dbpedia import DBpedia
from kb.freebase import Freebase
from common.container.uri import Uri

app = flask.Flask(__name__)


@app.route('/qg/api/v1.0/query', methods=['POST'])
def generate_query():
    if not flask.request.json:
        flask.abort(400)

    question = flask.request.json['question']
    entities = flask.request.json['entities']
    relations = flask.request.json['relations']
    kb = flask.request.json.get('kb', "dbpedia").lower()

    if kb == "dbpedia":
        kb = DBpedia()
    elif kb == "freebase":
        kb = Freebase()
    else:
        flask.abort(400)

    entities = [Uri(item, kb.parse_uri) for item in entities]
    relations = [Uri(item, kb.parse_uri) for item in relations]

    ask_query = False
    sort_query = False

    graph = Graph(kb)
    graph.find_minimal_subgraph(entities, relations, ask_query, sort_query)
    where = graph.to_where_statement()

    return flask.jsonify({'queries': [kb.sparql_query(item[1], "?u_" + str(item[0])) for item in where]}), 201


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)

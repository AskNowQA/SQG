#!flask/bin/python
import flask
import argparse
from orchestrator import Orchestrator
from common.container.uri import Uri
from common.container.linkeditem import LinkedItem
from parser.lc_quad import LC_QaudParser
from parser.webqsp import WebQSPParser
from learning.classifier.svmclassifier import SVMClassifier
from learning.classifier.naivebayesclassifier import NaiveBayesClassifier
import logging
import common.utility.utility as utility
import sys

app = flask.Flask(__name__)
queryBuilder = None
kb = None
classifier = None


@app.route('/qg/api/v1.0/query', methods=['POST'])
def generate_query():
    if not flask.request.json:
        flask.abort(400)

    question = flask.request.json['question']
    raw_entities = flask.request.json['entities']
    raw_relations = flask.request.json['relations']

    entities = []
    for item in raw_entities:
        uris = [Uri(uri["uri"], kb.parse_uri, uri["confidence"]) for uri in item["uris"]]
        entities.append(LinkedItem(item["surface"], uris))

    relations = []
    for item in raw_relations:
        uris = [Uri(uri["uri"], kb.parse_uri, uri["confidence"]) for uri in item["uris"]]
        relations.append(LinkedItem(item["surface"], uris))

    where = queryBuilder.generate_query(question, entities, relations)
    return flask.jsonify(
        {'queries': [kb.sparql_query(item["where"], "?u_" + str(item["suggested_id"])) for item in where]}), 201


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    utility.setup_logging()

    parser = argparse.ArgumentParser(description='Generate SPARQL query')
    parser.add_argument("--kb", help="'dbpedia' (default) or 'freebase'", default="dbpedia", dest="kb")
    parser.add_argument("--classifier", help="'svm' (default) or 'naivebayes'", default="svm", dest="classifier")
    args = parser.parse_args()

    if args.kb == "dbpedia":
        parser = LC_QaudParser()
    elif args.kb == "freebase":
        parser = WebQSPParser()

    kb = parser.kb

    if not kb.server_available:
        logger.error("Server is not available. Please check the endpoint at: {}".format(kb.endpoint))
        sys.exit(0)

    if args.classifier == "svm":
        classifier = SVMClassifier()
    elif args.classifier == "naivebayes":
        classifier = NaiveBayesClassifier()

    queryBuilder = Orchestrator(classifier, parser)
    app.run(debug=True)

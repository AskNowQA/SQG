#!flask/bin/python
import flask
from gevent.wsgi import WSGIServer
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
import os

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
    h1_threshold = int(flask.request.json['h1_threshold']) if 'h1_threshold' in flask.request.json else 9999999

    entities = []
    for item in raw_entities:
        uris = [Uri(uri["uri"], kb.parse_uri, uri["confidence"]) for uri in item["uris"]]
        entities.append(LinkedItem(item["surface"], uris))

    relations = []
    for item in raw_relations:
        uris = [Uri(uri["uri"], kb.parse_uri, uri["confidence"]) for uri in item["uris"]]
        relations.append(LinkedItem(item["surface"], uris))

    ask_query = False
    count_query = False
    where, question_type = queryBuilder.generate_query(question, entities, relations, h1_threshold)
    question_type_str = "list"
    if question_type == 2:
        count_query = True
        question_type_str = "count"
    elif question_type == 1:
        ask_query = True
        question_type_str = "boolean"
    return flask.jsonify(
        {'queries': [kb.sparql_query(item["where"], "?u_" + str(item["suggested_id"]), count_query, ask_query) for item in where],
         'type': question_type_str}), 201


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Command Not found'}), 404)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    utility.setup_logging()

    parser = argparse.ArgumentParser(description='Generate SPARQL query')
    parser.add_argument("--port", help="port", default=5000, type=int, dest="port")
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

    base_dir = "./output"
    classifier_dir = os.path.join(base_dir, "classifier")
    utility.makedirs(classifier_dir)
    if args.classifier == "svm":
        model_dir = os.path.join(classifier_dir, "svm.model")
        classifier = SVMClassifier(model_dir)
    elif args.classifier == "naivebayes":
        model_dir = os.path.join(classifier_dir, "naivebayes.model")
        classifier = NaiveBayesClassifier(model_dir)

    queryBuilder = Orchestrator(classifier, None, parser)
    logger.info("Starting the HTTP server")
    http_server = WSGIServer(('', args.port), app)
    http_server.serve_forever()

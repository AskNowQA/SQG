import urllib
from multiprocessing import Pool
from contextlib import closing
import json
import requests


def query(args):
    endpoint, q, idx = args
    payload = {'query': q, 'format': 'application/json'}
    try:
        query_string = urllib.parse.urlencode(payload)
        url = endpoint + '?' + query_string
        r = requests.get(url)
    except:
        return 0, None, idx
    return r.status_code, r.json() if r.status_code == 200 else None, idx


class KB(object):
    def __init__(self, endpoint, default_graph_uri=""):
        self.endpoint = endpoint
        self.default_graph_uri = default_graph_uri
        self.type_uri = "type_uri"
        self.server_available = self.check_server()

    def check_server(self):
        payload = {'query': 'select distinct ?Concept where {[] a ?Concept} LIMIT 1', 'format': 'application/json'}
        try:
            query_string = urllib.parse.urlencode(payload)
            url = self.endpoint + '?' + query_string
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except:
            return False
        return False

    def query(self, q):
        payload = {'query': q, 'format': 'application/json'}
        try:
            r = requests.post(self.endpoint, payload)
        except:
            return 0, None

        return r.status_code, r.json() if r.status_code == 200 else None

    def sparql_query(self, clauses, return_vars="*", count=False, ask=False):
        if isinstance(clauses, list):
            clauses = " .".join(clauses)
        where = u"WHERE {{ {} }}".format(clauses)
        if count:
            query = u"{} SELECT COUNT(DISTINCT {}) {}".format(self.query_prefix(), return_vars, where)
        elif ask:
            query = u"{} ASK {}".format(self.query_prefix(), where)
        else:
            query = u"{} SELECT DISTINCT {} {}".format(self.query_prefix(), return_vars, where)

        return query

    def query_where(self, clauses, return_vars="*", count=False, ask=False):
        query = self.sparql_query(clauses, return_vars, count, ask)
        status, response = self.query(query)
        if status == 200:
            return response

    def parallel_query(self, query_templates):
        results = []
        if len(query_templates) > 0:
            # query_templates = [[id, template.replace('<http://dbpedia.org/ontology/', 'dbo:').replace(
            #     '<http://dbpedia.org/property/', 'dbp:').replace('<http://dbpedia.org/resource/', 'dbr:').replace('>',
            #                                                                                                       '')]
            #                    for id, template in query_templates]
            #             query = '''PREFIX dbr: <http://dbpedia.org/resource/>
            # PREFIX dbp: <http://dbpedia.org/property/>
            # PREFIX dbo: <http://dbpedia.org/ontology/>'''
            query = ''
            query += 'SELECT DISTINCT ?type WHERE {{ {} }}'.format(
                '\n'.join([
                    '{{SELECT ?type WHERE {{ {1} . BIND ("{0}" as ?type)}} LIMIT 1}} UNION'.format(
                        id, template) for id, template in query_templates])[:-5])
            output = self.query(query)
            if output[0] != 200:
                print(output[1])
            output = [int(item['type']['value']) for item in output[1]['results']['bindings']]
            results = [(item[0], item[0] in output) for item in query_templates]
        return results

        # args = []
        # for i in range(len(query_templates)):
        #     args.append(
        #         (self.endpoint, u"{} ASK WHERE {{ {} }}".format(self.query_prefix(), query_templates[i][1]),
        #          query_templates[i][0]))
        # with closing(Pool(len(query_templates))) as pool:
        #     query_results = pool.map(query, args)
        #     pool.terminate()
        #     results = []
        #     for i in range(len(query_results)):
        #         if query_results[i][0] == 200:
        #             results.append((query_results[i][2], query_results[i][1]["boolean"]))
        #     return results

    def one_hop_graph(self, entity1_uri, relation_uri, entity2_uri=None):
        relation_uri = self.uri_to_sparql(relation_uri)
        entity1_uri = self.uri_to_sparql(entity1_uri)
        if entity2_uri is None:
            entity2_uri = "?u1"
        else:
            entity2_uri = self.uri_to_sparql(entity2_uri)

        query_types = [u"{ent2} {rel} {ent1}",
                       u"{ent1} {rel} {ent2}",
                       u"?u1 {type} {rel}"]
        where = ""
        for i in range(len(query_types)):
            where = where + u"UNION {{ values ?m {{ {} }} {{select <1> where {{ {} }} }} }}\n". \
                format(i,
                       query_types[
                           i].format(
                           rel=relation_uri,
                           ent1=entity1_uri,
                           ent2=entity2_uri,
                           type=self.type_uri,
                           prefix=self.query_prefix()))
        where = where[6:]
        query = u"""{prefix}
SELECT DISTINCT ?m WHERE {{ {where} }}""".format(prefix=self.query_prefix(), where=where)

        status, response = self.query(query)
        if status == 200 and len(response["results"]["bindings"]) > 0:
            output = response["results"]["bindings"]
            return output

    def two_hop_graph(self, entity1_uri, relation1_uri, entity2_uri, relation2_uri):
        relation1_uri = self.uri_to_sparql(relation1_uri)
        relation2_uri = self.uri_to_sparql(relation2_uri)
        entity1_uri = self.uri_to_sparql(entity1_uri)
        entity2_uri = self.uri_to_sparql(entity2_uri)

        queries = self.two_hop_graph_template(entity1_uri, relation1_uri, entity2_uri, relation2_uri)
        output = None
        if len(queries) > 0:
            output = self.parallel_query(queries)
        return output

    def two_hop_graph_template(self, entity1_uri, relation1_uri, entity2_uri, relation2_uri):
        query_types = [[0, u"{ent1} {rel1} {ent2} . ?u1 {rel2} {ent1}"],
                       [1, u"{ent1} {rel1} {ent2} . {ent1} {rel2} ?u1"],
                       [2, u"{ent1} {rel1} {ent2} . {ent2} {rel2} ?u1"],
                       [3, u"{ent1} {rel1} {ent2} . ?u1 {rel2} {ent2}"],
                       [4, u"{ent1} {rel1} {ent2} . ?u1 {type} {rel2}"]]
        output = [[item[0], item[1].format(rel1=relation1_uri, ent1=entity1_uri,
                                           ent2=entity2_uri, rel2=relation2_uri,
                                           type=self.type_uri)] for item in query_types]
        return output

    @staticmethod
    def shorten_prefix():
        return ""

    @staticmethod
    def query_prefix():
        return ""

    @staticmethod
    def prefix():
        return ""

    @staticmethod
    def parse_uri(input_uri):
        pass

    @staticmethod
    def uri_to_sparql(input_uri):
        return input_uri.uri

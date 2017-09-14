import requests


class KB(object):
    def __init__(self, endpoint, default_graph_uri=""):
        self.endpoint = endpoint
        self.default_graph_uri = default_graph_uri
        self.type_uri = "type_uri"

    def query(self, q):
        payload = (
            # ('default-graph-uri', self.default_graph_uri),
            ('query', q),
            ('format', 'application/json'))

        r = requests.get(self.endpoint, params=payload)
        return r.status_code, r.json() if r.status_code == 200 else None

    def query_where(self, clauses, count=False):
        where = u"WHERE {{ {} }}".format(" .".join(clauses))
        if count:
            query = u"{} SELECT COUNT(DISTINCT *) {}".format(self.query_prefix(), where)
        else:
            query = u"{} SELECT DISTINCT * {}".format(self.query_prefix(), where)
        status, response = self.query(query)
        if status == 200 and len(response["results"]["bindings"]) > 0:
            return response

    def one_hop_graph(self, entity_uri, relation_uri):
        query = u"""{3} 
SELECT DISTINCT ?m, count(?u1) WHERE {{
{{ values ?m {{ 0 }} ?u1 {0} {1} }}
UNION {{ values ?m {{ 1 }} {1} {0} ?u1 }}
UNION {{ values ?m {{ 2 }} {1} ?u1 {0} }}
UNION {{ values ?m {{ 3 }} {0} ?u1 {1} }}
UNION {{ values ?m {{ 4 }} ?u1 {2} {0} }}
}}""".format(self.uri_to_sparql(relation_uri), self.uri_to_sparql(entity_uri), self.type_uri, self.query_prefix())
        status, response = self.query(query)
        if status == 200 and len(response["results"]["bindings"]) > 0:
            return response["results"]["bindings"]

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

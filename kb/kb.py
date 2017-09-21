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

        r = requests.get(self.endpoint, params=payload, timeout=60)
        return r.status_code, r.json() if r.status_code == 200 else None

    def query_where(self, clauses, return_vars="*", count=False, ask=False):
        where = u"WHERE {{ {} }}".format(" .".join(clauses))
        if count:
            query = u"{} SELECT COUNT(DISTINCT {}) {}".format(self.query_prefix(), return_vars, where)
        elif ask:
            query = u"{} ASK {}".format(self.query_prefix(), where)
        else:
            query = u"{} SELECT DISTINCT {} {}".format(self.query_prefix(), return_vars, where)
        status, response = self.query(query)
        if status == 200:  # and len(response["results"]["bindings"]) > 0:
            return response

    def one_hop_graph(self, entity1_uri, relation_uri, entity2_uri=None):
        relation_uri = self.uri_to_sparql(relation_uri)
        entity1_uri = self.uri_to_sparql(entity1_uri)
        if entity2_uri is None:
            entity2_uri = "?u1"
        else:
            entity2_uri = self.uri_to_sparql(entity2_uri)
        query = u"""{prefix}
SELECT DISTINCT ?m, count(?u1) WHERE {{
{{ values ?m {{ 0 }} {ent2} {rel} {ent1} }}
UNION {{ values ?m {{ 1 }} {ent1} {rel} {ent2} }}
UNION {{ values ?m {{ 2 }} {ent1} {ent2} {rel} }}
UNION {{ values ?m {{ 3 }} {rel} {ent2} {ent1} }}
UNION {{ values ?m {{ 4 }} ?u1 {type} {rel} }}
}}""".format(rel=relation_uri, ent1=entity1_uri, ent2=entity2_uri, type=self.type_uri, prefix=self.query_prefix())
        status, response = self.query(query)
        if status == 200 and len(response["results"]["bindings"]) > 0:
            return response["results"]["bindings"]

    def two_hop_graph(self, entity1_uri, relation1_uri, entity2_uri, relation2_uri):
        relation1_uri = self.uri_to_sparql(relation1_uri)
        relation2_uri = self.uri_to_sparql(relation2_uri)
        # if entity1_uri.is_generic():
        entity1_uri = self.uri_to_sparql(entity1_uri)
        # if entity2_uri.is_generic():
        entity2_uri = self.uri_to_sparql(entity2_uri)

        query = u"""{prefix}
SELECT DISTINCT ?m, count(?u1) WHERE {{
{{ values ?m {{ 0 }} {ent1} {rel1} {ent2} . ?u1 {rel2} {ent1} }}
UNION {{ values ?m {{ 1 }} {ent1} {rel1} {ent2} . {ent1} {rel2} ?u1 }}
UNION {{ values ?m {{ 2 }} {ent1} {rel1} {ent2} . {ent2} {rel2} ?u1 }}
UNION {{ values ?m {{ 3 }} {ent1} {rel1} {ent2} . ?u1 {rel2} {ent2} }}
}}""".format(prefix=self.query_prefix(), rel1=relation1_uri, ent1=entity1_uri, ent2=entity2_uri, rel2=relation2_uri)

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

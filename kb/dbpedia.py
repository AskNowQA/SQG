from kb import KB
from pybloom import BloomFilter, ScalableBloomFilter
import os


class DBpedia(KB):
    # http://kb.org/sparql
    # http://drogon:7890/sparql
    # http://131.220.153.66:7890/sparql
    # 2016-04 http://sda-srv01.iai.uni-bonn.de:8164/sparql
    # 2014 http://sda-srv01.iai.uni-bonn.de:8014/sparql
    # http://dbpedia.org/sparql
    def __init__(self, endpoint="http://sda-srv01.iai.uni-bonn.de:8164/sparql",
                 one_hop_bloom_file="./data/blooms/spo1.bloom", two_hop_bloom_file="./data/blooms/spo2.bloom"):
        super(DBpedia, self).__init__(endpoint)
        self.type_uri = "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>"
        if os.path.exists(one_hop_bloom_file):
            with open(one_hop_bloom_file) as bloom_file:
                self.one_hop_bloom = BloomFilter.fromfile(bloom_file)
        else:
            self.one_hop_bloom = None
        self.two_hop_bloom_file = two_hop_bloom_file

        self.two_hop_bloom = dict()
        for item in [True, False]:
            file_path = two_hop_bloom_file.replace('spo2', 'spo2' + str(item))
            if os.path.exists(file_path):
                with open(file_path) as bloom_file:
                    self.two_hop_bloom[item] = ScalableBloomFilter.fromfile(bloom_file)
            else:
                self.two_hop_bloom[item] = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH)

        self.two_hop_bloom_counter = 0

    def bloom_query(self, filters):
        found = True
        for item in filters:
            bloom_filter = item.replace("<", "").replace(">", "")
            if bloom_filter not in self.one_hop_bloom:
                found = False
        return found

    def one_hop_graph(self, entity1_uri, relation_uri, entity2_uri=None):
        if self.one_hop_bloom is not None:
            relation_uri = self.uri_to_sparql(relation_uri)
            entity1_uri = self.uri_to_sparql(entity1_uri)
            if entity2_uri is None:
                query_types = [[u"{rel}:{ent1}"],
                               [u"{ent1}:{rel}"],
                               [u"{type}:{rel}"]]
            else:
                entity2_uri = self.uri_to_sparql(entity2_uri)
                query_types = [[u"{ent2}:{rel}", u"{rel}:{ent1}"],
                               [u"{ent1}:{rel}", u"{rel}:{ent2}"],
                               [u"{type}:{rel}"]]
            results = []
            for i in range(len(query_types)):
                if self.bloom_query(
                        [item.format(rel=relation_uri, ent1=entity1_uri, ent2=entity2_uri, type=self.type_uri) for item
                         in query_types[i]]):
                    results.append({"m": {"value": i}})
            return results
        else:
            return super(DBpedia, self).one_hop_graph(entity1_uri, relation_uri, entity2_uri)

    def two_hop_graph(self, entity1_uri, relation1_uri, entity2_uri, relation2_uri):
        relation1_uri = self.uri_to_sparql(relation1_uri)
        relation2_uri = self.uri_to_sparql(relation2_uri)
        entity1_uri = self.uri_to_sparql(entity1_uri)
        entity2_uri = self.uri_to_sparql(entity2_uri)

        queries = self.two_hop_graph_template(entity1_uri, relation1_uri, entity2_uri, relation2_uri)
        output = []

        for query in queries:
            for item in [True, False]:
                if query[1] in self.two_hop_bloom[item]:
                    output.append([query[0], item])
                    break

        if len(queries) != len(output):
            output = super(DBpedia, self).parallel_query(queries)

            for idx in range(len(output)):
                self.two_hop_bloom[output[idx][1]].add(queries[idx][1])
                self.two_hop_bloom_counter += 1

            if self.two_hop_bloom_counter > 100:
                self.two_hop_bloom_counter = 0
                for item in [True, False]:
                    file_path = self.two_hop_bloom_file.replace('spo2', 'spo2' + str(item))
                    with open(file_path, 'w') as bloom_file:
                        self.two_hop_bloom[item].tofile(bloom_file)

        return output

    def two_hop_graph_template(self, entity1_uri, relation1_uri, entity2_uri, relation2_uri):
        query_types = [[0, u"{ent1} {rel1} {ent2} . ?u1 {rel2} {ent1}", u"{rel2}:{ent1}"],
                       [1, u"{ent1} {rel1} {ent2} . {ent1} {rel2} ?u1", u"{ent1}:{rel2}"],
                       [2, u"{ent1} {rel1} {ent2} . {ent2} {rel2} ?u1", u"{ent2}:{rel2}"],
                       [3, u"{ent1} {rel1} {ent2} . ?u1 {rel2} {ent2}", u"{rel2}:{ent2}"],
                       [4, u"{ent1} {rel1} {ent2} . ?u1 {type} {rel2}", u"{type}:{rel2}"]]
        for item in query_types:
            item.append(item[2].format(rel1=relation1_uri, ent1=entity1_uri,
                                       ent2=entity2_uri, rel2=relation2_uri,
                                       type=self.type_uri))
        filtered_query_types = []
        if self.one_hop_bloom is not None:
            for item in query_types:
                if ("?" in item[3]) or self.bloom_query([item[3]]):
                    filtered_query_types.append(item)

        output = [[item[0], item[1].format(rel1=relation1_uri, ent1=entity1_uri,
                                           ent2=entity2_uri, rel2=relation2_uri,
                                           type=self.type_uri)] for item in filtered_query_types]
        return output

    @staticmethod
    def parse_uri(input_uri):
        if isinstance(input_uri, bool):
            return "bool", input_uri
        raw_uri = input_uri.strip("<>")
        if raw_uri.find("/resource/") >= 0:
            return "?s", raw_uri
        elif raw_uri.find("/ontology/") >= 0 or raw_uri.find("/property/") >= 0:
            return "?p", raw_uri
        elif raw_uri.find("rdf-syntax-ns#type") >= 0:
            return "?t", raw_uri
        elif raw_uri.startswith("?"):
            return "g", raw_uri
        else:
            return "?u", raw_uri

    @staticmethod
    def uri_to_sparql(input_uri):
        if input_uri.uri_type == "g":
            return input_uri.uri
        return u"<{}>".format(input_uri.uri)

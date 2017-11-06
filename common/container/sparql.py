class SPARQL:
    def __init__(self, raw_query, parser):
        self.raw_query = raw_query
        self.query, self.supported, self.uris = parser(raw_query)
        self.extrat_where_template()

    def extrat_where_template(self):
        WHERE = "WHERE"
        sparql_query = self.query.strip(" {};\t")
        for uri in self.uris:
            sparql_query = sparql_query.replace(uri.uri, uri.uri_type)

        idx = sparql_query.find(WHERE)
        self.where_clause = ' '.join(sparql_query.strip("{}. ").replace(".", " ").split())
        if idx >= 0:
            idx = sparql_query.find("{", idx)
            self.where_clause = ' '.join(
                self.where_clause[idx + 1:].split())

    def query_features(self):
        features = {"boolean": ["ask "],
                    "count": ["count("],
                    "filter": ["filter("],
                    "comparison": ["<= ", ">= ", " < ", " > "],
                    "sort": ["order by"],
                    "aggregate": ["max(", "min("]
                    }

        output = set()
        if self.where_clause.count(" ") > 3:
            output.add("compound")
        else:
            output.add("single")
        generic_uris = set()
        for uri in self.uris:
            if uri.is_generic():
                generic_uris.add(uri)
                if len(generic_uris) > 1:
                    output.add("multivar")
                    break
        if len(generic_uris) <= 1:
            output.add("singlevar")
        raw_query = self.raw_query.lower()
        for feature in features:
            for constraint in features[feature]:
                if constraint in raw_query:
                    output.add(feature)
        return output

    def __str__(self):
        return self.query.encode("ascii", "ignore")

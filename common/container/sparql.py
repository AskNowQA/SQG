class SPARQL:
    def __init__(self, raw_query, parser):
        self.raw_query = raw_query
        self.query, self.supported, self.uris = parser(raw_query)
        self.where_clause, self.where_clause_template = self.__extrat_where()

    def __extrat_where(self):
        WHERE = "WHERE"
        sparql_query = self.query.strip(" {};\t")
        idx = sparql_query.find(WHERE)
        where_clause_raw = sparql_query[idx + len(WHERE):].strip(" {}")
        where_clause_raw = [item.strip(" .") for item in where_clause_raw.split(" ")]
        where_clause_raw = [item for item in where_clause_raw if item != ""]
        buffer = []
        where_clause = []
        for item in where_clause_raw:
            buffer.append(item)
            if len(buffer) == 3:
                where_clause.append(buffer)
                buffer = []
        if len(buffer) > 0:
            where_clause.append(buffer)

        where_clause_template = " ".join([" ".join(item) for item in where_clause])
        for uri in set(self.uris):
            where_clause_template = where_clause_template.replace(uri.uri, uri.uri_type)

        return where_clause, where_clause_template

    def query_features(self):
        features = {"boolean": ["ask "],
                    "count": ["count("],
                    "filter": ["filter("],
                    "comparison": ["<= ", ">= ", " < ", " > "],
                    "sort": ["order by"],
                    "aggregate": ["max(", "min("]
                    }

        output = set()
        if self.where_clause_template.count(" ") > 3:
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

    def __eq__(self, other):
        if isinstance(other, SPARQL):
            mapping = {}
            for line in self.where_clause:
                found = False
                for other_line in other.where_clause:
                    match = 0
                    mapping_buffer = mapping.copy()
                    for i in range(len(line)):
                        if line[i] == other_line[i]:
                            match += 1
                        elif line[i].startswith("?") and other_line[i].startswith("?"):
                            if line[i] not in mapping_buffer:
                                mapping_buffer[line[i]] = other_line[i]
                                match += 1
                            else:
                                match += mapping_buffer[line[i]] == other_line[i]
                    if match == len(line):
                        found = True
                        mapping = mapping_buffer
                        break
                if not found:
                    return False
            return True

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return self.query.encode("ascii", "ignore")

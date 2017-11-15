import json
import itertools
from common.container.linkeditem import LinkedItem
from common.container.uri import Uri
from kb.dbpedia import DBpedia


class Earl:
    def __init__(self, path="data/LC-QUAD/EARL/output.json"):
        self.parser = DBpedia.parse_uri
        with file(path) as data_file:
            self.raw_data = json.load(data_file)
            self.questions = {}
            for item in self.raw_data:
                self.questions[item["question"]] = item

    def do(self, qapair):
        if qapair.question.text in self.questions:
            item = self.questions[qapair.question.text]
            entities = self.__parse(item, "entities", 5)
            relations = self.__parse(item, "relations", 5)

            return entities, relations
        else:
            return [], []

    def __parse(self, dataset, name, top):
        output = []
        for item in dataset[name]:
            uris = []
            for uri in item["uris"]:
                uris.append(Uri(uri["uri"], self.parser, uri["confidence"]))
            start_index, length = item["surface"]
            surface = dataset["question"][start_index: start_index + length]
            output.append(LinkedItem(surface, uris[:top]))
        return output

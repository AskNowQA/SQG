import ujson as json
from linker.goldLinker import GoldLinker
from common.container.linkeditem import LinkedItem
from common.container.uri import Uri
from kb.dbpedia import DBpedia
from common.utility.utility import closest_string


class Earl:
    def __init__(self, path="data/LC-QUAD/EARL/output_original.json"):
        self.parser = DBpedia.parse_uri
        self.gold_linker = GoldLinker()
        with open(path, 'r') as data_file:
            self.raw_data = json.load(data_file)
            self.questions = {}
            for item in self.raw_data:
                self.questions[item["question"]] = item

    def __force_gold(self, golden_list, surfaces, items):
        not_found = []
        for item in golden_list:
            idx = closest_string(item.surface_form, surfaces)
            if idx != -1:
                if item.uris[0] not in items[idx].uris:
                    items[idx].uris[len(items[idx].uris) - 1] = item.uris[0]
                surfaces.pop(idx)
            else:
                not_found.append(item)

        for item in not_found:
            if len(surfaces) > 0:
                idx = surfaces.keys()[0]
                items[idx].uris[0] = item.uris[0]
                surfaces.pop(idx)
            else:
                items.append(item)

        keys = surfaces.keys()
        keys.sort(reverse=True)
        for idx in keys:
            del items[idx]

        return items

    def do(self, qapair, force_gold=False, top=5):
        if qapair.question.text in self.questions:
            item = self.questions[qapair.question.text]
            entities = self.__parse(item, "entities", top)
            relations = self.__parse(item, "relations", top)

            if force_gold:
                gold_entities, gold_relations = self.gold_linker.do(qapair)
                entities_surface = {i: item.surface_form for i, item in enumerate(entities)}
                relations_surface = {i: item.surface_form for i, item in enumerate(relations)}

                entities = self.__force_gold(gold_entities, entities_surface, entities)
                relations = self.__force_gold(gold_relations, relations_surface, relations)

            return entities, relations
        else:
            return None, None

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

from common.container.linkeditem import LinkedItem
from common.utility.utility import find_mentions


class GoldLinker:
    def __init__(self):
        pass

    def do(self, qapair, force_gold=False, top=5):
        entities = []
        relations = []
        for u in qapair.sparql.uris:
            question = qapair.question.text
            mentions = find_mentions(question, [u])
            surface = ""
            if len(mentions) > 0:
                surface = question[mentions[0]["start"]:mentions[0]["end"]]

            linked_item = LinkedItem(surface, [u])
            if u.is_entity():
                entities.append(linked_item)
            if u.is_ontology():
                relations.append(linked_item)

        return entities, relations

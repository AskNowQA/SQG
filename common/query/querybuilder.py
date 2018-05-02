from common.container.answerset import AnswerSet
from common.container.linkeditem import LinkedItem
from common.graph.path import Path
from common.graph.paths import Paths
from common.utility.mylist import MyList


class QueryBuilder:
    def to_where_statement(self, graph, parse_queryresult, ask_query, count_query, sort_query):
        graph.generalize_nodes()
        graph.merge_edges()
        output = []
        paths = self.__find_paths(graph, graph.entity_items, graph.relation_items, graph.edges)

        # Expand coverage by changing generic ids
        new_paths = []
        for path in paths:
            to_be_updated_edges = []
            generic_nodes = set()
            for edge in path:
                if edge.source_node.are_all_uris_generic():
                    generic_nodes.add(edge.source_node)
                if edge.dest_node.are_all_uris_generic():
                    generic_nodes.add(edge.dest_node)

                if edge.source_node.are_all_uris_generic() and not edge.dest_node.are_all_uris_generic():
                    to_be_updated_edges.append(
                        {"type": "source", "node": edge.source_node, "edge": edge})
                if edge.dest_node.are_all_uris_generic() and not edge.source_node.are_all_uris_generic():
                    to_be_updated_edges.append(
                        {"type": "dest", "node": edge.dest_node, "edge": edge})

            for new_node in generic_nodes:
                for edge_info in to_be_updated_edges:
                    if edge_info["node"] != new_node:
                        new_path = None
                        if edge_info["type"] == "source":
                            new_path = path.replace_edge(edge_info["edge"],
                                                         edge_info["edge"].copy(source_node=new_node))
                        if edge_info["type"] == "dest":
                            new_path = path.replace_edge(edge_info["edge"], edge_info["edge"].copy(dest_node=new_node))
                        if new_path is not None and new_path not in new_paths:
                            new_paths.append(new_path)

        for new_path in new_paths:
            generic_equal = False
            if new_path not in paths:
                for path in paths:
                    if path.generic_equal_with_substitutable_id(new_path):
                        generic_equal = True
                        break
                if not generic_equal:
                    paths.append(new_path)

        paths.sort(key=lambda x: x.confidence, reverse=True)
        output = paths.to_where(graph.kb, ask_query)

        # Remove queries with no answer
        filtered_output = []
        for item in output:
            target_var = "?u_" + str(item["suggested_id"])
            raw_answer = graph.kb.query_where(item["where"], return_vars=target_var,
                                              count=count_query,
                                              ask=ask_query)
            answerset = AnswerSet(raw_answer, parse_queryresult)

            # Do not include the query if it does not return any answer, except for boolean query
            if len(answerset.answer_rows) > 0 or ask_query:
                item["target_var"] = target_var
                item["answer"] = answerset
                filtered_output.append(item)

        # filtered_output_with_no_duplicate_answer = []
        # for n, ii in enumerate(filtered_output):
        #     duplicate_answer = False
        #     for item in filtered_output[n + 1:]:
        #         if item["answer"] == ii["answer"]:
        #             duplicate_answer = True
        #     if not duplicate_answer:
        #         filtered_output_with_no_duplicate_answer.append(ii)

        # return filtered_output_with_no_duplicate_answer

        return filtered_output

    def __find_paths(self, graph, entity_items, relation_items, edges, output_paths=Paths()):
        new_output_paths = Paths([])

        if len(relation_items) == 0:
            if len(entity_items) > 0:
                return Paths()
            return output_paths

        used_relations = []
        for relation_item in relation_items:
            for relation in relation_item.uris:
                used_relations = used_relations + [relation]
                for edge in self.__find_edges(edges, relation):
                    entities = MyList()
                    if not (edge.source_node.are_all_uris_generic() or edge.uri.is_type()):
                        entities.extend(edge.source_node.uris)
                    if not (edge.dest_node.are_all_uris_generic() or edge.uri.is_type()):
                        entities.extend(edge.dest_node.uris)

                    new_paths = self.__find_paths(graph,
                                                  entity_items - LinkedItem.list_contains_uris(entity_items, entities),
                                                  relation_items - LinkedItem.list_contains_uris(relation_items,
                                                                                                 used_relations),
                                                  edges - {edge},
                                                  output_paths=output_paths.extend(edge))
                    new_output_paths.add(new_paths, lambda path: len(path) >= len(graph.relation_items))

        return new_output_paths

    def __find_edges(self, edges, uri):
        return [edge for edge in edges if edge.uri == uri or (edge.uri.is_type() and edge.dest_node.has_uri(uri))]

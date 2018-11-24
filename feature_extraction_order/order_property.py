import re


# Takes a SPARQL query and returns the order property in the query, if it exists
def get_order_property(query):
    try:
        triples = re.findall(r"{.*}", query)[0].replace("{", "").replace("}", "")
        order_property_literal = re.findall(r"\(\?\w+\)", query)[0].replace("(", "").replace(")", "")
        triples = triples.split(".")
        order_triple = " ".join([i for i in triples if order_property_literal in i])
        order_property = re.findall(r"\w+:\w+", order_triple)[0]
    except:
        order_property = None

    return order_property.replace("dbo:", "")

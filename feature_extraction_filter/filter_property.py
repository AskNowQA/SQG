from helper import *
from filter_helper import *
from prepare_train_test_classifier import filter_query_type


def get_filter_properties(sparql):
    type_ = filter_query_type(sparql)
    # print sparql
    # print "SPARQL Type", type_
    if type_ != -1:
        # Get filter( ) comparator
        filter_condition = re.findall(r"filter.*\(.*\)", sparql, flags=re.IGNORECASE)[0]
        # print "Filter( )", filter_condition

        filter_variables = list(set(re.findall(r"\?\w+", filter_condition, flags=re.IGNORECASE)))
        # print "Filter variables ", filter_variables

        lines = list(set(re.findall(r"<\S+>\s*\?\w+", sparql, flags=re.IGNORECASE)))
        lines = [{line.split(" ")[1]: line.split(" ")[0]} for line in lines]
        properties = [line for line in lines if line.keys()[0] in filter_variables]

        # properties = list(set(properties))
        # print properties
        # print lines

        # Type 0: Bound type, no comparator
        if type_ == 0:
            return {"properties": properties, "comparator": "bound", "value": None, "type": 0}
            # Type 1: One resource One value
        elif type_ == 1:
            comparator = get_filter_comparator(filter_condition)
            value = re.findall(r"\d+", filter_condition)
            return {"properties": properties, "comparator": comparator, "value": value, "type": 1}
            # Type 2: Two or resources
        else:
            comparator = get_filter_comparator(filter_condition)
            return {"properties": properties, "comparator": comparator, "value": None, "type": 2}

    return None


def get_filter_comparator(filter_condition):
    filter_condition = re.sub(r"<\S+>", "", filter_condition)
    filter_condition = re.findall(r">=|<=|>|<|=|!=", filter_condition, flags=re.IGNORECASE)
    return filter_condition


def main():
    print "MAIN"
    # data = load_json(filter_qald_path)
    data = load_json(filter_path)
    for row in data:
        question = row["question"]
        sparql = row["query"]
        print question
        print sparql
        print get_filter_properties(sparql)
        break

        print "\n ## \n"

        # break


if __name__ == '__main__':
    main()
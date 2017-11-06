from parser.webqsp import WebQSP
from common.utility.stats import Stats


def prepare_dataset(ds):
    ds.load()
    ds.parse()
    return ds


if __name__ == "__main__":

    stat = Stats()
    # Qald(Qald.qald_6) LC_Qaud WebQSP
    for item in prepare_dataset(WebQSP()).qapairs:
        if "order by" in item.sparql.raw_query.lower():
            stat.inc("total")
            question = item.question.text.lower()
            if " first" in question:
                stat.inc("first")
            elif " last " in question:
                stat.inc("last")
            elif "tallest" in question:
                stat.inc("tallest")
            elif " second " in question:
                stat.inc("second")
            elif "biggest" in question:
                stat.inc("biggest")
            elif " new " in question:
                stat.inc("new")
            elif " most " in question:
                stat.inc("most")
            else:
                print item.question
                print item.sparql.raw_query
                print "-" * 10

    print stat
# biggest:4 first:29 last:20 most:5 new:2 second:1 tallest:1 total:109
# biggest:4 first:62 most:11 new:46 second:2 tallest:1 total:3098
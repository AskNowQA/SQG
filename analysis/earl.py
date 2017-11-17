from parser.lc_quad_linked import LC_Qaud_Linked
from linker.earl import Earl
from linker.jerrl import Jerrl
from common.utility.stats import Stats
from tqdm import tqdm


def do(list1, list2):
    miss_match = False
    for item in list1:
        target_uri = item.uris[0]
        found = False
        for e2_item in list2:
            if target_uri in e2_item.uris:
                found = True
                break
        if not found:
            miss_match = True
            break
    return miss_match


if __name__ == "__main__":

    stats = Stats()

    ds = LC_Qaud_Linked("../data/LC-QUAD/linked.json")
    ds.load()
    ds.parse()

    jerrl = Jerrl()
    earl = Earl("../data/LC-QUAD/EARL/output.json")

    for qapair in tqdm(ds.qapairs):
        e1, r1 = jerrl.do(qapair)
        e2, r2 = earl.do(qapair, force_gold=False, top=100)
        if len(e2) == 0:
            stats.inc("earl_no_entity")
        if len(r2) == 0:
            stats.inc("earl_no_relation")

        if len(e2) == 0 and len(r2) == 0:
            stats.inc("earl_no")

        if len(e1) == len(e2):
            stats.inc("len_entity")

        if len(r1) == len(r2):
            stats.inc("len_relation")

        if len(e1) == len(e2) and len(r1) == len(r2):
            stats.inc("len_both")

        e = do(e1, e2)
        r = do(r1, r2)
        if not e:
            stats.inc("matched_entity")
        if not r:
            stats.inc("matched_relation")
        if not e and not r:
            stats.inc("matched_both")

        stats.inc("total")

    print stats

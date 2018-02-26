"""
Preprocessing script for LC-Quad data.

"""

import os
import glob
import json
import anytree
from tqdm import tqdm
from common.utility.utility import find_mentions
from parser.lc_quad_linked import LC_Qaud_LinkedParser


def make_dirs(dirs):
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)


def build_vocab(filepaths, dst_path, lowercase=True):
    vocab = set()
    for filepath in filepaths:
        with open(filepath) as f:
            for line in f:
                if lowercase:
                    line = line.lower()
                vocab |= set(line.split())
    with open(dst_path, 'w') as f:
        for w in sorted(vocab):
            f.write(w + '\n')


def generalize_question(a, b):
    # replace entity mention in question with a generic symbol
    parser = LC_Qaud_LinkedParser()

    _, _, uris = parser.parse_sparql(b)
    uris = [uri for uri in uris if uri.is_entity()]

    i = 0
    for item in find_mentions(a, uris):
        a = "{} #en{} {}".format(a[:item["start"]], "t" * (i + 1), a[item["end"]:])
        b = b.replace(item["uri"].raw_uri, "#en{}".format("t" * (i + 1)))

    # remove extra info from the relation's uri and remaining entities
    for item in ["http://dbpedia.org/resource/", "http://dbpedia.org/ontology/",
                 "http://dbpedia.org/property/", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"]:
        b = b.replace(item, "")
    b = b.replace("<", "").replace(">", "")

    return a, b


def split(filepath, dst_dir):
    with open(filepath) as datafile, \
            open(os.path.join(dst_dir, 'a.txt'), 'w') as afile, \
            open(os.path.join(dst_dir, 'b.txt'), 'w') as bfile, \
            open(os.path.join(dst_dir, 'id.txt'), 'w') as idfile, \
            open(os.path.join(dst_dir, 'sim.txt'), 'w') as simfile:
        dataset = json.load(datafile)
        for item in tqdm(dataset):
            i = item["id"]
            a = item["question"]
            for query in item["generated_queries"]:
                a, b = generalize_question(a, query["query"])

                # Empty query should be ignored
                if len(b) < 5:
                    continue
                sim = str(1 if query["correct"] else 0)
                idfile.write(i + '\n')
                afile.write(a.encode('ascii', 'ignore') + '\n')
                bfile.write(b.encode('ascii', 'ignore') + '\n')
                simfile.write(sim + '\n')


if __name__ == '__main__':
    print('=' * 80)
    print('Preprocessing LC-Quad dataset')
    print('=' * 80)

    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    lc_quad_dir = os.path.join(data_dir, 'lc_quad_earl_no_force_gold')
    lib_dir = os.path.join(base_dir, 'lib')
    train_dir = os.path.join(lc_quad_dir, 'train')
    dev_dir = os.path.join(lc_quad_dir, 'dev')
    test_dir = os.path.join(lc_quad_dir, 'test')
    make_dirs([train_dir, dev_dir, test_dir])

    # split into separate files
    train_filepath = os.path.join(lc_quad_dir, 'LCQuad_train.json')
    trail_filepath = os.path.join(lc_quad_dir, 'LCQuad_trial.json')
    test_filepath = os.path.join(lc_quad_dir, 'LCQuad_test.json')

    ds = json.load(open("../../../output/lc_quad_earl_no_force_gold.json"))
    total = len(ds)
    train_size = int(.7 * total)
    dev_size = int(.2 * total)
    test_size = int(.1 * total)

    json.dump(ds[:train_size], open(train_filepath, "w"))
    json.dump(ds[train_size:train_size + dev_size], open(trail_filepath, "w"))
    json.dump(ds[train_size + dev_size:], open(test_filepath, "w"))

    print('Split train set')
    split(train_filepath, train_dir)
    print('Split dev set')
    split(trail_filepath, dev_dir)
    print('Split test set')
    split(test_filepath, test_dir)

    # get vocabulary
    build_vocab(
        glob.glob(os.path.join(lc_quad_dir, '*/*.toks')),
        os.path.join(lc_quad_dir, 'vocab.txt'))
    build_vocab(
        glob.glob(os.path.join(lc_quad_dir, '*/*.toks')),
        os.path.join(lc_quad_dir, 'vocab-cased.txt'),
        lowercase=False)

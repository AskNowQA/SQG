import json, os, string
from unidecode import unidecode
from l3wtransformer import L3wTransformer
from collections import Counter
import numpy as np
from tqdm import tqdm


def make_dirs(dirs):
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)


def split(ds, size, dst_dir):
    with open(os.path.join(dst_dir, 'hashed_questions.txt'), 'w') as hashed_file:
        for item in tqdm(ds):
            item_ = [i for i in item if i <= size]
            counter = np.array([[k, v] for k, v in Counter(item_).items()])
            vect = np.zeros(size + 1, dtype=int)
            vect[counter[:, 0]] = counter[:, 1]
            hashed_file.write(" ".join(map(str, vect)) + "\n")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    lc_quad_dir = os.path.join(data_dir, 'lc_quad')
    lib_dir = os.path.join(base_dir, 'lib')
    train_dir = os.path.join(lc_quad_dir, 'train')
    dev_dir = os.path.join(lc_quad_dir, 'dev')
    test_dir = os.path.join(lc_quad_dir, 'test')
    make_dirs([train_dir, dev_dir, test_dir])

    train_filepath = os.path.join(lc_quad_dir, 'LCQuad_train.json')
    trail_filepath = os.path.join(lc_quad_dir, 'LCQuad_trial.json')
    test_filepath = os.path.join(lc_quad_dir, 'LCQuad_test.json')

    ds = json.load(open("../../../output/lc_quad.json"))
    l3wt = L3wTransformer()
    questions = [unidecode(item["question"].lower()).translate(None, string.punctuation) for item in ds]
    l3wt.fit_on_texts(questions)
    hashed_questions = l3wt.texts_to_sequences(questions)
    l3wt.save(os.path.join(lc_quad_dir, 'vocab.pk'))
    vocab_size = len(l3wt.indexed_lookup_table)

    total = len(ds)
    train_size = int(.7 * total)
    dev_size = int(.2 * total)
    test_size = int(.1 * total)

    json.dump(ds[:train_size], open(train_filepath, "w"))
    json.dump(ds[train_size:train_size + dev_size], open(trail_filepath, "w"))
    json.dump(ds[train_size + dev_size:], open(test_filepath, "w"))
    print('Split train set')
    split(hashed_questions[:train_size], vocab_size, train_dir)
    print('Split dev set')
    split(hashed_questions[train_size:train_size + dev_size], vocab_size, dev_dir)
    print('Split test set')
    split(hashed_questions[train_size + dev_size:], vocab_size, test_dir)

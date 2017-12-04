import ujson, os, string, codecs
from unidecode import unidecode
from l3wtransformer import L3wTransformer
from collections import Counter
import numpy as np
from tqdm import tqdm
import pandas as pd
import torch
from dataset import QGDataset


def make_dirs(dirs):
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)


def extract_core_chain(parse, replace_property=True):
    items = parse.split()
    items = items[1:]  # Ignore the first one which is supposed to entity
    ignoring = False
    ignore_next_token = False
    output = []
    for item in items:
        if item == "<<EQUALS>>":
            ignore_next_token = True
            continue
        if ignore_next_token:
            ignore_next_token = False
            continue
        if item == "<<BRANCH>>":
            ignoring = True
        if item == "<<JOIN>>":
            ignoring = False
        if not ignoring and "<<" not in item:
            if replace_property:
                output.append(item.replace("/property/", "/ontology/"))
            else:
                output.append(item)
    return output


def get_core_chain_score(core_chain, target_core_chain):
    return core_chain == target_core_chain


def clean_text(text):
    return unidecode(text.replace("\n", "").lower()).translate(None, string.punctuation)


def minimize_uri_in_chain(core_chain):
    text = " ".join(core_chain)

    text = text.replace("<http://dbpedia.org/ontology/", "o/") \
        .replace("<http://dbpedia.org/resource/", "r/") \
        .replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "/type")
    return clean_text(text)


def combine(lc_quad_dir, file_path):
    dataset = {}
    # Read Questions
    with codecs.open(os.path.join(lc_quad_dir, "lcquad.multilin"), 'r', 'utf-8') as questions_file:
        question_id, question = "", ""
        lines = questions_file.readlines()
        for line in lines:
            if ":" in line:
                idx = line.index(":")
                if ".P" not in line[:idx]:  # Is it a question
                    question_id, question = clean_text(line[:idx]), line[idx + 1:]
                    dataset[question_id] = {"question": question, "parses": []}
                else:  # Otherwise it is a parse
                    dataset[question_id]["parses"].append({"target_parse": line[idx + 1:], "core_chains": []})

    core_chains = ujson.load(open(os.path.join(lc_quad_dir, "lcquad.multilin.chains")))
    not_found = 0
    # Load core-chains
    for id in core_chains.keys():
        question_id, parse_id = id.split(".")
        parse_id = int(parse_id[1:]) - 1
        question_id = unidecode(question_id).lower()
        target_parse = dataset[question_id]["parses"][parse_id]["target_parse"]
        target_core_chain = extract_core_chain(target_parse)
        found = False
        for core_chain in core_chains[id]:
            score = int(get_core_chain_score(core_chain, target_core_chain))
            if score:
                found = True
            dataset[question_id]["parses"][parse_id]["core_chains"].append(
                {"score": score, "chain": minimize_uri_in_chain(core_chain)})
        if not found:
            not_found += 1
            print question_id
    assert not_found == 0

    with open(file_path, 'w') as outfile:
        ujson.dump(dataset, outfile, indent=4)


def count_n_gram_hash(input, l3wt):
    item = l3wt.texts_to_sequences(input.split())
    item = [i[:-1] for i in item]
    words_hashing = []
    for item_ in item:  # Create hashing for each words
        item_ = [i for i in item_ if i < vocab_size]
        if len(item_) > 0:
            counter = Counter(item_)
            counter = np.array([[k, v] for k, v in counter.items()])
            word_hashing = np.zeros((1, 1, vocab_size))
            word_hashing[0, 0, counter[:, 0]] = counter[:, 1]
            words_hashing.append(word_hashing)

    if len(words_hashing) < 3:  # Less than three words
        for i in range(0, 3 - len(words_hashing)):
            words_hashing.append(np.zeros(words_hashing[0].shape))

    three_grams = []
    for triple in zip(words_hashing, words_hashing[1:], words_hashing[2:]):
        three_grams.append(np.concatenate(triple, 2))
    return torch.from_numpy(np.concatenate(three_grams, 1))


def split(df, l3wt, dst_file):
    vocab_size = len(l3wt.indexed_lookup_table)
    dataset = QGDataset(2, vocab_size)
    last_question = ""
    last_question_hashed = ""
    for index, row in tqdm(df.iterrows(), total=len(df)):
        question = clean_text(row["question"])
        if last_question == question:
            hashed_question = last_question_hashed
        else:
            hashed_question = count_n_gram_hash(question, l3wt)

        hashed_query = count_n_gram_hash(row["chain"], l3wt)
        dataset.add(hashed_question, hashed_query, row["score"])
        last_question_hashed = hashed_question
        last_question = question

    torch.save(dataset, dst_file)


if __name__ == "__main__":
    # tmp = " <http://dbpedia.org/resource/West_Germany> :-<http://dbpedia.org/property/recorded> <<EQUALS>> <http://dbpedia.org/resource/Don\\'t_Bring_Me_Down> <<RETURN>>"
    # print extract_core_chain(tmp)
    # q = 1 / 0

    base_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    lc_quad_dir = os.path.join(data_dir, 'lc_quad')
    lc_quad_combined = os.path.join(lc_quad_dir, 'lcquad.multilin.chains.json')
    vocab_filepath = os.path.join(lc_quad_dir, 'vocab.pk')

    train_file = os.path.join(lc_quad_dir, 'dataset_train.pth')
    dev_file = os.path.join(lc_quad_dir, 'dataset_dev.pth')
    test_file = os.path.join(lc_quad_dir, 'dataset_test.pth')

    train_filepath = os.path.join(lc_quad_dir, 'LCQuad_train.json')
    trail_filepath = os.path.join(lc_quad_dir, 'LCQuad_trial.json')
    test_filepath = os.path.join(lc_quad_dir, 'LCQuad_test.json')

    print("Combine questions and core-chains")
    if not os.path.isfile(lc_quad_combined):
        combine(lc_quad_dir, lc_quad_combined)

    ds = ujson.load(open(lc_quad_combined))
    ds = [ds["q{}".format(item + 1)] for item in range(len(ds))]

    print("Load dataframe from combined dataset")
    df = pd.io.json.json_normalize(ds, record_path=['parses', 'core_chains'], meta=["question"])

    l3wt = L3wTransformer()
    if not os.path.isfile(vocab_filepath):
        print("Fit letter 3-gram on questions and chains")
        l3wt.fit_on_texts(list(df["chain"].values) + list(df["question"].values))
        print("Save the vocab file")
        l3wt.save(vocab_filepath)
    else:
        print("load 3-gram model")
        l3wt = L3wTransformer.load(vocab_filepath)
    vocab_size = len(l3wt.indexed_lookup_table)

    total = len(df)
    train_size = int(.7 * total)
    dev_size = int(.2 * total)
    test_size = int(.1 * total)

    ujson.dump(ds[:train_size], open(train_filepath, "w"))
    ujson.dump(ds[train_size:train_size + dev_size], open(trail_filepath, "w"))
    ujson.dump(ds[train_size + dev_size:], open(test_filepath, "w"))
    print('Split train set')
    split(df.loc[:train_size], l3wt, train_file)
    print('Split dev set')
    split(df.loc[train_size:train_size + dev_size], l3wt, dev_file)
    print('Split test set')
    split(df.loc[train_size + dev_size:], l3wt, test_file)

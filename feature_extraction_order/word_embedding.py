from helper import *
from tqdm import tqdm
from scipy import spatial
import operator
from pos import get_feature_precompiled
from pos import get_features_nlp
from order_property import get_order_property
import numpy as np
import gensim
from helper_functions.glove_word2vec_convert import convert
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from prepare_train_test import clean_question

# Sets nltk directory path
nltk.data.path.append("/Users/just3obad/Desktop/Thesis/Libraries/nltk_data")
stop_words = set(stopwords.words('english'))

# Initialize w2v embeddings matrix
print "Loading W2V Matrix"
W2V_PATH = "embeddings_matrix/glove_100d_word2vec_vocab.txt"
W2V_MODEL = gensim.models.KeyedVectors.load_word2vec_format(W2V_PATH, binary=False)
print "Done"


# Get embeddings matrix for all vocab
def __load_embeddings():
    glove_100d_w2v = "embeddings_matrix/glove_100d_word2vec.txt"
    print "Loading W2V Matrix"
    model = gensim.models.KeyedVectors.load_word2vec_format(glove_100d_w2v, binary=False)
    print "Matrix Loaded"
    print "Setting up Vocab list"
    vocab = load_json("data/vocabs.json")
    ordinals = load_json("../data/ComplexQuestionsOrder/ordinals.json")
    additions = ["most", "least", "new", "last", "latest", "top"]

    with open("embeddings_matrix/glove_100d_word2vec_vocab.txt", "wb") as data_file:
        for v in tqdm(vocab, desc="Preparing Vocab Embedding Matrix"):
            # if v in additions or v in ordinals or v not in stop_words:
            # try:
            if v in model:
                tmp = " ".join(str(x) for x in model[v])
                tmp = v + " " + tmp
                tmp += "\n"
                data_file.write(tmp)
            else:
                # tmp = " ".join(str(x) for x in model[v])
                zeroes = ["0"]*100
                tmp = v + " " + " ".join(zeroes)
                tmp += "\n"
                data_file.write(tmp)
            # except:
                # continue

    convert("/Users/just3obad/Desktop/Thesis/AskNow/SQG/feature_extraction_order/"
            "embeddings_matrix/glove_100d_word2vec_vocab.txt", "/Users/just3obad/Desktop/Thesis/AskNow/"
                                                               "SQG/feature_extraction_order/embeddings_matrix/"
                                                               "glove_100d_word2vec_vocab.txt")


# Compiles a list of all possible vocab in the questions
def __set_up_vocab():
    ontologies = load_json("data/clean_ontologies.json")
    ontologies = [o.replace("http://dbpedia.org/ontology/", "") for o in ontologies]

    questions = load_json("data/one_hop_ontologies_clean.json")
    questions = [clean_question(q["question"]) for q in questions]

    questions_words = []
    for q in questions:
        tmp_list = word_tokenize(clean_question(q))
        questions_words += tmp_list

    questions_words = list(set(questions_words))

    properties = ontologies

    words_hash = []

    for p in properties:
        words_hash += __decompose_word(p)

    words_hash = list(set(words_hash))

    vocab_list = words_hash + questions_words

    print "Vocab Size:", len(vocab_list)
    save_json(vocab_list, "data/vocabs.json")
    return vocab_list


# Splits a word on capital characters.
# Used for ontologies to get embeddings
def __decompose_word(word):
    indices = [0]
    for index, char in enumerate(word):
        if char.isupper():
            indices.append(index)

    indices.append(len(word))

    words = []
    for i, j in zip(indices[0:-1], indices[1:]):
        words.append(word[i:j].lower())

    return words


# Takes a list of tokens.
# Returns the embedding vector for the tokens
# The resulting vector could be of addition or mean
def __word_embedding(words, mode="cos_add"):
    if mode == "cos_add":
        return __word_embedding_addition(words)
    else:
        return __word_embedding_mean(words)


# Embedding vector of list of tokens by addition
def __word_embedding_addition(words):
    result = np.zeros(100)
    for w in words:
        if w in W2V_MODEL:
            result = np.sum([result, W2V_MODEL[w]], axis=0)
    return result


# Embedding vector of list of tokens by mean
def __word_embedding_mean(words):
    result = np.zeros(100)
    for w in words:
        if w in W2V_MODEL:
            result = np.sum([result, W2V_MODEL[w]], axis=0)
    result = result / len(words)
    return result


# Takes a list of tokens in features and space
# Computes the cosine similarity between the features and the space
# Returns a sorted list of space by distance
def __get_feature_property_cos(features, space, mode="cos_add"):
    embeddings_prop = {}

    for p in space:
        words = __decompose_word(p)
        embeddings_prop[p] = __word_embedding(words, mode)

    word_embd = __word_embedding(features, mode)

    sorted_list = {}

    for k, v in embeddings_prop.iteritems():
        tmp = spatial.distance.cosine(word_embd, v)
        sorted_list[k] = tmp

    sorted_list = sorted(sorted_list.items(), key=operator.itemgetter(1), reverse=False)

    return sorted_list[0][0].replace("http://dbpedia.org/ontology/", ""), sorted_list[0][1], sorted_list


# Takes a list of tokens in features and space
# Computes the word mover distance between the features and the space
# Returns a sorted list of space by distance
def __get_feature_property_wmd(features, space):
    space_list = {w: __decompose_word(w) for w in space}
    embeddings_prop = {}

    for p in space:
        embeddings_prop[p] = W2V_MODEL.wmdistance(features, space_list[p])

    sorted_list = sorted(embeddings_prop.items(), key=operator.itemgetter(1), reverse=False)

    return sorted_list[0][0].replace("http://dbpedia.org/ontology/", ""), sorted_list[0][1], sorted_list


# Takes a list of tokens in features and space
# Computes the word mover distance between the features and the space
# Gets the precompiled list of features and KB properties
# Returns the closest property in the WMD list that occurs in the precompiled features_properties list
def __get_feature_property_wmd_match(features, space):
    _, _, wmd_list_old = __get_feature_property_wmd(features, space)
    feature_prop_list = load_json("data/features_properties.json")

    feature = get_feature_precompiled(" ".join(features))["features"][0]
    feature_match = [p.replace("dbo:", "") for p in feature_prop_list[feature]["property"] if p is not None]

    wmd_list, _ = zip(*wmd_list_old)

    for prop in wmd_list:
        if prop in feature_match:
            return prop, "bestmatch", wmd_list_old

    return wmd_list_old[0][0], wmd_list_old[0][1], wmd_list_old


# Takes a list of tokens in features and space
# Computes the distance between the features and the space
# Returns a sorted list of space by distance
def get_embeddings(features, space, mode="wmd"):
    if mode == "wmd":
        return __get_feature_property_wmd(features, space)
    elif mode == "cos_add":
        return __get_feature_property_cos(features, space, mode)
    elif mode == "cos_mean":
        return __get_feature_property_cos(features, space, mode)
    elif mode == "wmd_match":
        return __get_feature_property_wmd_match(features, space)


# Gets similar embedding to the superlative in one hop space
def __experiment_one():
    data = load_json("data/one_hop_ontologies_clean.json")
    results = []
    total = len(data)
    correct = 0
    top_two = 0
    top_three = 0

    for row in tqdm(data):
        tmp = {}
        question = row["question"]
        tmp["question"] = question
        prop = get_order_property(row["query"])
        tmp["correct_property"] = prop
        space = [o.replace("http://dbpedia.org/ontology/", "") for o in row["one_hop_ontologies"]]
        # features = get_feature_precompiled(question)["features"]
        features = get_feature_precompiled(question)["keywords"]
        tmp["features"] = features

        embeddings_result = get_embeddings(features, space, mode="wmd")
        tmp["we_result"] = embeddings_result

        results.append(tmp)

        if prop == embeddings_result[0]:
            correct += 1

        top_three_embeddings = embeddings_result[2]
        top_three_embeddings = [i[0] for i in top_three_embeddings]
        top_three_embeddings = top_three_embeddings[:3]
        if prop in top_three_embeddings:
            top_three += 1

        top_two_embeddings = top_three_embeddings[:2]
        if prop in top_two_embeddings:
            top_two += 1

    print "Top One:", correct * 100 / float(total)
    print "Top Two:", top_two * 100 / float(total)
    print "Top Three:", top_three * 100 / float(total)

    save_json(results, "embeddings_exp/results_1.json")
    return results


# Gets similar embedding to the superlative in one hop space
def __experiment_two():
    data = load_json("data/one_hop_ontologies_clean.json")
    results = []
    total = len(data)
    correct = 0
    top_two = 0
    top_three = 0

    out = []

    for row in tqdm(data):
        tmp = {}
        question = row["question"]
        tmp["question"] = question
        prop = get_order_property(row["query"])
        tmp["correct_property"] = prop
        space = [o.replace("http://dbpedia.org/ontology/", "") for o in row["one_hop_ontologies"]]

        features = get_features_nlp(question, row["earl_query"])

        best_score = 100
        a, b, c, d = "", "", [], ""
        for f in features:
            x, score, z = embeddings_result = get_embeddings(f, space, mode="wmd")
            if score <= best_score:
                a = x
                b = score
                c = z
                d = f

        out.append(d)

        tmp["we_result"] = (a, b, c)
        tmp["features"] = d

        # if i == 30:
        #     break

        results.append(tmp)

        if prop == embeddings_result[0]:
            correct += 1

        top_three_embeddings = embeddings_result[2]
        top_three_embeddings = [i[0] for i in top_three_embeddings]
        top_three_embeddings = top_three_embeddings[:3]
        if prop in top_three_embeddings:
            top_three += 1

        top_two_embeddings = top_three_embeddings[:2]
        if prop in top_two_embeddings:
            top_two += 1

    print "Top One:", correct * 100 / float(total)
    print "Top Two:", top_two * 100 / float(total)
    print "Top Three:", top_three * 100 / float(total)

    save_json(results, "embeddings_exp/results_2.json")
    save_json(out, "out/res2.json")

    return results


# Gets similar embedding to the superlative in one hop space
def __experiment_three():
    data = load_json("data/one_hop_ontologies_clean.json")
    results = []
    total = len(data)
    correct = 0
    top_two = 0
    top_three = 0
    out = []
    question_feature = []

    for i, row in enumerate(tqdm(data)):
        tmp = {}
        question = row["question"]
        tmp["question"] = question
        prop = get_order_property(row["query"])
        tmp["correct_property"] = prop
        space = [o.replace("http://dbpedia.org/ontology/", "") for o in row["one_hop_ontologies"]]

        features = get_features_nlp(question, row["earl_query"])

        best_score = 100
        best_feature = []
        for f in features:
            dist = W2V_MODEL.distance(f[0], f[1])
            if dist < best_score:
                best_feature = f

        out.append(best_feature)
        question_feature.append([question, " ".join(best_feature)])


        tmp["features"] = best_feature
        embeddings_result = get_embeddings(best_feature, space, mode="wmd")
        tmp["we_result"] = embeddings_result

        # if i == 40:
        #     break

        results.append(tmp)

        if prop == embeddings_result[0]:
            correct += 1

        top_three_embeddings = embeddings_result[2]
        top_three_embeddings = [i[0] for i in top_three_embeddings]
        top_three_embeddings = top_three_embeddings[:3]
        if prop in top_three_embeddings:
            top_three += 1

        top_two_embeddings = top_three_embeddings[:2]
        if prop in top_two_embeddings:
            top_two += 1

    print "Top One:", correct * 100 / float(total)
    print "Top Two:", top_two * 100 / float(total)
    print "Top Three:", top_three * 100 / float(total)

    save_json(results, "embeddings_exp/results_3.json")
    save_json(out, "out/res3.json")
    save_json(question_feature, "out/question_feature.json")

    return results


def main():
    print "MAIN"
    # __set_up_vocab()
    # __load_embeddings()
    # __experiment_one()
    # __experiment_two()
    __experiment_three()

    # print W2V_MODEL["cyanic"]




if __name__ == '__main__':
    main()


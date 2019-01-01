from gensim.test.utils import datapath, get_tmpfile
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec


def convert(src, save):
    print "Converting Glove to Word2Vec"
    glove_file = datapath(src)
    tmp_file = get_tmpfile("w2v.txt")

    glove2word2vec(glove_file, tmp_file)

    model = KeyedVectors.load_word2vec_format(tmp_file)

    model.save_word2vec_format(save, binary=False)

if __name__ == '__main__':
    src = "/Users/just3obad/Desktop/Thesis/AskNow/SQG/feature_extraction_filter/embeddings_matrix/glove_100d_word2vec" \
          "_vocab.txt"
    save = "/Users/just3obad/Desktop/Thesis/AskNow/SQG/feature_extraction_filter/embeddings_matrix/glove_100d_word2vec" \
           "_vocab.txt"
    convert(src, save)




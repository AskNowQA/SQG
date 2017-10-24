import random
import time
import numpy as np
import tensorflow as tf


class DSSM:
    def __init__(self):
        flags = tf.app.flags
        self.FLAGS = flags.FLAGS

        flags.DEFINE_string('summaries_dir', '/tmp/dssm-400-120-relu', 'Summaries directory')
        flags.DEFINE_float('learning_rate', 0.1, 'Initial learning rate.')
        flags.DEFINE_integer('max_steps', 1000, 'Number of steps to run trainer.')
        flags.DEFINE_integer('epoch_steps', 10, "Number of steps in one epoch.")
        flags.DEFINE_integer('pack_size', 20, "Number of batches in one pickle pack.")
        flags.DEFINE_bool('gpu', 1, "Enable GPU or not")

        self.VOCAB_SIZE = 50000  # VOCAB_SIZE
        self.NEG = 10
        self.BS = 1000

        self.L1_N = 400
        self.L2_N = 120

        self.gamma = 20
        self.model_path = "./tmp/models/dssm.model"

    def __to_sparstensor2(self, input):
        tmp = tf.not_equal(input, 0)
        idx = tf.where(tmp)
        values = tf.gather_nd(input, idx)
        tns = tf.SparseTensor(idx, values, input.get_shape())
        return tns

    def __to_sparstensor(self, input):
        idxs = np.where(input > 0)
        return tf.SparseTensorValue(zip(idxs[0], idxs[1]), input[idxs],
                                    [self.BS, self.VOCAB_SIZE])

    def data_iterator(self, train_set, sparse_output=False):
        index_start = 0
        questions = train_set[0]
        sparqls = train_set[1]
        while True:
            index_end = index_start + self.BS
            if index_end > len(questions):
                index_start = 0
                index_end = index_start + self.BS

            questions_batch = questions[index_start:index_end]
            sparqls_batch = sparqls[index_start:index_end]

            index_start += self.BS
            if sparse_output:
                questions_batch = self.__to_sparstensor(questions_batch)
                sparqls_batch = self.__to_sparstensor(sparqls_batch)

            yield questions_batch, sparqls_batch, index_start

    def __model(self):
        with tf.name_scope('input'):
            query_batch = tf.placeholder(tf.float32, shape=[self.BS, self.VOCAB_SIZE], name="query_batch")
            doc_batch = tf.placeholder(tf.float32, shape=[self.BS, self.VOCAB_SIZE], name="doc_batch")
            query_batch_sparse = self.__to_sparstensor2(query_batch)
            doc_batch_sparse = self.__to_sparstensor2(doc_batch)

        with tf.name_scope('L1'):
            l1_par_range = np.sqrt(6.0 / (self.VOCAB_SIZE + self.L1_N))
            weight1 = tf.Variable(tf.random_uniform([self.VOCAB_SIZE, self.L1_N], -l1_par_range, l1_par_range),
                                  name="weight1")
            bias1 = tf.Variable(tf.random_uniform([self.L1_N], -l1_par_range, l1_par_range), name="bias1")
            query_l1 = tf.sparse_tensor_dense_matmul(query_batch_sparse, weight1) + bias1
            doc_l1 = tf.sparse_tensor_dense_matmul(doc_batch_sparse, weight1) + bias1
            query_l1_out = tf.nn.relu(query_l1)
            doc_l1_out = tf.nn.relu(doc_l1)

        with tf.name_scope('L2'):
            l2_par_range = np.sqrt(6.0 / (self.L1_N + self.L2_N))
            weight2 = tf.Variable(tf.random_uniform([self.L1_N, self.L2_N], -l2_par_range, l2_par_range),
                                  name="weight2")
            bias2 = tf.Variable(tf.random_uniform([self.L2_N], -l2_par_range, l2_par_range), name="bias2")
            query_l2 = tf.matmul(query_l1_out, weight2) + bias2
            doc_l2 = tf.matmul(doc_l1_out, weight2) + bias2
            query_y = tf.nn.relu(query_l2)
            doc_y = tf.nn.relu(doc_l2)

        with tf.name_scope('FD_rotate'):
            # Rotate FD+ to produce 50 FD-
            temp = tf.tile(doc_y, [1, 1])

            for i in range(self.NEG):
                rand = int((random.random() + i) * self.BS / self.NEG)
                doc_y = tf.concat(axis=0,
                                  values=[doc_y,
                                          tf.slice(temp, [rand, 0], [self.BS - rand, -1]),
                                          tf.slice(temp, [0, 0], [rand, -1])])

        with tf.name_scope('Cosine_Similarity'):
            # Cosine similarity
            query_norm = tf.tile(tf.sqrt(tf.reduce_sum(tf.square(query_y), 1, True)), [self.NEG + 1, 1])
            doc_norm = tf.sqrt(tf.reduce_sum(tf.square(doc_y), 1, True))

            prod = tf.reduce_sum(tf.multiply(tf.tile(query_y, [self.NEG + 1, 1]), doc_y), 1, True)
            norm_prod = tf.multiply(query_norm, doc_norm)

            cos_sim_raw = tf.truediv(prod, norm_prod)
            cos_sim = tf.transpose(tf.reshape(tf.transpose(cos_sim_raw), [self.NEG + 1, self.BS])) * self.gamma

        with tf.name_scope('Loss'):
            # Train Loss
            prob = tf.nn.softmax((cos_sim))
            hit_prob = tf.slice(prob, [0, 0], [-1, 1])
            # loss = -tf.reduce_sum(tf.log(hit_prob)) / self.BS
            loss = tf.negative(tf.divide(tf.reduce_sum(tf.log(hit_prob)), self.BS), name="loss_op")
            tf.summary.scalar('loss', loss)

        return loss, query_batch, doc_batch

    def train(self, train_set):
        loss, query_batch, doc_batch = self.__model()
        with tf.name_scope('Training'):
            train_step = tf.train.GradientDescentOptimizer(self.FLAGS.learning_rate).minimize(loss)

        with tf.name_scope('Test'):
            average_loss = tf.placeholder(tf.float32)
            loss_summary = tf.summary.scalar('average_loss', average_loss)

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True

        iter_train = self.data_iterator(train_set, False)
        with tf.Session(config=config) as sess:
            sess.run(tf.global_variables_initializer())
            train_writer = tf.summary.FileWriter(self.FLAGS.summaries_dir + '/train', sess.graph)
            start = time.time()
            for step in range(self.FLAGS.max_steps):
                query_in, doc_in, index_start = iter_train.next()
                sess.run(train_step, feed_dict={query_batch: query_in, doc_batch: doc_in})

                if step % self.FLAGS.epoch_steps == 0:
                    end = time.time()
                    epoch_loss = 0

                    loss_v = sess.run(loss, feed_dict={query_batch: query_in, doc_batch: doc_in})
                    epoch_loss += loss_v

                    train_loss = sess.run(loss_summary, feed_dict={average_loss: epoch_loss})
                    train_writer.add_summary(train_loss, step + 1)

                    print ("\nMiniBatch: %-5d | Train Loss: %-4.3f | PureTrainTime: %-3.3fs | File ptr: %d" %
                           (step, epoch_loss, end - start, index_start))
                    saver = tf.train.Saver()
                    save_path = saver.save(sess, self.model_path, global_step=step)

            saver = tf.train.Saver()
            save_path = saver.save(sess, self.model_path, global_step=self.FLAGS.max_steps)
            print "Model saved in file: %s" % save_path
            end = time.time()
            print ("\nTotal time: %-3.3fs" % (end - start))

    def test(self, test_set):
        saver = tf.train.import_meta_graph(self.model_path + "-1000.meta")
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        iter_test = self.data_iterator(test_set, False)
        with tf.Session(config=config) as sess:
            ckpt = tf.train.get_checkpoint_state("./tmp/models/")
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)

            epoch_loss = 0
            graph = tf.get_default_graph()
            loss = graph.get_tensor_by_name("Loss/loss_op:0")
            query_batch = graph.get_tensor_by_name("input/query_batch:0")
            doc_batch = graph.get_tensor_by_name("input/doc_batch:0")
            for i in range(self.FLAGS.pack_size):
                query_in, doc_in, index_start = iter_test.next()
                loss_v = sess.run(loss, feed_dict={query_batch: query_in, doc_batch: doc_in})
                epoch_loss += loss_v

            epoch_loss /= self.FLAGS.pack_size

            print "Test Loss: %-4.3f" % epoch_loss


if __name__ == "__main__":
    q = DSSM()
    # q.train1()
    # q.test1()

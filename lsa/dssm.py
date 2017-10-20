import pickle
import random
import time
import sys
import numpy as np
import linecache
import tensorflow as tf


class DSSM:
    def __init__(self, VOCAB_SIZE):
        flags = tf.app.flags
        self.FLAGS = flags.FLAGS

        flags.DEFINE_string('summaries_dir', '/tmp/dssm-400-120-relu', 'Summaries directory')
        flags.DEFINE_float('learning_rate', 0.1, 'Initial learning rate.')
        flags.DEFINE_integer('max_steps', 500, 'Number of steps to run trainer.')
        flags.DEFINE_integer('epoch_steps', 10, "Number of steps in one epoch.")
        flags.DEFINE_integer('pack_size', 2000, "Number of batches in one pickle pack.")
        flags.DEFINE_bool('gpu', 1, "Enable GPU or not")

        self.model_path = "/home/raojun/tensorflow/model/dssm.model"
        self.VOCAB_SIZE = 50000  # VOCAB_SIZE
        self.NEG = 10
        self.BS = 1000

        self.L1_N = 400
        self.L2_N = 120

        self.query_in_shape = np.array([self.BS, self.VOCAB_SIZE], np.int64)
        self.doc_in_shape = np.array([self.BS, self.VOCAB_SIZE], np.int64)
        self.label_in_shape = np.array([self.BS, 1], np.int64)

    @staticmethod
    def variable_summaries(var, name):
        """Attach a lot of summaries to a Tensor."""
        with tf.name_scope('summaries'):
            mean = tf.reduce_mean(var)
            tf.summary.scalar('mean/' + name, mean)
            with tf.name_scope('stddev'):
                stddev = tf.sqrt(tf.reduce_sum(tf.square(var - mean)))
            tf.summary.scalar('sttdev/' + name, stddev)
            tf.summary.scalar('max/' + name, tf.reduce_max(var))
            tf.summary.scalar('min/' + name, tf.reduce_min(var))
            tf.summary.histogram(name, var)

    def data_iterator(self, train_set):
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
            idxs = np.where(questions_batch > 0)
            questions_batch = tf.SparseTensorValue(zip(idxs[0], idxs[1]), questions_batch[idxs],
                                                   [self.BS, self.VOCAB_SIZE])
            idxs = np.where(sparqls_batch > 0)
            sparqls_batch = tf.SparseTensorValue(zip(idxs[0], idxs[1]), sparqls_batch[idxs], [self.BS, self.VOCAB_SIZE])

            yield questions_batch, sparqls_batch, index_start

    def train(self, train_set):
        with tf.name_scope('input'):
            # Shape [BS, VOCAB_SIZE].
            query_batch = tf.sparse_placeholder(tf.float32, shape=None)
            # Shape [BS, VOCAB_SIZE]
            doc_batch = tf.sparse_placeholder(tf.float32, shape=None)
            # label_batch = tf.sparse_placeholder(tf.float32, shape=None, name='LabelBatch')

        with tf.name_scope('L1'):
            l1_par_range = np.sqrt(6.0 / (self.VOCAB_SIZE + self.L1_N))
            weight1 = tf.Variable(tf.random_uniform([self.VOCAB_SIZE, self.L1_N], -l1_par_range, l1_par_range))
            bias1 = tf.Variable(tf.random_uniform([self.L1_N], -l1_par_range, l1_par_range))
            DSSM.variable_summaries(weight1, 'L1_weights')
            DSSM.variable_summaries(bias1, 'L1_biases')

            # query_l1 = tf.matmul(tf.to_float(query_batch),weight1)+bias1
            query_l1 = tf.sparse_tensor_dense_matmul(query_batch, weight1) + bias1
            # doc_l1 = tf.matmul(tf.to_float(doc_batch),weight1)+bias1
            doc_l1 = tf.sparse_tensor_dense_matmul(doc_batch, weight1) + bias1

            query_l1_out = tf.nn.relu(query_l1)
            doc_l1_out = tf.nn.relu(doc_l1)

        with tf.name_scope('L2'):
            l2_par_range = np.sqrt(6.0 / (self.L1_N + self.L2_N))

            weight2 = tf.Variable(tf.random_uniform([self.L1_N, self.L2_N], -l2_par_range, l2_par_range))
            bias2 = tf.Variable(tf.random_uniform([self.L2_N], -l2_par_range, l2_par_range))
            DSSM.variable_summaries(weight2, 'L2_weights')
            DSSM.variable_summaries(bias2, 'L2_biases')

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
            cos_sim = tf.transpose(tf.reshape(tf.transpose(cos_sim_raw), [self.NEG + 1, self.BS])) * 20

        with tf.name_scope('Loss'):
            # Train Loss
            prob = tf.nn.softmax((cos_sim))
            hit_prob = tf.slice(prob, [0, 0], [-1, 1])
            loss = -tf.reduce_sum(tf.log(hit_prob)) / self.BS
            tf.summary.scalar('loss', loss)

        with tf.name_scope('Training'):
            # Optimizer
            train_step = tf.train.GradientDescentOptimizer(self.FLAGS.learning_rate).minimize(loss)

        # with tf.name_scope('Accuracy'):
        #     correct_prediction = tf.equal(tf.argmax(prob, 1), 0)
        #     accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        #     tf.scalar_summary('accuracy', accuracy)

        merged = tf.summary.merge_all()

        with tf.name_scope('Test'):
            average_loss = tf.placeholder(tf.float32)
            loss_summary = tf.summary.scalar('average_loss', average_loss)

        config = tf.ConfigProto()  # log_device_placement=True)
        config.gpu_options.allow_growth = True
        # if not FLAGS.gpu:
        # config = tf.ConfigProto(device_count= {'GPU' : 0})

        saver = tf.train.Saver()
        iter_train = self.data_iterator(train_set)
        # iter_test = data_iterator("test")
        with tf.Session(config=config) as sess:
            sess.run(tf.global_variables_initializer())
            train_writer = tf.summary.FileWriter(self.FLAGS.summaries_dir + '/train', sess.graph)
            # test_writer = tf.summary.FileWriter(self.FLAGS.summaries_dir + '/test', sess.graph)

            # Actual execution
            start = time.time()
            q = None
            d = None
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

            save_path = saver.save(sess, self.model_path)
            print "Model saved in file: %s" % save_path

            # for step in range(10):
            #     query_in, doc_in, index_start = iter_test.next()
            #     test_loss = sess.run(loss, feed_dict={query_batch: query_in, doc_batch: doc_in}) #, label_batch:label})
            #     print ("\nMiniBatch: %-5d | Test Loss: %-4.3f" % (step, test_loss))

            end = time.time()
            print ("\nTotal time: %-3.3fs" % (end - start))

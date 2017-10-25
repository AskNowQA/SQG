import random
import time
import numpy as np
import tensorflow as tf


class DSSM:
    def __init__(self, max_steps=1000):
        flags = tf.app.flags
        self.FLAGS = flags.FLAGS

        flags.DEFINE_string('summaries_dir', '/tmp/dssm-400-120-relu', 'Summaries directory')
        flags.DEFINE_float('learning_rate', 0.1, 'Initial learning rate.')
        flags.DEFINE_integer('max_steps', max_steps, 'Number of steps to run trainer.')
        flags.DEFINE_integer('epoch_steps', 100, "Number of steps in one epoch.")
        flags.DEFINE_integer('pack_size', 20, "Number of batches in one pickle pack.")
        flags.DEFINE_bool('gpu', 1, "Enable GPU or not")

        self.VOCAB_SIZE = 50000  # VOCAB_SIZE
        self.NEG = 4
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
        queries = train_set[1]
        while True:
            index_end = index_start + self.BS
            if index_end > len(questions):
                index_start = 0
                index_end = index_start + self.BS

            question_batch = questions[index_start:index_end]
            query_batch = queries[index_start:index_end]

            index_start += self.BS
            if sparse_output:
                question_batch = self.__to_sparstensor(question_batch)
                query_batch = self.__to_sparstensor(query_batch)

            yield question_batch, query_batch, index_start

    def model(self):
        self.__model()

    def __L1(self, question_batch_sparse, query_batch_sparse, weight1, bias1):
        question_l1 = tf.sparse_tensor_dense_matmul(question_batch_sparse, weight1) + bias1
        query_l1 = tf.sparse_tensor_dense_matmul(query_batch_sparse, weight1) + bias1
        question_l1_out = tf.nn.relu(question_l1)
        query_l1_out = tf.nn.relu(query_l1)

        return question_l1_out, query_l1_out

    def __L2(self, question_l1_out, query_l1_out, weight2, bias2):
        question_l2 = tf.matmul(question_l1_out, weight2) + bias2
        query_l2 = tf.matmul(query_l1_out, weight2) + bias2
        question_y = tf.nn.relu(question_l2)
        query_y = tf.nn.relu(query_l2)
        return question_y, query_y

    def __FD_rotate(self, query_y):
        with tf.name_scope('FD_rotate'):
            # Rotate FD+ to produce self.NEG FD-

            temp = tf.tile(query_y, [1, 1], name="tile")
            for i in range(self.NEG):
                rand = int((random.random() + i) * self.BS / self.NEG)
                query_y = tf.concat(axis=0,
                                    values=[query_y,
                                            tf.slice(temp, [rand, 0], [self.BS - rand, -1]),
                                            tf.slice(temp, [0, 0], [rand, -1])])
            return query_y

    def __cosine_similarity(self, question_y, query_y, rotated=True):
        with tf.name_scope('Cosine_Similarity'):
            if rotated:
                question_norm = tf.tile(tf.sqrt(tf.reduce_sum(tf.square(question_y), 1, True)), [self.NEG + 1, 1])
            else:
                question_norm = tf.sqrt(tf.reduce_sum(tf.square(question_y), 1, True))
            query_norm = tf.sqrt(tf.reduce_sum(tf.square(query_y), 1, True))

            prod = tf.reduce_sum(tf.multiply(tf.tile(question_y, [self.NEG + 1, 1]), query_y), 1, True)
            norm_prod = tf.multiply(question_norm, query_norm)

            cos_sim_raw = tf.truediv(prod, norm_prod)
            # cos_sim = tf.transpose(tf.reshape(tf.transpose(cos_sim_raw), [self.NEG + 1, self.BS])) * self.gamma
            cos_sim = tf.multiply(tf.transpose(tf.reshape(tf.transpose(cos_sim_raw), [self.NEG + 1, self.BS])),
                                  self.gamma, name="cos_sim")
            return cos_sim

    def __log_loss(self, cos_sim):
        with tf.name_scope('Loss'):
            prob = tf.nn.softmax((cos_sim))
            hit_prob = tf.slice(prob, [0, 0], [-1, 1])
            # loss = -tf.reduce_sum(tf.log(hit_prob)) / self.BS
            loss = tf.negative(tf.divide(tf.reduce_sum(tf.log(hit_prob)), self.BS), name="loss_op")
            tf.summary.scalar('loss', loss)
            return loss

    def __input_layer(self):
        with tf.name_scope('input'):
            question_batch = tf.placeholder(tf.float32, shape=[self.BS, self.VOCAB_SIZE], name="question_batch")
            query_batch = tf.placeholder(tf.float32, shape=[self.BS, self.VOCAB_SIZE], name="query_batch")
            question_batch_sparse = self.__to_sparstensor2(question_batch)
            query_batch_sparse = self.__to_sparstensor2(query_batch)
            return question_batch_sparse, query_batch_sparse, question_batch, query_batch

    def __model(self, training=True, weight1=None, bias1=None, weight2=None, bias2=None):
        question_batch_sparse, query_batch_sparse, question_batch, query_batch = self.__input_layer()

        with tf.name_scope('L1'):
            if training:
                l1_par_range = np.sqrt(6.0 / (self.VOCAB_SIZE + self.L1_N))
                weight1 = tf.Variable(tf.random_uniform([self.VOCAB_SIZE, self.L1_N], -l1_par_range, l1_par_range),
                                      name="weight1")
                bias1 = tf.Variable(tf.random_uniform([self.L1_N], -l1_par_range, l1_par_range), name="bias1")
            question_l1_out, query_l1_out = self.__L1(question_batch_sparse, query_batch_sparse, weight1, bias1)

        with tf.name_scope('L2'):
            if training:
                l2_par_range = np.sqrt(6.0 / (self.L1_N + self.L2_N))
                weight2 = tf.Variable(tf.random_uniform([self.L1_N, self.L2_N], -l2_par_range, l2_par_range),
                                      name="weight2")
                bias2 = tf.Variable(tf.random_uniform([self.L2_N], -l2_par_range, l2_par_range), name="bias2")
            question_y, query_y = self.__L2(question_l1_out, query_l1_out, weight2, bias2)

        if training:
            query_y = self.__FD_rotate(query_y)
        cos_sim = self.__cosine_similarity(question_y, query_y, training)
        loss = self.__log_loss(cos_sim)

        return {"cos_sim": cos_sim, "loss": loss, "question_batch": question_batch, "query_batch": query_batch}

    def train(self, train_set):
        model = self.__model()
        loss, question_batch, query_batch = model["loss"], model["question_batch"], model["query_batch"]

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
                question_in, query_in, index_start = iter_train.next()
                sess.run(train_step, feed_dict={question_batch: question_in, query_batch: query_in})

                if step % self.FLAGS.epoch_steps == 0:
                    end = time.time()
                    epoch_loss = 0

                    loss_v = sess.run(loss, feed_dict={question_batch: question_in, query_batch: query_in})
                    epoch_loss += loss_v

                    train_loss = sess.run(loss_summary, feed_dict={average_loss: epoch_loss})
                    train_writer.add_summary(train_loss, step + 1)

                    print ("\nMiniBatch: %-5d | Train Loss: %-4.3f | PureTrainTime: %-3.3fs | File ptr: %d" %
                           (step, epoch_loss, end - start, index_start))
                    saver = tf.train.Saver()
                    saver.save(sess, self.model_path, global_step=step)

            saver = tf.train.Saver()
            save_path = saver.save(sess, self.model_path, global_step=self.FLAGS.max_steps)
            print "Model saved in file: %s" % save_path
            end = time.time()
            print ("\nTotal time: %-3.3fs" % (end - start))

    def test(self, test_set):
        saver = tf.train.import_meta_graph(self.model_path + "-" + str(self.FLAGS.max_steps) + ".meta")
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
            question_batch = graph.get_tensor_by_name("input/question_batch:0")
            query_batch = graph.get_tensor_by_name("input/query_batch:0")
            for i in range(self.FLAGS.pack_size):
                question_in, query_in, index_start = iter_test.next()
                loss_v = sess.run(loss, feed_dict={question_batch: question_in, query_batch: query_in})
                print loss_v
                epoch_loss += loss_v

            epoch_loss /= self.FLAGS.pack_size

            print "Test Loss: %-4.3f" % epoch_loss

    def similarity(self, question_in, query_in):
        self.NEG = 0
        saver = tf.train.import_meta_graph(self.model_path + "-" + str(self.FLAGS.max_steps) + ".meta")
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        with tf.Session(config=config) as sess:
            ckpt = tf.train.get_checkpoint_state("./tmp/models/")
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)

            graph = tf.get_default_graph()
            weight1 = graph.get_tensor_by_name("L1/weight1:0")
            bias1 = graph.get_tensor_by_name("L1/bias1:0")
            weight2 = graph.get_tensor_by_name("L2/weight2:0")
            bias2 = graph.get_tensor_by_name("L2/bias2:0")

            weight1_v = sess.run(weight1)
            bias1_v = sess.run(bias1)
            weight2_v = sess.run(weight2)
            bias2_v = sess.run(bias2)

        tf.reset_default_graph()
        with tf.Session(config=config) as sess:
            model = self.__model(False, weight1_v, bias1_v, weight2_v, bias2_v)
            question_batch, query_batch = model["question_batch"], model["query_batch"]
            cos_sim = model["cos_sim"]
            cos_sim_v = sess.run(cos_sim, feed_dict={question_batch: question_in, query_batch: query_in})
            print cos_sim_v.shape
            return cos_sim_v


if __name__ == "__main__":
    q = DSSM()
    # q.tmp()
    q.similarity()

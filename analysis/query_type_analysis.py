import numpy as np
from parser.lc_quad import LC_Qaud
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV

ds = LC_Qaud("../data/LC-QUAD/data_v8.json")
ds.load()
ds.parse()

X = []
y = []
for qapair in ds.qapairs:
    X.append(qapair.question.text)
    if "COUNT(" in qapair.sparql.raw_query:
        y.append(2)
    elif "ASK WHERE" in qapair.sparql.raw_query:
        y.append(1)
    else:
        y.append(0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

text_clf = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()), ('clf', MultinomialNB())])
text_clf = text_clf.fit(X_train, y_train)

predicted = text_clf.predict(X_test)
print "naive bayes: ", np.mean(predicted == y_test)

parameters = {'vect__ngram_range': [(1, 1), (1, 2)], 'tfidf__use_idf': (True, False), 'clf__alpha': (1e-2, 1e-3)}
gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
gs_clf = gs_clf.fit(X_train, y_train)
print "naive bayes optimized :"
print gs_clf.best_score_
print gs_clf.best_params_

predicted = gs_clf.predict(X_test)
print "naive bayes: ", np.mean(predicted == y_test)

text_clf_svm = Pipeline([('vect', CountVectorizer()), ('tfidf', TfidfTransformer()),
                         ('clf-svm', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, n_iter=5, random_state=42))])

text_clf_svm = text_clf_svm.fit(X_train, y_train)
predicted_svm = text_clf_svm.predict(X_test)
print "\n\nsvm", np.mean(predicted_svm == y_test)

parameters_svm = {'vect__ngram_range': [(1, 1), (1, 2)], 'tfidf__use_idf': (True, False),
                  'clf-svm__alpha': (1e-2, 1e-3)}
gs_clf_svm = GridSearchCV(text_clf_svm, parameters_svm, n_jobs=-1)
gs_clf_svm = gs_clf_svm.fit(X_train, y_train)

print "naive bayes optimized :"
print gs_clf_svm.best_score_
print gs_clf_svm.best_params_

predicted_svm = text_clf_svm.predict(X_test)
print "svm", np.mean(predicted_svm == y_test)

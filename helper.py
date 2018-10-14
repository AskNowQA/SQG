from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

text = ["The quick brown fox jumped over the lazy dog.", "dog cat lazy lion jumped"]

vectorizer = CountVectorizer(ngram_range=(2,2))
text_count = vectorizer.fit_transform(text)
print text_count.toarray()
print vectorizer.get_feature_names()
#
# print (vectorizer.vocabulary_)
#
# vector = vectorizer.transform(text)
#
# print(vector.shape)
# print(type(vector))
# print(vector.toarray())


# vectorizer_2 = TfidfTransformer(use_idf=False).fit(text_count)
# vector = vectorizer_2.transform(text_count)

# print vectorizer_2.get_feature_names()





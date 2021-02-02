from sudachipy import tokenizer, dictionary

tokenizer_obj =dictionary.Dictionary().create()
mode = tokenizer.Tokenizer.SplitMode.C
opentime = [m.surface() for m in tokenizer_obj.tokenize("頭が痛い", mode)]
# print(opentime)

import spacy
nlp = spacy.load('ja_ginza')
# doc = nlp('お腹が痛い')

# for sent in doc.sents:
#     for token in sent:
#         print(token)

doc1 = nlp("昔、高校の運動部で厳しい練習をしていた")
doc2 = nlp("セーフモードで起動できる")

similarity = doc1.similarity(doc2)
print(similarity)
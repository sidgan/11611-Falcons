import nltk
from nltk.corpus import treebank

s = "The boy is playing with a ball"

#Tokenize 
tokens = nltk.word_tokenize(s)

#POS Tagging
tags = nltk.pos_tag(tokens)

#Named entities
entities = nltk.chunk.ne_chunk(tags)
entities.draw()

#Good example of a parse tree
tree = treebank.parsed_sents('wsj_0001.mrg')[0]
tree.draw()



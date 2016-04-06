__author__ = 'avnishs'

from collections import Counter

import nltk as nl


class Article:
    def __init__(self, article):
        self.sentences = nl.tokenize.sent_tokenize(article)
        self.doc_len = dict()
        self.tf = Counter()
        for sentence in self.sentences:
            self.tf.update(sentence.split())
            self.doc_len[sentence] = len(sentence)

            # pprint(self.doc_len)
            # pprint(self.tf)

    def get_N(self):
        return len(self.sentences)

    def get_avg_dlen(self):
        return sum(self.doc_len.values()) / len(self.doc_len)

    def get_dlen(self, sentence):
        return self.doc_len[sentence]

    def get_tf(self, term):
        if term in self.tf:
            return self.tf[term]
        return 0

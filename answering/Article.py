__author__ = 'avnishs'

import nltk as nl
from collections import Counter


class Article:
    def __init__(self, article):
        self.sentences = article
        self.doc_len = dict()
        self.tf = Counter()
        for sentence in self.sentences:
            self.tf.update(sentence.split())
            self.doc_len[sentence] = len(sentence)

    def get_num_sentences(self):
        return len(self.sentences)

    def get_avg_doclen(self):
        return sum(self.doc_len.values()) / len(self.doc_len)

    def get_doclen(self, sentence):
        return self.doc_len[sentence]

    def get_term_freq(self, term):
        if term in self.tf:
            return self.tf[term]
        return 0

__author__ = 'pbamotra'

from gensim import corpora
import gensim


class Dict2Mat:
    def __init__(self):
        self.dictionary = corpora.dictionary.Dictionary()
        self.documents = list()

    def add_document(self, list_of_words):
        self.documents.append(list_of_words)
        self.dictionary.add_documents([list_of_words])

    def get_doc_term_matrix(self):
        doc2bow = [self.dictionary.doc2bow(text) for text in self.documents]
        doc_term_matrix = gensim.matutils.corpus2dense(doc2bow, num_terms=len(self.dictionary.keys()))
        return doc_term_matrix.transpose()


if __name__ == '__main__':
    sample = [['what', 'nn-nnp', 'location-o'],
              ['what', 'nn-nnp', 'vb-vbz', 'location-o', 'organization-o']]
    dic2mat = Dict2Mat()
    for document in sample:
        dic2mat.add_document(document)

    print dic2mat.get_doc_term_matrix()
__author__ = 'pbamotra'

import gensim
from gensim import corpora


class Dict2Mat:
    def __init__(self, training_phase=True):
        self.documents = list()
        self.training_phase = training_phase
        if self.training_phase:
            self.dictionary = corpora.dictionary.Dictionary()

    def add_document(self, list_of_words):
        self.documents.append(list_of_words)
        if self.training_phase:
            self.dictionary.add_documents([list_of_words])

    def get_doc_term_matrix(self, dictionary=None):
        if self.training_phase:
            doc2bow = [self.dictionary.doc2bow(text) for text in self.documents]
        else:
            if dictionary is None:
                raise UserWarning('Please supply the dictionary you used in training')
            else:
                self.dictionary = dictionary
                doc2bow = [self.dictionary.doc2bow(text) for text in self.documents]
        doc_term_matrix = gensim.matutils.corpus2dense(doc2bow, num_terms=len(self.dictionary.keys()))
        return doc_term_matrix.transpose()

    def get_dictionary(self):
        return self.dictionary

'''
if __name__ == '__main__':
    sample = [['what', 'nn-nnp', 'location-o'],
              ['what', 'nn-nnp', 'vb-vbz', 'location-o', 'organization-o']]
    dic2mat = Dict2Mat()
    for document in sample:
        dic2mat.add_document(document)

    print dic2mat.get_doc_term_matrix()

    dictionary = dic2mat.get_dictionary()
    dic2mat2 = Dict2Mat(False)
    sample = [['what', 'nn-vb', 'location-o']]

    for document in sample:
        dic2mat2.add_document(document)

    print dic2mat2.get_doc_term_matrix(dictionary)
'''
import gensim
from gensim import corpora

__author__ = 'pbamotra'


class Dict2Mat:
    """
    Used to convert a set of documents into BOW matrix
    """
    def __init__(self, training_phase=True):
        """
        Initializes the class

        :param training_phase: boolean set to true saves dictionary in case it's the training phase
        """
        self.documents = list()
        self.training_phase = training_phase
        if self.training_phase:
            self.dictionary = corpora.dictionary.Dictionary()

    def add_document(self, list_of_words):
        """
        Adds document at time into dictionary

        :param list_of_words: document as a list of word
        """
        self.documents.append(list_of_words)
        if self.training_phase:
            self.dictionary.add_documents([list_of_words])

    def get_doc_term_matrix(self, dictionary=None):
        """
        Converts the stored documents into BOW count matrix

        :param dictionary: dictionary constructed in the training phase
        :return: BOW count matrix
        """
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
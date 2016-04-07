# encoding: utf-8
from __future__ import unicode_literals
__author__ = 'avnishs'

from itertools import chain
import Queue
import threading
from spacy.en import English
import nltk as nl


class FeatureExtractor:
    Tagger = None

    '''Extract WH-WORD'''

    def extract_wh_word(self, terms):
        # wh_list = ['Whose', 'When', 'Where', 'Why', 'How', 'What', 'Who', 'Which']
        # try:
        #     return wh_list.index(terms[0])
        # except ValueError:
        #     print terms[0]
        #     return -1
        return [terms[0].lower()]

    '''Extract HEAD-WORD'''

    def extract_head(self, terms):
        if terms[0] in ['when', 'where', 'why']:
            return None

        elif terms[0] == 'how':
            return terms[1]

        elif terms[0] == 'what':
            if terms[1] in {'is', 'are'}:
                if terms[-2:] in [['composed', 'of'], ['made', 'of']] or terms[-3:] == ['made', 'out', 'of']:
                    return 'enty_subs'

                if terms[-2:] == ['used', 'for']:
                    return 'desc_reason_p2'

                if len(terms) < 5:
                    return 'desc_def_p1'

            elif terms[1] in {'do', 'does'}:
                if terms[-1:] in {'mean', 'means'}:
                    return 'desc_def_p2'

                if terms[-2:] == ['stand', 'for']:
                    return 'abbr_exp'

                if terms[0] == 'does' and terms[-1:] == 'do':
                    return 'desc_desc'

                if terms[1:4] == ['do', 'you', 'call']:
                    return 'entity_term'

            elif terms[1] in {'causes', 'cause'}:
                return 'desc_reason_p1'

        elif terms[0] == 'who' and terms[1] in {'is', 'are', 'was', 'were'} and (
                    (terms[2] == 'the' and nl.pos_tag(terms[3])[0][1].startswith('NN')) or nl.pos_tag(terms[2])[0][
                    1].startswith('NN')):
            return 'hum_desc'

        tags = nl.pos_tag(terms)
        for i in range(len(terms)):
            if tags[i][1].startswith('NN'):
                return terms[i]

    '''Extract WORD-SHAPE'''

    def extract_word_shape(self, head_word):
        if head_word.isdigit():
            return 'digits'
        elif head_word.isalpha():
            if head_word.islower():
                return 'lower'
            elif head_word.isupper():
                return 'upper'
            else:
                return 'mixed'
        else:
            return 'other'

    '''Extact N-GRAMS'''

    def extract_bigrams(self, terms):
        return map(lambda (w1, w2): w1 + "-" + w2, zip(terms, terms[1:]))

    def extract_tagged_bigrams(self, sentence):
        q1 = Queue.Queue()
        q2 = Queue.Queue()
        threading.Thread(target=self.extract_POS_tags, args=(sentence, q1)).start()
        threading.Thread(target=self.extract_NER_tags, args=(sentence, q2)).start()
        pos_tags = q1.get()
        ner_tags = q2.get()
        rel_ner = list()
        rel_pos = list()
        rel_terms = list()
        for i in range(len(ner_tags)):
            if len(ner_tags[i]) != 0 or pos_tags[i].startswith(u'NN') or pos_tags[i].startswith(u'VB') or \
                    pos_tags[i].startswith(u'RB') or pos_tags[i].startswith(u'JJ'):
                rel_ner.append(ner_tags[i])
                rel_pos.append(pos_tags[i])
        return self.extract_bigrams(rel_ner), self.extract_bigrams(rel_pos)  # ,self.extract_bigrams(rel_terms)

    def extract_trigrams(self, terms):
        return map(lambda (w1, w2, w3): w1 + " " + w2 + " " + w3, zip(terms, terms[1:], terms[2:]))

    def extract_NER_tags(self, sentence, q):
        tagged_sen = self.Tagger(sentence)
        q.put([word.ent_type_ for word in tagged_sen])

    def extract_POS_tags(self, sentence, q):
        tagged_sen = self.Tagger(sentence)
        q.put([word.tag_ for word in tagged_sen])

    '''Extract WORDNET SEMANTIC FTRS'''

    def extract_wordnet_sem(self):
        pass

    def __init__(self):
        self.Tagger = English()

    def extract_features(self, sentence, q=None):
        terms = nl.word_tokenize(sentence)
        feature_vector = list()
        feature_vector.append(self.extract_wh_word(terms))
        ner_bigrams, pos_bigrams = self.extract_tagged_bigrams(u"{}".format(sentence))
        feature_vector.append(ner_bigrams)
        feature_vector.append(pos_bigrams)
        # feature_vector.append(self.extract_head(terms))
        # feature_vector.append(terms)
        return list(chain.from_iterable(feature_vector))

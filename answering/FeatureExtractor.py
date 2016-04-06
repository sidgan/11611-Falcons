__author__ = 'avnishs'

from itertools import chain

import nltk as nl
from nltk.tag import StanfordNERTagger


class FeatureExtractor:
    NERTagger = None

    '''Extract WH-WORD'''

    def extract_wh_word(self, terms):
        # wh_list = ['Whose', 'When', 'Where', 'Why', 'How', 'What', 'Who', 'Which']
        # try:
        #     return wh_list.index(terms[0])
        # except ValueError:
        #     print terms[0]
        #     return -1
        return [terms[0].lower()]

    def extract_NER_tags(self, terms):
        return self.NERTagger.tag(terms)

    def extract_POS_tags(self, terms):
        return nl.pos_tag(terms)

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

    def extract_tagged_bigrams(self, terms):
        pos_tags = self.extract_POS_tags(terms)
        ner_tags = self.extract_NER_tags(terms)
        rel_ner = list()
        rel_pos = list()
        rel_terms = list()
        for i in range(len(ner_tags)):
            if ner_tags[i][1] != u'O' or pos_tags[i][1].startswith(u'NN') or pos_tags[i][1].startswith(u'VB') or \
                    pos_tags[i][1].startswith(u'RB') or pos_tags[i][1].startswith(u'JJ'):
                rel_ner.append(ner_tags[i][1])
                rel_pos.append(pos_tags[i][1])
                rel_terms.append(pos_tags[i][0])
        return self.extract_bigrams(rel_ner), self.extract_bigrams(rel_pos)  # ,self.extract_bigrams(rel_terms)

    def extract_trigrams(self, terms):
        return map(lambda (w1, w2, w3): w1 + " " + w2 + " " + w3, zip(terms, terms[1:], terms[2:]))

    '''Extract WORDNET SEMANTIC FTRS'''

    def extract_wordnet_sem(self):
        pass

    def __init__(self):
        self.NERTagger = StanfordNERTagger('../Stanford-NER/classifiers/english.muc.7class.distsim.crf.ser.gz',
                                           '../Stanford-NER/stanford-ner.jar')

    def extract_features(self, sentence):
        terms = nl.word_tokenize(sentence)
        feature_vector = list()
        feature_vector.append(self.extract_wh_word(terms))
        ner_bigrams, pos_bigrams = self.extract_tagged_bigrams(terms)
        feature_vector.append(ner_bigrams)
        feature_vector.append(pos_bigrams)
        # feature_vector.append(self.extract_head(terms))
        # feature_vector.append(terms)
        return list(chain.from_iterable(feature_vector))

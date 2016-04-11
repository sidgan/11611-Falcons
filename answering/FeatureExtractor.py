from __future__ import unicode_literals
import Queue
import threading
import nltk as nl
from Commons import *
from itertools import chain
from nltk.corpus import wordnet as wn

__author__ = 'avnishs'


class FeatureExtractor:
    def __init__(self):
        self.TAGGER = nlp
        self.PATTERN = re.compile(r"(\w+):(\w+) (.+)")

    def extract_wh_word(self, terms):
        """
        Extracts wh words from the terms in question
        :param terms: terms of the question sentence
        :return: wh-word from the sentence in lower-case
        """
        wh_list = ['whose', 'when', 'where', 'why', 'how', 'what', 'who', 'which', 'whom']
        for term in terms[::-1]:
            if term.lower() in wh_list:
                return term
        return [terms[0].lower()]

    def extract_head(self, terms):
        """
        Extracts head word of the sentence from the terms in question
        :param terms: terms of the question sentence
        :return: head word in the question
        """
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

    def extract_word_shape(self, head_word):
        """
        Extracts the head word's syntactic class - digit? lowercase? etc.
        :param head_word: head word of the question
        :return: syntactic class - digits, lower, upper, mixed, other
        """
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

    def create_ngrams(self, terms, n=2):
        """
        Creates n-grams from the terms
        :param terms: list of terms from which n-grams are to be formed
        :param n: length of the n-gram
        :return: list of n-grams
        """
        n_grams = map(list, zip(*[terms[i:] for i in range(n)]))
        return ['-'.join(n_gram) for n_gram in n_grams]

    def create_tagged_seq(self, sentence):
        """
        Extracts language features like POS n-grams, NER n-grams, WORD-NET term synonyms
        of the terms in the sentence
        :param sentence: sentence to be tagged
        :return: Features of sentence including
        """
        sentence = self.TAGGER(sentence)
        sentence_tokens = sentence.text.split()

        q1 = Queue.Queue()
        q2 = Queue.Queue()

        threading.Thread(target=self.extract_pos_tags, args=(sentence, q1)).start()
        threading.Thread(target=self.extract_ner_tags, args=(sentence, q2)).start()

        pos_tags = q1.get()
        ner_tags = q2.get()

        rel_ner, rel_pos, rel_cat = list(), list(), list()

        for i in range(len(ner_tags)):
            if len(ner_tags[i]) != 0 \
                    or pos_tags[i].startswith(u'NN') or pos_tags[i].startswith(u'VB') \
                    or pos_tags[i].startswith(u'RB') or pos_tags[i].startswith(u'JJ'):
                rel_ner.append(ner_tags[i])
                rel_pos.append(pos_tags[i])
                if pos_tags[i][0] in {'R', 'N', 'V'}:
                    word_cat = wn.synsets(sentence_tokens[i], pos_tags[i][0].lower())
                    if len(word_cat) > 0:
                        rel_cat.append(word_cat[0].lexname().split('.')[-1])

        if len(rel_cat) == 0:
            rel_cat.append(u'')

        return rel_cat, rel_ner, rel_pos

    def extract_ner_tags(self, tagged_sen, q):
        """
        Extracts NER tags from the tagged sentence
        :param tagged_sen: SPACY.IO specific tagged sentence
        :param q: thread queue
        """
        q.put([word.ent_type_ for word in tagged_sen])

    def extract_pos_tags(self, tagged_sen, q):
        """
        Extracts POS tags from the tagged sentence
        :param tagged_sen: SPACY.IO specific tagged sentence
        :param q: thread queue
        """
        q.put([word.tag_ for word in tagged_sen])

    def create_wh_term_priors(self, wh_term):
        """
        Extract prior probabilities of the wh-terms
        :param wh_term: term for which probability is to be found
        """
        with open('qa_classification_pr.txt', 'r') as f:
            lines = f.readlines()

        for line in lines:
            match = self.PATTERN.match(line)

    def get_question_features(self, sentence):
        """
        Creates a list of features used by the question classifier
        :param sentence: question for which features are to be created
        :return: feature list - ['Wh-word', 'word-net category', 'NER unigrams', 'POS unigrams',
                                'NER bigrams', 'POS bigrams']
        """
        terms = nl.word_tokenize(sentence)
        feature_vector = list()
        feature_vector.append(self.extract_wh_word(terms))
        rel_cat, rel_ner, rel_pos = self.create_tagged_seq(u"{}".format(sentence))
        feature_vector.append(rel_cat)
        feature_vector.append(rel_ner)
        feature_vector.append(rel_pos)
        feature_vector.append(self.create_ngrams(rel_ner, n=2))
        feature_vector.append(self.create_ngrams(rel_pos, n=2))
        return list(chain.from_iterable(feature_vector))

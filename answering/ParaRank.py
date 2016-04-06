# -*- coding: utf-8 -*-

import math
import operator
import re
import sys
from collections import Counter
from collections import defaultdict
from itertools import chain

import nltk as nl
import numpy as np
from nltk.tag import StanfordNERTagger
from sklearn.svm import SVC

WORD = re.compile(r'\w+')


def main(argv=None):
    if argv is None:
        argv = sys.argv

    # articlePath = '../data/a1.txt'
    # question = u"When was Dempsey born ?"
    #
    # with open('../data/qa_classification_tr.txt','r') as f:
    #     lines = f.readlines()
    #     qc = QuestionClassifier()
    #     qc.train(lines)
    #
    # with open('../data/qa_classification_te.txt','r') as f:
    #     lines = f.readlines()
    #     acc,pred = qc.test(lines)
    #     print acc
    #     #print pred
    #
    # print qc.predict("Where was Pankesh born?")
    # print qc.predict("When was Pankesh born?")
    # print qc.predict("How was Pankesh born?")
    # print qc.predict("What is Pankesh doing?")
    # print qc.predict("Who is Pankesh?")


    fe = FeatureExtractor()

    print fe.extract_tagged_bigrams("Is Pittsburgh the coldest place in the world ?".split())
    # with open(articlePath, 'r') as file:
    #     paras = file.readlines()
    #
    # paras = process_text(paras)
    # paras = ' . '.join(paras)
    #
    # # TODO: Remove Stop Words from Query and Article
    # curr_article = Article(paras.decode('utf-8'))
    #
    # fe = FeatureExtractor()
    # # print fe.extract_head("who was the inventor of television ?");
    # print fe.extract_word_shape('e3llo')
    # print bm25_ranker(curr_article,question,1.2,0.75,0,10)
    # print cos_similarity_ranker(curr_article, question, 10)
    print 'done!'


def process_text(sentences):
    # "Hello World!" -> "hello world !"
    new_sen = list()
    for sen in sentences:
        s = re.sub('([.,!?()])', r' \1 ', sen)
        s = re.sub('\s{2,}', ' ', s.strip())
        s = s.lower().strip()
        if len(s) < 1: continue
        new_sen.append(s)
    return new_sen


def bm25_ranker(article, question, k1, b, k3, K):
    df = defaultdict(int)
    pattern = re.compile('[\W_]+')
    pattern.sub('', question)
    line2score = defaultdict()
    qtf = Counter(question.split())
    # pprint(qtf)
    for term in qtf.keys():
        for sentence in article.sentences:
            if term in sentence:
                df[term] = df.get(term, 0) + 1

        for sentence in article.sentences:
            if term in sentence:
                log_term = math.log10((article.get_N() - df[term] + 0.5) / (float)(df[term] + 0.5))
                # print log_term
                k1_term = k1 * ((1 - b) + b * (len(sentence) / (float)(article.get_avg_dlen())))
                # print k1_term
                k3_term = ((float)((k3 + 1) * qtf[term])) / (k3 + qtf[term])
                # print k3_term
                # print '-' * 100
                line2score[sentence] = line2score.get(sentence, 0) + log_term * (
                    (float)(article.get_tf(term)) / (article.get_tf(term) + k1_term)) * k3_term;

    return sorted(line2score.items(), key=operator.itemgetter(1), reverse=True)[0:min(K, len(line2score))]


def cos_similarity_ranker(article, question, K):
    pattern = re.compile('[\W_]+')
    pattern.sub('', question)
    line2score = defaultdict()

    term_count = defaultdict()
    for sentence in article.sentences:
        line2score[sentence] = get_cosine(text_to_vector(question), text_to_vector(sentence))

    return sorted(line2score.items(), key=operator.itemgetter(1), reverse=True)[0:min(K, len(line2score))]

####################### CHANGE ########################

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

#######################################################

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


class FeatureExtractor:
    NERTagger = None

    '''Extract WH-WORD'''
    def extract_wh_word(self, terms):
        wh_list = ['Whose', 'When', 'Where', 'Why', 'How', 'What', 'Who', 'Which']
        try:
            return wh_list.index(terms[0])
        except ValueError:
            print terms[0]
            return -1

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
        feature_vector = list();
        feature_vector.append(self.extract_wh_word(terms))
        feature_vector.append(self.extract_tagged_bigrams(terms))
        # feature_vector.append(self.extract_head(terms))
        # feature_vector.append(terms)
        return chain.from_iterable(feature_vector)


class QuestionClassifier:
    LABELS = ['DESC', 'ENTY', 'LOC', 'ABBR', 'HUM', 'NUM']
    PATTERN = re.compile(r"(\w+):(\w+) (.+)")
    MODEL = None

    def __init__(self):
        pass

    def train(self, training_set):
        training_features = list()
        training_labels = list()
        fe = FeatureExtractor()
        for sentence in training_set:
            match = self.PATTERN.match(sentence)
            # print fe.extract_features(match.group(3))
            training_features.append(fe.extract_features(match.group(3)))
            training_labels.append(self.LABELS.index(match.group(1)))
        # self.MODEL = linear_model.LogisticRegression(C=1e5)
        # self.MODEL = tree.DecisionTreeClassifier()
        self.MODEL = SVC()
        self.MODEL.fit(np.array(training_features), np.array(training_labels))

    def test(self, testing_set):
        if self.MODEL is None:
            print "Call the train function first!"
            return None
        predictions = list()
        correct = 0
        total = 0
        fe = FeatureExtractor()
        for sentence in testing_set:
            total += 1
            match = self.PATTERN.match(sentence)
            prediction = self.MODEL.predict(fe.extract_features(match.group(3)))
            predictions.append(self.LABELS[prediction])
            if prediction == self.LABELS.index(match.group(1)):
                correct += 1
        return float(correct) / total, predictions

    def predict(self, question):
        if self.MODEL is None:
            print "Call the train function first!"
            return None
        fe = FeatureExtractor()
        return self.LABELS[self.MODEL.predict(fe.extract_features(question))]

if __name__ == '__main__':
    main()

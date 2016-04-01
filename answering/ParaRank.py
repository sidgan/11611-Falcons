# -*- coding: utf-8 -*-

import math
import operator
import re
import sys
from collections import Counter
from collections import defaultdict

import nltk as nl

WORD = re.compile(r'\w+')


def main(argv=None):
    if argv is None:
        argv = sys.argv

    articlePath = '../data/a1.txt'
    question = u"When was Dempsey born ?"

    with open(articlePath, 'r') as file:
        paras = file.readlines()

    paras = process_text(paras)
    paras = ' . '.join(paras)

    # TODO: Remove Stop Words from Query and Article
    curr_article = Article(paras.decode('utf-8'))

    fe = FeatureExtractor()
    print fe.extract_head("who was the inventor of television ?");
    # print bm25_ranker(curr_article,question,1.2,0.75,0,10)
    # print cos_similarity_ranker(curr_article, question, 10)


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
    '''Extract WH-WORD'''

    def extract_wh_word(self, terms):
        return terms[0]

    '''Extract HEAD-WORD'''

    def extract_head(self, terms):
        # terms = nl.word_tokenize(question)

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

    '''Extact N-GRAMS'''
    def extract_bigrams(self, terms):
        return map(lambda (w1, w2): w1 + " " + w2, zip(terms, terms[1:]))

    def extract_trigrams(self, terms):
        return map(lambda (w1, w2, w3): w1 + " " + w2 + " " + w3, zip(terms, terms[1:], terms[2:]))

    '''Extract WORDNET SEMANTIC FTRS'''

    def __init__(self):
        pass


class Classifier:

    def __init__(self):
        pass

    def train(self):
        pass

    def predict(self):
        pass


if __name__ == '__main__':
    main()

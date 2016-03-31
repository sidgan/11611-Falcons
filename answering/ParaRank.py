# -*- coding: utf-8 -*-

import nltk as nl
import sys
import re, string
import math
import operator
import nltk
from nltk.tag import pos_tag, map_tag
from textblob import TextBlob
from collections import defaultdict
from collections import Counter
from pprint import pprint


def main(argv=None):
    if argv is None:
        argv = sys.argv

    articlePath = '../data/a1.txt'
    question = u"When was Dempsey born ?"

    with open(articlePath, 'r') as file:
        paras = file.readlines()

    paras = process_text(paras)

    paras = ' . '.join(paras)

    # nltk.download()

    # Remvoe Stop Words from Query and Article
    curr_article = Article(paras.decode('utf-8'))

    # blob = TextBlob("Hello World ! I am Avnishs",ap_tagger)

    # nltk.download()
    # print nltk.word_tokenize("Hello World!, my name is Avnish!")
    # posTagged = nltk.pos_tag(nltk.word_tokenize("Hello World!, my name is Avnish!"))
    # print posTagged
    # simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]
    # print(simplifiedTags)

    # print bm25_ranker(curr_article,question,1.2,0.75,0,10)
    print cos_similarity_ranker(curr_article, question, 10)


def process_text(sentences):
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


######### CHANGE ###############
WORD = re.compile(r'\w+')


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


if __name__ == '__main__':
    main()

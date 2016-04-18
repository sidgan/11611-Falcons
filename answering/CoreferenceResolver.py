from math import *
from Commons import *

__author__ = 'avnishs'

noun_dict = dict()


def resolve_coreference(para):
    """
    Resolves entity co-reference between pronouns and nouns

    :param para: Paragraph to be resolved
    :param nlp: spacy NLP processor
    :return: paragraph as a string with resolved entities
    """
    idx = 0
    
    res_list = list()

    for sentence in para:
        result = ''
        terms = nlp(u"{}".format(sentence))
        for term in terms:
            if len(str(term).strip()) == 0:
                continue

            tag = term.tag_
            if tag.startswith("NN"):
                noun_dict[term] = idx
                result += str(term)
            elif tag.startswith("PRP"):
                max_sim = 0.0
                best_term = None
                for (noun, pos) in noun_dict.iteritems():
                    sim = similarity(term, noun, idx, pos)
                    if sim > max_sim:
                        max_sim = sim
                        best_term = noun
                result += str(best_term)
                noun_dict[best_term] = idx
            else:
                result += str(term)

            result += " "
            idx += 1
        res_list.append(result)    

    return res_list


def normpdf(x, mu, sigma):
    """
    Computes the pdf of normal distribution at x, centered at mu and scaled by sigma
    (Runs faster than scipy implementation!)

    :param x: 1-D data point
    :param mu: mean/center of the normal distribution
    :param sigma: variance/scale of the normal distribution
    :return: pdf of normal distribution at x
    """
    u = (x - mu) / abs(sigma)
    y = (1 / (sqrt(2 * pi) * abs(sigma))) * exp(-u * u / 2)
    return y


def custompdf(noun_pos,  pro_pos):
    sigmoid = 1 / float(1 + exp(noun_pos - pro_pos))
    min_component = 0.5 * (pro_pos - noun_pos)
    return min((sigmoid + min_component) / float(2), sigmoid)
    
def similarity(pronoun, noun, idx, noun_pos):
    """
    Computes similarity score between pronoun and noun

    :param pronoun: pronoun to be resolved
    :param noun: noun as resolution candidate
    :param idx: index of the pronoun
    :param noun_pos: position of the noun candidate
    :return: similarity score based on combination of word2vec and normal distribution fit
    """
    mean = (idx - 15) / float(2)
    score = noun.similarity(pronoun) + normpdf(noun_pos, mean, (idx - mean) * 0.68)
    return score

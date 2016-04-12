from math import *

__author__ = 'avnishs'

noun_dict = dict()


def resolve_coreference(para, nlp):
    """
    Resolves entity co-reference between pronouns and nouns

    :param para: Paragraph to be resolved
    :param nlp: spacy NLP processor
    :return: paragraph as a string with resolved entities
    """
    terms = nlp(u"{}".format(para))
    idx = 0
    result = ''

    for term in terms:
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

    return result


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
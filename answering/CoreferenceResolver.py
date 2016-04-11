from math import *

__author__ = 'avnishs'

noun_dict = dict()


def resolve_coreference(para, nlp):
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
    u = (x - mu) / abs(sigma)
    y = (1 / (sqrt(2 * pi) * abs(sigma))) * exp(-u * u / 2)
    return y


def similarity(pronoun, noun, idx, noun_pos):
    mean = (idx - 15) / float(2)
    score = noun.similarity(pronoun) + normpdf(noun_pos, mean, (idx - mean) * 0.68)
    return score

    # print resolve_coreference("Ophiuchus is located between Aquila , Serpens and Hercules , northwest of the center of the "
    # "Milky Way . The southern part lies between Scorpius to the west and Sagittarius to the east . "
    #                           "In the northern hemisphere , it is best visible in summer .")

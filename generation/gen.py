import re

from nltk.tree import Tree
from nltk.stem.wordnet import WordNetLemmatizer
import calendar
from SupersenseTagger import proc

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

WHO_PRONOUNS=set(["i", "he", "she", "you", "we", "they"])
WHO_TAGS=set(["noun.person", "noun.group"])
WHAT_PRONOUNS=set(["it", "this", "that"])
WHAT_TAGS=set(["noun.Tops","noun.act","noun.animal","noun.artifact","noun.attribute","noun.body","noun.cognition","noun.communication","noun.event","noun.feeling","noun.food","noun.group","noun.location","noun.motive","noun.object","noun.other","noun.phenomenon","noun.plant","noun.possession","noun.process","noun.quantity","noun.relation","noun.shape","noun.state","noun.substance"])
VERB_PAST='VBD'
VERB_PRESENT='VBP'
VERB_FUTURE='VB'
DAYS_MONTHS=[name.lower() for name in calendar.day_name[:] + calendar.month_name[1:] + ["a.m", "p.m"]]
LOCATION_TIME_PP=["in", "on", "over", "at", "during"]

lemmatizer = WordNetLemmatizer()

def get_wh_word(ner_tagger, np_tree):
    #tags = ner_tagger.tag(np_tree.leaves())
    tags = proc.tag(" ".join(np_tree.leaves()))
    #TODO: Apply WH word logic
    for num, word in enumerate(np_tree.leaves()):
        if tags[num] in WHO_TAGS or word in WHO_PRONOUNS:
            return "Who"
        if tags[num] in WHAT_TAGS or word in WHAT_PRONOUNS:
            return "What"
    return "What"

def apply_subject_rule(sentence, ner_tagger):
    s = sentence[0]
    if s[0].label() == "NP" and s[1].label() == "VP":
        wh_word = get_wh_word(ner_tagger, s[0])
        question =  wh_word + " " +  " ".join(s[1].flatten()) + "?"
        return [(question, wh_word.lower())]
    return []


def check_location(tree, count, curr_count = 0):
    for child in tree:
        if type(child) == Tree:
            for grandchild in child:
                if type(grandchild) == Tree and grandchild.label() == "PP" and grandchild[0,0] in LOCATION_TIME_PP:
                    curr_count += 1
                    if curr_count > count:
                        return grandchild
            location_tree = check_location(child, count, curr_count)
            if location_tree != None:
                return location_tree
    return None

def get_verb_form(label):
    if label == VERB_PAST:
        verb = "did"
    elif label == VERB_PRESENT:
        verb = "will"
    else:
        verb = "does"
    return verb

def get_tense_root(tree):
    verb = get_verb_form(tree[0].label())
    verb_root = lemmatizer.lemmatize(tree[0].leaves()[0], u'v')
    tree.remove(tree[0])
    tree.insert(0, Tree('Inserted', [verb_root]))
    return verb

def get_wh_word_location_time(location_tree):
    for word in location_tree.leaves():
        if word in DAYS_MONTHS or re.match(r'[1-2][0-9][0-9][0-9]\b', word):
            return "When"
    return "Where"

def remove_location(tree, location_tree):
    if tree.count(location_tree) > 0:
        tree.remove(location_tree)
        return get_wh_word_location_time(location_tree), get_verb_form(tree)
    else:
        for child in tree:
            if type(child) == Tree:
                wh_word, verb = remove_location(child, location_tree)
                if wh_word != None:
                    return wh_word, verb
        return None, None

def apply_location_rule(orig_sentence):
    sentence = orig_sentence.copy(deep=True)
    location_tree = check_location(sentence, 0)
    count = 1
    while location_tree != None:
        wh_word, verb = remove_location(sentence, location_tree)
        #print_sent = [wh_word, verb] + sentence.leaves()
        #print " ".join(print_sent)
        count += 1
        sentence = orig_sentence.copy(deep=True)
        location_tree = check_location(sentence, count)
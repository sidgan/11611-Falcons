import os
from nltk.parse import stanford
from nltk.tag import StanfordNERTagger
from nltk.tree import Tree
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
import calendar

PROJECT_HOME='/home/deepak/Downloads/NLP/project'
PARSER_PATH=os.path.join(PROJECT_HOME, 'stanford-parser-full-2015-04-20')
NER_PATH=os.path.join(PROJECT_HOME, 'stanford-ner-2015-04-20')
PARSER_MODEL_PATH=os.path.join(PARSER_PATH, 'stanford-parser-3.5.2-models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')
NER_MODEL_PATH=os.path.join(NER_PATH, 'classifiers/english.all.3class.distsim.crf.ser.gz')
DELIMITERS=" "
WHO_PRONOUNS=set(["i", "he", "she", "you", "we", "they"])
WHAT_PRONOUNS=set(["it", "this", "that"])
VERB_PAST='VBD'
VERB_PRESENT='VBP'
VERB_FUTURE='VB'
DAYS_MONTHS=[name.lower() for name in calendar.day_name[:] + calendar.month_name[1:] + ["a.m", "p.m"]]
LOCATION_TIME_PP=["in", "on", "over", "at"]

os.environ['STANFORD_PARSER'] = PARSER_PATH
os.environ['STANFORD_MODELS'] = PARSER_PATH
os.environ['CLASSPATH'] = PARSER_PATH + ':' + NER_PATH

s = ["The boy is playing with a ball.", "Sachin won an award.", "I was born on a Tuesday", "Manchester United played on a Monday in Pittsburgh", "Why Did You Put Up That Banner When We Won 4 Nil?"]
parser = stanford.StanfordParser(model_path=PARSER_MODEL_PATH)
ner_tagger = StanfordNERTagger(NER_MODEL_PATH)
lemmatizer = WordNetLemmatizer()

sentences = parser.raw_parse_sents((s[:]))
#tags = [ner_tagger.tag(sentence.split(DELIMITERS)) for sentence in s]

def get_wh_word(np_tree):
    tags = ner_tagger.tag(np_tree.leaves())
    #TODO: Apply WH word logic
    for num, word in enumerate(np_tree.leaves()):
        if tags[num][1] == "PERSON" or tags[num][1] == "ORGANIZATION" or word in WHO_PRONOUNS:
            return "Who"
        if word in WHAT_PRONOUNS:
            return "What"
    return "What"


def apply_naive_rule(sentence):
    s = sentence[0]
    if s[0].label() == "NP" and s[1].label() == "VP":
        print get_wh_word(s[0]) + " " +  " ".join(s[1].flatten())


def check_location(tree, count, curr_count = 0):
    for child in tree:
        if type(child) == Tree:
            for grandchild in child:
                if type(grandchild) == Tree and grandchild.label() == "PP" and grandchild[0,0].lower() in LOCATION_TIME_PP:
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
    verb_root = lemmatizer.lemmatize(tree[0].leaves()[0], wn.VERB)
    tree.remove(tree[0])
    tree.insert(0, Tree('Inserted', [verb_root]))
    return verb


def get_wh_word_location_time(location_tree):
    for word in location_tree.leaves():
        if word.lower() in DAYS_MONTHS:
            return "when"
    return "where"



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
    sentence = orig_sentence.copy()
    location_tree = check_location(sentence, 0)
    count = 1
    while location_tree != None:
        wh_word, verb = remove_location(sentence, location_tree)
        print_sent = [wh_word, verb] + sentence.leaves()
        print " ".join(print_sent)
        count += 1
        sentence = orig_sentence.copy()
        location_tree = check_location(sentence, count)

for line in sentences:
    for sentence in line:
        apply_location_rule(sentence)
        apply_naive_rule(sentence)

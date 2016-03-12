import os
from nltk.parse import stanford
from nltk.tag import StanfordNERTagger

PROJECT_HOME='/home/deepak/Downloads/NLP/project'
PARSER_PATH=os.path.join(PROJECT_HOME, 'stanford-parser-full-2015-04-20')
NER_PATH=os.path.join(PROJECT_HOME, 'stanford-ner-2015-04-20')
PARSER_MODEL_PATH=os.path.join(PARSER_PATH, 'stanford-parser-3.6.0-models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')
NER_MODEL_PATH=os.path.join(NER_PATH, 'classifiers/english.all.3class.distsim.crf.ser.gz')
DELIMITERS=" "

os.environ['STANFORD_PARSER'] = PARSER_PATH
os.environ['STANFORD_MODELS'] = PARSER_PATH
os.environ['CLASSPATH'] = PARSER_PATH + ':' + NER_PATH

s = ["The boy is playing with a ball.", "The teacher won an award.", "I was born on a Tuesday", "He played in Pittsburgh", "Why Did You Put Up That Banner When We Won 4 Nil?"]

parser = stanford.StanfordParser(model_path=PARSER_MODEL_PATH)
st = StanfordNERTagger(NER_MODEL_PATH)

sentences = parser.raw_parse_sents((s[:]))
tags = [st.tag(sentence.split(DELIMITERS)) for sentence in s]


def get_wh_word(sentence, np_tree):
    #TODO: Apply WH word logic
    return "WH"


def apply_naive_rule(sentence):
    s = sentence[0]
    if s[0].label() == "NP" and s[1].label() == "VP":
        return True, get_wh_word(sentence, s[0]), " ".join(s[1].flatten())
    else:
        return False, None, None


for line,tag in zip(sentences, tags):
    for sentence in line:
        print tag
        isNaive, wh, sent = apply_naive_rule(sentence)
        if isNaive:
            print wh + " " + sent
        else:
            sentence.draw()



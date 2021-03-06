import os
import random
import sys
from nltk.parse import stanford
import re
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import StanfordNERTagger
from collections import Counter
import unicodedata
import FactualStatementExtractor.proc as proc
from itertools import chain
from textblob import TextBlob
import gen
import time
from subprocess import Popen, PIPE, STDOUT
import helper
import ranker

PROJECT_HOME='/home/deepak/Downloads/NLP/project'
PARSER_PATH=os.path.join(PROJECT_HOME, 'stanford-parser-full-2015-04-20')
NER_PATH=os.path.join(PROJECT_HOME, 'stanford-ner-2015-04-20')
PARSER_MODEL_PATH=os.path.join(PARSER_PATH, 'stanford-parser-3.5.2-models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')
#NER_MODEL_PATH=os.path.join(NER_PATH, 'classifiers/english.all.3class.distsim.crf.ser.gz')
NER_MODEL_PATH=os.path.join(NER_PATH, 'classifiers/english.conll.4class.distsim.crf.ser.gz')

'''
#Loading tools on DEV
os.environ['STANFORD_PARSER'] = PARSER_PATH
os.environ['STANFORD_MODELS'] = PARSER_PATH
os.environ['CLASSPATH'] = PARSER_PATH + ':' + NER_PATH
parser = stanford.StanfordParser(model_path=PARSER_MODEL_PATH)
ner_tagger = StanfordNERTagger(NER_MODEL_PATH)
#END
'''
#Loading tools on PROD
stanford_path = os.environ["CORENLP_3_5_2_PATH"]
parser = stanford.StanfordParser(os.path.join(stanford_path, "stanford-corenlp-3.5.2.jar"),
                        os.path.join(stanford_path, "stanford-corenlp-3.5.2-models.jar"))
ner_tagger = StanfordNERTagger(os.path.join(stanford_path, "models/edu/stanford/nlp/models/ner/english.all.3class.distsim.crf.ser.gz"), \
                       os.path.join(stanford_path, "stanford-corenlp-3.5.2.jar"))
#END


lemmatizer = WordNetLemmatizer()

AUXILLARIES = set(['is','am','are','was','were','can','could','shall','should','may','might','will','would','has','have','did'])
YES_NO_TYPE="yes_no"


#checks if the question has a pronoun as the subject. If true, it replaces the pronoun with the most common named 
#entity in the paragraph from where the question was generated 

def get_MostFrequent_NE(paragraph):
    
    tagged = ner_tagger.tag(paragraph.split())
    #print tagged
    named_entities  = Counter(tagged)
    #print named_entities
    
    #get the most common named entity in this paragraph 
    while(len(named_entities)>0):
        e = named_entities.most_common(1)
        key = e[0][0]
        if key[1] == 'O':
            named_entities.pop(key)
            continue
        else: 
            break
    
    if len(named_entities)==0:
        return ""
    
    most_frequent_NE = key[0]
    
    return most_frequent_NE

def post_process(question,pronoun,most_frequent_NE):
    pronoun = pronoun.lower()
    question = question.replace(pronoun,most_frequent_NE,1)
    return question

#function to produce better no questions using wordnet hypernyms and hyponyms
''' 
def create_no_question(question):
    
    tagged = ner_tagger.tag(question.split())
    #print tagged

    for t in list(tagged):
        if t[1]== u'O':tagged.remove(t)
    
    #named_entities  = Counter(tagged)
    
    synonyms = []
    antonyms = []

    for syn in wordnet.synsets("language", 'n'):
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    
    syns = wordnet.synsets('English')
    
    print synonyms
    
    #print tagged
    return question
'''
    
def yes_no_rule_helper(sentence,verb,base_verb,label,negative=False):
    
    #remove the auxillary verb
    if negative:
        question = sentence.replace(" "+verb," not "+base_verb,1)
    else:
        question = sentence.replace(" "+verb," "+base_verb,1)
        
    question = re.sub(' +',' ',question)
    
    question = question.replace("not not "," ")    
    #remove the extra white space left behind after removing the auxillary verb
    question = re.sub(' +',' ',question)
    #convert the first letter to lower case
    question = question[0].lower()+question[1:]
    #append the auxillary at the beginning after its case conversion to title
    if label=='AUX':
        question = verb.title()+" "+question+"?"
    elif label=='VBD':
        question = 'Did'+" "+question+"?"
    else:
        question = 'Does'+" "+question+"?"

    #create_no_question(question)
    #question = post_process(question)
    
    return question

def apply_auxillary_rule(sentence,verb):
    
    q1 = yes_no_rule_helper(sentence,verb,"",'AUX')
    q2 = yes_no_rule_helper(sentence,verb,"", 'AUX',True)
    
    return [q1,q2]

def apply_tense_rule(sentence,verb,label):
    
    base_verb = lemmatizer.lemmatize(verb, 'v')
    
    q1 = yes_no_rule_helper(sentence,verb,base_verb,label)
    q2 = yes_no_rule_helper(sentence,verb,base_verb,label,True)
    
    return [q1,q2]


def generate_when_where(root, ner_tagger):
    return gen.apply_location_rule(root)

def generate_question(sentences):
    #most_frequent_NE = get_MostFrequent_NE(data)
    #print most_frequent_NE
    #sentences =  sent_tokenize(data)
    questions = []
    for sentence in sentences:
        sentence = sentence.rstrip(".")
        if len(sentence.split()) > 12 or len(sentence.split()) < 4:
            #print sentence+"...Sentence not usable!!"
            continue
        parseTree = parser.raw_parse(sentence)
        #root is the root node in the parse tree
        root = parseTree.next()
        if helper.isPronounResolved(root)==False:
            continue
        #print sentence
        questions.extend(generate_yes_no(root, sentence))
        questions.extend(generate_who_what(root, ner_tagger))
        #questions.extend(generate_when_where(root))
    return questions

def generate_who_what(root, ner_tagger):
    return gen.apply_subject_rule(root, ner_tagger)

def generate_yes_no(root, sentence):
    S = root[0]
    questions = []

    #only use those sentences that have NP, VP structure at the top
    if not(len(root)>0 and len(S)>1 and S[0].label()=='NP' and S[1].label()=='VP'):
        return []

    node = root[0][1][0]
    label = node.label()
    verb = node[0]

    if not(type(verb) is unicode and label.startswith('VB')) :
        return []

    if verb in AUXILLARIES:
        q = apply_auxillary_rule(sentence,verb)
    else:
        q = apply_tense_rule(sentence,verb,label)

    '''
    #post_processing involves resolving the pronoun with the most common named entity in the same paragraph
    subject = S[0][0]
    if subject.label()=='PRP':

        q[0] = post_process(q[0],subject[0],most_frequent_NE)
        q[1] = post_process(q[1],subject[0],most_frequent_NE)
    '''
    if random.random() > 0.25:
        questions.append((q[0], YES_NO_TYPE))
    else:
        questions.append((q[1], YES_NO_TYPE))

    return questions

def simplify(sentences):
    return proc.simplify(sentences)
        
def process_article_file(filename, nquestions):
    nquestions = int(nquestions)
    bracket_regex = r'\([^)]*\)'
    questions = []
    try:
        os.system("kill -9 $(lsof -i:5556 -t) >/dev/null 2>&1")
        FNULL = open(os.devnull, 'w')
        server = Popen("sh runStanfordParserServer.sh".split(), cwd="question-dir/11611-Falcons/generation/FactualStatementExtractor", stdout=FNULL, stderr=STDOUT)
        time.sleep(12)
        with open(filename, 'r') as article:
            for line in article:
                sentences = []
                cleaned = unicodedata.normalize('NFKD', line.decode('utf-8').strip()).encode('ASCII', 'ignore')
                cleaned = re.sub(bracket_regex,'',cleaned)
                sentences.extend([str(sent) for sent in TextBlob(cleaned).sentences if len(sent.tokens) > 4 and len(sent.tokens) < 20])
                sentences = simplify(". ".join(sentences))
                if sentences is None:
                    continue
                questions.extend(generate_question(sentences))
                #print len(questions)
                if len(questions) > nquestions * 3:
                    break
            questions_ranked = ranker.rank(questions, nquestions)
            random.shuffle(questions_ranked)
            print "\n".join(questions_ranked)
        os.system("kill -9 $(lsof -i:5556 -t) >/dev/null 2>&1")

    except:
        os.system("kill -9 $(lsof -i:5556 -t) >/dev/null 2>&1")
        print sys.exc_info()[0]
        for question in questions[:nquestions]:
            print question[0]

if __name__=="__main__":process_article_file('question-dir/11611-Falcons/generation/a2.txt', 10)

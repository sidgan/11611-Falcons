import os
from nltk.parse import stanford
from nltk.tree import Tree
from sets import Set
import re
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import StanfordNERTagger
from collections import Counter
from nltk.tokenize import sent_tokenize
from nltk.corpus import wordnet
import unicodedata
import FactualStatementExtractor.proc as proc
from itertools import chain
from textblob import TextBlob
import gen

PROJECT_HOME='/home/deepak/Downloads/NLP/project'
PARSER_PATH=os.path.join(PROJECT_HOME, 'stanford-parser-full-2015-04-20')
NER_PATH=os.path.join(PROJECT_HOME, 'stanford-ner-2015-04-20')
PARSER_MODEL_PATH=os.path.join(PARSER_PATH, 'stanford-parser-3.5.2-models/edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz')
#NER_MODEL_PATH=os.path.join(NER_PATH, 'classifiers/english.all.3class.distsim.crf.ser.gz')
NER_MODEL_PATH=os.path.join(NER_PATH, 'classifiers/english.conll.4class.distsim.crf.ser.gz')

os.environ['STANFORD_PARSER'] = PARSER_PATH
os.environ['STANFORD_MODELS'] = PARSER_PATH
os.environ['CLASSPATH'] = PARSER_PATH + ':' + NER_PATH

parser = stanford.StanfordParser(model_path=PARSER_MODEL_PATH)
ner_tagger = StanfordNERTagger(NER_MODEL_PATH)
lemmatizer = WordNetLemmatizer()

AUXILLARIES = Set(['is','am','are','was','were','can','could','shall','should','may','might','will','would','has','have','did'])


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
    
    #print question
    
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

def generate_question(sentences):
    #most_frequent_NE = get_MostFrequent_NE(data)
    #print most_frequent_NE
    #sentences =  sent_tokenize(data)
    questions = []
    for sentence in sentences:
        print sentence
        if len(sentence.split()) > 12 or len(sentence.split()) < 4:
            #print sentence+"...Sentence not usable!!"
            continue
        parseTree = parser.raw_parse(sentence)
        #root is the root node in the parse tree
        root = parseTree.next()

        questions.extend(generate_yes_no(root, sentence))
        questions.extend(generate_who_what(root, ner_tagger))
    

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

    questions.append(q[0])
    questions.append(q[1])
    print q[0]
    print q[1]

    return questions

def simplify(sentences):
    return proc.simplify(sentences)
        
def process_article_file(filename):    
    bracket_regex = r'\([^)]*\)'
    sentences = []
    with open(filename, 'r') as article:
        for line in article:
            cleaned = unicodedata.normalize('NFKD', line.decode('utf-8').strip()).encode('ASCII', 'ignore')
            cleaned = re.sub(bracket_regex,'',cleaned)
            sentences.extend([str(sent) for sent in TextBlob(cleaned).sentences])
        sentences = simplify(". ".join(sentences))
        generate_question(sentences)
    #sentences = filter(lambda sent: (len(sent.word_counts) > 3) and '.' in sent.tokens,
    #                   list(chain.from_iterable(result)))

#readData('testSample.txt')

process_article_file('a1small.txt')


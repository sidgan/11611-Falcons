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

PROJECT_HOME='/Users/sanchitagarwal/Desktop/11611-NLP/Project/'
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

#takes data corresponding to a paragraph
def generate_question(data):
    
    most_frequent_NE = get_MostFrequent_NE(data)
    
    sentences =  sent_tokenize(data)
    
    #sentences = data.split('. ')
    
    questions = []
    
    for sentence in sentences:
    
        print sentence
        print ''
        if len(sentence.split())<3:
            print sentence+"...Sentence not usable!!"
            continue
    
        parseTree = parser.raw_parse(sentence)
    
        #root is the root node in the parse tree
    
        for node in parseTree:
            root = node
            
        #print root
    
        S = root[0]
    
        #only use those sentences that have NP, VP structure at the top
        if not(len(root)>0 and len(S)>1 and S[0].label()=='NP' and S[1].label()=='VP'):
            continue
    
        node = root[0][1][0]
    
        label = node.label()
        verb = node[0]
        
        #print type(verb)
    
        if not(type(verb) is unicode and label.startswith('VB')) :
            continue
    
        if verb in AUXILLARIES:
            q = apply_auxillary_rule(sentence,verb)
        else:
            q = apply_tense_rule(sentence,verb,label)
            
        
        subject = S[0][0]
        
        #post_processing involves resolving the pronoun with the most common named entity in the same paragraph
        if subject.label()=='PRP':
            
            q[0] = post_process(q[0],subject[0],most_frequent_NE)
            q[1] = post_process(q[1],subject[0],most_frequent_NE)
    
        questions.append(q[0])
        questions.append(q[1])
        
        print q[0]
        print q[1]
        
        print ''
        
    #for q in questions:
    #    print q+'\n'
            
        
#read data one paragraph at a time and use it to generate questions
def readData(inputFile):
    
    with open(inputFile,'r') as f:
        data = f.read()
        
    data = data.decode('unicode_escape').encode('ascii','ignore')
    #re.sub(r'[^\x00-\x7f]+',r' ',data)
    #data = re.sub(' +',' ',data)    
    
    #print data
    
    generate_question(data)
        

sentence = 'English is a West Germanic language that was first spoken in early medieval England and is now a global lingua franca'
sentence1 = 'The boy is playing with the ball'
sentence2 = 'The boy played with the ball'
sentence3 = 'The boy plays with the ball'
sentence4 = 'The boy plays'
sentence5 = 'The boy can do the work'
sentence6 = 'He is a great person'
sentence7 = 'He will do the work'
sentence8 = 'The book was bought by John'
sentence9 = 'He did not solve the problem'
sentence10 = 'Francisco gives swimming all of his energy and time'

#auxillary_rule fails here, need to handle this corner case
sentence11 = 'He did the work'

'''
generate_question(sentence1)
generate_question(sentence2)
generate_question(sentence3)
generate_question(sentence4)
generate_question(sentence5)
generate_question(sentence6)
generate_question(sentence7)
generate_question(sentence8)
generate_question(sentence9)

'''
#s = 'He is doing the work'
#generate_question(s)

readData('testSample.txt')


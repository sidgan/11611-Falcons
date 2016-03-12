import nltk
from nltk.corpus import treebank

from nltk.parse.stanford import StanfordParser,StanfordDependencyParser

from nltk.tag import StanfordNERTagger
from nltk.tag.stanford import StanfordPOSTagger

sentence = "At eight o'clock on Thursday morning"


tokens = nltk.word_tokenize(sentence)
print tokens
tagged = nltk.pos_tag(tokens)
print tagged

pt = StanfordPOSTagger('english-bidirectional-distsim.tagger')
st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')

print pt.tag(tokens)  
print st.tag('Rami Eid is studying at Stony Brook University in NY'.split()) 


path_to_jar = '/Users/sanchitagarwal/Desktop/11611-NLP/Project/stanford-parser-full-2015-12-09/stanford-parser.jar'
path_to_models_jar = '/Users/sanchitagarwal/Desktop/11611-NLP/Project/stanford-parser-full-2015-12-09/stanford-parser-3.6.0-models.jar'

'''
parser = StanfordParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)

sentences = parser.raw_parse_sents(("Hello, My name is Melroy.", "What is your name?"))
#print sentences

for line in sentences:
    for sentence in line:
        sentence.draw()
'''
            
dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar,path_to_models_jar=path_to_models_jar)

result = dependency_parser.raw_parse('I shot an elephant in my sleep')

dep = result.next()
print list(dep.triples())


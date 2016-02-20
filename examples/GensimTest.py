from gensim.summarization import summarize
from gensim.summarization import keywords
import string
import sys
import re

with open(sys.argv[1]) as f:
    text = f.read().replace('\n','')

text = filter(lambda x: x in string.printable, text)

print 'Input text:'
print text

print '\nSummary:'
print summarize(text, ratio = 0.2) # summarize(text, ratio=0.5) or summarize(text, word_count=50)

print '\nKeywords:'
print keywords(text)

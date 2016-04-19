import shlex
from subprocess import PIPE, Popen
import subprocess
import os
import time

def simplify(sentences):
    try:
        p = Popen("java -Xmx1500m -cp factual-statement-extractor.jar:lib/jwnl.jar:lib/stanford-parser-2008-10-26.jar:lib/commons-logging.jar:lib/commons-lang.jar edu/cmu/ark/SentenceSimplifier".split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1, cwd="FactualStatementExtractor", timeout=10)
        answer = p.communicate(sentences)
        return answer[0].split("\n")
    except:
        return None

def main():
    print simplify("English is a West Germanic language that was first spoken in early medieval England and is now a global lingua franca. It is an official language of almost 60 sovereign states, the most commonly spoken language in the United Kingdom, the United States, Canada, Australia, Ireland, and New Zealand, and a widely spoken language in countries in the Caribbean, Africa, and South Asia. It is the third most common native language in the world, after Mandarin and Spanish. It is the most widely learned second language and is an official language of the United Nations, of the European Union, and of many other world and regional international organisations.")

if __name__=="__main__":main()
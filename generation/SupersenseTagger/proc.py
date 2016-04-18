import shlex
from subprocess import PIPE, Popen
import os
import time

def tag(sentence):
    #os.system("kill -9 $(lsof -i:5556 -t)")
    p = Popen("sh run.sh".split(),stdin=PIPE, stdout=PIPE)
    #time.sleep(15)
    #p = Popen("java -Xmx1500m -cp factual-statement-extractor.jar:lib/jwnl.jar:lib/stanford-parser-2008-10-26.jar:lib/commons-logging.jar:lib/commons-lang.jar edu/cmu/ark/SentenceSimplifier".split(), stdin=PIPE, stdout=PIPE, bufsize=1, cwd="FactualStatementExtractor")
    answer = p.communicate(sentence)
    #p.wait()
    #os.system("kill -9 $(lsof -i:5556 -t)")
    return answer[0].split("\n")
    
    #print answer

def main():
    print tag("English is a West Germanic language that was first spoken in early medieval England")

if __name__=="__main__":main()
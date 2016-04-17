from subprocess import PIPE, Popen
import os
import signal

#server = Popen("sh runStanfordParserServer.sh".split())
p = Popen("java -Xmx1500m -cp factual-statement-extractor.jar:lib/jwnl.jar:lib/stanford-parser-2008-10-26.jar:lib/commons-logging.jar:lib/commons-lang.jar edu/cmu/ark/SentenceSimplifier".split(), stdin=PIPE, stdout=PIPE, bufsize=1)
print "HERE"
p.stdin.write("Testing a sentence")
p.stdin.flush()
while p.poll() is None:
    #p.stdin.write("Testing a sentence")
    l = p.stdout.readline()
    print l
print p.stdout.read()
#os.killpg(os.getpgid(server.pid), signal.SIGTERM)

#/usr/bin/env bash

#java -Xmx1000m -server -cp factual-statement-extractor.jar:lib/stanford-parser-2008-10-26.jar edu.cmu.ark.StanfordParserServer config/englishPCFG.ser.gz -port 5556
java -Xmx1000m -cp factual-statement-extractor.jar:lib/stanford-parser-2008-10-26.jar edu.cmu.ark.StanfordParserServer config/englishFactored.ser.gz -port 5556




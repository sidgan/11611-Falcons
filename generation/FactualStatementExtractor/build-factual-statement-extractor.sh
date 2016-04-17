#!/usr/bin/env bash

TARGET=factual-statement-extractor.jar

set -eux

rm -rf build-fse
mkdir -p build-fse

javac -d build-fse \
 -cp lib/commons-lang-2.4.jar:lib/commons-logging.jar:lib/jwnl.jar:lib/stanford-parser-2008-10-26.jar \
 src/edu/cmu/ark/SentenceSimplifier.java \
 src/edu/cmu/ark/AnalysisUtilities.java \
 src/edu/cmu/ark/Question.java \
 src/edu/cmu/ark/VerbConjugator.java \
 src/edu/cmu/ark/TregexPatternFactory.java \
 src/edu/cmu/ark/GlobalProperties.java \
 src/edu/cmu/ark/ParseResult.java \
 src/edu/cmu/ark/StanfordParserServer.java

(cd build-fse && jar cf $TARGET edu)

mv build-fse/$TARGET $TARGET


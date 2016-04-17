Simple Factual Statement Extractor

Michael Heilman and Noah A. Smith
Language Technologies Institute
Carnegie Mellon University


This is a software package for extracting simplified factual 
statements from complex sentences
It was designed for the automatic factual question generation 
but may be useful for other natural language processing 
and generation problems (e.g., summarization).

Note: The code is packaged up for use on UNIX systems,
or for use in the Eclipse IDE.



Distribution website: 
http://www.ark.cs.cmu.edu/mheilman/qg-2010-workshop/

Authors' websites:
http://www.cs.cmu.edu/~mheilman
http://www.cs.cmu.edu/~nasmith




-------------------------
License

The software is distributed under the GNU license.  
See licenses/LICENSE.txt for details.
The system also includes the Stanford Parser, Tregex,
the Java WordNet Library (JWNL), WordNet, and the Apache commons libraries.
Licenses for those packages are in the subdirectory "licenses." 


------------------------
Unit Testing

A suite of JUnit tests is provided to ensure that the system is working properly. 
See TestSentenceSimplifier.java (under src/edu/cmu/ark).


-----------------------
Running the parsing server

Before running the program, you may want to 
start the socket server for the parser 
(if you do this, then the actual simplification program
will only require a small amount of memory).
If the socket server is running, then the system
will not load up the Stanford Parser, which takes 
a lot of time and memory.

To start the socket server, execute
runStanfordParserServer.sh

You can also change whether the Stanford Parser uses
a lexicalized (englishFactored.ser.gz, the default) 
or and unlexicalized grammar (englishPCFG.ser.gz).

To change what the socket server uses, modify
the runStanfordParserServer.sh script.

To change which grammar the system will load if the socket server is not running,
modify the parserGrammarFile property in 
config/factual-statement-extractor.properties.


-----------------------
Running the system

To run the program, execute the SentenceSimplifier program as follows.  
(Version 1.6.0_07 of the Sun JVM was used in developing the system.)

java -Xmx1500m -cp factual-statement-extractor.jar:lib/jwnl.jar:lib/stanford-parser-2008-10-26.jar:lib/commons-logging.jar:lib/commons-lang.jar edu/cmu/ark/SentenceSimplifier

(Note: "1500m" can be changed to "500m" if the parsing server is running.)

The system takes plain text input on standard input 
and prints plain text output on standard output.  
The command line options "-h", "--help", and "-help" 
will print a list of command line options. 
See src/edu/cmu/ark/SentenceSimplifier.java for further details. 

For convenience, there is also a script simplify.sh 
that simply calls the java command shown above.


-----------------------
Publication

The system is described further, along with experimental evaluation results,
in the following paper:

M. Heilman and N. A. Smith. 2010. Extracting Simplified Factual Statements for Question Generation.
In Proc. of the 3rd Workshop on Question Generation. 




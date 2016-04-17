package edu.cmu.ark;

import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.parser.lexparser.Options;
import edu.stanford.nlp.trees.*;
import edu.stanford.nlp.util.ScoredObject;

import java.io.*;

import java.net.*;
import java.util.List;
import java.util.Properties;

/**
 * Wrapper class to run the Stanford Parser as a socket server so the grammar need not
 * be loaded for every new sentence.
 * 
 * @author mheilman@cmu.edu
 *
 */
public class StanfordParserServer  {

	//@SuppressWarnings("unchecked")
	public static void main(String[] args) {

		//INITIALIZE PARSER
		String serializedInputFileOrUrl = null;
		int port = 5556;
		int maxLength = 40;
			
		// variables needed to process the files to be parse
		String sentenceDelimiter = null;
		int argIndex = 0;
		if (args.length < 1) {
			System.err.println("usage: java edu.stanford.nlp.parser.lexparser." + "LexicalizedParser parserFileOrUrl filename*");
			System.exit(1);
		}

		Options op = new Options();
		// while loop through option arguments
		while (argIndex < args.length && args[argIndex].charAt(0) == '-') {
			if (args[argIndex].equalsIgnoreCase("-sentences")) {
				sentenceDelimiter = args[argIndex + 1];
				if (sentenceDelimiter.equalsIgnoreCase("newline")) {
					sentenceDelimiter = "\n";
				}
				argIndex += 2;
			} else if (args[argIndex].equalsIgnoreCase("-loadFromSerializedFile")) {
				// load the parser from a binary serialized file
				// the next argument must be the path to the parser file
				serializedInputFileOrUrl = args[argIndex + 1];
				argIndex += 2;
			} else if (args[argIndex].equalsIgnoreCase("-maxLength")) {
				maxLength = new Integer(args[argIndex + 1]);
				argIndex += 2;
			} else if (args[argIndex].equalsIgnoreCase("-port")) {
				port = new Integer(args[argIndex + 1]);
				argIndex += 2;
			} else {
				argIndex = op.setOptionOrWarn(args, argIndex);
			}
		} // end while loop through arguments

		LexicalizedParser lp = null;
		// so we load a serialized parser
		if (serializedInputFileOrUrl == null && argIndex < args.length) {
			// the next argument must be the path to the serialized parser
			serializedInputFileOrUrl = args[argIndex];
			argIndex++;
		}
		if (serializedInputFileOrUrl == null) {
			System.err.println("No grammar specified, exiting...");
			System.exit(0);
		}
		try {
			lp = new LexicalizedParser(serializedInputFileOrUrl, op);
		} catch (IllegalArgumentException e) {
			System.err.println("Error loading parser, exiting...");
			System.exit(0);
		}
		lp.setMaxLength(maxLength);
		lp.setOptionFlags("-outputFormat", "oneline");
		
		// declare a server socket and a client socket for the server
		// declare an input and an output stream
		ServerSocket parseServer = null;
		BufferedReader br;
		PrintWriter outputWriter;
		Socket clientSocket = null;
		try {
			parseServer = new ServerSocket(port);
		}
		catch (IOException e) {
			System.err.println(e);
		} 

		// Create a socket object from the ServerSocket to listen and accept 
		// connections.
		// Open input and output streams

		while (true) {
			System.err.println("Waiting for Connection on Port: "+port);
			try {
				clientSocket = parseServer.accept();
				System.err.println("Connection Accepted From: "+clientSocket.getInetAddress());
				br = new BufferedReader(new InputStreamReader(new DataInputStream(clientSocket.getInputStream())));
				outputWriter = new PrintWriter(new PrintStream(clientSocket.getOutputStream()));

				String doc = "";

				do{
					doc += br.readLine();
				}while(br.ready());
				System.err.println("received: " + doc);
				
				//PARSE
				try{
					lp.parse(doc);
					
					//OUTPUT RESULT
					Tree bestParse = lp.getBestParse();
					TreePrint tp = lp.getTreePrint();
					tp.printTree(bestParse, outputWriter);
					outputWriter.println(lp.getPCFGScore());
					//String output = bestParse.toString();
					//outputWriter.println(output);
					//System.err.println("sent: " + output);
						
					int k=5;
					System.err.println("best factored parse:\n"+lp.getBestParse().toString());
					System.err.println("k-best PCFG parses:");
					List<ScoredObject<Tree>> kbest = lp.getKBestPCFGParses(k);
					for(int i=0; i<kbest.size(); i++){
						System.err.println(kbest.get(i).object().toString());
					}
					
				}catch(Exception e){
					outputWriter.println("(ROOT (. .))");
					outputWriter.println("-999999999.0");
					e.printStackTrace();
				}
				
				outputWriter.flush();
				outputWriter.close();

			}catch (IOException e) {
				e.printStackTrace();
			}
		}
	}

}


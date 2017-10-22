#!/usr/bin/env python

# Test harness for reading fonts from the filesystem and serving them to a web browser
# james.fell@alumni.york.ac.uk


import os
import sys
from twisted.internet import reactor, endpoints
from twisted.web.server import Site
from twisted.web.resource import Resource


# Read and sanity check all the command line arguments from the user
def readArgs():

	# Check the correct number of arguments have been supplied
	if (len(sys.argv) != 3):
		print "Test harness for reading fonts from disk and serving them to a web browser."
		print "Usage: harness.py directory port"
		exit()

	# Get directory to read the corpus from.
	corpusInDir = sys.argv[1]

	# Check that the input directory exists.
	if (os.path.isdir(corpusInDir) == False):
		print "Error: Directory does not exist", corpusInDir
		exit()

	# Get the TCP port on localhost that the test harness should listen on
	try: 
		listenPort = int(sys.argv[2])
	except ValueError:
		print "Error: Second argument must be an integer."
		exit()

	# Check that it is a valid port number, assume non-root user
	if ((listenPort < 1024) or (listenPort > 65535)):
		print "Error: TCP port should be between 1024 and 65535."
		exit()

	return corpusInDir, listenPort



# Code to execute whenever the HTTP server receives a request from a web browser
class FuzzPage(Resource):

	isLeaf = True

	# Handle GET requests
	def render_GET(self, request):

		global testCaseCounter, testCases, logFilename

		# If the GET request is for the web root
		if (request.uri == '/'):
			
			# If we have reached the end of the corpus, return a message stating this
			if (testCaseCounter >= len(testCases)):
				print "Finished."
				return """
				<html>
				<head>
				<title>All done!</title>
				</head>
				<body>
				<p>Finished!</p>
				</body>
				</html>
				"""

			# Otherwise generate the HTML and CSS to return to the web browser
			else:
				fuzzPage = """
				<html>
				<head>
				<meta http-equiv="refresh" content="1">
				<meta http-equiv="cache-control" content="no-cache">
				<title>Font fuzzing</title>
				<style>
				@font-face {
	    				font-family: 'fuzzFont';
					src: url(/font""" + str(testCaseCounter) + """);
				}
				body {
	  				font-family: 'fuzzFont';
				}
				</style>
				</head>
				<body>
				<p>Testing a font</p>
				</body>
				</html>
				"""

				# Append the filename of the current test case to the log file to track our progress
				f = open(logFilename, 'a')
				f.write(testCases[testCaseCounter] + '\n')
				f.close

				# Increment the test case counter
				testCaseCounter += 1

				# Return the web page to the web server to be fed to the browser
				return fuzzPage

		# If the GET request is for the font file
		elif 'font' in request.uri:
		
			# If we have reached the end of the corpus, return an empty string
			if (testCaseCounter >= len(testCases)):
				return ""

			# Otherwise read the next font file from disk and return its contents
			else:
				f = open(testCases[testCaseCounter], 'r')
				fontFileContent = f.read()
				f.close()

				# Return the font data to be fed to the browser
				return fontFileContent

		# If the GET request is for anything else return an empty string
		else:
			return ""


# Spin up a HTTP server on localhost
def startFuzzServer(listenPort):
	print "Starting HTTP Server. Please point the web browser to be tested at http://127.0.0.1:" + str(listenPort)
	resource = FuzzPage()
	factory = Site(resource)
	endpoint = endpoints.TCP4ServerEndpoint(reactor, listenPort)
	endpoint.listen(factory)
	reactor.run()
	return 0



# Recurse through the corpus directory and any subdirectories building a list of all the files
def scanCorpus(corpusInDir):
	filesList = []
	for subdir, dirs, files in os.walk(corpusInDir):
		for file in files:
		        filesList.append(os.path.join(subdir, file))
	print "Found", str(len(filesList)), "files in corpus"
	return filesList


def startup():

	global testCaseCounter, testCases, logFilename

	# Read command line arguments from user
	corpusInDir, listenPort = readArgs()

	# Set the filename of the log file and create the empty log file
	logFilename = 'fontharness-log-' + str(listenPort) + '.txt'
	f = open(logFilename, 'w')
	f.close

	# Initialise counter for number of test cases served so far
	testCaseCounter = 0

	# Read all test case file names into a list ready to process
	testCases = scanCorpus(corpusInDir)

	# Start up the web server and wait for a web browser to connect
	startFuzzServer(listenPort)



startup()





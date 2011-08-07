"""
Devcoin jury is a program to determine jury selection given a forum post time.

This is meant to be used by devcoin administrators to determine who will vote on an issue.


==Commands==
===Help===
The -h option or the -help option will print the help, which is this document.  The example follows:
python devcoinjury.py -h

===Input===
The -time option sets the Simple Machines Forum post time.  The example follows:
python devcoinjury.py -time 'August 06, 2011, 9:36:00 pm'

===Output===
The -output option sets the output.  If the output ends with stderr, the output will be sent to stderr  If the output ends with stdout or is empty, the output will be sent to stdout.  If the output does not end with stderr or stdout, the output will be written to a file by that name.  The example follows:
python almoner.py -time 'August 06, 2011, 9:36:00 pm' -output stdout


==Install==
For devcoinjury to run, you need Python 2.x, devcoinjury will probably not run with python 3.x.  To check if it is on your machine, in a terminal type:
python

If python 2.x is not on your machine, download the latest python 2.x, which is available from:
http://www.python.org/download/
"""

import cStringIO
import datetime
import hashlib
import math
import sys
import time


__license__ = 'AGPL'


globalBlockDelayTimeDelta = datetime.timedelta(hours = 2)


def addJuror(devcoinJurors, hashString):
	'Add a juror to the devcoin jury list.'
	numberOfRemainingJurors = 0
	for devcoinJuror in devcoinJurors:
		if devcoinJuror == None:
			numberOfRemainingJurors += 1
	if numberOfRemainingJurors == 0:
		print('Warning, there are no jurors left to add.')
		return
	addedIndex = int(math.floor(float(numberOfRemainingJurors) * getFloatHash(hashString)))
	numberOfRemainingJurors = 0
	for devcoinJurorIndex, devcoinJuror in enumerate(devcoinJurors):
		if devcoinJuror == None:
			if numberOfRemainingJurors == addedIndex:
				devcoinJurors[devcoinJurorIndex] = getFloatHash(hashString + 'extraString')
				return
			numberOfRemainingJurors += 1

def getBitcoinBlockHash(delayDateTime):
	'Get the hash of the first bitcoin block at or after the delayDateTime.'
	print(  'This stub output is using the block at:')
	print(  'http://abe.john-edwin-tobey.org/block/00000000000008b66a4e3b498fb8c96395e101aae664176ff5364ebf446da80f')
	print(  'Which was made at time:')
	print(  '2011-08-06 23:36:02')
	print(  'The input delayDatetime is:')
	print(  delayDateTime)
	return '00000000000008b66a4e3b498fb8c96395e101aae664176ff5364ebf446da80f'

def getDateTimeBySimpleMachinesForumString(postTimeString):
	'Get the datetime from the Simple Machines Forum post time stamp string.'
	postTimeStringSpaced = postTimeString.replace(',', ' ').replace(':', ' ')
	postTimeList = postTimeStringSpaced.split()
	postTimeStringFirstThree = ' '.join(postTimeList[: 3])
	postTimeTuple = time.strptime(postTimeStringFirstThree, '%B %d %Y')
	hour = int(postTimeList[3])
	if postTimeList[6].lower().startswith('p'):
		hour += 12
	minute = int(postTimeList[4])
	second = int(postTimeList[5])
	return datetime.datetime(postTimeTuple[0], postTimeTuple[1], postTimeTuple[2], hour, minute, second)

def getDevcoinJuryText(hashString, juryPoolSize, jurySize):
	'Get the devcoin jury text, which is lines jurors and alternates.'
	devcoinJurors = [None] * juryPoolSize
	devcoinJuryOutput = cStringIO.StringIO()
	totalHashString = ''
	for juror in xrange(jurySize):
		totalHashString += hashString
		addJuror(devcoinJurors, totalHashString)
	for devcoinJurorIndex, devcoinJuror in enumerate(devcoinJurors):
		if devcoinJuror != None:
			devcoinJuryOutput.write('%s, %s\n' % (devcoinJurorIndex, devcoinJuror))
	return devcoinJuryOutput.getvalue()

def getFloatHash(word):
	'Get the float from the sha256 hash of the word.'
	return float.fromhex('.' + hashlib.sha256(word).hexdigest())

def getOutput(arguments):
	'Get the output according to the arguments.'
	postTimeString = getParameter(arguments, 'August 06, 2011, 9:36:01 pm', 'time') #the default is just for testing
	postDateTime = getDateTimeBySimpleMachinesForumString(postTimeString)
	postDelayDateTime = postDateTime + globalBlockDelayTimeDelta
	hashString = postTimeString + getBitcoinBlockHash(postDelayDateTime)
	return 'Jurors:\n' + getDevcoinJuryText(hashString, 10, 3)

def getParameter(arguments, defaultValue, name):
	'Get the parameter of the given name from the arguments.'
	name = '-' + name
	if name not in arguments:
		return defaultValue
	nameIndexNext = arguments.index(name) + 1
	if nameIndexNext >= len(arguments):
		return defaultValue
	return arguments[nameIndexNext]

def sendOutputTo(outputTo, text):
	'Send output to a file or a standard output.'
	if outputTo == '':
		return False
	if outputTo.endswith('stderr'):
		sys.stderr.write(text)
		sys.stderr.flush()
		return False
	if outputTo.endswith('stdout'):
		sys.stdout.write(text)
		sys.stdout.flush()
		return False
	return writeFileText(outputTo, text)

def writeFileText(fileName, fileText, writeMode='w+'):
	'Write a text to a file.'
	try:
		file = open(fileName, writeMode)
		file.write(fileText)
		file.close()
	except IOError:
		print('The file ' + fileName + ' can not be written to.')
		return False
	return True

def writeOutput(arguments):
	'Write output.'
#	if len(arguments) < 2 or '-h' in arguments or '-help' in arguments:
#		print(  __doc__)
#		return
	outputTo = getParameter(arguments, 'stdout', 'output')
	sendOutputTo(outputTo, getOutput(arguments))


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

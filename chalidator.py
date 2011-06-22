"""
Chalidator is a script to determine to what extent the donation meets the requirement.

This is meant to be used by coin programs to validate the block.


==Commands==
===Help===
The -h option or the -help option will print the help, which is this document.  The example follows:
python almoner.py -h

===Input===
The -input option sets the input file name.  The example follows:
python almoner.py -input bitcoindonationinformation.txt

An example of a donation information input file is at:
https://github.com/Unthinkingbit/charity/blob/master/bitcoindonationinformation.txt

===Output===
The -output option sets the output.  If the output ends with stderr, the output will be sent to stderr  If the output ends with stdout, the output will be sent to stdout.  If the output does not end with stderr or stdout, the output will be written to a file by that name.  The example follows:
python almoner.py -input bitcoindonationinformation.txt -output stdout

An example of an almoner output file is at:
https://github.com/Unthinkingbit/charity/blob/master/almoner.txt


==Install==
For almoner to run, you need Python 2.x, almoner will probably not run with python 3.x.  To check if it is on your machine, in a terminal type:
python

If python 2.x is not on your machine, download the latest python 2.x, which is available from:
http://www.python.org/download/
"""


import cStringIO
import math
import sys
import urllib


__license__ = 'public domain'


def getCoinDictionary(text):
	'Get the coin dictionary for the text.'
	coinDictionary = {}
	for line in getTextLines(text):
		words = line.split(',')
		if len(words) > 2:
			firstLowerSpaceless = words[0].lower().replace(' ', '')
			if firstLowerSpaceless == 'coin':
				coinAddress = words[1]
				share = getFloat(0.0, words[2])
				if coinAddress in coinDictionary:
					coinDictionary[coinAddress] += share
				else:
					coinDictionary[coinAddress] = share
	return coinDictionary

def getFileText(fileName, printWarning=True, readMode='r'):
	'Get the entire text of a file.'
	try:
		file = open(fileName, readMode)
		fileText = file.read()
		file.close()
		return fileText
	except IOError:
		if printWarning:
			print('The file ' + fileName + ' does not exist.')
	return ''

def getFileTextOrText(fileName, printWarning=True, readMode='r'):
	'Get the text if there is a carriage return in the file, otherwise get the entire text of a file.'
	if '\n' in fileName:
		return fileName
	return getFileText(fileName, printWarning, readMode)

def getFloat(defaultValue, text):
	'Get float if possible, defaultValue if not.'
	try:
		return float(text)
	except:
		pass
	return defaultValue

def getOutput(arguments):
	'Get the output according to the arguments.'
	inputString = getParameter(arguments, 'input')
	requirementString = getParameter(arguments, 'requirement')
	return str(getTotalValue(inputString, requirementString))

def getParameter(arguments, name):
	'Get the parameter of the given name from the arguments.'
	name = '-' + name
	if name not in arguments:
		return ''
	nameIndexNext = arguments.index(name) + 1
	if nameIndexNext >= len(arguments):
		return ''
	return arguments[nameIndexNext]

def getTextLines(text):
	'Get the all the lines of text of a text.'
	textLines = text.replace('\r', '\n').replace('\n\n', '\n').split('\n')
	if len(textLines) == 1:
		if textLines[0] == '':
			return []
	return textLines

def getTotalValue(inputString, requirementString):
	'Get the total value according to the input and requirement.'
	return getTotalValueByText(getFileTextOrText(inputString), getFileTextOrText(requirementString))

def getTotalValueByText(inputText, requirementText):
	'Get the total value according to the input text and requirement text.'
	inputCoinDictionary = getCoinDictionary(inputText)
	requirementCoinDictionary = getCoinDictionary(requirementText)
	totalValue = 0.0
	for inputCoinDictionaryKey in inputCoinDictionary:
		if inputCoinDictionaryKey in requirementCoinDictionary:
			totalValue += min(inputCoinDictionary[inputCoinDictionaryKey], requirementCoinDictionary[inputCoinDictionaryKey])
	return totalValue

def sendOutputTo(outputTo, text):
	'Send output to a file or a standard output.'
	if outputTo.endswith('stderr'):
		sys.stderr.write(text)
		sys.stderr.write('\n')
		sys.stderr.flush()
		return
	if outputTo.endswith('stdout'):
		sys.stdout.write(text)
		sys.stdout.write('\n')
		sys.stdout.flush()
		return
	writeFileText(outputTo, text)

def writeFileText(fileName, fileText, writeMode='w+'):
	'Write a text to a file.'
	try:
		file = open(fileName, writeMode)
		file.write(fileText)
		file.close()
	except IOError:
		print('The file ' + fileName + ' can not be written to.')

def writeOutput(arguments):
	'Write output.'
	if len(arguments) < 2 or '-h' in arguments or '-help' in arguments:
		print(  __doc__)
		return
	outputTo = getParameter(arguments, 'output')
	if outputTo != '':
		sendOutputTo(outputTo, getOutput(arguments))


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

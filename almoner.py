"""
Almoner is a program to determine how many bitcoins to donate to each recipient.

This is meant to be used by bitcoin pools or miners to automatically donate to a list of recipients.  With this program, people could simply decide how much to donate, they don't have to also look up bitcoin addresses for each recipient.

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


globalMinimumIdenticalProportion = 0.6
globalOpenSourceStartWords = 'agpl apache bsd creative gnu gpl mit public unlicense'.split()


def getAlmonerText(contributors):
	'Get the almoner text which consists of lines each of which have a coin address followed by a space then the share.'
	almonerText = ''
	for contributor in contributors:
		almonerText += '%s %s\n' % (contributor.bitcoinAddress, contributor.share)
	return almonerText

def getColonDividedWords(text):
	'Get the words divided around the colon.'
	colonIndex = text.find(':')
	if colonIndex < 0:
		return [text]
	return [text[: colonIndex], text[colonIndex + 1 :]]

def getContributors(fileName):
	'Get the words divided around the colon.'
	return getContributorsByText(getFileText(fileName))

def getContributorsByText(text):
	'Get the contributors by text.'
	contributor = None
	contributors = []
	for line in getTextLines(text):
		words = getColonDividedWords(line)
		if len(words) > 1:
			firstLowerSpaceless = words[0].lower().replace(' ', '')
			if len(firstLowerSpaceless) > 0:
				if firstLowerSpaceless == 'contributor':
					contributor = Contributor()
					contributors.append(contributor)
				if contributor != None:
					contributor.parseLine(line)
	return contributors

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

def getFloat(defaultValue, text):
	'Get float if possible, defaultValue if not.'
	try:
		return float(text)
	except:
		pass
	return defaultValue

def getLinkText(text):
	'Get the text part of a text without the tag part.'
	isLinkText = True
	cLinkText = cStringIO.StringIO()
	for character in text:
		if character == '<':
			isLinkText = False
		elif character == '>':
			isLinkText = True
		elif isLinkText:
			cLinkText.write(character)
	return cLinkText.getvalue().strip()

def getOutput(arguments):
	'Get the output according to the arguments.'
	fileName = getParameter(arguments, 'input')
	outputTo = getParameter(arguments, 'output')
	contributors = getContributors(fileName)
	setUtilityValues(contributors)
	setShares(contributors)
	return getAlmonerText(contributors)

def getParameter(arguments, name):
	'Get the parameter of the given name from the arguments.'
	name = '-' + name
	if name not in arguments:
		return ''
	nameIndexNext = arguments.index(name) + 1
	if nameIndexNext >= len(arguments):
		return ''
	return arguments[nameIndexNext]

def getStartsWithWords(text, words):
	'Determine if the text starts with a word in the list of words.'
	for word in words:
		if text.startswith(word):
			return True
	return False

def getTextLines(text):
	'Get the all the lines of text of a text.'
	textLines = text.replace('\r', '\n').replace('\n\n', '\n').split('\n')
	if len(textLines) == 1:
		if textLines[0] == '':
			return []
	return textLines

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

def setShares(contributors):
	'Set each shares to the utility value divided by the total of the utility values.'
	totalUtilityValue = 0.0
	for contributor in contributors:
		totalUtilityValue += contributor.utilityValue
	for contributor in contributors:
		contributor.share += contributor.utilityValue / totalUtilityValue

def setUtilityValues(contributors):
	'Set the utility values of the contributors.'
	numberOfUtilityValues = 0
	totalUtilityValue = 0.0
	for contributor in contributors:
		if contributor.utilityValue != None:
			numberOfUtilityValues += 1
			totalUtilityValue += contributor.utilityValue
	average = 1.0
	if numberOfUtilityValues > 0:
		average = totalUtilityValue / float(numberOfUtilityValues)
	for contributor in contributors:
		if contributor.utilityValue == None:
			contributor.utilityValue = average

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
	text = getOutput(arguments)
	outputTo = getParameter(arguments, 'output')
	if outputTo != '':
		sendOutputTo(outputTo, text)

def writeTitleValue(cString, title, value):
	'Write the title and value line, if the value is not empty.'
	if value != '':
		cString.write('%s: %s\n' % (title, value))


class Contributor:
	'A class to handle a contributor.'
	def __init__(self):
		'Make empty contributor.'
		self.bitcoinAddress = ''
		self.contributor = ''
		self.description = ''
		self.isOpenSource = False
		self.projectHomepage = ''
		self.projectLicense = ''
		self.projectType = ''
		self.share = 0.0
		self.utility = ''
		self.utilityValue = None

	def __repr__(self):
		"Get the string representation of this Contributor."
		return self.toString()

	def addAlmonerLine(self, cString):
		'Add bitcoin address and share to the cString.'
		cString.write('%s %s\n' % (self.bitcoinAddress, self.share))

	def parseLine(self, line):
		'Parse line, splitting into two words around a colon, do nothing if there are less than two words.'
		words = getColonDividedWords(line)
		if len(words) < 2:
			return
		firstLowerSpaceless = words[0].lower().replace(' ', '')
		if len(firstLowerSpaceless) < 1:
			return
		secondWord = words[1].lstrip()
		if firstLowerSpaceless == 'bitcoinaddress':
			self.bitcoinAddress = secondWord
		elif firstLowerSpaceless == 'contributor':
			self.contributor = secondWord
		elif firstLowerSpaceless == 'description':
			self.description = secondWord
		elif firstLowerSpaceless == 'projecthomepage':
			self.projectHomepage = secondWord
		elif firstLowerSpaceless == 'projectlicense':
			self.projectLicense = secondWord
			self.isOpenSource = getStartsWithWords(getLinkText(secondWord).lower().replace(' ', ''), globalOpenSourceStartWords)
		elif firstLowerSpaceless == 'projectype':
			self.projectType = secondWord
		elif firstLowerSpaceless == 'utility':
			self.utility = secondWord
			self.utilityValue = getFloat(None, secondWord)

	def toString(self):
		'Get contributor, bitcoin address, share and utility value as string.'
		cString = cStringIO.StringIO()
		cString.write('Contributor: %s\n' % self.contributor)
		cString.write('Bitcoin Address: %s\n' % self.bitcoinAddress)
		writeTitleValue(cString, 'Description', self.description)
		writeTitleValue(cString, 'Open Source', self.isOpenSource)
		writeTitleValue(cString, 'Project Homepage', self.projectHomepage)
		writeTitleValue(cString, 'Project License', self.projectLicense)
		writeTitleValue(cString, 'Project Type', self.projectType)
		cString.write('Share: %s' % str(round(100.0 * self.share, 1)) +'%\n')
		writeTitleValue(cString, 'Utility', self.utility)
		cString.write('Utility Value: %s\n' % self.utilityValue)
		return cString.getvalue()


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

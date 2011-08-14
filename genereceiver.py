"""
Genereceiver
 is a program to determine how many bitcoins to donate to each recipient.

This is meant to be used by bitcoin pools or miners to automatically donate to a list of recipients.  With this program, people could simply decide how much to donate, they don't have to also look up bitcoin addresses for each recipient.


==Commands==
===Help===
The -h option or the -help option will print the help, which is this document.  The example follows:
python almoner.py -h

===Input===
The -input option sets the input file name.  The example follows:
python almoner.py -input bitcoindonationinformation.html

An example of a donation information input file is at:
https://github.com/Unthinkingbit/charity/blob/master/bitcoindonationinformation.html

===Output===
The -output option sets the output.  If the output ends with stderr, the output will be sent to stderr  If the output ends with stdout or is empty, the output will be sent to stdout.  If the output does not end with stderr or stdout, the output will be written to a file by that name.  The example follows:
python almoner.py -input bitcoindonationinformation.txt -output stdout

An example of an almoner output file is at:
https://github.com/Unthinkingbit/charity/blob/master/almoner.csv


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


__license__ = 'MIT'


def getAddressFractions(text):
	'Get the AddressFractions by text.'
	addressFractions = []
	isAddressSection = True
	for line in getTextLines(text):
		firstLowerSpaceless = ''
		words = getCommaDividedWords(line)
		if len(words) > 0:
			firstLowerSpaceless = words[0].lower().replace(' ', '')
		words = getCommaDividedWords(line)
		if isAddressSection:
			addressFractions.append(AddressFraction(line))
	return addressFractions

def getCommaDividedWords(text):
	'Get the words divided around the comma.'
	commaIndex = text.find(',')
	if commaIndex < 0:
		return [text]
	return [text[: commaIndex], text[commaIndex + 1 :]]

def getDenominatorSequences(addressFractions, isDescending):
	'Get the DenominatorSequences from the addressFractions.'
	denominatorSequences = []
	for addressFraction in addressFractions:
		for fraction in addressFraction.fractions:
			if fraction.denominator not in denominatorSequences:
				denominatorSequences.append(fraction.denominator)
	denominatorSequences.sort(reverse=isDescending)
	for denominatorSequenceIndex, denominatorSequence in enumerate(denominatorSequences):
		denominatorSequence = DenominatorSequence(addressFractions, denominatorSequence, isDescending)
		denominatorSequences[denominatorSequenceIndex] = denominatorSequence
	return denominatorSequences

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

def getGenereceiverText(denominatorSequences):
	'Get the genereceiver text which consists of lines of comma separated addresses.'
	genereceiverOutput = cStringIO.StringIO()
	for denominatorSequence in denominatorSequences:
		genereceiverOutput.write(denominatorSequence.getReceiverString())
	return genereceiverOutput.getvalue()

def getInternetText(address):
	'Get the entire text of an internet page.'
	try:
		page = urllib.urlopen(address)
		text = page.read()
		page.close()
		return text
	except IOError:
		return ''

def getIsDescending(fileName):
	'Return false unless the fileName finishes with an odd number.'
	underscoreIndex = fileName.find('_')
	if underscoreIndex == -1:
		return False
	afterUnderscore = fileName[underscoreIndex + 1 :]
	dotIndex = afterUnderscore.rfind('.')
	if dotIndex == -1:
		return False
	afterUnderscore = afterUnderscore[: dotIndex]
	if not afterUnderscore.isdigit():
		return False
	return int(afterUnderscore) % 2 == 1

def getLocationText(address):
	'Get the page by the address, be it a file name or hypertext address.'
	if address.startswith('http://') or address.startswith('https://'):
		return getInternetText(address)
	return getFileText(address)

def getOutput(arguments):
	'Get the output according to the arguments.'
	fileName = getParameter(arguments, 'account.csv', 'input')
	addressFractions = getAddressFractions(getLocationText(fileName))
	denominatorSequences = getDenominatorSequences(addressFractions, getIsDescending(fileName))
	return getGenereceiverText(denominatorSequences)

def getParameter(arguments, defaultValue, name):
	'Get the parameter of the given name from the arguments.'
	name = '-' + name
	if name not in arguments:
		return defaultValue
	nameIndexNext = arguments.index(name) + 1
	if nameIndexNext >= len(arguments):
		return defaultValue
	return arguments[nameIndexNext]

def getTextLines(text):
	'Get the all the stripped lines of text of a text.'
	originalLines = text.replace('\r', '\n').replace('\n\n', '\n').split('\n')
	textLines = []
	for originalLine in originalLines:
		originalLineStripped = originalLine.strip()
		if originalLineStripped != '':
			textLines.append(originalLineStripped)
	return textLines

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
	if len(arguments) < 2 or '-h' in arguments or '-help' in arguments:
		print(  __doc__)
		return
	outputTo = getParameter(arguments, 'test_receiver.csv', 'output')
	if sendOutputTo(outputTo, getOutput(arguments)):
		print('The receiver file has been written to:\n%s\n' % outputTo)


class AddressFraction:
	'A class to handle an address and associated fractions.'
	def __init__(self, line=''):
		'Initialize.'
		self.coinAddress = ''
		self.fractions = []
		words = line.split(',')
		if len(words) < 1:
			return
		self.coinAddress = words[0]
		lastDashIndex = self.coinAddress.rfind('-')
		if lastDashIndex != -1:
			self.coinAddress = self.coinAddress[lastDashIndex + 1 :]
		if len(words) == 1:
			self.fractions.append(Fraction())
			return
		for word in words[1 :]:
			wordStripped = word.replace('/', '').strip()
			if wordStripped.isdigit() or len(wordStripped) == 0:
				self.fractions.append(Fraction(word))

	def __repr__(self):
		"Get the string representation of this class."
		return '%s, %s' % (self.coinAddress, self.fractions)


class DenominatorSequence:
	'A class to handle a DenominatorSequence.'
	def __init__(self, addressFractions, denominator, isDescending):
		'Initialize.'
		self.coinAddresses = []
		self.denominator = denominator
		for addressFraction in addressFractions:
			for fraction in addressFraction.fractions:
				if fraction.denominator == denominator:
					for addressIndex in xrange(fraction.numerator):
						self.coinAddresses.append(addressFraction.coinAddress)
		self.coinAddresses.sort(reverse=isDescending)

	def __repr__(self):
		"Get the string representation of this class."
		return '%s, %s\n' % (self.denominator, self.coinAddresses)

	def getReceiverString(self):
		'Get the receiver format string.'
		numberOfSlots = int(math.ceil(float(len(self.coinAddresses)) / float(self.denominator)))
		numberOfCells = numberOfSlots * self.denominator
		floatWidth = float(len(self.coinAddresses)) / float(numberOfSlots)
		maximumSlotWidth = int(math.ceil(floatWidth))
		minimumSlotWidth = int(math.floor(floatWidth))
		remainingNumberOfNarrows = numberOfCells - len(self.coinAddresses)
		remainingNumberOfWides = numberOfSlots - remainingNumberOfNarrows
		receiverOutput = cStringIO.StringIO()
		coinAddressIndex = 0
		for wideIndex in xrange(remainingNumberOfWides):
			endIndex = coinAddressIndex + maximumSlotWidth
			receiverOutput.write('%s\n' % ','.join(self.coinAddresses[coinAddressIndex : endIndex]))
			coinAddressIndex = endIndex
		for narrowIndex in xrange(remainingNumberOfNarrows):
			endIndex = coinAddressIndex + minimumSlotWidth
			receiverOutput.write('%s\n' % ','.join(self.coinAddresses[coinAddressIndex : endIndex]))
			coinAddressIndex = endIndex
		return receiverOutput.getvalue()


class Fraction:
	'A class to handle a fraction.'
	def __init__(self, line=''):
		'Initialize.'
		self.denominator = 1
		self.numerator = 1
		lineStripped = line.strip()
		if len(lineStripped) < 1:
			return
		if lineStripped[0] == '/':
			lineStripped = '1' + lineStripped
		words = lineStripped.replace('/', ' ').split()
		if len(words) == 0:
			return
		self.numerator = int(words[0])
		if len(words) == 2:
			self.denominator = int(words[1])

	def __repr__(self):
		"Get the string representation of this class."
		return '%s/%s' % (self.numerator, self.denominator)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

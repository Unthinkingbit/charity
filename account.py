"""
Account is a program to generate a devcoin receiver file from a bitcoinshare, bounty, devcoinshare and peer file.

This is meant to be used by devcoin accountants and auditors to create and check the receiver files.  The account file has a list of addresses and shares.  Anything after a dash is a comment.


==Commands==
===Help===
The -h option, the -help option, will print the help, which is this document.  The example follows:
python account.py -h

===Input===
Default is https://raw.github.com/Unthinkingbit/charity/master/account_3.csv

The -input option sets the input file name.  The example follows:
python account.py -input https://raw.github.com/Unthinkingbit/charity/master/account_3.csv

An example of an account information input file is at:
https://raw.github.com/Unthinkingbit/charity/master/account_3.csv

===Output===
Default is test_receiver.csv

The -output option sets the output.  If the output ends with stderr, the output will be sent to stderr  If the output ends with stdout, the output will be sent to stdout.  If the output does not end with stderr or stdout, the output will be written to a file by that name, with whatever suffix the input file has.  The example follows:
python genereceiver.py -output test_receiver.csv

An example of an genereceiver output file is at:
https://raw.github.com/Unthinkingbit/charity/master/test_receiver_3.csv


==Install==
For genereceiver to run, you need Python 2.x, almoner will probably not run with python 3.x.  To check if it is on your machine, in a terminal type:
python

If python 2.x is not on your machine, download the latest python 2.x, which is available from:
http://www.python.org/download/
"""

import almoner
import cStringIO
import hashlib
import math
import sys


__license__ = 'MIT'


def addReceiverLines(coinAddresses, receiverLines):
	'Get the receiver format line.'
	if len(coinAddresses) == 0:
		return
	addressQuantityDictionary = getQuantityDictionary(coinAddresses)
	firstQuantity = addressQuantityDictionary.values()[0]
	for addressQuantity in addressQuantityDictionary.values():
		if addressQuantity != firstQuantity:
			receiverLines.append(','.join(coinAddresses))
			return
	receiverLines.append(','.join(addressQuantityDictionary.keys()))

def carryCoinAddresses(denominatorSequences):
	'Carry coin addresses from high denominator sequences to lower denominator sequences.'
	for denominatorSequenceIndex in xrange(len(denominatorSequences) - 2, -1, -1):
		denominatorSequence = denominatorSequences[denominatorSequenceIndex]
		denominatorSequenceBelow = denominatorSequences[denominatorSequenceIndex + 1]
		denominatorRatio = denominatorSequenceBelow.denominator / denominatorSequence.denominator
		belowCoinAddressQuantityDictionary = getQuantityDictionary(denominatorSequenceBelow.coinAddresses)
		for belowCoinAddressKey in belowCoinAddressQuantityDictionary:
			belowCoinAddressValue = belowCoinAddressQuantityDictionary[belowCoinAddressKey]
			carry = belowCoinAddressValue / denominatorRatio
			if carry > 0:
				belowCoinAddressQuantityDictionary[belowCoinAddressKey] -= carry * denominatorRatio
				denominatorSequence.coinAddresses += [belowCoinAddressKey] * carry
		denominatorSequenceBelow.coinAddresses = []
		for belowCoinAddressKey in belowCoinAddressQuantityDictionary:
			denominatorSequenceBelow.coinAddresses += [belowCoinAddressKey] * belowCoinAddressQuantityDictionary[belowCoinAddressKey]

def getAccountLines(arguments, fileName):
	'Get the lines according to the arguments.'
	bitcoinFileName = almoner.getParameter(arguments, 'bitcoinshare.html', 'inputbitcoin')
	bitcoinLines = almoner.getAddressLines(bitcoinFileName)
	bountyLines = almoner.getTextLines(almoner.getLocationText(fileName))
	devcoinFileName = almoner.getParameter(arguments, 'devcoinshare.html', 'inputdevcoin')
	devcoinLines = almoner.getAddressLines(devcoinFileName)
	accountLines = bountyLines + bitcoinLines + devcoinLines
	print('Number of bitcoin lines: %s' % len(bitcoinLines))
	print('Number of devcoin lines: %s' % len(devcoinLines))
	print('')
	return accountLines

def getAddressFractions(lines):
	'Get the AddressFractions by text.'
	addressFractions = []
	for line in lines:
		addressFractions.append(AddressFraction(line))
	return addressFractions

def getDenominatorSequences(addressFractions):
	'Get the DenominatorSequences from the addressFractions.'
	denominatorSequences = []
	for addressFraction in addressFractions:
		for fraction in addressFraction.fractions:
			if fraction.denominator not in denominatorSequences:
				denominatorSequences.append(fraction.denominator)
	denominatorSequences.sort()
	for denominatorSequenceIndex, denominatorSequence in enumerate(denominatorSequences):
		denominatorSequence = DenominatorSequence(addressFractions, denominatorSequence)
		denominatorSequences[denominatorSequenceIndex] = denominatorSequence
	return denominatorSequences

def getPeerLines(arguments):
	'Get the inner peer text according to the arguments.'
	peerFileName = almoner.getParameter(arguments, 'peer.csv', 'inputpeer')
	peerLines = almoner.getTextLines(almoner.getLocationText(peerFileName))
	print('Number of peers: %s' % len(peerLines))
	print('')
	return peerLines

def getPluribusunumText(peerText, receiverLines):
	'Get the pluribusunum text according to the arguments.'
	return 'Format,pluribusunum\n%s_begincoins\n%s_endcoins\n' % (peerText, almoner.getTextByLines(receiverLines))

def getQuantityDictionary(elements):
	'Get the quantity dictionary.'
	quantityDictionary = {}
	for element in elements:
		if element in quantityDictionary:
			quantityDictionary[element] += 1
		else:
			quantityDictionary[element] = 1
	return quantityDictionary

def getReceiverLines(accountLines, suffixNumber):
	'Get the lines according to the arguments.'
	addressFractions = getAddressFractions(accountLines)
	denominatorSequences = getDenominatorSequences(addressFractions)
	carryCoinAddresses(denominatorSequences)
	maximumReceivers = 4000
	receiverLines = getReceiverLinesByDenominatorSequences(denominatorSequences)
	if len(receiverLines) > maximumReceivers:
		denominatorMultiplier = (len(receiverLines) + maximumReceivers) / (maximumReceivers + 1 - len(denominatorSequences))
		multiplyDenominatorSequences(denominatorMultiplier, denominatorSequences)
		receiverLines = getReceiverLinesByDenominatorSequences(denominatorSequences)
		if len(receiverLines) > maximumReceivers:
			print('Warning, denominatorMultiplier math is wrong, the receiver lines will be grouped by another factor of two.')
			multiplyDenominatorSequences(2, denominatorSequences)
			receiverLines = getReceiverLinesByDenominatorSequences(denominatorSequences)
	devcoinBlocksPerShareFloat = 4000.0 / len(receiverLines)
	averageDevcoinsPerShare = int(round(devcoinBlocksPerShareFloat * 45000.0))
	maximumDevcoinsPerShare = int(math.ceil(devcoinBlocksPerShareFloat)) * 45000
	minimumDevcoinsPerShare = int(math.floor(devcoinBlocksPerShareFloat)) * 45000
	print('Average devcoins per share: %s' % averageDevcoinsPerShare)
	print('Minimum devcoins per share: %s' % minimumDevcoinsPerShare)
	print('Maximum devcoins per share: %s' % maximumDevcoinsPerShare)
	print('Number of receiverLines lines: %s' % len(receiverLines))
	print('')
	return getShuffledLines(receiverLines, suffixNumber)

def getReceiverLinesByDenominatorSequences(denominatorSequences):
	'Concatenate the receiver lines from all the denominator sequences.'
	receiverLines = []
	for denominatorSequence in denominatorSequences:
		receiverLines += denominatorSequence.getReceiverLines()
	return receiverLines

def getShuffledLines(receiverLines, suffixNumber):
	'Get the shuffled lines.'
	goldenRatio = math.sqrt(1.25) + 0.5
	shuffledLines = []
	for receiverLine in receiverLines:
		shuffledLengthFloat = float(len(shuffledLines))
		index = int(shuffledLengthFloat * ((shuffledLengthFloat * goldenRatio) % 1.0))
		shuffledLines.insert(min(index, len(shuffledLines) - 1), receiverLine)
	rotation = (float(suffixNumber) * goldenRatio) % 1.0
	rotationIndex = int(math.floor(rotation * float(len(shuffledLines))))
	if suffixNumber % 2 == 0:
		shuffledLines.reverse()
	shuffledLines = shuffledLines[rotationIndex :] + shuffledLines[: rotationIndex]
	return shuffledLines

def getSuffixNumber(fileName):
	'Determine the suffix number, returning 0 if there is not one.'
	underscoreIndex = fileName.rfind('_')
	if underscoreIndex == -1:
		return 0
	afterUnderscore = fileName[underscoreIndex + 1 :]
	dotIndex = afterUnderscore.rfind('.')
	if dotIndex == -1:
		return 0
	afterUnderscore = afterUnderscore[: dotIndex]
	if not afterUnderscore.isdigit():
		return 0
	return int(afterUnderscore)

def getSummaryText(peerLines, receiverLines, suffixNumber):
	'Get the summary text.'
	cString = cStringIO.StringIO()
	suffixNumberPlusOne = suffixNumber + 1
	numberOfLines = len(receiverLines)
	cString.write('The round %s receiver files have been uploaded to:\n' % suffixNumber)
	for peerLine in peerLines:
		suffixedPeerLine = peerLine[: -len('.csv')] + ('_%s.csv' % suffixNumber)
		cString.write('%s\n' % suffixedPeerLine)
	cString.write('\nThe account file is at:\n')
	cString.write('http://galaxies.mygamesonline.org/account_%s.csv\n\n' % suffixNumber)
	devcoins = int(round(180000000.0 / float(numberOfLines)))
	cString.write('There were %s receiver lines, so the average generation share was worth ' % numberOfLines)
	cString.write('180,000,000 dvc / %s = %s dvc.\n\n' % (numberOfLines, almoner.getCommaNumberString(devcoins)))
	cString.write('People on that list will start getting those coins in round %s, starting at block %s,000.' % (suffixNumber, 4 * suffixNumber))
	cString.write(' The procedure for generating the receiver files is at:\n')
	cString.write('http://devtome.com/doku.php?id=devcoin#generating_the_files\n\n')
	cString.write('The next bounties will go into round %s:\n' % suffixNumberPlusOne)
	cString.write('https://raw.github.com/Unthinkingbit/charity/master/bounty_%s.csv\n' % suffixNumberPlusOne)
	return cString.getvalue()

def multiplyDenominatorSequences(denominatorMultiplier, denominatorSequences):
	'Multiply the denominator of the denominatorSequences.'
	print('Receiver lines will be grouped by a factor of %s.' % denominatorMultiplier)
	for denominatorSequence in denominatorSequences:
		denominatorSequence.denominator *= denominatorMultiplier

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	fileName = almoner.getParameter(arguments, 'bounty_6.csv', 'input')
	suffixNumber = getSuffixNumber(fileName)
	outputAccountTo = almoner.getSuffixedFileName(almoner.getParameter(arguments, 'account.csv', 'output'), str(suffixNumber))
	accountLines = getAccountLines(arguments, fileName)
	peerLines = getPeerLines(arguments)
	peerText = '_beginpeers\n%s_endpeers\n' % almoner.getTextByLines(peerLines)
	accountText = getPluribusunumText(peerText, accountLines)
	if almoner.sendOutputTo(outputAccountTo, accountText):
		print('The account file has been written to:\n%s\n' % outputAccountTo)
	outputReceiverTo = almoner.getSuffixedFileName(almoner.getParameter(arguments, 'receiver.csv', 'outputreceiver'), str(suffixNumber))
	outputSummaryTo = almoner.getParameter(arguments, 'receiver_summary.txt', 'outputsummary')
	receiverLines = getReceiverLines(accountLines, suffixNumber)
	receiverText = getPluribusunumText(peerText, receiverLines)
	if almoner.sendOutputTo(outputReceiverTo, receiverText):
		print('The receiver file has been written to:\n%s\n' % outputReceiverTo)
		shaOutputPrefix = almoner.getParameter(arguments, '', 'outputsha')
		if len(shaOutputPrefix) != 0:
			sha256FileName = almoner.getSuffixedFileName(outputReceiverTo, shaOutputPrefix)
			almoner.writeFileText(sha256FileName, hashlib.sha256(receiverText).hexdigest())
			print('The sha256 receiver file has been written to:\n%s\n' % sha256FileName)
	if almoner.sendOutputTo(outputSummaryTo, getSummaryText(peerLines, receiverLines, suffixNumber)):
		print('The summary file has been written to:\n%s\n' % outputSummaryTo)


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
		if len(words) < 3:
			self.fractions.append(Fraction())
			return
		self.coinAddress = words[1]
		for word in words[2 :]:
			lastDashIndex = word.rfind('-')
			if lastDashIndex != -1:
				word = word[: lastDashIndex]
			wordStripped = word.replace('/', '').strip()
			if wordStripped.isdigit() or len(wordStripped) == 0:
				self.fractions.append(Fraction(word))

	def __repr__(self):
		"Get the string representation of this class."
		return '%s, %s' % (self.coinAddress, self.fractions)


class DenominatorSequence:
	'A class to handle a DenominatorSequence.'
	def __init__(self, addressFractions, denominator):
		'Initialize.'
		self.coinAddresses = []
		self.denominator = denominator
		for addressFraction in addressFractions:
			for fraction in addressFraction.fractions:
				if fraction.denominator == denominator:
					for addressIndex in xrange(fraction.numerator):
						self.coinAddresses.append(addressFraction.coinAddress)
		self.coinAddresses.sort()

	def __repr__(self):
		"Get the string representation of this class."
		return '%s, %s\n' % (self.denominator, self.coinAddresses)

	def getReceiverLines(self):
		'Get the receiver lines.'
		numberOfSlots = int(math.ceil(float(len(self.coinAddresses)) / float(self.denominator)))
		floatWidth = float(len(self.coinAddresses)) / float(numberOfSlots)
		maximumSlotWidth = int(math.ceil(floatWidth))
		minimumSlotWidth = int(math.floor(floatWidth))
		numberOfCells = numberOfSlots * maximumSlotWidth
		remainingNumberOfNarrows = numberOfCells - len(self.coinAddresses)
		remainingNumberOfWides = numberOfSlots - remainingNumberOfNarrows
		receiverLines = []
		coinAddressIndex = 0
		for wideIndex in xrange(remainingNumberOfWides):
			endIndex = coinAddressIndex + maximumSlotWidth
			addReceiverLines(self.coinAddresses[coinAddressIndex : endIndex], receiverLines)
			coinAddressIndex = endIndex
		for narrowIndex in xrange(remainingNumberOfNarrows):
			endIndex = coinAddressIndex + minimumSlotWidth
			addReceiverLines(self.coinAddresses[coinAddressIndex : endIndex], receiverLines)
			coinAddressIndex = endIndex
		return receiverLines


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

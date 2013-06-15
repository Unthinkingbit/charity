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


globalGoldenRatio = math.sqrt(1.25) + 0.5


def addAdministratorBonus(accountLines):
	'Add the administrator bonus, up to a maximum of 9%.'
	originalReceiverLines = getReceiverLinesByAccountLines(accountLines)
	originalNumberOfLinesFloat = float(len(originalReceiverLines))
	administrators = []
	for accountLine in accountLines:
		if 'Administrator' in accountLine:
			administrators.append(Administrator(accountLine))
	administratorPay = 0.0
	generalAdministrators = []
	for administrator in administrators:
		administratorPay += administrator.pay
		if administrator.isGeneralAdministrator:
			generalAdministrators.append(administrator)
	for bonusMultiplier in xrange(7, 1, -1):
		bonusPay = bonusMultiplier * float(len(generalAdministrators))
		totalAdministratorPay = bonusPay + administratorPay
		totalShares = originalNumberOfLinesFloat + bonusPay
		percentPay = 0.1 * round(1000.0 * totalAdministratorPay / totalShares)
		if percentPay < 9.0:
			bonusShares = bonusMultiplier * len(generalAdministrators)
			accountLines.append('Administrator Bonus' + ': %s Shares' % bonusShares)
			for generalAdministrator in generalAdministrators:
				accountLines.append(generalAdministrator.getAccountLine(bonusMultiplier))
			accountLines.append('')
			print('Name: Administrator Bonus, Shares: %s' % bonusShares)
			return

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
	"""
	Sometimes there number of identical coin addresses in the denominator sequence is as high as the denominator. To condense the receiver file,
	if the number of copies of the coin address is as high as the denominator, coin addresses are carried to the sequence with the smaller
	denominator.
	
	To do this, the sequences to be carried into, which are sorted in ascending value of the denominator, are iterated downward from
	the length minus two, to zero. The quantity of each coin address in the sequence with the big denominator is entered into a
	dictionary. For	each coin address, the carry is calculated by dividing quantity of the coin address by the denominator ratio between the
	sequence with the big denominator and the denominator of the sequence to be carried into. The carry is then added to the sequence to be
	carried into, and the carry times the denominator ratio is subtracted from the sequence with the big denominator. For example, if the
	sequence has six copies of a coin address, and the denominator is five, and the sequence to be carried into has a denominator of one, the
	denominator ratio is five, and the carry integer is int(6 / 5) = 1. So one coin address is added to the list of coin addresses in the
	sequence to be carried into, and 1 * 5 = 5 is subtracted from the quantity of the coin address in the sequence with the big	denominator.

	After the quantities of each coin address are modified, the coin address lists in the sequence with the big denominator are generated from
	the quantity dictionary.
	"""
	for denominatorSequenceIndex in xrange(len(denominatorSequences) - 2, -1, -1):
		denominatorSequence = denominatorSequences[denominatorSequenceIndex]
		denominatorSequenceBigDenominator = denominatorSequences[denominatorSequenceIndex + 1]
		denominatorRatio = denominatorSequenceBigDenominator.denominator / denominatorSequence.denominator
		bigDenominatorAddressDictionary = getQuantityDictionary(denominatorSequenceBigDenominator.coinAddresses)
		for bigDenominatorAddressKey in bigDenominatorAddressDictionary:
			bigDenominatorAddressValue = bigDenominatorAddressDictionary[bigDenominatorAddressKey]
			carry = bigDenominatorAddressValue / denominatorRatio
			if carry > 0:
				bigDenominatorAddressDictionary[bigDenominatorAddressKey] -= carry * denominatorRatio
				denominatorSequence.coinAddresses += [bigDenominatorAddressKey] * carry
		denominatorSequenceBigDenominator.coinAddresses = []
		for bigDenominatorAddressKey in bigDenominatorAddressDictionary:
			bigDenominatorAddressValue = bigDenominatorAddressDictionary[bigDenominatorAddressKey]
			denominatorSequenceBigDenominator.coinAddresses += [bigDenominatorAddressKey] * bigDenominatorAddressValue

def getAccountLines(arguments, suffixNumberString):
	'Get the lines according to the arguments.'
	linkFileName = almoner.getParameter(arguments, 'account_location.csv', 'location')
	linkLines = almoner.getTextLines(almoner.getLocationText(linkFileName))[1 :]
	accountLines = ['']
	for linkLine in linkLines:
		linkLineSplit = linkLine.split(',')
		name = linkLineSplit[0]
		location = linkLineSplit[1]
		extraLines = []
		if '_xx' in location:
			location = location.replace('_xx', '_' + suffixNumberString)
			extraLines = almoner.getTextLines(almoner.getLocationText(location))
		else:
			extraLines = almoner.getNameAddressLines(location)
		numberOfShares = len(getReceiverLinesByAccountLines(extraLines))
		print('Name: %s, Location: %s, Shares: %s' % (name, location, numberOfShares))
		accountLines.append(name + ': %s Shares' % numberOfShares)
		accountLines += extraLines
		accountLines.append('')
	addAdministratorBonus(accountLines)
	print('')
	return accountLines

def getAddressDictionary(round):
	'Get the address dictionary.'
	addressDictionary = {}
	for accountLine in getAccountLines([], str(round)):
		accountLineSplit = accountLine.split(',')
		if len(accountLineSplit) > 1:
			name = accountLineSplit[0].strip()
			if name != '':
				addressDictionary[accountLineSplit[1]] = name
	return addressDictionary

def getAddressFractions(lines):
	'Get the AddressFractions by text.'
	addressFractions = []
	for line in lines:
		addressFractions.append(AddressFraction(line))
	return addressFractions

def getCutLines(cutLines, suffixNumber):
	"""
	The lines are cut at a different part of the list, so that a developer whose key starts with 1A does not get more on average over multiple
	rounds than a developer whose key starts with 1Z. This is done by cutting the list at an index which is the golden ratio times the round
	number, then modulo is used to keep it within the list bounds. It also reverses the list at every even suffix number, in case cutting is
	not enough to average pay over multiple rounds.
	"""
	rotation = (float(suffixNumber) * globalGoldenRatio) % 1.0
	rotationIndex = int(math.floor(rotation * float(len(cutLines))))
	if suffixNumber % 2 == 0:
		cutLines.reverse()
	cutLines = cutLines[rotationIndex :] + cutLines[: rotationIndex]
	return cutLines

def getDenominatorSequences(addressFractions):
	'Get the DenominatorSequences from the addressFractions.'
	denominators = []
	for addressFraction in addressFractions:
		for fraction in addressFraction.fractions:
			if fraction.denominator not in denominators:
				denominators.append(fraction.denominator)
	denominators.sort()
	denominatorSequences = []
	for denominator in denominators:
		denominatorSequence = DenominatorSequence(addressFractions, denominator)
		denominatorSequence.coinAddresses = getShuffledElements(denominatorSequence.coinAddresses)
		denominatorSequences.append(denominatorSequence)
	return denominatorSequences

def getDenominatorSequencesByAccountLines(accountLines):
	'Get the lines according to the arguments.'
	addressFractions = getAddressFractions(accountLines)
	denominatorSequences = getDenominatorSequences(addressFractions)
	carryCoinAddresses(denominatorSequences)
	return denominatorSequences

def getGroupedReceiverLines(denominatorMultiplier, denominatorSequences):
	'Get grouped receiver lines.'
	print('Receiver lines will be grouped by a factor of %s.' % denominatorMultiplier)
	for denominatorSequence in denominatorSequences:
		denominatorSequence.denominator *= denominatorMultiplier
	return getReceiverLinesByDenominatorSequences(denominatorSequences)

def getPackedReceiverLines(denominatorSequences, originalReceiverLines, suffixNumber):
	"""
	A devcoin round has 4,000 blocks, if there are more than 4,000 receiver lines, the lines after the four thousandth row will not get
	generation devcoins. To get devcoins to every line, the receiver lines are packed by the denominatorMultiplier:
	denominatorMultiplier = (len(originalReceiverLines) + maximumReceivers) / (maximumReceivers + 1 - len(denominatorSequences))

	The denominator in each denominator sequence is multiplied by the denominatorMultiplier. When the receiver lines are then generated by the
	denominator sequences, the column width of the line will be up to the denominator, in effect reducing the number of rows by the
	denominatorMultiplier and increasing the number of columns by the denominatorMultiplier.

	Because this changes the number of rows, the 'Average devcoins per share' is calculated from the original number of lines.
	"""
	maximumReceivers = 4000
	originalReceiverLineLength = len(originalReceiverLines)
	denominatorMultiplier = 1
	if len(originalReceiverLines) > maximumReceivers:
		denominatorMultiplier = (len(originalReceiverLines) + maximumReceivers) / (maximumReceivers + 1 - len(denominatorSequences))
		originalReceiverLines = getGroupedReceiverLines(denominatorMultiplier, denominatorSequences)
		if len(originalReceiverLines) > maximumReceivers:
			print('Warning, denominatorMultiplier math is wrong, the receiver lines will be grouped by another factor of two.')
			originalReceiverLines = getGroupedReceiverLines(2, denominatorSequences)
	originalDevcoinBlocksPerShareFloat = float(maximumReceivers) / originalReceiverLineLength
	averageDevcoinsPerShare = int(round(originalDevcoinBlocksPerShareFloat * 45000.0))
	print('Average devcoins per share: %s' % almoner.getCommaNumberString(averageDevcoinsPerShare))
	print('Number of original receiver lines lines: %s' % originalReceiverLineLength)
	print('Number of receiver lines lines: %s' % len(originalReceiverLines))
	print('')
	return getCutLines(originalReceiverLines, suffixNumber)

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

def getReceiverLinesByAccountLines(accountLines):
	'Write output.'
	denominatorSequences = getDenominatorSequencesByAccountLines(accountLines)
	return getReceiverLinesByDenominatorSequences(denominatorSequences)

def getReceiverLinesByDenominatorSequences(denominatorSequences):
	'Concatenate the receiver lines from all the denominator sequences.'
	receiverLines = []
	for denominatorSequence in denominatorSequences:
		receiverLines += denominatorSequence.getReceiverLines()
	return receiverLines

def getRecipientDictionary(round):
	'Get the recipient dictionary.'
	recipientDictionary = {}
	for accountLine in getAccountLines([], str(round)):
		accountLineSplit = accountLine.split(',')
		if len(accountLineSplit) > 1:
			name = accountLineSplit[0]
			if name != '':
				recipientDictionary[name] = accountLineSplit[1]
	return recipientDictionary

def getShareListSet(round):
	'Get the names of the developers on the share list set.'
	isShareName = False
	shareListSet = set([])
	for accountLine in getAccountLines([], str(round)):
		accountLineSplit = accountLine.split(',')
		if len(accountLineSplit) == 0:
			isShareName = False
		elif len(accountLineSplit[0]) == 0:
			isShareName = False
		if isShareName:
			shareListSet.add(accountLineSplit[0])
		if len(accountLineSplit) == 1:
			if ' Share List: ' in accountLineSplit[0]:
				isShareName = True
	return shareListSet

def getShuffledElements(elements):
	"""
	Because the number of lines is usually not perfectly divisible into 4,000, the addresses of each developer are spread out, so that in each
	round the amount that the developer receives is close to the average. This is done by inserting them at an index within the shuffledLines
	list which is increased by the golden ratio, then modulo is used to keep it within the list bounds.
	"""
	shuffledElements = []
	for element in elements:
		shuffledLengthFloat = float(len(shuffledElements))
		index = int(shuffledLengthFloat * ((shuffledLengthFloat * globalGoldenRatio) % 1.0))
		shuffledElements.insert(min(index, len(shuffledElements) - 1), element)
	return shuffledElements

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

def getSummaryText(accountLines, originalReceiverLines, peerLines, suffixNumber):
	'Get the summary text.'
	cString = cStringIO.StringIO()
	suffixNumberPlusOne = suffixNumber + 1
	numberOfLines = len(originalReceiverLines)
	numberOfLinesFloat = float(numberOfLines)
	administratorPay = 0.0
	for accountLine in accountLines:
		if 'Administrator' in accountLine:
			administratorPay += Administrator(accountLine).pay
	percentPay = 0.1 * round(1000.0 * administratorPay / numberOfLinesFloat)
	cString.write('The round %s receiver files have been uploaded to:\n' % suffixNumber)
	for peerLine in peerLines:
		suffixedPeerLine = peerLine[: -len('.csv')] + ('_%s.csv' % suffixNumber)
		cString.write('%s\n' % suffixedPeerLine)
	cString.write('\nThe account file is at:\n')
	cString.write('http://galaxies.mygamesonline.org/account_%s.csv\n' % suffixNumber)
	devcoins = int(round(180000000.0 / numberOfLinesFloat))
	cString.write('\nThere were %s original receiver lines, so the average number of devcoins per share is ' % numberOfLines)
	cString.write('180,000,000 dvc / %s = %s dvc.' % (numberOfLines, almoner.getCommaNumberString(devcoins)))
	cString.write(' Administrator pay is %s shares, %s percent of the total.\n' % (administratorPay, percentPay))
	cString.write('\nPeople on that list will start getting those coins in round %s, starting at block %s,000.' % (suffixNumber, 4 * suffixNumber))
	cString.write(' The procedure for generating the receiver files is at:\n')
	cString.write('http://devtome.com/doku.php?id=devcoin#generating_the_files\n')
	cString.write('\nThe next bounties will go into round %s:\n' % suffixNumberPlusOne)
	cString.write('https://raw.github.com/Unthinkingbit/charity/master/bounty_%s.csv\n' % suffixNumberPlusOne)
	return cString.getvalue()

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	suffixNumberString = almoner.getParameter(arguments, '24', 'round')
	suffixNumber = int(suffixNumberString)
	outputAccountTo = almoner.getSuffixedFileName(almoner.getParameter(arguments, 'account.csv', 'account'), suffixNumberString)
	accountLines = getAccountLines(arguments, suffixNumberString)
	peerLines = getPeerLines(arguments)
	peerText = '_beginpeers\n%s_endpeers\n' % almoner.getTextByLines(peerLines)
	accountText = getPluribusunumText(peerText, accountLines)
	if almoner.sendOutputTo(outputAccountTo, accountText):
		print('The account file has been written to:\n%s\n' % outputAccountTo)
	outputReceiverTo = almoner.getSuffixedFileName(almoner.getParameter(arguments, 'receiver.csv', 'receiver'), suffixNumberString)
	outputSummaryTo = almoner.getParameter(arguments, 'receiver_summary.txt', 'summary')
	denominatorSequences = getDenominatorSequencesByAccountLines(accountLines)
	originalReceiverLines = getReceiverLinesByDenominatorSequences(denominatorSequences)
	receiverLines = getPackedReceiverLines(denominatorSequences, originalReceiverLines, suffixNumber)
	receiverText = getPluribusunumText(peerText, receiverLines)
	if almoner.sendOutputTo(outputReceiverTo, receiverText):
		print('The receiver file has been written to:\n%s\n' % outputReceiverTo)
		shaOutputPrefix = almoner.getParameter(arguments, '', 'sha')
		if len(shaOutputPrefix) != 0:
			sha256FileName = almoner.getSuffixedFileName(outputReceiverTo, shaOutputPrefix)
			almoner.writeFileText(sha256FileName, hashlib.sha256(receiverText).hexdigest())
			print('The sha256 receiver file has been written to:\n%s\n' % sha256FileName)
	if almoner.sendOutputTo(outputSummaryTo, getSummaryText(accountLines, originalReceiverLines, peerLines, suffixNumber)):
		print('The summary file has been written to:\n%s\n' % outputSummaryTo)


class AddressFraction:
	'A class to handle an address and associated fractions.'
	def __init__(self, line=''):
		'Initialize.'
		self.coinAddress = ''
		self.fractions = []
		words = line.split(',')
		if len(words) < 2:
			return
		self.coinAddress = words[1].strip()
		if len(words) < 3:
			self.fractions.append(Fraction())
			return
		for word in words[2 :]:
			dashIndex = word.find('-')
			if dashIndex != -1:
				word = word[: dashIndex]
			wordStripped = word.replace('/', '').strip()
			if wordStripped.isdigit() or len(wordStripped) == 0:
				self.fractions.append(Fraction(word))

	def __repr__(self):
		"Get the string representation of this class."
		return '%s, %s' % (self.coinAddress, self.fractions)


class Administrator:
	'A class to handle an administrator.'
	def __init__(self, line):
		'Initialize.'
		self.isFileAdministrator = False
		self.isGeneralAdministrator = False
		self.pay = 0.0
		lineSplit = line.split(',')
		if len(lineSplit) < 3:
			return
		self.name = lineSplit[0].strip()
		self.coinAddress = lineSplit[1].strip()
		for word in lineSplit:
			wordUntilBracket = word
			bracketIndex = word.find('(')
			if bracketIndex > -1:
				wordUntilBracket = word[: bracketIndex]
			if wordUntilBracket.endswith('-File Administrator'):
				self.isFileAdministrator = True
				numberStrings = wordUntilBracket[: wordUntilBracket.find('-')].split('/')
				firstFloat = float(numberStrings[0])
				if len(numberStrings) == 2:
					self.pay += firstFloat / float(numberStrings[1])
				else:
					self.pay += firstFloat
			elif 'Administrator' in wordUntilBracket:
				dashIndex = wordUntilBracket.find('-')
				if dashIndex != -1:
					self.pay += float(wordUntilBracket[: dashIndex])
					self.isGeneralAdministrator = True
					self.description = word[dashIndex + 1 :]

	def getAccountLine(self, bonusMultiplier):
		'Get account line.'
		return '%s,%s,%s-%s' % (self.name, self.coinAddress, bonusMultiplier, self.description)


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

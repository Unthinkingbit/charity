"""
<textarea id="wpTextbox1" name="wpTextbox1" cols="80" rows="25" readonly="">
==Articles==
===Collated===
*[[Home Remedy]] - Source: [http://en.wikibooks.org/wiki/Ethnomedicine/Ethnomedicine_by_Illness Ethnomedicine by Illness] and [http://en.wikibooks.org/wiki/Ethnomedicine/Home_Remedies Home Remedies] - Improvement: Combined wikibooks with wikipedia articles

===Original===
*[[:Arthritis]] - Source: Original
*[[:Devcoin]] - Source: [https://github.com/Unthinkingbit/charity/blob/master/devcoin.html https://github.com/Unthinkingbit/charity/blob/master/devcoin.html]

==Link==
https://raw.github.com/Unthinkingbit/charity/master/devcoin.html

==Tip==
Coin Address: 17vec4jQGCzMEsTnivizHPaowE715tu2CB
</textarea>


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

from datetime import date
import almoner
import cStringIO
import devtome
import random
import rating
import sys


__license__ = 'MIT'


def addWriter(line, previousVoteDictionary, writers):
	'Get the writers.'
	words = line.split(',')
	if len(words) < 2:
		return
	name = words[0].strip().lower()
	if name == '':
		return
	writer = Writer(name)
	if len(writer.articles) <= 0:
		return
	numberOfRatings = 0
	if name in previousVoteDictionary:
		numberOfRatings = len(previousVoteDictionary[name])
	if numberOfRatings > 8:
		return
	if numberOfRatings > 4:
		if random.random() > 0.2 * float(9 - numberOfRatings):
			return
	writers.append(writer)

def getBelowRaterWriters(name, raterWriters):
	'Get the rater writers whose name is 1 to 12 ordinals below, wrapped around.'
	nameOrdinal = getFirstLetterIndex(name)
	belowRaterWriters = []
	for raterWriter in raterWriters:
		raterOrdinal = getFirstLetterIndex(raterWriter.name)
		if raterOrdinal >= nameOrdinal:
			raterOrdinal -= 26
		if nameOrdinal - raterOrdinal <= 12:
			belowRaterWriters.append(raterWriter)
	return belowRaterWriters

def getFirstLetterIndex(name):
	'Get the index of the first letter, with A being 0, and anything other than a letter being 25.'
	firstLetterIndex = ord(name[0].lower()) - 97
	if firstLetterIndex < 0:
		return 25
	if firstLetterIndex > 25:
		return 25
	return firstLetterIndex

def getRaters(round):
	'Get the rater names.'
	raters = []
	lines = almoner.getTextLines(almoner.getFileText('rater_%s.csv' % round))
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 0:
			rater = words[0].strip().lower()
			if rater != '':
				raters.append(rater)
	return raters

def getRaterText(maximumWriters, round, seedString):
	'Get the rater text.'
	previousRaterDictionary = rating.getPreviousRaterDictionary(round)
	previousNameDictionary = {}
	writers = getWriters(round)
	random.shuffle(writers)
	cString = cStringIO.StringIO()
	otherWriters = []
	raterWriters = []
	raters = getRaters(round)
	raters.sort()
	raterSet = set(raters)
	for previousRaterKey in previousRaterDictionary.keys():
		previousRaters = previousRaterDictionary[previousRaterKey]
		for previousRater in previousRaters:
			if previousRater in previousNameDictionary:
				previousNameDictionary[previousRater].append(previousRaterKey)
			else:
				previousNameDictionary[previousRater] = [previousRaterKey]
	for writer in writers:
		if writer.name in raterSet:
			raterWriters.append(writer)
		else:
			otherWriters.append(writer)
	writersInRange = WriterRange(maximumWriters, otherWriters, previousNameDictionary, raterWriters)
	for raterIndex, rater in enumerate(raters):
		if raterIndex != 0:
			cString.write('\n\n\n')
		ratedWriters = writersInRange.getRatedWriters(rater)
		ratedWriters.sort(key=getWriterName)
		cString.write('Create:\n')
		cString.write('http://devtome.com/doku.php?id=rating_%s_%s\n\n' % (rater.lower(), round))
		cString.write('Copy and paste:\n')
		cString.write('Writer, Article: 0-99\n')
		for ratedWritersIndex, ratedWriter in enumerate(ratedWriters):
			articles = ratedWriter.articles
			articleLinkString = '[[%s]]' % articles[int(float(len(articles)) * random.random())].replace('_', ' ').capitalize()
			if ratedWritersIndex % 3 == 0 and ratedWritersIndex > 0:
				cString.write('\n')
			cString.write('*[[wiki:user:%s]], %s: \n' % (ratedWriter.name.capitalize(), articleLinkString))
	cString.write('\n\nRater seed string: %s\n' % seedString)
	return cString.getvalue()

def getWriterName(writer):
	'Get the name for sorting.'
	return writer.name

def getWriters(round):
	'Get the writers.'
	writers = []
	lines = almoner.getTextLines(almoner.getFileText('devtome_%s.csv' % (round - 1)))
	previousVoteDictionary = rating.getPreviousVoteDictionary(round)
	for line in lines[1 :]:
		addWriter(line, previousVoteDictionary, writers)
	return writers

def getWritersMinusNameSet(nameSet, writers):
	'Get the writers minus the names in the set.'
	writersMinusNameSet = []
	for writer in writers:
		if writer.name not in nameSet:
			writersMinusNameSet.append(writer)
	return writersMinusNameSet

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	round = int(almoner.getParameter(arguments, '27', 'round'))
	maximumWriters = int(almoner.getParameter(arguments, '12', 'writers'))
	outputRaterTo = 'rater_%s.txt' % round
	seedString = almoner.getParameter(arguments, date.today().isoformat(), 'seed')
	random.seed(seedString[: -1])
	raterText = getRaterText(maximumWriters, round, seedString)
	if almoner.sendOutputTo(outputRaterTo, raterText):
		print('The rater file has been written to:\n%s\n' % outputRaterTo)


class Writer:
	'A class to handle a writer.'
	def __init__(self, name):
		'Initialize.'
		self.articles = []
		self.name = name
		sourceAddress = 'http://devtome.com/doku.php?id=wiki:user:%s&do=edit' % self.name
		print('Loading user page from %s' % self.name)
		sourceText = almoner.getSourceText(sourceAddress)
		isCollated = False
		isOriginal = False
		for line in almoner.getTextLines(sourceText):
			lineStrippedLower = line.strip().lower()
			if '==' in lineStrippedLower:
				isCollated = False
				isOriginal = False
			if isCollated:
				lowerLinkName = devtome.getLinkName(line).lower()
				self.articles.append(lowerLinkName)
			if isOriginal:
				lowerLinkName = devtome.getLinkName(line).lower()
				self.articles.append(lowerLinkName)
			if '==' in lineStrippedLower:
				if 'collated' in lineStrippedLower:
					isCollated = True
				elif 'original' in lineStrippedLower:
					isOriginal = True

	def __repr__(self):
		'Get the string representation of this class.'
		return self.name

class WriterRange:
	'A class to handle a range of writers.'
	def __init__(self, maximumWriters, otherWriters, previousNameDictionary, raterWriters):
		'Initialize.'
		self.maximumWriters = maximumWriters
		self.otherWriters = otherWriters
		self.previousNameDictionary = previousNameDictionary
		self.raterQuantityMultiplier = float(maximumWriters) / float(len(otherWriters) + len(raterWriters)) * 26.0 / 12.0
		self.raterWriters = raterWriters
		self.writerIndex = 0

	def getRatedWriters(self, name):
		'Get the rated writers.'
		belowRaterWriters = getBelowRaterWriters(name, self.raterWriters)
		previousNameSet = set()
		if name in self.previousNameDictionary:
			previousNameSet = set(self.previousNameDictionary[name])
		belowRaterWriters = getWritersMinusNameSet(previousNameSet, belowRaterWriters)
		random.shuffle(belowRaterWriters)
		numberOfRatersFloat = self.raterQuantityMultiplier * len(belowRaterWriters)
		numberOfRaters = int(numberOfRatersFloat)
		if random.random() < numberOfRatersFloat - numberOfRaters:
			numberOfRaters += 1
		ratedWriters = belowRaterWriters[: numberOfRaters]
		if len(ratedWriters) >= self.maximumWriters:
			return ratedWriters[: self.maximumWriters]
		writersRemaining = self.maximumWriters - len(ratedWriters)
		otherWriters = getWritersMinusNameSet(previousNameSet, self.otherWriters)
		if writersRemaining >= len(otherWriters):
			return ratedWriters + otherWriters
		nextWriterIndex = (self.writerIndex + writersRemaining) % len(otherWriters)
		if nextWriterIndex > self.writerIndex:
			ratedWriters += otherWriters[self.writerIndex : nextWriterIndex]
		else:
			ratedWriters += otherWriters[self.writerIndex :] + otherWriters[: nextWriterIndex]
		self.writerIndex = nextWriterIndex
		return ratedWriters


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

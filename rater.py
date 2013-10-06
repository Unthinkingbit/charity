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
import sys


__license__ = 'MIT'


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

def getRaters():
	'Get the rater names.'
	raters = []
	lines = almoner.getTextLines(almoner.getFileText('rater.csv'))
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 0:
			rater = words[0].strip().lower()
			if rater != '':
				raters.append(rater)
	return raters

def getRaterText(maximumWriters, round, seedString):
	'Get the rater text.'
	writers = getWriters(round)
	random.shuffle(writers)
	cString = cStringIO.StringIO()
	otherWriters = []
	raterWriters = []
	raters = getRaters()
	raters.sort()
	raterSet = set(raters)
	for writer in writers:
		if writer.name in raterSet:
			raterWriters.append(writer)
		else:
			otherWriters.append(writer)
	writersInRange = WriterRange(maximumWriters, otherWriters, raterWriters)
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
	cString.write('\n\nRater seed: %s\n' % seedString)
	return cString.getvalue()

def getWriterName(writer):
	'Get the name for sorting.'
	return writer.name

def getWriters(round):
	'Get the writers.'
	writers = []
	lines = almoner.getTextLines(almoner.getFileText('devtome_%s.csv' % (round - 1)))
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 1:
			name = words[0].strip().lower()
			if name != '':
				writer = Writer(name)
				if len(writer.articles) > 0:
					writers.append(writer)
	return writers

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	round = int(almoner.getParameter(arguments, '27', 'round'))
	maximumWriters = int(almoner.getParameter(arguments, '12', 'writers'))
	outputRaterTo = 'rater_%s.csv' % round
	seedString = almoner.getParameter(arguments, date.today().isoformat(), 'seed')
	random.seed(seedString)
#	ratingFileName = almoner.getParameter(arguments, 'rating_%s.csv' % round, 'rating')
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
	def __init__(self, maximumWriters, otherWriters, raterWriters):
		'Initialize.'
		self.maximumWriters = maximumWriters
		self.otherWriters = otherWriters
		self.raterQuantityMultiplier = float(maximumWriters) / float(len(otherWriters) + len(raterWriters)) * 26.0 / 12.0
		self.raterWriters = raterWriters
		self.writerIndex = 0

	def getRatedWriters(self, name):
		'Get the rated writers.'
		belowRaterWriters = getBelowRaterWriters(name, self.raterWriters)
		random.shuffle(belowRaterWriters)
		numberOfRatersFloat = self.raterQuantityMultiplier * len(belowRaterWriters)
		numberOfRaters = int(numberOfRatersFloat)
		if random.random() < numberOfRatersFloat - numberOfRaters:
			numberOfRaters += 1
		ratedWriters = belowRaterWriters[: numberOfRaters]
		if len(ratedWriters) >= self.maximumWriters:
			return ratedWriters[: self.maximumWriters]
		writersRemaining = self.maximumWriters - len(ratedWriters)
		if writersRemaining >= len(self.otherWriters):
			return ratedWriters + self.otherWriters[:]
		nextWriterIndex = (self.writerIndex + writersRemaining) % len(self.otherWriters)
		if nextWriterIndex > self.writerIndex:
			ratedWriters += self.otherWriters[self.writerIndex : nextWriterIndex]
		else:
			ratedWriters += self.otherWriters[self.writerIndex :] + self.otherWriters[: nextWriterIndex]
		self.writerIndex = nextWriterIndex
		return ratedWriters


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

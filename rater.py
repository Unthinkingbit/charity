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

import almoner
import cStringIO
import devtome
import random
import sys


__license__ = 'MIT'


def getRaters():
	raters = []
	lines = almoner.getTextLines(almoner.getFileText('rater.csv'))
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 0:
			rater = words[0].strip()
			if rater != '':
				raters.append(rater)
	return raters

def getRaterText(maximumWriters, round):
	'Get the rater text.'
	cString = cStringIO.StringIO()
	raters = getRaters()
	raters.sort()
	writers = getWriters(round)
	random.shuffle(writers)
	writersInRange = WriterRange()
	for raterIndex, rater in enumerate(raters):
		if raterIndex != 0:
			cString.write('\n\n\n')
		ratedWriters = writersInRange.getRatedWriters(maximumWriters, round, raters, writers)
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
	return cString.getvalue()

def getWriterName(writer):
	'Get the name for sorting.'
	return writer.name

def getWriters(round):
	writers = []
	lines = almoner.getTextLines(almoner.getFileText('devtome_%s.csv' % round))
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 1:
			name = words[0].strip()
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
	random.seed(1) #delete this after test
	round = int(almoner.getParameter(arguments, '26', 'round'))
	maximumWriters = int(almoner.getParameter(arguments, '12', 'writers'))
	outputRaterTo = almoner.getParameter(arguments, 'rater_%s.csv' % round, 'rater')
#	ratingFileName = almoner.getParameter(arguments, 'rating_%s.csv' % round, 'rating')
	raterText = getRaterText(maximumWriters, round)
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
		sourceText = devtome.getSourceText(sourceAddress)
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
	def __init__(self):
		'Initialize.'
		self.writerIndex = 0

	def getRatedWriters(self, maximumWriters, round, unrateables, writers):
		'Get the rated writers.'
		numberOfWriters = len(writers)
		writersInRange = []
		maximumIndex = self.writerIndex + numberOfWriters
		while len(writersInRange) < maximumWriters and self.writerIndex < maximumIndex:
			writer = writers[self.writerIndex % numberOfWriters]
			if writer.name not in unrateables:
				writersInRange.append(writer)
			self.writerIndex += 1
		return writersInRange


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

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
import sys


__license__ = 'MIT'


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

def getRatings(round):
	'Get the ratings.'
	ratings = []
	return ratings

def getRatingsByAddress(address):
	'Get the ratings by address.'
	ratings = []
	firstUnderscore = address.find('_')
	if firstUnderscore == -1:
		print('Warning, no underscore in address.')
		return []
	lastUnderscore = address.rfind('_')
	if firstUnderscore == lastUnderscore:
		print('Warning, firstUnderscore same as lastUnderscore.')
		return []
	rater = address[firstUnderscore + 1 : lastUnderscore]
	lines = almoner.getTextLines(devtome.getSourceText(address))
	for line in lines[1 :]:
		rating = Rating(address, line, rater)
		if rating.article != '':
			ratings.append(rating)
	return ratings

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	round = int(almoner.getParameter(arguments, '27', 'round'))
	outputRatingTo = almoner.getParameter(arguments, 'rating_%s.csv' % round, 'rating')
	ratings = getRatingsByAddress('http://devtome.com/doku.php?id=rating_unthinkingbit_27&do=edit')
	print(  ratings)
	return ###
	ratingText = getRatingText(maximumWriters, round)
	if almoner.sendOutputTo(outputRatingTo, ratingText):
		print('The rating file has been written to:\n%s\n' % outputRatingTo)


class Rating:
	'A class to handle a rating.'
	def __init__(self, address, line, rater):
		'Initialize.'
		self.address = address
		self.article = ''
		self.comment = ''
		self.ratee = ''
		self.rater = rater
		self.vote = 0
		if not line.startswith('*[[wiki:user:'):
			return
		words = line.split(']]:')
		if len(words) < 2:
			return
		ratingLine = words[1].strip()
		spaceIndex = ratingLine.find(' ')
		voteString = ratingLine
		if spaceIndex != -1:
			voteString = ratingLine[: spaceIndex]
			self.comment = ratingLine[spaceIndex :].strip()
		if not voteString.isdigit():
			return
		self.vote = int(voteString)
		raterLine = words[0].strip()
		raterWords = raterLine.split(']], [[')
		if len(raterWords) < 2:
			return
		self.ratee = raterWords[0][len('*[[wiki:user:') :].strip()
		if self.ratee == '':
			return
		self.article = raterWords[1].strip()

	def __repr__(self):
		'Get the string representation of this class.'
		return '%s, %s: %s' % (self.ratee, self.rater, self.vote)


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

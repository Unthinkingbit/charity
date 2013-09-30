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
import math
import sys


__license__ = 'MIT'


def getEarningsText(ratings):
	'Get the ratings earnings text.'
	cString = cStringIO.StringIO()
	raterDictionary = {}
	for rating in ratings:
		if rating.rater in raterDictionary:
			raterDictionary[rating.rater].append(rating)
		else:
			raterDictionary[rating.rater] = [rating]
	raterKeys = raterDictionary.keys()
	raterKeys.sort()
	for raterKey in raterKeys:
		rating = raterDictionary[raterKey][0]
		cString.write('%s,%s,%s-Rating Comments(%s)\n' % (rating.rater, 'coin address', '2', rating.address.replace('&do=edit', '')))
	return cString.getvalue()

def getRatingText(ratings):
	'Get the rating text.'
	cString = cStringIO.StringIO()
	maxLength = 0
	authorDictionary = {}
	for rating in ratings:
		if rating.author in authorDictionary:
			authorDictionary[rating.author].addRating(rating)
		else:
			authorDictionary[rating.author] = Author(rating)
	authorKeys = authorDictionary.keys()
	authorKeys.sort()
	for authorKey in authorKeys:
		maxLength = max(maxLength, len(authorDictionary[authorKey].ratings))
	titles = ['Author', 'All Votes', 'Median']
	for voteIndex in xrange(maxLength):
		titles.append('Address')
		titles.append('Vote')
	cString.write('%s\n' % ','.join(titles))
	for authorKey in authorKeys:
		authorDictionary[authorKey].addLine(cString)
	return cString.getvalue()

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
	lines = almoner.getTextLines(almoner.getSourceText(address))
	for line in lines[1 :]:
		rating = Rating(address, line, rater)
		if rating.article != '':
			ratings.append(rating)
	return ratings

def getRatings(round):
	'Get the ratings by the round.'
	lines = almoner.getTextLines(almoner.getFileText('rater_%s.csv' % round))
	ratings = []
	for line in lines:
		if line.startswith('http://devtome.com/doku.php?id=rating_'):
			ratings += getRatingsByAddress('%s&do=edit' % line.strip())
	return ratings

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	round = int(almoner.getParameter(arguments, '27', 'round'))
	ratings = getRatings(round)
	ratingText = getRatingText(ratings)
	earningsText = getEarningsText(ratings)
	outputEarningsTo = almoner.getParameter(arguments, 'rating_earnings_%s.csv' % round, 'earnings')
	outputRatingTo = almoner.getParameter(arguments, 'rating_%s.csv' % round, 'rating')
	if almoner.sendOutputTo(outputEarningsTo, earningsText):
		print('The rating earnings file has been written to:\n%s\n' % outputEarningsTo)
	if almoner.sendOutputTo(outputRatingTo, ratingText):
		print('The rating file has been written to:\n%s\n' % outputRatingTo)


class Author:
	'A class to handle an author.'
	def __init__(self, rating):
		'Initialize.'
		self.name = rating.author
		self.ratings = []
		self.addRating(rating)

	def addLine(self, cString):
		'Add the author to the rating csv cString.'
		votes = []
		for rating in self.ratings:
			votes.append(rating.vote)
		votes.sort()
		voteStrings = []
		for vote in votes:
			voteStrings.append(str(vote))
		halfLength = len(voteStrings) / 2
		median = float(votes[halfLength])
		if len(voteStrings) % 2 == 0:
			median = 0.5 * (median + float(votes[halfLength - 1]))
		fields = [self.name, '-'.join(voteStrings), str(median)]
		for rating in self.ratings:
			fields.append(rating.address)
			fields.append(str(rating.vote))
		cString.write('%s\n' % ','.join(fields))

	def addRating(self, rating):
		'Add rating vote.'
		self.ratings.append(rating)


class Rating:
	'A class to handle a rating.'
	def __init__(self, address, line, rater):
		'Initialize.'
		self.address = address
		self.article = ''
		self.author = ''
		self.comment = ''
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
		self.author = raterWords[0][len('*[[wiki:user:') :].strip()
		if self.author == '':
			return
		self.article = raterWords[1].strip()

	def __repr__(self):
		'Get the string representation of this class.'
		return '%s, %s: %s' % (self.ratee, self.rater, self.vote)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

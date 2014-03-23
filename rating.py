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

import account
import almoner
import cStringIO
import sys


__license__ = 'MIT'


def getAddress(addressName):
	'Get the address for sorting.'
	return addressName.address

def getEarningsText(ratings, recipientDictionary):
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
		numberOfComments = 0
		numberOfRatings = 0
		for rating in raterDictionary[raterKey]:
			if len(rating.comment) > 5:
				numberOfComments += 1
			numberOfRatings += 1
		earning = min(3, numberOfRatings) + int(round(0.35 * float(min(numberOfComments, 5))))
		rating = raterDictionary[raterKey][0]
		coinAddress = recipientDictionary[raterKey]
		cString.write('%s,%s,%s-Rating Comments(%s)\n' % (raterKey.capitalize(), coinAddress, earning, rating.address.replace('&do=edit', '')))
	return cString.getvalue()

def getMedian(values):
	'Get the median.'
	halfLength = len(values) / 2
	median = float(values[halfLength])
	if len(values) % 2 == 1:
		return median
	return 0.5 * (median + float(values[halfLength - 1]))

def getPreviousAddressVoteDictionary(previousLines):
	'Get the address vote dictionary from the previous round.'
	if len(previousLines) < 2:
		return {}
	titles = previousLines[0].lower().split(',')
	previousAddressVoteDictionary = {}
	for line in previousLines[1 :]:
		words = line.split(',')
		for wordIndex, word in enumerate(words):
			nextIndex = wordIndex + 1
			if len(words) > nextIndex and len(titles) > nextIndex:
				if titles[wordIndex].strip() == 'address' and titles[nextIndex].strip() == 'vote':
					name = words[0].strip().lower()
					if len(name) > 0:
						address = words[wordIndex].strip().lower()
						vote = words[nextIndex].strip().lower()
						addressVote = AddressVote(address, vote)
						if name in previousAddressVoteDictionary:
							previousAddressVoteDictionary[name].append(addressVote)
						else:
							previousAddressVoteDictionary[name] = [addressVote]
	return previousAddressVoteDictionary

def getPreviousAddressVotes(name, previousAddressVoteDictionary):
	'Get the previous address votes.'
	if name in previousAddressVoteDictionary:
		return previousAddressVoteDictionary[name]
	return []

def getRatings(round):
	'Get the ratings by the round.'
	lines = almoner.getTextLines(almoner.getFileText('rater_%s.txt' % round))
	ratings = []
	for line in lines:
		if line.startswith('http://devtome.com/doku.php?id=rating_'):
			ratings += getRatingsByAddress('%s&do=edit' % line.strip())
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
	rater = address[firstUnderscore + 1 : lastUnderscore].lower()
	lines = almoner.getTextLines(almoner.getSourceText(address))
	for line in lines[1 :]:
		rating = Rating(address, line, rater)
		if rating.article != '':
			ratings.append(rating)
	return ratings

def getRatingText(ratings, round):
	'Get the rating text.'
	cString = cStringIO.StringIO()
	maxLength = 0
	authorDictionary = {}
	previousLines = almoner.getTextLines(almoner.getFileText('rating_%s.csv' % (round - 1)))
	previousAddressVoteDictionary = getPreviousAddressVoteDictionary(previousLines)
	for rating in ratings:
		if rating.author in authorDictionary:
			authorDictionary[rating.author].addRating(rating)
		else:
			previousAddressVotes = getPreviousAddressVotes(rating.author, previousAddressVoteDictionary)
			author = Author(previousAddressVotes, rating.author)
			author.addRating(rating)
			authorDictionary[rating.author] = author
	for name in previousAddressVoteDictionary:
		if name not in authorDictionary:
			previousAddressVotes = getPreviousAddressVotes(name, previousAddressVoteDictionary)
			authorDictionary[name] = Author(previousAddressVotes, name)
	authorKeys = authorDictionary.keys()
	authorKeys.sort()
	for authorKey in authorKeys:
		maxLength = max(maxLength, len(authorDictionary[authorKey].addressVotes))
	titles = ['Author', 'All Votes', 'Median', 'Raters']
	for voteIndex in xrange(maxLength):
		titles.append('Address')
		titles.append('Vote')
	cString.write('%s\n' % ','.join(titles))
	for authorKey in authorKeys:
		authorDictionary[authorKey].addLine(cString)
	return cString.getvalue()

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	round = int(almoner.getParameter(arguments, '27', 'round'))
	ratings = getRatings(round)
	recipientDictionary = account.getRecipientDictionary(round)
	earningsText = getEarningsText(ratings, recipientDictionary)
	ratingText = getRatingText(ratings, round)
	outputEarningsTo = almoner.getParameter(arguments, 'rating_earnings_%s.csv' % round, 'earnings')
	outputRatingTo = 'rating_%s.csv' % round
	if almoner.sendOutputTo(outputEarningsTo, earningsText):
		print('The rating earnings file has been written to:\n%s\n' % outputEarningsTo)
	if almoner.sendOutputTo(outputRatingTo, ratingText):
		print('The rating file has been written to:\n%s\n' % outputRatingTo)


class AddressVote:
	'A class to hold an address and vote.'
	def __init__(self, address, vote):
		'Initialize.'
		self.address = address
		self.vote = vote


class Author:
	'A class to handle an author.'
	def __init__(self, addressVotes, name):
		'Initialize.'
		self.addressVotes = addressVotes
		self.name = name
		self.ratings = []

	def addLine(self, cString):
		'Add the author to the rating csv cString.'
		self.addressVotes.sort(key=getAddress)
		raters = []
		votes = []
		for addressVote in self.addressVotes:
			rater = addressVote.address
			ratingIndex = rater.find('rating_')
			if ratingIndex != -1:
				rater = rater[ratingIndex + len('rating_') :]
			underscoreIndex = rater.rfind('_')
			if underscoreIndex != -1:
				rater = rater[: underscoreIndex]
			if rater not in raters:
				raters.append(rater)
			votes.append(addressVote.vote)
		raters.sort()
		votes.sort()
		voteStrings = []
		for vote in votes:
			voteStrings.append(str(vote))
		fields = [self.name, '-'.join(voteStrings), str(getMedian(votes)), '-'.join(raters)]
		for addressVote in self.addressVotes:
			fields.append(addressVote.address)
			fields.append(str(addressVote.vote))
		cString.write('%s\n' % ','.join(fields))

	def addRating(self, rating):
		'Add rating vote.'
		self.ratings.append(rating)
		addressVote = AddressVote(rating.address.replace('&do=edit', ''), rating.vote)
		self.addressVotes.append(addressVote)


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
			voteString = ratingLine[: spaceIndex].strip()
			self.comment = ratingLine[spaceIndex :].strip()
		voteString = voteString.replace(',', '').replace("'", '').replace('"', '').replace(".", '').replace(";", '')
		if not voteString.isdigit():
			if voteString != '':
				print('Warning, not a pure number in:')
				print(address)
				print(line)
			return
		self.vote = int(voteString)
		raterLine = words[0].strip()
		raterWords = raterLine.split(']], [[')
		if len(raterWords) < 2:
			return
		self.author = raterWords[0][len('*[[wiki:user:') :].strip().lower()
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

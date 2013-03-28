"""
<textarea id="wpTextbox1" name="wpTextbox1" cols="80" rows="25" readonly="">==Articles==
===Collated===
*[[Home Remedy]] - Source: [http://en.wikibooks.org/wiki/Ethnomedicine/Ethnomedicine_by_Illness Ethnomedicine by Illness] and [http://en.wikibooks.org/wiki/Ethnomedicine/Home_Remedies Home Remedies] - Improvement: Combined wikibooks with wikipedia articles

===Original===
*[[Devcoin]] - Source: [https://github.com/Unthinkingbit/charity/blob/master/devcoin.html https://github.com/Unthinkingbit/charity/blob/master/devcoin.html]
*[[Devcoin_bounty|Devcoin Bounty]] - Source: [https://github.com/Unthinkingbit/charity/blob/master/devcoin_bounty.html https://github.com/Unthinkingbit/charity/blob/master/devcoin_bounty.html]

==Tip==
Coin Address: 17vec4jQGCzMEsTnivizHPaowE715tu2CB</textarea>


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
import math
import sys


__license__ = 'MIT'


def addJoinedTitles(cString, payoutBegin, payoutEnd, words):
	'Add joined titles to the cString.'
	words.append('Collated Word Count')
	words.append('Collated Weighted Word Count')
	words.append('Image Count')
	words.append('Original Word Count')
	words.append('Word Count')
	words.append('Weighted Word Count')
	for payoutIndex in xrange(payoutBegin, payoutEnd + 1):
		words.append('Payout %s' % str(payoutIndex))
	words.append('Cumulative Payout')
	words.append('Proportion')
	cString.write('%s\n' % ','.join(words))

def getAuthors(lines, payoutBegin, payoutEnd, titles):
	'Get the authors.'
	authors = []
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 0:
			if len(words[0]) > 0:
				authors.append(Author(payoutBegin, payoutEnd, titles, words))
	return authors

def getBountyText(authors):
	'Get the devtome bounty text.'
	cString = cStringIO.StringIO()
	for author in authors:
		coinAddress = author.parameterDictionary['Coin Address']
		name = author.parameterDictionary['Name']
		lastPayoutString = str(author.tomecount.payouts[-1])
		if lastPayoutString != '0':
			cString.write('%s-%s,%s-Word Count(%s)\n' % (coinAddress, name, lastPayoutString, author.sourceAddress))
	return cString.getvalue()

def getImageCount(linkText):
	'Get the image count of the page linked to in the line.'
	if linkText == '':
		return 0
	imageCount = 0
	lines = linkText.lower().split('[[')
	for line in lines:
		if line.startswith('file:') or line.startswith('image:'):
			if (']]') in line:
				line = line[: line.find(']]')].strip()
			if ('|') in line:
				line = line[: line.find('|')].strip()
			if line.endswith('.gif') or line.endswith('.jpg') or line.endswith('.png'):
				imageCount += 1
	return imageCount

def getLinkText(line):
	'Get the text of the page linked to in the line.'
	linkStartIndex = line.find('[[')
	if linkStartIndex == -1:
		return ''
	linkStartIndex += len('[[')
	linkEndIndex = line.find(']]', linkStartIndex)
	if linkEndIndex == -1:
		return ''
	linkString = line[linkStartIndex : linkEndIndex]
	linkDividerIndex = linkString.find('|')
	if linkDividerIndex != -1:
		linkString = linkString[: linkDividerIndex]
	return getSourceText('http://devtome.com/doku.php?id=%s&do=edit' % linkString)

def getSourceText(address):
	'Get the devtome source text for the address.'
	text = almoner.getInternetText(address)
	textAreaTagIndex = text.find('<textarea')
	if textAreaTagIndex == -1:
		print('Warning, no textarea tag found for:')
		print(address)
		return ''
	tagEndIndex = text.find('>', textAreaTagIndex)
	if tagEndIndex == -1:
		print('Warning, no tag end found for:')
		print(address)
		return ''
	textAreaEndTagIndex = text.find('</textarea>', tagEndIndex)
	if textAreaEndTagIndex == -1:
		print('Warning, no textarea end tag found for:')
		print(address)
		return ''
	return text[tagEndIndex + 1 : textAreaEndTagIndex].lstrip()

def getTomecountText(authors, payoutBegin, payoutEnd):
	'Get the tomecount csv text for the authors.'
	cString = cStringIO.StringIO()
	addJoinedTitles(cString, payoutBegin, payoutEnd, ['Name','Coin Address'])
	totalTomecount = Tomecount(payoutBegin, payoutEnd)
	totalTomecount.proportion = 1.0
	for author in authors:
		totalTomecount.collatedWordCount += author.tomecount.collatedWordCount
		totalTomecount.collatedWeightedWordCount += author.tomecount.collatedWeightedWordCount
		totalTomecount.imageCount += author.tomecount.imageCount
		totalTomecount.originalWordCount += author.tomecount.originalWordCount
		totalTomecount.wordCount += author.tomecount.wordCount
		totalTomecount.weightedWordCount += author.tomecount.weightedWordCount
		totalTomecount.cumulativePayout += author.tomecount.cumulativePayout
		for payoutIndex, payout in enumerate(author.tomecount.payouts):
			totalTomecount.payouts[payoutIndex] += payout
	weightedWordCountFloat = float(totalTomecount.weightedWordCount)
	for author in authors:
		author.tomecount.proportion = float(author.tomecount.weightedWordCount) / weightedWordCountFloat
		author.addLine(cString)
	addJoinedTitles(cString, payoutBegin, payoutEnd, ['','Totals'])
	cString.write(totalTomecount.getJoinedWords(['','']))
	cString.write(',Date\n')
	cString.write(',%s\n' % date.today().isoformat())
	return cString.getvalue()

def getWordCount(linkText):
	'Get the word count of the page linked to in the line.'
	if linkText == '':
		return 0
	linkText = linkText.replace('.', ' ').replace(',', ' ').replace(';', ' ').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
	return len(linkText.split())

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	fileName = almoner.getParameter(arguments, 'tomecount.csv', 'input')
	payoutEnd = int(almoner.getParameter(arguments, '8', 'payout'))
	payoutBegin = payoutEnd
	lines = almoner.getTextLines(almoner.getFileText(fileName))
	titleLine = lines[0]
	titles = titleLine.split(',')
	for title in titles[: : -1]:
		if title.startswith('Payout'):
			payoutBegin = int(title.split()[1])
	authors = getAuthors(lines, payoutBegin, payoutEnd, titles)
	tomecountText = getTomecountText(authors, payoutBegin, payoutEnd)
	bountyText = getBountyText(authors)
	almoner.writeFileText(fileName, tomecountText)
	outputBountyTo = almoner.getSuffixedFileName(almoner.getParameter(arguments, 'devtome_bounty.csv', 'outputbounty'), str(payoutEnd))
	if almoner.sendOutputTo(outputBountyTo, bountyText):
		print('The devtome bounty file has been written to:\n%s\n' % outputBountyTo)


class Author:
	'A class to handle an author.'
	def __init__(self, payoutBegin, payoutEnd, titles, words):
		'Initialize.'
		self.tomecount = Tomecount(payoutBegin, payoutEnd)
		self.parameterDictionary = {}
		for wordIndex, word in enumerate(words):
			self.parameterDictionary[titles[wordIndex]] = word
		for payoutIndex in xrange(payoutBegin, payoutEnd):
			payoutTitle = 'Payout %s' % str(payoutIndex)
			if payoutTitle in self.parameterDictionary:
				self.tomecount.payouts[payoutIndex - payoutBegin] = int(self.parameterDictionary[payoutTitle])
		name = self.parameterDictionary['Name']
		self.sourceAddress = 'http://devtome.com/doku.php?id=wiki:user:%s&do=edit' % name
		print('Loading articles from %s' % name)
		sourceText = getSourceText(self.sourceAddress)
		isCollated = False
		isOriginal = False
		for line in almoner.getTextLines(sourceText):
			lineStrippedLower = line.strip().lower()
			if '==' in lineStrippedLower:
				isCollated = False
				isOriginal = False
				if 'collated' in lineStrippedLower:
					isCollated = True
				elif 'original' in lineStrippedLower:
					isOriginal = True
			if isCollated:
				linkText = getLinkText(lineStrippedLower)
				self.tomecount.imageCount += getImageCount(linkText)
				wordCount = getWordCount(linkText)
				self.tomecount.collatedWordCount += wordCount
				if wordCount > 0:
					print('Collated article: %s, Word Count: %s' % (lineStrippedLower, wordCount))
			if isOriginal:
				linkText = getLinkText(lineStrippedLower)
				self.tomecount.imageCount += getImageCount(linkText)
				wordCount = getWordCount(linkText)
				self.tomecount.originalWordCount += wordCount
				if wordCount > 0:
					print('Original article: %s, Word Count: %s' % (lineStrippedLower, wordCount))
		self.tomecount.collatedWeightedWordCount = self.tomecount.collatedWordCount * 3 / 10
		self.tomecount.wordCount = self.tomecount.collatedWordCount + self.tomecount.originalWordCount
		self.tomecount.weightedWordCount = self.tomecount.collatedWeightedWordCount + self.tomecount.originalWordCount
		self.tomecount.weightedWordCount += 10 * self.tomecount.imageCount
		self.tomecount.cumulativePayout = int(round(float(self.tomecount.weightedWordCount) * 0.001))
		print('Weighted Word Count: %s' % self.tomecount.weightedWordCount)
		lastPayout = self.tomecount.cumulativePayout
		for payout in self.tomecount.payouts[: -1]:
			lastPayout -= payout
		self.tomecount.payouts[-1] = max(lastPayout, 0)

	def __repr__(self):
		'Get the string representation of this class.'
		return str(self.parameterDictionary)

	def addLine(self, cString):
		'Add the author to the tomecount csv cString.'
		words = [self.parameterDictionary['Name'], self.parameterDictionary['Coin Address']]
		cString.write(self.tomecount.getJoinedWords(words))


class Tomecount:
	'A class to handle the tome accounting.'
	def __init__(self, payoutBegin, payoutEnd):
		'Initialize.'
		self.collatedWordCount = 0
		self.imageCount = 0
		self.originalWordCount = 0
		self.collatedWeightedWordCount = 0
		self.payouts = [0] * (payoutEnd + 1 - payoutBegin)
		self.proportion = 0.0
		self.wordCount = 0
		self.weightedWordCount = 0
		self.cumulativePayout = 0

	def __repr__(self):
		'Get the string representation of this class.'
		return self.getJoinedWords([])

	def getJoinedWords(self, words):
		'Add the variables to the words.'
		words.append(str(self.collatedWordCount))
		words.append(str(self.collatedWeightedWordCount))
		words.append(str(self.imageCount))
		words.append(str(self.originalWordCount))
		words.append(str(self.wordCount))
		words.append(str(self.weightedWordCount))
		for payout in self.payouts:
			words.append(str(payout))
		words.append(str(self.cumulativePayout))
		words.append(str(self.proportion))
		return '%s\n' % ','.join(words)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

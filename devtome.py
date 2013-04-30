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
import os
import shutil
import sys
import time


__license__ = 'MIT'


def addJoinedTitles(cString, words):
	'Add joined titles to the cString.'
	words.append('Collated Word Count')
	words.append('Collated Weighted Word Count')
	words.append('Image Count')
	words.append('Original Word Count')
	words.append('Word Count')
	words.append('Weighted Word Count')
	words.append('Cumulative Payout')
	words.append('Proportion')
	words.append('Previous Cumulative Payout')
	words.append('Payout')
	cString.write('%s\n' % ','.join(words))

def getAuthors(backupFolder, lines, titles):
	'Get the authors.'
	authors = []
	if os.path.isdir(backupFolder):
		shutil.rmtree(backupFolder)
	os.makedirs(backupFolder)
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 0:
			if len(words[0]) > 0:
				authors.append(Author(backupFolder, titles, words))
	almoner.writeZipFileByFolder(backupFolder)
	return authors

def getEarningsText(authors):
	'Get the devtome earnings text.'
	cString = cStringIO.StringIO()
	for author in authors:
		coinAddress = author.parameterDictionary['Coin Address']
		name = author.parameterDictionary['Name']
		lastPayoutString = str(author.tomecount.payout)
		if lastPayoutString != '0':
			cString.write('%s,%s,%s-Word Count(%s)\n' % (name, coinAddress, lastPayoutString, author.sourceAddress.replace('&do=edit', '')))
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

def getLinkName(line):
	'Get the name of the article in the line.'
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
	return linkString

def getLinkText(line):
	'Get the text of the page linked to in the line.'
	linkString = getLinkName(line)
	if linkString == '':
		return ''
	time.sleep(1)
	return getSourceText('http://devtome.com/doku.php?id=%s&do=edit' % linkString)

def getSourceText(address):
	'Get the devtome source text for the address.'
	text = almoner.getInternetText(address)
	textAreaTagIndex = text.find('<textarea')
	if textAreaTagIndex == -1:
		print('')
		print('Warning, no textarea tag found for:')
		print(address)
		print('')
		return ''
	tagEndIndex = text.find('>', textAreaTagIndex)
	if tagEndIndex == -1:
		print('')
		print('Warning, no tag end found for:')
		print(address)
		print('')
		return ''
	textAreaEndTagIndex = text.find('</textarea>', tagEndIndex)
	if textAreaEndTagIndex == -1:
		print('')
		print('Warning, no textarea end tag found for:')
		print(address)
		print('')
		return ''
	return text[tagEndIndex + 1 : textAreaEndTagIndex].lstrip()

def getSummaryText(earningsText, round, totalTomecount):
	'Get the summary text.'
	cString = cStringIO.StringIO()
	cString.write('The round %s devtome word earnings are pasted below and at:\n' % round)
	cString.write('https://raw.github.com/Unthinkingbit/charity/master/devtome_earnings_%s.csv\n\n' % round)
	cString.write('%s\n' % earningsText)
	cString.write('They are generated by devtome.py:\n')
	cString.write('https://raw.github.com/Unthinkingbit/charity/master/devtome.py\n\n')
	cString.write('The word counts for each writer are at:\n')
	cString.write('https://raw.github.com/Unthinkingbit/charity/master/devtome_%s.csv\n\n' % round)
	cString.write('The word earnings were generated on %s, and the total word counts follow below.\n\n' % date.today().isoformat())
	cString.write('Collated Word Count: %s\n' % almoner.getCommaNumberString(totalTomecount.collatedWordCount))
	cString.write('Collated Weighted Word Count: %s\n' % almoner.getCommaNumberString(totalTomecount.collatedWeightedWordCount))
	cString.write('Images: %s\n' % almoner.getCommaNumberString(totalTomecount.imageCount))
	cString.write('Original Word Count: %s\n' % almoner.getCommaNumberString(totalTomecount.originalWordCount))
	cString.write('Total Word Count: %s\n' % almoner.getCommaNumberString(totalTomecount.wordCount))
	cString.write('Total Weighted Word Count: %s\n' % almoner.getCommaNumberString(totalTomecount.weightedWordCount))
	return cString.getvalue()

def getTomecountText(authors, totalTomecount):
	'Get the tomecount csv text for the authors.'
	cString = cStringIO.StringIO()
	addJoinedTitles(cString, ['Name','Coin Address'])
	weightedWordCountFloat = float(totalTomecount.weightedWordCount)
	for author in authors:
		author.tomecount.proportion = float(author.tomecount.weightedWordCount) / weightedWordCountFloat
		author.addLine(cString)
	addJoinedTitles(cString, ['','Totals'])
	cString.write(totalTomecount.getJoinedWords(['','']))
	cString.write(',Date\n')
	cString.write(',%s\n' % date.today().isoformat())
	return cString.getvalue()

def getTotalTomecount(authors):
	'Get the tomecount csv text for the authors.'
	totalTomecount = Tomecount()
	totalTomecount.proportion = 1.0
	for author in authors:
		totalTomecount.collatedWordCount += author.tomecount.collatedWordCount
		totalTomecount.collatedWeightedWordCount += author.tomecount.collatedWeightedWordCount
		totalTomecount.imageCount += author.tomecount.imageCount
		totalTomecount.originalWordCount += author.tomecount.originalWordCount
		totalTomecount.wordCount += author.tomecount.wordCount
		totalTomecount.weightedWordCount += author.tomecount.weightedWordCount
		totalTomecount.cumulativePayout += author.tomecount.cumulativePayout
		totalTomecount.payout += author.tomecount.payout
		totalTomecount.previousPayout += author.tomecount.previousPayout
	return totalTomecount

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
	round = int(almoner.getParameter(arguments, '23', 'round'))
	rootFileName = almoner.getParameter(arguments, 'devtome', 'wiki')
	currentFileName = almoner.getParameter(arguments, rootFileName + '_%s.csv' % round, 'current')
	previousFileName = almoner.getParameter(arguments, rootFileName + '_%s.csv' % (round - 1), 'previous')
	lines = almoner.getTextLines(almoner.getFileText(previousFileName))
	titleLine = lines[0]
	titles = titleLine.split(',')
	backupFolder = rootFileName + '_backup'
	authors = getAuthors(backupFolder, lines, titles)
	totalTomecount = getTotalTomecount(authors)
	tomecountText = getTomecountText(authors, totalTomecount)
	earningsText = getEarningsText(authors)
	outputSummaryTo = almoner.getParameter(arguments, 'devtome_summary.txt', 'summary')
	almoner.writeFileText(currentFileName, tomecountText)
	outputEarningsTo = almoner.getParameter(arguments, 'devtome_earnings_%s.csv' % round, 'earnings')
	if almoner.sendOutputTo(outputEarningsTo, earningsText):
		print('The devtome earnings file has been written to:\n%s\n' % outputEarningsTo)
	if almoner.sendOutputTo(outputSummaryTo, getSummaryText(earningsText, round, totalTomecount)):
		print('The summary file has been written to:\n%s\n' % outputSummaryTo)


class Author:
	'A class to handle an author.'
	def __init__(self, backupFolder, titles, words):
		'Initialize.'
		self.tomecount = Tomecount()
		self.parameterDictionary = {}
		for wordIndex, word in enumerate(words):
			self.parameterDictionary[titles[wordIndex]] = word
		if 'Cumulative Payout' in self.parameterDictionary:
			self.tomecount.previousPayout = int(self.parameterDictionary['Cumulative Payout'])
		name = self.parameterDictionary['Name']
		self.sourceAddress = 'http://devtome.com/doku.php?id=wiki:user:%s&do=edit' % name
		print('Loading articles from %s' % name)
		sourceText = getSourceText(self.sourceAddress)
		almoner.writeFileText(os.path.join(backupFolder, 'wiki:user:' + name), sourceText)
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
					almoner.writeFileText(os.path.join(backupFolder, getLinkName(lineStrippedLower)[1 :]), linkText)
			if isOriginal:
				linkText = getLinkText(lineStrippedLower)
				self.tomecount.imageCount += getImageCount(linkText)
				wordCount = getWordCount(linkText)
				self.tomecount.originalWordCount += wordCount
				if wordCount > 0:
					print('Original article: %s, Word Count: %s' % (lineStrippedLower, wordCount))
					almoner.writeFileText(os.path.join(backupFolder, getLinkName(lineStrippedLower)[1 :]), linkText)
		self.tomecount.collatedWeightedWordCount = self.tomecount.collatedWordCount * 3 / 10
		self.tomecount.wordCount = self.tomecount.collatedWordCount + self.tomecount.originalWordCount
		self.tomecount.weightedWordCount = self.tomecount.collatedWeightedWordCount + self.tomecount.originalWordCount
		self.tomecount.weightedWordCount += 10 * self.tomecount.imageCount
		self.tomecount.cumulativePayout = int(round(float(self.tomecount.weightedWordCount) * 0.001))
		print('Weighted Word Count: %s' % self.tomecount.weightedWordCount)
		self.tomecount.payout = max(self.tomecount.cumulativePayout - self.tomecount.previousPayout, 0)

	def __repr__(self):
		'Get the string representation of this class.'
		return str(self.parameterDictionary)

	def addLine(self, cString):
		'Add the author to the tomecount csv cString.'
		words = [self.parameterDictionary['Name'], self.parameterDictionary['Coin Address']]
		cString.write(self.tomecount.getJoinedWords(words))


class Tomecount:
	'A class to handle the tome accounting.'
	def __init__(self):
		'Initialize.'
		self.collatedWordCount = 0
		self.imageCount = 0
		self.originalWordCount = 0
		self.collatedWeightedWordCount = 0
		self.payout = 0
		self.previousPayout = 0
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
		words.append(str(self.cumulativePayout))
		words.append(str(self.proportion))
		words.append(str(self.previousPayout))
		words.append(str(self.payout))
		return '%s\n' % ','.join(words)

def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

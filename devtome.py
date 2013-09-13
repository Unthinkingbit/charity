"""
Devtome is a program to calculate the writer earnings.

The weighted word counts for all the articles invoiced by the writer are totalled. The word count is divided by a thousand to get the total number of shares. The total minus the total of the previous round is the earnings for that round, which is written to the earnings file. All the statistics for the writers for that round are written to the devtome file.

The weighted word count is the sum of the words, plus the number of images times ten. If the article is in the collated section, the total is multiplied by 0.3. The writers are read from the devtome file of the previous round.

==Commands==
===Help===
The -h option, or the -help option, will print the help, which is this document. The example follows:
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
	words.append('Unique Page Views')
	words.append('Normalized Root Worth')
	words.append('Bounded Earnings Multiplier')
	words.append('Earnings')
	cString.write('%s\n' % ','.join(words))

def getAuthors(backupFolder, lines, titles, viewDictionary):
	'Get the authors.'
	authors = []
	authorSet = set([])
	almoner.makeDirectory(backupFolder)
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 0:
			if len(words[0]) > 0:
				author = Author(backupFolder, titles, viewDictionary, words)
				if author.name not in authorSet:
					authorSet.add(author.name)
					authors.append(author)
	almoner.writeZipFileByFolder(backupFolder)
	for author in authors:
		if len(author.warnings) > 0:
			print('BIG WARNING')
			print(author.name)
			for warning in author.warnings:
				print(warning)
			print('')
	return authors

def getEarningsText(authors):
	'Get the devtome earnings text.'
	cString = cStringIO.StringIO()
	for author in authors:
		coinAddress = author.parameterDictionary['Coin Address']
		name = author.parameterDictionary['Name']
		lastPayoutString = str(author.tomecount.earnings)
		if lastPayoutString != '0':
			cString.write('%s,%s,%s-Word Count(%s)\n' % (name, coinAddress, lastPayoutString, author.sourceAddress.replace('&do=edit', '')))
	return cString.getvalue()

def getImageCount(linkText):
	'Get the image count of the page linked to in the line.'
	if linkText == '':
		return 0
	imageCount = 0
	lines = linkText.lower().split('{{')
	for line in lines:
		endBracketIndex = line.find('}}')
		if endBracketIndex != -1:
			line = line[: endBracketIndex].strip()
#			if ('|') in line:
#				line = line[: line.find('|')].strip()
		if line.endswith('.gif') or line.endswith('.jpg') or line.endswith('.png'):
			imageCount += 1
	return imageCount

def getIsLastEditByAuthor(linkString, name):
	'Determine if the last edit was by the author.'
	if name == 'Knotwork' or name == 'Kumala' or name == 'Icoin' or name == 'Xenophaux' or name == 'Unthinkingbit':
		return True
	revisionsText = almoner.getInternetText('http://devtome.com/doku.php?id=%s&do=revisions' % linkString)
	time.sleep(1)
	lastModIndex = revisionsText.find('<li id="lastmod">')
	if lastModIndex == -1:
		print('Warning, lastmod not found on revisions page.')
		return False
	revisionsText = revisionsText[lastModIndex :]
	breakIndex = revisionsText.find('<br')
	if breakIndex == -1:
		print('Warning, break not found on revisions page.')
		return False
	revisionsText = revisionsText[: breakIndex]
	byString = ' by '
	byIndex = revisionsText.find(byString)
	if byIndex == -1:
		print('Warning, byString not found on revisions page.')
		print(linkString)
		return False
	editor = revisionsText[byIndex + len(byString) :].strip()
	if editor == 'raptorak' or editor == 'twobits' or editor == 'unthinkingbit' or editor == 'weisoq' or editor == 'xenophaux':
		return True
	if editor != name.lower():
		print('Warning, editor is not the same as the name.')
		print(editor)
		print(linkString)
		return False
	return True

def getLinkName(line):
	'Get the name of the article in the line.'
	linkStartIndex = line.find('[[')
	if linkStartIndex == -1:
		if '[' in line and 'devtome.' in line:
			print('Warning, external link format instead of internal link format.')
			print(line)
		return ''
	linkStartIndex += len('[[')
	linkEndIndex = line.find(']]', linkStartIndex)
	if linkEndIndex == -1:
		return ''
	linkString = line[linkStartIndex : linkEndIndex]
	linkDividerIndex = linkString.find('|')
	if linkDividerIndex != -1:
		linkString = linkString[: linkDividerIndex]
	if len(linkString) == 0:
		return ''
	linkString = linkString.strip()
	if linkString[0] == ':':
		linkString = linkString[1 :]
	linkString = linkString.replace('&amp;', ' ').replace('&quot;', ' ').replace('  ', ' ').replace('  ', ' ')
	return linkString.strip().replace(' ', '_')

def getLinkText(lowerLinkName, name):
	'Get the text of the page linked to in the line.'
	if lowerLinkName == '':
		return ''
	time.sleep(1)
	if getIsLastEditByAuthor(lowerLinkName, name):
		return getSourceText('http://devtome.com/doku.php?id=%s&do=edit' % lowerLinkName)
	return ''

def getRevenueNeutralEarnings(authors, totalTomecount):
	'Get the revenue neutral earnings.'
	earningsMultiplier = 2.0
	extraMultiplier = earningsMultiplier
	revenueNeutralEarnings = totalTomecount.payout
	while extraMultiplier > 0.00001:
		extraMultiplier *= 0.5
		revenueNeutralEarnings = getTotalEarnings(authors, earningsMultiplier, totalTomecount)
		if revenueNeutralEarnings == totalTomecount.payout:
			return revenueNeutralEarnings
		if revenueNeutralEarnings > totalTomecount.payout:
			earningsMultiplier -= extraMultiplier
		else:
			earningsMultiplier += extraMultiplier
	return revenueNeutralEarnings

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

def getTotalEarnings(authors, earningsMultiplier, totalTomecount):
	'Get the total earnings.'
	totalEarnings = 0
	for author in authors:
		if author.tomecount.payout > 0:
			author.tomecount.boundedEarningsMultiplier = max(min(earningsMultiplier * author.tomecount.normalizedRootWorth, 1.25), 0.75)
			author.tomecount.earnings = int(round(author.tomecount.boundedEarningsMultiplier * float(author.tomecount.payout)))
			totalEarnings += author.tomecount.earnings
	return totalEarnings

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
	'Get the tomecount total and calculate the earnings for the authors.'
	totalTomecount = Tomecount()
	numberOfActiveWriters = 0
	numberOfWriters = 0
	totalBoundedEarningsMultiplier = 0.0
	totalRootWorth = 0.0
	totalTomecount.proportion = 1.0
	for author in authors:
		totalTomecount.collatedWeightedWordCount += author.tomecount.collatedWeightedWordCount
		totalTomecount.collatedWordCount += author.tomecount.collatedWordCount
		totalTomecount.cumulativePayout += author.tomecount.cumulativePayout
		totalTomecount.imageCount += author.tomecount.imageCount
		totalTomecount.originalWordCount += author.tomecount.originalWordCount
		totalTomecount.pageViews += author.tomecount.pageViews
		totalTomecount.payout += author.tomecount.payout
		totalTomecount.previousPayout += author.tomecount.previousPayout
		totalTomecount.weightedWordCount += author.tomecount.weightedWordCount
		totalTomecount.wordCount += author.tomecount.wordCount
		if author.tomecount.cumulativePayout > 0:
			numberOfWriters += 1
		totalRootWorth += author.tomecount.normalizedRootWorth
	if totalRootWorth == 0.0:
		totalRootWorth = 1.0
	rootWorthMultiplier = float(numberOfWriters) / totalRootWorth
	totalTomecount.normalizedRootWorth = 1.0
	for author in authors:
		if author.tomecount.cumulativePayout > 0:
			author.tomecount.normalizedRootWorth *= rootWorthMultiplier
	earningsMultiplier = 1.0
	totalTomecount.earnings = getRevenueNeutralEarnings(authors, totalTomecount)
	for author in authors:
		if author.tomecount.earnings > 0:
			totalBoundedEarningsMultiplier += author.tomecount.boundedEarningsMultiplier
			numberOfActiveWriters += 1
	totalTomecount.boundedEarningsMultiplier = totalBoundedEarningsMultiplier / float(numberOfActiveWriters)
	return totalTomecount

def getViewDictionary(viewFileName):
	'Get the page view dictionary.'
	viewDictionary = {}
	lines = almoner.getTextLines(almoner.getFileText(viewFileName))
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 1:
			viewDictionary[words[0]] = words[1]
	return viewDictionary

def getWordCount(linkText):
	'Get the word count of the page linked to in the line.'
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
	viewFileName = almoner.getParameter(arguments, 'devtome_analytics_%s.csv' % round, 'view')
	lines = almoner.getTextLines(almoner.getFileText(previousFileName))
	titleLine = lines[0]
	titles = titleLine.split(',')
	backupFolder = rootFileName + '_articles'
	viewDictionary = getViewDictionary(viewFileName)
	authors = getAuthors(backupFolder, lines, titles, viewDictionary)
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
	def __init__(self, backupFolder, titles, viewDictionary, words):
		'Initialize.'
		self.tomecount = Tomecount()
		self.parameterDictionary = {}
		self.warnings = []
		for wordIndex, word in enumerate(words):
			self.parameterDictionary[titles[wordIndex]] = word
		if 'Cumulative Payout' in self.parameterDictionary:
			self.tomecount.previousPayout = int(self.parameterDictionary['Cumulative Payout'])
		self.name = self.parameterDictionary['Name']
		self.sourceAddress = 'http://devtome.com/doku.php?id=wiki:user:%s&do=edit' % self.name
		tipAddress = ''
		print('Loading articles from %s' % self.name)
		sourceText = getSourceText(self.sourceAddress)
		almoner.writeFileText(os.path.join(backupFolder, 'wiki:user:' + self.name), sourceText)
		isCollated = False
		isOriginal = False
		isTip = False
		linkTexts = set([])
		for line in almoner.getTextLines(sourceText):
			lineStrippedLower = line.strip().lower()
			if '==' in lineStrippedLower:
				isCollated = False
				isOriginal = False
				isTip = False
			if isCollated:
				lowerLinkName = getLinkName(line).lower()
				linkText = getLinkText(lowerLinkName, self.name)
				if linkText not in linkTexts:
					linkTexts.add(linkText)
					self.tomecount.imageCount += getImageCount(linkText)
					wordCount = getWordCount(linkText)
					self.tomecount.collatedWordCount += wordCount
					if lowerLinkName in viewDictionary:
						self.tomecount.pageViews += int(viewDictionary[lowerLinkName])
					if wordCount > 0:
						print('Collated article: %s, Word Count: %s' % (lineStrippedLower, almoner.getCommaNumberString(wordCount)))
						almoner.writeFileText(os.path.join(backupFolder, lowerLinkName), linkText)
			if isOriginal:
				lowerLinkName = getLinkName(line).lower()
				linkText = getLinkText(lowerLinkName, self.name)
				if linkText not in linkTexts:
					linkTexts.add(linkText)
					self.tomecount.imageCount += getImageCount(linkText)
					wordCount = getWordCount(linkText)
					self.tomecount.originalWordCount += wordCount
					if lowerLinkName in viewDictionary:
						self.tomecount.pageViews += int(viewDictionary[lowerLinkName])
					if wordCount > 0:
						print('Original article: %s, Word Count: %s' % (lineStrippedLower, almoner.getCommaNumberString(wordCount)))
						almoner.writeFileText(os.path.join(backupFolder, lowerLinkName), linkText)
			if isTip:
				tipAddress = line.strip()
				if ':' in tipAddress:
					tipAddress = tipAddress[tipAddress.find(':') + 1 :].strip()
			if '==' in lineStrippedLower:
				if 'collated' in lineStrippedLower:
					isCollated = True
				elif 'original' in lineStrippedLower:
					isOriginal = True
				elif 'tip' in lineStrippedLower:
					isTip = True
		self.tomecount.collatedWeightedWordCount = self.tomecount.collatedWordCount * 3 / 10
		self.tomecount.wordCount = self.tomecount.collatedWordCount + self.tomecount.originalWordCount
		self.tomecount.weightedWordCount = self.tomecount.collatedWeightedWordCount + self.tomecount.originalWordCount
		self.tomecount.weightedWordCount += 10 * self.tomecount.imageCount
		if self.tomecount.weightedWordCount >= 1000:
			self.tomecount.cumulativePayout = int(round(float(self.tomecount.weightedWordCount) * 0.001))
		print('Weighted Word Count: %s' % almoner.getCommaNumberString(self.tomecount.weightedWordCount))
		self.tomecount.payout = max(self.tomecount.cumulativePayout - self.tomecount.previousPayout, 0)
		maximumPayout = 80
		if tipAddress != self.parameterDictionary['Coin Address'] and self.name != 'Mosinnagant':
			self.printWarning('Warning, the coin address is not the same as the tip address, so nothing will be paid.')
			maximumPayout = 0
		if self.tomecount.payout > maximumPayout:
			self.tomecount.payout = maximumPayout
			self.tomecount.cumulativePayout = self.tomecount.previousPayout + maximumPayout
		if self.tomecount.cumulativePayout > 0:
			worthRatio = float(self.tomecount.pageViews) / float(self.tomecount.weightedWordCount)
			self.tomecount.normalizedRootWorth = math.sqrt(math.sqrt(worthRatio))

	def __repr__(self):
		'Get the string representation of this class.'
		return str(self.parameterDictionary)

	def addLine(self, cString):
		'Add the author to the tomecount csv cString.'
		words = [self.parameterDictionary['Name'], self.parameterDictionary['Coin Address']]
		if self.tomecount.weightedWordCount == 0 and self.tomecount.previousPayout == 0:
			cString.write('%s\n' % ','.join(words))
			return 
		cString.write(self.tomecount.getJoinedWords(words))

	def printWarning(self, warning):
		'Print warning and add it to the warnings.'
		self.warnings.append(warning)
		print(warning)


class Tomecount:
	'A class to handle the tome accounting.'
	def __init__(self):
		'Initialize.'
		self.boundedEarningsMultiplier = 0.0
		self.collatedWeightedWordCount = 0
		self.collatedWordCount = 0
		self.cumulativePayout = 0
		self.earnings = 0
		self.imageCount = 0
		self.normalizedRootWorth = 0.0
		self.originalWordCount = 0
		self.pageViews = 0
		self.payout = 0
		self.previousPayout = 0
		self.proportion = 0.0
		self.weightedWordCount = 0
		self.wordCount = 0

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
		words.append(str(self.pageViews))
		words.append(str(self.normalizedRootWorth))
		words.append(str(self.boundedEarningsMultiplier))
		words.append(str(self.earnings))
		return '%s\n' % ','.join(words)

def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

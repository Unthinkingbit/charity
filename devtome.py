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
import zipfile


__license__ = 'MIT'


globalEditors = 'athanasios_motok ba_al bigdaub cyke64 deadsea33 eeharris finshaggy ftgcoin giftculturewriting ghostofdawn hunterbunter knotwork ibrennan infoporter maitotoxin master-p melodiem nsddev paul3 raptorak smeagol stealtheh thedischarger tom twobits unthinkingbit weisoq wekkel wiser xenophaux'.split()
globalNames = 'knotwork kumala icoin xenophaux unthinkingbit'.split()


def addJoinedTitles(cString, words):
	'Add joined titles to the cString.'
	words.append('Collated Word Count')
	words.append('Collated Weighted Word Count')
	words.append('Image Count')
	words.append('Original Word Count')
	words.append('Word Count')
	words.append('Weighted Word Count')
	words.append('Cumulative Payout')
	words.append('Previous Cumulative Payout')
	words.append('Payout')
	words.append('Unique Page Views')
	words.append('Popularity Times Rating')
	words.append('Advertising Portion')
	words.append('Advertising Revenue')
	words.append('Views per Thousand Words')
	words.append('Normalized Popularity')
	words.append('Rating Median')
	words.append('Normalized Rating Median')
	words.append('Categorized Articles')
	words.append('Articles')
	words.append('Categorization')
	words.append('Normalized Categorization')
	words.append('Normalized Worth')
	words.append('Earnings Multiplier')
	words.append('Earnings')
	cString.write('%s\n' % ','.join(words))

def getAdvertisingRevenueText(authors):
	'Get the devtome advertising revenue text.'
	cString = cStringIO.StringIO()
	for author in authors:
		coinAddress = author.parameterDictionary['Coin Address']
		advertisingRevenueString = str(author.tomecount.advertisingRevenue)
		if advertisingRevenueString != '0':
			cString.write('%s,%s\n' % (coinAddress, advertisingRevenueString))
	return cString.getvalue()

def getAuthors(backupFolder, lines, ratingDictionary, titles, viewDictionary):
	'Get the authors.'
	averageRating = 0.0
	authors = []
	authorSet = set([])
	ratingValues = ratingDictionary.values()
	almoner.makeDirectory(backupFolder)
	zipFileName = backupFolder + '.zip'
	backupFileSet = set([])
	if os.path.isfile(zipFileName):
		zipArchive = zipfile.ZipFile(zipFileName, 'r', compression=zipfile.ZIP_DEFLATED)
		backupFileSet = set(zipArchive.namelist())
		zipArchive.close()
	for ratingValue in ratingValues:
		averageRating += ratingValue
	if averageRating == 0.0:
		averageRating = 1.0
	else:
		averageRating /= float(len(ratingDictionary.values()))
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 0:
			if len(words[0]) > 0:
				author = Author(averageRating, backupFolder, backupFileSet, ratingDictionary, titles, viewDictionary, words)
				if author.name not in authorSet:
					authorSet.add(author.name)
					authors.append(author)
	if len(authors) > 50:
		almoner.writeZipFileByFolder(backupFolder)
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
		if line.endswith('.gif') or line.endswith('.jpg') or line.endswith('.png'):
			imageCount += 1
	return imageCount

def getIsLastEditByAuthor(author, linkString):
	'Determine if the last edit was by the author.'
	nameLower = author.name.lower()
	if nameLower in globalNames:
		return True
	revisionsText = almoner.getInternetText('http://devtome.com/doku.php?id=%s&do=revisions' % linkString)
	time.sleep(0.5)
	lastModIndex = revisionsText.find('<li id="lastmod">')
	if lastModIndex == -1:
		time.sleep(180)
		revisionsText = almoner.getInternetText('http://devtome.com/doku.php?id=%s&do=revisions' % linkString)
		lastModIndex = revisionsText.find('<li id="lastmod">')
	if lastModIndex == -1:
		author.printWarning('Warning, lastmod not found on revisions page.')
		return False
	revisionsText = revisionsText[lastModIndex :]
	breakIndex = revisionsText.find('<br')
	if breakIndex == -1:
		author.printWarning('Warning, break not found on revisions page.')
		return False
	revisionsText = revisionsText[: breakIndex]
	byString = ' by '
	byIndex = revisionsText.find(byString)
	if byIndex == -1:
		author.printWarning('Warning, byString not found on revisions page.')
		author.printWarning(linkString)
		return False
	editor = revisionsText[byIndex + len(byString) :].strip()
	if editor in globalEditors:
		return True
	if editor != nameLower:
		author.printWarning('Warning, editor (%s) is not the same as the creator (%s) in the article: %s.' % (editor, author.name, linkString))
		return False
	return True

def getLinkName(line, name):
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
	if linkString[0] != ':':
		return ''
	linkString = linkString[1 :]
	if linkString.startswith('wiki:user:'):
		return ''
	questionMarkIndex = linkString.find('?')
	if questionMarkIndex >= 0:
		linkString = linkString[: questionMarkIndex]
	linkString = linkString.replace('&amp;', ' ').replace('&quot;', ' ').replace('/', '_').replace('  ', ' ').replace('  ', ' ')
	if linkString.lower() == name.lower():
		return ''
	return linkString.strip().replace(' ', '_')

def getNewArticlesText(authors, round):
	'Get the new articles text in wiki format.'
	cString = cStringIO.StringIO()
	cString.write('New articles in round %s. \n' % round)
	for author in authors:
		for newArticle in author.newArticles:
			cString.write('*[[%s]] \n' % newArticle)
	return cString.getvalue()

def getRatingMedianIndex(line):
	'Get the rating median index.'
	words = line.split(',')
	for wordIndex, word in enumerate(words):
		if word.strip().lower() == 'median':
			return wordIndex
	return 2

def getRatingDictionary(ratingFileName):
	'Get the rating median vote dictionary.'
	lines = almoner.getTextLines(almoner.getFileText(ratingFileName))
	if len(lines) < 2:
		return {}
	ratingDictionary = {}
	ratingMedianIndex = getRatingMedianIndex(lines[0])
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > ratingMedianIndex:
			name = words[0].strip().lower()
			if len(name) > 0:
				ratingDictionary[name] = float(words[ratingMedianIndex].strip().lower())
	return ratingDictionary

def getRevenueNeutralEarnings(authors, totalTomecount):
	'Get the revenue neutral earnings.'
	earningsMultiplier = 4.0
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

def getSourceTextIfByAuthor(author, lowerLinkName):
	'Get the source text if the author wrote it.'
	if lowerLinkName == '':
		return ''
	time.sleep(0.5)
	if getIsLastEditByAuthor(author, lowerLinkName):
		return almoner.getSourceText('http://devtome.com/doku.php?id=%s&do=edit' % lowerLinkName)
	return ''

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

def getThreeSignificantFigures(number):
	'Get number rounded to three significant figures as a string.'
	absoluteNumber = abs(number)
	places = 1
	if absoluteNumber < 10.0:
		if absoluteNumber < 0.000000001:
			places = 12
		else:
			places = max(1, int(round(2 - math.floor(math.log10(absoluteNumber)))))
	threeSignificantFigures = round(number, places)
	threeSignificantFiguresString = str(threeSignificantFigures)
	if 'e' in threeSignificantFiguresString:
		return ('%.15f' % threeSignificantFigures).rstrip('0')
	return threeSignificantFiguresString

def getTotalEarnings(authors, earningsMultiplier, totalTomecount):
	'Get the total earnings.'
	totalEarnings = 0
	for author in authors:
		if author.tomecount.payout > 0:
			author.tomecount.earningsMultiplier = max(min(earningsMultiplier * author.tomecount.normalizedWorth, 1.4999), 0.5001)
			author.tomecount.earnings = int(round(author.tomecount.earningsMultiplier * float(author.tomecount.payout)))
			totalEarnings += author.tomecount.earnings
	return totalEarnings

def getTomecountText(authors, totalTomecount):
	'Get the tomecount csv text for the authors.'
	cString = cStringIO.StringIO()
	addJoinedTitles(cString, ['Name','Coin Address'])
	for author in authors:
		author.addLine(cString)
	addJoinedTitles(cString, ['','Totals'])
	cString.write(totalTomecount.getJoinedWords(['','']))
	cString.write(',Date\n')
	cString.write(',%s\n' % date.today().isoformat())
	return cString.getvalue()

def getTotalTomecount(advertisingRevenue, authors):
	'Get the tomecount total and calculate the earnings for the authors.'
	totalTomecount = Tomecount()
	numberOfActiveWriters = 0
	numberOfWriters = 0
	totalTomecount.advertisingPortion = 1.0
	normalizedCategorizations = []
	normalizedPopularities = []
	normalizedRatingMedians = []
	for author in authors:
		normalizedCategorizations.append(author.tomecount.normalizedCategorization)
		normalizedPopularities.append(author.tomecount.normalizedPopularity)
		normalizedRatingMedians.append(author.tomecount.normalizedRatingMedian)
	normalizeValues(normalizedCategorizations)
	normalizeValues(normalizedPopularities)
	normalizeValues(normalizedRatingMedians)
	for authorIndex, author in enumerate(authors):
		tomecount = author.tomecount
		tomecount.normalizedCategorization = normalizedCategorizations[authorIndex]
		tomecount.normalizedPopularity = normalizedPopularities[authorIndex]
		tomecount.normalizedRatingMedian = normalizedRatingMedians[authorIndex]
		tomecount.normalizedWorth = 0.1 * tomecount.normalizedCategorization + 0.3 * tomecount.normalizedPopularity
		tomecount.normalizedWorth += 0.6 * tomecount.normalizedRatingMedian
	for author in authors:
		totalTomecount.articleCount += author.tomecount.articleCount
		totalTomecount.categorizedArticleCount += author.tomecount.categorizedArticleCount
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
			totalTomecount.categorization += author.tomecount.categorization
			totalTomecount.popularityTimesRating += author.tomecount.popularityTimesRating
			totalTomecount.normalizedCategorization += author.tomecount.normalizedCategorization
			totalTomecount.normalizedPopularity += author.tomecount.normalizedPopularity
			totalTomecount.normalizedRatingMedian += author.tomecount.normalizedRatingMedian
			totalTomecount.normalizedWorth += author.tomecount.normalizedWorth
			totalTomecount.ratingMedian += author.tomecount.ratingMedian
			totalTomecount.viewsPerThousandWords += author.tomecount.viewsPerThousandWords
	if numberOfWriters > 0:
		totalTomecount.categorization /= float(numberOfWriters)
		totalTomecount.normalizedCategorization /= float(numberOfWriters)
		totalTomecount.normalizedPopularity /= float(numberOfWriters)
		totalTomecount.normalizedRatingMedian /= float(numberOfWriters)
		totalTomecount.normalizedWorth /= float(numberOfWriters)
		totalTomecount.ratingMedian /= float(numberOfWriters)
		totalTomecount.viewsPerThousandWords /= float(numberOfWriters)
	totalTomecount.earnings = getRevenueNeutralEarnings(authors, totalTomecount)
	for author in authors:
		if author.tomecount.earnings > 0:
			totalTomecount.earningsMultiplier += author.tomecount.earningsMultiplier
			numberOfActiveWriters += 1
		if author.tomecount.popularityTimesRating > 0:
			author.tomecount.advertisingPortion = float(author.tomecount.popularityTimesRating) / float(totalTomecount.popularityTimesRating)
			author.tomecount.advertisingRevenue = int(round(author.tomecount.advertisingPortion * float(advertisingRevenue)))
			totalTomecount.advertisingRevenue += author.tomecount.advertisingRevenue
	if numberOfActiveWriters > 0:
		totalTomecount.earningsMultiplier /= float(numberOfActiveWriters)
	return totalTomecount

def getViewDictionary(viewFileName):
	'Get the page view dictionary.'
	viewDictionary = {}
	lines = almoner.getTextLines(almoner.getFileText(viewFileName))
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 1:
			viewDictionary[words[0]] = int(words[1])
	return viewDictionary

def getWarningsText(authors):
	'Get the warnings text.'
	cString = cStringIO.StringIO()
	for author in authors:
		if len(author.warnings) > 0:
			cString.write('%s\n' % author.name)
			for warning in author.warnings:
				cString.write('%s\n' % warning)
			cString.write('\n')
	warningsText = cString.getvalue()
	if warningsText != '':
		print('\n')
		print('Monetary Warnings')
		print(warningsText)
		print('')
	return warningsText

def getWordCount(linkText):
	'Get the word count of the page linked to in the line.'
	linkText = linkText.replace(',', ' ').replace(';', ' ').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
	return len(linkText.split())

def normalizeValues(values):
	'Get the positives values normalized in average and standard deviation.'
	average = 0.0
	numberOfPositives = 0
	for value in values:
		if value > 0.0:
			average += value
			numberOfPositives += 1
	if numberOfPositives == 0:
		return
	average /= float(numberOfPositives)
	reciprocalAverage = 1.0 / average
	for valueIndex, value in enumerate(values):
		if value > 0.0:
			values[valueIndex] *= reciprocalAverage
	standardDeviation = 0.0
	for value in values:
		if value > 0.0:
			difference = value - 1.0
			standardDeviation += difference * difference
	if standardDeviation == 0.0:
		return
	standardDeviation = math.sqrt(standardDeviation / float(numberOfPositives))
	halfOverDeviation = 0.5 / standardDeviation
	for valueIndex, value in enumerate(values):
		if value > 0.0:
			values[valueIndex] **= halfOverDeviation

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	advertisingRevenue = int(almoner.getParameter(arguments, '0', 'revenue'))
	round = int(almoner.getParameter(arguments, '23', 'round'))
	advertisingFileName = almoner.getParameter(arguments, 'devtome', 'wiki')
	rootFileName = almoner.getParameter(arguments, 'devtome', 'wiki')
	currentFileName = almoner.getParameter(arguments, rootFileName + '_%s.csv' % round, 'current')
	previousFileName = almoner.getParameter(arguments, rootFileName + '_%s.csv' % (round - 1), 'previous')
	ratingFileName = almoner.getParameter(arguments, 'rating_%s.csv' % round, 'rating')
	viewFileName = almoner.getParameter(arguments, 'devtome_analytics_%s.csv' % round, 'view')
	lines = almoner.getTextLines(almoner.getFileText(previousFileName))
	titleLine = lines[0]
	titles = titleLine.split(',')
	backupFolder = rootFileName + '_articles'
	ratingDictionary = getRatingDictionary(ratingFileName)
	viewDictionary = getViewDictionary(viewFileName)
	authors = getAuthors(backupFolder, lines, ratingDictionary, titles, viewDictionary)
	totalTomecount = getTotalTomecount(advertisingRevenue, authors)
	tomecountText = getTomecountText(authors, totalTomecount)
	advertisingRevenueText = getAdvertisingRevenueText(authors)
	earningsText = getEarningsText(authors)
	newArticlesText = getNewArticlesText(authors, round)
	warningsText = getWarningsText(authors)
	outputSummaryTo = almoner.getParameter(arguments, 'devtome_summary.txt', 'summary')
	almoner.writeFileText(currentFileName, tomecountText)
	outputAdvertisingRevenueTo = almoner.getParameter(arguments, 'devtome_advertising_revenue.csv', 'advertising')
	outputEarningsTo = almoner.getParameter(arguments, 'devtome_earnings_%s.csv' % round, 'earnings')
	outputNewArticlesTo = almoner.getParameter(arguments, 'devtome_new_articles.txt', 'articles')
	outputWarningsTo = almoner.getParameter(arguments, 'devtome_warnings.txt', 'warnings')
	if advertisingRevenue > 0:
		if almoner.sendOutputTo(outputAdvertisingRevenueTo, advertisingRevenueText):
			print('The devtome advertising revenue file has been written to:\n%s\n' % outputAdvertisingRevenueTo)
	if almoner.sendOutputTo(outputEarningsTo, earningsText):
		print('The devtome earnings file has been written to:\n%s\n' % outputEarningsTo)
	if almoner.sendOutputTo(outputNewArticlesTo, newArticlesText):
		print('The devtome new articles file has been written to:\n%s\n' % outputNewArticlesTo)
	if almoner.sendOutputTo(outputSummaryTo, getSummaryText(earningsText, round, totalTomecount)):
		print('The summary file has been written to:\n%s\n' % outputSummaryTo)
	if almoner.sendOutputTo(outputWarningsTo, warningsText):
		print('The devtome warnings file has been written to:\n%s\n' % outputWarningsTo)


class Author:
	'A class to handle an author.'
	def __init__(self, averageRating, backupFolder, backupFileSet, ratingDictionary, titles, viewDictionary, words):
		'Initialize.'
		self.backupFolder = backupFolder
		self.backupFileSet = backupFileSet
		identicalCollatedCount = 0
		identicalOriginalCount = 0
		self.newArticles = []
		self.tomecount = Tomecount()
		self.parameterDictionary = {}
		self.sentenceSet = set([])
		self.warnings = []
		for wordIndex, word in enumerate(words):
			self.parameterDictionary[titles[wordIndex]] = word
		if 'Cumulative Payout' in self.parameterDictionary:
			self.tomecount.previousPayout = int(self.parameterDictionary['Cumulative Payout'])
		self.name = self.parameterDictionary['Name']
		self.sourceAddress = 'http://devtome.com/doku.php?id=wiki:user:%s&do=edit' % self.name
		tipAddress = ''
		print('Loading articles from %s' % self.name)
		sourceText = almoner.getSourceText(self.sourceAddress)
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
				lowerLinkName = getLinkName(line, self.name).lower()
				linkText = getSourceTextIfByAuthor(self, lowerLinkName)
				if lowerLinkName != '' and linkText == '':
					self.printWarning('Warning, could not invoice article link: %s' % lowerLinkName)
				if linkText not in linkTexts:
					linkTexts.add(linkText)
					self.tomecount.imageCount += getImageCount(linkText)
					wordCount = getWordCount(linkText)
					if lowerLinkName in viewDictionary:
						self.tomecount.pageViews += viewDictionary[lowerLinkName]
					if wordCount > 0:
						print('Collated article: %s, Word Count: %s' % (lineStrippedLower, almoner.getCommaNumberString(wordCount)))
						self.saveArticle(lowerLinkName, linkText)
						identicalCollatedCount += self.getIdenticalWordCount(linkText)
						self.tomecount.collatedWordCount += wordCount
			if isOriginal:
				lowerLinkName = getLinkName(line, self.name).lower()
				linkText = getSourceTextIfByAuthor(self, lowerLinkName)
				if lowerLinkName != '' and linkText == '':
					self.printWarning('Warning, could not invoice article link: %s' % lowerLinkName)
				if linkText not in linkTexts:
					linkTexts.add(linkText)
					self.tomecount.imageCount += getImageCount(linkText)
					wordCount = getWordCount(linkText)
					if lowerLinkName in viewDictionary:
						self.tomecount.pageViews += viewDictionary[lowerLinkName]
					if wordCount > 0:
						print('Original article: %s, Word Count: %s' % (lineStrippedLower, almoner.getCommaNumberString(wordCount)))
						self.saveArticle(lowerLinkName, linkText)
						identicalOriginalCount += self.getIdenticalWordCount(linkText)
						self.tomecount.originalWordCount += wordCount
			if isTip:
				tipLine = line.strip().replace("'", '')
				colonIndex = tipLine.find(':')
				if colonIndex >= 0:
					addressName = tipLine[: colonIndex].strip().lower()
					if 'dvc' in addressName or 'devcoin' in addressName or 'coin address' in addressName:
						tipAddress = tipLine[colonIndex + 1 :].strip()
			if '==' in lineStrippedLower:
				if 'collated' in lineStrippedLower:
					isCollated = True
				elif 'original' in lineStrippedLower:
					isOriginal = True
				elif 'tip' in lineStrippedLower:
					isTip = True
		if identicalCollatedCount > 0:
			self.tomecount.collatedWeightedWordCount -= identicalCollatedCount
			print('Identical Collated Word Count: %s' % almoner.getCommaNumberString(identicalCollatedCount))
		if identicalOriginalCount > 0:
			self.tomecount.originalWordCount -= identicalOriginalCount
			print('Identical Original Word Count: %s' % almoner.getCommaNumberString(identicalOriginalCount))
		self.tomecount.collatedWeightedWordCount = self.tomecount.collatedWordCount * 3 / 10
		self.tomecount.wordCount = self.tomecount.collatedWordCount + self.tomecount.originalWordCount
		self.tomecount.weightedWordCount = self.tomecount.collatedWeightedWordCount + self.tomecount.originalWordCount
		self.tomecount.weightedWordCount += 10 * self.tomecount.imageCount
		if self.tomecount.weightedWordCount >= 1000:
			self.tomecount.cumulativePayout = int(round(float(self.tomecount.weightedWordCount) * 0.001))
		print('Weighted Word Count: %s' % almoner.getCommaNumberString(self.tomecount.weightedWordCount))
		self.tomecount.payout = max(self.tomecount.cumulativePayout - self.tomecount.previousPayout, 0)
		maximumPayout = 50
		if tipAddress != self.parameterDictionary['Coin Address'] and self.name != 'Mosinnagant':
			self.printWarning('Warning, the coin address is not the same as the tip address, so nothing will be paid.')
			maximumPayout = 0
		if self.tomecount.payout > maximumPayout:
			self.tomecount.payout = maximumPayout
			self.tomecount.cumulativePayout = self.tomecount.previousPayout + maximumPayout
		if self.tomecount.cumulativePayout > 0:
			self.tomecount.categorization = float(self.tomecount.categorizedArticleCount) / float(self.tomecount.articleCount)
			self.tomecount.ratingMedian = averageRating
			lowerName = self.name.lower()
			if lowerName in ratingDictionary:
				self.tomecount.ratingMedian = ratingDictionary[lowerName]
			weightedPageViews = self.tomecount.pageViews
			if self.tomecount.previousPayout == 0:
				weightedPageViews += weightedPageViews
			self.tomecount.viewsPerThousandWords = 1000.0 * float(weightedPageViews) / float(self.tomecount.weightedWordCount)
			self.tomecount.normalizedCategorization = self.tomecount.categorization
			self.tomecount.normalizedPopularity = self.tomecount.viewsPerThousandWords
			self.tomecount.normalizedRatingMedian = self.tomecount.ratingMedian
			self.tomecount.popularityTimesRating = int(round(self.tomecount.pageViews * float(self.tomecount.ratingMedian) / 99.0))

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

	def getIdenticalWordCount(self, linkText):
		'Get the number of identical words.'
		identicalCount = 0
		sentences = linkText.lower().replace('\r', ' ').replace('\n', ' ').replace(',', ' ').replace('  ', ' ').split('. ')
		for sentence in sentences:
			if ':' not in sentence:
				if sentence in self.sentenceSet:
					identicalCount += len(sentence.split())
				else:
					self.sentenceSet.add(sentence)
		return identicalCount

	def printWarning(self, warning):
		'Print warning and add it to the warnings.'
		self.warnings.append(warning)
		print(warning)

	def saveArticle(self, lowerLinkName, linkText):
		'Save article and if new add to new articles list.'
		if lowerLinkName not in self.backupFileSet:
			self.newArticles.append(lowerLinkName)
		almoner.writeFileText(os.path.join(self.backupFolder, lowerLinkName), linkText)
		self.tomecount.articleCount += 1
		if '[[category:' in linkText.lower():
			self.tomecount.categorizedArticleCount += 1


class Tomecount:
	'A class to handle the tome accounting.'
	def __init__(self):
		'Initialize.'
		self.advertisingPortion = 0.0
		self.advertisingRevenue = 0
		self.articleCount = 0
		self.categorization = 0.0
		self.categorizedArticleCount = 0
		self.collatedWeightedWordCount = 0
		self.collatedWordCount = 0
		self.cumulativePayout = 0
		self.earnings = 0
		self.earningsMultiplier = 0.0
		self.imageCount = 0
		self.normalizedCategorization = 0.0
		self.normalizedPopularity = 0.0
		self.normalizedRatingMedian = 0.0
		self.normalizedWorth = 0.0
		self.originalWordCount = 0
		self.pageViews = 0
		self.payout = 0
		self.popularityTimesRating = 0
		self.previousPayout = 0
		self.ratingMedian = 0.0
		self.viewsPerThousandWords = 0.0
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
		words.append(str(self.previousPayout))
		words.append(str(self.payout))
		words.append(str(self.pageViews))
		words.append(getThreeSignificantFigures(self.popularityTimesRating))
		words.append(getThreeSignificantFigures(self.advertisingPortion))
		words.append(getThreeSignificantFigures(self.advertisingRevenue))
		words.append(getThreeSignificantFigures(self.viewsPerThousandWords))
		words.append(getThreeSignificantFigures(self.normalizedPopularity))
		words.append(getThreeSignificantFigures(self.ratingMedian))
		words.append(getThreeSignificantFigures(self.normalizedRatingMedian))
		words.append(str(self.categorizedArticleCount))
		words.append(str(self.articleCount))
		words.append(getThreeSignificantFigures(self.categorization))
		words.append(getThreeSignificantFigures(self.normalizedCategorization))
		words.append(getThreeSignificantFigures(self.normalizedWorth))
		words.append(getThreeSignificantFigures(self.earningsMultiplier))
		words.append(str(self.earnings))
		return '%s\n' % ','.join(words)

def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

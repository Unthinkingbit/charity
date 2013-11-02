"""
http://www.megamillions.com/numbers/
https://bitcointalk.org/index.php?topic=34586.msg2028001;topicseen#msg2028001
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
import os
import shutil
import sys
import zipfile


__license__ = 'MIT'

	
def addToAuthorDictionary(authorDictionary, name, text):
	'Add author name to invoiced articles.'
	isArticle = False
	for line in almoner.getTextLines(text):
		lineStrippedLower = line.strip().lower()
		if '==' in lineStrippedLower:
			isArticle = False
			if 'collated' in lineStrippedLower or 'original' in lineStrippedLower:
				isArticle = True
		if isArticle:
			title = devtome.getLinkName(lineStrippedLower, name)
			if title != '':
				authorDictionary[title] = name
	
def getArticles():
	'Get the articles.'
	articles = []
	authorDictionary = {}
	fileNameRoot = 'devtome_articles'
	archiveFileName = fileNameRoot + '.zip'
	zipArchive = zipfile.ZipFile(archiveFileName, 'r')
	zipArchive.extractall(fileNameRoot)
	zipArchive.close()
	names = os.listdir(fileNameRoot)
	for name in names:
		filePath = os.path.join(fileNameRoot, name)
		text = almoner.getFileText(filePath)
		if name.startswith('wiki:user:'):
			addToAuthorDictionary(authorDictionary, name[len('wiki:user:') :], text)
		else:
			longWords = getLongWords(text)
			if len(longWords) > 40:
				articles.append(Article(longWords, name))
	for article in articles:
		if article.name in authorDictionary:
			article.author = authorDictionary[article.name]
	shutil.rmtree(fileNameRoot)
	return articles

def getGreatestSimilarity(article):
	'Get the greatest similarity for a compare function.'
	return article.greatestSimilarity

def getLongWords(text):
	'Get the long words of the text.'
	longWords = []
	text = text.replace(',', ' ').replace(';', ' ').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').lower()
	words = text.split()
	for word in words:
		if word.endswith('.'):
			word = word[: -1]
		if len(word) > 4 and word.isalpha():
			longWords.append(word)
	return longWords

def getSimilarityText(articles):
	'Get the text of the most similar other article for each article.'
	cString = cStringIO.StringIO()
	cString.write('Name,Other,Similarity (%)\n')
	totalFrequencyDictionary = {}
	for article in articles:
		for frequencyKey in article.frequencyDictionary.keys():
			count = article.frequencyDictionary[frequencyKey]
			if frequencyKey in totalFrequencyDictionary:
				totalFrequencyDictionary[frequencyKey] += count
			else:
				totalFrequencyDictionary[frequencyKey] = count
	normalizeFrequencyDictionary(totalFrequencyDictionary)
	for article in articles:
		article.setDistinct(totalFrequencyDictionary)
	for articleIndex, article in enumerate(articles):
		article.setSimilar(articles[: articleIndex] + articles[articleIndex + 1 :])
	articles.sort(key=getGreatestSimilarity)
	articles.reverse()
	for article in articles:
		article.addLine(cString)
	return cString.getvalue()

def getSockpuppetText(articles):
	'Get the text of the most similar other article from different authors.'
	cString = cStringIO.StringIO()
	cString.write('Author,Other Author,Name,Other,Similarity (%)\n')
	for article in articles:
		article.addSockpuppetLine(cString)
	return cString.getvalue()

def normalizeFrequencyDictionary(frequencyDictionary):
	'Divide each frequency by the total count.'
	totalCount = 0
	for count in frequencyDictionary.values():
		totalCount += count
	totalCountInverse = 1.0 / float(totalCount)
	for frequencyKey in frequencyDictionary.keys():
		frequencyDictionary[frequencyKey] = totalCountInverse * float(frequencyDictionary[frequencyKey])

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments or len(arguments) == 0:
		print(__doc__)
		return
	outputSimilarityTo = almoner.getParameter(arguments, 'similarity.csv', 'output')
	outputSockpuppetTo = almoner.getParameter(arguments, 'similarity_sockpuppet.csv', 'output')
	articles = getArticles()
	similarityText = getSimilarityText(articles)
	sockpuppetText = getSockpuppetText(articles)
	if almoner.sendOutputTo(outputSimilarityTo, similarityText):
		print('The similarity file has been written to:\n%s\n' % outputSimilarityTo)
	if almoner.sendOutputTo(outputSockpuppetTo, sockpuppetText):
		print('The sockpuppet file has been written to:\n%s\n' % outputSockpuppetTo)


class Article:
	'A class to handle an article.'
	def __init__(self, longWords, name):
		'Initialize.'
		self.author = ''
		self.name = name
		self.frequencyDictionary = {}
		for longWord in longWords:
			if longWord in self.frequencyDictionary:
				self.frequencyDictionary[longWord] += 1
			else:
				self.frequencyDictionary[longWord] = 1

	def __repr__(self):
		'Get the string representation of this class.'
		return '%s, %s' % (self.name, self.author)

	def addLine(self, cString):
		'Add the article to the similarity csv cString.'
		cString.write('%s,%s,%s\n' % (self.name, self.mostSimilar.name, round(100.0 * self.greatestSimilarity, 1)))

	def addSockpuppetLine(self, cString):
		'Add the article to the sockpuppet csv cString.'
		if self.author != self.mostSimilar.author:
			similarity = round(100.0 * self.greatestSimilarity, 1)
			cString.write('%s,%s,%s,%s,%s\n' % (self.author, self.mostSimilar.author, self.name, self.mostSimilar.name, similarity))

	def setDistinct(self, totalFrequencyDictionary):
		'Set distinct words.'
		normalizeFrequencyDictionary(self.frequencyDictionary)
		for frequencyKey in self.frequencyDictionary.keys():
			self.frequencyDictionary[frequencyKey] /= totalFrequencyDictionary[frequencyKey]
		frequencies = self.frequencyDictionary.values()
		frequencies.sort()
		minimumDistinctiveness = frequencies[len(frequencies) / 2]
		self.distinctSet = set([])
		for frequencyKey in self.frequencyDictionary.keys():
			if self.frequencyDictionary[frequencyKey] >= minimumDistinctiveness:
				self.distinctSet.add(frequencyKey)

	def setSimilar(self, articles):
		'Set distinct words.'
		self.greatestSimilarity = -1
		self.mostSimilar = None
		for article in articles:
			intersection = len(self.distinctSet.intersection(article.distinctSet))
			similarity = float(intersection) / float(max(len(self.distinctSet), len(article.distinctSet)))
			if similarity > self.greatestSimilarity:
				self.greatestSimilarity = similarity
				self.mostSimilar = article


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

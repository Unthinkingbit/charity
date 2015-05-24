"""
Wikicopy is a program to download the articles of a dokuwiki and save them in a zip file.


==Commands==
===Help===
The -h option, the -help option, will print the help, which is this document. The example follows:
python account.py -h

===Input===
Default is http://devtome.com

The -input option sets the input file name. The example follows:
python wikicopy.py -input http://devtome.com


==Install==
For wikicopy to run, you need Python 2.x, wikicopy will probably not run with python 3.x. To check if it is on your machine, in a terminal type:
python

If python 2.x is not on your machine, download the latest python 2.x, which is available from:
http://www.python.org/download/
"""

from datetime import timedelta
import almoner
import cStringIO
import datetime
import devtome
import os
import rater
import sys
import time


__license__ = 'MIT'


globalDateTimeFormat = '%y/%m/%d %H:%M'


def getIsWriterNewProductive(name, paidNameSet):
	'Determine if the writer is new and wrote at least a thousand words.'
	if name.lower() in paidNameSet:
		return False
	totalWordCount = 0
	articles = rater.getArticles(name)
	for article in articles:
		print(  article)
		totalWordCount += devtome.getWordCount(almoner.getSourceText('http://devtome.com/doku.php?id=%s&do=edit' % article))
		if totalWordCount >= 1000:
			return True
	return False

def getPaidNameSet(previousDevtomeName):
	'Get the names of the paid writers.'
	lines = almoner.getTextLines(almoner.getFileText(previousDevtomeName))
	paidNameSet = set([])
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 0:
			firstWord = words[0].strip().lower()
			if firstWord != '':
				paidNameSet.add(firstWord)
	return paidNameSet

def getRecentNames(fileName, nowDatetime, previousDevtomeName, wikiAddress):
	'Get the recent user names.'
	lastModifiedText = almoner.getFileText(fileName)
	lastModifiedDatetime = nowDatetime - timedelta(30)
	if lastModifiedText != '':
		lines = almoner.getTextLines(lastModifiedText)
		if len(lines) > 0:
			words = lines[0].split(',')
			if len(words) > 1:
				lastModifiedDatetime = datetime.datetime.strptime(words[1], globalDateTimeFormat)
	print('Last modified: %s' % lastModifiedDatetime)
	nowMinusLast = nowDatetime - lastModifiedDatetime
	paidNameSet = getPaidNameSet(previousDevtomeName)
	print('Now minus last: %s' % nowMinusLast)
	twentySixHours = 26 * 3600
	startChangesAddress = wikiAddress + '/doku.php?do=recent&id=start&show_changes=pages&'
	recentPageAddress = startChangesAddress + 'first[0]'
	lineDatetime = None
	dateTitle = 'class="date">'
	linkTitle = 'class="wikilink1" title="'
	nameTitle = 'name="'
	names = []
	while True:
		print('Parsing: %s' % recentPageAddress)
		lines = almoner.getTextLines(almoner.getInternetText(recentPageAddress))
		for lineIndex, line in enumerate(lines):
			if dateTitle in line:
				dateLine = lines[lineIndex + 1]
				dateString = dateLine[: dateLine.find('<')]
				if dateString.startswith('20'):
					dateString = dateString[len('20') :]
				lineDatetime = datetime.datetime.strptime(dateString, globalDateTimeFormat)
			if linkTitle in line:
				line = line[line.find(linkTitle) + len(linkTitle) :]
				name = line[: line.find('"')]
				if name != 'start':
					lastMinusLine = lastModifiedDatetime - lineDatetime
					if getSeconds(lastMinusLine) > twentySixHours:
						names.sort()
						return names
					if name.startswith('wiki:user:'):
						name = name[len('wiki:user:') :]
						if getIsWriterNewProductive(name, paidNameSet):
							names.append(name)
			if line.startswith('<input') and 'value="less recent' in line and nameTitle in line:
				line = line[line.find(nameTitle) + len(nameTitle) :]
				name = line[: line.find('"')]
				recentPageAddress = startChangesAddress + name
		time.sleep(1)
	return None

def getSeconds(timedelta):
	'Get the total number of seconds.'
	return timedelta.days * 86400 + timedelta.seconds

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	round = int(almoner.getParameter(arguments, '34', 'round'))
	wikiAddress = almoner.getParameter(arguments, 'http://devtome.com', 'wiki')
	fileNameRoot = wikiAddress
	if 'http://' in fileNameRoot:
		fileNameRoot = fileNameRoot[len('http://') :]
	if fileNameRoot.startswith('www.'):
		fileNameRoot = fileNameRoot[len('www.') :]
	if '.' in fileNameRoot:
		fileNameRoot = fileNameRoot[: fileNameRoot.find('.')]
	previousDevtomeName = almoner.getParameter(arguments, 'devtome_%s.csv' % (round - 1), 'previous')
	fileName = almoner.getParameter(arguments, 'writers.txt', 'output')
	writeWriterFile(fileName, previousDevtomeName, wikiAddress)

def writeWriterFile(fileName, previousDevtomeName, wikiAddress):
	'Write writer file.'
	nowDatetime = datetime.datetime.today()
	cString = cStringIO.StringIO()
	cString.write('Date,%s' % nowDatetime.strftime(globalDateTimeFormat))
	names = getRecentNames(fileName, nowDatetime, previousDevtomeName, wikiAddress)
	print('Number of names: %s' % len(names))
	for name in names:
		cString.write('\nhttp://devtome.com/doku.php?id=wiki:user:%s' % name)
	almoner.writeFileText(fileName, cString.getvalue())


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

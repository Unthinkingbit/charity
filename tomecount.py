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

import almoner
import cStringIO
import math
import sys


__license__ = 'MIT'


def getAuthors(fileName):
	'Determine the suffix number, returning 0 if there is not one.'
	authors = []
	titles = []
	lines = almoner.getTextLines(almoner.getFileText(fileName))
	titleLine = lines[0]
	words = titleLine.split(',')
	for word in words:
		titles.append(word.lower())
	for line in lines[1 :]:
		authors.append(Author(line, titles))
	return authors

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
	return text[tagEndIndex + 1 : textAreaEndTagIndex]

def getTomecountText(authors):
	'Get the tomecount csv text for the authors.'
	cString = cStringIO.StringIO()
	for author in authors:
		author.addLine(cString)
	return cString.getvalue()

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	fileName = almoner.getParameter(arguments, 'tomecount.csv', 'input')
	authors = getAuthors(fileName)
	accountText = getTomecountText(authors)
	print(  authors)
	print(  accountText)
	return
	suffixNumber = getSuffixNumber(fileName)
	outputAccountTo = getSuffixedFileName(almoner.getParameter(arguments, 'account.csv', 'output'), str(suffixNumber))
	accountLines = getAccountLines(arguments, fileName)
	peerText = getPeerText(arguments)
	accountText = getPluribusunumText(accountLines, peerText)
	if almoner.sendOutputTo(outputAccountTo, accountText):
		print('The account file has been written to:\n%s\n' % outputAccountTo)
	outputReceiverTo = getSuffixedFileName(almoner.getParameter(arguments, 'receiver.csv', 'outputreceiver'), str(suffixNumber))
	receiverLines = getReceiverLines(accountLines, suffixNumber)
	receiverText = getPluribusunumText(receiverLines, peerText)
	if almoner.sendOutputTo(outputReceiverTo, receiverText):
		print('The receiver file has been written to:\n%s\n' % outputReceiverTo)
		shaOutputPrefix = almoner.getParameter(arguments, '', 'outputsha')
		if len(shaOutputPrefix) != 0:
			sha256FileName = getSuffixedFileName(outputReceiverTo, shaOutputPrefix)
			almoner.writeFileText(sha256FileName, hashlib.sha256(receiverText).hexdigest())
			print('The sha256 receiver file has been written to:\n%s\n' % sha256FileName)

def getWordCount(line):
	'Get the word count of the page linked to in the line.'
	linkStartIndex = line.find('[[')
	if linkStartIndex == -1:
		return 0
	linkStartIndex += len('[[')
	linkEndIndex = line.find(']]', linkStartIndex)
	if linkEndIndex == -1:
		return 0
	linkString = line[linkStartIndex : linkEndIndex]
	linkDividerIndex = linkString.find('|')
	if linkDividerIndex != -1:
		linkString = linkString[: linkDividerIndex]
	sourceText = getSourceText('http://devtome.org/wiki/index.php?title=%s&action=edit' % linkString)
	sourceText = sourceText.replace('.', ' ').replace(',', ' ').replace(';', ' ').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
	return len(sourceText.split())


class Author:
	'A class to handle an author.'
	def __init__(self, line, titles):
		'Initialize.'
		words = line.split(',')
		self.collatedWordCount = 0
		self.originalWordCount = 0
		self.parameterDictionary = {}
		for wordIndex, word in enumerate(words):
			self.parameterDictionary[titles[wordIndex]] = word
		print(  self.parameterDictionary)
		sourceText = getSourceText('http://devtome.org/wiki/index.php?title=User:%s&action=edit' % self.parameterDictionary['name'])
		isCollated = False
		isOriginal = False
		for line in almoner.getTextLines(sourceText):
			lineStripped = line.strip()
			lineStrippedLower = lineStripped.lower()
			if lineStripped.startswith('=='):
				isCollated = False
				isOriginal = False
			if '==' in lineStripped:
				if 'collated' in lineStrippedLower:
					isCollated = True
				elif 'original' in lineStrippedLower:
					isOriginal = True
			if isCollated:
				self.collatedWordCount += getWordCount(lineStripped)
			if isOriginal:
				self.originalWordCount += getWordCount(lineStripped)

	def __repr__(self):
		'Get the string representation of this class.'
		return str(self.parameterDictionary)

	def addLine(self, cString):
		'Add the author to the tomecount csv cString.'
		coinAddress = self.parameterDictionary['coin address']
		name = self.parameterDictionary['name']
		cString.write('%s,%s,%s\n' % (name, coinAddress, str(self.originalWordCount)))


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

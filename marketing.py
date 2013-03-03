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
import sys
import tomecount


__license__ = 'MIT'


def getMarketingEarningsText(publishers):
	'Get the marketing earnings text.'
	cString = cStringIO.StringIO()
	for publisher in publishers:
		if publisher.payoutFifth != 0:
			publisher.write(cString)
	return cString.getvalue()

def getPublishers(lines):
	'Get the publishers.'
	publishers = []
	for line in lines:
		publishers.append(Publisher(line))
	return publishers

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	fileName = almoner.getParameter(arguments, 'publishers.csv', 'input')
	lines = almoner.getTextLines(almoner.getFileText(fileName))
	publishers = getPublishers(lines)
	marketingEarningsText = getMarketingEarningsText(publishers)
	outputEarningsTo = almoner.getParameter(arguments, 'marketing_earnings_???.csv', 'outputearnings')
	if almoner.sendOutputTo(outputEarningsTo, marketingEarningsText):
		print('The marketing earnings bounty file has been written to:\n%s\n' % outputEarningsTo)


class Publisher:
	'A class to handle a publisher.'
	def __init__(self, line):
		'Initialize.'
		splitLine = line.split(',')
		self.coinAddress = splitLine[1]
		self.linkPayout = False
		self.name = splitLine[0]
		self.payoutFifth = 0
		self.postPayout = 0
		self.postWords = 0
		self.signaturePayout = False
		self.sourceAddress = 'http://devtome.com/doku.php?id=wiki:user:%s&do=edit' % self.name
		print('Loading pages from %s' % self.name)
		sourceText = tomecount.getSourceText(self.sourceAddress)
		isLink = False
		isPost = False
		isSignature = False
		for line in almoner.getTextLines(sourceText):
			lineStrippedLower = line.strip().lower()
			if '==' in lineStrippedLower:
				isLink = False
				isPost = False
				isSignature = False
				if 'link' in lineStrippedLower:
					isLink = True
				if 'post' in lineStrippedLower:
					isPost = True
				if 'signature' in lineStrippedLower:
					isSignature = True
			if isLink:
				self.addLinkPayout(lineStrippedLower)
			if isPost:
				self.addPostPayout(lineStrippedLower)
			if isSignature:
				self.addSignaturePayout(lineStrippedLower)
		if self.postWords > 500:
			self.payoutFifth += 1
			if self.postWords > 5000:
				self.payoutFifth += 1

	def addLinkPayout(self, lineStrippedLower):
		'Add link payout if there is a devtome link.'
		if lineStrippedLower.startswith('*'):
			lineStrippedLower = lineStrippedLower[1 :]
		if not lineStrippedLower.startswith('http'):
			return
		linkText = almoner.getInternetText(lineStrippedLower)
		if 'devtome.com' not in linkText:
			return
		if self.linkPayout:
			return
		self.payoutFifth += 1
		self.linkPayout = False
		if lineStrippedLower.startswith('http://'):
			lineStrippedLower = lineStrippedLower[len('http://') :]
		elif lineStrippedLower.startswith('https://'):
			lineStrippedLower = lineStrippedLower[len('https://') :]
		if lineStrippedLower.startswith('www.'):
			lineStrippedLower = lineStrippedLower[len('www.') :]
		if lineStrippedLower.startswith('vps.'):
			lineStrippedLower = lineStrippedLower[len('vps.') :]
		if lineStrippedLower.endswith('/'):
			lineStrippedLower = lineStrippedLower[: -1]
		if '/' in lineStrippedLower:
			return
		self.payoutFifth += 1

	def addPostPayout(self, lineStrippedLower):
		'Add post payout if there is a devtome link.'
		if lineStrippedLower.startswith('*'):
			lineStrippedLower = lineStrippedLower[1 :]
		if not lineStrippedLower.startswith('http'):
			return
		if self.postPayout > 4:
			return
		linkText = almoner.getInternetText(lineStrippedLower)
		if '#' in lineStrippedLower:
			lineStrippedLower = lineStrippedLower[: lineStrippedLower.find('#')]
		if ';' in lineStrippedLower:
			lineStrippedLower = lineStrippedLower[: lineStrippedLower.find(';')]
		messageString = '<a class="message_number" style="vertical-align: middle;" href="' + lineStrippedLower
		if messageString not in linkText:
			return
		postBeginIndex = linkText.find(messageString)
		postBeginIndex = linkText.find('<div class="post"', postBeginIndex)
		if postBeginIndex == -1:
			return
		postEndIndex = linkText.find('<td valign="bottom"', postBeginIndex + 1)
		linkText = linkText[postBeginIndex : postEndIndex]
		if 'devtome.com' not in linkText:
			return
		self.postWords += len(linkText)
		self.postPayout += 1

	def addSignaturePayout(self, lineStrippedLower):
		'Add signature payout if there is a devtome link.'
		if lineStrippedLower.startswith('*'):
			lineStrippedLower = lineStrippedLower[1 :]
		if not lineStrippedLower.startswith('http'):
			return
		linkText = almoner.getInternetText(lineStrippedLower)
		if 'devtome.com' not in linkText:
			return
		if self.signaturePayout:
			return
		self.payoutFifth += 1
		self.signaturePayout = True
		postString = '<td><b>Posts: </b></td>'
		postIndex = linkText.find(postString)
		if postIndex == -1:
			return
		postEndIndex = postIndex + len(postString)
		postNumberEndIndex = linkText.find('</td>', postEndIndex + 1)
		if postNumberEndIndex == -1:
			return
		postNumberString = linkText[postEndIndex : postNumberEndIndex].strip()
		if '>' in postNumberString:
			postNumberString = postNumberString[postNumberString.find('>') + 1 :]
		postNumber = int(postNumberString)
		if postNumber > 1000:
			self.payoutFifth += 1

	def write(self, cString):
		'Initialize.'
		cString.write('%s-%s,%s/5-Marketing(%s)\n' % (self.coinAddress, self.name, self.payoutFifth, self.sourceAddress))


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

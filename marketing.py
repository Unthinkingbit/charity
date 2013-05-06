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
import devtome
import sys


__license__ = 'MIT'


def getEarningsText(publishers):
	'Get the marketing earnings text.'
	cString = cStringIO.StringIO()
	for publisher in publishers:
		publisher.write(cString)
	return cString.getvalue()

def getExtraPayoutFifth(lineStrippedLower):
	"""
	The extra payout is calculated from the Alexa page rank of the site. This is used rather than the Alexa page views because the page view
	information is only available to javascript interpreters, a read() command from urllib will only get the page rank. The lower the page rank,
	the higher the page views, so the reciprocal of the page rank is used to get the approximate number of dollars per month in proportion to
	page views.

	Because two fifths have already been added in addLinkPayout, two fifths are subtracted from the payout fifth, to a minimum of one, to
	determine the extra payout fifths.
	"""
	'Get extra payout fifth according to alexa ranking.'
	alexaLink = 'http://www.alexa.com/siteinfo/%s' % lineStrippedLower
	alexaText = almoner.getInternetText(alexaLink)
	isRankedNumberIndex = alexaText.find('is ranked number')
	if isRankedNumberIndex < 0:
		return 1
	alexaText = alexaText[isRankedNumberIndex + len('is ranked number') + 1:]
	inIndex = alexaText.find('in')
	if inIndex < 0:
		return 1
	alexaText = alexaText[: inIndex].strip().replace(',', '')
	rank = int(alexaText)
	if rank < 0:
		return 1
	dollarsPerMonth = 60000000 / rank
	if lineStrippedLower == 'bitcoinaddict.com':
		dollarsPerMonth = dollarsPerMonth * 8 / 10
	return max(dollarsPerMonth / 40 - 2, 1) # roundedUp(240 / 5 * 2)

def getPublishers(lines, workerNameSet):
	publishers = []
	for line in lines[1 :]:
		splitLine = line.split(',')
		if len(splitLine) > 1:
			coinAddress = splitLine[1].strip()
			name = splitLine[0].strip()
			if name != '':
				publisher = Publisher(coinAddress, name)
				if publisher.name in workerNameSet:
					publishers.append(publisher)
				else:
					print('%s did not work this round.' % publisher.name)
	return publishers
	
def getSummaryText(earningsText, publishers, suffixNumber):
	'Get the summary text.'
	totalPayoutFifth = 0
	for publisher in publishers:
		totalPayoutFifth += publisher.payoutFifth
	cString = cStringIO.StringIO()
	cString.write('The round %s marketing earnings are pasted below and at:\n' % suffixNumber)
	cString.write('https://raw.github.com/Unthinkingbit/charity/master/marketing_earnings_%s.csv\n\n' % suffixNumber)
	cString.write('%s\n' % earningsText)
	totalPayoutFloat = float(totalPayoutFifth) * 0.2
	cString.write('Total payout is %s/5 = %s.\n\n' % (totalPayoutFifth, totalPayoutFloat))
	cString.write('The earnings are generated by marketing.py:\n')
	cString.write('https://raw.github.com/Unthinkingbit/charity/master/marketing.py\n\n')
	return cString.getvalue()

def getWorkerNameSet(round):
	'Get the worker names.'
	accountLines = account.getAccountLines([], str(round))
	workerNames = []
	for accountLine in accountLines:
		accountLineSplit = accountLine.split(',')
		if len(accountLineSplit) > 1:
			name = accountLineSplit[0]
			if name != '':
				workerNames.append(name)
	return set(workerNames)

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	round = int(almoner.getParameter(arguments, '23', 'round'))
	publishersFileName = almoner.getParameter(arguments, 'devtome_%s.csv' % round, 'publishers')
	lines = almoner.getTextLines(almoner.getFileText(publishersFileName))
	outputEarningsTo = almoner.getParameter(arguments, 'marketing_earnings_%s.csv' % round, 'earnings')
	outputSummaryTo = almoner.getParameter(arguments, 'marketing_summary.txt', 'summary')
	workerNameSet = getWorkerNameSet(round)
	publishers = getPublishers(lines, workerNameSet)
	earningsText = getEarningsText(publishers)
	if almoner.sendOutputTo(outputEarningsTo, earningsText):
		print('The marketing earnings bounty file has been written to:\n%s\n' % outputEarningsTo)
	if almoner.sendOutputTo(outputSummaryTo, getSummaryText(earningsText, publishers, round)):
		print('The summary file has been written to:\n%s\n' % outputSummaryTo)


class Publisher:
	'A class to handle a publisher.'
	def __init__(self, coinAddress, name):
		'Initialize.'
		self.coinAddress = coinAddress
		self.domainPayout = 0
		self.name = name
		self.payoutFifth = 0
		self.postPayout = 0
		self.postWords = 0
		self.signaturePayout = False
		self.sourceAddress = 'http://devtome.com/doku.php?id=wiki:user:%s&do=edit' % self.name
		self.subdomainPayout = 0
		print('\nLoading pages from %s' % self.name)
		sourceText = devtome.getSourceText(self.sourceAddress)
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
		if self.domainPayout == 0:
			if self.subdomainPayout == 1:
				self.payoutFifth += 1
				print('Subdomain payout: 1')
		if self.postWords > 100:
			if self.postWords > 1000:
				self.payoutFifth += 2
				print('Big post payout: 2')
			else:
				self.payoutFifth += 1
				print('Small post payout: 1')
		if self.payoutFifth > 0:
			print('Total payout fifths: %s' % self.payoutFifth)

	def addLinkPayout(self, lineStrippedLower):
		'Add link payout if there is a devtome link.'
		if lineStrippedLower.startswith('*'):
			lineStrippedLower = lineStrippedLower[1 :]
		if not lineStrippedLower.startswith('http'):
			return
		if self.domainPayout > 4:
			return
		originalLink = lineStrippedLower
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
			if self.subdomainPayout == 0:
				linkText = almoner.getInternetText(originalLink)
				if 'devtome.com' not in linkText:
					return
				self.subdomainPayout = 1
			return
		linkText = '<a href="http://www.devtome.com/doku.php?id=earn_devcoins_by_writing"><img width="728" height="90"></a>'
		if lineStrippedLower != 'bitcoinaddict.com':
			linkText = almoner.getInternetText(originalLink)
		if 'devtome.com' not in linkText:
			return
		self.domainPayout += 1
		self.payoutFifth += 2
		printString = 'Domain name payout: 2, Address: %s' % lineStrippedLower
		beginIndex = linkText.find('devtome.com')
		while beginIndex != -1:
			endIndex = linkText.find('</a>', beginIndex)
			if endIndex == -1:
				print(printString)
				return
			linkString = linkText[beginIndex : endIndex]
			if '<img' in linkString:
#			if '<img' in linkString and '728' in linkString and '90' in linkString:
				extraPayoutFifth = getExtraPayoutFifth(lineStrippedLower)
				self.payoutFifth += extraPayoutFifth
				print('Banner payout: %s, Address: %s' % (extraPayoutFifth + 2, lineStrippedLower))
				return
			beginIndex = linkText.find('devtome.com', endIndex)
		print(printString)

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
		self.postWords += len(linkText.split())
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
			self.payoutFifth += 2
			print('Big signature payout: 2')
		else:
			self.payoutFifth += 1
			print('Small signature payout: 1')

	def write(self, cString):
		'Write.'
		if self.payoutFifth == 0:
			return
		cString.write('%s,%s,%s/5-Marketing(%s)\n' % (self.name, self.coinAddress, self.payoutFifth, self.sourceAddress.replace('&do=edit', '')))


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

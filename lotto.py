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


def getCountDictionary(round):
	'Get the weighted word count dictionary.'
	countDictionary = {}
	devtomeFileName = 'devtome_%s.csv' % round
	lines = almoner.getTextLines(almoner.getFileText(devtomeFileName))
	for line in lines[1 :]:
		words = line.split(',')
		if len(words) > 7:
			name = words[0].strip()
			if name != '':
				countDictionary[name] = int(words[7].strip())
	return countDictionary

def getDifferenceDictionary(round):
	'Get the difference in word count between the current dictionary and the previous dictionary.'
	differenceDictionary = getCountDictionary(round)
	previousDictionary = getCountDictionary(round - 1)
	highestCount = -1
	highestKey = None
	for previousKey in previousDictionary.keys():
		if previousKey in differenceDictionary:
			differenceDictionary[previousKey] -= previousDictionary[previousKey]
	for differenceKey in differenceDictionary.keys():
		if differenceDictionary[differenceKey] > highestCount:
			highestCount = differenceDictionary[differenceKey]
			highestKey = differenceKey
	del(differenceDictionary[highestKey])
	return differenceDictionary

def getLottoText(differenceDictionary):
	'Get the list of proportions, and lotto numbers.'
	cString = cStringIO.StringIO()
	cString.write('Name,Cumulative Proportion,Ball 0, Ball 1, Ball 2, Ball 3, Ball 4, Ball Yellow\n')
	cumulativeWords = 0
	differenceKeys = differenceDictionary.keys()
	differenceKeys.sort()
	totalWords = 0
	for differenceKey in differenceKeys:
		totalWords += differenceDictionary[differenceKey]
	for differenceKey in differenceKeys:
		cumulativeWords += differenceDictionary[differenceKey]
		remainingProportion = float(cumulativeWords) / float(totalWords)
		cString.write('%s,%s' % (differenceKey, remainingProportion))
		for ball in xrange(5):
			integerProportion = int(remainingProportion * 56)
			ballNumber = integerProportion + 1
			cString.write(',%s' % ballNumber)
			remainingProportion = 56.0 * (remainingProportion - float(integerProportion) / 56.0)
		integerProportion = int(remainingProportion * 46)
		ballNumber = integerProportion + 1
		cString.write(',%s\n' % ballNumber)
	return cString.getvalue()

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments or len(arguments) == 0:
		print(__doc__)
		return
	round = int(almoner.getParameter(arguments, '23', 'round'))
	outputLottoTo = almoner.getParameter(arguments, 'lotto.csv', 'output')
	differenceDictionary = getDifferenceDictionary(round)
	lottoText = getLottoText(differenceDictionary)
	if almoner.sendOutputTo(outputLottoTo, lottoText):
		print('The lotto file has been written to:\n%s\n' % outputLottoTo)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

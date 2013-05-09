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


def getPreviousRecipentDictionary(accountRootName, round, start):
	'Get the dictionary of the previous recipients.'
	previousRecipentDictionary = {}
	for accountIndex in xrange(start, round):
		accountFileName = accountRootName + '_%s.csv' % accountIndex
		lines = almoner.getTextLines(almoner.getFileText(accountFileName))
		for line in lines[1 :]:
			splitLine = line.split(',')
			if len(splitLine) > 1:
				name = splitLine[0].strip()
				if name != '':
					previousRecipentDictionary[name] = ''
	return previousRecipentDictionary

def getNewbieText(previousRecipentDictionary, round, shouldAddName):
	'Get the list of newbie keys, and optionally also names.'
	cString = cStringIO.StringIO()
	recipientDictionary = account.getRecipientDictionary(round)
	for recipientKey in recipientDictionary.keys():
		if recipientKey not in previousRecipentDictionary:
			if shouldAddName:
				cString.write('%s,' % recipientKey)
			cString.write('%s\n' % recipientDictionary[recipientKey])
	return cString.getvalue()

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	accountRootName = almoner.getParameter(arguments, 'account', 'input')
	nameStartLower = almoner.getParameter(arguments, 'False', 'name').lower()
	shouldAddName = False
	if nameStartLower.startswith('1') or nameStartLower.startswith('t') or nameStartLower.startswith('y'):
		shouldAddName = True
	round = int(almoner.getParameter(arguments, '23', 'round'))
	start = int(almoner.getParameter(arguments, '22', 'start'))
	outputNewbieTo = almoner.getParameter(arguments, 'newbie_%s.csv' % round, 'output')
	previousRecipentDictionary = getPreviousRecipentDictionary(accountRootName, round, start)
	newbieText = getNewbieText(previousRecipentDictionary, round, shouldAddName)
	if almoner.sendOutputTo(outputNewbieTo, newbieText):
		print('The marketing earnings bounty file has been written to:\n%s\n' % outputNewbieTo)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

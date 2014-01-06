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


def getPaymentText(paymentDictionary, round):
	'Get payment csv file.'
	cString = cStringIO.StringIO()
	recipientDictionary = account.getRecipientDictionary(round)
	paymentKeys = paymentDictionary.keys()
	paymentKeys.sort()
	for paymentKey in paymentKeys:
		cString.write('%s,%s,%s\n' % (paymentKey.capitalize(), recipientDictionary[paymentKey], paymentDictionary[paymentKey]))
	return cString.getvalue()

def getPaymentDictionary(round):
	'Get the payment dictionary.'
	addressDictionary = account.getAddressDictionary(round)
	paymentDictionary = {}
	lines = almoner.getTextLines(almoner.getFileText('receiver_%s.csv' % round))
	isAddressSection = False
	addressLines = []
	for line in lines[: 4000]:
		firstWord = ''
		line = line.strip()
		words = line.split(',')
		if len(words) > 0:
			firstWord = words[0].strip()
		if firstWord == '_endcoins':
			isAddressSection = False
		if isAddressSection and len(line) > 0:
				addressLines.append(line)
		if firstWord == '_begincoins':
			isAddressSection = True
	addressLines += addressLines * (4000 / len(addressLines))
	for addressLine in addressLines[: 4000]:
		payment = 45000.0 / float(len(words))
		words = addressLine.split(',')
		for word in words:
			name = addressDictionary[word].lower()
			if name in paymentDictionary:
				paymentDictionary[name] += payment
			else:
				paymentDictionary[name] = payment
	return paymentDictionary

def getTotalPayment(paymentDictionary):
	'Get total payment.'
	totalPayment = 0.0
	for payment in paymentDictionary.values():
		totalPayment += payment
	return totalPayment

def multiplyPayments(multiplier, paymentDictionary):
	'Multiply each payment by the multiplier.'
	for name in paymentDictionary.keys():
		paymentDictionary[name] = round(multiplier * paymentDictionary[name])

def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	outputPaymentTo = almoner.getParameter(arguments, 'payment.csv', 'output')
	remove = almoner.getParameter(arguments, '', 'remove')
	round = int(almoner.getParameter(arguments, '23', 'round'))
	total = float(almoner.getParameter(arguments, '0.0', 'total'))
	paymentDictionary = getPaymentDictionary(round)
	if remove != '':
		del paymentDictionary[remove]
	if total != '':
		multiplyPayments(total / getTotalPayment(paymentDictionary), paymentDictionary)
	paymentText = getPaymentText(paymentDictionary, round)
	if almoner.sendOutputTo(outputPaymentTo, paymentText):
		print('The payment file has been written to:\n%s\n' % outputPaymentTo)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

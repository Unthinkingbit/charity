"""
Almoner is a program to determine how many bitcoins to donate to each recipient.

This is meant to be used by bitcoin pools or miners to automatically donate to a list of recipients.  With this program, people could simply decide how much to donate, they don't have to also look up bitcoin addresses for each recipient.


==Commands==
===Help===
The -h option or the -help option will print the help, which is this document.  The example follows:
python almoner.py -h

===Input===
The -input option sets the input file name.  The example follows:
python almoner.py -input bitcoinshare.html

An example of a donation information input file is at:
https://github.com/Unthinkingbit/charity/blob/master/bitcoinshare.html

===Output===
The -output option sets the output.  If the output ends with stderr, the output will be sent to stderr  If the output ends with stdout or is empty, the output will be sent to stdout.  If the output does not end with stderr or stdout, the output will be written to a file by that name.  The example follows:
python almoner.py -input bitcoinshare.html

An example of an almoner output file is at:
https://github.com/Unthinkingbit/charity/blob/master/almoner.csv


==Install==
For almoner to run, you need Python 2.x, almoner will probably not run with python 3.x.  To check if it is on your machine, in a terminal type:
python

If python 2.x is not on your machine, download the latest python 2.x, which is available from:
http://www.python.org/download/
"""

import almoner
import sys


__license__ = 'MIT'


def getOutput(arguments):
	'Get the output according to the arguments.'
	bitcoinFileName = almoner.getParameter(arguments, 'bitcoinshare.html', 'inputbitcoin')
	devcoinFileName = almoner.getParameter(arguments, '', 'inputdevcoin')
	bitcoinOutput = almoner.getAddressText(bitcoinFileName)
	devcoinOutput = almoner.getAddressText(devcoinFileName)
	output = bitcoinOutput + devcoinOutput
	print('Number of bitcoin lines: %s' % len(almoner.getTextLines(bitcoinOutput)))
	print('Number of devcoin lines: %s' % len(almoner.getTextLines(devcoinOutput)))
	print('Number of address lines: %s' % len(almoner.getTextLines(output)))
	return output

def writeOutput(arguments):
	'Write output.'
	if len(arguments) < 2 or '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	outputTo = almoner.getParameter(arguments, 'devcoinalmoner.csv', 'output')
	if almoner.sendOutputTo(outputTo, getOutput(arguments)):
		print('The devcoin almoner file has been written to:\n%s' % outputTo)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

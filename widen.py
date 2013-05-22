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

import almoner
import devtome
import os
import shutil
import sys


__license__ = 'MIT'


def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	folderName = almoner.getParameter(arguments, 'widen', 'folder')
	peerRootAddress = almoner.getParameter(arguments, 'http://galaxies.mygamesonline.org/receiver.csv', 'input')
	round = int(almoner.getParameter(arguments, '23', 'round'))
	writeFolder(folderName, peerRootAddress, round)

def writeFolder(folderName, peerRootAddress, round):
	'Write zip file.'
	print('Making directory:')
	print(folderName)
	print('')
	almoner.makeDirectory(folderName)
	peerAddress = almoner.getSuffixedFileName(peerRootAddress, str(round))
	print('Getting peer:')
	print(peerAddress)
	print('')
	peerText = almoner.getLocationText(peerAddress)
	peerTextUntilCoins = peerText[: peerText.find('_begincoins')]
	unthinkingbitString = 'https://raw.github.com/Unthinkingbit/charity/master/receiver.csv'
	fuzzyString = 'http://devcoinpool.btc-music.com/receiver/receiver.csv'
	peerTextUntilCoins = peerTextUntilCoins.replace(unthinkingbitString, fuzzyString)
	print('Peer text until coins:')
	print(peerTextUntilCoins)
	print('')
	print('Writing widened files:')
	for widenRound in xrange(round + 1):
		writeWidenedFile(folderName, peerRootAddress, peerTextUntilCoins, widenRound)
	print('')

def writeWidenedFile(folderName, peerRootAddress, peerTextUntilCoins, widenRound):
	'Write widened file.'
	title = almoner.getSuffixedFileName('receiver.csv', str(widenRound))
	widenPath = os.path.join(folderName, title)
	receiverAddress = almoner.getSuffixedFileName(peerRootAddress, str(widenRound))
	receiverText = almoner.getLocationText(receiverAddress)
	receiverTextFromCoins = receiverText[receiverText.find('_begincoins') :]
	widenText = peerTextUntilCoins + receiverTextFromCoins
	almoner.writeFileText(widenPath, widenText)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

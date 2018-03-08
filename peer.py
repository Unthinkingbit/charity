"""
Peer replaces the old peers in the reciever files with the current peers in peer.csv.

==Install==
For peer to run, you need Python 2.x, peer will probably not run with python 3.x.  To check if it is on your machine, in a terminal type:
python

If python 2.x is not on your machine, download the latest python 2.x, which is available from:
http://www.python.org/download/
"""

import almoner


__license__ = 'MIT'


def getReceiverFileName(index):
	'Get receiver file name.'
	return 'receiver_%s.csv' % index

def main():
	'Replace peers.'
	beginPeerString = '_beginpeers\n'
	endPeerString = '_endpeers\n'
	receiverIndex = 0
	receiverFileName = getReceiverFileName(receiverIndex)
	receiverText = almoner.getFileText(receiverFileName)
	peerLines = almoner.getTextLines(almoner.getFileText('peer.csv'))
	replacementString = beginPeerString + almoner.getTextByLines(peerLines) + endPeerString
	while receiverText != '':
		beginPeerIndex = receiverText.find(beginPeerString)
		endPeerEndIndex = receiverText.find(endPeerString) + len(endPeerString)
		betweenString = receiverText[beginPeerIndex : endPeerEndIndex]
		almoner.writeFileText('backup_receiver_%s.csv' % receiverIndex, receiverText)
		replacedText = receiverText.replace(betweenString, replacementString)
		almoner.writeFileText(receiverFileName, replacedText)
		print('Replaced peers in file: ' + receiverFileName)
		receiverIndex += 1
		receiverFileName = getReceiverFileName(receiverIndex)
		receiverText = almoner.getFileText(receiverFileName, False)

if __name__ == '__main__':
	main()

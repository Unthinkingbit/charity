"""
Receiver

Example:
python receiver.py 1

Example:
python receiver.py -directory ~/test -height 1 -input receiver.csv -share 50 -step 2000

"""

import cStringIO
import pluribusunum
import sys


__license__ = 'MIT'


def getCoinLists(text):
	'Get the coin lists.'
	coinLists = []
	isCoinSection = False
	for line in pluribusunum.getTextLines(text):
		firstLowerSpaceless = ''
		words = pluribusunum.getCommaDividedWords(line)
		if len(words) > 0:
			firstLowerSpaceless = words[0].lower().replace(' ', '')
		if firstLowerSpaceless == 'coin':
			coinLists.append(words[1].split(','))
		if firstLowerSpaceless == '_endcoins':
			isCoinSection = False
		if isCoinSection:
			coinLists.append(line.split(','))
		if firstLowerSpaceless == '_begincoins':
			isCoinSection = True
	return coinLists

def getOutput(directoryName, fileName, height, share, step):
	'Get the receiver output.'
	stepOutput = pluribusunum.getStepOutput(directoryName, fileName, step, height)
	coinLists = getCoinLists(stepOutput)
	remainder = height - step * (height / step)
	modulo = remainder % len(coinLists)
	coins = coinLists[modulo]
	sharePerCoin = share / float(len(coins))
	output = cStringIO.StringIO()
	for coin in coins:
		if len(output.getvalue()) > 0:
			output.write(',')
		if share == 0.0:
			output.write(str(coin))
		else:
			output.write('%s,%i' % (coin, sharePerCoin))
	return output.getvalue()

def writeOutput(arguments):
	'Write output.'
	directoryName = pluribusunum.getParameter(arguments, '', 'directory')
	fileName = pluribusunum.getParameter(arguments, 'receiver.csv', 'input')
	heightString = pluribusunum.getParameter(arguments, '0', 'height')
	if len(arguments) == 2:
		heightString = arguments[1]
	outputTo = pluribusunum.getParameter(arguments, 'stdout', 'output')
	shareString = pluribusunum.getParameter(arguments, '0', 'share')
	stepString = pluribusunum.getParameter(arguments, '2000', 'step')
	text = getOutput(directoryName, fileName, int(heightString), float(shareString), int(stepString))
	pluribusunum.sendOutputTo(outputTo, text)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

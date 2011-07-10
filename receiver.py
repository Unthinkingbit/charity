"""
Receiver

python receiver.py -input receiver.csv -step 2000 -subsidy 50 -value 500

"""

import cStringIO
import pluribusunum
import sys


__license__ = 'public domain'


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

def getOutput(fileName, step, subsidy, value):
	'Get the receiver output.'
	stepOutput = pluribusunum.getStepOutput(fileName, step, value)
	coinLists = getCoinLists(stepOutput)
	remainder = value - step * (value / step)
	modulo = remainder % len(coinLists)
	coins = coinLists[modulo]
	subsidyPerCoin = subsidy / float(len(coins))
	output = cStringIO.StringIO()
	for coin in coins:
		if len(output.getvalue()) > 0:
			output.write(',')
		output.write('%s,%s' % (coin, subsidyPerCoin))
	return output.getvalue()

def writeOutput(arguments):
	'Write output.'
	fileName = pluribusunum.getParameter(arguments, '', 'input')
	outputTo = pluribusunum.getParameter(arguments, 'stdout', 'output')
	stepString = pluribusunum.getParameter(arguments, '', 'step')
	subsidyString = pluribusunum.getParameter(arguments, '1.0', 'subsidy')
	valueString = pluribusunum.getParameter(arguments, '0', 'value')
	text = getOutput(fileName, int(stepString), float(subsidyString), int(valueString))
	pluribusunum.sendOutputTo(outputTo, text)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

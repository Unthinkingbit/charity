"""
Generator

python generator.py -input generator.csv -key 789 -step 2000 -value 5
"""

import pluribusunum
import sys


__license__ = 'public domain'


def getGeneratorKeys(text):
	'Get the generator keys.'
	generatorKeys = []
	for line in pluribusunum.getTextLines(text):
		firstLowerSpaceless = ''
		words = pluribusunum.getCommaDividedWords(line)
		if len(words) > 1:
			firstLowerSpaceless = words[0].lower().replace(' ', '')
			if firstLowerSpaceless == 'keys':
				generatorKeys += words[1].split(',')
	return generatorKeys

def getOutput(fileName, key, step, value):
	'Get the receiver output.'
	stepOutput = pluribusunum.getStepOutput(fileName, step, value)
	generatorKeys = getGeneratorKeys(stepOutput)
	for generatorKey in generatorKeys:
		if key == generatorKey:
			return 'true'
	return 'false'

def writeOutput(arguments):
	'Write output.'
	fileName = pluribusunum.getParameter(arguments, '', 'input')
	keyString = pluribusunum.getParameter(arguments, '', 'key')
	outputTo = pluribusunum.getParameter(arguments, 'stdout', 'output')
	stepString = pluribusunum.getParameter(arguments, '', 'step')
	valueString = pluribusunum.getParameter(arguments, '0', 'value')
	text = getOutput(fileName, keyString, int(stepString), int(valueString))
	pluribusunum.sendOutputTo(outputTo, text)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

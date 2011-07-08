"""
Generator

python generator.py -input generator.csv -key 789 -step 2000 -value 5
"""

import pluribusunum
import sys


__license__ = 'public domain'


def getGeneratorSignatures(text):
	'Get the generator keys or signatures.'
	generatorSignatures = []
	for line in pluribusunum.getTextLines(text):
		firstLowerSpaceless = ''
		words = pluribusunum.getCommaDividedWords(line)
		if len(words) > 1:
			firstLowerSpaceless = words[0].lower().replace(' ', '')
			if firstLowerSpaceless == 'keys' or firstLowerSpaceless == 'signatures':
				generatorSignatures += words[1].split(',')
	return generatorSignatures

def getOutput(fileName, signature, step, value):
	'Get the receiver output.'
	stepOutput = pluribusunum.getStepOutput(fileName, step, value)
	generatorSignatures = getGeneratorSignatures(stepOutput)
	for generatorSignature in generatorSignatures:
		if signature == generatorSignature:
			return 'true'
	return 'false'

def writeOutput(arguments):
	'Write output.'
	fileName = pluribusunum.getParameter(arguments, '', 'input')
	outputTo = pluribusunum.getParameter(arguments, 'stdout', 'output')
	signatureString = pluribusunum.getParameter(arguments, '', 'signature')
	stepString = pluribusunum.getParameter(arguments, '', 'step')
	valueString = pluribusunum.getParameter(arguments, '0', 'value')
	text = getOutput(fileName, signatureString, int(stepString), int(valueString))
	pluribusunum.sendOutputTo(outputTo, text)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

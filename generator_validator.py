"""
Generator

python generator_validator.py -input generator.csv -signature 789 -step 2000 -value 5

"""

import pluribusunum
import sys


__license__ = 'MIT'


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

def getOutput(directoryPath, fileName, signature, step, value):
	'Get the receiver output.'
	stepOutput = pluribusunum.getStepOutput(directoryPath, fileName, step, value)
	return str(signature in getGeneratorSignatures(stepOutput)).lower()

def writeOutput(arguments):
	'Write output.'
	directoryPath = pluribusunum.getParameter(arguments, '', 'directory')
	fileName = pluribusunum.getParameter(arguments, '', 'input')
	outputTo = pluribusunum.getParameter(arguments, 'stdout', 'output')
	signatureString = pluribusunum.getParameter(arguments, '', 'signature')
	stepString = pluribusunum.getParameter(arguments, '', 'step')
	valueString = pluribusunum.getParameter(arguments, '0', 'value')
	text = getOutput(directoryPath, fileName, signatureString, int(stepString), int(valueString))
	pluribusunum.sendOutputTo(outputTo, text)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

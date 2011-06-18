"""
E Pluribus Unum. "Out of many, One."
writeOutput
http://asciitable.com/ < 32 or > 126 return False
"""

import math
import sys
import urllib


globalMinimumIdenticalProportion = 0.6


def getColonDividedWords(text):
	'Get the words divided around the colon.'
	colonIndex = text.find(':')
	if colonIndex < 0:
		return [text]
	return [text[: colonIndex], text[colonIndex + 1 :]]

def getCommonOutput(fileName):
	'Get the common output according to the peers listed in a file.'
	fileText = getFileText(fileName)
	return getCommonOutputByText(fileText)

def getCommonOutputByText(fileText):
	'Get the common output according to the peers listed in a text.'
	peerNames = getPeerNames(fileText)
	pages = getTexts(peerNames)
	minimumIdentical = int(math.ceil(globalMinimumIdenticalProportion * float(len(pages))))
	pageDictionary = {}
	for page in pages:
		if page in pageDictionary:
			pageDictionary[page] += 1
		else:
			pageDictionary[page] = 1
	for page in pageDictionary:
		if pageDictionary[page] >= minimumIdentical:
			return page
	return ''

def getFileText(fileName, printWarning=True, readMode='r'):
	'Get the entire text of a file.'
	try:
		file = open(fileName, readMode)
		fileText = file.read()
		file.close()
		return fileText
	except IOError:
		if printWarning:
			print('The file ' + fileName + ' does not exist.')
	return ''

def getInternetText(address):
	'Get the entire text of an internet page.'
	page = urllib.urlopen(address)
	text = page.read()
	page.close()
	return text

def getParameter(arguments, name):
	'Get the parameter of the given name from the arguments.'
	name = '-' + name
	if name not in arguments:
		return ''
	nameIndexNext = arguments.index(name) + 1
	if nameIndexNext >= len(arguments):
		return ''
	return arguments[nameIndexNext]

def getPeerNames(text):
	'Get the peer names.'
	peerNames = []
	for line in getTextLines(text):
		firstLowerSpaceless = ''
		words = getColonDividedWords(line)
		if len(words) > 1:
			firstLowerSpaceless = words[0].lower().replace(' ', '')
			if firstLowerSpaceless == 'peer':
				peerNames.append(words[1].strip())
			else:
				return peerNames
	return peerNames

def getStepOutput(fileName, step, value):
	'Get the step output according to the peers listed in a file.'
	stepText = getStepText(fileName, step, value)
	if stepText != '':
		return stepText
	valueDown = value - step
	previousText = ''
	while valueDown >= 0:
		previousText = getStepText(fileName, step, valueDown)
		if previousText != '':
			print(  'sdjkfhsdkfh')
			return getStepTextRecursively(fileName, previousText, step, valueDown, value)
		valueDown -= step
	return ''

def getStepText(address, step, value):
	'Get the step page by the address, be it a file name or hypertext address.'
	lastDotIndex = address.rfind('.')
	stepAddress = '%s_%s%s' % (address[: lastDotIndex], step* (int(value) / step), address[lastDotIndex :])
	print(  stepAddress)
	return getFileText(stepAddress)

def getStepTextRecursively(fileName, previousText, step, valueDown, value):
	'Get the step text recursively.'
	for valueUp in xrange(valueDown, value, step):
		previousText = getCommonOutputByText(previousText)
		print(  'getCommonOutputByText')
		print(  previousText)
		print(  valueDown)
		print(  value)
		print(  'valueUp')
		print(  valueUp)
	return previousText

def getText(address):
	'Get the page by the address, be it a file name or hypertext address.'
	if address.startswith('http://'):
		return getInternetText(address)
	return getFileText(address)

def getTextLines(text):
	'Get the all the lines of text of a text.'
	textLines = text.replace('\r', '\n').replace('\n\n', '\n').split('\n')
	if len(textLines) == 1:
		if textLines[0] == '':
			return []
	return textLines

def getTexts(addresses):
	'Get the page by the addresses, be they file names or hypertext addresses.'
	pages = []
	for address in addresses:
		pages.append(getFileText(address))
	return pages

def writeOutput(arguments):
	'Write output.'
	print(  arguments)
	fileName = getParameter(arguments, 'input')
	stepString = getParameter(arguments, 'step')
	if stepString == '':
		commonOutput = getCommonOutput(fileName)
		print(  commonOutput)
	else:
		value = 0
		valueString = getParameter(arguments, 'value')
		if valueString != '':
			value = int(valueString)
		stepOutput = getStepOutput(fileName, int(stepString), value)
		print(  'stepOutput')
		print(  stepOutput)


def main():
	'Write output.'
	writeOutput(sys.argv)
#	print(  getText('http://members.axion.net/~enrique/book.html'))

if __name__ == '__main__':
	main()

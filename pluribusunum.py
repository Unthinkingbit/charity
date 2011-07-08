"""
E Pluribus Unum. "Out of many, One."

python pluribusunum.py -input receiver.csv -step 2000 -value 1900

directory, begin
"""

import math
import os
import random
import sys
import urllib


__license__ = 'public domain'


globalMinimumIdenticalProportion = 0.51
globalWriteNextThreshold = 0.7


def getCommaDividedWords(text):
	'Get the words divided around the comma.'
	commaIndex = text.find(',')
	if commaIndex < 0:
		return [text]
	return [text[: commaIndex], text[commaIndex + 1 :]]

def getCommonOutput(fileName):
	'Get the common output according to the peers listed in a file.'
	return getCommonOutputByText(getFileText(fileName))

def getCommonOutputByText(fileText, suffix=''):
	'Get the common output according to the peers listed in a text.'
	peerNames = getPeerNames(fileText)
	pages = getLocationTexts(getSuffixedFileNames(peerNames, suffix))
	minimumIdentical = int(math.ceil(globalMinimumIdenticalProportion * float(len(pages))))
	pageDictionary = {}
	for page in pages:
		firstLine = ''
		lines = getTextLines(page)
		if len(lines) > 0:
			firstLine = lines[0].lower()
		if firstLine.startswith('format') and 'pluribusunum' in firstLine:
			if page in pageDictionary:
				pageDictionary[page] += 1
			else:
				pageDictionary[page] = 1
	for page in pageDictionary:
		if pageDictionary[page] >= minimumIdentical:
			return page
	return ''

def getFileRandomNumber(fileName):
	'Get the random number from a file randomnumber in the same directory as the given file.'
	numberFilePath = os.path.join(os.path.dirname(fileName), 'randomnumber.txt')
	numberFileText = getFileText(numberFilePath)
	if numberFileText == '':
		numberFileText = str(random.random())
		writeFileText(numberFilePath, numberFileText)
	return float(numberFileText)

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
	print(  'Get the entire text of an internet page.')
	try:
		page = urllib.urlopen(address)
		text = page.read()
		page.close()
		return text
	except IOError:
		return ''

def getLocationText(address):
	'Get the page by the address, be it a file name or hypertext address.'
	if address.startswith('http://'):
		return getInternetText(address)
	return getFileText(address)

def getLocationTexts(addresses):
	'Get the page by the addresses, be they file names or hypertext addresses.'
	pages = []
	for address in addresses:
		pages.append(getLocationText(address))
	return pages

def getParameter(arguments, defaultValue, name):
	'Get the parameter of the given name from the arguments.'
	name = '-' + name
	if name not in arguments:
		return defaultValue
	nameIndexNext = arguments.index(name) + 1
	if nameIndexNext >= len(arguments):
		return defaultValue
	return arguments[nameIndexNext]

def getPeerNames(text):
	'Get the peer names.'
	peerNames = []
	for line in getTextLines(text):
		firstLowerSpaceless = ''
		words = getCommaDividedWords(line)
		if len(words) > 1:
			firstLowerSpaceless = words[0].lower().replace(' ', '')
			if firstLowerSpaceless == 'peer':
				peerNames.append(words[1].strip())
			elif firstLowerSpaceless != 'format':
				return peerNames
	return peerNames

def getStepFileName(fileName, step, value):
	'Get the step file name by the file name.'
	return getSuffixedFileName(fileName, str(value / step))

def getStepOutput(fileName, step, value):
	'Get the step output according to the peers listed in a file.'
	stepText = getStepText(fileName, step, value)
	if stepText != '':
		writeNextIfValueHigher(fileName, step, stepText, value)
		return stepText
	valueDown = value - step
	previousText = ''
	while valueDown >= 0:
		previousText = getStepText(fileName, step, valueDown)
		if previousText != '':
			print(  'previousText getStepTextRecursively')
			return getStepTextRecursively(fileName, previousText, step, valueDown, value)
		valueDown -= step
	return ''

def getStepText(fileName, step, value):
	'Get the step text by the file name.'
	return getFileText(getStepFileName(fileName, step, value))

def getStepTextRecursively(fileName, previousText, step, valueDown, value):
	'Get the step text recursively.'
	for valueUp in xrange(valueDown, value, step):
		nextValue = valueUp + step
		previousText = getCommonOutputByText(previousText, str(nextValue / step))
		stepFileName = getStepFileName(fileName, step, nextValue)
		print(  'getCommonOutputByText')
		print(  valueDown)
		print(  value)
		print(  previousText)
		print(  'valueUp')
		print(  valueUp)
		writeFileText(getStepFileName(fileName, step, nextValue), previousText)
	return previousText

def getSuffixedFileName(fileName, suffix=''):
	'Get the file name with the suffix.'
	if suffix == '':
		return fileName
	lastDotIndex = fileName.rfind('.')
	return '%s_%s%s' % (fileName[: lastDotIndex], suffix, fileName[lastDotIndex :])

def getSuffixedFileNames(fileNames, suffix=''):
	'Get the file names with the suffix.'
	suffixedFileNames = []
	for fileName in fileNames:
		suffixedFileNames.append(getSuffixedFileName(fileName, suffix))
	return suffixedFileNames

def getTextLines(text):
	'Get the all the lines of text of a text.'
	textLines = text.replace('\r', '\n').replace('\n\n', '\n').split('\n')
	if len(textLines) == 1:
		if textLines[0] == '':
			return []
	return textLines

def sendOutputTo(outputTo, text):
	'Send output to a file or a standard output.'
	if outputTo == '':
		return
	if outputTo.endswith('stderr'):
		sys.stderr.write(text)
		sys.stderr.write('\n')
		sys.stderr.flush()
		return
	if outputTo.endswith('stdout'):
		sys.stdout.write(text)
		sys.stdout.write('\n')
		sys.stdout.flush()
		return
	writeFileText(outputTo, text)

def writeFileText(fileName, fileText, writeMode='w+'):
	'Write a text to a file.'
	try:
		file = open(fileName, writeMode)
		file.write(fileText)
		file.close()
	except IOError:
		print('The file ' + fileName + ' can not be written to.')

def writeNextIfValueHigher(fileName, step, stepText, value):
	'Write next step file if value is higher than the threshold.'
	remainder = value - step * (value / step)
	floatPart = float(remainder) / float(step)
	lessThanOneMinusThreshold = 0.95 * (1.0 - globalWriteNextThreshold)
	if floatPart < globalWriteNextThreshold + lessThanOneMinusThreshold * getFileRandomNumber(fileName):
		return
	nextValue = value + step
	nextFileName = getStepFileName(fileName, step, nextValue)
	if getFileText(nextFileName) == '':
		nextText = getCommonOutputByText(stepText, str(nextValue / step))
		if nextText != '':
			writeFileText(nextFileName, nextText)

def writeOutput(arguments):
	'Write output.'
	print(  arguments)
	fileName = getParameter(arguments, '', 'input')
	outputTo = getParameter(arguments, 'stdout', 'output')
	stepString = getParameter(arguments, '', 'step')
	text = ''
	if stepString == '':
		text = getCommonOutput(fileName)
	else:
		valueString = getParameter(arguments, '0', 'value')
		text = getStepOutput(fileName, int(stepString), int(valueString))
	sendOutputTo(outputTo, text)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

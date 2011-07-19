"""
E Pluribus Unum. "Out of many, One."

python pluribusunum.py -input receiver.csv -step 2000 -value 1900

"""

import math
import os
import random
import sys
import urllib


__license__ = 'MIT'


globalMinimumIdenticalProportion = 0.500001
globalWriteNextThreshold = 0.75


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

def getFileRandomNumber(directoryPath, fileName):
	'Get the random number from a file randomnumber in the same directory as the given file.'
	if directoryPath == '':
		directoryPath = os.path.dirname(fileName)
	numberFilePath = os.path.join(directoryPath, 'randomnumber.txt')
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
	try:
		page = urllib.urlopen(address)
		text = page.read()
		page.close()
		return text
	except IOError:
		return ''

def getLocationText(address):
	'Get the page by the address, be it a file name or hypertext address.'
	if address.startswith('http://') or address.startswith('https://'):
		return getInternetText(address)
	return getFileText(address)

def getLocationTexts(addresses):
	'Get the pages by the addresses, be they file names or hypertext addresses.'
	pages = []
	for address in addresses:
		pages.append(getLocationText(address))
	return pages

def getOutput(directoryName, fileName, stepString='', valueString=''):
	'Get output.'
	if stepString == '':
		return getCommonOutput(fileName)
	return getStepOutput(directoryName, fileName, int(stepString), int(valueString))

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

def getStepOutput(directoryName, fileName, step, value):
	'Get the step output according to the peers listed in a file.'
	directoryPath = ''
	if directoryName != '':
		directoryPath = os.path.join(os.path.expanduser(directoryName), fileName[: fileName.rfind('.')])
	stepText = getStepText(directoryPath, fileName, step, value)
	if stepText != '':
		writeNextIfValueHigher(directoryPath, fileName, step, stepText, value)
		return stepText
	valueDown = value - step
	previousText = ''
	while valueDown >= 0:
		previousText = getStepText(directoryPath, fileName, step, valueDown)
		if previousText != '':
			print(  'previousText getStepTextRecursively')
			return getStepTextRecursively(directoryPath, fileName, previousText, step, valueDown, value)
		valueDown -= step
	return ''

def getStepText(directoryPath, fileName, step, value):
	'Get the step text by the file name.'
	stepFileName = getStepFileName(fileName, step, value)
	if directoryPath == '':
		return getFileText(stepFileName)
	directorySubName = os.path.join(directoryPath, stepFileName)
	if os.path.exists(directorySubName):
		return getFileText(directorySubName)
	stepText = getFileText(stepFileName)
	if stepText == '':
		return ''
	writeFileText(directorySubName, stepText)
	return stepText

def getStepTextRecursively(directoryPath, fileName, previousText, step, valueDown, value):
	'Get the step text recursively.'
	for valueUp in xrange(valueDown, value, step):
		nextValue = valueUp + step
		previousText = getCommonOutputByText(previousText, str(nextValue / step))
		stepFileName = getStepFileName(fileName, step, nextValue)
		print(  'valueDown')
		print(  valueDown)
		print(  'value')
		print(  value)
		print(  'valueUp')
		print(  valueUp)
		print(  'directoryPath')
		print(  directoryPath)
		writeFileTextByDirectory(directoryPath, stepFileName, previousText)
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
	'Get all the lines of text of a text.'
	textLines = text.replace('\r', '\n').replace('\n\n', '\n').split('\n')
	if len(textLines) == 1:
		if textLines[0] == '':
			return []
	return textLines

def makeDirectory(directoryPath):
	'Make a directory if it does not already exist.'
	if os.path.isdir(directoryPath):
		return
	try:
		print('The following directory was made:')
		print(os.path.abspath(directoryPath))
		os.makedirs(directoryPath)
	except OSError:
		print('Pluribusunum can not make the directory %s so give it read/write permission for that directory and the containing directory.' % directoryPath)

def sendOutputTo(outputTo, text):
	'Send output to a file or a standard output.'
	if outputTo == '':
		return
	if outputTo.endswith('stderr'):
		sys.stderr.write(text)
		sys.stderr.flush()
		return
	if outputTo.endswith('stdout'):
		sys.stdout.write(text)
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

def writeFileTextByDirectory(directoryPath, fileName, fileText, writeMode='w+'):
	'Write a text to a file joined to the directory path.'
	writeFileText(os.path.join(directoryPath, fileName), fileText, writeMode)

def writeNextIfValueHigher(directoryPath, fileName, step, stepText, value):
	'Write next step file if value is higher than the threshold.'
	remainder = value - step * (value / step)
	floatPart = float(remainder) / float(step)
	lessThanOneMinusThreshold = 0.95 * (1.0 - globalWriteNextThreshold)
	fileRandomNumber = getFileRandomNumber(directoryPath, fileName)
	if floatPart < globalWriteNextThreshold + lessThanOneMinusThreshold * fileRandomNumber:
		return
	nextValue = value + step
	nextFileName = getStepFileName(fileName, step, nextValue)
	if getFileText(nextFileName) == '':
		nextText = getCommonOutputByText(stepText, str(nextValue / step))
		if nextText != '':
			writeFileTextByDirectory(directoryPath, nextFileName, nextText)

def writeOutput(arguments):
	'Write output.'
	print(  arguments)
	directoryName = getParameter(arguments, '', 'directory')
	fileName = getParameter(arguments, '', 'input')
	outputTo = getParameter(arguments, 'stdout', 'output')
	stepString = getParameter(arguments, '', 'step')
	valueString = getParameter(arguments, '0', 'value')
	sendOutputTo(outputTo, getOutput(directoryName, fileName, stepString, valueString))


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

"""
E Pluribus Unum. "Out of many, One."

python pluribusunum.py -input donationvalue.txt -output stdout -step 5000 -value 6000
getFileRandomNumber
try url

check that format plu.. is there
getCommaDividedWords
"""

import math
import sys
import urllib


__license__ = 'public domain'


globalMinimumIdenticalProportion = 0.51


# writeOutput, look for next after 0.7


def getColonDividedWords(text):
	'Get the words divided around the colon.'
	colonIndex = text.find(':')
	if colonIndex < 0:
		return [text]
	return [text[: colonIndex], text[colonIndex + 1 :]]

def getCommonOutput(fileName):
	'Get the common output according to the peers listed in a file.'
	return getCommonOutputByText(getFileText(fileName))

def getCommonOutputByText(fileText):
	'Get the common output according to the peers listed in a text.'
	peerNames = getPeerNames(fileText)
	pages = getLocationTexts(peerNames)
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
			elif firstLowerSpaceless != 'format':
				return peerNames
	return peerNames

def getStepFileName(fileName, step, value):
	'Get the step file name by the file name.'
	lastDotIndex = fileName.rfind('.')
	return '%s_%s%s' % (fileName[: lastDotIndex], step * (value / step), fileName[lastDotIndex :])

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
		previousText = getCommonOutputByText(previousText)
		stepFileName = getStepFileName(fileName, step, valueUp + step)
		print(  'getCommonOutputByText')
		print(  valueDown)
		print(  value)
		print(  previousText)
		print(  'valueUp')
		print(  valueUp)
		writeStepText(fileName, step, previousText, valueUp)
	return previousText

def getTextLines(text):
	'Get the all the lines of text of a text.'
	textLines = text.replace('\r', '\n').replace('\n\n', '\n').split('\n')
	if len(textLines) == 1:
		if textLines[0] == '':
			return []
	return textLines

def sendOutputTo(outputTo, text):
	'Send output to a file or a standard output.'
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
	# if higher get commonOutput, write it as getStepFileName(fileName, step, value + step)
	floatPart = float(value - step * (value / step)) / float(step)
	print(  'floatPart')
	print(  floatPart)
	if floatPart < 0.7:
		return
	nextText = getCommonOutputByText(stepText)
	print(  'nextText')
	print(  nextText)
	writeStepText(fileName, step, nextText, value)

def writeOutput(arguments):
	'Write output.'
	print(  arguments)
	fileName = getParameter(arguments, 'input')
	outputTo = getParameter(arguments, 'output')
	stepString = getParameter(arguments, 'step')
	text = ''
	if stepString == '':
		text = getCommonOutput(fileName)
	else:
		value = 0
		valueString = getParameter(arguments, 'value')
		if valueString != '':
			value = int(valueString)
		text = getStepOutput(fileName, int(stepString), value)
	if outputTo != '':
		sendOutputTo(outputTo, text)

def writeStepText(fileName, step, stepText, value):
	'Write the step text to the next step file value.'
	writeFileText(getStepFileName(fileName, step, value + step), stepText)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

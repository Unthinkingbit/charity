"""
E Pluribus Unum. "Out of many, One."
writeOutput

"""

import math
import sys


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
	pages = getPages(peerNames)
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

def getPage(address):
	'Get the page by the address, be it a file name or hypertext address.'
	return getFileText(address)

def getPages(addresses):
	'Get the page by the addresses, be they file names or hypertext addresses.'
	pages = []
	for address in addresses:
		pages.append(getFileText(address))
	return pages

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
	stepPage = getStepPage(fileName, step, value)
	print(  'stepPage')
	print(  stepPage)
	if stepPage != '':
		return
	previousPage = getStepPage(fileName, step, value - step)
	print(  'previousPage')
	print(  previousPage)
	commonOutput = getCommonOutputByText(previousPage)
	print(  'commonOutputpreviousPage')
	print(  commonOutput)
	return ###
	fileText = getFileText(fileName)
	peerNames = getPeerNames(fileText)
	pages = getPages(peerNames)
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

def getStepPage(address, step, value):
	'Get the step page by the address, be it a file name or hypertext address.'
	lastDotIndex = address.rfind('.')
	stepAddress = address[: lastDotIndex] + str(step* (int(value) / step)) + address[lastDotIndex :]
	print(  stepAddress)
	return getFileText(stepAddress)

def getTextLines(text):
	'Get the all the lines of text of a text.'
	textLines = text.replace('\r', '\n').replace('\n\n', '\n').split('\n')
	if len(textLines) == 1:
		if textLines[0] == '':
			return []
	return textLines

def writeOutput(arguments):
	'Write output.'
	print(  arguments)
	commonOutput = getCommonOutput('donationvalue.txt')
	print(  commonOutput)
	stepOutput = getStepOutput('donationvalue.txt', 5000, 6000)
	print(  stepOutput)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

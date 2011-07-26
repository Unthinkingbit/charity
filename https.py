"""
Read https address and save text to a file."

python https.py -address https://raw.github.com/Unthinkingbit/charity/master/receiver_0.csv -out https.txt

"""

import sys
import urllib


__license__ = 'MIT'


def getInternetText(address):
	'Get the entire text of an internet page.'
	try:
		page = urllib.urlopen(address)
		text = page.read()
		page.close()
		return text
	except IOError:
		return ''

def getParameter(arguments, defaultValue, name):
	'Get the parameter of the given name from the arguments.'
	name = '-' + name
	if name not in arguments:
		return defaultValue
	nameIndexNext = arguments.index(name) + 1
	if nameIndexNext >= len(arguments):
		return defaultValue
	return arguments[nameIndexNext]

def writeFileText(fileName, fileText, writeMode='w+'):
	'Write a text to a file.'
	try:
		file = open(fileName, writeMode)
		file.write(fileText)
		file.close()
	except IOError:
		print('The file ' + fileName + ' can not be written to.')

def writeOutput(arguments):
	'Write output.'
	address = getParameter(arguments, '', 'address')
	if len(arguments) == 2:
		address = arguments[1]
	outputName = getParameter(arguments, 'https.txt', 'output')
	internetText = getInternetText(address)
	if internetText != '':
		writeFileText(outputName, internetText)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

"""
Wikicopy is a program to download the articles of a dokuwiki and save them in a zip file.


==Commands==
===Help===
The -h option, the -help option, will print the help, which is this document. The example follows:
python account.py -h

===Input===
Default is http://devtome.com

The -input option sets the input file name. The example follows:
python wikicopy.py -input http://devtome.com


==Install==
For wikicopy to run, you need Python 2.x, wikicopy will probably not run with python 3.x. To check if it is on your machine, in a terminal type:
python

If python 2.x is not on your machine, download the latest python 2.x, which is available from:
http://www.python.org/download/
"""

import almoner
import devtome
import os
import shutil
import sys
import time


__license__ = 'MIT'


def writeOutput(arguments):
	'Write output.'
	if '-h' in arguments or '-help' in arguments:
		print(__doc__)
		return
	writeZipFile(almoner.getParameter(arguments, 'http://devtome.com', 'input'))

def writeZipFile(wikiAddress):
	'Write zip file.'
	isArticle = False
	print('Copying:')
	print(wikiAddress)
	print('')
	popularPageAddress = wikiAddress + '/doku.php?id=start&do=index/'
	lines = almoner.getTextLines(almoner.getInternetText(popularPageAddress))
	numberOfFiles = 0
	wikiPath = wikiAddress
	if 'http://' in wikiPath:
		wikiPath = wikiPath[len('http://') :]
	if '.' in wikiPath:
		wikiPath = wikiPath[: wikiPath.find('.')]
	if os.path.isdir(wikiPath):
		shutil.rmtree(wikiPath)
	os.makedirs(wikiPath)
	prefix = '?id='
	prefixLength = len(prefix)
	previousLetter = '0'
	for line in lines:
		if line.startswith('</ul>'):
			isArticle = False
		if isArticle and '&amp;' not in line:
			prefixIndex = line.find(prefix) + prefixLength
			title = line[prefixIndex :]
			quoteIndex = title.find('"')
			title = title[: quoteIndex]
			if len(title) > 0:
				letter = title[0]
				if letter != previousLetter:
					previousLetter = letter
					print('Copying articles starting with %s.' % letter.upper())
			sourceText = devtome.getSourceText(wikiAddress + '/doku.php?id=%s&do=edit' % title)
			time.sleep(2)
			fileName = os.path.join(wikiPath, title)
			almoner.writeFileText(fileName, sourceText)
			numberOfFiles += 1
		if line == '<ul class="idx">':
			isArticle = True
	print('There were %s files in the wiki.\n' % numberOfFiles)
	almoner.writeZipFileByFolder(wikiPath)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

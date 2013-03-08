"""
Wikicopy is a program to download the articles of a wiki and save them in a zip file.


==Commands==
===Help===
The -h option, the -help option, will print the help, which is this document.  The example follows:
python account.py -h

===Input===
Default is http://devtome.com

The -input option sets the input file name.  The example follows:
python wikicopy.py -input http://devtome.com


==Install==
For wikicopy to run, you need Python 2.x, almoner will probably not run with python 3.x.  To check if it is on your machine, in a terminal type:
python

If python 2.x is not on your machine, download the latest python 2.x, which is available from:
http://www.python.org/download/
"""

import almoner
import os
import shutil
import sys
import tomecount


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
	for line in lines:
		if line.startswith('</ul>'):
			isArticle = False
		if isArticle and '&amp;' not in line:
			prefixIndex = line.find(prefix) + prefixLength
			title = line[prefixIndex :]
			quoteIndex = title.find('"')
			title = title[: quoteIndex]
			fileName = os.path.join(wikiPath, title)
			sourceText = tomecount.getSourceText(wikiAddress + '/doku.php?id=%s&do=edit' % title)
			almoner.writeFileText(fileName, sourceText)
			numberOfFiles += 1
		if line == '<ul class="idx">':
			isArticle = True
	print('There were %s files in the wiki.\n' % numberOfFiles)
	zipNameExtension = wikiPath + '.zip'
	if zipNameExtension in os.listdir(os.getcwd()):
		os.remove(zipNameExtension)
	shellCommand = 'zip -r %s %s' % (zipNameExtension, wikiPath)
	if os.system(shellCommand) != 0:
		print('Failed to execute the following command in removeZip in wikicopy.')
		print(shellCommand)
	else:
		print('The wiki zip file has been written to:\n%s\n' % zipNameExtension)
	if os.path.isdir(wikiPath):
		shutil.rmtree(wikiPath)


def main():
	'Write output.'
	writeOutput(sys.argv)

if __name__ == '__main__':
	main()

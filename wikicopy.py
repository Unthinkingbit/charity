"""
Wikicopy is a program to download the articles of a wiki and save them in a zip file.


==Commands==
===Help===
The -h option, the -help option, will print the help, which is this document.  The example follows:
python account.py -h

===Input===
Default is http://devtome.org

The -input option sets the input file name.  The example follows:
python wikicopy.py -input http://devtome.org


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
	writeZipFile(almoner.getParameter(arguments, 'http://devtome.org', 'input'))

def writeZipFile(wikiAddress):
	'Write zip file.'
	isArticle = False
	popularPageAddress = wikiAddress + '/wiki/index.php?title=Special:PopularPages&limit=100000&offset=0'
	lines = almoner.getTextLines(almoner.getInternetText(popularPageAddress))
	numberOfFiles = 0
	wikiPath = wikiAddress
	if 'http://' in wikiPath:
		wikiPath = wikiPath[len('http://') :]
	if '.' in wikiPath:
		wikiPath = wikiPath[: wikiPath.rfind('.')]
	if os.path.isdir(wikiPath):
		shutil.rmtree(wikiPath)
	os.makedirs(wikiPath)
	prefixLength = len('<li><a href="/wiki/index.php?title=')
	for line in lines:
		if line.startswith('</ol>'):
			isArticle = False
		if isArticle:
			title = line[prefixLength :]
			quoteIndex = title.find('"')
			title = title[: quoteIndex]
			fileName = os.path.join(wikiPath, title)
			sourceText = tomecount.getSourceText('http://devtome.org/wiki/index.php?title=%s&action=edit' % title)
			almoner.writeFileText(fileName, sourceText)
			numberOfFiles += 1
		if line.replace('"', "'").replace('  ', ' ') == "<ol start='1' class='special'>":
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

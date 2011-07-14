#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include "stdio.h"
#include <string>
#include <vector>

std::string getCoinAddressString(const std::string& fileName, int height);
std::vector<std::vector<std::string> > getCoinLists(const std::string& text);
std::vector<std::string> getCommaDividedWords(const std::string& text);
std::string getFileText(const std::string& fileName);
std::string getLower(std::string& text);
std::string getReplaced(std::string& text, const std::string& searchString, const std::string& replaceString);
std::string getSuffixedFileName(const std::string& fileName, const std::string& suffix="");
std::vector<std::string> getTextLines(const std::string& text);
std::vector<std::string> getTokens(const std::string& text, const std::string& delimiters=" ");


// Get the coin address string for a height.
std::string getCoinAddressString(const std::string& fileName, int height)
{
	std::string suffixedFileName = getSuffixedFileName(fileName, std::string("_0"));
	std::string fileText = getFileText(suffixedFileName);
	std::vector<std::vector<std::string> > coinLists = getCoinLists(fileText);
	int modulo = height % (int)coinLists.size();
	return coinLists[modulo][0];
}

// Get the coin lists from a text.'
std::vector<std::vector<std::string> > getCoinLists(const std::string& text)
{
	std::vector<std::vector<std::string> > coinLists;
	std::vector<std::string> textLines = getTextLines(text);
	for (int lineIndex = 0; lineIndex < textLines.size(); lineIndex++)
	{
		std::string line = textLines[lineIndex];
		std::string firstLowerSpaceless = std::string();
		std::vector<std::string> words = getCommaDividedWords(line);
		if (words.size() > 0)
		{
			std::string firstLower = getLower(words[0]);
			firstLowerSpaceless = getReplaced(firstLower, std::string(" "), std::string());
		}
		if (firstLowerSpaceless == std::string("coin"))
		{
			std::vector<std::string> tokens = getTokens(words[1], ",");
			coinLists.push_back(tokens);
		}
	}

	return coinLists;
}

// Get the words divided around the comma.
std::vector<std::string> getCommaDividedWords(const std::string& text)
{
	std::vector<std::string> commaDividedWords;
	int commaIndex = text.find(',');
	if (commaIndex == std::string::npos)
	{
		commaDividedWords.push_back(text);
		return commaDividedWords;
	}

	commaDividedWords.push_back(text.substr(0, commaIndex));
	commaDividedWords.push_back(text.substr(commaIndex + 1));
	return commaDividedWords;
}

// Get the entire text of a file.
std::string getFileText(const std::string& fileName)
{
	std::ifstream fileStream(fileName.c_str());
	if (!fileStream.is_open())
	{
		return std::string();
	}
	std::string fileText;
	fileStream.seekg(0, std::ios::end);
	fileText.reserve(fileStream.tellg());
	fileStream.seekg(0, std::ios::beg);
	fileText.assign((std::istreambuf_iterator<char>(fileStream)), std::istreambuf_iterator<char>());
	return fileText;
}

// Get the lowercase string.
std::string getLower(std::string& text)
{
	int textLength = text.length();

	for(int characterIndex = 0; characterIndex < textLength; characterIndex++)
	{
		text[characterIndex] = std::tolower(text[characterIndex]);
	}

	return text;
}

// Get the string with the search string replaced with the replace string.
std::string getReplaced(std::string& text, const std::string& searchString, const std::string& replaceString)
{
	std::string::size_type position = 0;

	while ((position = text.find(searchString, position)) != std::string::npos)
	{
		text.replace(position, searchString.size(), replaceString );
		position++;
	}

	return text;
}

// Get the file name with the suffix just before the extension.
std::string getSuffixedFileName(const std::string& fileName, const std::string& suffix)
{
	if (suffix == std::string())
		return fileName;

	int lastDotIndex = fileName.rfind(".");

	return fileName.substr(0, lastDotIndex) + suffix + fileName.substr(lastDotIndex);
}

// Get all the lines of text of a text.
std::vector<std::string> getTextLines(const std::string& text)
{
	return getTokens(text, std::string("\n"));
}

// Get the tokens of the text split by the delimeters.
std::vector<std::string> getTokens(const std::string& text, const std::string& delimiters)
{
	std::vector<std::string> tokens;
	std::string::size_type lastPosition = text.find_first_not_of(delimiters, 0);
	std::string::size_type position = text.find_first_of(delimiters, lastPosition);

	while (std::string::npos != position || std::string::npos != lastPosition)
	{
		tokens.push_back(text.substr(lastPosition, position - lastPosition));
		lastPosition = text.find_first_not_of(delimiters, position);
		position = text.find_first_of(delimiters, lastPosition);
	}

	return tokens;
}

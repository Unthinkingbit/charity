#include <QDir>
#include <QFileInfo>


std::string getCoinAddressString(const std::string& fileName, int height); // DeprecatedDeprecated
std::vector<std::string> getCoinAddressStrings(const std::string& fileName, int height); // DeprecatedDeprecated
std::vector<std::string> getCoinAddressStrings(const std::string& dataDirectory, const std::string& fileName, int height);
std::vector<std::string> getCoinList(const std::string& fileName, int height);
std::vector<std::vector<std::string> > getCoinLists(const std::string& text);
std::vector<std::string> getCommaDividedWords(const std::string& text);
std::string getDirectoryName(const std::string& fileName);
double getDouble(const std::string& doubleString);
double getFileRandomNumber(const std::string& dataDirectory, const std::string& fileName);
std::string getFileText(const std::string& fileName);
bool getIsSufficientAmount(std::vector<std::string> addressStrings, std::vector<int64> amounts, const std::string& dataDirectory, const std::string& fileName, int height, int64 share);
std::string getJoinedPath(const std::string& directoryPath, const std::string& fileName);
std::string getLower(const std::string& text);
std::vector<std::string> getPeerNames(const std::string& text);
std::string getReplaced(const std::string& text, const std::string& searchString, const std::string& replaceString);
bool getStartsWith(const std::string& firstString, const std::string& secondString);
std::string getStringByBoolean(bool boolean);
std::string getStringByDouble(double doublePrecision);
std::string getSuffixedFileName(const std::string& fileName, const std::string& suffix="");
std::vector<std::string> getSuffixedFileNames(std::vector<std::string> fileNames, const std::string& suffix="");
std::vector<std::string> getSuffixedFileNames(std::vector<std::string> fileNames, const std::string& suffix);
std::vector<std::string> getTextLines(const std::string& text);
std::vector<std::string> getTokens(const std::string& text, const std::string& delimiters=" ");
void writeFileText(const std::string& fileName, const std::string& fileText);


// DeprecatedDeprecatedDeprecatedDeprecated
std::string getCoinAddressString(const std::string& fileName, int height)
{
	return getCoinList(fileName, height)[0];
}

// DeprecatedDeprecatedDeprecatedDeprecated
std::vector<std::string> getCoinAddressStrings(const std::string& fileName, int height)
{
	return getCoinList(fileName, height);
}

// Get the coin address strings for a height.
std::vector<std::string> getCoinAddressStrings(const std::string& dataDirectory, const std::string& fileName, int height)
{
	return getCoinList(fileName, height);
}

// Get the coin list from a text for a height.
std::vector<std::string> getCoinList(const std::string& fileName, int height)
{
	std::string suffixedFileName = getSuffixedFileName(fileName, std::string("_0"));
	std::string fileText = getFileText(suffixedFileName);
	std::vector<std::vector<std::string> > coinLists = getCoinLists(fileText);
	int modulo = height % (int)coinLists.size();

	return coinLists[modulo];
}

// Get the coin lists from a text.
std::vector<std::vector<std::string> > getCoinLists(const std::string& text)
{
	std::vector<std::vector<std::string> > coinLists;
	std::vector<std::string> textLines = getTextLines(text);
	bool isCoinSection = false;

	for (int lineIndex = 0; lineIndex < textLines.size(); lineIndex++)
	{
		std::string firstLowerSpaceless = std::string();
		std::string line = textLines[lineIndex];
		std::vector<std::string> words = getCommaDividedWords(line);

		if (words.size() > 0)
			firstLowerSpaceless = getReplaced(getLower(words[0]), std::string(" "), std::string());

		if (firstLowerSpaceless == std::string("coin"))
		{
			std::vector<std::string> coinList = getTokens(words[1], ",");
			coinLists.push_back(coinList);
		}

		if (firstLowerSpaceless == std::string("_endcoins"))
			isCoinSection = false;

		if (isCoinSection)
		{
			std::vector<std::string> coinList = getTokens(line, ",");
			coinLists.push_back(coinList);
		}

		if (firstLowerSpaceless == std::string("_begincoins"))
			isCoinSection = true;
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

// Get the directory name of the given file.
std::string getDirectoryName(const std::string& fileName)
{
	return QFileInfo(QString(fileName.c_str())).dir().dirName().toStdString();
}

// Get a double precision float from a string.
double getDouble(const std::string& doubleString)
{
	double doublePrecision;
	std::istringstream doubleStream(doubleString);

	doubleStream >> doublePrecision;
	return doublePrecision;
}

// Get the random number from a file random_number in the same directory as the given file.
double getFileRandomNumber(const std::string& dataDirectory, const std::string& fileName)
{
	std::string directoryPath = dataDirectory.substr();
	if (dataDirectory == std::string())
		directoryPath = getDirectoryName(fileName);
	std::string numberFilePath = getJoinedPath(directoryPath, std::string("random_number.txt"));
	std::string numberFileText = getFileText(numberFilePath);

	if (numberFileText == std::string())
	{
		srand(time(NULL));
		double randomDouble = ((double)(rand() % 10000) + 0.5) / 10000.0;
		numberFileText = getStringByDouble(randomDouble);
		writeFileText(numberFilePath, numberFileText);
	}

	return getDouble(numberFileText);
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

// Determine if the transactions add up to a share per address for each address.
bool getIsSufficientAmount(std::vector<std::string> addressStrings, std::vector<int64> amounts, const std::string& dataDirectory, const std::string& fileName, int height, int64 share)
{
	std::vector<std::string> coinAddressStrings = getCoinAddressStrings(dataDirectory, fileName, height);
	std::map<std::string, int64> receiverMap;
	int64 sharePerAddress = share / (int64)coinAddressStrings.size();

	for (int i = 0; i < coinAddressStrings.size(); i++)
		receiverMap[coinAddressStrings[i]] = (int64)0;

	for (int i = 0; i < addressStrings.size(); i++)
	{
		std::string addressString = addressStrings[i];

		if (receiverMap.count(addressString) > 0)
			receiverMap[addressString] += amounts[i];
	}

	for (int i = 0; i < coinAddressStrings.size(); i++)
	{
		if (receiverMap[coinAddressStrings[i]] < sharePerAddress)
			return false;
	}

	return true;
}

// Get the directory path joined with the file name.
std::string getJoinedPath(const std::string& directoryPath, const std::string& fileName)
{
	return QDir(QString(directoryPath.c_str())).absoluteFilePath(QString(fileName.c_str())).toStdString();
}

// Get the lowercase string.
std::string getLower(const std::string& text)
{
	int textLength = text.length();
	std::string lower = text.substr();

	for(int characterIndex = 0; characterIndex < textLength; characterIndex++)
	{
		lower[characterIndex] = std::tolower(text[characterIndex]);
	}

	return lower;
}

// Get the peer names from the text.
std::vector<std::string> getPeerNames(const std::string& text)
{
	std::vector<std::string> peerNames;
	std::vector<std::string> textLines = getTextLines(text);

	for (int lineIndex = 0; lineIndex < textLines.size(); lineIndex++)
	{
		std::string firstLowerSpaceless = std::string();
		std::string line = textLines[lineIndex];
		std::vector<std::string> words = getCommaDividedWords(line);

		if (words.size() > 0)
			firstLowerSpaceless = getReplaced(getLower(words[0]), std::string(" "), std::string());

		if (firstLowerSpaceless == std::string("peer"))
			peerNames.push_back(getReplaced(words[1], std::string(" "), std::string()));

		if (firstLowerSpaceless != std::string("format"))
			return peerNames;
	}

	return peerNames;
}

// Get the string with the search string replaced with the replace string.
std::string getReplaced(const std::string& text, const std::string& searchString, const std::string& replaceString)
{
	std::string::size_type position = 0;
	std::string replaced = text.substr();

	while ((position = replaced.find(searchString, position)) != std::string::npos)
	{
		replaced.replace(position, searchString.size(), replaceString );
		position++;
	}

	return replaced;
}

// Determine if the first string starts with the second string.
bool getStartsWith(const std::string& firstString, const std::string& secondString)
{
	if (firstString.substr(0, secondString.size()) == secondString)
		return true;

	return false;
}

// Get the string from the boolean.
std::string getStringByBoolean(bool boolean)
{
	if (boolean)
		return std::string("true");
	return std::string("false");
}

// Get the string from the double precision float.
std::string getStringByDouble(double doublePrecision)
{
	std::ostringstream doubleStream;

	doubleStream << doublePrecision;

	return doubleStream.str();
}

// Get the file name with the suffix just before the extension.
std::string getSuffixedFileName(const std::string& fileName, const std::string& suffix)
{
	if (suffix == std::string())
		return fileName;

	int lastDotIndex = fileName.rfind(".");

	return fileName.substr(0, lastDotIndex) + suffix + fileName.substr(lastDotIndex);
}

// Get the file names with the suffixes just before the extension.
std::vector<std::string> getSuffixedFileNames(std::vector<std::string> fileNames, const std::string& suffix)
{
	std::vector<std::string> suffixedFileNames;

	for(int fileNameIndex = 0; fileNameIndex < fileNames.size(); fileNameIndex++)
		suffixedFileNames.push_back(getSuffixedFileName(fileNames[fileNameIndex], suffix));

	return suffixedFileNames;
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

// Write a text to a file.
void writeFileText(const std::string& fileName, const std::string& fileText)
{
	std::ofstream fileStream(fileName.c_str());

	if (fileStream.is_open())
	{
	  fileStream << fileText;
	  fileStream.close();
	}
	else printf("The file %s can not be written to.\n", fileName.c_str());
}

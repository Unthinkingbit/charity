//////////////////////////////////////////////////////////////////////////////////////////////////////////
//
// Note: receiver.h uses QT networking classes.
// So, in order for receiver.h to compile, it is necessary to add the following line to the .pro file:
//
// QT += network
//
// Right after INCLUDEPATH is a good place for it, although it can go anywhere.
// The 'QT' is uppercase and 'network' is lower case.
//
//////////////////////////////////////////////////////////////////////////////////////////////////////////


#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QHttp>
#include <QString>
#include <QUrl>


std::string getCoinAddressString(const std::string& fileName, int height); // DeprecatedDeprecated
std::vector<std::string> getCoinAddressStrings(const std::string& fileName, int height); // DeprecatedDeprecated
std::vector<std::string> getCoinAddressStrings(const std::string& dataDirectory, const std::string& fileName, int height);
std::vector<std::string> getCoinList(const std::string& fileName, int height);
std::vector<std::vector<std::string> > getCoinLists(const std::string& text);
std::vector<std::string> getCommaDividedWords(const std::string& text);
std::vector<std::string> getDirectoryNames(const std::string& directoryName);
std::string getDirectoryPath(const std::string& fileName);
double getDouble(const std::string& doubleString);
bool getExists(const std::string& fileName);
double getFileRandomNumber(const std::string& dataDirectory, const std::string& fileName);
std::string getFileText(const std::string& fileName);
bool getIsSufficientAmount(std::vector<std::string> addressStrings, std::vector<int64> amounts, const std::string& dataDirectory, const std::string& fileName, int height, int64 share);
std::string getJoinedPath(const std::string& directoryPath, const std::string& fileName);
std::string getLower(const std::string& text);
std::vector<std::string> getPeerNames(const std::string& text);
std::string getReplaced(const std::string& text, const std::string& searchString, const std::string& replaceString);
bool getStartsWith(const std::string& firstString, const std::string& secondString);
std::string getStepFileName(const std::string& fileName, int step, int value);
std::string getStepText(const std::string& dataDirectory, const std::string& fileName, int step, int value);
std::string getStringByBoolean(bool boolean);
std::string getStringByDouble(double doublePrecision);
std::string getStringByInt(int integer);
std::string getSuffixedFileName(const std::string& fileName, const std::string& suffix="");
std::vector<std::string> getSuffixedFileNames(std::vector<std::string> fileNames, const std::string& suffix="");
std::vector<std::string> getSuffixedFileNames(std::vector<std::string> fileNames, const std::string& suffix);
std::vector<std::string> getTextLines(const std::string& text);
std::vector<std::string> getTokens(const std::string& text, const std::string& delimiters=" ");
void makeDirectory(const std::string& directoryPath);
void writeFileText(const std::string& fileName, const std::string& fileText);
void writeFileTextByDirectory(const std::string& directoryPath, const std::string& fileName, const std::string& fileText);


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

std::vector<std::string> getDirectoryNames(const std::string& directoryName)
{
	std::vector<std::string> directoryNames;
	struct dirent *entry;
	DIR *directory = opendir(directoryName.c_str());

	if (directory == NULL)
	{
		printf("Warning, can not open directory: %s", directoryName);
		return directoryNames;
	}

	while((entry = readdir(directory)))
		directoryNames.push_back(std::string(entry->d_name));

	closedir(directory);

	return directoryNames;
}

// Get the directory name of the given file.
std::string getDirectoryPath(const std::string& fileName)
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

// Determine if the file exists.
bool getExists(const std::string& fileName)
{
	return QFileInfo(QString(fileName.c_str())).exists();
}

// Get the random number from a file random_number in the same directory as the given file.
double getFileRandomNumber(const std::string& dataDirectory, const std::string& fileName)
{
	std::string directoryPath = dataDirectory.substr();
	if (dataDirectory == std::string())
		directoryPath = getDirectoryPath(fileName);
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
		return std::string();

	std::string fileText;
	fileStream.seekg(0, std::ios::end);
	fileText.reserve(fileStream.tellg());
	fileStream.seekg(0, std::ios::beg);
	fileText.assign((std::istreambuf_iterator<char>(fileStream)), std::istreambuf_iterator<char>());
	fileStream.close();

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

// Get the step file name by the file name.
std::string getStepFileName(const std::string& fileName, int step, int value)
{
	return getSuffixedFileName(fileName, getStringByInt(value / step));
}

// Get the random number from a file random_number in the same directory as the given file.
std::string getStepText(const std::string& dataDirectory, const std::string& fileName, int step, int value)
{
	std::string stepFileName = getStepFileName(fileName, step, value);
	if (dataDirectory == std::string())
		return getFileText(stepFileName);
	std::string directorySubName = getJoinedPath(dataDirectory, stepFileName);
	if (getExists(directorySubName))
		return getFileText(directorySubName);
	std::string stepText = getFileText(stepFileName);
	if (stepText == std::string())
		return std::string();
	writeFileText(directorySubName, stepText);
	return stepText;
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

// Get the string from the integer.
std::string getStringByInt(int integer)
{
	std::ostringstream integerStream;

	integerStream << integer;

	return integerStream.str();
}

// Get the file name with the suffix just before the extension.
std::string getSuffixedFileName(const std::string& fileName, const std::string& suffix)
{
	if (suffix == std::string())
		return fileName;

	int lastDotIndex = fileName.rfind(".");

	if (lastDotIndex == std::string::npos)
		return fileName + suffix;
	return fileName.substr(0, lastDotIndex) + std::string("_") + suffix + fileName.substr(lastDotIndex);
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

// Make a directory if it does not already exist.
void makeDirectory(const std::string& directoryPath)
{
	if (getExists(directoryPath))
		return;
	if (QDir(QString()).mkpath(QString(directoryPath.c_str())))
		printf("The following directory was made: %s", directoryPath.c_str());
	else
		printf("Receiver.h can not make the directory %s so give it read/write permission for that directory.", directoryPath.c_str());
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

// Write a text to a file joined to the directory path.
void writeFileTextByDirectory(const std::string& directoryPath, const std::string& fileName, const std::string& fileText)
{
	writeFileText(getJoinedPath(directoryPath, fileName), fileText);
}

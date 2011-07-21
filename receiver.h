#include <boost/asio.hpp>
#include <boost/filesystem.hpp>

using namespace boost;
using namespace std;


static const double globalMinimumIdenticalProportion = 0.500001;
static const double globalWriteNextThreshold = 0.75;
static const int globalStepDefault = 4000;


vector<string> getCoinAddressStrings(const string& dataDirectory, const string& fileName, int height, int step=globalStepDefault);
vector<string> getCoinList(const string& directoryPath, const string& fileName, int height, int step);
vector<vector<string> > getCoinLists(const string& text);
vector<string> getCommaDividedWords(const string& text);
string getCommonOutputByText(const string& fileName, const string& suffix=string(""));
string getDirectoryPath(const string& fileName);
double getDouble(const string& doubleString);
bool getExists(const string& fileName);
double getFileRandomNumber(const string& dataDirectory, const string& fileName);
string getFileText(const string& fileName);
int getInt(const string& integerString);
string getInternetText(const string& address);
bool getIsSufficientAmount(vector<string> addressStrings, vector<int64> amounts, const string& dataDirectory, const string& fileName, int height, int64 share, int step=globalStepDefault);
string getJoinedPath(const string& directoryPath, const string& fileName);
string getLocationText(const string& address);
vector<string> getLocationTexts(vector<string> addresses);
string getLower(const string& text);
vector<string> getPeerNames(const string& text);
string getReplaced(const string& text, const string& searchString, const string& replaceString);
bool getStartsWith(const string& firstString, const string& secondString);
string getStepFileName(const string& fileName, int height, int step);
string getStepOutput(const string& directoryPathInput, const string& fileName, int height, int step);
string getStepText(const string& dataDirectory, const string& fileName, int height, int step);
string getStepTextRecursively(const string& directoryPath, const string& fileName, int height, const string& previousTextInput, int step, int valueDown);
string getStringByBoolean(bool boolean);
string getStringByDouble(double doublePrecision);
string getStringByInt(int integer);
string getSuffixedFileName(const string& fileName, const string& suffix=string());
vector<string> getSuffixedFileNames(vector<string> fileNames, const string& suffix=string());
vector<string> getTextLines(const string& text);
vector<string> getTokens(const string& text=string(), const string& delimiters=string(" "));
void makeDirectory(const string& directoryPath);
void writeFileText(const string& fileName, const string& fileText);
void writeFileTextByDirectory(const string& directoryPath, const string& fileName, const string& fileText);
void writeNextIfValueHigher(const string& directoryPath, const string& fileName, int height, int step, const string& stepText);


// Get the coin address strings for a height.
vector<string> getCoinAddressStrings(const string& dataDirectory, const string& fileName, int height, int step)
{
	return getCoinList(dataDirectory, fileName, height, step);
}

// Get the coin list from a text for a height.
vector<string> getCoinList(const string& directoryPath, const string& fileName, int height, int step)
{
	string stepOutput = getStepOutput(directoryPath, fileName, height, step);
	vector<vector<string> > coinLists = getCoinLists(stepOutput);

	if ((int)coinLists.size() == 0)
	{
		printf("Warning, no coin lists were found for the file: %s", fileName.c_str());
		return getTokens();
	}

	int remainder = height - step * (height / step);
	int modulo = remainder % (int)coinLists.size();

	return coinLists[modulo];
}

// Get the coin lists from a text.
vector<vector<string> > getCoinLists(const string& text)
{
	vector<vector<string> > coinLists;
	vector<string> textLines = getTextLines(text);
	bool isCoinSection = false;

	for (int lineIndex = 0; lineIndex < textLines.size(); lineIndex++)
	{
		string firstLowerSpaceless = string();
		string line = textLines[lineIndex];
		vector<string> words = getCommaDividedWords(line);

		if (words.size() > 0)
			firstLowerSpaceless = getReplaced(getLower(words[0]), string(" "), string());

		if (firstLowerSpaceless == string("coin"))
		{
			vector<string> coinList = getTokens(words[1], ",");
			coinLists.push_back(coinList);
		}

		if (firstLowerSpaceless == string("_endcoins"))
			isCoinSection = false;

		if (isCoinSection)
		{
			vector<string> coinList = getTokens(line, ",");
			coinLists.push_back(coinList);
		}

		if (firstLowerSpaceless == string("_begincoins"))
			isCoinSection = true;
	}

	return coinLists;
}

// Get the words divided around the comma.
vector<string> getCommaDividedWords(const string& text)
{
	vector<string> commaDividedWords;
	int commaIndex = text.find(',');

	if (commaIndex == string::npos)
	{
		commaDividedWords.push_back(text);
		return commaDividedWords;
	}

	commaDividedWords.push_back(text.substr(0, commaIndex));
	commaDividedWords.push_back(text.substr(commaIndex + 1));
	return commaDividedWords;
}

// Get the common output according to the peers listed in a text.
string getCommonOutputByText(const string& fileText, const string& suffix)
{
	vector<string> peerNames = getPeerNames(fileText);
	vector<string> pages = getLocationTexts(getSuffixedFileNames(peerNames, suffix));
	int minimumIdentical = (int)ceil(globalMinimumIdenticalProportion * (double)pages.size());
	map<string, int> pageMap;

	for (vector<string>::iterator pageIterator = pages.begin(); pageIterator < pages.end(); pageIterator++)
	{
		string firstLine = string();
		vector<string> lines = getTextLines(*pageIterator);

		if (lines.size() > 0)
			firstLine = getLower(lines[0]);

		if (getStartsWith(firstLine, string("format")) && (firstLine.find(string("pluribusunum")) != string::npos))
		{
			if (pageMap.count(*pageIterator))
				pageMap[*pageIterator] += 1;
			else
				pageMap[*pageIterator] = 1;
		}
	}

	for (map<string,int>::iterator pageMapIterator = pageMap.begin(); pageMapIterator != pageMap.end(); pageMapIterator++)
		if ((*pageMapIterator).second >= minimumIdentical)
			return (*pageMapIterator).first;

	return string();
}

// Get the directory name of the given file.
string getDirectoryPath(const string& fileName)
{
	return (filesystem::path(fileName)).parent_path().string();
}

// Get a double precision float from a string.
double getDouble(const string& doubleString)
{
	double doublePrecision;
	istringstream doubleStream(doubleString);

	doubleStream >> doublePrecision;
	return doublePrecision;
}

// Determine if the file exists.
bool getExists(const string& fileName)
{
	return filesystem::exists(fileName);
}

// Get the random number from a file random_number in the same directory as the given file.
double getFileRandomNumber(const string& dataDirectory, const string& fileName)
{
	string directoryPath = dataDirectory.substr();
	if (dataDirectory == string())
		directoryPath = getDirectoryPath(fileName);
	string numberFilePath = getJoinedPath(directoryPath, string("random_number.txt"));
	string numberFileText = getFileText(numberFilePath);

	if (numberFileText == string())
	{
		srand(time(NULL));
		double randomDouble = ((double)(rand() % 10000) + 0.5) / 10000.0;
		numberFileText = getStringByDouble(randomDouble);
		writeFileText(numberFilePath, numberFileText);
	}

	return getDouble(numberFileText);
}

// Get the entire text of a file.
string getFileText(const string& fileName)
{
	ifstream fileStream(fileName.c_str());

	if (!fileStream.is_open())
		return string();

	string fileText;
	fileStream.seekg(0, ios::end);
	fileText.reserve(fileStream.tellg());
	fileStream.seekg(0, ios::beg);
	fileText.assign((istreambuf_iterator<char>(fileStream)), istreambuf_iterator<char>());
	fileStream.close();
	return fileText;
}

// Get an integer from a string.
int getInt(const string& integerString)
{
	int integer;
	istringstream intStream(integerString);

	intStream >> integer;
	return integer;
}

// Get the entire text of an internet page.
string getInternetText(const string& address)
{
	try
	{
		string host = address.substr();
		string httpPrefix = string("http://");
		string path = string();

		if (host.substr(0, httpPrefix.size()) == httpPrefix)
			host = host.substr(httpPrefix.size());

		int slashIndex = host.find('/');

		if (slashIndex != string::npos)
		{
			path = host.substr(slashIndex);
			host = host.substr(0, slashIndex);
		}

		asio::io_service io_service;

		// Get a list of endpoints corresponding to the server name.
		asio::ip::tcp::resolver resolver(io_service);
		asio::ip::tcp::resolver::query query(host.c_str(), "http");
		asio::ip::tcp::resolver::iterator endpoint_iterator = resolver.resolve(query);

		// Try each endpoint until we successfully establish a connection.
		asio::ip::tcp::socket socket(io_service);
		socket.connect(*endpoint_iterator++);

		// Form the request. We specify the "Connection: close" header so that the
		// server will close the socket after transmitting the response. This will
		// allow us to treat all data up until the EOF as the content.
		asio::streambuf request;
		ostream request_stream(&request);
		request_stream << "GET " << path << " HTTP/1.0\r\n";
		request_stream << "Host: " << host << "\r\n";
		request_stream << "Accept: */*\r\n";
		request_stream << "Connection: close\r\n\r\n";

		// Send the request.
		asio::write(socket, request);

		// Read the response status line. The response streambuf will automatically
		// grow to accommodate the entire line. The growth may be limited by passing
		// a maximum size to the streambuf constructor.
		asio::streambuf response;
		asio::read_until(socket, response, "\r\n");

		// Check that response is OK.
		istream response_stream(&response);
		string http_version;
		response_stream >> http_version;
		unsigned int status_code;
		response_stream >> status_code;
		string status_message;
		getline(response_stream, status_message);
		if (!response_stream || http_version.substr(0, 5) != "HTTP/")
		{
			cout << "Could not get the page: " << address << endl;
			cout << "Invalid response\n";
			return string();
		}
		if (status_code != 200)
		{
			cout << "Could not get the page: " << address << endl;
			cout << "Response returned with status code " << status_code << "\n";
			return string();
		}

		// Read the response headers, which are terminated by a blank line.
		asio::read_until(socket, response, "\r\n\r\n");

		// Process the response headers.
		string header;
		while (getline(response_stream, header) && header != "\r")
			;
//			cout << header << "\n";
//		cout << "\n";

		stringstream stringStream(stringstream::in | stringstream::out);

		// Write whatever content we already have to output.
		if (response.size() > 0)
			stringStream << &response;

		// Read until EOF, writing data to output as we go.
		system::error_code error;
		while (asio::read(socket, response, asio::transfer_at_least(1), error))
			stringStream << &response;

		if (error != asio::error::eof)
			cout << "Could not get the page: " << address << endl;
			return string();

		return stringStream.str();
	}
	catch (std::exception& e)
	{
		cout << "Could not get the page: " << address << endl;
		cout << "Exception: " << e.what() << "\n";
		return string();
	}

	return string();
}

// Determine if the transactions add up to a share per address for each address.
bool getIsSufficientAmount(vector<string> addressStrings, vector<int64> amounts, const string& dataDirectory, const string& fileName, int height, int64 share, int step)
{
	vector<string> coinAddressStrings = getCoinAddressStrings(dataDirectory, fileName, height, step);
	map<string, int64> receiverMap;

	if (coinAddressStrings.size() == 0)
	{
		cout << "No coin addresses were found, there may be something wrong with the receiver_x.csv files." << endl;
		return false;
	}

	int64 sharePerAddress = share / (int64)coinAddressStrings.size();

	for (int i = 0; i < coinAddressStrings.size(); i++)
		receiverMap[coinAddressStrings[i]] = (int64)0;

	for (int i = 0; i < addressStrings.size(); i++)
	{
		string addressString = addressStrings[i];

		if (receiverMap.count(addressString) > 0)
			receiverMap[addressString] += amounts[i];
	}

	for (int i = 0; i < coinAddressStrings.size(); i++)
	{
		if (receiverMap[coinAddressStrings[i]] < sharePerAddress)
		{
			cout << endl << "In receiver.h, getIsSufficientAmount rejected the addresses or amounts." << endl;
			cout << "For the given:" << endl;
			cout << "Height: " << height << endl;
			cout << "Share: " << share << endl;
			cout << "Step: " << step << endl;
			cout << "The expected addresses are:" << endl;

			for (int i = 0; i < coinAddressStrings.size(); i++)
				cout << coinAddressStrings[i] << endl;

			cout << endl << "The given addresses are:" << endl;

			for (int i = 0; i < addressStrings.size(); i++)
				cout << addressStrings[i] << endl;

			cout << endl << "The given amounts are:" << endl;

			for (int i = 0; i < amounts.size(); i++)
				cout << amounts[i] << endl;

			cout << endl;
			return false;
		}
	}

	return true;
}

// Get the directory path joined with the file name.
string getJoinedPath(const string& directoryPath, const string& fileName)
{
	filesystem::path completePath = filesystem::system_complete(filesystem::path(directoryPath));
	return (completePath / (filesystem::path(fileName))).string();
}

// Get the page by the address, be it a file name or hypertext address.
string getLocationText(const string& address)
{
	if (getStartsWith(address, string("http://")) || getStartsWith(address, string("https://")))
		return getInternetText(address);
	return getFileText(address);
}

// Get the pages by the addresses, be they file names or hypertext addresses.
vector<string> getLocationTexts(vector<string> addresses)
{
	vector<string> locationTexts;

	for(int addressIndex = 0; addressIndex < addresses.size(); addressIndex++)
		locationTexts.push_back(getLocationText(addresses[addressIndex]));

	return locationTexts;
}

// Get the lowercase string.
string getLower(const string& text)
{
	int textLength = text.length();
	string lower = text.substr();

	for(int characterIndex = 0; characterIndex < textLength; characterIndex++)
	{
		lower[characterIndex] = tolower(text[characterIndex]);
	}

	return lower;
}

// Get the peer names from the text.
vector<string> getPeerNames(const string& text)
{
	bool isPeerSection = false;
	vector<string> peerNames;
	vector<string> textLines = getTextLines(text);

	for (int lineIndex = 0; lineIndex < textLines.size(); lineIndex++)
	{
		string firstLowerSpaceless = string();
		string line = textLines[lineIndex];
		vector<string> words = getCommaDividedWords(line);

		if (words.size() > 0)
			firstLowerSpaceless = getReplaced(getLower(words[0]), string(" "), string());

		if (firstLowerSpaceless == string("peer"))
			peerNames.push_back(getReplaced(words[1], string(" "), string()));

		if (firstLowerSpaceless == string("_endpeers"))
			isPeerSection = false;

		if (isPeerSection)
			peerNames.push_back(getReplaced(words[0], string(" "), string()));

		if (firstLowerSpaceless == string("_beginpeers"))
			isPeerSection = true;
	}

	return peerNames;
}

// Get the string with the search string replaced with the replace string.
string getReplaced(const string& text, const string& searchString, const string& replaceString)
{
	string::size_type position = 0;
	string replaced = text.substr();

	while ((position = replaced.find(searchString, position)) != string::npos)
	{
		replaced.replace(position, searchString.size(), replaceString );
		position++;
	}

	return replaced;
}

// Determine if the first string starts with the second string.
bool getStartsWith(const string& firstString, const string& secondString)
{
	if (firstString.substr(0, secondString.size()) == secondString)
		return true;

	return false;
}

// Get the step file name by the file name.
string getStepFileName(const string& fileName, int height, int step)
{
	return getSuffixedFileName(fileName, getStringByInt(height / step));
}

// Get the step output according to the peers listed in a file.
string getStepOutput(const string& directoryPathInput, const string& fileName, int height, int step)
{
	string directoryPath = string();

	if (directoryPathInput != string())
		directoryPath = getJoinedPath(directoryPathInput, fileName.substr(0, fileName.rfind('.')));

	string stepText = getStepText(directoryPath, fileName, height, step);

	if (stepText != string())
	{
		writeNextIfValueHigher(directoryPath, fileName, height, step, stepText);
		return stepText;
	}

	int valueDown = height - step;
	string previousText = string();
	while (valueDown >= 0)
	{
		previousText = getStepText(directoryPath, fileName, valueDown, step);

		if (previousText != string())
			return getStepTextRecursively(directoryPath, fileName, height, previousText, step, valueDown);

		valueDown -= step;
	}

	return string();
}

// Get the step text by the file name.
string getStepText(const string& dataDirectory, const string& fileName, int height, int step)
{
	string stepFileName = getStepFileName(fileName, height, step);
	if (dataDirectory == string())
		return getFileText(stepFileName);

	string directorySubName = getJoinedPath(dataDirectory, stepFileName);

	if (getExists(directorySubName))
		return getFileText(directorySubName);

	string stepText = getFileText(stepFileName);

	if (stepText == string())
		return string();

	writeFileText(directorySubName, stepText);
	return stepText;
}

// Get the step text recursively.
string getStepTextRecursively(const string& directoryPath, const string& fileName, int height, const string& previousTextInput, int step, int valueDown)
{
	string previousText = previousTextInput.substr();
	string stepFileName;

	for(int valueUp = valueDown; valueUp < height; valueUp += step)
	{
		int nextValue = valueUp + step;
		previousText = getCommonOutputByText(previousText, getStringByInt(nextValue / step));
		stepFileName = getStepFileName(fileName, nextValue, step);
		writeFileTextByDirectory(directoryPath, stepFileName, previousText);
	}

	return previousText;
}

// Get the string from the boolean.
string getStringByBoolean(bool boolean)
{
	if (boolean)
		return string("true");
	return string("false");
}

// Get the string from the double precision float.
string getStringByDouble(double doublePrecision)
{
	ostringstream doubleStream;

	doubleStream << doublePrecision;

	return doubleStream.str();
}

// Get the string from the integer.
string getStringByInt(int integer)
{
	ostringstream integerStream;

	integerStream << integer;

	return integerStream.str();
}

// Get the file name with the suffix just before the extension.
string getSuffixedFileName(const string& fileName, const string& suffix)
{
	if (suffix == string())
		return fileName;

	int lastDotIndex = fileName.rfind(".");

	if (lastDotIndex == string::npos)
		return fileName + suffix;
	return fileName.substr(0, lastDotIndex) + string("_") + suffix + fileName.substr(lastDotIndex);
}

// Get the file names with the suffixes just before the extension.
vector<string> getSuffixedFileNames(vector<string> fileNames, const string& suffix)
{
	vector<string> suffixedFileNames;

	for(int fileNameIndex = 0; fileNameIndex < fileNames.size(); fileNameIndex++)
	{
		string fileName = fileNames[fileNameIndex];
		int doNotAddSuffixIndex = fileName.find("_do_not_add_suffix_");

		if (doNotAddSuffixIndex == string::npos)
			suffixedFileNames.push_back(getSuffixedFileName(fileName, suffix));
		else
			suffixedFileNames.push_back(fileName.substr(0, doNotAddSuffixIndex));
	}

	return suffixedFileNames;
}

// Get all the lines of text of a text.
vector<string> getTextLines(const string& text)
{
	return getTokens(getReplaced(getReplaced(text, string("\r"), string("\n")), string("\n\n"), string("\n")), string("\n"));
}

// Get the tokens of the text split by the delimeters.
vector<string> getTokens(const string& text, const string& delimiters)
{
	vector<string> tokens;
	string::size_type lastPosition = text.find_first_not_of(delimiters, 0);
	string::size_type position = text.find_first_of(delimiters, lastPosition);

	while (string::npos != position || string::npos != lastPosition)
	{
		tokens.push_back(text.substr(lastPosition, position - lastPosition));
		lastPosition = text.find_first_not_of(delimiters, position);
		position = text.find_first_of(delimiters, lastPosition);
	}

	return tokens;
}

// Make a directory if it does not already exist.
void makeDirectory(const string& directoryPath)
{
	if (getExists(directoryPath))
		return;

	if (filesystem::create_directories(filesystem::path(directoryPath)))
		printf("The following directory was made: %s\n", directoryPath.c_str());
	else
		printf("Receiver.h can not make the directory %s so give it read/write permission for that directory.", directoryPath.c_str());
}

// Write a text to a file.
void writeFileText(const string& fileName, const string& fileText)
{
	makeDirectory(getDirectoryPath(fileName));
	ofstream fileStream(fileName.c_str());

	if (fileStream.is_open())
	{
	  fileStream << fileText;
	  fileStream.close();
	}
	else printf("The file %s can not be written to.\n", fileName.c_str());
}

// Write a text to a file joined to the directory path.
void writeFileTextByDirectory(const string& directoryPath, const string& fileName, const string& fileText)
{
	writeFileText(getJoinedPath(directoryPath, fileName), fileText);
}

// Write next step file if height is higher than the threshold.
void writeNextIfValueHigher(const string& directoryPath, const string& fileName, int height, int step, const string& stepText)
{
	int remainder = height - step * (height / step);
	double floatPart = double(remainder) / double(step);
	double lessThanOneMinusThreshold = 0.95 * (1.0 - globalWriteNextThreshold);
	double fileRandomNumber = getFileRandomNumber(directoryPath, fileName);

	if (floatPart < globalWriteNextThreshold + lessThanOneMinusThreshold * fileRandomNumber)
		return;
	int nextValue = height + step;
	string nextFileName = getStepFileName(fileName, nextValue, step);

	if (getFileText(nextFileName) == string())
	{
		string nextText = getCommonOutputByText(stepText, getStringByInt(nextValue / step));

		if (nextText != string())
			writeFileTextByDirectory(directoryPath, nextFileName, nextText);
	}
}

import json

def convertJson(fileName, listAttributes, intAttributes):
    print("Beginning conversion for file: {}.tsv".format(fileName))
    # For some reason, I run into an issue on Niall Byrne in name.basics.tsv (with char 0x81) if I don't use an encoding
    inFile = open(fileName + ".tsv", 'r', encoding='utf-8')
    # The first line contains the titles
    titles = inFile.readline().strip().split('\t') # The \t character separates each entry; strip() gets rid of the \n character
    anotherLine = inFile.readline()
    allEntries = []
    while anotherLine:
        entry = {}
        for title, data in zip(titles, anotherLine.strip().split('\t')):
            if title in intAttributes and (data != '\\N'):
                # Values are floats
                data = int(data)
            elif title == 'averageRating':
                # Values are floats
                data = float(data)
            if title in listAttributes:
                # List attribute
                entry[title] = data.split(',')
            elif title == 'characters':
                # Stored differently for some reason
                if data == '\\N':
                    # Null
                    entry[title] = ['\\N']
                else:
                    # Parse it into a list
                    entry[title] = json.loads(data)
            else:
                # Non-list attribute
                entry[title] = data

        allEntries.append(entry)
        anotherLine = inFile.readline()
    outFile = open(fileName + '.json', 'w')
    outFile.write(json.dumps(allEntries, indent = 2)) # Having an indent keeps the file from just being one long line
    print("Wrote to the output file: {}.json".format(fileName))



def main():
    listAttributes = {'primaryProfession','knownForTitles','genres'} # Characters are stored differently for some reason
    intAttributes = {'birthYear','deathYear','isAdult','startYear','runtimeMinutes','ordering','numVotes','avgRating'}
    listOfFiles = ['name.basics', 'title.basics','title.principals','title.ratings']
    for file in listOfFiles:
        convertJson(file, listAttributes, intAttributes)
    print("Done")

if __name__=='__main__':
    main()
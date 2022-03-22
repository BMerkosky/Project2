import pymongo
import json
import time
# Use client = MongoClient('mongodb://localhost:27017') for specific ports!
# Connect to the default port on localhost for the mongodb server.
client = pymongo.MongoClient()

def convertJson(fileName):
    inFile = open(fileName + ".tsv", 'r', encoding='utf-8') # For some reason, I run into an issue on Niall Byrne (with char 0x81) if I don't use this encoding
    # The first line contains the titles
    titles = inFile.readline().strip().split('\t') # The \t character separates each entry. strip() gets rid of the \n character
    print(titles)
    anotherLine = inFile.readline()
    allEntries = []
    while anotherLine:
        entry = {}
        for title, data in zip(titles, anotherLine.strip().split('\t')):
            entry[title] = data
        #print(entry)
        allEntries.append(entry)
        anotherLine = inFile.readline()
    outFile = open(fileName + '.json', 'w', encoding = 'utf-8')
    outFile.write(json.dumps(allEntries)) #TODO: indent = 4?



def main():
    print("Here")
    testingFile = 'name.basics'
    convertJson(testingFile)
    print("Done")

if __name__=='__main__':
    main()

# https://www.geeksforgeeks.org/python-tsv-conversion-to-json/
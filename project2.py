import pymongo
import re
import time

def main():
    db = connect()
    # Now we create the collections
    nameBasics = db["name_basics"]
    titleBasics = db["title_basics"]
    titlePrincipals = db["title_principals"]
    titleRatings = db["title_ratings"]
    # Main menu
    exitFlag = False
    while True:
        if exitFlag:
            exitProgram()
            break

        printMenu()
        validOptions = ['1','2','3', '4', '5', '6']

        option = input("Choose an option: ")
        
        if option not in validOptions:
            validInput = False
        else:
            validInput = True

        while not validInput:
            option = input("Invalid input. Choose an option: ")
            if option in validOptions:
                validInput = True
        
        if option == '1':
            titleSearch(nameBasics, titleBasics, titlePrincipals, titleRatings)
        elif option == '2':
            searchGenres(titleBasics)
        elif option == '3':
            searchPeople(nameBasics)
        elif option == '4':
            addMovie(titleBasics)
        elif option == '5':
            addMoviePeople(nameBasics, titleBasics, titlePrincipals)
        else:
            exitFlag = True

def printMenu():
    print('='*26)
    print("CMPUT 291 - Mini Project 2")
    print('='*26)
    print("1 - Search for titles")
    print("2 - Search for genres")
    print("3 - Search for cast/crew members")
    print("4 - Add a movie")
    print("5 - Add a cast/crew member")
    print("6 - Exit")
    print('='*26)

def exitProgram():
    print("Exiting program...")
    time.sleep(1)
    print("Goodbye")

def connect():
    # Connect to the mongo database
    # Returns the database object
    validResponse = False
    while not validResponse:
        portNum = input("Which port would you like to use (empty response is the default port: 27017)? ")
        if portNum =='':
            portNum = 27017
        elif portNum.isdigit():
            portNum = int(portNum)
        else:
            print("Invalid port number")
            continue
        print("Connecting...")
        client = pymongo.MongoClient(port = portNum)
        try:
            # Check if this is a valid client
            client.admin.command('ping')
            validResponse = True
        except pymongo.errors.ConnectionFailure:
            # Invalid client
            print("Server not available")
    print("Connection successful")

    # Create or open the database on server
    db = client['291db']
    return db

def titleSearch(nameBasics, titleBasics, titlePrincipals, titleRatings):
    # Created a Text Index on title_basics as:
    # db.title_basics.createIndex({"primaryTitle": "text", "startYear": "text"})
    # this searches for all KEYWORDS related to input!
    # TODO: Do we need to keep this index?
    validAnswer = False
    while not validAnswer:

        keyword = input("Enter one or more keywords to search for, separated by a space: ").lower()
        count = titleBasics.count_documents({ "$text": { "$search": keyword }}) # count to see if something exists

        cursor = titleBasics.find( { "$text": { "$search": keyword}})
        if count > 0:
            validAnswer = True
        else:
            print("Sorry, could not find movies with that keyword. Try Again.")

    # print keyword searches 
    i = 1
    ids = []
    for documents in cursor:
        ids.append(documents["tconst"])
        print(i, end = '|')
        for item in documents:
            print("{}: ".format(item) + str(documents[item]), end = ', ')
        i += 1
        print('')
    print("0| Exit to menu")
    validAnswer = False
    while not validAnswer:
        choice = input(("Select an to view the information of its corresponding movie: "))
        if choice == '0': return
        elif choice.isdigit() and int(choice) <= i:
            choice = int(choice)
            validAnswer = True
        else:
            print("Sorry, invalid answer. Please try again")

    id = ids[choice - 1]

    # Print the information for the movie
    res = titleRatings.aggregate( [ { "$match": { "tconst": id } },
        {
            "$lookup": {
                "from": "title_principals",
                "localField": "tconst", 
                "foreignField": "tconst", 
                "pipeline" : [{"$sort": {"nconst" : pymongo.DESCENDING}}],
                "as": "principalsRow" 
            },
        },
        {
            "$lookup": {
                "from": "name_basics",
                "localField": "principalsRow.nconst",
                "foreignField": "nconst",
                "pipeline" : [{"$sort": {"nconst" : pymongo.DESCENDING}}],
                "as": "namesRow"
            }
        }    
    ] )
    for r in res:
        # There should only be one row
        print("Average rating:", r["averageRating"])
        print("Number of votes:", r["numVotes"])
        for member in range(len(r["principalsRow"])):
            # We should also be able to use r["namesRow"] if we wanted
            print("Name: ", r["namesRow"][member]["primaryName"])
            for character in r["principalsRow"][member]["characters"]:
                if character == "\\N":
                    print("- No characters found")
                else:
                    print("- Character:", character)

def addMoviePeople(nameBasics, titleBasics, titlePrincipals):
    # Adds a cast/crew member to the title_principals collection
    validAnswer = False
    while not validAnswer:
        # Get the cast member id
        nconst = input("Provide the id of the person to add: ")
        result = nameBasics.count_documents({"nconst": nconst})
        if result > 0:
            validAnswer = True
        else:
            print("Sorry, we could not find a cast/crew member in name_basics with that nconst.")
    validAnswer = False
    while not validAnswer:
        # Get the movie they have acted in
        tconst = input("Provide the id of the title this person was in: ")
        result = titleBasics.count_documents({"tconst": tconst})
        if result > 0:
            validAnswer = True
        else:
            print("Sorry, we couldn't find a movie int title_basics with that tconst.")

    # Get the category
    category = input("Provide the category (ex: 'production_designer') of this role: ")

    # Get the ordering
    ordering = titlePrincipals.find_one({"tconst":tconst}, sort=[('ordering', pymongo.DESCENDING)])
    if ordering == None:
        # Title not in title_principals
        ordering = 1
    else:
        # Add one to the max
        ordering = ordering['ordering'] + 1
        

    # Add the cast/crew member
    titlePrincipals.insert_one(
        {"tconst": tconst,
        "ordering": ordering,
        "nconst": nconst,
        "category": category,
        "job": "\\N",
        "characters": ["\\N"]})

    print("Cast/crew member added")

def searchPeople(nameBasics):
    name = input("Provide a cast or crew member: ")

    # check if the member exists
    count = nameBasics.count_documents( { 
        "primaryName": { 
            "$regex": "^"+name+"$", 
            "$options": "i" 
        } 
    } )

    if count == 0:
        print("No members found")
        return
    
    res = nameBasics.aggregate( [ 
        { "$match": { "primaryName": {"$regex": "^"+name+"$", "$options": "i"} } },
        {
            "$lookup": {
                "from": "title_principals",
                "localField": "nconst", 
                "foreignField": "nconst", 
                "as": "movies" 
            },
        },
        {
            "$lookup": {
                "from": "title_basics",
                "localField": "movies.tconst",
                "foreignField": "tconst",
                "as": "ptitle"
            }
        },        
    ] )

    # printing output    
    for r in res:
        print('-'*26)
        print(r["primaryName"], end=' ')
        print('('+r["nconst"]+')')
        print("Professions:", ', '.join(r["primaryProfession"]))
        
        # print movie and jobs/characters only if they had an appearance in the movie
        for i in range(len(r["movies"])):
            if r["movies"][i]["job"] != '\\N' or ''.join(r["movies"][i]["characters"]) != '\\N':
                print(r["ptitle"][i]["primaryTitle"])
                if r["movies"][i]["job"] != '\\N':
                    print("- Job:", r["movies"][i]["job"])
                elif ''.join(r["movies"][i]["characters"]) != '\\N':
                    print("- Characters:", ', '.join(r["movies"][i]["characters"]))

def searchGenres(titleBasics):
    genre = input("Search for genre: ")
    vcnt = int(input("Minimum vote count: "))

    # check if the genre exists
    count = titleBasics.count_documents( { 
        "genres": { 
            "$regex": "^"+genre+"$", 
            "$options": "i" 
        } 
    } )

    if count == 0:
        print("Nothing found")
        return

    res = titleBasics.aggregate( [
        { "$match": { "genres": re.compile(genre, re.IGNORECASE) } },
        {
            "$lookup": {
                "from": "title_ratings",
                "localField": "tconst",
                "foreignField": "tconst",
                "as": "votes"
            } 
        },
        { "$unwind": "$votes" },
        { "$match": { "votes.numVotes": { "$gte": vcnt } } },
        { "$sort": { "votes.averageRating": -1 } }
    ] )

    # printing output
    print('-'*60)
    print("{m:50} | Rating".format(m="Movies"))
    print('-'*60)
    for r in res:        
        print("{m:50} | {v}".format(m=r["primaryTitle"], v=r["votes"]["averageRating"]))

if __name__=='__main__':
    main()


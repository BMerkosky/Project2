import pymongo
import re
import time
#TODO: Check that using different ports also works with the lab machines
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
            title_search(nameBasics, titleBasics, titleRatings)
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

def title_search(nameBasics, titleBasics, titleRatings):
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
        for documents in cursor:
            print(documents)
        print("\n")

    validAnswer = False
    while not validAnswer:
        input2 = input("Enter a title to see rating, number of votes and names of cast/crew:  ")
        # count2: check to see if there is any movies with that name
        count2 = titleBasics.count_documents({"primaryTitle": { "$regex": input2, "$options": "i"}}) 
        # case insensitive user_title
        user_title = titleBasics.find({"primaryTitle": { "$regex": input2, "$options": "i"}}) 
        if count2 > 0:
            validAnswer = True
        else:
            print("Sorry, no titles found. Try again.")
        user_titles_list = []
        tconst1 = []

        for i in user_title:
            tconst1.append(i['tconst'])
            user_titles_list.append(i)

    #print(user_titles_list)
    #print(tconst1[0])


    validAnswer = False
    while not validAnswer:
        user_menu = input("Enter 1 to see rating, Enter 2 to see votes, Enter 3 to see cast/crew members, Enter 4 to end: ")
        if user_menu == '1':
            ratings_list = []
            # if more than 1 movie, takes first movie index.
            ratings = titleRatings.find({"tconst": tconst1[0]})
            for i in ratings:
                ratings_list.append(i["averageRating"])
            for i in ratings_list:
                print("Average rating is: ",ratings_list)

        elif user_menu == '2':
            votes_list = []
            votes = titleRatings.find({"tconst": tconst1[0]})
            for i in votes:
                votes_list.append(i["numVotes"])
            print("Number of votes is: ",votes_list)
            
        elif user_menu == '3':

            if nameBasics.find({'knownForTitles': tconst1[0]}): 
                crew = nameBasics.find({'knownForTitles': tconst1[0]}, {'primaryName':1})
                chars = []
                knownfor = nameBasics.find({"knownForTitles": tconst1[0] })
                if knownfor:
                    for i in knownfor:
                        chars.append(i["nconst"])
                name = []
                for i in crew:
                    name.append(i["primaryName"])

                print(name)
                print("Name of cast/crew members: ", ', '.join(name))
                #print(chars)

        elif user_menu == '4':
            validAnswer = True

def addMovie(titleBasics):
    #TODO: Error checking for this one
    validAnswer = False
    while not validAnswer:
        # need unique tconst, checking if user input tconst already exists in titleBasics
        tconst = input("Provide ID of movie to add: ")
        result = titleBasics.count_documents({"tconst": tconst})
        if result == 0:
            validAnswer = True
        else:
            print("Sorry, that tconst value already exists. Enter a unique value: ")


    title = input("Provide a movie title to add: ")
    
    start_year = input("Enter movie start year: ")

    mov_time = input("Enter movie runtime in minutes: ")

    genre_list = []

    genre = input("Enter movie genre(s): ")
    genre_list.append(genre)


    titleBasics.insert_one(
        {"tconst": tconst,
        "titleType": "movie",
        "primaryTitle": title,
        "originalTitle": title,
        "isAdult": "\\N",
        "startYear": start_year,
        "endYear": "\\N",
        "runtimeMinutes": mov_time,
        "genres": genre_list,
        })

    print("Movie added.")

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
    vcnt = int(input("Mininum vote count: "))

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
        { "$sort": { "votes.numVotes": -1 } }
    ] )

    # printing output
    print('-'*50)
    print("{m:40} | Votes".format(m="Movies"))
    print('-'*50)
    for r in res:        
        print("{m:40} | {v}".format(m=r["primaryTitle"], v=r["votes"]["numVotes"]))

if __name__=='__main__':
    main()


import pymongo
import re
import time
start_time = time.time()


# Use client = MongoClient('mongodb://localhost:27017') for specific ports!
# Connect to the default port on localhost for the mongodb server.
client = pymongo.MongoClient()
#TODO: Do we have to prompt the user for a specific port again?


# Create or open the video_store database on server.
db = client["291"]

# Now we create the collections
nameBasics = db["name_basics"]
titleBasics = db["title_basics"]
titlePrincipals = db["title_principals"]
titleRatings = db["title_ratings"]

# Now we can run our code here. TODO: Create a main function etc.
def title_search():
    # Created a Text Index on title_basics as:
    # db.title_basics.createIndex({"primaryTitle": "text", "startYear": "text"})
    # this searches for all KEYWORDS related to input!
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

def addMovie():

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


def addMoviePeople(titleBasics, nameBasics, titlePrincipals):
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
    
def addMoviePeople(titleBasics, nameBasics, titlePrincipals):
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

def searchPeople():
    # name = input("Provide a cast or crew member: ")
    name = "Michael Jordan"  # for testing

    # TODO: this is rlly ugly but it works lol
    # u can probably combine some of the lookup queries
    # try to get the name of the titles in the movies part
    # TODO: print nicely

    res = db.name_basics.aggregate( [ 
        { "$match": { "primaryName": re.compile(name, re.IGNORECASE) } },
        # { "$unwind": "$knownForTitles" },
        {
            "$lookup": {
                "from": "title_principals",
                "localField": "nconst", 
                "foreignField": "nconst", 
                "pipeline": [ {
                        "$project": {
                            "tconst": 1,
                            "_id": 0
                        }
                    } ],
                "as": "movies" 
            },
        },
        { "$project": { "birthYear": 0, "deathYear": 0 } },
        { "$unwind": "$movies" },
        {
            "$lookup": {
                "from": "title_principals",
                "let": {
                    "a": "$nconst",
                    "b": "$movies.tconst"
                },
                "pipeline": [
                    { "$match": { "$expr": { "$and": [
                        { "$eq": [ "$nconst", "$$a" ] },
                        { "$eq": [ "$tconst", "$$b" ] }
                    ] } }
                    },
                    { "$project": {
                        "_id": 0,
                        "ordering": 0,
                        "category": 0
                    } }
                ],
                "as": "jobs"
            }
        },
        { "$unwind": "$jobs" },
        {
            "$lookup": {
                "from": "title_basics",
                "localField": "movies.tconst",
                "foreignField": "tconst",
                "pipeline": [ {
                        "$project": {
                            "primaryTitle": 1,
                            "_id": 0
                        }
                    } ],
                "as": "names"
            }
        }
    ] )
    
    for r in res:
        # print(r["primaryName"], end=' ')
        # print('('+r["nconst"]+')')
        # print(r["primaryProfession"])
        # print(r["movies"])
        # print(r["jobs"])
        print(r)
        print()

def searchGenres():
    # genre = input("Search for genre: ")
    # vcnt = input("Mininum vote count: ")

    # for easy testing
    genre = "Drama"
    vcnt = 200000

    # NOTE: this isn't "instant" like in the rubric :(
    # but idk how to make it even faster
    
    db.title_basics.create_index([("genres", pymongo.TEXT)])

    res = db.title_basics.find( { "$text": { "$search": genre } } ).limit(3)

    db.title_ratings.create_index("numVotes", pymongo.DESCENDING)
    # res.sort("numVotes", -1)


    # res = db.title_basics.aggregate( [
    #     # { "$match": { "genres": re.compile(genre, re.IGNORECASE) } },
    #     { "$match": { "$text": { "$search": genre } } },
    #     {
    #         "$lookup": {
    #             "from": "title_ratings",
    #             "localField": "tconst",
    #             "foreignField": "tconst",
    #             "as": "votes"
    #         } 
    #     },
    #     { "$unwind": "$votes" },
    #     { "$sort": { "votes.numVotes": -1 } },
    #     { "$match": { "votes.numVotes": { "$gte": vcnt } } },
    #     # { "$sort": { "votes.numVotes": -1 } },
    #     { "$limit": 20 }  # TODO: get rid of this later
    # ] )

    for r in res:
        print(r["primaryTitle"])

searchGenres()
# searchPeople()

print("--- %s seconds ---" % (time.time() - start_time))

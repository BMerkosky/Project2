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

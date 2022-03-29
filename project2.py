import pymongo
import re

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
                # "localField": "nconst",
                # "foreignField": "nconst",
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

    # # make our own dict so we can print it out easy later :) jk this is shit lol
    # pdict = defaultdict(list)
    # mdict = defaultdict(list)

    # # tconst and nconst are unique
    # # professions is top 3

    # findName = db.name_basics.find( {"primaryName": name} )
    
    # for r in findName:
    #     nconst = r["nconst"]
    #     pdict[nconst].append(r["primaryProfession"])
    #     pdict[nconst].append(r["knownForTitles"])

    #     # format: nconst: [professions], [titles]

    # for v in pdict.values():
    #     for t in v[1]:
    #         findTitle = db.title_basics.find( {"tconst": t} )
    #         for title in findTitle:
    #             print(title)
    #         # print(t)
    #     # print(v[1])  # get the titles

    # # get primary title



    # # format of nested dictionary at the end:
    # # nconst: [professions], [titles: [primary title], [jobs], [chars]]
    
    # print(pdict)
    # # {'nm0003044': [['actor', 'producer', 'soundtrack'], ['tt0124718', 'tt0117705']], 
    # # 'nm0430106': [['actress'], ['tt0204388']], 
    # # 'nm1243542': [['editor'], ['tt0274509']]}
    
    # # for t in tconst:
    # #     findMovies = db.title_basics.find( {"tconst": t} )
    # #     findJobs = db.title_principals.find( {"tconst": t, "nconst": nconst} )
    # #     for m in findMovies:
    # #         ptitle = m["primaryTitle"]
    # #         mdict[t].append(ptitle)
    # #     # print(ptitle)
    # # #         mdict[t] = ptitle
    # # #         # mlist.append(ptitle)
    # #     for j in findJobs:
    # #         job = j["job"]
    # #         mdict[t].append(job)
    # # #     # print("wow",mdict[t])
    # # # # print(mdict)

    # # # for t in tconst:
    # # #     findJobs = db.title_principals.find( {"tconst": t, "nconst": nconst} )
    # # #     for j in findJobs:
    # # #         job = j["job"]
    # # #         characters = j["characters"]
    # # #         print(characters)
    # # #         for x in characters:
    # # #             print("mdict:",mdict[t])

    # # #     # findJobs = db.title_principals.find( {"tconst": t, "nconst": nconst} )
    # # #     # for r in findMovies:
    # # #     #     ptitle = r["primaryTitle"]
    # # #     #     print('-',ptitle, end='')
    # # #     # for j in findJobs:
    # # #     #     job = j["job"]
    # # #     #     print(':',job)

    # # # jobs and characters
    # # print(mdict)


    # # # and for each tconst, take the tconst and nconst together to find job and characters in title_principals

    # # print(nconst, professions, tconst)
print('='*100)
searchPeople()

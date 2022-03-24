import pymongo

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




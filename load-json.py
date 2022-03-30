import pymongo, json

def main():
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
    collections = ["name_basics", "title_basics", "title_principals", "title_ratings"]
    for collection in collections:
        if collection in db.list_collection_names():
            # Drop the collection if it exists
            print("Dropping collection:", collection)
            temp = db[collection]
            temp.drop()
        # Create the collection
        print("Building collection:", collection)
        newCollection = db[collection]
        with open(collection.replace('_', '.')+'.json', encoding = 'utf-8') as file:
            # See note on March 21
            collection_data = json.load(file)
            newCollection.insert_many(collection_data)
    # Create indices:
    db.title_ratings.create_index("tconst", unique = True)
    
    print("Done")

if __name__=='__main__':
    main()



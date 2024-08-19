from pymongo_get_database import get_database


def run():
    db = get_database()
    collection = db["ActivityDocument"]
    documents = collection.find({}).limit(5)
    for doc in documents:
        print(doc.get('eventName'))
    print("done")


if __name__ == '__main__':
    run()

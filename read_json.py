import json
import os
import re

import pymongo


def get_pdf_json(path: str):
    f = None
    try:
        f = open(path)
        sections = {}
        data = json.load(f)

        # Iterating through the json
        # list
        for i in data['Sections']:
            sections[i['Header']] = i['text']
    except Exception as e:
        print(str(e))
    finally:
        # Closing file
        f.close()
    return sections


def read_directory():
    dir_list = os.listdir('./static/pdfs/')
    for item in dir_list:
        # print(item)
        fileName = item if bool(re.match(".*\\.pdf$", item)) else ""
        print(fileName)


def save_json_object():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["vidly"]
    mycol = mydb["users"]

    mydict = {"firstName": "John", "lastName": "Highway 37", "email": "r@gmail.com"}

    x = mycol.insert_one(mydict)


# Opening JSON file
# print(read_jsonFile("./static/pdfs/2018.json"))
if __name__ == '__main__':
    save_json_object()
    read_directory()

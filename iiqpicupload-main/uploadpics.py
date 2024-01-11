import json
import sys
import os
import time
import logzero
from logzero import logger
import requests

SITE_ID = "de6d0003-9a31-46ee-b52e-9c9ea08f8f0f"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkZTZkMDAwMy05YTMxLTQ2ZWUtYjUyZS05YzllYTA4ZjhmMGYiLCJzY29wZSI6Imh0dHBzOi8vc3RqYWNhZGVteS5pbmNpZGVudGlxLmNvbSIsInN1YiI6ImUzMmE4ZTYxLTE1NzctNDM2Mi1hYzJjLTVjMjZlYjczNzlhNCIsImp0aSI6ImRhZjM5NmYwLTk2OGYtZWUxMS04OTI1LTYwNDViZDg0YWRkYSIsImlhdCI6MTcwMTM1ODg5OS45LCJleHAiOjE3OTYwNTMyOTkuOTEzfQ.jCyIs_5F6thcXCYz4e_ebSjXwqR1zoq3AHYaPDzwugE"
BASE_URL = "stjacademy.incidentiq.com"
PATH = "/Users/mpeters/Desktop/PIX/"

logzero.logfile("logfile.log", disableStderrLogger=False)





def userlookup(id_number):

    userID = ""
    url = "https://stjacademy.incidentiq.com/api/v1.0/search"

    #These variables are used to assist the dictionary lookup in the response.
    item = "Item"
    userKey = "UserId"

    payload = {
        "Query": id_number,
        "Facets": 4,
        "IncludeMatchedItem": False
    }

    headers = {
        'Client': 'ApiClient',
        'SiteId': SITE_ID,
        'authority': 'stjacademy.incidentiq.com',
        'productid': '88df910c-91aa-e711-80c2-0004ffa00010',
        'usertoken': 'c71a7f1a-508e-ee11-8925-6045bd84adda'

    }

    response = requests.request("POST", url, headers=headers, json=payload)

    try:
        u = response.json()
        if u[item]['Users'][0][userKey]:
            userID = u[item]['Users'][0][userKey]


    except:
        logger.error(f"API returned unknown info for {id_number} - rate limited?")

    if userID == "":
        return "fail"

    else:
        return userID

def uploadpic(id_number, userid):

    filename = id_number + '.jpg'
    filepath = PATH + filename
    #url = "https://stjacademy.incidentiq.com/api/v1.0/users/" + userid
    url = "https://" + BASE_URL + "/api/v1.0/profiles/" + userid + "/picture"

    payload = {}
    files = [
        ('File', (filename, open(filepath, 'rb'), 'image/jpeg'))
    ]
    headers = {
        'siteid': SITE_ID,
        'Client': 'ApiClient',
        #'Authorization': TOKEN
        'usertoken': 'c71a7f1a-508e-ee11-8925-6045bd84adda'
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response.status_code


def main():
    success = 0
    fail = 0
    allfiles = []
    fileList = os.listdir(PATH)

    print(allfiles)

    for x in fileList:
        num = x.split('.')[0]
        allfiles.append(str(num))

    allfiles.sort()

    for y in allfiles:
        if y == "":
            continue
        elif int(y.strip()) < 12308700:
            continue
        else:
            userid = userlookup(y)

        if userid == "fail":
            logger.error(f"Looking up user {y} failed")
            continue
        if userid == "duplicate":
            logger.error(f"Duplicates of user {y} found")
            continue
        api = uploadpic(y, userid)
        if api == 200:
            logger.info(f"Uploaded {y} successfully")
            success = success + 1
        else:
            logger.error(f"Failed to upload {y}")
            fail = fail + 1
    # time.sleep(1)
    logger.warning(f"Uploaded {success} successfully, failed on {fail}")


if __name__ == "__main__":
    main()

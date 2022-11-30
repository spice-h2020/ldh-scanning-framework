from LDH import LDH
from Scanner import Scanner
import json
import time


def getStatus():
    try:
        with open('status.json') as statusFile:
            status = json.load(statusFile)
    except:
        print("unable to open status.json, creating new status object")
        status = {

        }
    return status


def writeStatus(status):
    with open('status.json', 'w') as outfile:
        json.dump(status, outfile)


def main():
    ldh = LDH()
    scanner = Scanner()
    status = getStatus()
    if 'lastRun' in status:
        timestamp = status['lastRun']
    else:
        timestamp = 0
    allResultsReturned = False
    page = 0
    processBeginTimestamp = int(time.time())

    # Repeat Activity Log calls for multiple pages until all results are returned
    while not allResultsReturned:
        page += 1
        print('Requesting page: ' + str(page))
        alResponse = ldh.getALEntries(page, timestamp)
        if int(alResponse['documentCount']) < int(alResponse['pagesize']):
                allResultsReturned = True
        # Loop through each activity log entry
        for alEntry in alResponse['results']:
            datasetID = alEntry['al:datasetId']
            documentID = alEntry['al:documentId']
            payload = alEntry['al:request']['al:payload']
            payloadObject = json.loads(payload)
            notifications = scanner.scanObject(datasetID, documentID, payloadObject)
            for notification in notifications:
                # Push notifications back to LDH here
                #response = ldh.pushNotification(notification)
                #print(response.text)
                print(notification)
        status['lastRun'] = processBeginTimestamp
        writeStatus(status)


if __name__ == "__main__":
    main()


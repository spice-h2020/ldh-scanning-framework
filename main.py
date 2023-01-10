from LDH import LDH
from Scanner import Scanner
from Hate import Hate
import json
import time


def getStatus():
    try:
        with open('status.json') as statusFile:
            status = json.load(statusFile)
    except:
        print("unable to open status.json, creating new status file")
        status = {}
    return status


def writeStatus(status):
    with open('status.json', 'w') as outfile:
        json.dump(status, outfile)


def main():
    ldh = LDH()
    scanner = Scanner('scanner_config.json')
    hate = Hate('hate_config.json')
    # scannerList = [scanner, hate]
    scannerList = [scanner]
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
            #notifications = hate.scanObject(datasetID, documentID, payloadObject)
            for notification in notifications:
                # Push notifications back to LDH here, or comment out and just print to the screen for testing
                #response = ldh.pushNotification(notification)
                print(notification)
        status['lastRun'] = processBeginTimestamp
        writeStatus(status)


if __name__ == "__main__":
    main()

